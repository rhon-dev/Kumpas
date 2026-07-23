package com.kumpas.kumpas_app.benchmark

import android.os.SystemClock
import android.util.Log
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import org.json.JSONObject
import org.junit.After
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.tensorflow.lite.Interpreter
import java.nio.ByteBuffer
import java.nio.ByteOrder

/**
 * Instrumented latency benchmark for the Kumpas TFLite CNN-LSTM model.
 *
 * Runs N=100 inferences of a 30×258 input (matching the live pipeline shape)
 * and reports timing statistics (mean, median/p50, p95, max) plus cold-start.
 *
 * Results are logged to logcat with tag "KumpasBenchmark" and marker
 * "BENCHMARK_RESULT" so the host script (collect_latency.py) can parse them.
 *
 * Run:
 *   ./gradlew :app:connectedAndroidTest -Pandroid.testInstrumentationRunnerArguments.class=com.kumpas.kumpas_app.benchmark.LatencyBenchmarkTest
 */
@RunWith(AndroidJUnit4::class)
class LatencyBenchmarkTest {

    companion object {
        private const val TAG = "KumpasBenchmark"
        private const val MODEL_ASSET = "kumpas_50sign.tflite"
        private const val SEQ_LEN = 30
        private const val N_FEATURES = 258
        private const val N_INFERENCES = 100
        private const val LATENCY_GATE_P95_MS = 150.0
    }

    private lateinit var interpreter: Interpreter

    @Before
    fun setup() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val modelBytes = context.assets.open(MODEL_ASSET).readBytes()
        val bb = ByteBuffer.allocateDirect(modelBytes.size).order(ByteOrder.nativeOrder())
        bb.put(modelBytes)
        bb.rewind()
        interpreter = Interpreter(bb, Interpreter.Options().apply { numThreads = 2 })
    }

    @After
    fun teardown() {
        interpreter.close()
    }

    @Test
    fun benchmarkInferenceLatency() {
        // Prepare a sample input (random values — we're measuring speed, not accuracy)
        val input = Array(1) { Array(SEQ_LEN) { FloatArray(N_FEATURES) { Math.random().toFloat() } } }
        val numLabels = interpreter.getOutputTensor(0).shape()[1]
        val output = Array(1) { FloatArray(numLabels) }

        // Cold start: first inference after model load
        val coldStart = SystemClock.elapsedRealtime()
        interpreter.run(input, output)
        val coldStartMs = SystemClock.elapsedRealtime() - coldStart

        // Warm inferences
        val times = mutableListOf<Long>()
        for (i in 0 until N_INFERENCES) {
            val t0 = SystemClock.elapsedRealtime()
            interpreter.run(input, output)
            times.add(SystemClock.elapsedRealtime() - t0)
        }

        times.sort()
        val mean = times.average()
        val median = times[times.size / 2].toDouble()
        val p50 = median
        val p95 = times[(times.size * 0.95).toInt()].toDouble()
        val max = times.last().toDouble()
        val min = times.first().toDouble()

        val result = JSONObject().apply {
            put("n_inferences", N_INFERENCES)
            put("cold_start_ms", coldStartMs)
            put("mean_ms", String.format("%.2f", mean).toDouble())
            put("median_ms", String.format("%.2f", median).toDouble())
            put("p50_ms", String.format("%.2f", p50).toDouble())
            put("p95_ms", String.format("%.2f", p95).toDouble())
            put("max_ms", max)
            put("min_ms", min)
            put("model", MODEL_ASSET)
            put("seq_len", SEQ_LEN)
            put("n_features", N_FEATURES)
            put("num_threads", 2)
        }

        // Log with parseable marker
        Log.i(TAG, "BENCHMARK_RESULT ${result}")

        // Also log human-readable summary
        Log.i(TAG, "=== Latency Benchmark ===")
        Log.i(TAG, "Cold start: ${coldStartMs}ms")
        Log.i(TAG, "Warm (N=$N_INFERENCES): mean=%.2fms, p50=%.2fms, p95=%.2fms, max=%.0fms".format(mean, p50, p95, max))
        Log.i(TAG, "Gate: p95 <${LATENCY_GATE_P95_MS}ms -> ${if (p95 < LATENCY_GATE_P95_MS) "PASS" else "FAIL"}")

        // Assert gate
        assertTrue(
            "Inference latency p95 (${p95}ms) exceeds gate (${LATENCY_GATE_P95_MS}ms)",
            p95 < LATENCY_GATE_P95_MS
        )
    }
}
