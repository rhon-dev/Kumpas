package com.kumpas.kumpas_app

import android.content.Context
import org.robolectric.RuntimeEnvironment
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.Shadows.shadowOf
import org.robolectric.annotation.Config
import android.os.Looper
import java.time.Duration

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class BenchmarkModeTest {
    private val context: Context = RuntimeEnvironment.getApplication()

    @Test fun countersSeparateEventsFromAnalyzerWithTrailingStall() {
        val benchmark = BenchmarkMode(context)
        benchmark.start(60)
        repeat(30) { BenchmarkMode::class.java.getMethod("recordAnalyzer").invoke(benchmark) }
        repeat(8) { BenchmarkMode::class.java.getMethod("recordSelected").invoke(benchmark) }
        repeat(7) { BenchmarkMode::class.java.getMethod("recordProcessed").invoke(benchmark) }
        repeat(2) { BenchmarkMode::class.java.getMethod("recordEvent").invoke(benchmark) }
        BenchmarkMode::class.java.getMethod("recordFailure", String::class.java).invoke(benchmark, "no_signer")
        shadowOf(Looper.getMainLooper()).idleFor(Duration.ofSeconds(60))
        val result = JSONObject(benchmark.finish())
        assertEquals(30, result.getInt("analyzer_count"))
        assertEquals(8, result.getInt("selected_count"))
        assertEquals(7, result.getInt("processed_count"))
        assertEquals(2, result.getInt("event_count"))
        assertEquals(1, result.getInt("failure_count"))
        val rate = result.getJSONObject("fps").getJSONObject("analyzer")
        assertEquals(0.5, rate.getDouble("mean_fps"), 0.0)
        assertEquals(30.0, rate.getJSONArray("per_second_samples").getDouble(0), 0.0)
        assertEquals(0.0, rate.getJSONArray("per_second_samples").getDouble(59), 0.0)
        assertFalse(result.getBoolean("physical_fps_gate_pass"))
    }

    @Test fun traceWhitelistRetainsSameClockBoundariesOnly() {
        val benchmark = BenchmarkMode(context)
        benchmark.start(60)
        val ns = android.os.SystemClock.elapsedRealtimeNanos()
        val trace = JSONObject().put("attempt_id", "synthetic").put("first_analyzer_ns", ns)
            .put("final_analyzer_ns", ns).put("native_result_ns", ns + 1)
            .put("event_delivery_ns", ns + 2).put("raw_video", "never store")
        BenchmarkMode::class.java.getMethod("recordTrace", JSONObject::class.java).invoke(benchmark, trace)
        trace.put("attempt_id", "mutated")
        val report = JSONObject(benchmark.finish())
        val saved = report.getJSONArray("traces").getJSONObject(0)
        assertEquals("synthetic", saved.getString("attempt_id"))
        assertFalse(saved.has("raw_video"))
        assertEquals(0.000002, saved.getDouble("final_analyzer_to_event_ms"), 0.00000001)
        assertFalse(saved.has("final_analyzer_to_ui_ack_ms"))
    }

    @Test fun autoDeadlinePersistsUniqueReportsAndCallsBackOnce() {
        var callbacks = 0
        val benchmark = BenchmarkMode(context) { callbacks++ }
        val id = benchmark.start(60)
        try { benchmark.start(60); fail("busy accepted") } catch (_: IllegalStateException) { }
        shadowOf(Looper.getMainLooper()).idleFor(Duration.ofSeconds(60))
        assertFalse(benchmark.isActive)
        assertEquals(1, callbacks)
        assertTrue(java.io.File(benchmark.reportPath!!).isFile)
        assertEquals(id, JSONObject(benchmark.latestResults()!!).getString("run_id"))
        benchmark.finish()
        assertEquals(1, callbacks)
        val next = benchmark.start(60)
        assertNotEquals(id, next)
        val early = JSONObject(benchmark.finish())
        assertFalse(early.getBoolean("complete"))
        assertTrue(java.io.File(context.filesDir, "benchmarks/$id.json").isFile)
        assertEquals(next, JSONObject(java.io.File(context.filesDir, "benchmarks/latest.json").readText()).getString("run_id"))
    }

    @Test fun reportContainsBuildModelIdentityAndBoundaryLabels() {
        val benchmark = BenchmarkMode(context)
        benchmark.start(60)
        val result = JSONObject(benchmark.finish())
        val model = result.getJSONObject("model")
        assertEquals("kumpas_50sign.tflite", model.getString("asset"))
        assertTrue(model.getString("sha256").matches(Regex("[0-9a-f]{64}")))
        assertTrue(result.getJSONObject("build").has("version_code"))
        assertEquals("analyzer_entry_not_sensor_exposure", result.getString("origin"))
        assertEquals("post_frame_native_ack_upper_bound_not_physical_display", result.getString("ui_endpoint"))
    }

    @Test fun traceDoesNotPersistNestedRawDataInTimingFields() {
        val benchmark = BenchmarkMode(context)
        benchmark.start(60)
        benchmark.recordTrace(JSONObject().put("attempt_id", "bad-shape")
            .put("inference_ms", JSONObject().put("participant_video", "private")))
        val report = JSONObject(benchmark.finish())
        assertEquals(0, report.getJSONArray("traces").length())
        assertFalse(report.toString().contains("participant_video"))
        assertEquals("malformed_trace", report.getJSONArray("excluded_samples").getJSONObject(0).getString("reason"))
    }

    @Test fun failedStorageStopsDeadlineWithoutClaimingPersistedReport() {
        val root = java.io.File(context.cacheDir, "blocked-benchmark-${java.util.UUID.randomUUID()}").apply { mkdirs() }
        java.io.File(root, "benchmarks").writeText("unrelated sentinel")
        val isolated = object : android.content.ContextWrapper(context) {
            override fun getFilesDir(): java.io.File = root
        }
        var completed: String? = null
        val benchmark = BenchmarkMode(isolated) { completed = it }
        benchmark.start(60)
        shadowOf(Looper.getMainLooper()).idleFor(Duration.ofSeconds(60))
        assertFalse(benchmark.isActive)
        assertNull(benchmark.reportPath)
        val report = JSONObject(completed!!)
        assertTrue(report.has("storage_error"))
        assertFalse(report.getBoolean("physical_fps_gate_pass"))
        assertEquals(completed, benchmark.latestResults())
        assertEquals("unrelated sentinel", java.io.File(root, "benchmarks").readText())
    }

    @Test fun activeRunNeverExposesPreviousReportAsCurrent() {
        val benchmark = BenchmarkMode(context)
        val a = benchmark.start(60)
        benchmark.finish()
        val b = benchmark.start(60)
        assertNotEquals(a, b)
        assertNull("prior A exposed while B active", benchmark.latestResults())
        assertEquals(a, JSONObject(java.io.File(context.filesDir, "benchmarks/$a.json").readText()).getString("run_id"))
        benchmark.finish()
    }

    @Test fun reportAndStopAreBoundToRequestedRun() {
        val benchmark = BenchmarkMode(context)
        val a = benchmark.start(60)
        benchmark.finish()
        val b = benchmark.start(60)
        val lookup = BenchmarkMode::class.java.getMethod("reportFor", String::class.java)
        val stop = BenchmarkMode::class.java.getMethod("stop", String::class.java)
        assertEquals(a, JSONObject(lookup.invoke(benchmark, a) as String).getString("run_id"))
        assertNull(lookup.invoke(benchmark, b))
        try { stop.invoke(benchmark, a); fail("stale stop accepted") }
        catch (e: java.lang.reflect.InvocationTargetException) { assertTrue(e.cause is IllegalStateException) }
        assertTrue(benchmark.isActive)
        assertEquals(b, JSONObject(stop.invoke(benchmark, b) as String).getString("run_id"))
        assertEquals(b, JSONObject(lookup.invoke(benchmark, b) as String).getString("run_id"))
    }

    @Test fun tracesUseHalfOpenRunWindowAndLateAckCannotOverwriteEvent() {
        val benchmark = BenchmarkMode(context)
        benchmark.start(60)
        val ns = android.os.SystemClock.elapsedRealtimeNanos()
        fun trace(id: String, first: Long = ns, event: Long = ns + 2) = JSONObject()
            .put("attempt_id", id).put("first_analyzer_ns", first).put("final_analyzer_ns", ns)
            .put("native_result_ns", ns + 1).put("event_delivery_ns", event)
        benchmark.recordTrace(trace("pre", first = ns - 1))
        benchmark.recordTrace(trace("end", event = ns + 60_000_000_000L))
        benchmark.recordTrace(trace("valid"))
        benchmark.recordTrace(trace("valid").put("ui_ack_ns", ns + 60_000_000_000L))
        val report = JSONObject(benchmark.finish())
        val saved = report.getJSONArray("traces")
        assertEquals(1, saved.length())
        assertEquals("valid", saved.getJSONObject(0).getString("attempt_id"))
        assertFalse(saved.getJSONObject(0).has("ui_ack_ns"))
        assertEquals(3, report.getJSONArray("excluded_samples").length())
    }

    @Test fun attemptStartedBeforeRunIsNotRelabelledIntoRun() {
        val benchmark = BenchmarkMode(context)
        benchmark.start(60)
        val ns = android.os.SystemClock.elapsedRealtimeNanos()
        val trace = PipelineTrace("pre-run-attempt", ns, ns, ns + 1, 0).toJson()
        trace.put("event_delivery_ns", ns + 2).put("attempt_started_ns", ns - 1)
        benchmark.recordTrace(trace)
        val report = JSONObject(benchmark.finish())
        assertEquals(0, report.getJSONArray("traces").length())
    }

    @Test fun latestWriteFailureLeavesOnlyExplicitNonGatingImmutableEvidence() {
        val root = java.io.File(context.cacheDir, "latest-fault-${java.util.UUID.randomUUID()}").apply { mkdirs() }
        val directory = java.io.File(root, "benchmarks").apply { mkdirs() }
        java.io.File(directory, "latest.json.new").apply { mkdirs() }
            .resolve("sentinel").writeText("block replacement")
        val isolated = object : android.content.ContextWrapper(context) { override fun getFilesDir() = root }
        val benchmark = BenchmarkMode(isolated)
        val id = benchmark.start(60)
        val returned = JSONObject(benchmark.finish())
        assertTrue("real latest failure must be observed", returned.has("storage_error"))
        val retained = JSONObject(java.io.File(directory, "$id.json").readText())
        assertEquals("immutable_only_latest_unverified", retained.getString("storage_state"))
        assertFalse(retained.getBoolean("physical_fps_gate_pass"))
        assertNull(benchmark.reportPath)
    }

    @Test fun missingSetupIsRetainedDiagnosticWithoutInventedMeasurements() {
        val benchmark = BenchmarkMode(context)
        benchmark.start(60)
        val report = JSONObject(benchmark.finish())
        assertEquals("diagnostic", report.optString("measurement_status"))
        assertFalse(report.getBoolean("physical_fps_gate_pass"))
        assertEquals(0, report.getJSONObject("setup").length())
        assertEquals("setup_missing", report.getJSONArray("setup_errors").getString(0))
        assertEquals("unknown", report.getJSONObject("camera").getString("lens"))
    }

    private fun validSetup() = JSONObject().put("setup_id", "synthetic-setup")
        .put("condition", "optimal").put("lux", 400).put("background", "plain").put("distance_cm", 75)
        .put("device_fingerprint", android.os.Build.FINGERPRINT).put("chip", "Snapdragon 680").put("ram_gb", 4)
        .put("setup_verified", true).put("device_verified", true).put("front_camera_verified", true)
        .put("apk_sha256", "a".repeat(64)).put("revision", "b".repeat(40)).put("thermal_state", "nominal")

    @Test fun provisionedSetupIsValidatedAndImmutableForItsRun() {
        val root = java.io.File(context.cacheDir, "setup-${java.util.UUID.randomUUID()}").apply { mkdirs() }
        val isolated = object : android.content.ContextWrapper(context) { override fun getFilesDir() = root }
        val manifest = java.io.File(root, "benchmarks/next_setup.json")
        manifest.parentFile!!.mkdirs()
        val supplied = validSetup()
        manifest.writeText(supplied.toString())
        val benchmark = BenchmarkMode(isolated)
        benchmark.start(60)
        supplied.put("condition", "low_light").put("lux", 20)
        manifest.writeText(supplied.toString())
        val report = JSONObject(benchmark.finish())
        assertEquals("optimal", report.getJSONObject("setup").optString("condition"))
        assertEquals(400, report.getJSONObject("setup").getInt("lux"))
        assertEquals(0, report.getJSONArray("setup_errors").length())
        assertEquals("diagnostic", report.getString("measurement_status")) // still no bound camera
    }

    @Test fun malformedOrUnverifiedSetupCannotQualifyEvenWithRecognizedModelName() {
        val root = java.io.File(context.cacheDir, "invalid-setup-${java.util.UUID.randomUUID()}").apply { mkdirs() }
        val isolated = object : android.content.ContextWrapper(context) { override fun getFilesDir() = root }
        val manifest = java.io.File(root, "benchmarks/next_setup.json")
        manifest.parentFile!!.mkdirs()
        val cases = listOf("lux" to -1, "lux" to 300, "distance_cm" to 59, "ram_gb" to 3,
            "chip" to "unknown", "device_fingerprint" to "other", "setup_verified" to false,
            "device_verified" to false, "front_camera_verified" to false, "apk_sha256" to "bad",
            "revision" to "bad", "thermal_state" to "", "background" to "complex", "condition" to "invented")
        for ((key, value) in cases) {
            manifest.writeText(validSetup().put(key, value).toString())
            val benchmark = BenchmarkMode(isolated)
            benchmark.start(60)
            val report = JSONObject(benchmark.finish())
            assertTrue("Accepted invalid $key", report.getJSONArray("setup_errors").length() > 0)
            assertFalse(report.getBoolean("physical_fps_gate_pass"))
        }
        manifest.writeText("{\"lux\":1,\"lux\":2}")
        val duplicate = BenchmarkMode(isolated)
        duplicate.start(60)
        assertEquals("setup_malformed", JSONObject(duplicate.finish()).getJSONArray("setup_errors").getString(0))
    }

    @Test fun actualCameraAtStartAndChangesControlSetupQualification() {
        val root = java.io.File(context.cacheDir, "camera-setup-${java.util.UUID.randomUUID()}").apply { mkdirs() }
        val isolated = object : android.content.ContextWrapper(context) { override fun getFilesDir() = root }
        val manifest = java.io.File(root, "benchmarks/next_setup.json")
        manifest.parentFile!!.mkdirs()
        manifest.writeText(validSetup().toString())
        val method = BenchmarkMode::class.java.getMethod("recordCamera", String::class.java, String::class.java, Boolean::class.javaPrimitiveType, String::class.java)
        for (lens in listOf("front", "back", "unknown")) {
            val benchmark = BenchmarkMode(isolated)
            method.invoke(benchmark, if (lens == "back") "default_back_fallback" else "default_front", lens, lens != "unknown", "synthetic-camera")
            benchmark.start(60)
            val report = JSONObject(benchmark.finish())
            assertEquals(lens, report.getJSONObject("camera").getString("lens"))
            assertEquals(if (lens == "front") "qualified_setup" else "diagnostic", report.getString("measurement_status"))
        }
        val changed = BenchmarkMode(isolated)
        method.invoke(changed, "default_front", "front", true, "synthetic-front")
        changed.start(60)
        method.invoke(changed, "default_back_fallback", "back", true, "synthetic-back")
        val report = JSONObject(changed.finish())
        assertTrue(report.getJSONObject("camera").getBoolean("changed"))
        assertEquals("diagnostic", report.getString("measurement_status"))
        assertFalse(report.getBoolean("physical_fps_gate_pass"))
    }

    @Test fun pendingPreDeadlineAttemptIsExplicitlyCensoredAtCloseAndLateCompletionCannotEraseIt() {
        val benchmark = BenchmarkMode(context)
        benchmark.start(60)
        val ns = android.os.SystemClock.elapsedRealtimeNanos()
        val start = BenchmarkMode::class.java.getMethod("recordAttemptStart", String::class.java, Long::class.javaPrimitiveType)
        start.invoke(benchmark, "slow-synthetic", ns)
        shadowOf(Looper.getMainLooper()).idleFor(Duration.ofSeconds(60))
        val report = JSONObject(benchmark.latestResults()!!)
        assertEquals(1, report.getInt("attempt_count"))
        assertEquals(1, report.getInt("censored_count"))
        assertEquals("censored_at_close", report.getJSONArray("outcomes").getJSONObject(0).getString("code"))
        assertEquals(0, report.getJSONArray("traces").length())
        val trace = PipelineTrace("slow-synthetic", ns, ns + 1, ns + 2, 0, ns).toJson()
            .put("event_delivery_ns", ns + 60_000_000_001L)
        benchmark.recordTrace(trace)
        benchmark.recordOutcome("slow-synthetic", "success")
        assertEquals(report.toString(), JSONObject(benchmark.latestResults()!!).toString())
    }

    @Test fun outcomeFromAttemptNotStartedInRunIsExplicitlyExcludedNotRelabelled() {
        val benchmark = BenchmarkMode(context)
        benchmark.start(60)
        benchmark.recordOutcome("pre-run", "no_signer")
        val report = JSONObject(benchmark.finish())
        assertEquals(0, report.getJSONArray("outcomes").length())
        assertEquals("outcome_unbound_attempt", report.getJSONArray("excluded_samples").getJSONObject(0).getString("reason"))
        assertEquals(0, report.getInt("failure_count"))
    }

    @Test fun emptyRunUsesFullMonotonicWindow() {
        val benchmark = BenchmarkMode(context)
        benchmark.start(60)
        shadowOf(Looper.getMainLooper()).idleFor(Duration.ofSeconds(60))
        val result = JSONObject(benchmark.finish())
        assertEquals(2, result.optInt("schema_version"))
        assertEquals(60.0, result.getDouble("duration_s"), 0.001)
        assertEquals(0, result.getInt("analyzer_count"))
        assertEquals(60, result.getJSONObject("fps").getJSONObject("analyzer").getJSONArray("per_second_samples").length())
        assertFalse(result.getBoolean("physical_fps_gate_pass"))
    }
}
