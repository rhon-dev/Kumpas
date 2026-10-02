package com.kumpas.kumpas_app

import org.junit.Assert.*
import org.junit.Test

class PipelineTraceTest {
    @Test fun boundariesUseOnlyMonotonicNativeClock() {
        val trace = PipelineTrace("synthetic", 1_000_000, 5_000_000, 8_000_000, 2_000_000)
        trace.delivered(10_000_000)
        trace.acknowledged(12_000_000)
        val json = trace.toJson()
        assertEquals(4.0, json.getDouble("collection_ms"), 0.0)
        assertEquals(5.0, json.getDouble("final_analyzer_to_event_ms"), 0.0)
        assertEquals(5.0, json.getDouble("analyzer_to_feedback_ms"), 0.0)
        assertEquals(7.0, json.getDouble("final_analyzer_to_ui_ack_ms"), 0.0)
        assertEquals(11.0, json.getDouble("first_analyzer_to_ui_ack_ms"), 0.0)
        assertEquals(2.0, json.getDouble("inference_ms"), 0.0)
        assertEquals("analyzer_entry_not_sensor_exposure", json.getString("origin"))
    }
    @Test fun retainsAttemptStartBeforeFirstSelectedAnalyzer() {
        val constructor = PipelineTrace::class.java.getDeclaredConstructor(String::class.java,
            Long::class.javaPrimitiveType, Long::class.javaPrimitiveType, Long::class.javaPrimitiveType,
            Long::class.javaPrimitiveType, Long::class.javaPrimitiveType)
        val trace = constructor.newInstance("synthetic", 10L, 20L, 30L, 1L, 5L)
        assertEquals(5L, trace.toJson().getLong("attempt_started_ns"))
    }
    @Test fun absentUiAckRemainsAbsentNotZero() {
        val trace = PipelineTrace("synthetic", 1, 2, 3, 0)
        trace.delivered(4)
        assertFalse(trace.toJson().has("ui_ack_ns"))
        assertFalse(trace.toJson().has("final_analyzer_to_ui_ack_ms"))
    }
    @Test fun impossibleOrderingIsRejected() {
        assertThrows(IllegalArgumentException::class.java) { PipelineTrace("bad", 5, 2, 3, 0) }
        val trace = PipelineTrace("synthetic", 1, 2, 3, 0)
        assertThrows(IllegalArgumentException::class.java) { trace.delivered(2) }
        assertThrows(IllegalArgumentException::class.java) { trace.acknowledged(4) }
        trace.delivered(5)
        assertThrows(IllegalArgumentException::class.java) { trace.acknowledged(4) }
    }
}
