package com.kumpas.kumpas_app

import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.RuntimeEnvironment
import org.robolectric.annotation.Config
import java.util.concurrent.Executors

/** Calls actual engine.close/camera.dispose/Activity.onDestroy with injected
 * owned cleanup actions. Native constructors are unavailable on JVM.
 * Wired teardown coverage is not real CameraX/detector release acceptance. */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class ResourceCleanupTest {
    private val unsafeClass = Class.forName("sun.misc.Unsafe")
    private val unsafe = unsafeClass.getDeclaredField("theUnsafe").apply { isAccessible = true }.get(null)
    private fun <T : Any> blank(type: Class<T>): T = type.cast(unsafeClass.getMethod("allocateInstance", Class::class.java).invoke(unsafe, type))!!
    private fun set(target: Any, name: String, value: Any?) {
        target.javaClass.getDeclaredField(name).apply { isAccessible = true }.set(target, value)
    }
    private fun engine(calls: MutableList<String>, fail: Boolean): VisionEngine = blank(VisionEngine::class.java).also {
        set(it, "sharedLock", Any())
        set(it, "attemptSamples", arrayListOf<FloatArray>())
        set(it, "closeActions", listOf<() -> Unit>(
            { calls.add("pose"); if (fail) throw IllegalStateException("pose fault") },
            { calls.add("hand") }, { calls.add("interpreter") }))
    }
    @Test fun detectorFailureStillClosesEveryOwnedResourceAndRepeatIsSafe() {
        val calls = mutableListOf<String>()
        val engine = engine(calls, true)
        val error = assertThrows(IllegalStateException::class.java) { engine.close() }
        assertEquals("pose fault", error.message)
        assertEquals(listOf("pose", "hand", "interpreter"), calls)
        engine.close()
        assertEquals(3, calls.size)
    }
    @Test fun cameraClearAndUnbindFaultsStillCancelAndShutdown() {
        for (clear in listOf(true, false)) {
            val calls = mutableListOf<String>()
            val context = RuntimeEnvironment.getApplication()
            val engine = VisionEngine(context, resourceFactory = object : VisionResourceFactory {
                override fun pose() = OwnedNative<com.google.mediapipe.tasks.vision.poselandmarker.PoseLandmarker>(null) {}
                override fun hand() = OwnedNative<com.google.mediapipe.tasks.vision.handlandmarker.HandLandmarker>(null) {}
                override fun interpreter(model: java.nio.ByteBuffer) = OwnedNative<org.tensorflow.lite.Interpreter>(null) {}
                override fun asset(name: String) = java.io.ByteArrayInputStream(if (name.endsWith("json")) "{\"0\":{\"label\":\"ONE\"}}".toByteArray() else byteArrayOf(1))
            }, onResult = {})
            engine.startAttempt(0)
            val lifecycle = object : androidx.lifecycle.LifecycleOwner {
                override val lifecycle = androidx.lifecycle.LifecycleRegistry(this)
            }
            val camera = CameraPreviewView(context, lifecycle, engine, bindCamera = false,
                clearOwnedAnalyzer = { calls.add("clear"); if (clear) throw IllegalStateException("clear fault") },
                unbindOwnedUseCases = { calls.add("unbind"); if (!clear) throw IllegalStateException("unbind fault") })
            val executor = CameraPreviewView::class.java.getDeclaredField("analysisExecutor").apply { isAccessible = true }.get(camera) as java.util.concurrent.ExecutorService
            try {
                assertThrows(IllegalStateException::class.java) { camera.dispose() }
                assertEquals(listOf("clear", "unbind"), calls)
                assertTrue(executor.isShutdown)
                assertEquals(-1, VisionEngine::class.java.getDeclaredField("attemptTarget").apply { isAccessible = true }.getInt(engine))
                camera.dispose()
                assertEquals(2, calls.size)
            } finally { executor.shutdownNow(); engine.close() }
        }
    }
    @Test fun activityEngineAndBenchmarkCallbackFailuresStillAttemptFrameworkDestroy() {
        val calls = mutableListOf<String>()
        val activity = MainActivity()
        val benchmark = BenchmarkMode(RuntimeEnvironment.getApplication()) { throw IllegalArgumentException("callback fault") }
        benchmark.start(60)
        set(activity, "visionEngine", engine(calls, true))
        set(activity, "benchmarkMode", benchmark)
        val destroy = MainActivity::class.java.getDeclaredMethod("onDestroy").apply { isAccessible = true }
        val thrown = assertThrows(java.lang.reflect.InvocationTargetException::class.java) { destroy.invoke(activity) }
        val cause = thrown.cause!!
        assertEquals("pose fault", cause.message)
        assertFalse(benchmark.isActive)
        assertEquals(listOf("pose", "hand", "interpreter"), calls)
        assertTrue("benchmark failure lost", cause.suppressed.any { it.message == "callback fault" })
        // Bare Activity deliberately lacks Flutter delegate: the real super call
        // must be attempted and its failure retained, not skipped.
        assertTrue("framework destroy skipped", cause.suppressed.any { error -> error.stackTrace.any { it.className.contains("FlutterActivity") && it.methodName == "onDestroy" } })
        assertNotNull(benchmark.latestResults())
    }
}
