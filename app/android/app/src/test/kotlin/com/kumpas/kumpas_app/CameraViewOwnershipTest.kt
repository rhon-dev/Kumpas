package com.kumpas.kumpas_app

import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.RuntimeEnvironment
import org.robolectric.annotation.Config
import androidx.lifecycle.LifecycleOwner
import androidx.lifecycle.LifecycleRegistry
import java.io.ByteArrayInputStream
import java.nio.ByteBuffer
import com.google.mediapipe.tasks.vision.handlandmarker.HandLandmarker
import com.google.mediapipe.tasks.vision.poselandmarker.PoseLandmarker
import org.tensorflow.lite.Interpreter

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34], shadows = [CameraViewOwnershipTest.ProviderShadow::class])
class CameraViewOwnershipTest {
    /** Shadow only provider driver calls; real queued callback, use cases and view disposal execute. */
    @org.robolectric.annotation.Implements(androidx.camera.lifecycle.ProcessCameraProvider::class)
    class ProviderShadow {
        companion object {
            var binds = 0
            val unbound = mutableListOf<androidx.camera.core.UseCase>()
        }
        @org.robolectric.annotation.Implementation
        fun hasCamera(selector: androidx.camera.core.CameraSelector) = true
        @org.robolectric.annotation.Implementation
        fun bindToLifecycle(owner: LifecycleOwner, selector: androidx.camera.core.CameraSelector,
            vararg cases: androidx.camera.core.UseCase): androidx.camera.core.Camera {
            binds++
            throw IllegalStateException("synthetic bind failure")
        }
        @org.robolectric.annotation.Implementation
        fun unbind(vararg cases: androidx.camera.core.UseCase) { unbound.addAll(cases) }
    }

    @Test fun queuedProviderAndBindFailuresAreOwnedAndDisposeReleasesAcquiredUseCases() {
        for (fault in listOf("provider", "bind", "stale-provider", "stale-bind", "disposed")) {
            ProviderShadow.binds = 0
            ProviderShadow.unbound.clear()
            val events = mutableListOf<org.json.JSONObject>()
            val engine = engine { events.add(org.json.JSONObject(it)) }
            val future = com.google.common.util.concurrent.SettableFuture.create<androidx.camera.lifecycle.ProcessCameraProvider>()
            var listenerRegistered = false
            var ownedExecutor: java.util.concurrent.ExecutorService? = null
            val factory = object : CameraViewResourceFactory {
                override fun preview(context: android.content.Context) = AndroidCameraViewResourceFactory.preview(context)
                override fun executor() = java.util.concurrent.Executors.newSingleThreadExecutor().also { ownedExecutor = it }
                override fun provider(context: android.content.Context) = future
                override fun listen(future: com.google.common.util.concurrent.ListenableFuture<androidx.camera.lifecycle.ProcessCameraProvider>, callback: Runnable, executor: java.util.concurrent.Executor) {
                    listenerRegistered = true
                    // Explicit Handler queue keeps completion and callback execution separate.
                    future.addListener(callback) { task -> android.os.Handler(android.os.Looper.getMainLooper()).post(task) }
                }
            }
            val a = CameraPreviewView(context, lifecycle, engine, resourceFactory = factory)
            var b: CameraPreviewView? = null
            try {
                assertTrue(listenerRegistered)
                if (fault.contains("provider") || fault == "disposed") future.setException(IllegalStateException("provider completion"))
                else future.set(androidx.camera.lifecycle.ProcessCameraProvider::class.java.getDeclaredConstructor().apply { isAccessible = true }.newInstance())
                assertTrue(events.isEmpty())
                if (fault.startsWith("stale")) b = CameraPreviewView(context, lifecycle, engine, bindCamera = false)
                if (fault == "disposed") a.dispose()
                org.robolectric.Shadows.shadowOf(android.os.Looper.getMainLooper()).idle()
                if (fault.startsWith("stale") || fault == "disposed") {
                    assertTrue(events.isEmpty())
                    assertEquals(0, ProviderShadow.binds)
                    b?.let { assertTrue(it.runOwned {}) }
                } else {
                    assertEquals("camera_error", events.single().getString("state"))
                    assertTrue(events.single().has("viewOwner"))
                    assertEquals(if (fault == "bind") 1 else 0, ProviderShadow.binds)
                }
                a.dispose(); a.dispose()
                assertTrue(ownedExecutor!!.isShutdown)
                assertEquals(if (fault == "bind") 2 else 0, ProviderShadow.unbound.size)
                if (fault == "bind") {
                    assertTrue(ProviderShadow.unbound.any { it is androidx.camera.core.Preview })
                    assertTrue(ProviderShadow.unbound.any { it is androidx.camera.core.ImageAnalysis })
                }
            } finally { a.dispose(); b?.dispose(); engine.close() }
        }
    }

