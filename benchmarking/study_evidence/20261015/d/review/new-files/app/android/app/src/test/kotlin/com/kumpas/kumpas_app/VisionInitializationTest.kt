package com.kumpas.kumpas_app

import com.google.mediapipe.tasks.vision.handlandmarker.HandLandmarker
import com.google.mediapipe.tasks.vision.poselandmarker.PoseLandmarker
import org.tensorflow.lite.Interpreter
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.RuntimeEnvironment
import org.robolectric.annotation.Config
import java.io.ByteArrayInputStream
import java.io.InputStream
import java.nio.ByteBuffer

/** Actual VisionEngine constructor with synthetic owned native handles; no inference/device claims. */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class VisionInitializationTest {
    private class Factory(val failAt: String? = null, val closeFailures: Set<String> = emptySet()) : VisionResourceFactory {
        val closed = mutableListOf<String>()
        val failure = IllegalArgumentException("original initialization failure")
        private fun stage(name: String) { if (failAt == name) throw failure }
        private fun release(name: String) { closed.add(name); if (name in closeFailures) throw IllegalStateException("release $name") }
        override fun pose() = OwnedNative<PoseLandmarker>(null) { release("pose") }.also { stage("pose") }
        override fun hand() = OwnedNative<HandLandmarker>(null) { release("hand") }.also { stage("hand") }
        override fun interpreter(model: ByteBuffer) = OwnedNative<Interpreter>(null) { release("interpreter") }.also { stage("interpreter") }
        override fun asset(name: String): InputStream {
            val tag = if (name.endsWith("tflite")) "model" else "labels"
            stage("open-$tag")
            val bytes = if (tag == "model") byteArrayOf(1) else if (failAt == "parse-labels") "bad".toByteArray() else "{\"0\":{\"label\":\"ONE\"}}".toByteArray()
            return object : ByteArrayInputStream(bytes) {
                override fun read(b: ByteArray, off: Int, len: Int): Int { stage("read-$tag"); return super.read(b, off, len) }
                override fun close() { release(tag) }
            }
        }
    }
    @Test fun runtimeLabelAndGoldAssetStreamsCloseOnSuccessReadAndParseFailure() {
        for (asset in listOf("label_map.json", "gold_standards.bin")) {
            for (fault in listOf("success", "read", "parse")) {
                var runtime = false
                var closedStreams = 0
                val original = IllegalStateException("runtime read failure")
                val factory = object : VisionResourceFactory {
                    override fun pose() = OwnedNative<PoseLandmarker>(null) {}
                    override fun hand() = OwnedNative<HandLandmarker>(null) {}
                    override fun interpreter(model: ByteBuffer) = OwnedNative<Interpreter>(null) {}
                    override fun asset(name: String): InputStream {
                        val bytes = if (name == "gold_standards.bin") {
                            if (fault == "parse") byteArrayOf(1) else ByteArray(50 * VisionEngine.SEQ_LEN * VisionEngine.N_FEATURES * 4)
                        } else if (name.endsWith("json")) "{\"0\":{\"label\":\"ONE\"}}".toByteArray() else byteArrayOf(1)
                        return object : ByteArrayInputStream(bytes) {
                            override fun read(b: ByteArray, off: Int, len: Int): Int {
                                if (runtime && fault == "read") throw original
                                return super.read(b, off, len)
                            }
                            override fun close() { if (runtime) closedStreams++ }
                        }
                    }
                }
                val engine = VisionEngine(RuntimeEnvironment.getApplication(), resourceFactory = factory, onResult = {})
                runtime = true
                try {
                    val call = {
                        if (asset.endsWith("json")) engine.labelsJson()
                        else VisionEngine::class.java.getDeclaredMethod("loadGold").apply { isAccessible = true }.invoke(engine)
                        Unit
                    }
                    if (fault == "read" || (fault == "parse" && asset.endsWith("bin"))) assertThrows(Exception::class.java) { call() }
                    else call()
                    assertEquals("$asset/$fault runtime stream not closed", 1, closedStreams)
                } finally { engine.close() }
            }
        }
    }

    @Test fun stagedConstructorFailuresRollbackAllAcquiredResourcesAndStreams() {
        for ((stage, expected) in listOf(
            "pose" to emptyList(), "hand" to listOf("pose"),
            "open-model" to listOf("pose", "hand"), "read-model" to listOf("model", "pose", "hand"),
            "interpreter" to listOf("model", "pose", "hand"),
            "open-labels" to listOf("model", "pose", "hand", "interpreter"),
            "read-labels" to listOf("model", "labels", "pose", "hand", "interpreter"),
            "parse-labels" to listOf("model", "labels", "pose", "hand", "interpreter"))) {
            val factory = Factory(stage)
            val thrown = assertThrows(Exception::class.java) { VisionEngine(RuntimeEnvironment.getApplication(), resourceFactory = factory, onResult = {}) }
            if (stage != "parse-labels") assertSame(factory.failure, thrown)
            assertEquals(stage, expected, factory.closed)
        }
    }
    @Test fun rollbackKeepsOriginalFailureAndSuppressesEveryLaterReleaseFailure() {
        val factory = Factory("open-labels", setOf("pose", "hand", "interpreter"))
        val thrown = assertThrows(IllegalArgumentException::class.java) { VisionEngine(RuntimeEnvironment.getApplication(), resourceFactory = factory, onResult = {}) }
        assertSame(factory.failure, thrown)
        assertEquals(listOf("model", "pose", "hand", "interpreter"), factory.closed)
        assertEquals(3, thrown.suppressed.size)
    }
    @Test fun constructorStreamCloseAndReadCloseFaultsPreservePrimaryAndReleaseNativeHandles() {
        for (tag in listOf("model", "labels")) {
            for (readFails in listOf(false, true)) {
                val native = if (tag == "model") listOf("pose", "hand") else listOf("pose", "hand", "interpreter")
                val factory = Factory(if (readFails) "read-$tag" else null, (native + tag).toSet())
                val thrown = assertThrows(Exception::class.java) {
                    VisionEngine(RuntimeEnvironment.getApplication(), resourceFactory = factory, onResult = {})
                }
                if (readFails) assertSame(factory.failure, thrown)
                else assertEquals("release $tag", thrown.message)
                assertEquals(if (tag == "model") listOf("model") + native else listOf("model", "labels") + native, factory.closed)
                assertEquals(native.size + if (readFails) 1 else 0, thrown.suppressed.size)
            }
        }
    }

    @Test fun runtimeLabelsAndGoldCloseFaultsSuppressUnderReadFailureWithoutClosingEngine() {
        for (asset in listOf("label_map.json", "gold_standards.bin")) {
            for (readFails in listOf(false, true)) {
                var runtime = false
                var streamCloses = 0
                val nativeCloses = mutableListOf<String>()
                val readFailure = IllegalArgumentException("read")
                val closeFailure = IllegalStateException("close")
                val factory = object : VisionResourceFactory {
                    override fun pose() = OwnedNative<PoseLandmarker>(null) { nativeCloses.add("pose") }
                    override fun hand() = OwnedNative<HandLandmarker>(null) { nativeCloses.add("hand") }
                    override fun interpreter(model: ByteBuffer) = OwnedNative<Interpreter>(null) { nativeCloses.add("interpreter") }
                    override fun asset(name: String): InputStream {
                        val bytes = if (name.endsWith("json")) "{\"0\":{\"label\":\"ONE\"}}".toByteArray()
                            else if (name.endsWith("bin")) ByteArray(50 * VisionEngine.SEQ_LEN * VisionEngine.N_FEATURES * 4) else byteArrayOf(1)
                        return object : ByteArrayInputStream(bytes) {
                            override fun read(b: ByteArray, off: Int, len: Int): Int {
                                if (runtime && readFails) throw readFailure
                                return super.read(b, off, len)
                            }
                            override fun close() { if (runtime) { streamCloses++; throw closeFailure } }
                        }
                    }
                }
                val engine = VisionEngine(RuntimeEnvironment.getApplication(), resourceFactory = factory, onResult = {})
                runtime = true
                try {
                    val thrown = assertThrows(Exception::class.java) {
                        if (asset.endsWith("json")) engine.labelsJson()
                        else try {
                            VisionEngine::class.java.getDeclaredMethod("loadGold").apply { isAccessible = true }.invoke(engine)
                        } catch (wrapped: java.lang.reflect.InvocationTargetException) { throw wrapped.targetException }
                    }
                    assertSame(if (readFails) readFailure else closeFailure, thrown)
                    assertEquals(if (readFails) listOf(closeFailure) else emptyList<Throwable>(), thrown.suppressed.toList())
                    assertEquals(1, streamCloses)
                    assertTrue(nativeCloses.isEmpty())
                    engine.startAttempt(0)
                } finally { engine.close(); engine.close() }
                assertEquals(listOf("pose", "hand", "interpreter"), nativeCloses)
            }
        }
    }

    @Test fun successfulConstructionTransfersOwnershipAndRepeatCloseIsSafe() {
        val factory = Factory()
        val engine = VisionEngine(RuntimeEnvironment.getApplication(), resourceFactory = factory, onResult = {})
        assertEquals(listOf("model", "labels"), factory.closed)
        engine.startAttempt(0)
        engine.close()
        engine.close()
        assertEquals(listOf("model", "labels", "pose", "hand", "interpreter"), factory.closed)
    }
}
