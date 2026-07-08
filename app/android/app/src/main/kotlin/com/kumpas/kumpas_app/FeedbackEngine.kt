package com.kumpas.kumpas_app

import kotlin.math.abs
import kotlin.math.acos
import kotlin.math.ln
import kotlin.math.min
import kotlin.math.sqrt

/**
 * Kotlin port of training/feedback/feedback_engine.py — DTW-based comparison
 * of a learner sequence against the class gold standard across four
 * dimensions: timing, motion, handshape, orientation.
 *
 * HIGH-RISK CODE (PRD §7, Feedback Algorithm Agent): every behavioural change
 * here must be mirrored in the Python reference and pass the parity unit test
 * (FeedbackEngineParityTest) built from real fixture sequences.
 *
 * Sequences are (T=30) frames of 258 floats (pose 33*4 + left hand 63 +
 * right hand 63), normalized as in build_sequences.py.
 */
object FeedbackEngine {

    const val SEQ_LEN = 30
    const val N_FEATURES = 258
    private const val L_WRIST_P = 15
    private const val R_WRIST_P = 16
    private const val LHAND0 = 132
    private const val RHAND0 = 132 + 63
    private const val WRIST_H = 0
    private const val INDEX_MCP = 5
    private const val PINKY_MCP = 17

    private val FINGERS = linkedMapOf(
        "thumb" to intArrayOf(1, 2, 3, 4),
        "index" to intArrayOf(5, 6, 7, 8),
        "middle" to intArrayOf(9, 10, 11, 12),
        "ring" to intArrayOf(13, 14, 15, 16),
        "pinky" to intArrayOf(17, 18, 19, 20),
    )

    private val THRESHOLDS = mapOf(
        "timing" to 0.30, "motion" to 0.25, "handshape" to 0.22, "orientation" to 0.25
    )

    data class FeedbackItem(
        val dimension: String, val severity: Double, val hand: String, val prompt: String
    )

    data class FeedbackReport(
        val targetLabel: String, val overallMatch: Double, val items: List<FeedbackItem>
    )

    // ---- geometry helpers ----

    private fun poseXyz(seq: Array<FloatArray>, t: Int, lm: Int) =
        doubleArrayOf(seq[t][lm * 4].toDouble(), seq[t][lm * 4 + 1].toDouble(),
                      seq[t][lm * 4 + 2].toDouble())

    private fun handPoint(seq: Array<FloatArray>, t: Int, base: Int, i: Int) =
        doubleArrayOf(seq[t][base + i * 3].toDouble(), seq[t][base + i * 3 + 1].toDouble(),
                      seq[t][base + i * 3 + 2].toDouble())

    private fun handPresent(seq: Array<FloatArray>, t: Int, base: Int): Boolean {
        for (i in 0 until 63) if (seq[t][base + i] != 0f) return true
        return false
    }

    /** 6-dim wrist trajectory frame: left wrist xyz + right wrist xyz. */
    private fun wristFrame(seq: Array<FloatArray>, t: Int): DoubleArray {
        val l = poseXyz(seq, t, L_WRIST_P); val r = poseXyz(seq, t, R_WRIST_P)
        return doubleArrayOf(l[0], l[1], l[2], r[0], r[1], r[2])
    }

    private fun dist(a: DoubleArray, b: DoubleArray): Double {
        var s = 0.0
        for (i in a.indices) { val d = a[i] - b[i]; s += d * d }
        return sqrt(s)
    }

    // ---- DTW (mirrors dtw_path in the Python reference, including tie-break order) ----

    fun dtwPath(a: List<DoubleArray>, b: List<DoubleArray>): List<Pair<Int, Int>> {
        val n = a.size; val m = b.size
        val acc = Array(n + 1) { DoubleArray(m + 1) { Double.POSITIVE_INFINITY } }
        acc[0][0] = 0.0
        for (i in 1..n) for (j in 1..m) {
            acc[i][j] = dist(a[i - 1], b[j - 1]) +
                minOf(acc[i - 1][j], acc[i][j - 1], acc[i - 1][j - 1])
        }
        val path = ArrayList<Pair<Int, Int>>()
        var i = n; var j = m
        while (i > 0 && j > 0) {
            path.add(Pair(i - 1, j - 1))
            // argmin over [diag, up, left] with first-wins ties — same as np.argmin
            val diag = acc[i - 1][j - 1]; val up = acc[i - 1][j]; val left = acc[i][j - 1]
            when {
                diag <= up && diag <= left -> { i--; j-- }
                up <= left -> i--
                else -> j--
            }
        }
        path.reverse()
        return path
    }

