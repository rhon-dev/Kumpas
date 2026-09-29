package com.kumpas.kumpas_app

import org.junit.Assert.assertEquals
import org.junit.Test

class FeatureNormalizerTest {
    @Test fun missingHandRemainsZeroAfterNormalization() {
        val raw = FloatArray(258)
        for (i in 0 until 33) {
            raw[i * 4] = 0.5f
            raw[i * 4 + 1] = 0.5f
            raw[i * 4 + 2] = 0.1f
            raw[i * 4 + 3] = 1f
        }
        raw[11 * 4 + 1] = 0.2f
        raw[12 * 4 + 1] = 0.2f
        for (i in 195 until 258) raw[i] = 0.6f
        FeatureNormalizer.normalize(raw, true)
        for (i in 132 until 195) assertEquals(0f, raw[i], 0f)
        assertEquals(0f, raw[23 * 4], 0.0001f) // mid-hip is origin
        assertEquals(1f, raw[11 * 4 + 3], 0f) // visibility is not scaled
        assertEquals((0.6f - 0.5f) / 0.3f, raw[195], 0.0001f)
    }

    @Test fun noPoseLeavesFeatureVectorUntouched() {
        val raw = FloatArray(258) { 0.75f }
        FeatureNormalizer.normalize(raw, false)
        for (i in raw.indices) assertEquals(0.75f, raw[i], 0f)
    }
}
