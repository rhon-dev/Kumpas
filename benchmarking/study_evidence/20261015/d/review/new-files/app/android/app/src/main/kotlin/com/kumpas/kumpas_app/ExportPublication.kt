package com.kumpas.kumpas_app

import java.io.File
import java.io.OutputStream

/** Narrow I/O seam for exercising real export failures with synthetic files. */
internal open class ExportPublication {
    open fun open(file: File): OutputStream = file.outputStream()
    open fun publish(staging: File, destination: File) {
        if (!staging.renameTo(destination)) throw java.io.IOException("Export publication failed")
    }
    open fun read(file: File): ByteArray = file.readBytes()
}
