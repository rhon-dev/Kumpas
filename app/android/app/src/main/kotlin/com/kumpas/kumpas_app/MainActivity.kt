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

class MainActivity : FlutterActivity() {

    private var visionEngine: VisionEngine? = null
    private var sessionLog: SessionLog? = null
    private var eventSink: EventChannel.EventSink? = null
    private val mainHandler = Handler(Looper.getMainLooper())

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

        sessionLog = SessionLog(applicationContext)
        visionEngine = VisionEngine(applicationContext) { json ->
            if (json.contains("\"attempt_result\"")) sessionLog?.append(json)
            mainHandler.post { eventSink?.success(json) }
        }

        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, "kumpas/control")
            .setMethodCallHandler { call, result ->
                when (call.method) {
                    "getLabels" -> result.success(visionEngine!!.labelsJson())
                    "startAttempt" -> {
                        visionEngine!!.startAttempt(call.argument<Int>("classId")!!)
                        result.success(null)
                    }
                    "cancelAttempt" -> { visionEngine!!.cancelAttempt(); result.success(null) }
                    "getHistory" -> result.success(sessionLog!!.historyJson())
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

    override fun onDestroy() {
        visionEngine?.close()
        super.onDestroy()
    }
}
