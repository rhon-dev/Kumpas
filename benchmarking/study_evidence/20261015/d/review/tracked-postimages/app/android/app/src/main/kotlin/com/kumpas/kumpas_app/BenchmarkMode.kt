package com.kumpas.kumpas_app

import android.content.Context
import android.os.Build
import android.os.Handler
import android.os.Looper
import android.os.SystemClock
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.util.UUID
import java.security.MessageDigest

/** Monotonic CameraX analyzer benchmark; output contains timings only. */
class BenchmarkMode(private val context: Context, private val onComplete: (String) -> Unit = {}) {
    companion object {
        private val uuidFormat = Regex("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
        private val supportedChips = setOf("Snapdragon 680", "Helio G80")
        private val failureCodes = setOf("no_signer", "persistence_failed", "failure", "IOException",
            "FileNotFoundException", "IllegalStateException", "IllegalArgumentException", "RuntimeException", "SecurityException")
        fun safeFailureCode(reason: String): String = if (reason in failureCodes) reason else "failure"
    }
    private val handler = Handler(Looper.getMainLooper())
    private var metrics: PipelineMetrics? = null
    private var runId = ""
    private var controlConfirmed = false
    private var controlPersisted = false
    private var deadline: Runnable? = null
    private var results: String? = null
    private val traces = linkedMapOf<String, JSONObject>()
    private val outcomes = linkedMapOf<String, JSONObject>()
    private val attemptStarts = linkedMapOf<String, Long>()
    private val excludedSamples = mutableListOf<JSONObject>()
    private var modelMetadata = JSONObject()
    private var buildMetadata = JSONObject()
    private var setupMetadata = JSONObject()
    private var setupErrors = listOf("setup_missing")
    private var currentCamera = JSONObject().put("lens", "unknown").put("selector", "unknown")
        .put("bound", false).put("changed", false)
    private var cameraMetadata = JSONObject(currentCamera.toString())
    @Volatile var isActive = false
        private set
    @Volatile var reportPath: String? = null
        private set

    @Synchronized fun start(durationSeconds: Int = 60): String {
        check(!isActive) { "Benchmark already active" }
        require(durationSeconds >= 60) { "Benchmark requires at least 60 seconds" }
        modelMetadata = JSONObject().put("asset", "kumpas_50sign.tflite")
        try {
            val digest = MessageDigest.getInstance("SHA-256")
            context.assets.open("kumpas_50sign.tflite").use { input ->
                val buffer = ByteArray(8192)
                var size = input.read(buffer)
                while (size >= 0) {
                    digest.update(buffer, 0, size)
                    size = input.read(buffer)
                }
            }
            modelMetadata.put("sha256", digest.digest().joinToString("") { "%02x".format(it.toInt() and 0xff) })
        } catch (error: Exception) {
            modelMetadata.put("metadata_error", safeFailureCode(error.javaClass.simpleName))
        }
        val info = context.packageManager.getPackageInfo(context.packageName, 0)
        buildMetadata = JSONObject().put("version_name", info.versionName ?: JSONObject.NULL)
            .put("version_code", if (Build.VERSION.SDK_INT >= 28) info.longVersionCode else info.versionCode.toLong())
            .put("debuggable", context.applicationInfo.flags and android.content.pm.ApplicationInfo.FLAG_DEBUGGABLE != 0)
        captureSetup()
        cameraMetadata = JSONObject(currentCamera.toString()).put("changed", false)
        runId = UUID.randomUUID().toString()
        controlConfirmed = false
        controlPersisted = try { publishControl("unconfirmed"); true } catch (_: Exception) { false }
        metrics = PipelineMetrics(SystemClock.elapsedRealtimeNanos(), durationSeconds)
        traces.clear()
        outcomes.clear()
        attemptStarts.clear()
        excludedSamples.clear()
        results = null
        reportPath = null
        isActive = true
        deadline = Runnable { finish() }.also { handler.postDelayed(it, durationSeconds * 1000L) }
        return runId
    }

    private fun publishControl(status: String) {
        val directory = File(context.filesDir, "benchmarks").apply { check(mkdirs() || isDirectory) }
        atomicWrite(File(directory, "$runId.control.json"), JSONObject().put("schema_version", 1)
            .put("run_id", runId).put("status", status).toString())
    }

    /** Only timely, still-active ownership can be confirmed. Closed/late runs never upgrade. */
    @Synchronized fun confirmStart(expectedRunId: String): Boolean {
        if (expectedRunId != runId || !isActive || !controlPersisted ||
            SystemClock.elapsedRealtimeNanos() - metrics!!.startNs >= 30_000_000_000L) return false
        return try {
            publishControl("confirmed")
            controlConfirmed = true
            true
        } catch (_: Exception) { controlConfirmed = false; false }
    }

    private fun captureSetup() {
        setupMetadata = JSONObject()
        val errors = mutableListOf<String>()
        val file = File(context.filesDir, "benchmarks/next_setup.json")
        if (!file.exists()) { setupErrors = listOf("setup_missing"); return }
        val strings = setOf("setup_id", "condition", "background", "device_fingerprint", "chip", "apk_sha256", "revision", "thermal_state")
        val numbers = setOf("lux", "distance_cm", "ram_gb")
        val flags = setOf("setup_verified", "device_verified", "front_camera_verified")
        try {
            require(file.length() <= 8192) { "Oversize setup" }
            android.util.JsonReader(java.io.StringReader(file.readText())).use { reader ->
                reader.beginObject()
                val seen = mutableSetOf<String>()
                while (reader.hasNext()) {
                    val key = reader.nextName()
                    require(seen.add(key)) { "Duplicate setup field" }
                    val token = reader.peek()
                    when {
                        key in strings && token == android.util.JsonToken.STRING -> {
                            val value = reader.nextString()
                            if (value.length in 1..256 && !value.contains('\n')) setupMetadata.put(key, value)
                            else errors.add("setup_invalid_field")
                        }
                        key in numbers && token == android.util.JsonToken.NUMBER -> {
                            val value = reader.nextDouble()
                            if (value.isFinite()) setupMetadata.put(key, value) else errors.add("setup_invalid_field")
                        }
                        key in flags && token == android.util.JsonToken.BOOLEAN -> setupMetadata.put(key, reader.nextBoolean())
                        else -> { reader.skipValue(); errors.add("setup_invalid_field") }
                    }
                }
                reader.endObject()
                require(reader.peek() == android.util.JsonToken.END_DOCUMENT) { "Trailing setup data" }
            }
        } catch (_: Exception) {
            setupMetadata = JSONObject()
            errors.add("setup_malformed")
        }
        fun invalid(ok: Boolean, code: String) { if (!ok) errors.add(code) }
        fun number(key: String) = (setupMetadata.opt(key) as? Number)?.toDouble()
        val condition = setupMetadata.optString("condition")
        val lux = number("lux")
        invalid(condition in setOf("optimal", "low_light", "cluttered"), "setup_condition_invalid")
        invalid(lux != null && lux.isFinite() && lux >= 0 &&
            (if (condition == "low_light") lux < 100 else lux > 300), "setup_lux_invalid")
        invalid(setupMetadata.optString("background") == (if (condition == "cluttered") "complex" else "plain"), "setup_background_invalid")
        invalid(number("distance_cm")?.let { it in 60.0..90.0 } == true, "setup_distance_invalid")
        invalid(number("ram_gb")?.let { it in 4.0..64.0 } == true, "setup_ram_invalid")
        invalid(setupMetadata.optString("chip") in supportedChips, "setup_chip_invalid")
        invalid(setupMetadata.optString("device_fingerprint") == Build.FINGERPRINT, "setup_device_mismatch")
        flags.forEach { invalid(setupMetadata.opt(it) == true, "setup_verification_missing") }
        invalid(setupMetadata.optString("setup_id").matches(uuidFormat), "setup_identity_invalid")
        val declaredApk = setupMetadata.optString("apk_sha256")
        invalid(declaredApk.matches(Regex("[0-9a-f]{64}")), "setup_apk_identity_invalid")
        // Hash before creating PipelineMetrics: setup I/O is outside observation.
        val installedApk = try {
            val appInfo = context.applicationInfo
            require(appInfo.splitSourceDirs.isNullOrEmpty()) { "Split APK unsupported" }
            val source = File(requireNotNull(appInfo.sourceDir))
            require(source.isFile && source.canRead()) { "APK unavailable" }
            val digest = MessageDigest.getInstance("SHA-256")
            source.inputStream().use { input ->
                val buffer = ByteArray(8192)
                var size = input.read(buffer)
                while (size >= 0) {
                    digest.update(buffer, 0, size)
                    size = input.read(buffer)
                }
            }
            digest.digest().joinToString("") { "%02x".format(it.toInt() and 0xff) }
        } catch (_: Exception) { null }
        invalid(installedApk != null, "setup_apk_identity_unavailable")
        if (installedApk != null) invalid(declaredApk == installedApk, "setup_apk_identity_mismatch")
        invalid(setupMetadata.optString("revision").matches(Regex("[0-9a-f]{40}|[0-9a-f]{64}")), "setup_revision_invalid")
        invalid(setupMetadata.optString("thermal_state") in setOf("nominal", "fair", "serious", "critical"), "setup_thermal_missing")
        // Validate before retention too: rejection is not a privacy sanitizer.
        val formats = mapOf(
            "setup_id" to uuidFormat,
            "condition" to Regex("optimal|low_light|cluttered"),
            "background" to Regex("plain|complex"),
            "chip" to Regex("Snapdragon 680|Helio G80"),
            "apk_sha256" to Regex("[0-9a-f]{64}"), "revision" to Regex("[0-9a-f]{40}|[0-9a-f]{64}"),
            "thermal_state" to Regex("nominal|fair|serious|critical"))
        formats.forEach { (key, format) ->
            if (setupMetadata.has(key) && !setupMetadata.optString(key).matches(format)) {
                setupMetadata.remove(key); errors.add("setup_invalid_field")
            }
        }
        if (setupMetadata.has("device_fingerprint") && setupMetadata.optString("device_fingerprint") != Build.FINGERPRINT) {
            setupMetadata.remove("device_fingerprint"); errors.add("setup_device_mismatch")
        }
        setupErrors = errors.distinct()
    }

    @Synchronized fun recordCamera(selector: String, lens: String, bound: Boolean, cameraId: String) {
        val next = JSONObject().put("selector", if (selector in setOf("default_front", "default_back_fallback")) selector else "unknown")
            .put("lens", if (lens in setOf("front", "back")) lens else "unknown")
            .put("bound", bound).put("camera_id", if (bound && cameraId.isNotEmpty() && cameraId != "unknown") "camera2-sha256:" +
                MessageDigest.getInstance("SHA-256").digest(cameraId.toByteArray(Charsets.UTF_8))
                    .joinToString("") { "%02x".format(it.toInt() and 0xff) } else "unknown")
            .put("changed", false)
        if (isActive && (cameraMetadata.optString("lens") != next.optString("lens") ||
            cameraMetadata.optString("camera_id") != next.optString("camera_id") ||
            cameraMetadata.optString("selector") != next.optString("selector") ||
            cameraMetadata.optBoolean("bound") != bound)) next.put("changed", true)
        if (isActive && cameraMetadata.optBoolean("changed")) next.put("changed", true)
        currentCamera = JSONObject(next.toString()).put("changed", false)
        if (isActive) cameraMetadata = next
    }

    private fun setupQualified(): Boolean = setupErrors.isEmpty() && cameraMetadata.optBoolean("bound") &&
        cameraMetadata.optString("lens") == "front" && cameraMetadata.optString("selector") == "default_front" &&
        !cameraMetadata.optBoolean("changed") && cameraMetadata.optString("camera_id") !in setOf("", "unknown")

    /** Legacy event tick, never a camera-frame counter. */
    @Synchronized fun recordFrame(): Boolean = isActive &&
        SystemClock.elapsedRealtimeNanos() - metrics!!.startNs >= metrics!!.durationNs

    @Synchronized fun recordAnalyzer() = record(PipelineMetrics.Stage.ANALYZER)
    @Synchronized fun recordSelected() = record(PipelineMetrics.Stage.SELECTED)
    @Synchronized fun recordProcessed() = record(PipelineMetrics.Stage.PROCESSED)
    @Synchronized fun recordEvent() = record(PipelineMetrics.Stage.EVENT)
    @Synchronized fun recordFailure(reason: String) {
        if (isActive) metrics!!.recordFailure(safeFailureCode(reason), SystemClock.elapsedRealtimeNanos())
    }
    @Synchronized fun recordAttemptStart(attemptId: String, startedNs: Long) {
        if (!isActive || !attemptId.matches(uuidFormat)) return
        val m = metrics!!
        if (startedNs < m.startNs || startedNs >= m.startNs + m.durationNs) {
            exclude(attemptId, "attempt_start_outside_window", startedNs)
            return
        }
        attemptStarts.putIfAbsent(attemptId, startedNs)
    }

    @Synchronized fun recordOutcome(attemptId: String, code: String) {
        if (!isActive || !attemptId.matches(uuidFormat)) return
        require(code in setOf("success", "no_signer", "cancelled", "timeout", "camera_error", "persistence_failed", "failure")) { "Unknown outcome" }
        val now = SystemClock.elapsedRealtimeNanos()
        if (!attemptStarts.containsKey(attemptId)) {
            exclude(attemptId, "outcome_unbound_attempt", now)
            return
        }
        val m = metrics!!
        if (now < m.startNs || now >= m.startNs + m.durationNs) {
            exclude(attemptId, "outcome_outside_window", now)
            return
        }
        if (outcomes.containsKey(attemptId)) return
        outcomes[attemptId] = JSONObject().put("attempt_id", attemptId).put("code", code).put("at_ns", now)
        if (code in setOf("no_signer", "persistence_failed", "failure")) m.recordFailure(code, now)
    }
    private fun record(stage: PipelineMetrics.Stage) {
        if (isActive) metrics!!.record(stage, SystemClock.elapsedRealtimeNanos())
    }

    private fun exclude(id: String, reason: String, at: Long) {
        excludedSamples.add(JSONObject().apply { if (id.matches(uuidFormat)) put("attempt_id", id) }.put("reason", reason).put("at_ns", at))
    }

    /** Copies an allowlist only; repeated attempt IDs update the optional native UI ACK. */
    @Synchronized fun recordTrace(trace: JSONObject) {
        if (!isActive) return
        val m = metrics!!
        val id = trace.optString("attempt_id")
        val times = listOf("first_analyzer_ns", "final_analyzer_ns", "native_result_ns", "event_delivery_ns")
        if (!id.matches(uuidFormat) || times.any { trace.opt(it) !is Number }) {
            exclude(id, "malformed_trace", SystemClock.elapsedRealtimeNanos())
            return
        }
        val values = times.map { trace.getLong(it) }
        val started = trace.optLong("attempt_started_ns", values.first())
        if (started < m.startNs || values.any { it < m.startNs || it >= m.startNs + m.durationNs } || values != values.sorted()) {
            exclude(id, "trace_outside_window_or_order", values.last())
            return
        }
        val copy = JSONObject()
        val keys = listOf("attempt_id", "attempt_started_ns", "first_analyzer_ns", "final_analyzer_ns", "native_result_ns",
            "event_delivery_ns", "ui_ack_ns", "inference_ms", "collection_ms")
        keys.filter { trace.has(it) }.forEach { key ->
            val value = trace.get(key)
            if ((key == "attempt_id" && value is String) || (key != "attempt_id" && value is Number))
                copy.put(key, value)
        }
        if (copy.has("ui_ack_ns") && (copy.getLong("ui_ack_ns") < values.last() || copy.getLong("ui_ack_ns") >= m.startNs + m.durationNs)) {
            exclude(id, "ack_outside_window_or_order", copy.getLong("ui_ack_ns"))
            copy.remove("ui_ack_ns")
            if (traces.containsKey(id)) return // Preserve the valid dispatch sample, never overwrite with late ACK.
        }
        copy.put("run_id", runId).put("clock", "elapsedRealtimeNanos")
        fun delta(from: String, to: String, field: String) {
            val a = copy.opt(from) as? Number
            val b = copy.opt(to) as? Number
            if (a != null && b != null && b.toLong() >= a.toLong())
                copy.put(field, (b.toLong() - a.toLong()) / 1e6)
        }
        delta("final_analyzer_ns", "event_delivery_ns", "final_analyzer_to_event_ms")
        delta("final_analyzer_ns", "event_delivery_ns", "analyzer_to_feedback_ms")
        delta("final_analyzer_ns", "ui_ack_ns", "final_analyzer_to_ui_ack_ms")
        delta("first_analyzer_ns", "ui_ack_ns", "first_analyzer_to_ui_ack_ms")
        traces[id] = copy
    }

    @Synchronized fun finish(): String {
        if (!isActive) return checkNotNull(results) { "No benchmark has started" }
        val m = metrics!!
        val s = m.snapshot(SystemClock.elapsedRealtimeNanos())
        val closeNs = m.startNs + (s.durationSeconds * 1e9).toLong()
        for ((id, started) in attemptStarts) {
            if (!outcomes.containsKey(id)) outcomes[id] = JSONObject().put("attempt_id", id)
                .put("attempt_started_ns", started).put("code", "censored_at_close").put("at_ns", closeNs)
        }
        val fps = JSONObject()
        s.rates.forEach { (stage, rate) ->
            fps.put(stage.name.lowercase(), JSONObject().put("count", rate.count)
                .put("mean_fps", rate.meanFps).put("per_second_samples", JSONArray(rate.perSecondSamples)))
        }
        val report = JSONObject().put("schema_version", 2).put("run_id", runId)
            .put("package", context.packageName).put("source", "camerax_analyzer")
            .put("clock", "elapsedRealtimeNanos").put("origin", "analyzer_entry_not_sensor_exposure")
            .put("ui_endpoint", "post_frame_native_ack_upper_bound_not_physical_display")
            .put("build", buildMetadata).put("model", modelMetadata).put("start_ns", m.startNs)
            .put("setup", JSONObject(setupMetadata.toString())).put("setup_errors", JSONArray(setupErrors))
            .put("camera", JSONObject(cameraMetadata.toString())).put("measurement_status", if (setupQualified()) "qualified_setup" else "diagnostic")
            .put("end_ns", m.startNs + (s.durationSeconds * 1e9).toLong())
            .put("duration_s", s.durationSeconds).put("requested_duration_s", m.requestedDurationSeconds)
            .put("control_status", if (controlConfirmed) "confirmed" else "unconfirmed")
            .put("complete", s.complete).put("analyzer_count", s.analyzer.count)
            .put("selected_count", s.rates.getValue(PipelineMetrics.Stage.SELECTED).count)
            .put("processed_count", s.rates.getValue(PipelineMetrics.Stage.PROCESSED).count)
            .put("event_count", s.rates.getValue(PipelineMetrics.Stage.EVENT).count)
            .put("failure_count", s.failureCount).put("fps", fps)
            .put("traces", JSONArray(traces.values.toList())).put("failures", JSONObject(s.failures))
            .put("outcomes", JSONArray(outcomes.values.toList()))
            .put("attempts", JSONArray(attemptStarts.map { (id, started) ->
                JSONObject().put("attempt_id", id).put("attempt_started_ns", started) }))
            .put("attempt_count", attemptStarts.size)
            .put("censored_count", outcomes.values.count { it.optString("code") == "censored_at_close" })
            .put("excluded_samples", JSONArray(excludedSamples))
            .put("device", JSONObject().put("manufacturer", Build.MANUFACTURER).put("model", Build.MODEL)
                .put("hardware", Build.HARDWARE).put("fingerprint", Build.FINGERPRINT)
                .put("sdk_int", Build.VERSION.SDK_INT).put("is_emulator", isEmulator()))
            .put("physical_fps_gate_pass", controlConfirmed && setupQualified() && s.sustainedAnalyzerPass(isEmulator()))
        isActive = false
        deadline?.let(handler::removeCallbacks)
        try {
            val directory = File(context.filesDir, "benchmarks").apply { check(mkdirs() || isDirectory) }
            val file = File(directory, "$runId.json")
            // Immutable evidence does not promise that the separate latest publication succeeded.
            val immutable = JSONObject(report.toString()).put("storage_state", "immutable_only_latest_unverified")
                .put("physical_fps_gate_pass", false)
            atomicWrite(file, immutable.toString(2))
            report.put("storage_state", "latest_published")
            val json = report.toString(2)
            atomicWrite(File(directory, "latest.json"), json)
            reportPath = file.absolutePath
        } catch (error: Exception) {
            report.put("storage_state", "publication_failed").put("storage_error", safeFailureCode(error.javaClass.simpleName))
                .put("physical_fps_gate_pass", false)
            reportPath = null
        }
        val json = report.toString(2)
        results = json
        onComplete(json)
        return json
    }
    @Synchronized fun latestResults(): String? = if (isActive) null else results ?: File(context.filesDir, "benchmarks/latest.json")
        .takeIf { it.isFile }?.readText()
    private fun atomicWrite(file: File, json: String) {
        val atomic = android.util.AtomicFile(file)
        val stream = atomic.startWrite()
        try { stream.write(json.toByteArray(Charsets.UTF_8)); atomic.finishWrite(stream) }
        catch (error: Exception) { atomic.failWrite(stream); throw error }
        // AtomicFile.finishWrite can log a failed rename without throwing.
        // Verify the exact target, not .new or a helper's successful return.
        val expected = json.toByteArray(Charsets.UTF_8)
        check(file.isFile && file.readBytes().contentEquals(expected)) { "Report commit verification failed" }
        check(JSONObject(file.readText()).getString("run_id") == runId) { "Report commit identity mismatch" }
    }
    @Synchronized fun reportFor(expectedRunId: String): String? {
        require(expectedRunId.matches(Regex("[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"))) { "Invalid run UUID" }
        if (expectedRunId == runId) return if (isActive) null else results
        val file = File(context.filesDir, "benchmarks/$expectedRunId.json")
        return file.takeIf { it.isFile }?.readText()?.also {
            check(JSONObject(it).getString("run_id") == expectedRunId) { "Report identity mismatch" }
        }
    }
    @Synchronized fun stop(expectedRunId: String): String {
        check(expectedRunId == runId) { "Stop request is not for the current run" }
        return if (isActive) finish() else checkNotNull(reportFor(expectedRunId)) { "No retained report" }
    }
    private fun isEmulator(): Boolean = Build.FINGERPRINT.startsWith("generic") ||
        Build.FINGERPRINT.contains("emulator") || Build.MODEL.contains("Emulator") ||
        Build.MODEL.contains("sdk", ignoreCase = true) || Build.HARDWARE in listOf("goldfish", "ranchu")
}