    // ---- dimension scores (each mirrors its Python counterpart) ----

    private fun timingScore(path: List<Pair<Int, Int>>): Pair<Double, String> {
        var li = 0.0; var gi = 0.0
        for (k in 1 until path.size) {
            val gStep = path[k].second - path[k - 1].second
            if (gStep > 0) { li += path[k].first - path[k - 1].first; gi += gStep }
        }
        if (li == 0.0 || gi == 0.0) return Pair(1.0, "faster")
        val ratio = li / gi
        val score = min(abs(ln(ratio) / ln(2.0)), 1.0)
        return Pair(score, if (ratio > 1) "slower" else "faster")
    }

    private fun motionScore(
        learner: Array<FloatArray>, gold: Array<FloatArray>, path: List<Pair<Int, Int>>
    ): Triple<Double, String, String> {
        var err = 0.0
        val meanDiff = DoubleArray(6)
        for ((i, j) in path) {
            val lw = wristFrame(learner, i); val gw = wristFrame(gold, j)
            var s = 0.0
            for (k in 0 until 6) { val d = lw[k] - gw[k]; s += d * d; meanDiff[k] += d }
            err += sqrt(s)
        }
        err /= path.size
        for (k in 0 until 6) meanDiff[k] /= path.size
        val normL = sqrt(meanDiff[0] * meanDiff[0] + meanDiff[1] * meanDiff[1] + meanDiff[2] * meanDiff[2])
        val normR = sqrt(meanDiff[3] * meanDiff[3] + meanDiff[4] * meanDiff[4] + meanDiff[5] * meanDiff[5])
        val hand = if (normR >= normL) "right" else "left"
        val d = if (hand == "right") meanDiff.copyOfRange(3, 6) else meanDiff.copyOfRange(0, 3)
        val dirs = ArrayList<String>()
        if (abs(d[0]) > 0.05) dirs.add(if (d[0] > 0) "left" else "right")
        if (abs(d[1]) > 0.05) dirs.add(if (d[1] > 0) "higher" else "lower")
        val direction = if (dirs.isEmpty()) "closer to the model path" else dirs.joinToString(" and ")
        return Triple(min(err / 0.8, 1.0), hand, direction)
    }

    private fun handshapeScore(
        learner: Array<FloatArray>, gold: Array<FloatArray>,
        path: List<Pair<Int, Int>>, base: Int
    ): Pair<Double, List<String>> {
        val pairs = path.filter { (i, j) -> handPresent(learner, i, base) && handPresent(gold, j, base) }
        if (pairs.isEmpty()) {
            val goldUses = (0 until gold.size).any { handPresent(gold, it, base) }
            val learnerUses = (0 until learner.size).any { handPresent(learner, it, base) }
            return if (goldUses && !learnerUses) Pair(1.0, listOf("hand not detected"))
            else Pair(0.0, emptyList())
        }
        val fingerErr = LinkedHashMap<String, Double>()
        for ((name, ids) in FINGERS) {
            var e = 0.0
            for ((i, j) in pairs) {
                val lw = handPoint(learner, i, base, WRIST_H)
                val gw = handPoint(gold, j, base, WRIST_H)
                var fe = 0.0
                for (id in ids) {
                    val lp = handPoint(learner, i, base, id)
                    val gp = handPoint(gold, j, base, id)
                    var s = 0.0
                    for (k in 0 until 3) {
                        val d = (lp[k] - lw[k]) - (gp[k] - gw[k]); s += d * d
                    }
                    fe += sqrt(s)
                }
                e += fe / ids.size
            }
            fingerErr[name] = e / pairs.size
        }
        val worst = fingerErr.entries.sortedByDescending { it.value }
        val score = min(worst[0].value / 0.30, 1.0)
        val fingers = worst.filter { it.value > 0.6 * worst[0].value }.take(2).map { it.key }
        return Pair(score, fingers)
    }

