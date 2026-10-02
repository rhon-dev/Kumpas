package com.kumpas.kumpas_app

import java.nio.ByteBuffer

internal object RgbaFramePacking {
    fun pack(width: Int, height: Int, rowStride: Int, pixelStride: Int, plane: ByteBuffer): ByteBuffer {
        require(width > 0 && height > 0 && pixelStride >= 4 && rowStride >= width * pixelStride)
        require((height - 1L) * rowStride + (width - 1L) * pixelStride + 4 <= plane.limit()) {
            "Truncated RGBA plane"
        }
        val source = plane.duplicate()
        val packed = ByteBuffer.allocate(Math.multiplyExact(Math.multiplyExact(width, height), 4))
        if (pixelStride == 4) {
            val row = ByteArray(width * 4)
            for (y in 0 until height) {
                source.position(y * rowStride)
                source.get(row)
                packed.put(row)
            }
        } else {
            for (y in 0 until height) {
                for (x in 0 until width) {
                    source.position(y * rowStride + x * pixelStride)
                    repeat(4) { packed.put(source.get()) }
                }
            }
        }
        packed.flip()
        return packed
    }
}
