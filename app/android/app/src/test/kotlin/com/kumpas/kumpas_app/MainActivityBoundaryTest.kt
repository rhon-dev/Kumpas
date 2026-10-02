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
