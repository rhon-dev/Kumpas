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

    private lateinit var fixtureRoot: File
    private lateinit var context: Context
    private lateinit var db: SessionDatabase
    private lateinit var exporter: DataExporter

    private val participantId = "11111111-2222-3333-4444-555555555555"

    @Before
    fun setUp() {
        val app = RuntimeEnvironment.getApplication() as Context
        fixtureRoot = java.nio.file.Files.createTempDirectory("kumpas-export-test-").toFile()
        context = object : android.content.ContextWrapper(app) {
            override fun getFilesDir(): File = File(fixtureRoot, "internal").apply { mkdirs() }
            override fun getExternalFilesDir(type: String?): File = File(fixtureRoot, "external").apply { mkdirs() }
            override fun getDatabasePath(name: String): File = File(fixtureRoot, name)
            override fun openOrCreateDatabase(name: String, mode: Int,
                factory: android.database.sqlite.SQLiteDatabase.CursorFactory?): android.database.sqlite.SQLiteDatabase =
                super.openOrCreateDatabase(getDatabasePath(name).absolutePath, mode, factory)
            override fun openOrCreateDatabase(name: String, mode: Int,
                factory: android.database.sqlite.SQLiteDatabase.CursorFactory?,
                handler: android.database.DatabaseErrorHandler?): android.database.sqlite.SQLiteDatabase =
                super.openOrCreateDatabase(getDatabasePath(name).absolutePath, mode, factory, handler)
        }
        db = SessionDatabase(context)
        exporter = DataExporter(context, ExportPublication()) { java.util.Date(0L) }
        db.insertParticipant(participantId, "test-device", "1.0.0")
    }

    @After
    fun tearDown() {
        db.close()
        fixtureRoot.deleteRecursively()
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
    fun export_summaryCountsOnlyNestedParticipantAttempts() {
        seedSession("owned", "AKO", "IKAW")
        val other = "99999999-8888-7777-6666-555555555555"
        db.insertParticipant(other, "synthetic", "1.0.0")
        db.insertSession("other", other)
        db.insertAttempt("other", 1L, 1, "OTHER", "OTHER", 0.9, true, 0.8, "[]")
        val (_, root) = exportAndParse()
        val sessions = root.getJSONArray("sessions")
        val nested = (0 until sessions.length()).sumOf {
            val session = sessions.getJSONObject(it)
            assertEquals(participantId, session.getString("participant_id"))
            session.getJSONArray("attempts").length()
        }
        assertEquals(2, nested)
        assertEquals(nested, root.getJSONObject("summary").getInt("total_attempts"))
    }

    @Test
    fun export_repeatedSameTimeDoesNotOverwriteCompletedData() {
        seedSession("first", "AKO")
        val first = File(exporter.export(participantId, db))
        val original = first.readBytes()
        seedSession("second", "IKAW")
        val second = File(exporter.export(participantId, db))
        org.junit.Assert.assertNotEquals(first, second)
        org.junit.Assert.assertArrayEquals(original, first.readBytes())
        assertEquals(2, JSONObject(second.readText()).getJSONArray("sessions").length())
    }

    @Test
    fun export_partialWriteFailureRemovesOnlyNewArtifacts() {
        assertPublicationFailure(object : ExportPublication() {
            override fun open(file: File): java.io.OutputStream {
                val real = super.open(file)
                return object : java.io.FilterOutputStream(real) {
                    override fun write(bytes: ByteArray, off: Int, len: Int) {
                        out.write(bytes, off, minOf(8, len))
                        throw java.io.IOException("synthetic partial write")
                    }
                }
            }
        })
    }

    @Test
    fun export_closeFailureRemovesOnlyNewArtifacts() {
        assertPublicationFailure(object : ExportPublication() {
            override fun open(file: File): java.io.OutputStream =
                object : java.io.FilterOutputStream(super.open(file)) {
                    override fun close() {
                        super.close()
                        throw java.io.IOException("synthetic close failure")
                    }
                }
        })
    }

    @Test
    fun export_publicationFailureRemovesOnlyNewArtifacts() {
        assertPublicationFailure(object : ExportPublication() {
            override fun publish(staging: File, destination: File) {
                assertTrue("must publish from separate staging", staging != destination)
                JSONObject(staging.readText())
                throw java.io.IOException("synthetic publication failure")
            }
        })
    }

    @Test
    fun export_corruptPublicationCannotReturnSuccess() {
        assertPublicationFailure(object : ExportPublication() {
            override fun publish(staging: File, destination: File) {
                super.publish(staging, destination)
                destination.writeText("{}")
            }
        })
    }

    @Test
    fun export_committedReadFailureCannotReturnSuccess() {
        assertPublicationFailure(object : ExportPublication() {
            override fun read(file: File): ByteArray {
                if (!file.name.startsWith("kumpas_export_stage-")) {
                    throw java.io.IOException("synthetic committed read failure")
                }
                return super.read(file)
            }
        })
    }

    @Test
    fun export_errorAfterRenameRemovesOnlyNewArtifacts() {
        assertPublicationFailure(object : ExportPublication() {
            override fun publish(staging: File, destination: File) {
                super.publish(staging, destination)
                throw java.io.IOException("synthetic error after rename")
            }
        })
    }

    @Test
    fun export_allActualStagingAndCompletedNamesAreManagedByPurge() {
        val artifacts = mutableListOf<File>()
        val io = object : ExportPublication() {
            override fun publish(staging: File, destination: File) {
                artifacts.add(staging)
                artifacts.add(destination)
                super.publish(staging, destination)
            }
        }
        DataExporter(context, io).export(participantId, db)
        val internalOnly = object : android.content.ContextWrapper(context) {
            override fun getExternalFilesDir(type: String?): File? = null
        }
        DataExporter(internalOnly, io).export(participantId, db)
        // Recreate exact observed staging names to model interrupted work.
        artifacts.forEach { if (!it.exists()) it.writeText("synthetic interrupted staging") }
        val sentinels = artifacts.map { it.parentFile }.distinct().map {
            File(it, "unrelated.json").apply { writeText("sentinel") }
        }
        StudyDataFiles.purge(context)
        artifacts.forEach { org.junit.Assert.assertFalse(it.exists()) }
        sentinels.forEach { assertEquals("sentinel", it.readText()) }
    }

    @Test
    fun export_silentShortWriteFailsStagingVerification() {
        assertPublicationFailure(object : ExportPublication() {
            override fun open(file: File): java.io.OutputStream =
                object : java.io.FilterOutputStream(super.open(file)) {
                    override fun write(bytes: ByteArray, off: Int, len: Int) {
                        out.write(bytes, off, minOf(8, len))
                    }
                }
        })
    }

    private fun assertPublicationFailure(io: ExportPublication) {
        seedSession("prior", "AKO")
        val prior = File(exporter.export(participantId, db))
        val priorBytes = prior.readBytes()
        val sentinel = File(prior.parentFile, "unrelated.txt").apply { writeText("sentinel") }
        val before = prior.parentFile!!.listFiles()!!.map { it.name }.toSet()
        seedSession("later", "IKAW")
        val borrowedHandle = db.writableDatabase
        try {
            DataExporter(context, io) { java.util.Date(0L) }.export(participantId, db)
            org.junit.Assert.fail("failed export must not return a success path")
        } catch (_: java.io.IOException) { }
        org.junit.Assert.assertArrayEquals(priorBytes, prior.readBytes())
        assertEquals("sentinel", sentinel.readText())
        assertEquals("no partial new export may remain", before,
            prior.parentFile!!.listFiles()!!.map { it.name }.toSet())
        assertTrue("original borrowed handle must remain open before any getter can reopen it", borrowedHandle.isOpen)
        assertEquals(2, db.getAttemptCount())
        // Failure must not poison a subsequent export or the borrowed database.
        assertEquals(2, exportAndParse().second.getJSONObject("summary").getInt("total_attempts"))
    }

    @Test
    fun export_fileNameCarriesParticipantPrefix() {
        val (file, _) = exportAndParse()

        assertTrue(
            "unexpected export file name: ${file.name}",
            Regex("^kumpas_export_${participantId.take(8)}-[A-Za-z0-9-]+_\\d{8}_\\d{6}\\.json$")
                .matches(file.name)
        )
    }

    @Test
    fun export_unavailableExternalStorageUsesInternalFallbackAndLeavesBorrowedHelperOpen() {
        seedSession("fallback-session", "SYNTHETIC")
        val unavailable = object : android.content.ContextWrapper(context) {
            override fun getExternalFilesDir(type: String?): File? = null
        }
        val path = DataExporter(unavailable).export(participantId, db)
        val file = File(path)
        assertEquals(File(context.filesDir, "exports").canonicalFile, file.parentFile!!.canonicalFile)
        assertEquals(1, JSONObject(file.readText()).getJSONObject("summary").getInt("total_attempts"))
        assertTrue("export borrows rather than owns the helper", db.readableDatabase.isOpen)
        assertEquals(1, db.getAttemptCount())
    }

    @Test
    fun export_writeFailurePropagatesWithoutClosingBorrowedHelper() {
        val blocked = File(context.filesDir, "blocked-export-root").apply { writeText("sentinel") }
        val unavailable = object : android.content.ContextWrapper(context) {
            override fun getExternalFilesDir(type: String?): File = blocked
        }
        val borrowedHandle = db.writableDatabase
        try {
            DataExporter(unavailable).export(participantId, db)
            org.junit.Assert.fail("cannot claim an export path when writing fails")
        } catch (_: java.io.IOException) { }
        assertEquals("sentinel", blocked.readText())
        assertTrue("caller remains responsible for closing its original handle", borrowedHandle.isOpen)
    }

    @Test
    fun export_successLeavesBorrowedDatabaseOpenUntilCallerClosesIt() {
        val openDatabase = db.writableDatabase
        exportAndParse()
        assertTrue(openDatabase.isOpen)
        db.close()
        org.junit.Assert.assertFalse("caller use/finally must release the database", openDatabase.isOpen)
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
