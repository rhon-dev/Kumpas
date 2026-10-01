package com.kumpas.kumpas_app.benchmark

import android.graphics.BitmapFactory
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.kumpas.kumpas_app.VisionEngine
import org.json.JSONArray
import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import java.io.File
import java.security.MessageDigest

/** Replay external PNGs through the production detector and feature normalizer.
 * Inputs/outputs stay in app-specific storage, never in the APK or Git.
 * Host must push manifest and PNGs to externalFilesDir/parity/input first.
 */
@RunWith(AndroidJUnit4::class)
class PipelineParityTest {
    @Test fun replayHashedFrames() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val root = File(requireNotNull(context.getExternalFilesDir(null)), "parity")
        val input = File(root, "input")
        val manifest = JSONObject(File(input, "manifest.json").readText())
        assertEquals("kumpas-replay-v1", manifest.getString("schema"))
        val listed = manifest.getJSONArray("frames")
        assertTrue("empty replay", listed.length() > 0)
        val rows = JSONArray()
        val engine = VisionEngine(context) { }
        try {
            for (i in 0 until listed.length()) {
                val entry = listed.getJSONObject(i)
                assertEquals("ordered frame index", i, entry.getInt("index"))
                val filename = entry.getString("filename")
                assertTrue("unsafe filename", Regex("frame_[0-9]{5}\\.png").matches(filename))
                val bytes = File(input, filename).readBytes()
                val digest = MessageDigest.getInstance("SHA-256").digest(bytes)
                    .joinToString("") { "%02x".format(it) }
                assertEquals("frame $i hash mismatch", entry.getString("sha256"), digest)
                val bitmap = requireNotNull(BitmapFactory.decodeByteArray(bytes, 0, bytes.size))
                val extracted = engine.extractFrame(bitmap, i.toLong() + 1L)
                bitmap.recycle()
                assertEquals(VisionEngine.N_FEATURES, extracted.features.size)
                rows.put(JSONObject().apply {
                    put("index", i)
                    put("sha256", digest)
                    put("pose_seen", extracted.poseSeen)
                    put("left_seen", extracted.leftSeen)
                    put("right_seen", extracted.rightSeen)
                    put("features", JSONArray(extracted.features.map { it.toDouble() }))
                })
            }
        } finally {
            engine.close()
        }
        val targetClass = requireNotNull(
            InstrumentationRegistry.getArguments().getString("targetClass")
        ) { "pass -e targetClass with the known dense class ID" }.toInt()
        var attemptResult: JSONObject? = null
        val attemptEngine = VisionEngine(context) { event ->
            val obj = JSONObject(event)
            if (obj.optString("state") == "attempt_result") attemptResult = obj
        }
        try {
            attemptEngine.startAttempt(targetClass)
            for (i in 0 until listed.length()) {
                val bytes = File(input, listed.getJSONObject(i).getString("filename")).readBytes()
                val bitmap = requireNotNull(BitmapFactory.decodeByteArray(bytes, 0, bytes.size))
                attemptEngine.onFrame(bitmap, i.toLong() + 1L)
                bitmap.recycle()
            }
        } finally {
            attemptEngine.close()
        }
        assertTrue("expected exactly 30 frames", listed.length() == VisionEngine.SEQ_LEN)
        assertEquals(targetClass, requireNotNull(attemptResult).getInt("targetClass"))
        val output = File(requireNotNull(context.getExternalFilesDir(null)), "android_features.json")
        output.writeText(JSONObject().apply {
            put("schema", "kumpas-android-replay-v1")
            put("extractor", "Android live VisionEngine pose+hand")
            put("anatomical_left_right", "unverified")
            put("frames", rows)
            put("attempt_result", attemptResult)
        }.toString())
    }
}
