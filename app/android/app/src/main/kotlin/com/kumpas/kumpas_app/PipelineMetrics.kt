package com.kumpas.kumpas_app

import kotlin.math.ceil
import kotlin.math.min

/** Pure half-open monotonic windows; no Android clock or participant data. */
class PipelineMetrics(val startNs: Long, val requestedDurationSeconds: Int) {
    init { require(requestedDurationSeconds >= 60) { "Benchmark requires at least 60 seconds" } }
    val durationNs: Long get() = requestedDurationSeconds * 1_000_000_000L
    enum class Stage { ANALYZER, SELECTED, PROCESSED, EVENT }
    private val bins = Stage.entries.associateWith { mutableMapOf<Int, Int>() }
    private val failures = mutableMapOf<String, Int>()

    @Synchronized fun record(stage: Stage, atNs: Long) {
        val elapsed = atNs - startNs
        if (elapsed < 0 || elapsed >= durationNs) return
        val bin = (elapsed / 1_000_000_000L).toInt()
        val stageBins = bins.getValue(stage)
        stageBins[bin] = (stageBins[bin] ?: 0) + 1
    }
    @Synchronized fun recordFailure(reason: String, atNs: Long) {
        if (atNs < startNs || atNs - startNs >= durationNs) return
        failures[reason] = (failures[reason] ?: 0) + 1
    }
    @Synchronized fun snapshot(endNs: Long): Snapshot {
        require(endNs >= startNs) { "Monotonic clock went backwards" }
        val elapsed = (endNs - startNs).coerceAtMost(durationNs) / 1e9
        val n = ceil(elapsed).toInt()
        fun rate(stage: Stage): Rate {
            val counts = List(n) { bins.getValue(stage)[it] ?: 0 }
            val samples = counts.mapIndexed { i, count -> count / min(1.0, elapsed - i) }
            val count = counts.sum()
            return Rate(count, if (elapsed > 0) count / elapsed else 0.0, samples)
        }
        return Snapshot(elapsed, elapsed >= requestedDurationSeconds,
            Stage.entries.associateWith(::rate), failures.toMap())
    }
    data class Rate(val count: Int, val meanFps: Double, val perSecondSamples: List<Double>)
    data class Snapshot(val durationSeconds: Double, val complete: Boolean,
        val rates: Map<Stage, Rate>, val failures: Map<String, Int>) {
        val analyzer: Rate get() = rates.getValue(Stage.ANALYZER)
        val failureCount: Int get() = failures.values.sum()
        fun sustainedAnalyzerPass(isEmulator: Boolean): Boolean = !isEmulator && complete &&
            analyzer.count > 0 && analyzer.meanFps >= 24.0 && analyzer.perSecondSamples.all { it >= 24.0 }
    }
}
