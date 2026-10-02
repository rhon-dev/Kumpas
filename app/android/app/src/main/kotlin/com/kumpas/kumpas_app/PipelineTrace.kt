package com.kumpas.kumpas_app

import org.json.JSONObject

/** Native elapsedRealtimeNanos only. Sensor timestamps and Dart epochs never mix. */
internal class PipelineTrace(
    val attemptId: String,
    private val firstAnalyzerNs: Long,
    private val finalAnalyzerNs: Long,
    private val nativeResultNs: Long,
    private val inferenceNs: Long,
    private val attemptStartedNs: Long = firstAnalyzerNs,
) {
    private var deliveryNs: Long? = null
    private var ackNs: Long? = null
    init {
        require(firstAnalyzerNs > 0 && finalAnalyzerNs >= firstAnalyzerNs && nativeResultNs >= finalAnalyzerNs)
        require(inferenceNs >= 0)
        require(attemptStartedNs > 0 && attemptStartedNs <= firstAnalyzerNs)
    }
    fun delivered(nowNs: Long) {
        require(nowNs >= nativeResultNs)
        deliveryNs = nowNs
    }
    fun acknowledged(nowNs: Long) {
        require(deliveryNs != null && nowNs >= deliveryNs!!)
        ackNs = nowNs
    }
    fun toJson(): JSONObject = JSONObject().apply {
        put("attempt_id", attemptId)
        put("origin", "analyzer_entry_not_sensor_exposure")
        put("ui_endpoint", "post_frame_native_ack_upper_bound_not_physical_display")
        put("attempt_started_ns", attemptStartedNs)
        put("first_analyzer_ns", firstAnalyzerNs)
        put("final_analyzer_ns", finalAnalyzerNs)
        put("native_result_ns", nativeResultNs)
        put("collection_ms", (finalAnalyzerNs - firstAnalyzerNs) / 1e6)
        put("inference_ms", inferenceNs / 1e6)
        deliveryNs?.let {
            put("event_delivery_ns", it)
            put("final_analyzer_to_event_ms", (it - finalAnalyzerNs) / 1e6)
            put("analyzer_to_feedback_ms", (it - finalAnalyzerNs) / 1e6)
        }
        ackNs?.let {
            put("ui_ack_ns", it)
            put("final_analyzer_to_ui_ack_ms", (it - finalAnalyzerNs) / 1e6)
            put("first_analyzer_to_ui_ack_ms", (it - firstAnalyzerNs) / 1e6)
        }
    }
}
