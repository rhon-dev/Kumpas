package com.kumpas.kumpas_app

import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.ByteArrayOutputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder

/**
 * Parity test: the Kotlin FeedbackEngine must produce the same feedback as
 * the Python reference (training/feedback/feedback_engine.py) on real
 * fixture sequences exported by training/feedback/export_for_app.py.
 *
 * Regenerate fixtures + gold_standards.bin with export_for_app.py whenever
 * the Python reference changes.
 */
class FeedbackEngineParityTest {

    private val severityTolerance = 0.05

    private fun loadGold(): Array<Array<FloatArray>> {
        val stream = javaClass.classLoader!!.getResourceAsStream("gold_standards.bin")
            ?: this::class.java.getResourceAsStream("/gold_standards.bin")
            ?: error("gold_standards.bin not on test classpath")
        val bytes = ByteArrayOutputStream().use { out -> stream.copyTo(out); out.toByteArray() }
        val buf = ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN)
        return Array(50) { Array(FeedbackEngine.SEQ_LEN) {
            FloatArray(FeedbackEngine.N_FEATURES) { buf.float } } }
    }

    private fun runCase(name: String) {
        val text = javaClass.classLoader!!.getResourceAsStream("feedback_$name.json")!!
            .readBytes().decodeToString()
        val fixture = JSONObject(text)
        val attemptJson = fixture.getJSONArray("attempt")
        val attempt = Array(attemptJson.length()) { t ->
            val row = attemptJson.getJSONArray(t)
            FloatArray(row.length()) { f -> row.getDouble(f).toFloat() }
        }
        val gold = loadGold()[fixture.getInt("target_class")]
        val report = FeedbackEngine.compare(attempt, gold, fixture.getString("target_label"))

        val expected = fixture.getJSONArray("expected_items")
        val expectedKeys = (0 until expected.length()).map {
            val e = expected.getJSONObject(it)
            "${e.getString("dimension")}/${e.getString("hand")}" to e.getDouble("severity")
        }.toMap()
        val actualKeys = report.items.associate { "${it.dimension}/${it.hand}" to it.severity }

        assertEquals("flagged dimensions differ for $name", expectedKeys.keys, actualKeys.keys)
        for ((key, expSev) in expectedKeys) {
            assertTrue("severity drift on $key for $name: expected $expSev got ${actualKeys[key]}",
                Math.abs(expSev - actualKeys[key]!!) <= severityTolerance)
        }
        assertTrue("overall match drift for $name",
            Math.abs(fixture.getDouble("expected_overall_match") - report.overallMatch)
                <= severityTolerance)
    }

    @Test fun confusedPairAttemptMatchesPython() = runCase("case_confused_pair")
    @Test fun handshapeAttemptMatchesPython() = runCase("case_handshape")
    @Test fun correctAttemptProducesNoItems() = runCase("case_correct")
}
