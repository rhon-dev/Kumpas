package com.kumpas.kumpas_app

import android.content.Context
import com.google.mediapipe.tasks.core.BaseOptions
import com.google.mediapipe.tasks.vision.core.RunningMode
import com.google.mediapipe.tasks.vision.handlandmarker.HandLandmarker
import com.google.mediapipe.tasks.vision.poselandmarker.PoseLandmarker
import org.tensorflow.lite.Interpreter
import java.io.InputStream
import java.nio.ByteBuffer

/** Nullable values permit synthetic constructor orchestration, never synthetic inference. */
class OwnedNative<T>(val value: T?, val release: () -> Unit)
interface VisionResourceFactory {
    fun pose(): OwnedNative<PoseLandmarker>
    fun hand(): OwnedNative<HandLandmarker>
    fun interpreter(model: ByteBuffer): OwnedNative<Interpreter>
    fun asset(name: String): InputStream
}
internal class AndroidVisionResourceFactory(private val context: Context) : VisionResourceFactory {
    override fun pose(): OwnedNative<PoseLandmarker> {
        val value = PoseLandmarker.createFromOptions(context, PoseLandmarker.PoseLandmarkerOptions.builder()
            .setBaseOptions(BaseOptions.builder().setModelAssetPath("pose_landmarker_lite.task").build())
            .setRunningMode(RunningMode.VIDEO).setNumPoses(1).build())
        return OwnedNative(value) { value.close() }
    }
    override fun hand(): OwnedNative<HandLandmarker> {
        val value = HandLandmarker.createFromOptions(context, HandLandmarker.HandLandmarkerOptions.builder()
            .setBaseOptions(BaseOptions.builder().setModelAssetPath("hand_landmarker.task").build())
            .setRunningMode(RunningMode.VIDEO).setNumHands(2).build())
        return OwnedNative(value) { value.close() }
    }
    override fun interpreter(model: ByteBuffer): OwnedNative<Interpreter> {
        val value = Interpreter(model, Interpreter.Options().apply { numThreads = 2 })
        return OwnedNative(value) { value.close() }
    }
    override fun asset(name: String) = context.assets.open(name)
}
