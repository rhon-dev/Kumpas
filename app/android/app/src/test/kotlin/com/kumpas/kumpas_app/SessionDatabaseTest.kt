package com.kumpas.kumpas_app

import android.content.Context
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.RuntimeEnvironment
import org.robolectric.annotation.Config

/**
 * Unit tests for [SessionDatabase] — schema creation and CRUD operations
 * against a real (Robolectric-backed) SQLite instance.
 *
 * Pinned to SDK 34: Robolectric 4.12.1 ships no runtime for the project's
 * targetSdk (36). Nothing under test is SDK-specific — it is plain SQLite.
 *
 * Phase 8, Task 14.
 */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class SessionDatabaseTest {

    private lateinit var context: Context
    private lateinit var db: SessionDatabase

    private val participantId = "test-participant-1"

    @Before
    fun setUp() {
        context = RuntimeEnvironment.getApplication()
        db = SessionDatabase(context)
        db.insertParticipant(participantId, "test-device", "1.0.0")
    }

    @After
    fun tearDown() {
        db.close()
    }

    /** Count rows in a table. */
    private fun rowCount(table: String): Int {
        val cursor = db.readableDatabase.rawQuery("SELECT COUNT(*) FROM $table", null)
        cursor.use {
            it.moveToFirst()
            return it.getInt(0)
        }
    }

    @Test
    fun onCreate_createsAllTablesAndIndexes() {
        val cursor = db.readableDatabase.rawQuery(
            "SELECT name, type FROM sqlite_master WHERE type IN ('table','index')", null
        )
        val names = mutableSetOf<String>()
        cursor.use {
            while (it.moveToNext()) names.add(it.getString(0))
        }

        assertTrue("participants table missing", names.contains(SessionDatabase.T_PARTICIPANTS))
        assertTrue("sessions table missing", names.contains(SessionDatabase.T_SESSIONS))
        assertTrue("attempts table missing", names.contains(SessionDatabase.T_ATTEMPTS))
        assertTrue("assessments table missing", names.contains(SessionDatabase.T_ASSESSMENTS))
        assertTrue("attempts session index missing", names.contains("idx_attempts_session"))
        assertTrue("attempts timestamp index missing", names.contains("idx_attempts_timestamp"))
        assertTrue("sessions participant index missing", names.contains("idx_sessions_participant"))
    }

    @Test
    fun insertParticipant_isIdempotent() {
        // setUp already inserted once; a second insert with the same id must be ignored
        db.insertParticipant(participantId, "other-device", "2.0.0")
        assertEquals(1, rowCount(SessionDatabase.T_PARTICIPANTS))

        val participant = db.getParticipant()
        assertNotNull("participant row should exist", participant)
        assertEquals(participantId, participant!!.getString("id"))
    }

    @Test
    fun insertSession_persistsRowAndIsActive() {
        val sessionId = "session-1"
        db.insertSession(sessionId, participantId)

        assertEquals(1, rowCount(SessionDatabase.T_SESSIONS))
        // ended_at is NULL until closeSession, so it reads back as the active session
        assertEquals(sessionId, db.getActiveSession(participantId))
    }

    @Test
    fun closeSession_computesSummaries() {
        val sessionId = "session-1"
        db.insertSession(sessionId, participantId)

        val now = System.currentTimeMillis()
        // Two attempts on the same sign, one on a different sign -> 2 distinct signs
        db.insertAttempt(sessionId, now, 1, "AKO", "AKO", 0.9, true, 0.8, "[]")
        db.insertAttempt(sessionId, now + 10, 1, "AKO", "IKAW", 0.5, false, 0.4, "[]")
        db.insertAttempt(sessionId, now + 20, 2, "IKAW", "IKAW", 0.9, true, 0.6, "[]")

        db.closeSession(sessionId)

        val cursor = db.readableDatabase.query(
            SessionDatabase.T_SESSIONS,
            arrayOf("ended_at", "attempt_count", "signs_attempted", "avg_match"),
            "id = ?", arrayOf(sessionId), null, null, null
        )
        cursor.use {
            assertTrue("closed session row missing", it.moveToFirst())
            assertTrue("ended_at should be set", it.getLong(0) > 0)
            assertEquals(3, it.getInt(1))
            assertEquals(2, it.getInt(2))
            assertEquals(0.6, it.getDouble(3), 0.0001)
        }

        // A closed session is no longer the active one
        assertNull("closed session must not be active", db.getActiveSession(participantId))
    }

    @Test
    fun insertAttempt_linksToSessionAndRoundTrips() {
        val sessionId = "session-1"
        db.insertSession(sessionId, participantId)

        val now = System.currentTimeMillis()
        val items = """[{"dimension":"handshape","severity":0.4,"hand":"right","prompt":"tip"}]"""
        db.insertAttempt(sessionId, now, 7, "SALAMAT", "PASENSYA", 0.42, false, 0.55, items)

        val attempts = db.getAttempts(sessionId)
        assertEquals(1, attempts.length())

        val row = attempts.getJSONObject(0)
        assertEquals(sessionId, row.getString("session_id"))
        assertEquals(7, row.getInt("target_class"))
        assertEquals("SALAMAT", row.getString("target_label"))
        assertEquals("PASENSYA", row.getString("predicted_label"))
        assertEquals(0.42, row.getDouble("predicted_confidence"), 0.0001)
        assertEquals(0, row.getInt("recognized_as_target"))
        assertEquals(0.55, row.getDouble("overall_match"), 0.0001)
        assertEquals(items, row.getString("feedback_items"))
    }

    @Test
    fun getRecentAttempts_isNewestFirstAndRespectsLimit() {
        val sessionId = "session-1"
        db.insertSession(sessionId, participantId)

        val base = System.currentTimeMillis()
        db.insertAttempt(sessionId, base, 1, "OLDEST", "OLDEST", 0.9, true, 0.9, "[]")
        db.insertAttempt(sessionId, base + 100, 2, "MIDDLE", "MIDDLE", 0.9, true, 0.9, "[]")
        db.insertAttempt(sessionId, base + 200, 3, "NEWEST", "NEWEST", 0.9, true, 0.9, "[]")

        val all = db.getRecentAttempts(200)
        assertEquals(3, all.length())
        assertEquals("NEWEST", all.getJSONObject(0).getString("target_label"))
        assertEquals("OLDEST", all.getJSONObject(2).getString("target_label"))

        val limited = db.getRecentAttempts(2)
        assertEquals(2, limited.length())
        assertEquals("NEWEST", limited.getJSONObject(0).getString("target_label"))
    }

    @Test
    fun insertAssessment_storesResponsesPerType() {
        db.insertAssessment(participantId, "pre", """{"fslConfidence":2}""")
        db.insertAssessment(participantId, "post", """{"fslConfidence":4}""")

        val assessments = db.getAssessments(participantId)
        assertEquals(2, assessments.length())
        // ordered by timestamp ASC, so pre comes first
        assertEquals("pre", assessments.getJSONObject(0).getString("type"))
        assertEquals("""{"fslConfidence":2}""", assessments.getJSONObject(0).getString("responses"))
        assertEquals("post", assessments.getJSONObject(1).getString("type"))
    }

    @Test
    fun getAssessments_isScopedToParticipant() {
        db.insertParticipant("other-participant", "test-device", "1.0.0")
        db.insertAssessment(participantId, "pre", "{}")
        db.insertAssessment("other-participant", "pre", "{}")

        assertEquals(1, db.getAssessments(participantId).length())
        assertEquals(1, db.getAssessments("other-participant").length())
    }

    @Test
    fun getAllSessions_isScopedToParticipant() {
        db.insertParticipant("other-participant", "test-device", "1.0.0")
        db.insertSession("session-1", participantId)
        db.insertSession("session-2", participantId)
        db.insertSession("session-3", "other-participant")

        assertEquals(2, db.getAllSessions(participantId).length())
        assertEquals(1, db.getAllSessions("other-participant").length())
    }

    @Test
    fun clearAll_emptiesEveryTable() {
        val sessionId = "session-1"
        db.insertSession(sessionId, participantId)
        db.insertAttempt(sessionId, System.currentTimeMillis(), 1, "AKO", "AKO", 0.9, true, 0.9, "[]")
        db.insertAssessment(participantId, "pre", "{}")

        assertEquals(1, db.getAttemptCount())

        db.clearAll()

        assertEquals(0, rowCount(SessionDatabase.T_ATTEMPTS))
        assertEquals(0, rowCount(SessionDatabase.T_SESSIONS))
        assertEquals(0, rowCount(SessionDatabase.T_ASSESSMENTS))
        assertEquals(0, rowCount(SessionDatabase.T_PARTICIPANTS))
        assertEquals(0, db.getAttemptCount())
    }
}
