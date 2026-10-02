package com.kumpas.kumpas_app

import org.junit.Assert.*
import org.junit.Test

class PipelineMetricsTest {
    @Test fun invalidDurationsRejected() {
        for (duration in listOf(-1, 0, 59)) {
            try { PipelineMetrics(0, duration); fail("accepted $duration") }
            catch (_: IllegalArgumentException) { }
        }
    }
    @Test fun emptyHasTrailingZeros() {
        val snapshot = PipelineMetrics(0, 60).snapshot(60_000_000_000)
        assertEquals(60.0, snapshot.durationSeconds, 0.0)
        assertEquals(List(60) { 0.0 }, snapshot.analyzer.perSecondSamples)
        assertTrue(snapshot.complete)
    }
    @Test fun countersUseFullWindowIncludingLeadingAndTrailingSilence() {
        val metrics = PipelineMetrics(1_000_000_000, 60)
        repeat(30) { metrics.record(PipelineMetrics.Stage.ANALYZER, 2_000_000_000) }
        repeat(4) { metrics.record(PipelineMetrics.Stage.EVENT, 2_000_000_000) }
        val result = metrics.snapshot(61_000_000_000)
        assertEquals(0.5, result.analyzer.meanFps, 0.0)
        assertEquals(0.0, result.analyzer.perSecondSamples.first(), 0.0)
        assertEquals(30.0, result.analyzer.perSecondSamples[1], 0.0)
        assertEquals(0.0, result.analyzer.perSecondSamples.last(), 0.0)
        assertEquals(4, result.rates.getValue(PipelineMetrics.Stage.EVENT).count)
        assertEquals(0, result.rates.getValue(PipelineMetrics.Stage.PROCESSED).count)
        assertFalse(result.sustainedAnalyzerPass(false))
    }
    @Test fun sustainedGateIsAnalyzerNotStrideSelectedRate() {
        val metrics = PipelineMetrics(0, 60)
        repeat(60) { second ->
            repeat(30) { metrics.record(PipelineMetrics.Stage.ANALYZER, second * 1_000_000_000L) }
            repeat(8) { metrics.record(PipelineMetrics.Stage.SELECTED, second * 1_000_000_000L) }
        }
        val result = metrics.snapshot(60_000_000_000)
        assertTrue(result.sustainedAnalyzerPass(false))
        assertFalse(result.sustainedAnalyzerPass(true))
        assertEquals(8.0, result.rates.getValue(PipelineMetrics.Stage.SELECTED).meanFps, 0.0)
        assertFalse(metrics.snapshot(59_000_000_000).sustainedAnalyzerPass(false))
    }
    @Test fun timestampsOutsideHalfOpenRunAreNotCounted() {
        val metrics = PipelineMetrics(1_000_000_000, 60)
        metrics.record(PipelineMetrics.Stage.ANALYZER, 0)
        metrics.record(PipelineMetrics.Stage.ANALYZER, 61_000_000_000)
        assertEquals(0, metrics.snapshot(61_000_000_000).analyzer.count)
    }
    @Test fun parallelCountersAreThreadSafe() {
        val metrics = PipelineMetrics(0, 60)
        val threads = List(4) { Thread { repeat(1000) { metrics.record(PipelineMetrics.Stage.ANALYZER, 1) } } }
        threads.forEach { it.start() }
        threads.forEach { it.join() }
        assertEquals(4000, metrics.snapshot(60_000_000_000).analyzer.count)
    }
    @Test(expected = IllegalArgumentException::class) fun backwardsClockRejected() {
        PipelineMetrics(1, 60).snapshot(0)
    }
    @Test fun earlyStopIncomplete() {
        val snapshot = PipelineMetrics(0, 60).snapshot(500_000_000)
        assertFalse(snapshot.complete)
        assertEquals(0.5, snapshot.durationSeconds, 0.0)
    }
}
