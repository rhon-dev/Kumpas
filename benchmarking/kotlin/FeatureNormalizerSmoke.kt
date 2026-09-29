package com.kumpas.kumpas_app

/** Standalone smoke test when Android SDK is absent; JVM build only. */
fun main() {
    val f = FloatArray(258)
    for (i in 0 until 33) {
        f[i * 4] = 0.5f
        f[i * 4 + 1] = 0.5f
        f[i * 4 + 2] = 0.1f
        f[i * 4 + 3] = 1f
    }
    f[11 * 4 + 1] = 0.2f
    f[12 * 4 + 1] = 0.2f
    for (i in 195 until 258) f[i] = 0.6f
    FeatureNormalizer.normalize(f, true)
    check((132 until 195).all { f[it] == 0f })
    check(kotlin.math.abs(f[195] - 1f / 3f) < 1e-4f)
    check(f[11 * 4 + 3] == 1f)
    println("FeatureNormalizer smoke passed")
    println(f.joinToString(prefix = "[", postfix = "]", separator = ","))
}
