package com.kumpas.kumpas_app

import android.graphics.Bitmap
import android.graphics.Color
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith

/** Blank synthetic image; no participant video or default study-store mutation. */
@RunWith(AndroidJUnit4::class)
class VisionAttemptContractTest {
    @Test fun noSignerCancellationAndInvalidTargetKeepAttemptIdentity() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val events = mutableListOf<JSONObject>()
        val engine = VisionEngine(context) { events.add(JSONObject(it)) }
        val bitmap = Bitmap.createBitmap(128,128,Bitmap.Config.ARGB_8888).apply { eraseColor(Color.BLACK) }
        try {
            assertThrows(IllegalArgumentException::class.java) { engine.startAttempt(-1) }
            assertThrows(IllegalArgumentException::class.java) { engine.startAttempt(50) }
            val id = engine.startAttempt(22)
            repeat(VisionEngine.SEQ_LEN) { engine.onFrame(bitmap.copy(Bitmap.Config.ARGB_8888, false), it.toLong()+1) }
            val failures = events.filter { it.optString("state") == "attempt_failed" }
            assertEquals(1, failures.size)
            assertEquals(id,failures.single().getString("attemptId"))
            assertTrue(events.filter { it.optString("state") == "attempt_progress" }
                .all { it.getString("attemptId") == id })
            events.clear()
            val cancelled = engine.startAttempt(22)
            engine.cancelAttempt(cancelled)
            val finalBitmap = bitmap.copy(Bitmap.Config.ARGB_8888, false)
            engine.onFrame(finalBitmap,100)
            assertTrue(events.none { it.optString("state").startsWith("attempt_") })
            assertTrue(finalBitmap.isRecycled)
            assertThrows(IllegalArgumentException::class.java) { engine.onFrame(finalBitmap,101) }
        } finally {
            bitmap.recycle()
            engine.close()
            engine.close()
        }
    }
}
