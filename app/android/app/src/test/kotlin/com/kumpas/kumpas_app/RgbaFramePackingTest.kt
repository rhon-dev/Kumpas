package com.kumpas.kumpas_app

import java.nio.ByteBuffer
import org.junit.Assert.*
import org.junit.Test

class RgbaFramePackingTest {
    @Test fun paddingDoesNotBecomePixels() {
        val bytes = byteArrayOf(1,2,3,4, 5,6,7,8, 99,99,99,99, 9,10,11,12, 13,14,15,16)
        val packed = RgbaFramePacking.pack(2, 2, 12, 4, ByteBuffer.wrap(bytes))
        val actual = ByteArray(packed.remaining())
        packed.get(actual)
        assertArrayEquals(byteArrayOf(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16), actual)
    }
    @Test fun originalBufferPositionIsPreserved() {
        val buffer = ByteBuffer.wrap(byteArrayOf(1,2,3,4))
        RgbaFramePacking.pack(1,1,4,4,buffer)
        assertEquals(0,buffer.position())
    }
    @Test fun truncatedPlaneFailsInsteadOfReadingPadding() {
        assertThrows(IllegalArgumentException::class.java) {
            RgbaFramePacking.pack(2,2,12,4,ByteBuffer.allocate(19))
        }
    }
}
