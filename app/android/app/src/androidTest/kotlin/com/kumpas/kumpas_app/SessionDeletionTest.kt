package com.kumpas.kumpas_app

import android.content.Context
import android.content.ContextWrapper
import android.content.SharedPreferences
import android.database.DatabaseErrorHandler
import android.database.sqlite.SQLiteDatabase
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import java.io.File
import java.util.UUID

/** Synthetic fixture only. Never opens the default participant database/preferences. */
@RunWith(AndroidJUnit4::class)
class SessionDeletionTest {
    private class FixtureContext(base: Context) : ContextWrapper(base) {
        val fixtureId = "study_deletion_${UUID.randomUUID()}"
        val root = File(base.filesDir, fixtureId).apply { check(mkdirs()) }
        val externalRoot = File(checkNotNull(base.getExternalFilesDir(null)), fixtureId).apply { check(mkdirs()) }
        private val preferenceNames = mutableSetOf<String>()
        private val opened = mutableListOf<SQLiteDatabase>()

        override fun getApplicationContext(): Context = this
        override fun getFilesDir(): File = File(root, "files").apply { mkdirs() }
        override fun getExternalFilesDir(type: String?): File = externalRoot
        override fun getExternalFilesDirs(type: String?): Array<File> = arrayOf(externalRoot)
        override fun getDatabasePath(name: String): File = File(root, "databases/$name").apply { parentFile!!.mkdirs() }
        override fun openOrCreateDatabase(name: String, mode: Int, factory: SQLiteDatabase.CursorFactory?): SQLiteDatabase =
            openOrCreateDatabase(name, mode, factory, null)
        override fun openOrCreateDatabase(name: String, mode: Int, factory: SQLiteDatabase.CursorFactory?, handler: DatabaseErrorHandler?): SQLiteDatabase =
            SQLiteDatabase.openDatabase(getDatabasePath(name).path, factory, SQLiteDatabase.CREATE_IF_NECESSARY, handler).also { opened.add(it) }
        override fun deleteDatabase(name: String): Boolean = SQLiteDatabase.deleteDatabase(getDatabasePath(name))
        override fun getSharedPreferences(name: String, mode: Int): SharedPreferences {
            // Unique fixture namespace under the instrumentation process UID, never default app prefs.
            val isolatedName = "${fixtureId}_$name"
            preferenceNames.add(isolatedName)
            return baseContext.getSharedPreferences(isolatedName, mode)
        }
        fun dispose() {
            opened.forEach { if (it.isOpen) it.close() }
            preferenceNames.forEach { check(baseContext.deleteSharedPreferences(it)) }
            check(root.deleteRecursively())
            check(externalRoot.deleteRecursively())
        }
    }

    @Test
    fun clearsOnlyIsolatedStudyStoresAfterRealMigrationExportAndReopen() {
        val instrumentation = InstrumentationRegistry.getInstrumentation()
        // Instrumentation executes with the target UID, not the test APK UID.
        val testContext = instrumentation.targetContext
        val context = FixtureContext(testContext)
        try {
            assertNotEquals(testContext.filesDir.canonicalPath, context.filesDir.canonicalPath)
            assertTrue(context.filesDir.canonicalPath.startsWith(context.root.canonicalPath + "/"))
            assertNotEquals(testContext.getDatabasePath("kumpas_sessions.db"), context.getDatabasePath("kumpas_sessions.db"))
            val attempt = """{"targetClass":1,"targetLabel":"SYNTHETIC","predictedLabel":"SYNTHETIC","predictedConfidence":0.9,"recognizedAsTarget":true,"overallMatch":0.8,"items":[],"timestamp":1}"""
            File(context.filesDir, "attempt_history.jsonl").writeText(attempt)
            val manager = SessionManager(context)
            val database = SessionDatabase(context)
            assertEquals(1, database.getAttemptCount())
            manager.recordAttempt(attempt)
            manager.saveAssessment("pre", "{\"synthetic\":true}")
            val exported = File(DataExporter(context).export(manager.participantId, database))
            val fallback = object : ContextWrapper(context) {
                override fun getExternalFilesDir(type: String?): File? = null
            }
            val internalExport = File(DataExporter(fallback).export("old-synthetic", database))
            val sentinel = File(context.filesDir, "keep.txt").apply { writeText("keep") }
            val externalSentinel = File(context.externalRoot, "keep.json").apply { writeText("keep") }
            val migrated = File(context.filesDir, "attempt_history.jsonl.migrated")
            assertTrue(migrated.exists())
            manager.clearAllData()
            manager.clearAllData()
            assertFalse(migrated.exists())
            assertFalse(exported.exists())
            assertFalse(internalExport.exists())
            assertEquals("keep", sentinel.readText())
            assertEquals("keep", externalSentinel.readText())
            val reopened = SessionManager(context)
            assertEquals(manager.participantId, reopened.participantId)
            assertEquals("[]", reopened.historyJson())
            assertEquals("[]", reopened.getAssessments())
            assertTrue(context.getSharedPreferences("kumpas_session_prefs", Context.MODE_PRIVATE).getBoolean("jsonl_migrated", false))
            for (table in listOf("participants", "sessions", "attempts", "assessments")) {
                database.readableDatabase.rawQuery("SELECT COUNT(*) FROM $table", null).use {
                    assertTrue(it.moveToFirst())
                    assertEquals(table, if (table == "participants") 1 else 0, it.getInt(0))
                }
            }
            database.close()
        } finally {
            context.dispose()
        }
    }
}
