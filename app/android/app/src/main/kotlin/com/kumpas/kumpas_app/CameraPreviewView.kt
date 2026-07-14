package com.kumpas.kumpas_app

import android.content.Context
import android.graphics.Bitmap
import android.graphics.Matrix
import android.util.Log
import android.util.Size
import android.view.View
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.core.content.ContextCompat
import androidx.lifecycle.LifecycleOwner
import io.flutter.plugin.platform.PlatformView
import java.util.concurrent.Executors

/**
 * Native camera preview (CameraX PreviewView) exposed to Flutter as a
 * platform view, with an ImageAnalysis stream feeding VisionEngine.
 */
class CameraPreviewView(
    context: Context,
    lifecycleOwner: LifecycleOwner,
    private val engine: VisionEngine,
) : PlatformView {

    private val previewView = PreviewView(context).apply {
        // TextureView mode: SurfaceView punches through the Flutter layer and
        // hides the prediction overlay rendered above this platform view
        implementationMode = PreviewView.ImplementationMode.COMPATIBLE
    }
    private val analysisExecutor = Executors.newSingleThreadExecutor()
    private var bound = false

    private companion object {
        const val TAG = "KumpasCamera"
    }

    init {
        val providerFuture = ProcessCameraProvider.getInstance(context)
        providerFuture.addListener({
            val provider = providerFuture.get()
            val preview = Preview.Builder().build().also {
                it.surfaceProvider = previewView.surfaceProvider
            }
            val analysis = ImageAnalysis.Builder()
                .setTargetResolution(Size(640, 480))
                .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                .setOutputImageFormat(ImageAnalysis.OUTPUT_IMAGE_FORMAT_RGBA_8888)
                .build()
            analysis.setAnalyzer(analysisExecutor) { image ->
                if (!engine.tick()) { image.close(); return@setAnalyzer }
                val bmp = Bitmap.createBitmap(image.width, image.height, Bitmap.Config.ARGB_8888)
                bmp.copyPixelsFromBuffer(image.planes[0].buffer)
                val rotation = image.imageInfo.rotationDegrees
                val upright = if (rotation != 0) {
                    val m = Matrix().apply { postRotate(rotation.toFloat()) }
                    Bitmap.createBitmap(bmp, 0, 0, bmp.width, bmp.height, m, false)
                } else bmp
                engine.onFrame(upright, image.imageInfo.timestamp / 1_000_000)
                image.close()
            }
            provider.unbindAll()
            // Front camera is the practice default; fall back to back camera
            // (emulators, devices without a selfie cam) instead of crashing.
            try {
                val selector = when {
                    provider.hasCamera(CameraSelector.DEFAULT_FRONT_CAMERA) ->
                        CameraSelector.DEFAULT_FRONT_CAMERA
                    provider.hasCamera(CameraSelector.DEFAULT_BACK_CAMERA) ->
                        CameraSelector.DEFAULT_BACK_CAMERA
                    else -> null
                }
                if (selector == null) {
                    Log.e(TAG, "No camera available; preview disabled")
                } else {
                    provider.bindToLifecycle(lifecycleOwner, selector, preview, analysis)
                    bound = true
                }
            } catch (e: Exception) {
                Log.e(TAG, "Camera bind failed; preview disabled", e)
            }
        }, ContextCompat.getMainExecutor(context))
    }

    override fun getView(): View = previewView

    override fun dispose() {
        analysisExecutor.shutdown()
    }
}
