package com.kumpas.kumpas_app

import android.os.Looper
import io.flutter.plugin.common.EventChannel
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.Shadows.shadowOf
import org.robolectric.annotation.Config

/** Executes the production handleVisionEvent + Handler posting seam, no detector or participant store. */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class MainActivityBoundaryTest {
    private fun field(activity: MainActivity, name: String): Any? =
        MainActivity::class.java.getDeclaredField(name).apply { isAccessible = true }.get(activity)
    private fun events(activity: MainActivity): MutableList<JSONObject> {
        val delivered = mutableListOf<JSONObject>()
        val sink = object : EventChannel.EventSink {
            override fun success(event: Any?) { delivered.add(JSONObject(event as String)) }
            override fun error(code: String, message: String?, details: Any?) { fail(code) }
            override fun endOfStream() {}
        }
        MainActivity::class.java.getDeclaredField("eventSink").apply { isAccessible = true }.set(activity, sink)
        return delivered
    }
    private fun emit(activity: MainActivity, event: JSONObject) {
        MainActivity::class.java.getDeclaredMethod("handleVisionEvent", String::class.java)
            .apply { isAccessible = true }.invoke(activity, event.toString())
    }
    @Test fun queuedViewEventsCannotReachReplacementOrNewSubscriber() {
        for (state in listOf("prediction", "no_signer", "warmup", "camera_error")) {
            val activity = MainActivity()
            val benchmark = BenchmarkMode(org.robolectric.RuntimeEnvironment.getApplication())
            benchmark.start(60)
            MainActivity::class.java.getDeclaredField("benchmarkMode").apply { isAccessible = true }.set(activity, benchmark)
            val oldSink = events(activity)
            val owners = field(activity, "cameraViews") as CameraViewOwnership
            val a = owners.register()
            val attempts = field(activity, "attempts") as AttemptBoundary
            val generation = attempts.generation
            emit(activity, JSONObject().put("state", state).put("viewOwner", a)
                .put("cameraGeneration", generation).put("label", "OLD_A"))
            val afterEmissionGeneration = attempts.generation
            val b = owners.register()
            assertEquals(afterEmissionGeneration, attempts.generation)
            val newSink = oldSink // hold subscription constant: view identity alone must reject
            shadowOf(Looper.getMainLooper()).idle()
            assertTrue(oldSink.isEmpty())
            assertTrue("posted $state from A reached B", newSink.isEmpty())
            // View replacement did not itself increment attempt generation.
            assertTrue(owners.run(b) {})
            shadowOf(Looper.getMainLooper()).idleFor(java.time.Duration.ofMillis(1))
            assertEquals(0, JSONObject(benchmark.finish()).getInt("event_count"))
        }
        val activity = MainActivity()
        val oldSink = events(activity)
        emit(activity, JSONObject().put("state", "prediction").put("label", "OLD_SUBSCRIPTION"))
        val newSink = events(activity)
        shadowOf(Looper.getMainLooper()).idle()
        assertTrue(oldSink.isEmpty())
        assertTrue("queued event crossed subscription ownership", newSink.isEmpty())
    }

    @Test fun queuedOldCameraErrorCannotCancelReplacementCapture() {
        val activity = MainActivity()
        val delivered = events(activity)
        val attempts = field(activity, "attempts") as AttemptBoundary
        attempts.start(0)
        emit(activity, JSONObject().put("state", "camera_error").put("cameraGeneration", 1).put("reason", "old conversion"))
        val replacement = attempts.start(1)
        shadowOf(Looper.getMainLooper()).idle()
        assertTrue(attempts.canDeliver(replacement))
        assertTrue("stale camera failure reached the production EventSink", delivered.isEmpty())
        emit(activity, JSONObject().put("state", "attempt_progress").put("attemptId", replacement))
        shadowOf(Looper.getMainLooper()).idle()
        assertEquals("attempt_progress", delivered.single().getString("state"))
    }
    @Test fun noSignerOutcomeIsRecordedAtProductionEventBoundaryWithoutLatency() {
        val activity = MainActivity()
        val benchmark = BenchmarkMode(org.robolectric.RuntimeEnvironment.getApplication())
        benchmark.start(60)
        MainActivity::class.java.getDeclaredField("benchmarkMode").apply { isAccessible = true }.set(activity, benchmark)
        events(activity)
        val id = (field(activity, "attempts") as AttemptBoundary).start(0)
        benchmark.recordAttemptStart(id, android.os.SystemClock.elapsedRealtimeNanos())
        emit(activity, JSONObject().put("state", "attempt_failed").put("attemptId", id).put("outcome", "no_signer").put("reason", "synthetic"))
        shadowOf(Looper.getMainLooper()).idle()
        val report = JSONObject(benchmark.finish())
        assertEquals("no_signer", report.getJSONArray("outcomes").getJSONObject(0).getString("code"))
        assertEquals(0, report.getJSONArray("traces").length())
    }

    @Test fun cancellationAndTimeoutUseProductionControlHookWithoutDetectorFailure() {
        val activity = MainActivity()
        val benchmark = BenchmarkMode(org.robolectric.RuntimeEnvironment.getApplication())
        benchmark.start(60)
        MainActivity::class.java.getDeclaredField("benchmarkMode").apply { isAccessible = true }.set(activity, benchmark)
        val attempts = field(activity, "attempts") as AttemptBoundary
        val cancel = MainActivity::class.java.getDeclaredMethod("cancelCapture", String::class.java, String::class.java).apply { isAccessible = true }
        val a = attempts.start(0)
        benchmark.recordAttemptStart(a, android.os.SystemClock.elapsedRealtimeNanos())
        cancel.invoke(activity, a, "cancelled")
        val b = attempts.start(1)
        benchmark.recordAttemptStart(b, android.os.SystemClock.elapsedRealtimeNanos())
        cancel.invoke(activity, a, "timeout") // stale ID must not affect B
        assertTrue(attempts.canDeliver(b))
        cancel.invoke(activity, b, "timeout")
        val report = JSONObject(benchmark.finish())
        val outcomes = report.getJSONArray("outcomes")
        assertEquals(2, outcomes.length())
        assertEquals("cancelled", outcomes.getJSONObject(0).getString("code"))
        assertEquals("timeout", outcomes.getJSONObject(1).getString("code"))
        assertEquals(0, report.getInt("failure_count"))
        assertEquals(0, report.getJSONArray("traces").length())
    }

    @Test fun latePendingTimeoutAccountsOldIdentityWithoutCancellingReplacement() {
        val activity = MainActivity()
        val benchmark = BenchmarkMode(org.robolectric.RuntimeEnvironment.getApplication())
        benchmark.start(60)
        MainActivity::class.java.getDeclaredField("benchmarkMode").apply { isAccessible = true }.set(activity, benchmark)
        val attempts = field(activity, "attempts") as AttemptBoundary
        val old = attempts.start(0)
        benchmark.recordAttemptStart(old, android.os.SystemClock.elapsedRealtimeNanos())
        val replacement = attempts.start(1)
        benchmark.recordAttemptStart(replacement, android.os.SystemClock.elapsedRealtimeNanos())
        val cancel = MainActivity::class.java.getDeclaredMethod("cancelCapture", String::class.java, String::class.java).apply { isAccessible = true }
        cancel.invoke(activity, old, "timeout")
        cancel.invoke(activity, old, "timeout")
        cancel.invoke(activity, "unknown", "timeout")
        assertTrue(attempts.canDeliver(replacement))
        val report = JSONObject(benchmark.finish())
        val outcomes = report.getJSONArray("outcomes")
        assertEquals(2, outcomes.length())
        assertEquals(old, outcomes.getJSONObject(0).getString("attempt_id"))
        assertEquals("timeout", outcomes.getJSONObject(0).getString("code"))
        assertEquals("censored_at_close", outcomes.getJSONObject(1).getString("code"))
        cancel.invoke(activity, replacement, "timeout")
        assertEquals(report.toString(), JSONObject(benchmark.latestResults()!!).toString())
    }

    @Test fun currentCameraErrorRetainsCodedTerminalInsteadOfCensoringKnownFailure() {
        val activity = MainActivity()
        val benchmark = BenchmarkMode(org.robolectric.RuntimeEnvironment.getApplication())
        benchmark.start(60)
        MainActivity::class.java.getDeclaredField("benchmarkMode").apply { isAccessible = true }.set(activity, benchmark)
        events(activity)
        val attempts = field(activity, "attempts") as AttemptBoundary
        val id = attempts.start(0)
        benchmark.recordAttemptStart(id, android.os.SystemClock.elapsedRealtimeNanos())
        emit(activity, JSONObject().put("state", "camera_error").put("cameraGeneration", attempts.generation))
        val report = JSONObject(benchmark.finish())
        assertEquals("camera_error", report.getJSONArray("outcomes").getJSONObject(0).getString("code"))
        assertEquals(0, report.getInt("censored_count"))
    }

    @Test fun cancellationWithoutExplicitIdRetainsCurrentIdentityAndNotDetectorFailure() {
        val activity = MainActivity()
        val benchmark = BenchmarkMode(org.robolectric.RuntimeEnvironment.getApplication())
        benchmark.start(60)
        MainActivity::class.java.getDeclaredField("benchmarkMode").apply { isAccessible = true }.set(activity, benchmark)
        val id = (field(activity, "attempts") as AttemptBoundary).start(0)
        benchmark.recordAttemptStart(id, android.os.SystemClock.elapsedRealtimeNanos())
        MainActivity::class.java.getDeclaredMethod("cancelCapture", String::class.java, String::class.java)
            .apply { isAccessible = true }.invoke(activity, null, "cancelled")
        val report = JSONObject(benchmark.finish())
        assertEquals("cancelled", report.getJSONArray("outcomes").getJSONObject(0).getString("code"))
        assertEquals(id, report.getJSONArray("outcomes").getJSONObject(0).getString("attempt_id"))
        assertEquals(0, report.getInt("failure_count"))
        assertEquals(0, report.getInt("censored_count"))
    }

    @Test fun persistenceFailureReachesEventSinkAccountsFailureAndAllowsSafeRetry() {
        val base = org.robolectric.RuntimeEnvironment.getApplication()
        val root = java.io.File(base.cacheDir, "boundary-db-${java.util.UUID.randomUUID()}").apply { mkdirs() }
        val context = object : android.content.ContextWrapper(base) {
            override fun getFilesDir() = root
            override fun getDatabasePath(name: String) = java.io.File(root, name)
        }
        val manager = SessionManager(context)
        val probe = SessionDatabase(context)
        val benchmark = BenchmarkMode(context)
        val activity = MainActivity()
        try {
            MainActivity::class.java.getDeclaredField("sessionManager").apply { isAccessible = true }.set(activity, manager)
            MainActivity::class.java.getDeclaredField("benchmarkMode").apply { isAccessible = true }.set(activity, benchmark)
            val delivered = events(activity)
            val attempts = field(activity, "attempts") as AttemptBoundary
            benchmark.start(60)
            probe.writableDatabase.execSQL("CREATE TRIGGER synthetic_fault BEFORE INSERT ON attempts BEGIN SELECT RAISE(ABORT, 'synthetic'); END")
            fun result(id: String): JSONObject {
                val ns = android.os.SystemClock.elapsedRealtimeNanos()
                return JSONObject().put("state", "attempt_result").put("attemptId", id)
                    .put("targetClass", 0).put("targetLabel", "SYNTHETIC").put("predictedLabel", "SYNTHETIC")
                    .put("predictedConfidence", 0.9).put("recognizedAsTarget", true).put("overallMatch", 0.9)
                    .put("items", org.json.JSONArray()).put("timing", JSONObject()
                        .put("first_analyzer_ns", ns).put("final_analyzer_ns", ns).put("native_result_ns", ns)
                        .put("attempt_started_ns", ns).put("inference_ms", 0))
            }
            val failed = attempts.start(0)
            benchmark.recordAttemptStart(failed, android.os.SystemClock.elapsedRealtimeNanos())
            emit(activity, result(failed))
            shadowOf(Looper.getMainLooper()).idle()
            assertEquals("attempt_failed", delivered.single().getString("state"))
            assertEquals("persistence_failed", delivered.single().getString("outcome"))
            assertEquals(0, probe.getAttemptCount())
            assertNull(field(activity, "pendingTrace"))
            probe.writableDatabase.execSQL("DROP TRIGGER synthetic_fault")
            val retry = attempts.start(0)
            benchmark.recordAttemptStart(retry, android.os.SystemClock.elapsedRealtimeNanos())
            emit(activity, result(retry))
            shadowOf(Looper.getMainLooper()).idle()
            assertEquals("attempt_result", delivered.last().getString("state"))
            assertEquals(retry, delivered.last().getString("attemptId"))
            assertEquals(1, probe.getAttemptCount())
            val report = JSONObject(benchmark.finish())
            assertEquals("persistence_failed", report.getJSONArray("outcomes").getJSONObject(0).getString("code"))
            assertEquals("success", report.getJSONArray("outcomes").getJSONObject(1).getString("code"))
            assertEquals(1, report.getJSONArray("traces").length())
        } finally {
            if (benchmark.isActive) benchmark.finish()
            manager.close(); probe.close()
        }
    }

    @Test fun currentCameraErrorStillReachesUi() {
        val activity = MainActivity()
        val delivered = events(activity)
        val attempts = field(activity, "attempts") as AttemptBoundary
        val id = attempts.start(0)
        emit(activity, JSONObject().put("state", "camera_error").put("cameraGeneration", 1).put("reason", "current failure"))
        shadowOf(Looper.getMainLooper()).idle()
        assertFalse(attempts.canDeliver(id))
        assertEquals("camera_error", delivered.single().getString("state"))
    }
}
