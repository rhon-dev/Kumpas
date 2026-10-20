package com.kumpas.kumpas_app

import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

/** Calls the same acquisition/registration transaction as configureFlutterEngine; no default stores. */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class ActivityInitializationTest {
    private class Factory(val failAt: String? = null, val releaseFails: Boolean = false) : ActivityResourceFactory {
        val original = IllegalArgumentException("initialization")
        val acquired = mutableListOf<String>()
        val closed = mutableListOf<String>()
        private fun stage(name: String) { if (name == failAt) throw original; acquired.add(name) }
        private fun release(name: String) { closed.add(name); if (releaseFails) throw IllegalStateException(name) }
        override fun session(): OwnedNative<SessionManager> { stage("session"); return OwnedNative(null) { release("session") } }
        override fun exporter(): DataExporter? { stage("exporter"); return null }
        override fun benchmark(): OwnedNative<BenchmarkMode> { stage("benchmark"); return OwnedNative(null) { release("benchmark") } }
        override fun vision(): OwnedNative<VisionEngine> { stage("vision"); return OwnedNative(null) { release("vision") } }
    }
    private fun sink() = object : io.flutter.plugin.common.EventChannel.EventSink {
        override fun success(event: Any?) {}
        override fun error(code: String, message: String?, details: Any?) {}
        override fun endOfStream() {}
    }
    private fun setSink(activity: MainActivity, sink: io.flutter.plugin.common.EventChannel.EventSink?) =
        MainActivity::class.java.getDeclaredField("eventSink").apply { isAccessible = true }.set(activity, sink)
    private fun getSink(activity: MainActivity) =
        MainActivity::class.java.getDeclaredField("eventSink").apply { isAccessible = true }.get(activity)

    private fun collectingSink(events: MutableList<String>) = object : io.flutter.plugin.common.EventChannel.EventSink {
        override fun success(event: Any?) { events.add(event as String) }
        override fun error(code: String, message: String?, details: Any?) {}
        override fun endOfStream() {}
    }
    private fun prediction(activity: MainActivity) {
        MainActivity::class.java.getDeclaredMethod("handleVisionEvent", String::class.java).apply { isAccessible = true }
            .invoke(activity, "{\"state\":\"prediction\"}")
    }
    private fun drain() = org.robolectric.Shadows.shadowOf(android.os.Looper.getMainLooper()).idle()

    @Test fun successfulReplacementCannotInheritDisplacedSubscriberBeforeNewListen() {
        val activity = MainActivity()
        val oldEvents = mutableListOf<String>()
        val newEvents = mutableListOf<String>()
        val a = Factory()
        val b = Factory()
        val ownerB = MainActivity.Initialization()
        activity.initializeResources(a) { setSink(activity, collectingSink(oldEvents)) }
        prediction(activity)
        drain()
        assertEquals(1, oldEvents.size)
        oldEvents.clear()

        activity.initializeResources(b, ownerB) { /* B has not listened. */ }
        prediction(activity)
        drain()
        assertTrue("B prediction leaked to displaced A subscriber: $oldEvents", oldEvents.isEmpty())
        assertTrue(activity.isCurrent(ownerB))
        assertEquals(listOf("session", "benchmark", "vision"), a.closed)
        assertTrue(b.closed.isEmpty())

        setSink(activity, collectingSink(newEvents)) // Existing honest subscription seam, no BinaryMessenger claim.
        prediction(activity)
        drain()
        assertEquals(1, newEvents.size)
        assertEquals("prediction", org.json.JSONObject(newEvents.single()).getString("state"))
        assertTrue(oldEvents.isEmpty())
    }

    @Test fun reentrantFailedOlderRegistrationCannotLeakItsSubscriberIntoNewerOwner() {
        val activity = MainActivity()
        val a = Factory()
        val b = Factory()
        val ownerB = MainActivity.Initialization()
        val oldEvents = mutableListOf<String>()
        val newEvents = mutableListOf<String>()
        val attempts = MainActivity::class.java.getDeclaredField("attempts").apply { isAccessible = true }.get(activity) as AttemptBoundary
        var attempt: String? = null
        var staleDetach = 0
        val original = IllegalStateException("older registration")
        assertSame(original, assertThrows(IllegalStateException::class.java) {
            activity.initializeResources(a) { cleanup ->
                cleanup { staleDetach++ }
                setSink(activity, collectingSink(oldEvents))
                activity.initializeResources(b, ownerB) {
                    attempt = attempts.start(0)
                    // Runs inside registration, before B listens and before A's stale rollback.
                    prediction(activity)
                    activity.postBenchmarkReport(ownerB, "{\"probe\":1}")
                    drain()
                    assertTrue("registration inherited A subscriber", oldEvents.isEmpty())
                }
                throw original
            }
        })
        prediction(activity)
        activity.postBenchmarkReport(ownerB, "{\"probe\":2}")
        drain()
        assertTrue(oldEvents.isEmpty())
        assertTrue(activity.isCurrent(ownerB))
        assertEquals(attempt, attempts.currentId)
        assertNotNull(attempt)
        assertEquals(0, staleDetach)
        assertEquals(listOf("session", "benchmark", "vision"), a.closed)
        assertTrue(b.closed.isEmpty())
        setSink(activity, collectingSink(newEvents))
        prediction(activity)
        activity.postBenchmarkReport(ownerB, "{\"probe\":3}")
        drain()
        assertEquals(listOf("prediction", "benchmark_complete"), newEvents.map { org.json.JSONObject(it).getString("state") })
        assertTrue(oldEvents.isEmpty())
    }

    @Test fun benchmarkCompletionUsesOnlyCurrentOwnersPostPublicationSubscription() {
        val activity = MainActivity()
        val ownerA = MainActivity.Initialization()
        val ownerB = MainActivity.Initialization()
        val oldEvents = mutableListOf<String>()
        val newEvents = mutableListOf<String>()
        activity.initializeResources(Factory(), ownerA) { setSink(activity, collectingSink(oldEvents)) }
        activity.postBenchmarkReport(ownerA, "{\"probe\":0}")
        drain()
        assertEquals("benchmark_complete", org.json.JSONObject(oldEvents.single()).getString("state"))
        oldEvents.clear()
        activity.postBenchmarkReport(ownerA, "{\"probe\":1}") // queued displaced callback
        activity.initializeResources(Factory(), ownerB) {}
        activity.postBenchmarkReport(ownerB, "{\"probe\":2}") // no B listener
        drain()
        assertTrue("benchmark inherited displaced subscriber", oldEvents.isEmpty())
        assertTrue(newEvents.isEmpty())
        setSink(activity, collectingSink(newEvents))
        activity.postBenchmarkReport(ownerA, "{\"probe\":3}") // stale callback after listen
        activity.postBenchmarkReport(ownerB, "{\"probe\":4}")
        drain()
        assertEquals(1, newEvents.size)
        val event = org.json.JSONObject(newEvents.single())
        assertEquals("benchmark_complete", event.getString("state"))
        assertEquals(4, event.getJSONObject("results").getInt("probe"))
        assertTrue(oldEvents.isEmpty())
    }

    @Test fun registrationFailureDetachesSubscriptionsReleasesAllAndAllowsCleanRetry() {
        val activity = MainActivity()
        val factory = Factory(releaseFails = true)
        var detached = 0
        val original = IllegalStateException("registration")
        val thrown = assertThrows(IllegalStateException::class.java) {
            activity.initializeResources(factory) { cleanup ->
                cleanup { detached++; throw IllegalArgumentException("detach") }
                setSink(activity, sink())
                throw original
            }
        }
        assertSame(original, thrown)
        assertEquals(1, detached)
        assertNull(getSink(activity))
        assertEquals(listOf("session", "benchmark", "vision"), factory.closed)
        assertEquals(4, thrown.suppressed.size)
        val retry = Factory()
        activity.initializeResources(retry) { setSink(activity, sink()) }
        assertNotNull(getSink(activity))
        assertTrue(retry.closed.isEmpty())
    }

    @Test fun failedOlderRegistrationCannotClearOrDetachNewerReplacement() {
        val activity = MainActivity()
        val a = Factory()
        val b = Factory()
        val ownerB = MainActivity.Initialization()
        val newerSink = sink()
        val attempts = MainActivity::class.java.getDeclaredField("attempts").apply { isAccessible = true }.get(activity) as AttemptBoundary
        var replacementAttempt: String? = null
        var staleDetach = 0
        val original = IllegalStateException("old registration")
        assertSame(original, assertThrows(IllegalStateException::class.java) {
            activity.initializeResources(a) { cleanup ->
                cleanup { staleDetach++ }
                activity.initializeResources(b, ownerB) {
                    setSink(activity, newerSink)
                    replacementAttempt = attempts.start(0)
                }
                throw original
            }
        })
        assertSame(newerSink, getSink(activity))
        assertTrue(activity.isCurrent(ownerB))
        assertNotNull(replacementAttempt)
        assertEquals(replacementAttempt, attempts.currentId)
        assertEquals(0, staleDetach)
        assertEquals(listOf("session", "benchmark", "vision"), a.closed)
        assertTrue(b.closed.isEmpty())
    }

    @Test fun failedInitializationQueuedEventCannotCrossRetryEvenWithSameSubscriber() {
        val activity = MainActivity()
        val delivered = mutableListOf<String>()
        val subscriber = object : io.flutter.plugin.common.EventChannel.EventSink {
            override fun success(event: Any?) { delivered.add(event as String) }
            override fun error(code: String, message: String?, details: Any?) {}
            override fun endOfStream() {}
        }
        val owner = MainActivity.Initialization()
        val attempts = MainActivity::class.java.getDeclaredField("attempts").apply { isAccessible = true }.get(activity) as AttemptBoundary
        assertThrows(IllegalStateException::class.java) {
            activity.initializeResources(Factory(), owner) {
                setSink(activity, subscriber)
                attempts.start(0)
                MainActivity::class.java.getDeclaredMethod("handleVisionEvent", String::class.java).apply { isAccessible = true }
                    .invoke(activity, "{\"state\":\"prediction\"}")
                throw IllegalStateException("view registration")
            }
        }
        assertFalse(activity.isCurrent(owner))
        assertNull("failed initialization left an attempt live", attempts.currentId)
        activity.initializeResources(Factory()) { setSink(activity, subscriber) }
        org.robolectric.Shadows.shadowOf(android.os.Looper.getMainLooper()).idle()
        assertTrue("failed owner event reached retry subscriber", delivered.isEmpty())
    }

    @Test fun rejectedPlatformRegistrationRollsBackAndRetainedFactoryCannotCreate() {
        val activity = MainActivity()
        val factory = Factory()
        val owner = MainActivity.Initialization()
        var retained: io.flutter.plugin.platform.PlatformViewFactory? = null
        val registry = object : io.flutter.plugin.platform.PlatformViewRegistry {
            override fun registerViewFactory(id: String, viewFactory: io.flutter.plugin.platform.PlatformViewFactory): Boolean {
                assertEquals("kumpas/camera_preview", id)
                retained = viewFactory
                return false
            }
        }
        assertThrows(IllegalStateException::class.java) {
            activity.initializeResources(factory, owner) { activity.registerCameraView(registry, owner) }
        }
        assertFalse(activity.isCurrent(owner))
        assertEquals(listOf("session", "benchmark", "vision"), factory.closed)
        assertThrows(IllegalStateException::class.java) {
            retained!!.create(org.robolectric.RuntimeEnvironment.getApplication(), 7, null)
        }
    }

    @Test fun everyAcquisitionStagePreservesViableOwnerAndSuccessfulHandlesCloseOnceAtDestroy() {
        for (stage in listOf("session", "exporter", "benchmark", "vision")) {
            val activity = MainActivity()
            val viable = Factory()
            val owner = MainActivity.Initialization()
            val events = mutableListOf<String>()
            val subscriber = collectingSink(events)
            activity.initializeResources(viable, owner) { setSink(activity, subscriber) }
            val failing = Factory(stage)
            assertSame(failing.original, assertThrows(IllegalArgumentException::class.java) {
                activity.initializeResources(failing) { fail("registered failed acquisition") }
            })
            assertTrue(activity.isCurrent(owner))
            assertSame(subscriber, getSink(activity))
            prediction(activity)
            activity.postBenchmarkReport(owner, "{\"probe\":1}")
            drain()
            assertEquals(stage, listOf("prediction", "benchmark_complete"), events.map { org.json.JSONObject(it).getString("state") })
            assertTrue(viable.closed.isEmpty())
            val expected = when (stage) {
                "session" -> emptyList()
                "exporter", "benchmark" -> listOf("session")
                else -> listOf("session", "benchmark")
            }
            assertEquals(stage, expected, failing.closed)
            val destroy = MainActivity::class.java.getDeclaredMethod("onDestroy").apply { isAccessible = true }
            // Bare FlutterActivity has no delegate; framework teardown is still attempted.
            repeat(2) { assertThrows(java.lang.reflect.InvocationTargetException::class.java) { destroy.invoke(activity) } }
            assertEquals(listOf("session", "benchmark", "vision"), viable.closed)
            assertFalse(activity.isCurrent(owner))
            assertNull(getSink(activity))
        }
    }

    @Test fun rollbackClearsPublishedConcreteEngineAndRetryPublishesDifferentHandle() {
        val context = org.robolectric.RuntimeEnvironment.getApplication()
        fun engine() = VisionEngine(context, resourceFactory = object : VisionResourceFactory {
            override fun pose() = OwnedNative<com.google.mediapipe.tasks.vision.poselandmarker.PoseLandmarker>(null) {}
            override fun hand() = OwnedNative<com.google.mediapipe.tasks.vision.handlandmarker.HandLandmarker>(null) {}
            override fun interpreter(model: java.nio.ByteBuffer) = OwnedNative<org.tensorflow.lite.Interpreter>(null) {}
            override fun asset(name: String) = java.io.ByteArrayInputStream(if (name.endsWith("json")) "{\"0\":{\"label\":\"ONE\"}}".toByteArray() else byteArrayOf(1))
        }, onResult = {})
        val activity = MainActivity()
        val field = MainActivity::class.java.getDeclaredField("visionEngine").apply { isAccessible = true }
        val failed = engine()
        val retry = engine()
        fun factory(value: VisionEngine) = object : ActivityResourceFactory by Factory() {
            override fun vision() = OwnedNative(value) { value.close() }
        }
        try {
            assertThrows(IllegalStateException::class.java) {
                activity.initializeResources(factory(failed)) {
                    assertSame(failed, field.get(activity))
                    throw IllegalStateException("registration")
                }
            }
            assertNull(field.get(activity))
            assertThrows(IllegalStateException::class.java) { failed.startAttempt(0) }
            activity.initializeResources(factory(retry)) { assertSame(retry, field.get(activity)) }
            retry.startAttempt(0)
        } finally {
            try { MainActivity::class.java.getDeclaredMethod("onDestroy").apply { isAccessible = true }.invoke(activity) }
            catch (_: java.lang.reflect.InvocationTargetException) { /* bare Flutter delegate */ }
            failed.close(); retry.close()
        }
        assertNull(field.get(activity))
    }

    @Test fun failedReplacementReleasesDisplacedOwnerWithoutRestoringStaleFields() {
        val activity = MainActivity()
        val a = Factory(releaseFails = true)
        val b = Factory(releaseFails = true)
        val ownerA = MainActivity.Initialization()
        activity.initializeResources(a, ownerA) { setSink(activity, sink()) }
        val original = IllegalStateException("replacement registration")
        assertSame(original, assertThrows(IllegalStateException::class.java) {
            activity.initializeResources(b) { throw original }
        })
        assertEquals(listOf("session", "benchmark", "vision"), a.closed)
        assertEquals(listOf("session", "benchmark", "vision"), b.closed)
        assertEquals(6, original.suppressed.size)
        assertFalse(activity.isCurrent(ownerA))
        assertNull(getSink(activity))
    }

    @Test fun ownedDestroyAttemptsEveryReleaseAndFrameworkEvenWhenEachCloseFails() {
        val activity = MainActivity()
        val factory = Factory(releaseFails = true)
        var detached = 0
        activity.initializeResources(factory) { cleanup -> cleanup { detached++ } }
        val destroy = MainActivity::class.java.getDeclaredMethod("onDestroy").apply { isAccessible = true }
        val error = assertThrows(java.lang.reflect.InvocationTargetException::class.java) { destroy.invoke(activity) }.targetException
        assertEquals("session", error.message)
        assertEquals(listOf("session", "benchmark", "vision"), factory.closed)
        assertEquals(1, detached)
        assertTrue(error.suppressed.any { it.message == "benchmark" })
        assertTrue(error.suppressed.any { it.message == "vision" })
        assertTrue(error.suppressed.any { failure -> failure.stackTrace.any { it.className.contains("FlutterActivity") && it.methodName == "onDestroy" } })
        assertNull(getSink(activity))
        assertThrows(java.lang.reflect.InvocationTargetException::class.java) { destroy.invoke(activity) }
        assertEquals(3, factory.closed.size)
    }

    @Test fun laterAcquisitionFailureReleasesEveryOwnedHandleAndPreservesPrimary() {
        val activity = MainActivity()
        val factory = Factory("vision", releaseFails = true)
        val thrown = assertThrows(IllegalArgumentException::class.java) {
            activity.initializeResources(factory) { fail("registration after failed acquisition") }
        }
        assertSame(factory.original, thrown)
        assertEquals(listOf("session", "benchmark"), factory.closed)
        assertEquals(2, thrown.suppressed.size)
    }
}
