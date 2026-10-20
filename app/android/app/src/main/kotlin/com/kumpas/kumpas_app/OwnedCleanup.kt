package com.kumpas.kumpas_app

/** Attempt every owned cleanup action; retain first failure and all later ones. */
internal fun completeCleanup(actions: Iterable<() -> Unit>) {
    var failure: Throwable? = null
    for (action in actions) {
        try { action() } catch (error: Throwable) {
            if (failure == null) failure = error else if (failure !== error) failure.addSuppressed(error)
        }
    }
    failure?.let { throw it }
}
