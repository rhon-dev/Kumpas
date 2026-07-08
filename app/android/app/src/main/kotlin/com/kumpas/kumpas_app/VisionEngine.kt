package com.kumpas.kumpas_app

import android.content.Context
import android.os.SystemClock
import com.google.mediapipe.framework.image.BitmapImageBuilder
import com.google.mediapipe.framework.image.MPImage
import com.google.mediapipe.tasks.core.BaseOptions
import com.google.mediapipe.tasks.vision.core.RunningMode
import com.google.mediapipe.tasks.vision.handlandmarker.HandLandmarker
import com.google.mediapipe.tasks.vision.poselandmarker.PoseLandmarker
import org.json.JSONObject
import org.tensorflow.lite.Interpreter
import java.nio.ByteBuffer
import java.nio.ByteOrder

/**
 * Camera frame -> MediaPipe (pose + hands) -> 258-dim feature vector ->
 * ring buffer (30 samples, stride-sampled) -> TFLite CNN-LSTM -> prediction.
 *
 * Feature layout and normalization MUST mirror training/preprocessing/build_sequences.py
 * (no_face variant): pose 33*(x,y,z,visibility)=132, left hand 21*3=63,
 * right hand 21*3=63; per-frame mid-hip centering and torso scaling;
 * missing detections stay all-zero.
 *
 * Training clips were ~4s sampled to 30 frames (~7.5 samples/s). Live pipeline
 * matches that timescale: one buffer sample every SAMPLE_STRIDE analysis
 * frames (~30fps camera / 4 = 7.5/s), so a full buffer spans ~4s.
 */
class VisionEngine(context: Context, private val onResult: (String) -> Unit) {

    private val appContext: Context = context.applicationContext

    companion object {
        const val SEQ_LEN = 30
        const val N_FEATURES = 258
        const val SAMPLE_STRIDE = 4   // analysis frames per buffer sample
        const val INFER_EVERY = 4     // buffer samples between inferences (~0.5s)
        const val L_SHOULDER = 11; const val R_SHOULDER = 12
        const val L_HIP = 23; const val R_HIP = 24
    }

    private val poseLandmarker: PoseLandmarker
    private val handLandmarker: HandLandmarker
    private val tflite: Interpreter
    private val labels: List<String>

    private val buffer = ArrayDeque<FloatArray>()  // SEQ_LEN newest samples
    private val bufferPoseSeen = ArrayDeque<Boolean>()
    private var frameCount = 0
    private var samplesSinceInfer = 0
    private var lastFpsTime = SystemClock.elapsedRealtime()
    private var fpsFrames = 0
    private var cameraFps = 0.0

    // Attempt mode (Phase 7): collect one fresh window, then classify +
    // compare against the target's gold standard.
    private var attemptTarget = -1
    private var attemptSamples = ArrayList<FloatArray>()
    private var attemptPoseFrames = 0
    private val goldStandards: Array<Array<FloatArray>> by lazy { loadGold() }

