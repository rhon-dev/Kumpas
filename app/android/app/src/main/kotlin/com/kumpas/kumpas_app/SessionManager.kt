package com.kumpas.kumpas_app

import android.content.Context
import android.content.SharedPreferences
import android.os.Build
import android.os.Handler
import android.os.Looper
import android.util.Log
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.util.UUID

/**
 * Manages session lifecycle for the Kumpas practice app (Phase 8).
 *
 * Responsibilities:
 * - Generate/persist a participant UUID (one per device install)
 * - Start/end practice sessions with auto-timeout on app background
 * - Route attempt results into the SQLite database
 * - Migrate legacy JSONL data on first use
 *
 * Session auto-close: when the app goes to background, a 60-second timer
 * starts. If the app resumes before timeout, the session stays active.
 * If the timer fires, the session is closed.
 */
class SessionManager(private val context: Context) {

    companion object {
        private const val TAG = "KumpasSession"
        private const val PREFS_NAME = "kumpas_session_prefs"
        private const val KEY_PARTICIPANT_ID = "participant_id"
        private const val KEY_MIGRATED = "jsonl_migrated"
        private const val AUTO_CLOSE_DELAY_MS = 60_000L
    }

    private val db = SessionDatabase(context)
    private val prefs: SharedPreferences =
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    private val handler = Handler(Looper.getMainLooper())

    private var activeSessionId: String? = null
    private var autoCloseRunnable: Runnable? = null

    val participantId: String
        get() = getOrCreateParticipantId()

    init {
        ensureParticipant()
        migrateIfNeeded()
        // Recover any unclosed session from a crash
        activeSessionId = db.getActiveSession(participantId)
    }

    // ─── Participant ────────────────────────────────────────────────

    private fun getOrCreateParticipantId(): String {
        var id = prefs.getString(KEY_PARTICIPANT_ID, null)
        if (id == null) {
            id = UUID.randomUUID().toString()
            prefs.edit().putString(KEY_PARTICIPANT_ID, id).apply()
        }
        return id
    }

    private fun ensureParticipant() {
        val id = participantId
        val deviceModel = "${Build.MANUFACTURER} ${Build.MODEL}"
        val appVersion = try {
            context.packageManager.getPackageInfo(context.packageName, 0).versionName ?: "1.0.0"
        } catch (_: Exception) { "1.0.0" }
        db.insertParticipant(id, deviceModel, appVersion)
    }

    // ─── Session Lifecycle ──────────────────────────────────────────

    /**
     * Start a new practice session. Closes any existing active session first.
     * Returns the new session UUID.
     */
    fun startSession(): String {
        // Close existing if open
        activeSessionId?.let { endSession() }

        val sessionId = UUID.randomUUID().toString()
        db.insertSession(sessionId, participantId)
        activeSessionId = sessionId
        cancelAutoClose()
        Log.i(TAG, "Session started: $sessionId")
        return sessionId
    }

    /**
     * End the active session, computing summaries.
     */
    fun endSession() {
        val sid = activeSessionId ?: return
        db.closeSession(sid)
        activeSessionId = null
        cancelAutoClose()
        Log.i(TAG, "Session ended: $sid")
    }

    /**
     * Get the currently active session ID, or null.
     */
    fun getActiveSessionId(): String? = activeSessionId

    /**
     * Called when app goes to background. Starts the 60s auto-close timer.
     */
    fun onPause() {
        if (activeSessionId == null) return
        autoCloseRunnable = Runnable {
            Log.i(TAG, "Auto-closing session after ${AUTO_CLOSE_DELAY_MS / 1000}s background")
            endSession()
        }
        handler.postDelayed(autoCloseRunnable!!, AUTO_CLOSE_DELAY_MS)
    }

    /**
     * Called when app returns to foreground. Cancels auto-close if pending.
     */
    fun onResume() {
        cancelAutoClose()
    }

    private fun cancelAutoClose() {
        autoCloseRunnable?.let { handler.removeCallbacks(it) }
        autoCloseRunnable = null
    }

    // ─── Attempt Recording ──────────────────────────────────────────

    /**
     * Record an attempt result. If no session is active, one is created.
     * Accepts the raw JSON from VisionEngine's attempt_result callback.
     */
    fun recordAttempt(attemptJson: String) {
        // Ensure we have an active session
        if (activeSessionId == null) {
            startSession()
        }

        val obj = JSONObject(attemptJson)
        val timestamp = System.currentTimeMillis()

        db.insertAttempt(
            sessionId = activeSessionId!!,
            timestamp = timestamp,
            targetClass = obj.getInt("targetClass"),
            targetLabel = obj.getString("targetLabel"),
            predictedLabel = obj.getString("predictedLabel"),
            predictedConfidence = obj.getDouble("predictedConfidence"),
            recognizedAsTarget = obj.getBoolean("recognizedAsTarget"),
            overallMatch = obj.getDouble("overallMatch"),
            feedbackItems = obj.getJSONArray("items").toString()
        )
    }

    // ─── Query (backward-compatible with old SessionLog) ────────────

