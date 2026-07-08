package com.kumpas.kumpas_app

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject
import java.io.File

/**
 * Local attempt history (Phase 8 will decide on cloud sync; until then this
 * is append-only JSONL in app-private storage — nothing leaves the device,
 * consistent with the PRD's offline-first requirement).
 */
class SessionLog(context: Context) {

    private val file = File(context.filesDir, "attempt_history.jsonl")

    @Synchronized
    fun append(attemptResultJson: String) {
        val entry = JSONObject(attemptResultJson)
        entry.put("timestamp", System.currentTimeMillis())
        entry.remove("state")
        file.appendText(entry.toString() + "\n")
    }

    @Synchronized
    fun historyJson(limit: Int = 200): String {
        if (!file.exists()) return "[]"
        val lines = file.readLines().takeLast(limit).reversed()  // newest first
        val arr = JSONArray()
        for (l in lines) if (l.isNotBlank()) arr.put(JSONObject(l))
        return arr.toString()
    }
}