    private fun loadGold(): Array<Array<FloatArray>> {
        val bytes = appContext.assets.open("gold_standards.bin").readBytes()
        val buf = ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN)
        return Array(50) { Array(SEQ_LEN) { FloatArray(N_FEATURES) { buf.float } } }
    }

    fun labelsJson(): String {
        val ctx = appContext
        return ctx.assets.open("label_map.json").readBytes().decodeToString()
    }

    @Synchronized
    fun startAttempt(classId: Int) {
        attemptTarget = classId
        attemptSamples = ArrayList()
        attemptPoseFrames = 0
    }

    @Synchronized
    fun cancelAttempt() { attemptTarget = -1 }

    init {
        poseLandmarker = PoseLandmarker.createFromOptions(
            context,
            PoseLandmarker.PoseLandmarkerOptions.builder()
                .setBaseOptions(BaseOptions.builder().setModelAssetPath("pose_landmarker_lite.task").build())
                .setRunningMode(RunningMode.VIDEO)
                .setNumPoses(1)
                .build()
        )
        handLandmarker = HandLandmarker.createFromOptions(
            context,
            HandLandmarker.HandLandmarkerOptions.builder()
                .setBaseOptions(BaseOptions.builder().setModelAssetPath("hand_landmarker.task").build())
                .setRunningMode(RunningMode.VIDEO)
                .setNumHands(2)
                .build()
        )
        val modelBytes = context.assets.open("kumpas_50sign.tflite").readBytes()
        val bb = ByteBuffer.allocateDirect(modelBytes.size).order(ByteOrder.nativeOrder())
        bb.put(modelBytes); bb.rewind()
        tflite = Interpreter(bb, Interpreter.Options().apply { numThreads = 2 })

        val lm = JSONObject(context.assets.open("label_map.json").readBytes().decodeToString())
        labels = (0 until lm.length()).map { lm.getJSONObject(it.toString()).getString("label") }
    }

    /**
     * Frame tick at full camera rate. Returns true when this frame should be
     * converted to a bitmap and processed — callers must NOT allocate before
     * asking (bitmap conversion per frame caused GC pressure at 30fps).
     */
    fun tick(): Boolean {
        frameCount++
        fpsFrames++
        val now = SystemClock.elapsedRealtime()
        if (now - lastFpsTime >= 1000) {
            cameraFps = fpsFrames * 1000.0 / (now - lastFpsTime)
            fpsFrames = 0; lastFpsTime = now
        }
        return frameCount % SAMPLE_STRIDE == 0
    }

    /** Called on the ImageAnalysis thread with an upright RGBA bitmap (sampled frames only). */
    fun onFrame(bitmap: android.graphics.Bitmap, timestampMs: Long) {
        val mp: MPImage = BitmapImageBuilder(bitmap).build()
        val t0 = SystemClock.elapsedRealtime()
        val pose = poseLandmarker.detectForVideo(mp, timestampMs)
        val hands = handLandmarker.detectForVideo(mp, timestampMs)
        val landmarkMs = SystemClock.elapsedRealtime() - t0

        val feat = FloatArray(N_FEATURES)
        var poseSeen = false
        if (pose.landmarks().isNotEmpty()) {
            poseSeen = true
            val lms = pose.landmarks()[0]
            for (i in lms.indices) {
                feat[i * 4] = lms[i].x(); feat[i * 4 + 1] = lms[i].y()
                feat[i * 4 + 2] = lms[i].z()
                feat[i * 4 + 3] = pose.landmarks()[0][i].visibility().orElse(0f)
            }
        }
        var handsSeen = 0
        for (h in hands.landmarks().indices) {
            val handed = hands.handedness()[h][0].categoryName() // "Left"/"Right"
            val base = if (handed == "Left") 132 else 132 + 63
            val lms = hands.landmarks()[h]
            for (i in lms.indices) {
                feat[base + i * 3] = lms[i].x(); feat[base + i * 3 + 1] = lms[i].y()
                feat[base + i * 3 + 2] = lms[i].z()
            }
            handsSeen++
        }

        normalize(feat, poseSeen)
        buffer.addLast(feat)
        bufferPoseSeen.addLast(poseSeen)
        if (buffer.size > SEQ_LEN) { buffer.removeFirst(); bufferPoseSeen.removeFirst() }
        samplesSinceInfer++

        if (attemptTarget >= 0) {
            handleAttemptSample(feat, poseSeen, landmarkMs, handsSeen)
            return
        }

        val poseRate = bufferPoseSeen.count { it }.toDouble() / bufferPoseSeen.size
        if (buffer.size == SEQ_LEN && samplesSinceInfer >= INFER_EVERY) {
            samplesSinceInfer = 0
            if (poseRate < 0.5) {
                // no signer in frame — don't classify zeros (confident garbage)
                onResult(JSONObject(mapOf(
                    "state" to "no_signer", "cameraFps" to cameraFps,
                    "landmarkMs" to landmarkMs, "handsVisible" to handsSeen
                )).toString())
                return
            }
            val input = Array(1) { Array(SEQ_LEN) { s -> buffer.elementAt(s) } }
            val output = Array(1) { FloatArray(labels.size) }
            val t1 = SystemClock.elapsedRealtime()
            tflite.run(input, output)
            val inferMs = SystemClock.elapsedRealtime() - t1
            android.util.Log.i("KumpasVision",
                "fps=%.1f landmarkMs=%d inferMs=%d hands=%d".format(cameraFps, landmarkMs, inferMs, handsSeen))
            emit(output[0], landmarkMs, inferMs, handsSeen)
        } else {
            // keep UI stats alive while the buffer warms up
            onResult(JSONObject(mapOf(
                "state" to "warmup", "bufferFill" to buffer.size,
                "cameraFps" to cameraFps, "landmarkMs" to landmarkMs,
                "handsVisible" to handsSeen
            )).toString())
        }
    }

    private fun handleAttemptSample(feat: FloatArray, poseSeen: Boolean,
                                    landmarkMs: Long, handsSeen: Int) {
        attemptSamples.add(feat)
        if (poseSeen) attemptPoseFrames++
        if (attemptSamples.size < SEQ_LEN) {
            onResult(JSONObject(mapOf(
                "state" to "attempt_progress", "collected" to attemptSamples.size,
                "needed" to SEQ_LEN, "cameraFps" to cameraFps,
                "landmarkMs" to landmarkMs, "handsVisible" to handsSeen
            )).toString())
            return
        }
        val target = attemptTarget
        attemptTarget = -1
        val window = attemptSamples.toTypedArray()

        if (attemptPoseFrames < SEQ_LEN / 2) {
            onResult(JSONObject(mapOf(
                "state" to "attempt_failed",
                "reason" to "No signer detected — stand in front of the camera and try again."
            )).toString())
            return
        }

        val input = Array(1) { window }
        val output = Array(1) { FloatArray(labels.size) }
        tflite.run(input, output)
        val probs = output[0]
        val best = probs.indices.maxByOrNull { probs[it] } ?: 0

        val report = FeedbackEngine.compare(window, goldStandards[target], labels[target])
        onResult(JSONObject(mapOf(
            "state" to "attempt_result",
            "targetClass" to target,
            "targetLabel" to labels[target],
            "predictedLabel" to labels[best],
            "predictedConfidence" to probs[best].toDouble(),
            "recognizedAsTarget" to (best == target),
            "overallMatch" to report.overallMatch,
            "items" to report.items.map { mapOf(
                "dimension" to it.dimension, "severity" to it.severity,
                "hand" to it.hand, "prompt" to it.prompt) }
        )).toString())
    }

    /** Port of build_sequences.py normalize(): mid-hip center, torso scale. */
    private fun normalize(f: FloatArray, poseSeen: Boolean) {
        if (!poseSeen) return  // all-zero frame stays all-zero (matches training)
        val rootX = (f[L_HIP * 4] + f[R_HIP * 4]) / 2f
        val rootY = (f[L_HIP * 4 + 1] + f[R_HIP * 4 + 1]) / 2f
        val rootZ = (f[L_HIP * 4 + 2] + f[R_HIP * 4 + 2]) / 2f
        val neckX = (f[L_SHOULDER * 4] + f[R_SHOULDER * 4]) / 2f
        val neckY = (f[L_SHOULDER * 4 + 1] + f[R_SHOULDER * 4 + 1]) / 2f
        val neckZ = (f[L_SHOULDER * 4 + 2] + f[R_SHOULDER * 4 + 2]) / 2f
        var scale = kotlin.math.sqrt(
            (neckX - rootX) * (neckX - rootX) + (neckY - rootY) * (neckY - rootY) +
            (neckZ - rootZ) * (neckZ - rootZ)
        )
        if (scale < 1e-4f) scale = 1f
        for (i in 0 until 33) {
            f[i * 4] = (f[i * 4] - rootX) / scale
            f[i * 4 + 1] = (f[i * 4 + 1] - rootY) / scale
            f[i * 4 + 2] = (f[i * 4 + 2] - rootZ) / scale
        }
        for (handBase in intArrayOf(132, 132 + 63)) {
            var zero = true
            for (i in 0 until 63) if (f[handBase + i] != 0f) { zero = false; break }
            if (zero) continue  // missing hand stays zero
            for (i in 0 until 21) {
                f[handBase + i * 3] = (f[handBase + i * 3] - rootX) / scale
                f[handBase + i * 3 + 1] = (f[handBase + i * 3 + 1] - rootY) / scale
                f[handBase + i * 3 + 2] = (f[handBase + i * 3 + 2] - rootZ) / scale
            }
        }
    }

    private fun emit(probs: FloatArray, landmarkMs: Long, inferMs: Long, handsSeen: Int) {
        val idx = probs.indices.sortedByDescending { probs[it] }.take(3)
        onResult(JSONObject(mapOf(
            "state" to "prediction",
            "label" to labels[idx[0]],
            "confidence" to probs[idx[0]].toDouble(),
            "top3" to idx.map { mapOf("label" to labels[it], "p" to probs[it].toDouble()) },
            "cameraFps" to cameraFps,
            "landmarkMs" to landmarkMs,
            "inferMs" to inferMs,
            "handsVisible" to handsSeen
        )).toString())
    }

    fun close() {
        poseLandmarker.close(); handLandmarker.close(); tflite.close()
    }
}