    /**
     * Returns recent attempts as a JSON array string, newest first.
     * Same interface as the old SessionLog.historyJson() for backward compat.
     */
    fun historyJson(limit: Int = 200): String {
        val arr = db.getRecentAttempts(limit)
        // Remap column names to match the old format expected by Flutter
        val result = JSONArray()
        for (i in 0 until arr.length()) {
            val row = arr.getJSONObject(i)
            val mapped = JSONObject().apply {
                put("targetClass", row.getInt("target_class"))
                put("targetLabel", row.getString("target_label"))
                put("predictedLabel", row.getString("predicted_label"))
                put("predictedConfidence", row.getDouble("predicted_confidence"))
                put("recognizedAsTarget", row.getInt("recognized_as_target") == 1)
                put("overallMatch", row.getDouble("overall_match"))
                put("items", JSONArray(row.getString("feedback_items")))
                put("timestamp", row.getLong("timestamp"))
            }
            result.put(mapped)
        }
        return result.toString()
    }

    // ─── Assessments ────────────────────────────────────────────────

    fun saveAssessment(type: String, responses: String) {
        db.insertAssessment(participantId, type, responses)
        Log.i(TAG, "Assessment saved: type=$type")
    }

    fun getAssessments(): String {
        return db.getAssessments(participantId).toString()
    }

    // ─── Data Management ────────────────────────────────────────────

    fun clearAllData() {
        endSession()
        db.clearAll()
        // Generate new participant ID
        val newId = UUID.randomUUID().toString()
        prefs.edit().putString(KEY_PARTICIPANT_ID, newId).apply()
        ensureParticipant()
        Log.i(TAG, "All data cleared, new participant: $newId")
    }

    // ─── JSONL Migration ────────────────────────────────────────────

    private fun migrateIfNeeded() {
        if (prefs.getBoolean(KEY_MIGRATED, false)) return

        val jsonlFile = File(context.filesDir, "attempt_history.jsonl")
        if (!jsonlFile.exists()) {
            prefs.edit().putBoolean(KEY_MIGRATED, true).apply()
            return
        }

        Log.i(TAG, "Migrating attempt_history.jsonl → SQLite")
        val lines = jsonlFile.readLines().filter { it.isNotBlank() }
        if (lines.isEmpty()) {
            prefs.edit().putBoolean(KEY_MIGRATED, true).apply()
            return
        }

        // Create a legacy session to hold all migrated attempts
        val legacySessionId = UUID.randomUUID().toString()
        val wdb = db.writableDatabase
        wdb.beginTransaction()
        try {
            val sessionCv = android.content.ContentValues().apply {
                put("id", legacySessionId)
                put("participant_id", participantId)
                put("started_at", 0L) // will update from first attempt
                put("source", "legacy_migration")
            }
            wdb.insert(SessionDatabase.T_SESSIONS, null, sessionCv)

            var firstTs = Long.MAX_VALUE
            var lastTs = 0L
            var count = 0
            val signs = mutableSetOf<Int>()
            var matchSum = 0.0
            var errors = 0

            for (line in lines) {
                try {
                    val obj = JSONObject(line)
                    val ts = obj.optLong("timestamp", System.currentTimeMillis())
                    val targetClass = obj.optInt("targetClass", -1)
                    val targetLabel = obj.optString("targetLabel", "")
                    val predictedLabel = obj.optString("predictedLabel", "")
                    val confidence = obj.optDouble("predictedConfidence", 0.0)
                    val recognized = obj.optBoolean("recognizedAsTarget", false)
                    val match = obj.optDouble("overallMatch", 0.0)
                    val items = obj.optJSONArray("items")?.toString() ?: "[]"

                    if (targetClass < 0) { errors++; continue }

                    db.insertAttempt(
                        legacySessionId, ts, targetClass, targetLabel,
                        predictedLabel, confidence, recognized, match, items
                    )

                    if (ts < firstTs) firstTs = ts
                    if (ts > lastTs) lastTs = ts
                    signs.add(targetClass)
                    matchSum += match
                    count++
                } catch (e: Exception) {
                    errors++
                    Log.w(TAG, "Migration: skipped line: ${e.message}")
                }
            }

            // Update legacy session summaries
            if (count > 0) {
                val updateCv = android.content.ContentValues().apply {
                    put("started_at", firstTs)
                    put("ended_at", lastTs)
                    put("attempt_count", count)
                    put("signs_attempted", signs.size)
                    put("avg_match", matchSum / count)
                    put("duration_s", (lastTs - firstTs) / 1000.0)
                }
                wdb.update(SessionDatabase.T_SESSIONS, updateCv, "id = ?", arrayOf(legacySessionId))
            }

            wdb.setTransactionSuccessful()
            Log.i(TAG, "Migration complete: $count attempts migrated, $errors errors")
        } finally {
            wdb.endTransaction()
        }

        // Rename original file as backup
        val backup = File(context.filesDir, "attempt_history.jsonl.migrated")
        jsonlFile.renameTo(backup)
        prefs.edit().putBoolean(KEY_MIGRATED, true).apply()
    }
}