    private fun orientationScore(
        learner: Array<FloatArray>, gold: Array<FloatArray>,
        path: List<Pair<Int, Int>>, base: Int
    ): Double {
        val pairs = path.filter { (i, j) -> handPresent(learner, i, base) && handPresent(gold, j, base) }
        if (pairs.isEmpty()) return 0.0

        fun normal(seq: Array<FloatArray>, t: Int): DoubleArray {
            val w = handPoint(seq, t, base, WRIST_H)
            val im = handPoint(seq, t, base, INDEX_MCP)
            val pm = handPoint(seq, t, base, PINKY_MCP)
            val v1 = doubleArrayOf(im[0] - w[0], im[1] - w[1], im[2] - w[2])
            val v2 = doubleArrayOf(pm[0] - w[0], pm[1] - w[1], pm[2] - w[2])
            val n = doubleArrayOf(
                v1[1] * v2[2] - v1[2] * v2[1],
                v1[2] * v2[0] - v1[0] * v2[2],
                v1[0] * v2[1] - v1[1] * v2[0])
            val len = sqrt(n[0] * n[0] + n[1] * n[1] + n[2] * n[2]) + 1e-8
            return doubleArrayOf(n[0] / len, n[1] / len, n[2] / len)
        }

        var sum = 0.0
        for ((i, j) in pairs) {
            val a = normal(learner, i); val b = normal(gold, j)
            var dot = a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
            dot = dot.coerceIn(-1.0, 1.0)
            sum += Math.toDegrees(acos(dot))
        }
        return min(sum / pairs.size / 90.0, 1.0)
    }

    // ---- public API ----

    fun compare(
        learner: Array<FloatArray>, gold: Array<FloatArray>, targetLabel: String
    ): FeedbackReport {
        val lTraj = (0 until learner.size).map { wristFrame(learner, it) }
        val gTraj = (0 until gold.size).map { wristFrame(gold, it) }
        val path = dtwPath(lTraj, gTraj)
        val items = ArrayList<FeedbackItem>()

        val (tScore, tempo) = timingScore(path)
        if (tScore > THRESHOLDS["timing"]!!) {
            items.add(FeedbackItem("timing", round3(tScore), "both",
                "Your sign is $tempo than the model — " +
                    (if (tempo == "faster") "take your time." else "keep the movement flowing.")))
        }

        val (mScore, mHand, mDir) = motionScore(learner, gold, path)
        if (mScore > THRESHOLDS["motion"]!!) {
            items.add(FeedbackItem("motion", round3(mScore), mHand, "Move your $mHand hand $mDir."))
        }

        for ((hand, base) in listOf("left" to LHAND0, "right" to RHAND0)) {
            val (hScore, worst) = handshapeScore(learner, gold, path, base)
            if (hScore > THRESHOLDS["handshape"]!!) {
                if (worst == listOf("hand not detected")) {
                    items.add(FeedbackItem("handshape", 1.0, hand,
                        "This sign uses your $hand hand — keep it visible to the camera."))
                } else {
                    items.add(FeedbackItem("handshape", round3(hScore), hand,
                        "Check your $hand-hand shape — adjust your ${worst.joinToString(" and ")} " +
                            "finger${if (worst.size > 1) "s" else ""}."))
                }
            }
            val oScore = orientationScore(learner, gold, path, base)
            if (oScore > THRESHOLDS["orientation"]!!) {
                items.add(FeedbackItem("orientation", round3(oScore), hand,
                    "Rotate your $hand palm to match the model orientation."))
            }
        }

        items.sortByDescending { it.severity }
        val mean = if (items.isEmpty()) 0.0 else items.sumOf { it.severity } / items.size
        return FeedbackReport(targetLabel, round3(1.0 - mean), items)
    }

    private fun round3(v: Double) = Math.round(v * 1000.0) / 1000.0
}
