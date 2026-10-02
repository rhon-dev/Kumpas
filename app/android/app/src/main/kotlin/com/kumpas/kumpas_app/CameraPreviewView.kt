package com.kumpas.kumpas_app

import android.content.Context
import android.graphics.Bitmap
import android.graphics.Matrix
import android.os.SystemClock
import android.util.Log
import android.util.Size
import android.view.View
import android.hardware.camera2.CameraCharacteristics
import androidx.camera.camera2.interop.Camera2CameraInfo
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.core.content.ContextCompat
import androidx.lifecycle.LifecycleOwner
import io.flutter.plugin.platform.PlatformView

import java.util.concurrent.Executors

/** CameraX analyzer entry is measured before bitmap conversion, not sensor exposure. */
class CameraPreviewView(
    context: Context,
    lifecycleOwner: LifecycleOwner,
    private val engine: VisionEngine,
    private val benchmark: BenchmarkMode? = null,
) : PlatformView {
    private val previewView = PreviewView(context).apply {
        implementationMode = PreviewView.ImplementationMode.COMPATIBLE
    }
    private val analysisExecutor = Executors.newSingleThreadExecutor()
    private var provider: ProcessCameraProvider? = null
    private var analysis: ImageAnalysis? = null
    private var preview: Preview? = null
    @Volatile private var disposed = false

    init {
        val future = ProcessCameraProvider.getInstance(context)
        future.addListener({
            if (!disposed) {
                val generation = engine.cameraRequestGeneration()
                try {
                    val cameraProvider = future.get()
                    provider = cameraProvider
                    val previewUseCase = Preview.Builder().build().also {
                        it.surfaceProvider = previewView.surfaceProvider
                    }
                    val analysisUseCase = ImageAnalysis.Builder()
                        .setTargetResolution(Size(640, 480))
                        .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                        .setOutputImageFormat(ImageAnalysis.OUTPUT_IMAGE_FORMAT_RGBA_8888)
                        .build()
                    preview = previewUseCase
                    analysis = analysisUseCase
                    analysisUseCase.setAnalyzer(analysisExecutor) { image ->
                        val analyzerNs = SystemClock.elapsedRealtimeNanos()
                        val generation = engine.cameraRequestGeneration()
                        var bitmap: Bitmap? = null
                        var upright: Bitmap? = null
                        try {
                            if (!disposed) {
                                benchmark?.recordAnalyzer()
                                if (engine.tick()) {
                                    benchmark?.recordSelected()
                                    val frame = Bitmap.createBitmap(image.width, image.height, Bitmap.Config.ARGB_8888)
                                    bitmap = frame
                                    // CameraX row padding is not part of bitmap pixels.
                                    val plane = image.planes[0]
                                    val packed = RgbaFramePacking.pack(image.width, image.height,
                                        plane.rowStride, plane.pixelStride, plane.buffer)
                                    frame.copyPixelsFromBuffer(packed)
                                    val rotation = image.imageInfo.rotationDegrees
                                    val rotated = if (rotation != 0) {
                                        val matrix = Matrix().apply { postRotate(rotation.toFloat()) }
                                        Bitmap.createBitmap(frame, 0, 0, frame.width, frame.height, matrix, false)
                                    } else frame
                                    upright = rotated
                                    engine.onFrame(rotated, image.imageInfo.timestamp / 1_000_000, analyzerNs)
                                    benchmark?.recordProcessed()
                                }
                            }
                        } catch (error: Exception) {
                            benchmark?.recordFailure(error.javaClass.simpleName)
                            engine.reportCameraError("Camera processing failed: ${error.message}", generation)
                            Log.e("KumpasCamera", "Camera processing failed", error)
                        } finally {
                            if (upright != null && upright !== bitmap) upright?.recycle()
                            bitmap?.recycle()
                            image.close()
                        }
                    }
                    val selector = when {
                        cameraProvider.hasCamera(CameraSelector.DEFAULT_FRONT_CAMERA) -> CameraSelector.DEFAULT_FRONT_CAMERA
                        cameraProvider.hasCamera(CameraSelector.DEFAULT_BACK_CAMERA) -> CameraSelector.DEFAULT_BACK_CAMERA
                        else -> throw IllegalStateException("No camera available")
                    }
                    val camera = cameraProvider.bindToLifecycle(lifecycleOwner, selector, previewUseCase, analysisUseCase)
                    val info = Camera2CameraInfo.from(camera.cameraInfo)
                    val lens = when (info.getCameraCharacteristic(CameraCharacteristics.LENS_FACING)) {
                        CameraCharacteristics.LENS_FACING_FRONT -> "front"
                        CameraCharacteristics.LENS_FACING_BACK -> "back"
                        else -> "unknown"
                    }
                    benchmark?.recordCamera(if (selector == CameraSelector.DEFAULT_FRONT_CAMERA) "default_front" else "default_back_fallback",
                        lens, true, info.cameraId)
                } catch (error: Exception) {
                    benchmark?.recordCamera("unknown", "unknown", false, "unknown")
                    benchmark?.recordFailure(error.javaClass.simpleName)
                    engine.reportCameraError("Camera unavailable: ${error.message}", generation)
                    Log.e("KumpasCamera", "Camera bind failed", error)
                }
            }
        }, ContextCompat.getMainExecutor(context))
    }
    override fun getView(): View = previewView
    override fun dispose() {
        disposed = true
        benchmark?.recordCamera("unknown", "unknown", false, "unknown")
        analysis?.clearAnalyzer()
        val owned = listOfNotNull(preview, analysis).toTypedArray()
        if (owned.isNotEmpty()) provider?.unbind(*owned)
        engine.cancelAttempt()
        analysisExecutor.shutdown()
    }
}
