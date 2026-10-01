package com.kumpas.kumpas_app

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.os.Handler
import android.os.Looper
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

    // Keep legacy SessionLog reference only for the migration path —
    // SessionManager reads the file directly during migrateIfNeeded().
    @Suppress("unused")
    private var sessionLog: SessionLog? = null

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)

        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA)
            != PackageManager.PERMISSION_GRANTED
        ) {
            ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.CAMERA), 7001)
        }

        EventChannel(flutterEngine.dartExecutor.binaryMessenger, "kumpas/predictions")
            .setStreamHandler(object : EventChannel.StreamHandler {
                override fun onListen(args: Any?, sink: EventChannel.EventSink?) {
                    eventSink = sink
                }
                override fun onCancel(args: Any?) {
                    eventSink = null
                }
            })

        // Phase 8: SessionManager replaces SessionLog as the primary data layer.
        // On first init it migrates attempt_history.jsonl → SQLite automatically.
        sessionManager = SessionManager(applicationContext)
        dataExporter = DataExporter(applicationContext)
        benchmarkMode = BenchmarkMode(applicationContext)

        visionEngine = VisionEngine(applicationContext) { json ->
            // Route attempt results through SessionManager (SQLite)
            if (json.contains("\"attempt_result\"")) {
                sessionManager?.recordAttempt(json)
            }
            // Record frame for FPS benchmark if active
            benchmarkMode?.let { bm ->
                if (bm.isActive && bm.recordFrame()) {
                    val results = bm.finish()
                    mainHandler.post {
                        eventSink?.success(JSONObject(mapOf(
                            "state" to "benchmark_complete",
                            "results" to results
                        )).toString())
                    }
                }
            }
            mainHandler.post { eventSink?.success(json) }
        }

        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, "kumpas/control")
            .setMethodCallHandler { call, result ->
                when (call.method) {
                    // ─── Existing (Vision) ───────────────────────────
                    "getLabels" -> result.success(visionEngine!!.labelsJson())
                    "startAttempt" -> {
                        visionEngine!!.startAttempt(call.argument<Int>("classId")!!)
                        result.success(null)
                    }
                    "cancelAttempt" -> {
                        visionEngine!!.cancelAttempt()
                        result.success(null)
                    }

                    // ─── History (backward-compatible, now from SQLite) ──
                    "getHistory" -> {
                        result.success(sessionManager!!.historyJson())
                    }

                    // ─── Session lifecycle (Phase 8) ─────────────────
                    "startSession" -> {
                        val sessionId = sessionManager!!.startSession()
                        result.success(sessionId)
                    }
                    "endSession" -> {
                        sessionManager!!.endSession()
                        result.success(null)
                    }
                    "getActiveSession" -> {
                        result.success(sessionManager!!.getActiveSessionId())
                    }

                    // ─── Assessments (Phase 8) ───────────────────────
                    "saveAssessment" -> {
                        val type = call.argument<String>("type")!!
                        val responses = call.argument<String>("responses")!!
                        sessionManager!!.saveAssessment(type, responses)
                        result.success(null)
                    }
                    "getAssessments" -> {
                        result.success(sessionManager!!.getAssessments())
                    }

                    // ─── Data export / clear (Phase 8) ───────────────
                    "exportData" -> {
                        try {
                            val db = SessionDatabase(applicationContext)
                            val path = dataExporter!!.export(
                                sessionManager!!.participantId, db
                            )
                            result.success(path)
                        } catch (e: Exception) {
                            result.error("EXPORT_FAILED", e.message, null)
                        }
                    }
                    "clearAllData" -> {
                        sessionManager!!.clearAllData()
                        result.success(null)
                    }
                    "getParticipantId" -> {
                        result.success(sessionManager!!.participantId)
                    }

                    // ─── Benchmarking ────────────────────────────────
                    "startBenchmark" -> {
                        val duration = call.argument<Int>("durationSeconds") ?: 60
                        benchmarkMode!!.start(duration)
                        result.success(null)
                    }
                    "stopBenchmark" -> {
                        val results = if (benchmarkMode!!.isActive) benchmarkMode!!.finish() else "{}"
                        result.success(results)
                    }
                    "isBenchmarkActive" -> result.success(benchmarkMode!!.isActive)

                    else -> result.notImplemented()
                }
            }

        flutterEngine.platformViewsController.registry.registerViewFactory(
            "kumpas/camera_preview",
            object : PlatformViewFactory(StandardMessageCodec.INSTANCE) {
                override fun create(context: Context, viewId: Int, args: Any?): PlatformView {
                    return CameraPreviewView(this@MainActivity, this@MainActivity, visionEngine!!)
                }
            }
        )
    }

    override fun onPause() {
        super.onPause()
        sessionManager?.onPause()
    }

    override fun onResume() {
        super.onResume()
        sessionManager?.onResume()
    }

    override fun onDestroy() {
        sessionManager?.endSession()
        visionEngine?.close()
        super.onDestroy()
    }
}
