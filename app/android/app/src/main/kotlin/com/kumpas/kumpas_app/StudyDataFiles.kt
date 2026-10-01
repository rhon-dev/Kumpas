package com.kumpas.kumpas_app

import android.content.Context
import java.io.File
import java.io.IOException

/** Deletes only managed study files; never traverses directories or follows file links. */
internal object StudyDataFiles {
    private val exportName = Regex("^kumpas_export_[A-Za-z0-9-]+_[0-9]{8}(?:_[0-9]{6})?\\.json$")

    fun purge(context: Context) {
        val internal = context.filesDir
        // Null is unavailable, not evidence that old external exports do not exist.
        val external = context.getExternalFilesDir(null)
            ?: throw IOException("Study-data cleanup incomplete: external storage unavailable; retry when mounted")
        val roots = listOf(external, File(internal, "exports"))
        val managed = mutableListOf(
            File(internal, "attempt_history.jsonl"),
            File(internal, "attempt_history.jsonl.migrated")
        )
        for (root in roots) {
            if (root.canonicalFile != File(root.parentFile!!.canonicalFile, root.name)) {
                throw IOException("Study-data cleanup incomplete: export storage is redirected")
            }
            if (!root.exists() && root != external) continue
            val files = root.listFiles()
                ?: throw IOException("Study-data cleanup incomplete: cannot inspect export storage")
            managed.addAll(files.filter { exportName.matches(it.name) })
        }
        for (file in managed) {
            if (!file.exists()) continue
            // A directory or redirected path is unexpected: fail closed, do not erase its contents.
            if (!file.isFile || file.canonicalFile != File(file.parentFile!!.canonicalFile, file.name) || !file.delete() || file.exists()) {
                throw IOException("Study-data cleanup incomplete: managed file could not be removed; retry")
            }
        }
    }
}
