package com.kumpas.kumpas_app

import android.os.Looper
import android.os.SystemClock
import io.flutter.plugin.common.MethodCall
import io.flutter.plugin.common.MethodChannel
import org.json.JSONArray
import org.json.JSONObject
import org.junit.Assert.*
import org.robolectric.Shadows.shadowOf
import java.io.File
import java.time.Duration
import java.util.UUID

/** Executed host fixture. All terminal inputs are constructed, never recognized/inferred. */
internal object HostStudyProducer {
    private class Reply : MethodChannel.Result {
        var value: Any? = null
        var code: String? = null
        var replies = 0
        override fun success(result: Any?) { replies++; value = result }
        override fun error(errorCode: String, message: String?, details: Any?) { replies++; code = errorCode }
        override fun notImplemented() { replies++; code = "NOT_IMPLEMENTED" }
    }
    private fun rows(db: SessionDatabase, table: String): JSONArray {
        require(table in setOf("participants", "sessions", "attempts", "assessments"))
        val result = JSONArray()
        db.readableDatabase.rawQuery("SELECT * FROM $table ORDER BY id", null).use { cursor ->
            while (cursor.moveToNext()) result.put(JSONObject().apply {
                cursor.columnNames.forEachIndexed { i, name -> put(name, when (cursor.getType(i)) {
                    android.database.Cursor.FIELD_TYPE_NULL -> JSONObject.NULL
                    android.database.Cursor.FIELD_TYPE_INTEGER -> cursor.getLong(i)
                    android.database.Cursor.FIELD_TYPE_FLOAT -> cursor.getDouble(i)
                    else -> cursor.getString(i)
                }) }
            })
        }
        return result
    }
    private fun snapshot(db: SessionDatabase) = JSONObject().apply {
        for (table in listOf("participants", "sessions", "attempts", "assessments")) put(table, rows(db, table))
    }
    private fun syntheticResult(id: String, label: String): String {
        val start = SystemClock.elapsedRealtimeNanos()
        shadowOf(Looper.getMainLooper()).idleFor(Duration.ofMillis(100))
        return JSONObject().put("state", "attempt_result").put("attemptId", id)
            .put("targetClass", 0).put("targetLabel", label).put("predictedLabel", label)
            .put("predictedConfidence", 0.9).put("recognizedAsTarget", true).put("overallMatch", 0.8)
            .put("items", JSONArray().put(JSONObject().put("dimension", "handshape").put("severity", 0.25).put("hand", "right").put("prompt", "SYNTHETIC feedback")))
            .put("timing", JSONObject().put("first_analyzer_ns", start + 10_000_000)
                .put("final_analyzer_ns", start + 50_000_000).put("native_result_ns", start + 75_000_000)
                .put("attempt_started_ns", start).put("inference_ms", 1)).toString()
    }
    private fun emit(activity: MainActivity, json: String) = MainActivity::class.java.getDeclaredMethod("handleVisionEvent", String::class.java)
        .apply { isAccessible = true }.invoke(activity, json)
    private fun drain() = shadowOf(Looper.getMainLooper()).idle()

