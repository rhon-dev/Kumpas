package com.kumpas.kumpas_app

import android.content.Context
import org.json.JSONObject
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.RuntimeEnvironment
import org.robolectric.annotation.Config
import java.io.File

/**
 * Unit tests for [DataExporter] — asserts the export file is valid JSON with
 * the structure documented in design.md, and that it is *complete*: every
 * session, attempt and assessment for the participant appears in the output.
 *
 * Covers design.md "Property 4: Export Completeness".
 *
 * Pinned to SDK 34: Robolectric 4.12.1 ships no runtime for targetSdk 36.
 *
 * Phase 8, Task 16 (export verification).
 */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class DataExporterTest {

    private lateinit var context: Context
    private lateinit var db: SessionDatabase
    private lateinit var exporter: DataExporter

    private val participantId = "11111111-2222-3333-4444-555555555555"

    @Before
    fun setUp() {
        context = RuntimeEnvironment.getApplication()
        db = SessionDatabase(context)
        exporter = DataExporter(context)
        db.insertParticipant(participantId, "test-device", "1.0.0")
    }

    @After
    fun tearDown() {
        db.close()
    }

    /** Export and parse the resulting file back into JSON. */
    private fun exportAndParse(): Pair<File, JSONObject> {
        val path = exporter.export(participantId, db)
        val file = File(path)
        assertTrue("export file should exist at $path", file.exists())
        return file to JSONObject(file.readText())
    }

    private fun seedSession(sessionId: String, vararg labels: String) {
        db.insertSession(sessionId, participantId)
        var ts = System.currentTimeMillis()
        labels.forEachIndexed { index, label ->
            db.insertAttempt(
                sessionId, ts++, index + 1, label, label,
                0.9, true, 0.8, "[]"
            )
        }
        db.closeSession(sessionId)
    }

    @Test
    fun export_writesParsableJsonWithTopLevelSections() {
        val (_, root) = exportAndParse()

        assertTrue("missing metadata", root.has("metadata"))
        assertTrue("missing assessments", root.has("assessments"))
        assertTrue("missing sessions", root.has("sessions"))
        assertTrue("missing summary", root.has("summary"))
    }

    @Test
    fun export_metadataIdentifiesParticipantAndDevice() {
        val (_, root) = exportAndParse()
        val metadata = root.getJSONObject("metadata")

        assertEquals(participantId, metadata.getString("participant_id"))
        assertNotNull(metadata.getString("export_timestamp"))
        assertNotNull(metadata.getString("app_version"))
        assertNotNull(metadata.getString("device_model"))
        assertNotNull(metadata.getString("android_version"))
        // ISO-8601-ish: 2026-07-27T18:37:53
        assertTrue(
            "unexpected timestamp format: ${metadata.getString("export_timestamp")}",
            Regex("^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}$")
                .matches(metadata.getString("export_timestamp"))
        )
    }

    @Test
    fun export_isEmptyButValidWhenNoDataRecorded() {
        val (_, root) = exportAndParse()

        assertEquals(0, root.getJSONArray("sessions").length())
        assertEquals(0, root.getJSONArray("assessments").length())
        assertEquals(0, root.getJSONObject("summary").getInt("total_sessions"))
        assertEquals(0, root.getJSONObject("summary").getInt("total_attempts"))
        assertEquals(0, root.getJSONObject("summary").getInt("total_assessments"))
    }

    @Test
    fun export_nestsAttemptsUnderTheirSession() {
        seedSession("session-1", "AKO", "IKAW")
        seedSession("session-2", "SALAMAT")

        val (_, root) = exportAndParse()
        val sessions = root.getJSONArray("sessions")
        assertEquals(2, sessions.length())

        // Map session id -> nested attempt labels
        val byId = mutableMapOf<String, List<String>>()
        for (i in 0 until sessions.length()) {
            val session = sessions.getJSONObject(i)
            val attempts = session.getJSONArray("attempts")
            byId[session.getString("id")] = (0 until attempts.length()).map {
                attempts.getJSONObject(it).getString("target_label")
            }
        }

        assertEquals(listOf("AKO", "IKAW"), byId["session-1"])
        assertEquals(listOf("SALAMAT"), byId["session-2"])
    }

    @Test
    fun export_containsEverySessionAttemptAndAssessment() {
        seedSession("session-1", "AKO", "IKAW")
        seedSession("session-2", "SALAMAT")
        db.insertAssessment(participantId, "pre", """{"fslConfidence":2}""")
        db.insertAssessment(participantId, "post", """{"fslConfidence":5}""")

        val (_, root) = exportAndParse()

        // Every session is present
        assertEquals(2, root.getJSONArray("sessions").length())

        // Every attempt is present, counted across nested arrays
        var nestedAttempts = 0
        val sessions = root.getJSONArray("sessions")
        for (i in 0 until sessions.length()) {
            nestedAttempts += sessions.getJSONObject(i).getJSONArray("attempts").length()
        }
        assertEquals("all attempts must appear in the export", 3, nestedAttempts)

        // Every assessment is present
        assertEquals(2, root.getJSONArray("assessments").length())

        // Summary agrees with the payload
        val summary = root.getJSONObject("summary")
        assertEquals(2, summary.getInt("total_sessions"))
        assertEquals(3, summary.getInt("total_attempts"))
        assertEquals(2, summary.getInt("total_assessments"))
    }

    @Test
    fun export_preservesSessionSummaryFields() {
        seedSession("session-1", "AKO", "IKAW")

        val (_, root) = exportAndParse()
        val session = root.getJSONArray("sessions").getJSONObject(0)

        assertEquals(participantId, session.getString("participant_id"))
        assertEquals(2, session.getInt("attempt_count"))
        assertEquals(2, session.getInt("signs_attempted"))
        assertEquals("app", session.getString("source"))
        assertTrue("started_at should be set", session.getLong("started_at") > 0)
        assertTrue("ended_at should be set", session.getLong("ended_at") > 0)
    }

    @Test
    fun export_excludesOtherParticipantsData() {
        val other = "99999999-8888-7777-6666-555555555555"
        db.insertParticipant(other, "test-device", "1.0.0")
        db.insertSession("other-session", other)
        db.insertAssessment(other, "pre", "{}")

        seedSession("session-1", "AKO")
        db.insertAssessment(participantId, "pre", "{}")

        val (_, root) = exportAndParse()

        assertEquals(1, root.getJSONArray("sessions").length())
        assertEquals("session-1", root.getJSONArray("sessions").getJSONObject(0).getString("id"))
        assertEquals(1, root.getJSONArray("assessments").length())
    }

    @Test
    fun export_fileNameCarriesParticipantPrefix() {
        val (file, _) = exportAndParse()

        assertTrue(
            "unexpected export file name: ${file.name}",
            Regex("^kumpas_export_${participantId.take(8)}_\\d{8}_\\d{6}\\.json$")
                .matches(file.name)
        )
    }

    @Test
    fun export_afterClearAllProducesEmptyPayload() {
        seedSession("session-1", "AKO")
        db.insertAssessment(participantId, "pre", "{}")

        db.clearAll()
        // A cleared database has no participant rows; export must still succeed
        val (_, root) = exportAndParse()

        assertEquals(0, root.getJSONArray("sessions").length())
        assertEquals(0, root.getJSONArray("assessments").length())
        assertEquals(0, root.getJSONObject("summary").getInt("total_attempts"))
    }
}
