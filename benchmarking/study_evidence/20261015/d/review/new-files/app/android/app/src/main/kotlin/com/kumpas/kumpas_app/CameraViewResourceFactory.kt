package com.kumpas.kumpas_app

import android.content.Context
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import com.google.common.util.concurrent.ListenableFuture
import java.util.concurrent.Executor
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

/** Acquisition seams only; production CameraX options and scheduling stay unchanged. */
interface CameraViewResourceFactory {
    fun preview(context: Context): PreviewView
    fun executor(): ExecutorService
    fun provider(context: Context): ListenableFuture<ProcessCameraProvider>
    fun listen(future: ListenableFuture<ProcessCameraProvider>, callback: Runnable, executor: Executor)
}
internal object AndroidCameraViewResourceFactory : CameraViewResourceFactory {
    override fun preview(context: Context) = PreviewView(context).apply {
        implementationMode = PreviewView.ImplementationMode.COMPATIBLE
    }
    override fun executor(): ExecutorService = Executors.newSingleThreadExecutor()
    override fun provider(context: Context) = ProcessCameraProvider.getInstance(context)
    override fun listen(future: ListenableFuture<ProcessCameraProvider>, callback: Runnable, executor: Executor) =
        future.addListener(callback, executor)
}
