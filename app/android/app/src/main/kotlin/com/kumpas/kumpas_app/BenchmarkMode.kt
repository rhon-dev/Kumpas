package com.kumpas.kumpas_app

import android.content.Context
import android.os.Environment
import android.os.SystemClock
import android.util.Log
import org.json.JSONObject
import java.io.File

/**
 * FPS Benchmark mode for the Kumpas vision pipeline.
 *
 * When active, tracks per-frame timestamps over a configurable duration
 * and writes a structured JSON report to device storage for collection
 * by the host script (benchmarking/collect_fps.py).
 *
 * Activated via the "startBenchmark" method channel call from Flutter.
 */
class BenchmarkMode(private val context: Context) {

    companion object {
        private const val TAG = "KumpasBenchmark"
        private const val DEFAULT_DURATION_S = 60
        private const val DEGRADATION_THRESHOLD_FPS = 24.0
        private const val DEGRADATION_WINDOW_MS = 2000L
        private const val OUTPUT_FILE = "kumpas_fps_benchmark.json"
    }

    var isActive = false
        private set

    private var durationMs = DEFAULT_DURATION_S * 1000L
    private var startTime = 0L
    private val frameTimestamps = mutableListOf<Long>()

    /**
     * Start the benchmark for the given duration (seconds).
     */
    fun start(durationSeconds: Int = DEFAULT_DURATION_S) {
        frameTimestamps.clear()
        durationMs = durationSeconds * 1000L
        startTime = SystemClock.elapsedRealtime()
        isActive = true
        Log.i(TAG, "Benchmark started: ${durationSeconds}s")
    }

    /**
     * Record a frame tick. Call this on every processed frame.
     * Returns true when the benchmark window has elapsed and results are ready.
     */
    fun recordFrame(): Boolean {
        if (!isActive) return false
        val now = SystemClock.elapsedRealtime()
        frameTimestamps.add(now)
        return (now - startTime) >= durationMs
    }

    /**
     * Finalize the benchmark, compute metrics, write results to file.
     * Returns the results JSON string.
     */
    fun finish(): String {
        isActive = false
        val elapsed = if (frameTimestamps.isNotEmpty()) {
            (frameTimestamps.last() - frameTimestamps.first()).toDouble() / 1000.0
        } else 0.0

        val results = computeMetrics()
        val json = results.toString(2)

        // Write to Downloads for adb pull
        val outDir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS)
        outDir.mkdirs()
        val outFile = File(outDir, OUTPUT_FILE)
        outFile.writeText(json)
        Log.i(TAG, "Benchmark complete: ${outFile.absolutePath}")
        Log.i(TAG, "BENCHMARK_FPS_RESULT $results")

        frameTimestamps.clear()
        return json
    }

    private fun computeMetrics(): JSONObject {
        val n = frameTimestamps.size
        if (n < 2) {
            return JSONObject().apply {
                put("error", "Insufficient frames recorded")
                put("frame_count", n)
            }
        }

        val durationS = (frameTimestamps.last() - frameTimestamps.first()).toDouble() / 1000.0
        val overallFps = (n - 1).toDouble() / durationS

        // Per-second FPS calculation
        val perSecondFps = mutableListOf<Double>()
        var windowStart = 0
        for (i in 1 until n) {
            val elapsed = frameTimestamps[i] - frameTimestamps[windowStart]
            if (elapsed >= 1000) {
                perSecondFps.add((i - windowStart).toDouble() * 1000.0 / elapsed)
                windowStart = i
            }
        }

        val meanFps = if (perSecondFps.isNotEmpty()) perSecondFps.average() else overallFps
        val sortedFps = perSecondFps.sorted()
        val minFps = sortedFps.firstOrNull() ?: overallFps
        val maxFps = sortedFps.lastOrNull() ?: overallFps
        val p5Fps = if (sortedFps.size > 20) sortedFps[(sortedFps.size * 0.05).toInt()] else minFps
        val stddev = if (perSecondFps.size > 1) {
            val mean = perSecondFps.average()
            kotlin.math.sqrt(perSecondFps.sumOf { (it - mean) * (it - mean) } / (perSecondFps.size - 1))
        } else 0.0

        // Degradation detection: FPS below threshold for >2 consecutive seconds
        val degradationDetected = detectDegradation()

        return JSONObject().apply {
            put("duration_s", String.format("%.1f", durationS).toDouble())
            put("frame_count", n)
            put("mean_fps", String.format("%.2f", meanFps).toDouble())
            put("min_fps", String.format("%.2f", minFps).toDouble())
            put("max_fps", String.format("%.2f", maxFps).toDouble())
            put("p5_fps", String.format("%.2f", p5Fps).toDouble())
            put("stddev_fps", String.format("%.3f", stddev).toDouble())
            put("degradation_detected", degradationDetected)
            put("per_second_samples", perSecondFps.size)
        }
    }

    /**
     * Detect if FPS dropped below 24 for >2 consecutive seconds.
     */
    private fun detectDegradation(): Boolean {
        if (frameTimestamps.size < 10) return false

        var lowStart: Long? = null
        var windowFrameStart = 0

        for (i in 1 until frameTimestamps.size) {
            val elapsed = frameTimestamps[i] - frameTimestamps[windowFrameStart]
            if (elapsed >= 1000) {
                val fps = (i - windowFrameStart).toDouble() * 1000.0 / elapsed
                if (fps < DEGRADATION_THRESHOLD_FPS) {
                    if (lowStart == null) lowStart = frameTimestamps[windowFrameStart]
                    if (frameTimestamps[i] - lowStart >= DEGRADATION_WINDOW_MS) {
                        return true
                    }
                } else {
                    lowStart = null
                }
                windowFrameStart = i
            }
        }
        return false
    }
}