    fun execute(): File {
        val run = HostArtifactRun(HostArtifactRun.freshDestination(), HostArtifactRun.sourceRoot())
        try {
            val study = study(run)
            val benchmark = benchmarks(run)
            val required = setOf("study.json", "attempt-event.json", "external-export.json", "internal-export.json", "reopened-export.json",
                "benchmark-index.json", "confirmed-report.json", "confirmed-control.json", "unconfirmed-report.json", "unconfirmed-control.json", "faulted-report.json")
            val manifest = run.publish(required, JSONObject().put("study", study).put("benchmark_modes", benchmark))
            println("HOST_STUDY_FIXTURE_ROOT ${run.root.absolutePath}")
            println("HOST_STUDY_FIXTURE_MANIFEST ${manifest.absolutePath}")
            return manifest
        } catch (error: Throwable) { run.failure(error); throw error }
    }
    private fun study(run: HostArtifactRun): JSONObject {
        val envelope = JSONObject().put("test_schema_version", HostArtifactRun.SCHEMA).put("run_id", run.runId)
            .put("scenario_id", UUID.randomUUID().toString()).put("synthetic_origin", true)
            .put("execution_boundary", "Real MainActivity callable, Handler/EventSink, SessionManager/SQLite/export/purge; no messenger, camera, detector or inference")
            .put("attempt_setup", "Direct production AttemptBoundary.start because bare Activity has no permission context; terminal handler is real")
            .put("history_correlation", "Unique synthetic target/predicted labels + class/confidence/match + exact row counts; no durable attempt UUID column")
        HostStudyFixture().use { f ->
            // Explicitly exercise both database-open overloads and canonical containment.
            assertSame(f.context, f.context.applicationContext)
            f.context.openOrCreateDatabase("overload-three.db", 0, null).use { assertEquals(f.context.getDatabasePath("overload-three.db").canonicalPath, File(it.path).canonicalPath) }
            f.context.openOrCreateDatabase("overload-four.db", 0, null, null).use { assertEquals(f.context.getDatabasePath("overload-four.db").canonicalPath, File(it.path).canonicalPath) }
            f.initialize()
            var control = f.activity.controlHandler(f.owner)
            val calls = JSONArray()
            var stage = "initialized"
            fun call(method: String, args: Map<String, Any?>? = null, error: String? = null): Any? {
                val reply = Reply()
                control.onMethodCall(MethodCall(method, args), reply)
                assertEquals("$stage/$method replies", 1, reply.replies)
                assertEquals("$stage/$method error", error, reply.code)
                calls.put(JSONObject().put("stage", stage).put("method", method).put("arguments", args?.let { JSONObject(it.toMutableMap()) } ?: JSONObject.NULL)
                    .put("response", reply.value ?: JSONObject.NULL).put("error_code", reply.code ?: JSONObject.NULL))
                return reply.value
            }
            val participant = call("getParticipantId") as String
            UUID.fromString(participant)
            val session = call("startSession") as String
            assertEquals(session, call("getActiveSession"))
            call("saveAssessment", mapOf("type" to "pre", "responses" to "{\"synthetic\":true,\"stage\":\"pre\"}"))
            val probe = f.database()
            probe.writableDatabase.execSQL("CREATE TRIGGER synthetic_assessment_fault BEFORE INSERT ON assessments BEGIN SELECT RAISE(ABORT, 'synthetic'); END")
            call("saveAssessment", mapOf("type" to "post", "responses" to "{\"synthetic\":true}"), "CONTROL_FAILED")
            assertEquals(1, rows(probe, "assessments").length())
            probe.writableDatabase.execSQL("DROP TRIGGER synthetic_assessment_fault")
            call("saveAssessment", mapOf("type" to "post", "responses" to "{\"synthetic\":true,\"stage\":\"post\"}"))
            assertEquals(2, JSONArray(call("getAssessments") as String).length())
            val attempts = MainActivity::class.java.getDeclaredField("attempts").apply { isAccessible = true }.get(f.activity) as AttemptBoundary
            stage = "one-terminal"
            val id = attempts.start(0)
            val input = syntheticResult(id, "SYNTHETIC_PRIMARY")
            emit(f.activity, input)
            assertEquals(1, rows(probe, "attempts").length()) // persistence precedes posted delivery
            assertTrue(f.events.isEmpty())
            drain()
            assertEquals(1, f.events.size)
            val event = JSONObject(f.events.single())
            assertEquals("attempt_result", event.getString("state"))
            assertEquals(id, event.getString("attemptId"))
            assertEquals("SYNTHETIC_PRIMARY", event.getString("targetLabel"))
            assertEquals(1, event.getJSONArray("items").length())
            val feedback = event.getJSONArray("items").getJSONObject(0)
            assertTrue("Synthetic feedback must satisfy the existing consumer's numeric severity contract", feedback.get("severity") is Number)
            assertTrue(feedback.get("hand") is String)
            assertTrue(feedback.get("prompt") is String)
            assertTrue(event.getJSONObject("timing").getLong("event_delivery_ns") >= event.getJSONObject("timing").getLong("native_result_ns"))
            run.write("attempt-event.json", f.events.single().toByteArray(), "event", "study")
            call("feedbackPresented", mapOf("attemptId" to id))
            call("feedbackPresented", mapOf("attemptId" to id)) // accepted ACK is once-only
            assertNull(MainActivity::class.java.getDeclaredField("pendingTrace").apply { isAccessible = true }.get(f.activity))
            emit(f.activity, input)
            drain()
            assertEquals(1, rows(probe, "attempts").length())
            assertEquals(1, f.events.size)
            val staleId = attempts.start(0)
            val stale = syntheticResult(staleId, "SYNTHETIC_STALE")
            call("cancelAttempt", mapOf("attemptId" to staleId))
            emit(f.activity, stale)
            drain()
            assertEquals(1, rows(probe, "attempts").length())
            assertEquals(1, f.events.size)
            val history = call("getHistory") as String
            assertEquals(1, JSONArray(history).length())
            assertFalse(JSONArray(history).getJSONObject(0).has("attemptId"))
            assertEquals(event.getString("targetLabel"), JSONArray(history).getJSONObject(0).getString("targetLabel"))
            envelope.put("primary", JSONObject().put("attempt_id", id).put("input_event", input).put("delivered_event", f.events.single())
                .put("history", history).put("independent_rows", snapshot(probe)).put("duplicate_event_count", f.events.size).put("stale_terminal_rows", (0 until rows(probe, "attempts").length()).count { rows(probe, "attempts").getJSONObject(it).getString("target_label") == "SYNTHETIC_STALE" }))
            // Foreign participant with actual data exposes accidental global export counts.
            val foreign = UUID.randomUUID().toString()
            val foreignSession = UUID.randomUUID().toString()
            probe.insertParticipant(foreign, "SYNTHETIC", "host")
            probe.insertSession(foreignSession, foreign)
            probe.insertAttempt(foreignSession, 1, 1, "SYNTHETIC_FOREIGN", "SYNTHETIC_FOREIGN", 0.7, true, 0.6, "[]")
            probe.insertAssessment(foreign, "pre", "{\"synthetic\":true}")
            stage = "export-before-queued-terminal"
            val external = f.contained(File(call("exportData") as String))
            assertEquals(f.external.canonicalFile, external.parentFile!!.canonicalFile)
            val externalBytes = external.readBytes()
            f.externalAvailable = false
            val internal = f.contained(File(call("exportData") as String))
            assertEquals(File(f.internal, "exports").canonicalFile, internal.parentFile!!.canonicalFile)
            val internalBytes = internal.readBytes()
            f.externalAvailable = true
            for (bytes in listOf(externalBytes, internalBytes)) {
                val export = JSONObject(bytes.toString(Charsets.UTF_8))
                assertEquals(participant, export.getJSONObject("metadata").getString("participant_id"))
                assertEquals(1, export.getJSONObject("summary").getInt("total_attempts"))
                assertEquals(1, export.getJSONObject("summary").getInt("total_sessions"))
                assertEquals(2, export.getJSONObject("summary").getInt("total_assessments"))
                assertEquals(session, export.getJSONArray("sessions").getJSONObject(0).getString("id"))
                assertEquals("SYNTHETIC_PRIMARY", export.getJSONArray("sessions").getJSONObject(0).getJSONArray("attempts").getJSONObject(0).getString("target_label"))
                assertFalse(bytes.toString(Charsets.UTF_8).contains("SYNTHETIC_FOREIGN"))
            }
            envelope.put("export_stage_independent_rows", snapshot(probe))
            run.write("external-export.json", externalBytes, "export", "study")
            run.write("internal-export.json", internalBytes, "export", "study")
            f.failExport = true
            call("exportData", error = "EXPORT_FAILED")
            assertFalse(f.opened.last().isOpen)
            assertArrayEquals(externalBytes, external.readBytes())
            assertArrayEquals(internalBytes, internal.readBytes())
            f.failExport = false
            stage = "persist-then-replace-before-handler-drain"
            val queuedId = attempts.start(0)
            emit(f.activity, syntheticResult(queuedId, "SYNTHETIC_QUEUED"))
            assertEquals(3, rows(probe, "attempts").length())
            val replacementAttemptId = attempts.start(0) // same explicitly declared direct boundary setup, no inference
            call("cancelAttempt", mapOf("attemptId" to queuedId)) // stale cancellation must not cancel the replacement
            assertTrue(attempts.canDeliver(replacementAttemptId))
            drain()
            assertEquals(1, f.events.size)
            assertEquals(3, rows(probe, "attempts").length())
            envelope.put("queued_persistence", JSONObject().put("independent_rows", snapshot(probe)).put("delivered_event_count", f.events.size)
                .put("replacement_attempt_id", replacementAttemptId)
                .put("ordering", "commit terminal; direct AttemptBoundary replacement; stale cancel via production control; drain Handler: committed row survives, stale UI suppressed")
                .put("linked_coverage", "MainActivityBoundaryTest.queuedViewEventsCannotReachReplacementOrNewSubscriber; ActivityInitializationTest.failedInitializationQueuedEventCannotCrossRetryEvenWithSameSubscriber"))
            val sentinel = File(f.internal, "keep.txt").apply { writeText("keep-internal") }
            val externalSentinel = File(f.external, "keep.json").apply { writeText("keep-external") }
            val legacy = listOf("attempt_history.jsonl", "attempt_history.jsonl.migrated").map { File(f.internal, it).apply { writeText("synthetic residue") } }
            val blocked = File(internal.parentFile, "kumpas_export_blocked_20261016.json").apply { check(mkdir()) }
            val blockedSentinel = File(blocked, "keep").apply { writeText("not traversed") }
            stage = "partial-purge-failure"
            call("clearAllData", error = "CLEAR_FAILED")
            assertFalse(external.exists())
            assertTrue(legacy.none { it.exists() })
            assertEquals("not traversed", blockedSentinel.readText())
            assertEquals(3, rows(probe, "attempts").length())
            envelope.put("partial_clear", JSONObject().put("external_export_exists", external.exists()).put("internal_export_exists", internal.exists())
                .put("legacy_exists", JSONArray(legacy.map { it.exists() })).put("independent_rows", snapshot(probe)).put("error_code", "CLEAR_FAILED"))
            check(blockedSentinel.delete()); check(blocked.delete()) // remove only synthetic fault, then actual purge retry
            stage = "clear-retry"
            call("clearAllData")
            val replacement = call("getParticipantId") as String
            assertNotEquals(participant, replacement)
            assertEquals("[]", call("getHistory"))
            assertEquals("[]", call("getAssessments"))
            assertNull(call("getActiveSession"))
            assertFalse(external.exists()); assertFalse(internal.exists()); assertTrue(legacy.none { it.exists() })
            assertEquals("keep-internal", sentinel.readText()); assertEquals("keep-external", externalSentinel.readText())
            val cleared = snapshot(probe)
            assertEquals(1, cleared.getJSONArray("participants").length())
            for (table in listOf("attempts", "sessions", "assessments")) assertEquals(0, cleared.getJSONArray(table).length())
            envelope.put("clear", JSONObject().put("old_participant_id", participant).put("participant_id", replacement).put("independent_rows", cleared)
                .put("both_export_roots_purged", true).put("legacy_purged", true).put("unrelated_sentinels_survived", true))
            f.closeOwners()
            assertTrue(f.opened.none { it.isOpen })
            f.reloadPreferences()
            val reopenedOwner = MainActivity.Initialization()
            f.activity.initializeResources(f.factory, reopenedOwner) {}
            control = f.activity.controlHandler(reopenedOwner)
            stage = "reopened"
            assertEquals(replacement, call("getParticipantId"))
            assertEquals("[]", call("getHistory")); assertEquals("[]", call("getAssessments"))
            val reopenedProbe = f.database()
            val reopened = snapshot(reopenedProbe)
            assertEquals(1, reopened.getJSONArray("participants").length())
            val emptyExport = File(call("exportData") as String).readBytes()
            assertEquals(0, JSONObject(emptyExport.toString(Charsets.UTF_8)).getJSONObject("summary").getInt("total_attempts"))
            assertEquals(0, JSONObject(emptyExport.toString(Charsets.UTF_8)).getJSONArray("sessions").length())
            assertEquals(0, JSONObject(emptyExport.toString(Charsets.UTF_8)).getJSONArray("assessments").length())
            run.write("reopened-export.json", emptyExport, "export", "study")
            envelope.put("reopen", JSONObject().put("participant_id", replacement).put("independent_rows", reopened))
            envelope.put("control_calls", calls).put("delivered_events", JSONArray(f.events))
        }
        run.write("study.json", envelope.toString(2).toByteArray(), "study", "study")
        return JSONObject().put("scenario_id", envelope.getString("scenario_id")).put("outcome", "passed").put("primary_result_count", 1)
    }