    private val context = RuntimeEnvironment.getApplication()
    private val lifecycle = object : LifecycleOwner {
        override val lifecycle = LifecycleRegistry(this)
    }
    private fun engine(onResult: (String) -> Unit = {}) = VisionEngine(context, resourceFactory = object : VisionResourceFactory {
        override fun pose() = OwnedNative<PoseLandmarker>(null) {}
        override fun hand() = OwnedNative<HandLandmarker>(null) {}
        override fun interpreter(model: ByteBuffer) = OwnedNative<Interpreter>(null) {}
        override fun asset(name: String) = ByteArrayInputStream(if (name.endsWith("json")) "{\"0\":{\"label\":\"ONE\"}}".toByteArray() else byteArrayOf(1))
    }, onResult = onResult)
    @Test fun actualProducerEmissionCarriesViewOwnerAcrossPostedActivityDelivery() {
        val activity = MainActivity()
        val delivered = mutableListOf<String>()
        val sink = object : io.flutter.plugin.common.EventChannel.EventSink {
            override fun success(event: Any?) { delivered.add(event as String) }
            override fun error(code: String, message: String?, details: Any?) { fail(code) }
            override fun endOfStream() {}
        }
        MainActivity::class.java.getDeclaredField("eventSink").apply { isAccessible = true }.set(activity, sink)
        val emit = MainActivity::class.java.getDeclaredMethod("handleVisionEvent", String::class.java).apply { isAccessible = true }
        val engine = engine { json -> emit.invoke(activity, json) }
        val owners = MainActivity::class.java.getDeclaredField("cameraViews").apply { isAccessible = true }.get(activity) as CameraViewOwnership
        val a = CameraPreviewView(context, lifecycle, engine, bindCamera = false, ownership = owners)
        var b: CameraPreviewView? = null
        try {
            assertTrue(a.runOwned {
                VisionEngine::class.java.getDeclaredMethod("emit", FloatArray::class.java, Long::class.javaPrimitiveType, Long::class.javaPrimitiveType, Int::class.javaPrimitiveType)
                    .apply { isAccessible = true }.invoke(engine, floatArrayOf(1f), 0L, 0L, 0)
                engine.reportCameraError("synthetic", 0)
            })
            b = CameraPreviewView(context, lifecycle, engine, bindCamera = false, ownership = owners)
            org.robolectric.Shadows.shadowOf(android.os.Looper.getMainLooper()).idle()
            assertTrue("actual A emission lost its view owner", delivered.isEmpty())
        } finally { a.dispose(); b?.dispose(); engine.close() }
    }

