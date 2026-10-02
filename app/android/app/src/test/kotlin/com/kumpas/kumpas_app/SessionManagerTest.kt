package com.kumpas.kumpas_app

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.RuntimeEnvironment
import org.robolectric.Shadows
import org.robolectric.annotation.Config
import java.io.File

/**
 * Unit tests for [SessionManager] — session start/end state machine,
 * background auto-close timer, attempt linkage, and JSONL migration.
 *
 * Pinned to SDK 34: Robolectric 4.12.1 ships no runtime for the project's
 * targetSdk (36). Nothing under test is SDK-specific.
 *
 * Phase 8, Task 15.
 */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class SessionManagerTest {

    /** Keep fixture helpers reachable and close every reopened handle after each test. */
    private class TrackingDatabaseContext(base: Context) : android.content.ContextWrapper(base) {
        private val opened = mutableListOf<android.database.sqlite.SQLiteDatabase>()

        override fun openOrCreateDatabase(name: String, mode: Int, factory: android.database.sqlite.SQLiteDatabase.CursorFactory?): android.database.sqlite.SQLiteDatabase =
            super.openOrCreateDatabase(name, mode, factory).also { opened.add(it) }

        override fun openOrCreateDatabase(name: String, mode: Int, factory: android.database.sqlite.SQLiteDatabase.CursorFactory?, handler: android.database.DatabaseErrorHandler?): android.database.sqlite.SQLiteDatabase =
            super.openOrCreateDatabase(name, mode, factory, handler).also { opened.add(it) }

        fun closeFixtureDatabases() {
            opened.forEach { if (it.isOpen) it.close() }
            opened.clear()
        }
    }

    private lateinit var context: Context
    private lateinit var manager: SessionManager

    /**
     * Independent handle on the same underlying SQLite file, used to assert
     * on persisted rows without reaching into SessionManager's internals.
     */
    private lateinit var probe: SessionDatabase

    private fun attemptJson(
        targetClass: Int = 1,
        targetLabel: String = "AKO",
        predictedLabel: String = "AKO",
        confidence: Double = 0.92,
        recognized: Boolean = true,
        match: Double = 0.85
    ) = """
        {
          "targetClass": $targetClass,
          "targetLabel": "$targetLabel",
          "predictedLabel": "$predictedLabel",
          "predictedConfidence": $confidence,
          "recognizedAsTarget": $recognized,
          "overallMatch": $match,
          "items": []
        }
    """.trimIndent()

    @Before
    fun setUp() {
        context = TrackingDatabaseContext(RuntimeEnvironment.getApplication())
        manager = SessionManager(context)
        probe = SessionDatabase(context)
    }

    @After
    fun tearDown() {
        probe.close()
        (context as TrackingDatabaseContext).closeFixtureDatabases()
    }

    /** Wipe every table via an independent handle on the same SQLite file. */
    private fun resetDatabase() {
        val helper = SessionDatabase(context)
        try {
            helper.clearAll()
        } finally {
            helper.close()
        }
    }

    @Test
    fun ignoredSessionInsertFailsWithoutCachingIdentity() {
        probe.writableDatabase.execSQL("CREATE TRIGGER ignore_session BEFORE INSERT ON sessions BEGIN SELECT RAISE(IGNORE); END")
        org.junit.Assert.assertThrows(android.database.sqlite.SQLiteException::class.java) { manager.startSession() }
        assertNull(manager.getActiveSessionId())
    }

    @Test
    fun ignoredAttemptInsertMustNotSucceed() {
        probe.writableDatabase.execSQL("CREATE TRIGGER ignore_attempt BEFORE INSERT ON attempts BEGIN SELECT RAISE(IGNORE); END")
        org.junit.Assert.assertThrows(android.database.sqlite.SQLiteException::class.java) { manager.recordAttempt(attemptJson()) }
        assertEquals(0, probe.getAttemptCount())
    }

    @Test
    fun ignoredAssessmentInsertMustNotSucceed() {
        probe.writableDatabase.execSQL("CREATE TRIGGER ignore_assessment BEFORE INSERT ON assessments BEGIN SELECT RAISE(IGNORE); END")
        org.junit.Assert.assertThrows(android.database.sqlite.SQLiteException::class.java) { manager.saveAssessment("pre", "{}") }
        assertEquals("[]", manager.getAssessments())
    }

    @Test
    fun ignoredParticipantInsertMustNotSucceed() {
        resetDatabase()
        probe.writableDatabase.execSQL("CREATE TRIGGER ignore_participant BEFORE INSERT ON participants BEGIN SELECT RAISE(IGNORE); END")
        org.junit.Assert.assertThrows(android.database.sqlite.SQLiteException::class.java) { SessionManager(context) }
    }

    @Test
    fun ignoredMigrationInsertRollsBackAndRetainsSourceForRetry() {
        context.getSharedPreferences("kumpas_session_prefs", Context.MODE_PRIVATE).edit().putBoolean("jsonl_migrated", false).commit()
        val source = File(context.filesDir, "attempt_history.jsonl").apply { writeText(JSONObject(attemptJson()).toString()) }
        probe.writableDatabase.execSQL("CREATE TRIGGER ignore_migration BEFORE INSERT ON attempts BEGIN SELECT RAISE(IGNORE); END")
        org.junit.Assert.assertThrows(android.database.sqlite.SQLiteException::class.java) { SessionManager(context) }
        assertTrue(source.exists())
        assertFalse(context.getSharedPreferences("kumpas_session_prefs", Context.MODE_PRIVATE).getBoolean("jsonl_migrated", false))
        probe.readableDatabase.rawQuery("SELECT COUNT(*) FROM sessions", null).use { it.moveToFirst(); assertEquals(0, it.getInt(0)) }
        probe.writableDatabase.execSQL("DROP TRIGGER ignore_migration")
        SessionManager(context)
        assertEquals(1, probe.getAttemptCount())
    }

    @Test
    fun closeCancelsTimerAndClosesOwnedHelperEvenWhenSessionSummaryFails() {
        manager.startSession()
        manager.onPause()
        val owned = SessionManager::class.java.getDeclaredField("db").apply { isAccessible = true }.get(manager) as SessionDatabase
        val database = owned.writableDatabase
        probe.writableDatabase.execSQL("CREATE TRIGGER refuse_summary BEFORE UPDATE ON sessions BEGIN SELECT RAISE(ABORT, 'synthetic'); END")
        val close = SessionManager::class.java.getMethod("close")
        try { close.invoke(manager); org.junit.Assert.fail("summary failure should propagate") }
        catch (e: java.lang.reflect.InvocationTargetException) { assertTrue(e.cause is android.database.sqlite.SQLiteException) }
        assertFalse(database.isOpen)
        close.invoke(manager) // teardown is idempotent
        Shadows.shadowOf(android.os.Looper.getMainLooper()).idleFor(java.time.Duration.ofSeconds(61))
    }

    // ─── Participant ────────────────────────────────────────────────

    @Test
    fun participantId_isAStableUuid() {
        val first = manager.participantId
        val second = manager.participantId

        assertNotNull(first)
        assertTrue("participant id should not be blank", first.isNotBlank())
        assertEquals("participant id must be stable across reads", first, second)
        // UUID.randomUUID() form: 8-4-4-4-12
        assertTrue(
            "participant id should look like a UUID but was '$first'",
            Regex("^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
                .matches(first)
        )
    }

    @Test
    fun participantId_persistsAcrossManagerInstances() {
        val original = manager.participantId

        val reopened = SessionManager(context)

        assertEquals(original, reopened.participantId)
    }

    @Test
    fun init_registersParticipantRowExactlyOnce() {
        // Constructing a second manager must not duplicate the participant
        SessionManager(context)

        val cursor = probe.readableDatabase.rawQuery(
            "SELECT COUNT(*) FROM ${SessionDatabase.T_PARTICIPANTS}", null
        )
        cursor.use {
            it.moveToFirst()
            assertEquals(1, it.getInt(0))
        }
    }

    // ─── Session state machine ──────────────────────────────────────

    @Test
    fun startSession_returnsIdAndMarksItActive() {
        val sessionId = manager.startSession()

        assertNotNull(sessionId)
        assertTrue(sessionId.isNotBlank())
        assertEquals(sessionId, manager.getActiveSessionId())
        assertEquals(
            "session should be active in the database too",
            sessionId,
            probe.getActiveSession(manager.participantId)
        )
    }

    @Test
    fun endSession_clearsActiveSessionAndPersistsSummary() {
        val sessionId = manager.startSession()
        manager.recordAttempt(attemptJson(match = 0.8))
        manager.recordAttempt(attemptJson(targetClass = 2, targetLabel = "IKAW", match = 0.6))

        manager.endSession()

        assertNull(manager.getActiveSessionId())
        assertNull(probe.getActiveSession(manager.participantId))

        val cursor = probe.readableDatabase.query(
            SessionDatabase.T_SESSIONS,
            arrayOf("ended_at", "attempt_count", "signs_attempted", "avg_match"),
            "id = ?", arrayOf(sessionId), null, null, null
        )
        cursor.use {
            assertTrue("session row missing", it.moveToFirst())
            assertTrue("ended_at should be set", it.getLong(0) > 0)
            assertEquals(2, it.getInt(1))
            assertEquals(2, it.getInt(2))
            assertEquals(0.7, it.getDouble(3), 0.0001)
        }
    }

    @Test
    fun endSession_withoutActiveSessionIsANoOp() {
        assertNull(manager.getActiveSessionId())

        manager.endSession()

        assertNull(manager.getActiveSessionId())
    }

    @Test
    fun startSession_twiceClosesThePreviousSession() {
        val first = manager.startSession()
        val second = manager.startSession()

        assertNotEquals(first, second)
        assertEquals(second, manager.getActiveSessionId())

        // The first session must have been closed, not left dangling
        val cursor = probe.readableDatabase.query(
            SessionDatabase.T_SESSIONS, arrayOf("ended_at"),
            "id = ?", arrayOf(first), null, null, null
        )
        cursor.use {
            assertTrue("first session row missing", it.moveToFirst())
            assertFalse("first session should be closed", it.isNull(0))
        }
    }

    @Test
    fun sessionRecoversUnclosedSessionOnRestart() {
        val sessionId = manager.startSession()
        // Simulate a crash: no endSession() call, then a fresh manager
        val recovered = SessionManager(context)

        assertEquals(
            "an unclosed session should be picked back up",
            sessionId,
            recovered.getActiveSessionId()
        )
    }

    // ─── Auto-close timer ───────────────────────────────────────────

    @Test
    fun onPause_autoClosesSessionAfterTimeout() {
        val sessionId = manager.startSession()

        manager.onPause()
        // Still active before the timer fires
        assertEquals(sessionId, manager.getActiveSessionId())

        // Advance the main looper past the 60s auto-close delay
        Shadows.shadowOf(android.os.Looper.getMainLooper()).idleFor(
            java.time.Duration.ofSeconds(61)
        )

        assertNull("session should auto-close after 60s in background",
            manager.getActiveSessionId())
    }

    @Test
    fun onResume_cancelsPendingAutoClose() {
        val sessionId = manager.startSession()

        manager.onPause()
        manager.onResume()

        Shadows.shadowOf(android.os.Looper.getMainLooper()).idleFor(
            java.time.Duration.ofSeconds(61)
        )

        assertEquals("resuming should cancel the auto-close timer",
            sessionId, manager.getActiveSessionId())
    }

    @Test
    fun onPause_withoutActiveSessionSchedulesNothing() {
        assertNull(manager.getActiveSessionId())

        manager.onPause()
        Shadows.shadowOf(android.os.Looper.getMainLooper()).idleFor(
            java.time.Duration.ofSeconds(61)
        )

        assertNull(manager.getActiveSessionId())
    }

    // ─── Attempt recording ──────────────────────────────────────────

    @Test
    fun recordAttempt_linksAttemptToActiveSession() {
        val sessionId = manager.startSession()

        manager.recordAttempt(attemptJson(targetClass = 7, targetLabel = "SALAMAT"))

        val attempts = probe.getAttempts(sessionId)
        assertEquals(1, attempts.length())
        assertEquals(sessionId, attempts.getJSONObject(0).getString("session_id"))
        assertEquals(7, attempts.getJSONObject(0).getInt("target_class"))
        assertEquals("SALAMAT", attempts.getJSONObject(0).getString("target_label"))
    }

    @Test
    fun recordAttempt_startsASessionWhenNoneIsActive() {
        assertNull(manager.getActiveSessionId())

        manager.recordAttempt(attemptJson())

        val sessionId = manager.getActiveSessionId()
        assertNotNull("recordAttempt should open a session implicitly", sessionId)
        assertEquals(1, probe.getAttempts(sessionId!!).length())
    }

    @Test
    fun recordAttempt_preservesFieldsThroughHistoryJson() {
        manager.startSession()
        manager.recordAttempt(
            attemptJson(
                targetClass = 3,
                targetLabel = "PASENSYA",
                predictedLabel = "SALAMAT",
                confidence = 0.41,
                recognized = false,
                match = 0.52
            )
        )

        val history = JSONArray(manager.historyJson())
        assertEquals(1, history.length())

        val row = history.getJSONObject(0)
        assertEquals(3, row.getInt("targetClass"))
        assertEquals("PASENSYA", row.getString("targetLabel"))
        assertEquals("SALAMAT", row.getString("predictedLabel"))
        assertEquals(0.41, row.getDouble("predictedConfidence"), 0.0001)
        assertFalse(row.getBoolean("recognizedAsTarget"))
        assertEquals(0.52, row.getDouble("overallMatch"), 0.0001)
        assertEquals(0, row.getJSONArray("items").length())
        assertTrue("timestamp should be populated", row.getLong("timestamp") > 0)
    }

    @Test
    fun historyJson_spansMultipleSessionsNewestFirst() {
        manager.startSession()
        manager.recordAttempt(attemptJson(targetLabel = "FIRST"))
        manager.endSession()

        manager.startSession()
        manager.recordAttempt(attemptJson(targetLabel = "SECOND"))
        manager.endSession()

        val history = JSONArray(manager.historyJson())
        assertEquals(2, history.length())
        assertEquals("SECOND", history.getJSONObject(0).getString("targetLabel"))
        assertEquals("FIRST", history.getJSONObject(1).getString("targetLabel"))
    }

    // ─── Assessments ────────────────────────────────────────────────

    @Test
    fun saveAssessment_isReadableBackForTheParticipant() {
        manager.saveAssessment("pre", """{"fslConfidence":2}""")
        manager.saveAssessment("post", """{"fslConfidence":5}""")

        val assessments = JSONArray(manager.getAssessments())
        assertEquals(2, assessments.length())
        assertEquals("pre", assessments.getJSONObject(0).getString("type"))
        assertEquals("post", assessments.getJSONObject(1).getString("type"))
    }

    @Test
    fun clearAllData_removesActualExportsAndMigrationResidueAcrossRoots() {
        manager.recordAttempt(attemptJson())
        val externalExport = File(DataExporter(context).export(manager.participantId, probe))
        val fallback = object : android.content.ContextWrapper(context) {
            override fun getExternalFilesDir(type: String?): File? = null
        }
        val internalExport = File(DataExporter(fallback).export("old-participant", probe))
        val legacy = File(context.filesDir, "attempt_history.jsonl").apply { writeText(JSONObject(attemptJson()).toString()) }
        val migrated = File(context.filesDir, "attempt_history.jsonl.migrated").apply { writeText(attemptJson()) }
        val sentinel = File(context.filesDir, "keep.txt").apply { writeText("keep") }
        val externalSentinel = File(externalExport.parentFile, "keep.json").apply { writeText("keep") }
        manager.clearAllData()
        for (file in listOf(externalExport, internalExport, legacy, migrated)) {
            assertFalse("managed residue: ${file.name}", file.exists())
        }
        assertEquals("keep", sentinel.readText())
        assertEquals("keep", externalSentinel.readText())
        assertEquals("[]", manager.historyJson())
        manager.clearAllData()
        assertEquals("[]", SessionManager(context).historyJson())
    }

    @Test
    fun managerOperations_shareTheManagerMonitor() {
        val operations = listOf<() -> Unit>(
            { manager.recordAttempt(attemptJson()) }, { manager.startSession() },
            { manager.endSession() }, { manager.saveAssessment("pre", "{}") },
            { manager.clearAllData() }, { manager.onPause() }, { manager.onResume() },
            { manager.historyJson() }, { manager.getAssessments() },
            { manager.getActiveSessionId() }, { manager.participantId }
        )
        for (operation in operations) {
            val entered = java.util.concurrent.CountDownLatch(1)
            val error = java.util.concurrent.atomic.AtomicReference<Throwable>()
            val worker = Thread {
                entered.countDown()
                try { operation() } catch (t: Throwable) { error.set(t) }
            }
            var blocked = false
            synchronized(manager) {
                worker.start()
                assertTrue(entered.await(2, java.util.concurrent.TimeUnit.SECONDS))
                val deadline = System.nanoTime() + 2_000_000_000L
                while (worker.isAlive && worker.state != Thread.State.BLOCKED && System.nanoTime() < deadline) Thread.yield()
                blocked = worker.state == Thread.State.BLOCKED
            }
            worker.join(5000)
            assertFalse("operation did not finish", worker.isAlive)
            error.get()?.let { throw AssertionError(it) }
            assertTrue("operation bypassed manager serialization", blocked)
        }
    }

    @Test
    fun clearAllData_unavailableExternalStorageFailsWithoutClaimingSuccess() {
        val unavailable = object : android.content.ContextWrapper(context) {
            override fun getExternalFilesDir(type: String?): File? = null
        }
        manager.recordAttempt(attemptJson())
        val failing = SessionManager(unavailable)
        try {
            failing.clearAllData()
            org.junit.Assert.fail("unavailable storage must fail closed")
        } catch (_: java.io.IOException) { }
        assertEquals(1, probe.getAttemptCount())
        manager.clearAllData()
        assertEquals(0, probe.getAttemptCount())
    }

    @Test
    fun clearAllData_cannotListExternalStorageFailsClosed() {
        val unreadable = object : android.content.ContextWrapper(context) {
            override fun getExternalFilesDir(type: String?): File = object : File(context.filesDir, "unreadable") {
                override fun listFiles(): Array<File>? = null
            }
        }
        try {
            SessionManager(unreadable).clearAllData()
            org.junit.Assert.fail("uninspectable storage must fail closed")
        } catch (_: java.io.IOException) { }
    }

    @Test
    fun clearAllData_failedDeletionPreservesUnrelatedDirectoryContentsAndCanRetry() {
        val blocked = File(context.getExternalFilesDir(null), "kumpas_export_old_20260101.json")
        assertTrue(blocked.mkdir())
        val sentinel = File(blocked, "keep.txt").apply { writeText("untouched") }
        manager.recordAttempt(attemptJson())
        try {
            manager.clearAllData()
            org.junit.Assert.fail("unexpected managed directory must not report success")
        } catch (_: java.io.IOException) { }
        assertEquals("untouched", sentinel.readText())
        assertEquals(1, probe.getAttemptCount())
        assertTrue(sentinel.delete())
        assertTrue(blocked.delete())
        manager.clearAllData()
        assertEquals("[]", manager.historyJson())
    }

    @Test
    fun clearAllData_databaseFailureAfterFileRemovalIsHonestAndRetryable() {
        manager.recordAttempt(attemptJson())
        val exported = File(DataExporter(context).export(manager.participantId, probe))
        probe.writableDatabase.execSQL("CREATE TRIGGER refuse_clear BEFORE DELETE ON participants BEGIN SELECT RAISE(ABORT, 'synthetic failure'); END")
        try {
            manager.clearAllData()
            org.junit.Assert.fail("database failure must propagate")
        } catch (_: android.database.sqlite.SQLiteException) { }
        assertFalse(exported.exists())
        assertEquals(1, probe.getAttemptCount())
        probe.writableDatabase.execSQL("DROP TRIGGER refuse_clear")
        manager.clearAllData()
        assertEquals("[]", SessionManager(context).historyJson())
    }

    @Test
    fun clearAllData_failedPreferenceCommitIsHonestAndRetryable() {
        val real = context.getSharedPreferences("kumpas_session_prefs", Context.MODE_PRIVATE)
        var refuseCommit = false
        val wrappedPrefs = object : android.content.SharedPreferences by real {
            override fun edit(): android.content.SharedPreferences.Editor {
                val editor = real.edit()
                return object : android.content.SharedPreferences.Editor by editor {
                    override fun putString(key: String?, value: String?): android.content.SharedPreferences.Editor {
                        editor.putString(key, value)
                        return this
                    }
                    override fun putBoolean(key: String?, value: Boolean): android.content.SharedPreferences.Editor {
                        editor.putBoolean(key, value)
                        return this
                    }
                    override fun commit(): Boolean = if (refuseCommit) false else editor.commit()
                }
            }
        }
        val wrapped = object : android.content.ContextWrapper(context) {
            override fun getSharedPreferences(name: String?, mode: Int) = wrappedPrefs
        }
        val failing = SessionManager(wrapped)
        failing.recordAttempt(attemptJson())
        refuseCommit = true
        try {
            failing.clearAllData()
            org.junit.Assert.fail("commit failure must propagate")
        } catch (_: java.io.IOException) { }
        assertEquals(0, probe.getAttemptCount()) // filesystem/DB/prefs cannot be one atomic transaction
        refuseCommit = false
        failing.clearAllData()
        val reopened = SessionManager(context)
        assertEquals(failing.participantId, reopened.participantId)
        assertEquals("[]", reopened.historyJson())
        assertTrue(real.getBoolean("jsonl_migrated", false))
    }

    @Test
    fun clearAllData_removesRealMigrationAndPreventsReimportOnReopen() {
        context.getSharedPreferences("kumpas_session_prefs", Context.MODE_PRIVATE).edit().clear().commit()
        resetDatabase()
        val legacy = File(context.filesDir, "attempt_history.jsonl").apply { writeText(JSONObject(attemptJson()).toString()) }
        val migrated = SessionManager(context)
        assertEquals(1, probe.getAttemptCount())
        val backup = File(context.filesDir, "attempt_history.jsonl.migrated")
        assertTrue(backup.exists())
        migrated.clearAllData()
        assertFalse(backup.exists())
        val newId = migrated.participantId
        legacy.writeText(attemptJson()) // an old copy cannot bypass the completed marker
        val reopened = SessionManager(context)
        assertEquals(newId, reopened.participantId)
        assertEquals("[]", reopened.historyJson())
        reopened.clearAllData()
        assertFalse(legacy.exists())
        probe.readableDatabase.rawQuery("SELECT COUNT(*) FROM participants", null).use {
            assertTrue(it.moveToFirst())
            assertEquals(1, it.getInt(0))
        }
    }

    @Test
    fun clearAllData_redirectedExportDirectoryMustNotDeleteUnrelatedFiles() {
        val elsewhere = File(context.filesDir, "unrelated").apply { mkdirs() }
        val sentinel = File(elsewhere, "kumpas_export_old_20260101.json").apply { writeText("unrelated") }
        val exports = File(context.filesDir, "exports")
        java.nio.file.Files.createSymbolicLink(exports.toPath(), elsewhere.toPath())
        try {
            manager.clearAllData()
            org.junit.Assert.fail("redirected directory must fail closed")
        } catch (_: java.io.IOException) { }
        assertEquals("unrelated", sentinel.readText())
        java.nio.file.Files.delete(exports.toPath())
        manager.clearAllData()
    }

    @Test
    fun clearAllData_checksFreshParticipantPersistenceBeforeReportingSuccess() {
        manager.recordAttempt(attemptJson())
        probe.writableDatabase.execSQL("CREATE TRIGGER refuse_identity BEFORE INSERT ON participants BEGIN SELECT RAISE(IGNORE); END")
        try {
            manager.clearAllData()
            org.junit.Assert.fail("missing fresh participant must report incomplete cleanup")
        } catch (_: android.database.sqlite.SQLiteException) { }
        assertEquals(0, probe.getAttemptCount())
        assertNull(probe.getParticipant())
        probe.writableDatabase.execSQL("DROP TRIGGER refuse_identity")
        manager.clearAllData()
        assertEquals(manager.participantId, probe.getParticipant()!!.getString("id"))
        assertEquals(manager.participantId, SessionManager(context).participantId)
    }

    @Test
    fun clearAllData_preservesNonExportNamesAndModelDataAcrossBothRoots() {
        val roots = listOf(context.getExternalFilesDir(null)!!, File(context.filesDir, "exports").apply { mkdirs() })
        val keep = mutableListOf<File>()
        val remove = mutableListOf<File>()
        for (root in roots) {
            for (name in listOf("keep.json", "kumpas_export_notes.json", "kumpas_export_old_20260101.json.bak", "model.tflite", "reference_data.json")) {
                keep.add(File(root, name).apply { writeText("unrelated-synthetic") })
            }
            for (name in listOf("kumpas_export_old_20260101.json", "kumpas_export_another-id_20260101_010203.json")) {
                remove.add(File(root, name).apply { writeText("synthetic-export") })
            }
        }
        manager.clearAllData()
        for (file in keep) assertEquals(file.name, "unrelated-synthetic", file.readText())
        for (file in remove) assertFalse(file.name, file.exists())
    }

    @Test
    fun clearAllData_redirectedManagedFileNeverDeletesItsTarget() {
        val target = File(context.filesDir, "unrelated-study-lookalike").apply { writeText("unrelated") }
        val link = File(context.getExternalFilesDir(null), "kumpas_export_old_20260101.json")
        java.nio.file.Files.createSymbolicLink(link.toPath(), target.toPath())
        try {
            manager.clearAllData()
            org.junit.Assert.fail("redirected managed file must fail closed")
        } catch (_: java.io.IOException) { }
        assertEquals("unrelated", target.readText())
        assertTrue(java.nio.file.Files.isSymbolicLink(link.toPath()))
        java.nio.file.Files.delete(link.toPath())
        manager.clearAllData()
    }

    // ─── Data management ────────────────────────────────────────────

    @Test
    fun clearAllData_wipesRowsEndsSessionAndRotatesParticipant() {
        val originalParticipant = manager.participantId
        manager.startSession()
        manager.recordAttempt(attemptJson())
        manager.saveAssessment("pre", "{}")

        manager.clearAllData()

        assertNull("active session should be ended", manager.getActiveSessionId())
        assertEquals("attempts should be gone", 0, probe.getAttemptCount())
        assertNotEquals(
            "a fresh participant id should be issued",
            originalParticipant,
            manager.participantId
        )
        assertEquals(
            "new participant has no assessments",
            0,
            JSONArray(manager.getAssessments()).length()
        )
        assertEquals("[]", manager.historyJson())
    }

    // ─── JSONL migration ────────────────────────────────────────────

    @Test
    fun migration_importsLegacyJsonlIntoALegacySession() {
        // Fresh app state: legacy file present, migration flag unset
        context.getSharedPreferences("kumpas_session_prefs", Context.MODE_PRIVATE)
            .edit().clear().commit()
        resetDatabase()

        val base = System.currentTimeMillis()
        val jsonl = File(context.filesDir, "attempt_history.jsonl")
        jsonl.writeText(
            listOf(
                """{"targetClass":1,"targetLabel":"AKO","predictedLabel":"AKO","predictedConfidence":0.9,"recognizedAsTarget":true,"overallMatch":0.8,"items":[],"timestamp":$base}""",
                """{"targetClass":2,"targetLabel":"IKAW","predictedLabel":"AKO","predictedConfidence":0.5,"recognizedAsTarget":false,"overallMatch":0.4,"items":[],"timestamp":${base + 1000}}""",
                "",
                "{ not valid json",
            ).joinToString("\n")
        )

        val migrated = SessionManager(context)

        // Both well-formed rows imported, malformed + blank lines skipped
        val history = JSONArray(migrated.historyJson())
        assertEquals(2, history.length())
        assertEquals("IKAW", history.getJSONObject(0).getString("targetLabel"))
        assertEquals("AKO", history.getJSONObject(1).getString("targetLabel"))

        // Legacy session recorded with migration provenance and computed summary
        val cursor = probe.readableDatabase.query(
            SessionDatabase.T_SESSIONS,
            arrayOf("source", "attempt_count", "signs_attempted", "started_at", "ended_at"),
            "source = ?", arrayOf("legacy_migration"), null, null, null
        )
        cursor.use {
            assertTrue("legacy session row missing", it.moveToFirst())
            assertEquals(2, it.getInt(1))
            assertEquals(2, it.getInt(2))
            assertEquals(base, it.getLong(3))
            assertEquals(base + 1000, it.getLong(4))
        }

        // Original file renamed so it is not re-imported
        assertFalse("original jsonl should be renamed", jsonl.exists())
        assertTrue(
            "migrated backup should exist",
            File(context.filesDir, "attempt_history.jsonl.migrated").exists()
        )
    }

    @Test
    fun migration_runsOnlyOnce() {
        context.getSharedPreferences("kumpas_session_prefs", Context.MODE_PRIVATE)
            .edit().clear().commit()
        resetDatabase()

        val jsonl = File(context.filesDir, "attempt_history.jsonl")
        jsonl.writeText(
            """{"targetClass":1,"targetLabel":"AKO","predictedLabel":"AKO","predictedConfidence":0.9,"recognizedAsTarget":true,"overallMatch":0.8,"items":[],"timestamp":${System.currentTimeMillis()}}"""
        )

        val first = SessionManager(context)
        assertEquals(1, JSONArray(first.historyJson()).length())

        // A second manager must not re-import (file is gone and flag is set)
        val second = SessionManager(context)
        assertEquals(1, JSONArray(second.historyJson()).length())
    }

    @Test
    fun migration_withNoLegacyFileIsANoOp() {
        context.getSharedPreferences("kumpas_session_prefs", Context.MODE_PRIVATE)
            .edit().clear().commit()
        resetDatabase()
        File(context.filesDir, "attempt_history.jsonl").delete()

        val fresh = SessionManager(context)

        assertEquals("[]", fresh.historyJson())
        assertNull(fresh.getActiveSessionId())
    }
}
