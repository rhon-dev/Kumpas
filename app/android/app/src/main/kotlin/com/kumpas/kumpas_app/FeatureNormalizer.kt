package com.kumpas.kumpas_app

/** The exact live-path 258D mid-hip/torso normalization, independent of CV detectors. */
object FeatureNormalizer {
    private const val L_SHOULDER = 11
    private const val R_SHOULDER = 12
    private const val L_HIP = 23
    private const val R_HIP = 24

    fun normalize(f: FloatArray, poseSeen: Boolean) {
        require(f.size == 258) { "Expected 258 pose/hand features, got ${f.size}" }
        if (!poseSeen) return
        val rootX = (f[L_HIP * 4] + f[R_HIP * 4]) / 2f
        val rootY = (f[L_HIP * 4 + 1] + f[R_HIP * 4 + 1]) / 2f
        val rootZ = (f[L_HIP * 4 + 2] + f[R_HIP * 4 + 2]) / 2f
        val neckX = (f[L_SHOULDER * 4] + f[R_SHOULDER * 4]) / 2f
        val neckY = (f[L_SHOULDER * 4 + 1] + f[R_SHOULDER * 4 + 1]) / 2f
        val neckZ = (f[L_SHOULDER * 4 + 2] + f[R_SHOULDER * 4 + 2]) / 2f
        var scale = kotlin.math.sqrt(
            (neckX - rootX) * (neckX - rootX) + (neckY - rootY) * (neckY - rootY) +
                (neckZ - rootZ) * (neckZ - rootZ)
        )
        if (scale < 1e-4f) scale = 1f
        for (i in 0 until 33) {
            f[i * 4] = (f[i * 4] - rootX) / scale
            f[i * 4 + 1] = (f[i * 4 + 1] - rootY) / scale
            f[i * 4 + 2] = (f[i * 4 + 2] - rootZ) / scale
        }
        for (handBase in intArrayOf(132, 195)) {
            var zero = true
            for (i in 0 until 63) if (f[handBase + i] != 0f) { zero = false; break }
            if (zero) continue
            for (i in 0 until 21) {
                f[handBase + i * 3] = (f[handBase + i * 3] - rootX) / scale
                f[handBase + i * 3 + 1] = (f[handBase + i * 3 + 1] - rootY) / scale
                f[handBase + i * 3 + 2] = (f[handBase + i * 3 + 2] - rootZ) / scale
            }
        }
    }
}
