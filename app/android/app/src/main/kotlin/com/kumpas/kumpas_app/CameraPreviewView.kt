package com.kumpas.kumpas_app

import android.content.Context
import android.graphics.Bitmap
import android.graphics.Matrix
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

    private val previewView = PreviewView(context)
    private val analysisExecutor = Executors.newSingleThreadExecutor()
    private var bound = false

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
            provider.bindToLifecycle(
                lifecycleOwner,
                CameraSelector.DEFAULT_FRONT_CAMERA,
                preview,
                analysis
            )
            bound = true
        }, ContextCompat.getMainExecutor(context))
    }

    override fun getView(): View = previewView

    override fun dispose() {
        analysisExecutor.shutdown()
    }
}
