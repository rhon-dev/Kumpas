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
    private val cameraViews = CameraViewOwnership(pipelineLock) { cancelCapture(null, "cancelled") }
    private var pendingTrace: PipelineTrace? = null

    internal class Initialization {
        val resources = mutableListOf<() -> Unit>()
        val registrations = mutableListOf<() -> Unit>()
        var released = false
        var exportDatabase: (() -> SessionDatabase)? = null
    }
    private var initialization: Initialization? = null
    internal fun isCurrent(owner: Initialization) = initialization === owner && !owner.released

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.CAMERA), 7001)
        }
        val owner = Initialization()
        initializeResources(AndroidActivityResourceFactory(applicationContext, pipelineLock,
            { attempts.generation }, { report -> postBenchmarkReport(owner, report) },
            { json -> if (isCurrent(owner)) handleVisionEvent(json) }), owner) { cleanup ->
            val predictions = EventChannel(flutterEngine.dartExecutor.binaryMessenger, "kumpas/predictions")
            cleanup { predictions.setStreamHandler(null) }
            predictions.setStreamHandler(object : EventChannel.StreamHandler {
                override fun onListen(args: Any?, sink: EventChannel.EventSink?) { if (isCurrent(owner)) eventSink = sink }
                override fun onCancel(args: Any?) { if (isCurrent(owner)) eventSink = null }
            })
            val control = MethodChannel(flutterEngine.dartExecutor.binaryMessenger, "kumpas/control")
            cleanup { control.setMethodCallHandler(null) }
            control.setMethodCallHandler(controlHandler(owner))
            registerCameraView(flutterEngine.platformViewsController.registry, owner)
        }
    }

    internal fun controlHandler(owner: Initialization) = MethodChannel.MethodCallHandler { call, result ->
        synchronized(pipelineLock) {
            if (!isCurrent(owner)) {
                result.error("CONTROL_FAILED", "Activity initialization is no longer current", null)
                return@synchronized
            }
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
                        val database = checkNotNull(owner.exportDatabase) { "Export database acquisition not configured" }.invoke()
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
                    "confirmBenchmarkStart" -> result.success(benchmarkMode!!.confirmStart(requireNotNull(call.argument<String>("runId"))))
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

    // Same posted completion callback used by the Android factory; host tests do not install a messenger.
    internal fun postBenchmarkReport(owner: Initialization, report: String) {
        mainHandler.post {
            if (isCurrent(owner)) eventSink?.success(JSONObject().put("state", "benchmark_complete")
                .put("results", JSONObject(report)).toString())
        }
    }

    internal fun registerCameraView(registry: io.flutter.plugin.platform.PlatformViewRegistry, owner: Initialization) {
        check(registry.registerViewFactory(
            "kumpas/camera_preview", object : PlatformViewFactory(StandardMessageCodec.INSTANCE) {
                override fun create(context: Context, viewId: Int, args: Any?): PlatformView {
                    check(isCurrent(owner)) { "Activity initialization is no longer current" }
                    return CameraPreviewView(this@MainActivity, this@MainActivity, visionEngine!!, benchmarkMode, ownership = cameraViews)
                }
            })) { "Camera preview factory registration rejected" }
    }

    internal fun initializeResources(
        factory: ActivityResourceFactory,
        owner: Initialization = Initialization(),
        register: ((() -> Unit) -> Unit) -> Unit,
    ) = synchronized(pipelineLock) {
        val previous = initialization
        var published = false
        try {
            val session = factory.session().also { owner.resources.add(it.release) }
            val exporter = factory.exporter()
            val benchmark = factory.benchmark().also { owner.resources.add(it.release) }
            val vision = factory.vision().also { owner.resources.add(it.release) }
            owner.exportDatabase = factory::exportDatabase
            initialization = owner
            // Publication revokes the displaced subscription before registration can reenter.
            // Early acquisition failures above still preserve the viable owner's listener.
            eventSink = null
            published = true
            sessionManager = session.value
            dataExporter = exporter
            benchmarkMode = benchmark.value
            visionEngine = vision.value
            register { owner.registrations.add(it) }
            // A reentrant registration may have installed a newer owner.
            if (!isCurrent(owner)) releaseInitialization(owner)
            previous?.let { releaseInitialization(it) }
        } catch (original: Throwable) {
            releaseInitialization(owner, original)
            if (published) previous?.let { releaseInitialization(it, original) }
            throw original
        }
    }

    private fun releaseInitialization(owner: Initialization, primary: Throwable? = null) {
        if (owner.released) return
        val current = isCurrent(owner)
        owner.released = true
        val actions = mutableListOf<() -> Unit>()
        if (current) {
            // Invalidate before detaching callbacks; stale cleanup cannot remove newer handlers.
            initialization = null
            attempts.invalidate()
            pendingTrace = null
            sessionManager = null
            dataExporter = null
            benchmarkMode = null
            visionEngine = null
            eventSink = null
            actions.addAll(owner.registrations)
        }
        actions.addAll(owner.resources)
        if (primary == null) completeCleanup(actions) else actions.forEach { action ->
            try { action() } catch (cleanup: Throwable) {
                if (cleanup !== primary) primary.addSuppressed(cleanup)
            }
        }
    }

    private fun cancelCapture(id: String?, outcome: String) = synchronized(pipelineLock) {
        require(outcome in setOf("cancelled", "timeout")) { "Invalid cancellation outcome" }
        val current = attempts.currentId
        if (attempts.cancel(id)) {
            current?.let { benchmarkMode?.recordOutcome(it, outcome) }
            pendingTrace = null
            visionEngine?.cancelAttempt(id)
        } else if (id != null && outcome == "timeout") {
            // A delayed start response may describe a recognized older attempt.
            // Ledger deduplicates and ignores unknown/closed-run identities; do
            // not invalidate or cancel the replacement camera capture.
            benchmarkMode?.recordOutcome(id, "timeout")
        }
    }

    private fun handleVisionEvent(json: String) = synchronized(pipelineLock) {
        val event = JSONObject(json)
        val viewOwner = if (event.has("viewOwner")) event.getLong("viewOwner") else null
        event.remove("viewOwner") // internal ownership never becomes retained measurement metadata
        if (viewOwner != null && !cameraViews.isCurrent(viewOwner)) return@synchronized
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
                sessionManager!!.recordAttempt(event.toString())
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
        val deliveryInitialization = initialization
        val deliverySink = eventSink
        mainHandler.post {
            synchronized(pipelineLock) {
                // The posted event can outlive a clear, cancellation, or new attempt.
                if (initialization === deliveryInitialization &&
                    (!attemptEvent || attempts.canDeliver(id)) &&
                    (state != "camera_error" || deliveryGeneration == attempts.generation) &&
                    (viewOwner == null || cameraViews.isCurrent(viewOwner)) &&
                    deliverySink != null && eventSink === deliverySink) {
                    if (event.optString("state") == "attempt_result") {
                        pendingTrace?.takeIf { it.attemptId == id }?.let {
                            it.delivered(SystemClock.elapsedRealtimeNanos())
                            event.put("timing", it.toJson())
                            benchmarkMode?.recordTrace(it.toJson())
                            benchmarkMode?.recordOutcome(id, "success")
                        }
                    }
                    benchmarkMode?.recordEvent()
                    deliverySink.success(event.toString())
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
        completeCleanup(listOf(
            {
                synchronized(pipelineLock) {
                    attempts.invalidate()
                    pendingTrace = null
                    completeCleanup(listOf(
                        { initialization?.let { releaseInitialization(it) } ?: completeCleanup(listOf(
                            { sessionManager?.close(); Unit },
                            { visionEngine?.close(); Unit },
                            { if (benchmarkMode?.isActive == true) benchmarkMode?.finish(); Unit })); Unit },
                        { eventSink = null }))
                }
            },
            { super.onDestroy() }))
    }
}
