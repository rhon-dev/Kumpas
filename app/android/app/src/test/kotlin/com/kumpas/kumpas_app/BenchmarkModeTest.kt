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

    @Test fun invalidSetupTextNeverReachesNativePublishedReports() {
        val root = java.io.File(context.cacheDir, "privacy-${java.util.UUID.randomUUID()}").apply { mkdirs() }
        val isolated = setupContext(root)
        for (marker in listOf("PRIVATE patient text", "PRIVATE_patient_text", "Snapdragon 680PRIVATE"))
        for (key in listOf("setup_id", "condition", "background", "device_fingerprint", "chip", "apk_sha256", "revision", "thermal_state")) {
            root.resolve("benchmarks/next_setup.json").apply { parentFile!!.mkdirs(); writeText(validSetup().put(key, marker).toString()) }
            val benchmark = BenchmarkMode(isolated)
            val id = benchmark.start(60)
            val report = benchmark.finish()
            assertFalse("retained invalid $key", report.contains(marker))
            assertFalse(root.resolve("benchmarks/$id.json").readText().contains(marker))
            assertFalse(root.resolve("benchmarks/latest.json").readText().contains(marker))
            assertEquals(400, JSONObject(report).getJSONObject("setup").getInt("lux"))
            assertTrue(JSONObject(report).getJSONArray("setup_errors").length() > 0)
        }
    }

    @Test fun receiptCommittedProducerFullWindowPreservesConfirmedUnconfirmedAndFaultedDisposition() {
        for (mode in listOf("confirmed", "unconfirmed", "faulted")) {
            val root = java.io.File(context.cacheDir, "receipt-$mode-${java.util.UUID.randomUUID()}").apply { mkdirs() }
            root.resolve("benchmarks/next_setup.json").apply { parentFile!!.mkdirs(); writeText(validSetup().toString()) }
            val isolated = setupContext(root)
            val info = isolated.packageManager.getPackageInfo(isolated.packageName, 0)
            info.versionName = "synthetic-version"
            org.robolectric.Shadows.shadowOf(isolated.packageManager).installPackage(info)
            val benchmark = BenchmarkMode(isolated)
            // Real producer representation supports arbitrary OEM Camera2 strings,
            // never retains them as report aliases. No actual camera is used.
            benchmark.recordCamera("default_front", "front", true, "PRIVATE_patient_text")
            val id = benchmark.start(60)
            repeat(60) { second ->
                repeat(30) { benchmark.recordAnalyzer() }
                if (second == 1) {
                    val ns = android.os.SystemClock.elapsedRealtimeNanos()
                    val attempt = "44444444-4444-4444-8444-444444444444"
                    benchmark.recordAttemptStart(attempt, ns)
                    shadowOf(Looper.getMainLooper()).idleFor(Duration.ofMillis(100))
                    benchmark.recordTrace(PipelineTrace(attempt, ns, ns + 50_000_000,
                        ns + 75_000_000, 1_000_000, ns).toJson().put("event_delivery_ns", ns + 100_000_000))
                    benchmark.recordOutcome(attempt, "success")
                    shadowOf(Looper.getMainLooper()).idleFor(Duration.ofMillis(900))
                } else if (second == 29) {
                    shadowOf(Looper.getMainLooper()).idleFor(Duration.ofMillis(999))
                    if (mode == "faulted") {
                        root.resolve("benchmarks/$id.control.json").apply { delete(); mkdirs(); resolve("sentinel").writeText("unchanged") }
                    }
                    if (mode != "unconfirmed") assertEquals(mode == "confirmed", benchmark.confirmStart(id))
                    shadowOf(Looper.getMainLooper()).idleFor(Duration.ofMillis(1))
                } else shadowOf(Looper.getMainLooper()).idleFor(Duration.ofSeconds(1))
            }
            val report = JSONObject(benchmark.latestResults()!!)
            assertTrue(report.getBoolean("complete"))
            assertEquals(1800, report.getInt("analyzer_count"))
            assertEquals(if (mode == "confirmed") "confirmed" else "unconfirmed", report.getString("control_status"))
            assertFalse(report.toString().contains("PRIVATE_patient_text"))
            assertTrue(report.getJSONObject("camera").getString("camera_id").matches(Regex("camera2-sha256:[0-9a-f]{64}")))
            val original = root.resolve("benchmarks/$id.json").readBytes()
            val b = benchmark.start(60)
            assertFalse(benchmark.confirmStart(id))
            assertTrue(benchmark.isActive)
            assertArrayEquals(original, root.resolve("benchmarks/$id.json").readBytes())
            val fixture = JSONObject().put("mode", mode).put("report", report)
            val control = root.resolve("benchmarks/$id.control.json")
            if (control.isFile) fixture.put("control", JSONObject(control.readText()))
            println("NATIVE_RECEIPT_FIXTURE " + fixture.toString())
            assertTrue(benchmark.confirmStart(b))
            benchmark.finish()
        }
    }

    @Test fun unconfirmedFullWindowRemainsDiagnosticAfterReplacementAndLateResponse() {
        val root = java.io.File(context.cacheDir, "control-${java.util.UUID.randomUUID()}").apply { mkdirs() }
        root.resolve("benchmarks/next_setup.json").apply { parentFile!!.mkdirs(); writeText(validSetup().toString()) }
        val benchmark = BenchmarkMode(setupContext(root))
        benchmark.recordCamera("default_front", "front", true, "synthetic-front")
        val a = benchmark.start(60)
        repeat(60) { repeat(30) { benchmark.recordAnalyzer() }; shadowOf(Looper.getMainLooper()).idleFor(Duration.ofSeconds(1)) }
        val original = root.resolve("benchmarks/$a.json").readBytes()
        val completed = JSONObject(benchmark.latestResults()!!)
        assertEquals("unconfirmed", completed.optString("control_status"))
        assertTrue(completed.getBoolean("complete"))
        assertEquals(1800, completed.getInt("analyzer_count"))
        assertFalse(completed.getBoolean("physical_fps_gate_pass"))
        val b = benchmark.start(60)
        val confirm = BenchmarkMode::class.java.getMethod("confirmStart", String::class.java)
        assertEquals(false, confirm.invoke(benchmark, a))
        assertTrue(benchmark.isActive)
        assertEquals(true, confirm.invoke(benchmark, b))
        assertArrayEquals(original, root.resolve("benchmarks/$a.json").readBytes())
        assertEquals("unconfirmed", JSONObject(root.resolve("benchmarks/$a.control.json").readText()).getString("status"))
        assertEquals("confirmed", JSONObject(root.resolve("benchmarks/$b.control.json").readText()).getString("status"))
        benchmark.finish()
        assertEquals(false, confirm.invoke(benchmark, b))
        println("NATIVE_CONTROL_FIXTURE " + JSONObject().put("report", completed)
            .put("control", JSONObject(root.resolve("benchmarks/$a.control.json").readText())).toString())
    }

    @Test fun failureCensusUsesFixedCodesWithUnknownClassFallback() {
        val benchmark = BenchmarkMode(context)
        benchmark.start(60)
        for (code in listOf("SecurityException", "FileNotFoundException", "IOException", "no_signer", "PRIVATE_patient_class")) benchmark.recordFailure(code)
        val report = JSONObject(benchmark.finish())
        assertEquals(5, report.getInt("failure_count"))
        val codes = report.getJSONObject("failures")
        assertEquals(1, codes.getInt("SecurityException"))
        assertEquals(1, codes.getInt("FileNotFoundException"))
        assertEquals(1, codes.getInt("failure"))
        assertFalse(report.toString().contains("PRIVATE"))
    }

    @Test fun malformedAttemptIdentitiesNeverReachRetainedNativeEvidence() {
        val benchmark = BenchmarkMode(context)
        benchmark.start(60)
        val marker = "PRIVATE patient text"
        val ns = android.os.SystemClock.elapsedRealtimeNanos()
        benchmark.recordAttemptStart(marker, ns)
        benchmark.recordOutcome(marker, "failure")
        benchmark.recordTrace(JSONObject().put("attempt_id", marker).put("first_analyzer_ns", ns)
            .put("final_analyzer_ns", ns).put("native_result_ns", ns).put("event_delivery_ns", ns))
        assertFalse(benchmark.finish().contains(marker))
    }

    @Test fun confirmationDeadlineAndPublicationFailureFailClosed() {
        for (millis in listOf(29999L, 30000L, 30001L)) {
            val benchmark = BenchmarkMode(context)
            val id = benchmark.start(60)
            shadowOf(Looper.getMainLooper()).idleFor(Duration.ofMillis(millis))
            assertEquals(millis < 30000, benchmark.confirmStart(id))
            benchmark.finish()
        }
        val root = java.io.File(context.cacheDir, "control-write-fault-${java.util.UUID.randomUUID()}").apply { mkdirs() }
        val benchmark = BenchmarkMode(setupContext(root))
        val id = benchmark.start(60)
        val target = root.resolve("benchmarks/$id.control.json")
        target.delete()
        target.mkdirs()
        target.resolve("sentinel").writeText("unchanged")
        assertFalse(benchmark.confirmStart(id))
        assertEquals("unchanged", target.resolve("sentinel").readText())
        assertEquals("unconfirmed", JSONObject(benchmark.finish()).getString("control_status"))
    }

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
        val trace = JSONObject().put("attempt_id", "c6e0ece0-0ae9-544d-ace9-535d16533233").put("first_analyzer_ns", ns)
            .put("final_analyzer_ns", ns).put("native_result_ns", ns + 1)
            .put("event_delivery_ns", ns + 2).put("raw_video", "never store")
        BenchmarkMode::class.java.getMethod("recordTrace", JSONObject::class.java).invoke(benchmark, trace)
        trace.put("attempt_id", "af76c7e6-adf1-553f-bfd5-bdf64a2b067b")
        val report = JSONObject(benchmark.finish())
        val saved = report.getJSONArray("traces").getJSONObject(0)
        assertEquals("c6e0ece0-0ae9-544d-ace9-535d16533233", saved.getString("attempt_id"))
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
        benchmark.recordTrace(JSONObject().put("attempt_id", "ec381b92-e053-526d-998b-f240cfc5f549")
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
        benchmark.recordTrace(trace("b8e5a829-7e55-58ee-9307-2259fefc0fb2", first = ns - 1))
        benchmark.recordTrace(trace("383a5a5a-7da8-558a-85af-9df80f94a3e1", event = ns + 60_000_000_000L))
        benchmark.recordTrace(trace("9d5dfced-cfd4-53b4-b467-c93c018606e0"))
        benchmark.recordTrace(trace("9d5dfced-cfd4-53b4-b467-c93c018606e0").put("ui_ack_ns", ns + 60_000_000_000L))
        val report = JSONObject(benchmark.finish())
        val saved = report.getJSONArray("traces")
        assertEquals(1, saved.length())
        assertEquals("9d5dfced-cfd4-53b4-b467-c93c018606e0", saved.getJSONObject(0).getString("attempt_id"))
        assertFalse(saved.getJSONObject(0).has("ui_ack_ns"))
        assertEquals(3, report.getJSONArray("excluded_samples").length())
    }

    @Test fun attemptStartedBeforeRunIsNotRelabelledIntoRun() {
        val benchmark = BenchmarkMode(context)
        benchmark.start(60)
        val ns = android.os.SystemClock.elapsedRealtimeNanos()
        val trace = PipelineTrace("fbb22bc1-66cf-5ea7-afc7-1a56d65a618c", ns, ns, ns + 1, 0).toJson()
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
        val isolated = setupContext(root)
        val benchmark = BenchmarkMode(isolated)
        val id = benchmark.start(60)
        val returned = JSONObject(benchmark.finish())
        assertTrue("real latest failure must be observed", returned.has("storage_error"))
        val retained = JSONObject(java.io.File(directory, "$id.json").readText())
        assertEquals("immutable_only_latest_unverified", retained.getString("storage_state"))
        assertFalse(retained.getBoolean("physical_fps_gate_pass"))
        assertNull(benchmark.reportPath)
    }

    @Test fun nonthrowingFinalTargetFailureCannotPublishImmutableOrLatest() {
        for (blockedLatest in listOf(false, true)) {
            val root = java.io.File(context.cacheDir, "commit-fault-${java.util.UUID.randomUUID()}").apply { mkdirs() }
            val directory = java.io.File(root, "benchmarks").apply { mkdirs() }
            val isolated = setupContext(root)
            val benchmark = BenchmarkMode(isolated)
            val id = benchmark.start(60)
            val target = java.io.File(directory, if (blockedLatest) "latest.json" else "$id.json").apply { mkdirs() }
            val sentinel = target.resolve("sentinel").apply { writeText("unchanged") }
            val returned = JSONObject(benchmark.finish())
            assertEquals("publication_failed", returned.getString("storage_state"))
            assertFalse(returned.getBoolean("physical_fps_gate_pass"))
            assertNull(benchmark.reportPath)
            assertEquals("unchanged", sentinel.readText())
            if (blockedLatest) {
                val immutable = JSONObject(java.io.File(directory, "$id.json").readText())
                assertEquals("immutable_only_latest_unverified", immutable.getString("storage_state"))
            } else assertFalse(java.io.File(directory, "latest.json").exists())
            target.deleteRecursively()
            val retryId = benchmark.start(60)
            val retry = JSONObject(benchmark.finish())
            assertEquals("latest_published", retry.getString("storage_state"))
            assertEquals(retryId, JSONObject(java.io.File(directory, "latest.json").readText()).getString("run_id"))
            assertEquals(retryId, JSONObject(java.io.File(benchmark.reportPath!!).readText()).getString("run_id"))
        }
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

    @Test fun correctlyShapedWrongApkDigestCannotQualifySetup() {
        val root = java.io.File(context.cacheDir, "apk-setup-${java.util.UUID.randomUUID()}").apply { mkdirs() }
        val apk = java.io.File(root, "synthetic.apk").apply { writeText("synthetic APK bytes") }
        val isolated = object : android.content.ContextWrapper(context) {
            override fun getFilesDir() = root
            override fun getApplicationInfo() = android.content.pm.ApplicationInfo(context.applicationInfo).apply {
                sourceDir = apk.absolutePath; splitSourceDirs = null
            }
        }
        val manifest = java.io.File(root, "benchmarks/next_setup.json").apply { parentFile!!.mkdirs() }
        manifest.writeText(validSetup().put("apk_sha256", "d".repeat(64)).toString())
        val benchmark = BenchmarkMode(isolated)
        benchmark.recordCamera("default_front", "front", true, "synthetic-front")
        benchmark.start(60)
        val report = JSONObject(benchmark.finish())
        assertEquals("diagnostic", report.getString("measurement_status"))
        assertTrue(report.getJSONArray("setup_errors").toString().contains("setup_apk_identity_mismatch"))
        assertFalse(report.getBoolean("physical_fps_gate_pass"))
    }

    @Test fun unavailableAndSplitApkIdentityAreDiagnostic() {
        for (split in listOf(false, true)) {
            val root = java.io.File(context.cacheDir, "unavailable-apk-${java.util.UUID.randomUUID()}").apply { mkdirs() }
            val base = setupContext(root)
            val isolated = object : android.content.ContextWrapper(base) {
                override fun getApplicationInfo() = android.content.pm.ApplicationInfo(base.applicationInfo).apply {
                    if (split) splitSourceDirs = arrayOf("synthetic-split.apk") else sourceDir = root.resolve("missing.apk").absolutePath
                }
            }
            root.resolve("benchmarks/next_setup.json").apply { parentFile!!.mkdirs(); writeText(validSetup().toString()) }
            val benchmark = BenchmarkMode(isolated)
            benchmark.recordCamera("default_front", "front", true, "synthetic-front")
            benchmark.start(60)
            val report = JSONObject(benchmark.finish())
            assertEquals("diagnostic", report.getString("measurement_status"))
            assertTrue(report.getJSONArray("setup_errors").toString().contains("setup_apk_identity_unavailable"))
            assertFalse(report.getBoolean("physical_fps_gate_pass"))
        }
    }

    private val syntheticApkBytes = "synthetic APK bytes".toByteArray()
    private val syntheticApkDigest = java.security.MessageDigest.getInstance("SHA-256")
        .digest(syntheticApkBytes).joinToString("") { "%02x".format(it.toInt() and 0xff) }
    private fun setupContext(root: java.io.File): android.content.Context {
        val apk = java.io.File(root, "synthetic.apk").apply { writeBytes(syntheticApkBytes) }
        return object : android.content.ContextWrapper(context) {
            override fun getFilesDir() = root
            override fun getApplicationInfo() = android.content.pm.ApplicationInfo(context.applicationInfo).apply {
                sourceDir = apk.absolutePath; splitSourceDirs = null
            }
        }
    }
    private fun validSetup() = JSONObject().put("setup_id", "33333333-3333-4333-8333-333333333333")
        .put("condition", "optimal").put("lux", 400).put("background", "plain").put("distance_cm", 75)
        .put("device_fingerprint", android.os.Build.FINGERPRINT).put("chip", "Snapdragon 680").put("ram_gb", 4)
        .put("setup_verified", true).put("device_verified", true).put("front_camera_verified", true)
        .put("apk_sha256", syntheticApkDigest).put("revision", "b".repeat(40)).put("thermal_state", "nominal")

    @Test fun provisionedSetupIsValidatedAndImmutableForItsRun() {
        val root = java.io.File(context.cacheDir, "setup-${java.util.UUID.randomUUID()}").apply { mkdirs() }
        val isolated = setupContext(root)
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
        val isolated = setupContext(root)
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
        val isolated = setupContext(root)
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
        start.invoke(benchmark, "24bb0a68-bace-5cc2-9be4-4e94b6cc0c95", ns)
        shadowOf(Looper.getMainLooper()).idleFor(Duration.ofSeconds(60))
        val report = JSONObject(benchmark.latestResults()!!)
        assertEquals(1, report.getInt("attempt_count"))
        assertEquals(1, report.getInt("censored_count"))
        assertEquals("censored_at_close", report.getJSONArray("outcomes").getJSONObject(0).getString("code"))
        assertEquals(0, report.getJSONArray("traces").length())
        val trace = PipelineTrace("24bb0a68-bace-5cc2-9be4-4e94b6cc0c95", ns, ns + 1, ns + 2, 0, ns).toJson()
            .put("event_delivery_ns", ns + 60_000_000_001L)
        benchmark.recordTrace(trace)
        benchmark.recordOutcome("24bb0a68-bace-5cc2-9be4-4e94b6cc0c95", "success")
        assertEquals(report.toString(), JSONObject(benchmark.latestResults()!!).toString())
    }

    @Test fun outcomeFromAttemptNotStartedInRunIsExplicitlyExcludedNotRelabelled() {
        val benchmark = BenchmarkMode(context)
        benchmark.start(60)
        benchmark.recordOutcome("d2db00a1-84c4-538e-a8a8-96c1582e9e92", "no_signer")
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
