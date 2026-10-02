package com.kumpas.kumpas_app

import java.util.UUID

/** Caller holds the shared pipeline/data lock for every operation. */
internal class AttemptBoundary(private val labelCount: Int) {
    var generation: Long = 0
        private set
    private var current: String? = null
    val currentId: String? get() = current
    private var terminal = false
    private var acknowledged = false

    fun start(target: Int): String {
        require(target in 0 until labelCount) { "Invalid target class" }
        generation++
        current = UUID.randomUUID().toString()
        terminal = false
        acknowledged = false
        return current!!
    }
    fun canDeliver(id: String): Boolean = id == current
    fun acceptTerminal(id: String): Boolean {
        if (id != current || terminal) return false
        terminal = true
        return true
    }
    fun acknowledge(id: String): Boolean {
        if (id != current || !terminal || acknowledged) return false
        acknowledged = true
        return true
    }
    fun cancel(id: String?): Boolean {
        if (id != null && id != current) return false
        invalidate()
        return true
    }
    fun invalidate() {
        generation++
        current = null
        terminal = false
        acknowledged = false
    }
}
