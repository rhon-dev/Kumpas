package com.kumpas.kumpas_app

import org.junit.Assert.*
import org.junit.Test

class AttemptBoundaryTest {
    @Test fun invalidTargetCannotStart() {
        val boundary = AttemptBoundary(50)
        assertThrows(IllegalArgumentException::class.java) { boundary.start(-1) }
        assertThrows(IllegalArgumentException::class.java) { boundary.start(50) }
    }
    @Test fun resultCanBePersistedOnlyOnce() {
        val boundary = AttemptBoundary(50)
        val id = boundary.start(22)
        assertTrue(boundary.acceptTerminal(id))
        assertFalse(boundary.acceptTerminal(id))
        assertTrue(boundary.canDeliver(id))
        assertTrue(boundary.acknowledge(id))
        assertFalse(boundary.acknowledge(id))
    }
    @Test fun clearRejectsPendingResultAndDelivery() {
        val boundary = AttemptBoundary(50)
        val id = boundary.start(22)
        boundary.invalidate()
        assertFalse(boundary.acceptTerminal(id))
        assertFalse(boundary.canDeliver(id))
        assertFalse(boundary.acknowledge(id))
    }
    @Test fun newAttemptRejectsOldCallbackAndOldCancellation() {
        val boundary = AttemptBoundary(50)
        val old = boundary.start(22)
        val fresh = boundary.start(23)
        assertNotEquals(old, fresh)
        assertFalse(boundary.cancel(old))
        assertFalse(boundary.acceptTerminal(old))
        assertTrue(boundary.canDeliver(fresh))
        assertTrue(boundary.cancel(fresh))
        assertFalse(boundary.canDeliver(fresh))
    }
    @Test fun ackRequiresCompletedCurrentAttempt() {
        val boundary = AttemptBoundary(50)
        val id = boundary.start(22)
        assertFalse(boundary.acknowledge(id))
        assertTrue(boundary.acceptTerminal(id))
        boundary.invalidate()
        assertFalse(boundary.acknowledge(id))
    }
}