    @Test fun actualViewConstructionRollsBackAcquisitionsAndOnlyItsPublishedOwner() {
        for (stage in listOf("preview", "executor", "provider", "listener", "listener-newer")) {
            val engine = engine()
            var cancellations = 0
            val owners = CameraViewOwnership(Any()) { cancellations++ }
            val a = CameraPreviewView(context, lifecycle, engine, bindCamera = false, ownership = owners)
            val original = IllegalArgumentException("original-$stage")
            var acquiredExecutor: java.util.concurrent.ExecutorService? = null
            var newer: Long? = null
            val cleanups = mutableListOf<String>()
            val factory = object : CameraViewResourceFactory {
                override fun preview(context: android.content.Context): androidx.camera.view.PreviewView {
                    if (stage == "preview") throw original
                    return AndroidCameraViewResourceFactory.preview(context)
                }
                override fun executor(): java.util.concurrent.ExecutorService {
                    if (stage == "executor") throw original
                    return java.util.concurrent.Executors.newSingleThreadExecutor().also { acquiredExecutor = it }
                }
                override fun provider(context: android.content.Context): com.google.common.util.concurrent.ListenableFuture<androidx.camera.lifecycle.ProcessCameraProvider> {
                    if (stage == "provider") throw original
                    return com.google.common.util.concurrent.SettableFuture.create()
                }
                override fun listen(future: com.google.common.util.concurrent.ListenableFuture<androidx.camera.lifecycle.ProcessCameraProvider>, callback: Runnable, executor: java.util.concurrent.Executor) {
                    if (stage == "listener-newer") newer = owners.register()
                    throw original
                }
            }
            try {
                val thrown = assertThrows(IllegalArgumentException::class.java) {
                    CameraPreviewView(context, lifecycle, engine, ownership = owners, resourceFactory = factory,
                        clearOwnedAnalyzer = { cleanups.add("clear"); throw IllegalStateException("clear") },
                        unbindOwnedUseCases = { cleanups.add("unbind"); throw IllegalStateException("unbind") })
                }
                assertSame(original, thrown)
                if (acquiredExecutor != null) assertTrue("$stage leaked executor", acquiredExecutor!!.isShutdown)
                if (stage.startsWith("listener")) {
                    assertFalse("dead A restored", a.runOwned {})
                    assertEquals(listOf("clear", "unbind"), cleanups)
                    assertEquals(2, original.suppressed.size)
                    assertEquals(if (newer == null) 1 else 0, cancellations)
                    if (newer != null) assertTrue(owners.run(newer!!) {})
                } else {
                    assertTrue("early $stage displaced viable A", a.runOwned {})
                    assertEquals(0, cancellations)
                }
            } finally {
                a.dispose(); acquiredExecutor?.shutdown(); engine.close()
            }
        }
    }

    @Test fun queuedCallbacksCannotMutateReplacementAndCurrentDisposalInvalidatesActivityBoundary() {
        val engine = engine()
        val activity = MainActivity()
        MainActivity::class.java.getDeclaredField("visionEngine").apply { isAccessible = true }.set(activity, engine)
        val attempts = MainActivity::class.java.getDeclaredField("attempts").apply { isAccessible = true }.get(activity) as AttemptBoundary
        val ownership = MainActivity::class.java.getDeclaredField("cameraViews").apply { isAccessible = true }.get(activity) as CameraViewOwnership
        val benchmark = BenchmarkMode(context)
        MainActivity::class.java.getDeclaredField("benchmarkMode").apply { isAccessible = true }.set(activity, benchmark)
        val a = CameraPreviewView(context, lifecycle, engine, benchmark, bindCamera = false, ownership = ownership)
        val b = CameraPreviewView(context, lifecycle, engine, benchmark, bindCamera = false, ownership = ownership)
        benchmark.start(60)
        val id = attempts.start(0)
        engine.startAttempt(0, id)
        benchmark.recordAttemptStart(id, android.os.SystemClock.elapsedRealtimeNanos())
        try {
            for (callback in listOf<() -> Unit>(
                { benchmark.recordCamera("unknown", "unknown", false, "A") },
                { benchmark.recordAnalyzer(); engine.tick() },
                { benchmark.recordFailure("SecurityException"); engine.reportCameraError("stale") })) {
                assertFalse(a.runOwned(callback))
            }
            assertEquals(id, attempts.currentId)
            assertTrue(b.runOwned { benchmark.recordCamera("default_front", "front", true, "B"); benchmark.recordAnalyzer() })
            a.dispose()
            assertEquals(id, attempts.currentId)
            b.dispose()
            assertNull(attempts.currentId)
            assertFalse(b.runOwned { fail("disposed-before-bind callback executed") })
            b.dispose()
            val c = CameraPreviewView(context, lifecycle, engine, benchmark, bindCamera = false, ownership = ownership)
            assertFalse(b.runOwned { fail("old callback after new current") })
            assertTrue(c.runOwned {})
            c.dispose()
            org.robolectric.Shadows.shadowOf(android.os.Looper.getMainLooper()).idleFor(java.time.Duration.ofMillis(1))
            val report = org.json.JSONObject(benchmark.finish())
            assertEquals(1, report.getInt("analyzer_count"))
            assertEquals(0, report.getInt("failure_count"))
            assertEquals("cancelled", report.getJSONArray("outcomes").getJSONObject(0).getString("code"))
        } finally { a.dispose(); b.dispose(); engine.close() }
    }

