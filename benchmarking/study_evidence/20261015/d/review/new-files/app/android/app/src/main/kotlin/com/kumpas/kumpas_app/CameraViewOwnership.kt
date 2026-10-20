package com.kumpas.kumpas_app

/** View identity is separate from capture generation. All shared side effects
 * execute under the pipeline lock, including the final async callback boundary. */
class CameraViewOwnership(private val lock: Any, private val onCurrentRelease: () -> Unit) {
    private var next = 0L
    private var current: Long? = null
    fun isCurrent(token: Long): Boolean = synchronized(lock) { current == token }
    fun register(): Long = synchronized(lock) { (++next).also { current = it } }
    fun run(token: Long, action: () -> Unit): Boolean = synchronized(lock) {
        if (current != token) return@synchronized false
        action()
        true
    }
    fun release(token: Long, clearCamera: () -> Unit) = synchronized(lock) {
        if (current == token) {
            current = null
            completeCleanup(listOf(clearCamera, onCurrentRelease))
        }
    }
}
