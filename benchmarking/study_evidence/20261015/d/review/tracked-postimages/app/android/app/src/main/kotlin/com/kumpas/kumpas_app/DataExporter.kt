package com.kumpas.kumpas_app

import android.content.Context
import android.os.Build
import android.util.Log
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/**
 * Exports all session data as a single JSON file for research use (Phase 8).
 *
 * The export contains:
 * - metadata (timestamp, app version, device, participant ID)
 * - all assessments (pre/post)
 * - all sessions with nested attempts
 *
 * Output is written to app-specific external files directory, accessible
 * via `adb pull` without root.
 */
class DataExporter internal constructor(
    private val context: Context,
    private val publication: ExportPublication,
    private val now: () -> Date = { Date() }
) {
    constructor(context: Context) : this(context, ExportPublication())

    companion object {
        private const val TAG = "KumpasExport"
    }

    /**
     * Export all data for the given participant to a JSON file.
     * Returns the absolute file path on success, or throws on failure.
     * Borrows [db]: the caller must close its helper in use/finally on both paths.
     * The caller must also serialize this export with SessionManager persistence/purge.
     */
    fun export(participantId: String, db: SessionDatabase): String {
        val root = buildExportJson(participantId, db)
        val outFile = getExportFile(participantId)
        outFile.parentFile?.mkdirs()
        if (!outFile.createNewFile()) throw java.io.IOException("Export destination already exists")
        // Both names deliberately fit StudyDataFiles' managed-export matcher.
        // Reserve the unique destination before writing; never replace an existing export.
        val staging = File(outFile.parentFile, outFile.name.replaceFirst("kumpas_export_", "kumpas_export_stage-"))
        var stagingOwned = false
        try {
            if (!staging.createNewFile()) throw java.io.IOException("Export staging already exists")
            stagingOwned = true
            val bytes = root.toString(2).toByteArray(Charsets.UTF_8)
            publication.open(staging).use { it.write(bytes) }
            if (!publication.read(staging).contentEquals(bytes)) {
                throw java.io.IOException("Export staging verification failed")
            }
            publication.publish(staging, outFile)
            if (!publication.read(outFile).contentEquals(bytes) || staging.exists()) {
                throw java.io.IOException("Export publication verification failed")
            }
        } catch (failure: Exception) {
            for (file in listOfNotNull(outFile, staging.takeIf { stagingOwned })) {
                if (!file.delete() && file.exists()) {
                    failure.addSuppressed(java.io.IOException("Incomplete export cleanup; retry managed purge"))
                }
            }
            throw failure
        }
        Log.i(TAG, "Exported to: ${outFile.absolutePath}")
        return outFile.absolutePath
    }

    private fun buildExportJson(participantId: String, db: SessionDatabase): JSONObject {
        val root = JSONObject()

        // Metadata
        val metadata = JSONObject().apply {
            put("export_timestamp", isoTimestamp())
            put("app_version", getAppVersion())
            put("device_model", "${Build.MANUFACTURER} ${Build.MODEL}")
            put("android_version", Build.VERSION.RELEASE)
            put("participant_id", participantId)
        }
        root.put("metadata", metadata)

        // Assessments
        val assessments = db.getAssessments(participantId)
        root.put("assessments", assessments)

        // Sessions with nested attempts
        val sessions = db.getAllSessions(participantId)
        val sessionsWithAttempts = JSONArray()
        for (i in 0 until sessions.length()) {
            val session = sessions.getJSONObject(i)
            val sessionId = session.getString("id")
            val attempts = db.getAttempts(sessionId)
            session.put("attempts", attempts)
            sessionsWithAttempts.put(session)
        }
        root.put("sessions", sessionsWithAttempts)

        // Summary stats
        val summary = JSONObject().apply {
            put("total_sessions", sessions.length())
            put("total_attempts", (0 until sessionsWithAttempts.length()).sumOf {
                sessionsWithAttempts.getJSONObject(it).getJSONArray("attempts").length()
            })
            put("total_assessments", assessments.length())
        }
        root.put("summary", summary)

        return root
    }

    private fun getExportFile(participantId: String): File {
        // Use app-specific external files dir (no permission needed on API 19+)
        val dir = context.getExternalFilesDir(null)
            ?: File(context.filesDir, "exports")
        val shortId = participantId.take(8)
        val ts = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(now())
        return File(dir, "kumpas_export_${shortId}-${java.util.UUID.randomUUID()}_$ts.json")
    }

    private fun isoTimestamp(): String {
        return SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.US).format(now())
    }

    private fun getAppVersion(): String {
        return try {
            context.packageManager.getPackageInfo(context.packageName, 0).versionName ?: "1.0.0"
        } catch (_: Exception) { "1.0.0" }
    }
}