    @Test fun defaultOwnedResourceFailuresStillUnbindAndShutdownWithoutCancellingReplacement() {
        for (failClear in listOf(true, false)) {
            val engine = engine()
            val calls = mutableListOf<String>()
            val a = CameraPreviewView(context, lifecycle, engine, bindCamera = false,
                clearOwnedAnalyzer = { calls.add("clear"); if (failClear) throw IllegalStateException("clear") },
                unbindOwnedUseCases = { calls.add("unbind"); if (!failClear) throw IllegalStateException("unbind") })
            val b = CameraPreviewView(context, lifecycle, engine, bindCamera = false)
            try {
                engine.startAttempt(0)
                assertThrows(IllegalStateException::class.java) { a.dispose() }
                assertEquals(listOf("clear", "unbind"), calls)
                assertEquals(0, VisionEngine::class.java.getDeclaredField("attemptTarget").apply { isAccessible = true }.getInt(engine))
                val executor = CameraPreviewView::class.java.getDeclaredField("analysisExecutor").apply { isAccessible = true }.get(a) as java.util.concurrent.ExecutorService
                assertTrue(executor.isShutdown)
                a.dispose()
                assertEquals(2, calls.size)
            } finally { a.dispose(); b.dispose(); engine.close() }
        }
    }

    @Test fun staleDefaultDisposePreservesReplacementCaptureCameraAndLedger() {
        val engine = engine()
        val benchmark = BenchmarkMode(context)
        val a = CameraPreviewView(context, lifecycle, engine, benchmark, bindCamera = false)
        val b = CameraPreviewView(context, lifecycle, engine, benchmark, bindCamera = false)
        try {
            benchmark.recordCamera("default_front", "front", true, "B")
            benchmark.start(60)
            val id = engine.startAttempt(0)
            benchmark.recordAttemptStart(id, android.os.SystemClock.elapsedRealtimeNanos())
            a.dispose()
            a.dispose()
            val target = VisionEngine::class.java.getDeclaredField("attemptTarget").apply { isAccessible = true }.getInt(engine)
            assertEquals("stale default disposal cancelled B", 0, target)
            val report = org.json.JSONObject(benchmark.finish())
            val expected = "camera2-sha256:" + java.security.MessageDigest.getInstance("SHA-256")
                .digest("B".toByteArray()).joinToString("") { "%02x".format(it.toInt() and 0xff) }
            assertEquals(expected, report.getJSONObject("camera").getString("camera_id"))
            assertFalse(report.getJSONObject("camera").getBoolean("changed"))
            assertEquals(1, report.getInt("attempt_count"))
        } finally { a.dispose(); b.dispose(); engine.close() }
    }
}
