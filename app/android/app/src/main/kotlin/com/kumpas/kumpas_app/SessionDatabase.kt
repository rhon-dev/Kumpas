package com.kumpas.kumpas_app

import android.content.ContentValues
import android.content.Context
import android.database.Cursor
import android.database.sqlite.SQLiteDatabase
import android.database.sqlite.SQLiteOpenHelper
import org.json.JSONArray
import org.json.JSONObject

/**
 * SQLite database for structured session logging (Phase 8).
 *
 * Replaces the append-only JSONL file with a relational schema that
 * supports sessions, attempts, and pre/post assessments. All data
 * stays local — no network calls, consistent with PRD offline-first.
 *
 * Schema version 1:
 *   participants — one row per device install (UUID)
 *   sessions     — bounded practice periods with summaries
 *   attempts     — individual gesture recognition results
 *   assessments  — pre/post study questionnaire responses
 */
class SessionDatabase(context: Context) :
    SQLiteOpenHelper(context, DB_NAME, null, DB_VERSION) {

    companion object {
        const val DB_NAME = "kumpas_sessions.db"
        const val DB_VERSION = 1

        // Table names
        const val T_PARTICIPANTS = "participants"
        const val T_SESSIONS = "sessions"
        const val T_ATTEMPTS = "attempts"
        const val T_ASSESSMENTS = "assessments"
    }

    override fun onCreate(db: SQLiteDatabase) {
        db.execSQL("""
            CREATE TABLE $T_PARTICIPANTS (
                id TEXT PRIMARY KEY,
                created_at INTEGER NOT NULL,
                device_model TEXT,
                app_version TEXT
            )
        """.trimIndent())

        db.execSQL("""
            CREATE TABLE $T_SESSIONS (
                id TEXT PRIMARY KEY,
                participant_id TEXT NOT NULL REFERENCES $T_PARTICIPANTS(id),
                started_at INTEGER NOT NULL,
                ended_at INTEGER,
                attempt_count INTEGER DEFAULT 0,
                signs_attempted INTEGER DEFAULT 0,
                avg_match REAL DEFAULT 0,
                duration_s REAL DEFAULT 0,
                source TEXT DEFAULT 'app'
            )
        """.trimIndent())

        db.execSQL("""
            CREATE TABLE $T_ATTEMPTS (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL REFERENCES $T_SESSIONS(id),
                timestamp INTEGER NOT NULL,
                target_class INTEGER NOT NULL,
                target_label TEXT NOT NULL,
                predicted_label TEXT NOT NULL,
                predicted_confidence REAL NOT NULL,
                recognized_as_target INTEGER NOT NULL,
                overall_match REAL NOT NULL,
                feedback_items TEXT NOT NULL
            )
        """.trimIndent())

        db.execSQL("""
            CREATE TABLE $T_ASSESSMENTS (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                participant_id TEXT NOT NULL REFERENCES $T_PARTICIPANTS(id),
                type TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                responses TEXT NOT NULL
            )
        """.trimIndent())

        // Indexes for fast queries
        db.execSQL("CREATE INDEX idx_attempts_session ON $T_ATTEMPTS(session_id)")
        db.execSQL("CREATE INDEX idx_attempts_timestamp ON $T_ATTEMPTS(timestamp)")
        db.execSQL("CREATE INDEX idx_sessions_participant ON $T_SESSIONS(participant_id)")
    }

    override fun onUpgrade(db: SQLiteDatabase, oldVersion: Int, newVersion: Int) {
        // Future migrations go here (version 2+)
    }

    // ─── Participants ───────────────────────────────────────────────

    fun insertParticipant(id: String, deviceModel: String, appVersion: String) {
        val cv = ContentValues().apply {
            put("id", id)
            put("created_at", System.currentTimeMillis())
            put("device_model", deviceModel)
            put("app_version", appVersion)
        }
        writableDatabase.insertWithOnConflict(
            T_PARTICIPANTS, null, cv, SQLiteDatabase.CONFLICT_IGNORE
        )
    }

    fun getParticipant(): JSONObject? {
        val cursor = readableDatabase.query(
            T_PARTICIPANTS, null, null, null, null, null, null, "1"
        )
        return cursor.use {
            if (it.moveToFirst()) cursorToJson(it) else null
        }
    }

    // ─── Sessions ───────────────────────────────────────────────────

    fun insertSession(id: String, participantId: String): Long {
        val cv = ContentValues().apply {
            put("id", id)
            put("participant_id", participantId)
            put("started_at", System.currentTimeMillis())
            put("source", "app")
        }
        return writableDatabase.insert(T_SESSIONS, null, cv)
    }

    fun closeSession(sessionId: String) {
        // Compute summaries from attempts
        val cursor = readableDatabase.rawQuery("""
            SELECT COUNT(*) as cnt, 
                   COUNT(DISTINCT target_class) as signs,
                   AVG(overall_match) as avg_match
            FROM $T_ATTEMPTS WHERE session_id = ?
        """.trimIndent(), arrayOf(sessionId))

        var count = 0; var signs = 0; var avgMatch = 0.0
        cursor.use {
            if (it.moveToFirst()) {
                count = it.getInt(0)
                signs = it.getInt(1)
                avgMatch = it.getDouble(2)
            }
        }

        // Get session start time for duration calc
        val sessCursor = readableDatabase.query(
            T_SESSIONS, arrayOf("started_at"), "id = ?", arrayOf(sessionId),
            null, null, null
        )
        var startedAt = 0L
        sessCursor.use { if (it.moveToFirst()) startedAt = it.getLong(0) }

        val now = System.currentTimeMillis()
        val durationS = (now - startedAt) / 1000.0

        val cv = ContentValues().apply {
            put("ended_at", now)
            put("attempt_count", count)
            put("signs_attempted", signs)
            put("avg_match", avgMatch)
            put("duration_s", durationS)
        }
        writableDatabase.update(T_SESSIONS, cv, "id = ?", arrayOf(sessionId))
    }

    fun getActiveSession(participantId: String): String? {
        val cursor = readableDatabase.query(
            T_SESSIONS, arrayOf("id"),
            "participant_id = ? AND ended_at IS NULL", arrayOf(participantId),
            null, null, "started_at DESC", "1"
        )
        return cursor.use {
            if (it.moveToFirst()) it.getString(0) else null
        }
    }

    fun getAllSessions(participantId: String): JSONArray {
        val cursor = readableDatabase.query(
            T_SESSIONS, null,
            "participant_id = ?", arrayOf(participantId),
            null, null, "started_at DESC"
        )
        return cursorToJsonArray(cursor)
    }

    // ─── Attempts ───────────────────────────────────────────────────

    fun insertAttempt(
        sessionId: String,
        timestamp: Long,
        targetClass: Int,
        targetLabel: String,
        predictedLabel: String,
        predictedConfidence: Double,
        recognizedAsTarget: Boolean,
        overallMatch: Double,
        feedbackItems: String
    ): Long {
        val cv = ContentValues().apply {
            put("session_id", sessionId)
            put("timestamp", timestamp)
            put("target_class", targetClass)
            put("target_label", targetLabel)
            put("predicted_label", predictedLabel)
            put("predicted_confidence", predictedConfidence)
            put("recognized_as_target", if (recognizedAsTarget) 1 else 0)
            put("overall_match", overallMatch)
            put("feedback_items", feedbackItems)
        }
        return writableDatabase.insert(T_ATTEMPTS, null, cv)
    }

    fun getAttempts(sessionId: String): JSONArray {
        val cursor = readableDatabase.query(
            T_ATTEMPTS, null,
            "session_id = ?", arrayOf(sessionId),
            null, null, "timestamp ASC"
        )
        return cursorToJsonArray(cursor)
    }

    /**
     * Get recent attempts across all sessions (backward-compatible with
     * the old SessionLog.historyJson behavior).
     */
    fun getRecentAttempts(limit: Int = 200): JSONArray {
        val cursor = readableDatabase.query(
            T_ATTEMPTS, null, null, null, null, null,
            "timestamp DESC", limit.toString()
        )
        return cursorToJsonArray(cursor)
    }

    // ─── Assessments ────────────────────────────────────────────────

    fun insertAssessment(participantId: String, type: String, responses: String): Long {
        val cv = ContentValues().apply {
            put("participant_id", participantId)
            put("type", type)
            put("timestamp", System.currentTimeMillis())
            put("responses", responses)
        }
        return writableDatabase.insert(T_ASSESSMENTS, null, cv)
    }

    fun getAssessments(participantId: String): JSONArray {
        val cursor = readableDatabase.query(
            T_ASSESSMENTS, null,
            "participant_id = ?", arrayOf(participantId),
            null, null, "timestamp ASC"
        )
        return cursorToJsonArray(cursor)
    }

    // ─── Bulk Operations ────────────────────────────────────────────

    fun clearAll() {
        val db = writableDatabase
        db.delete(T_ATTEMPTS, null, null)
        db.delete(T_ASSESSMENTS, null, null)
        db.delete(T_SESSIONS, null, null)
        db.delete(T_PARTICIPANTS, null, null)
    }

    fun getAttemptCount(): Int {
        val cursor = readableDatabase.rawQuery(
            "SELECT COUNT(*) FROM $T_ATTEMPTS", null
        )
        return cursor.use { if (it.moveToFirst()) it.getInt(0) else 0 }
    }

    // ─── Utility ────────────────────────────────────────────────────

    private fun cursorToJson(cursor: Cursor): JSONObject {
        val obj = JSONObject()
        for (i in 0 until cursor.columnCount) {
            val name = cursor.getColumnName(i)
            when (cursor.getType(i)) {
                Cursor.FIELD_TYPE_NULL -> obj.put(name, JSONObject.NULL)
                Cursor.FIELD_TYPE_INTEGER -> obj.put(name, cursor.getLong(i))
                Cursor.FIELD_TYPE_FLOAT -> obj.put(name, cursor.getDouble(i))
                Cursor.FIELD_TYPE_STRING -> obj.put(name, cursor.getString(i))
                else -> obj.put(name, cursor.getString(i))
            }
        }
        return obj
    }

    private fun cursorToJsonArray(cursor: Cursor): JSONArray {
        val arr = JSONArray()
        cursor.use {
            while (it.moveToNext()) {
                arr.put(cursorToJson(it))
            }
        }
        return arr
    }
}