    private fun benchmarks(run: HostArtifactRun): JSONArray {
        val index = JSONArray()
        for (mode in listOf("confirmed", "unconfirmed", "faulted")) HostStudyFixture().use { f ->
            val apk = File(f.internal, "synthetic.apk").apply { writeText("synthetic APK bytes") }
            val context = object : android.content.ContextWrapper(f.context) {
                override fun getApplicationContext(): android.content.Context = this
                override fun getApplicationInfo() = android.content.pm.ApplicationInfo(f.context.applicationInfo).apply { sourceDir = apk.absolutePath; splitSourceDirs = null }
            }
            val setup = JSONObject().put("setup_id", UUID.randomUUID().toString()).put("condition", "optimal").put("lux", 400)
                .put("background", "plain").put("distance_cm", 75).put("device_fingerprint", android.os.Build.FINGERPRINT)
                .put("chip", "Snapdragon 680").put("ram_gb", 4).put("setup_verified", true).put("device_verified", true)
                .put("front_camera_verified", true).put("apk_sha256", HostArtifactRun.sha(apk.readBytes())).put("revision", "b".repeat(40)).put("thermal_state", "nominal")
            File(f.internal, "benchmarks/next_setup.json").apply { parentFile!!.mkdirs(); writeText(setup.toString()) }
            val benchmark = BenchmarkMode(context)
            try {
                benchmark.recordCamera("default_front", "front", true, "synthetic-front")
                val id = benchmark.start(60)
                val companion = File(f.internal, "benchmarks/$id.control.json")
                repeat(60) { second ->
                    repeat(30) { benchmark.recordAnalyzer() }
                    if (second == 1) {
                        val ns = SystemClock.elapsedRealtimeNanos()
                        val attemptId = UUID.randomUUID().toString()
                        benchmark.recordAttemptStart(attemptId, ns)
                        shadowOf(Looper.getMainLooper()).idleFor(Duration.ofMillis(100))
                        benchmark.recordTrace(PipelineTrace(attemptId, ns, ns + 50_000_000, ns + 75_000_000, 1_000_000, ns).toJson().put("event_delivery_ns", ns + 100_000_000))
                        benchmark.recordOutcome(attemptId, "success")
                        shadowOf(Looper.getMainLooper()).idleFor(Duration.ofMillis(900))
                    } else if (second == 29) {
                        shadowOf(Looper.getMainLooper()).idleFor(Duration.ofMillis(999))
                        if (mode == "faulted") { check(companion.delete()); check(companion.mkdir()); File(companion, "sentinel").writeText("unchanged") }
                        if (mode != "unconfirmed") assertEquals(mode == "confirmed", benchmark.confirmStart(id))
                        shadowOf(Looper.getMainLooper()).idleFor(Duration.ofMillis(1))
                    } else shadowOf(Looper.getMainLooper()).idleFor(Duration.ofSeconds(1))
                }
                val reportFile = File(f.internal, "benchmarks/$id.json")
                val bytes = reportFile.readBytes() // exact immutable native publication; never reconstructed
                val report = JSONObject(bytes.toString(Charsets.UTF_8))
                assertEquals(id, report.getString("run_id"))
                assertTrue(report.getBoolean("complete"))
                assertEquals(1800, report.getInt("analyzer_count"))
                assertEquals(if (mode == "confirmed") "confirmed" else "unconfirmed", report.getString("control_status"))
                val companionBytes = if (companion.isFile) companion.readBytes() else null
                if (mode == "faulted") { assertNull(companionBytes); assertEquals("unchanged", File(companion, "sentinel").readText()) }
                else { assertNotNull(companionBytes); assertEquals(id, JSONObject(companionBytes!!.toString(Charsets.UTF_8)).getString("run_id")) }
                val replacement = benchmark.start(60)
                assertNotEquals(id, replacement)
                assertFalse(benchmark.confirmStart(id))
                assertArrayEquals(bytes, reportFile.readBytes())
                if (companionBytes != null) assertArrayEquals(companionBytes, companion.readBytes())
                run.write("$mode-report.json", bytes, "benchmark_report", mode)
                if (companionBytes != null) run.write("$mode-control.json", companionBytes, "benchmark_control", mode)
                index.put(JSONObject().put("mode", mode).put("run_id", id).put("report", "$mode-report.json")
                    .put("control", if (companionBytes != null) "$mode-control.json" else JSONObject.NULL)
                    .put("control_observation", if (companionBytes == null) "publication fault: companion path is nonempty directory, no companion bytes" else "native exact bytes")
                    .put("setup_input", setup).put("synthetic_origin", true).put("not_physical_measurement", true))
            } finally { if (benchmark.isActive) benchmark.finish() }
        }
        run.write("benchmark-index.json", index.toString(2).toByteArray(), "benchmark_index", "study")
        return index
    }
}
