package com.kumpas.kumpas_app

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.os.Handler
import android.os.Looper
import android.os.SystemClock
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.EventChannel
import io.flutter.plugin.common.MethodChannel
import io.flutter.plugin.common.StandardMessageCodec
import io.flutter.plugin.platform.PlatformView
import io.flutter.plugin.platform.PlatformViewFactory
import org.json.JSONObject

class MainActivity : FlutterActivity() {
    private var visionEngine: VisionEngine? = null
    private var sessionManager: SessionManager? = null
    private var dataExporter: DataExporter? = null
    private var benchmarkMode: BenchmarkMode? = null
    private var eventSink: EventChannel.EventSink? = null
    private val mainHandler = Handler(Looper.getMainLooper())
    // One reentrant lock protects frame processing, persistence, export, and purge.
    private val pipelineLock = Any()
    private val attempts = AttemptBoundary(50)
    private var pendingTrace: PipelineTrace? = null

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.CAMERA), 7001)
        }
        EventChannel(flutterEngine.dartExecutor.binaryMessenger, "kumpas/predictions")
            .setStreamHandler(object : EventChannel.StreamHandler {
                override fun onListen(args: Any?, sink: EventChannel.EventSink?) { eventSink = sink }
                override fun onCancel(args: Any?) { eventSink = null }
            })
        sessionManager = SessionManager(applicationContext)
        dataExporter = DataExporter(applicationContext)
        benchmarkMode = BenchmarkMode(applicationContext) { report ->
            mainHandler.post {
                eventSink?.success(JSONObject().put("state", "benchmark_complete")
                    .put("results", JSONObject(report)).toString())
            }
        }
        visionEngine = VisionEngine(applicationContext, pipelineLock, { attempts.generation }, ::handleVisionEvent)
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, "kumpas/control")
            .setMethodCallHandler { call, result ->
                synchronized(pipelineLock) {
                    try {
                        when (call.method) {
                            "getLabels" -> result.success(visionEngine!!.labelsJson())
                            "startAttempt" -> {
                                check(ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED) {
                                    "Camera permission denied"
                                }
                                val target = requireNotNull(call.argument<Int>("classId")) { "Missing target class" }
                                val id = attempts.start(target)
                                pendingTrace = null
                                val startNs = SystemClock.elapsedRealtimeNanos()
                                visionEngine!!.startAttempt(target, id)
                                benchmarkMode?.recordAttemptStart(id, startNs)
                                result.success(id)
                            }
                            "cancelAttempt" -> {
                                val id = call.argument<String>("attemptId")
                                cancelCapture(id, call.argument<String>("outcome") ?: "cancelled")
                                result.success(null)
                            }
                            "feedbackPresented" -> {
                                val id = requireNotNull(call.argument<String>("attemptId")) { "Missing attempt identity" }
                                val trace = pendingTrace
                                if (trace != null && trace.attemptId == id && attempts.acknowledge(id)) {
                                    trace.acknowledged(SystemClock.elapsedRealtimeNanos())
                                    benchmarkMode?.recordTrace(trace.toJson())
                                    pendingTrace = null
                                }
                                result.success(null)
                            }
                            "getHistory" -> result.success(sessionManager!!.historyJson())
                            "startSession" -> result.success(sessionManager!!.startSession())
                            "endSession" -> {
                                sessionManager!!.endSession()
                                result.success(null)
                            }
                            "getActiveSession" -> result.success(sessionManager!!.getActiveSessionId())
                            "saveAssessment" -> {
                                sessionManager!!.saveAssessment(
                                    requireNotNull(call.argument<String>("type")),
                                    requireNotNull(call.argument<String>("responses")))
                                result.success(null)
                            }
                            "getAssessments" -> result.success(sessionManager!!.getAssessments())
                            "exportData" -> {
                                val database = SessionDatabase(applicationContext)
                                try {
                                    result.success(dataExporter!!.export(sessionManager!!.participantId, database))
                                } finally {
                                    database.close()
                                }
                            }
                            "clearAllData" -> {
                                // Invalidate before purge, including when purge reports partial failure.
                                cancelCapture(null, "cancelled")
                                sessionManager!!.clearAllData()
                                result.success(null)
                            }
                            "getParticipantId" -> result.success(sessionManager!!.participantId)
                            "startBenchmark" -> result.success(benchmarkMode!!.start(call.argument<Int>("durationSeconds") ?: 60))
                            "stopBenchmark" -> result.success(benchmarkMode!!.stop(requireNotNull(call.argument<String>("runId")) { "Missing run identity" }))
                            "getBenchmarkReport" -> result.success(benchmarkMode!!.reportFor(requireNotNull(call.argument<String>("runId")) { "Missing run identity" }))
                            "isBenchmarkActive" -> result.success(benchmarkMode!!.isActive)
                            else -> result.notImplemented()
                        }
                    } catch (error: Exception) {
                        val code = when (call.method) {
                            "clearAllData" -> "CLEAR_FAILED"
                            "exportData" -> "EXPORT_FAILED"
                            "startAttempt" -> "CAMERA_ERROR"
                            else -> "CONTROL_FAILED"
                        }
                        result.error(code, error.message, null)
                    }
                }
            }
        flutterEngine.platformViewsController.registry.registerViewFactory(
            "kumpas/camera_preview", object : PlatformViewFactory(StandardMessageCodec.INSTANCE) {
                override fun create(context: Context, viewId: Int, args: Any?): PlatformView =
                    CameraPreviewView(this@MainActivity, this@MainActivity, visionEngine!!, benchmarkMode)
            })
    }

    private fun cancelCapture(id: String?, outcome: String) = synchronized(pipelineLock) {
        require(outcome in setOf("cancelled", "timeout")) { "Invalid cancellation outcome" }
        val current = attempts.currentId
        if (attempts.cancel(id)) {
            current?.let { benchmarkMode?.recordOutcome(it, outcome) }
            pendingTrace = null
            visionEngine?.cancelAttempt(id)
        }
    }

    private fun handleVisionEvent(json: String) = synchronized(pipelineLock) {
        val event = JSONObject(json)
        val state = event.optString("state")
        val id = event.optString("attemptId")
        val attemptEvent = state in setOf("attempt_progress", "attempt_result", "attempt_failed")
        if (attemptEvent && !attempts.canDeliver(id)) return@synchronized
        if (state == "attempt_result" || state == "attempt_failed") {
            if (!attempts.acceptTerminal(id)) return@synchronized
        }
        if (state == "camera_error") {
            if (!event.has("cameraGeneration") || event.getLong("cameraGeneration") != attempts.generation) return@synchronized
            attempts.currentId?.let { benchmarkMode?.recordOutcome(it, "camera_error") }
            attempts.invalidate()
            pendingTrace = null
        }
        if (state == "attempt_result") {
            try {
                sessionManager!!.recordAttempt(json)
                val timing = event.getJSONObject("timing")
                pendingTrace = PipelineTrace(id, timing.getLong("first_analyzer_ns"),
                    timing.getLong("final_analyzer_ns"), timing.getLong("native_result_ns"),
                    (timing.getDouble("inference_ms") * 1e6).toLong(), timing.getLong("attempt_started_ns"))
            } catch (error: Exception) {
                pendingTrace = null
                event.put("state", "attempt_failed").put("reason", "Attempt could not be saved: ${error.message}")
                event.put("outcome", "persistence_failed")
            }
        }
        if (event.optString("state") == "attempt_failed") {
            benchmarkMode?.recordOutcome(id, event.optString("outcome", "failure"))
        }
        val deliveryGeneration = attempts.generation
        mainHandler.post {
            synchronized(pipelineLock) {
                // The posted event can outlive a clear, cancellation, or new attempt.
                if ((!attemptEvent || attempts.canDeliver(id)) &&
                    (state != "camera_error" || deliveryGeneration == attempts.generation) && eventSink != null) {
                    if (event.optString("state") == "attempt_result") {
                        pendingTrace?.takeIf { it.attemptId == id }?.let {
                            it.delivered(SystemClock.elapsedRealtimeNanos())
                            event.put("timing", it.toJson())
                            benchmarkMode?.recordTrace(it.toJson())
                            benchmarkMode?.recordOutcome(id, "success")
                        }
                    }
                    benchmarkMode?.recordEvent()
                    eventSink?.success(event.toString())
                }
            }
        }
        Unit
    }

    override fun onPause() {
        synchronized(pipelineLock) {
            cancelCapture(null, "cancelled")
            sessionManager?.onPause()
        }
        super.onPause()
    }
    override fun onResume() {
        super.onResume()
        synchronized(pipelineLock) { sessionManager?.onResume() }
    }
    override fun onDestroy() {
        synchronized(pipelineLock) {
            attempts.invalidate()
            pendingTrace = null
            try { sessionManager?.close() }
            catch (error: Exception) { android.util.Log.e("KumpasLifecycle", "Session teardown failed", error) }
            finally {
                try { visionEngine?.close() }
                finally {
                    try { if (benchmarkMode?.isActive == true) benchmarkMode?.finish() }
                    finally { eventSink = null }
                }
            }
        }
        super.onDestroy()
    }
}
