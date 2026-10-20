package com.kumpas.kumpas_app

import android.content.Context

/** Acquisition only. Null native values are reserved for isolated host orchestration tests. */
internal interface ActivityResourceFactory {
    fun session(): OwnedNative<SessionManager>
    fun exporter(): DataExporter?
    /** Transfers a fresh helper. Injected factories must opt in; never fall back to default stores. */
    fun exportDatabase(): SessionDatabase = error("Export database acquisition not configured")
    fun benchmark(): OwnedNative<BenchmarkMode>
    fun vision(): OwnedNative<VisionEngine>
}

internal class AndroidActivityResourceFactory(
    private val context: Context,
    private val lock: Any,
    private val generation: () -> Long,
    private val onBenchmark: (String) -> Unit,
    private val onVision: (String) -> Unit,
) : ActivityResourceFactory {
    override fun session(): OwnedNative<SessionManager> {
        val value = SessionManager(context)
        return OwnedNative(value) { value.close() }
    }
    override fun exporter() = DataExporter(context)
    override fun exportDatabase() = SessionDatabase(context)
    override fun benchmark(): OwnedNative<BenchmarkMode> {
        val value = BenchmarkMode(context, onBenchmark)
        return OwnedNative(value) { if (value.isActive) value.finish(); Unit }
    }
    override fun vision(): OwnedNative<VisionEngine> {
        val value = VisionEngine(context, lock, generation, onResult = onVision)
        return OwnedNative(value) { value.close() }
    }
}
