package com.kumpas.kumpas_app

import android.content.Context
import android.content.ContextWrapper
import android.content.SharedPreferences
import android.database.DatabaseErrorHandler
import android.database.sqlite.SQLiteDatabase
import io.flutter.plugin.common.EventChannel
import org.robolectric.RuntimeEnvironment
import java.io.ByteArrayInputStream
import java.io.File
import java.nio.file.Files
import java.util.UUID

/** Real isolated SQLite/preferences/files; fake native handles, no camera or inference. */
internal class HostStudyFixture : AutoCloseable {
    val root: File = Files.createTempDirectory(File(checkNotNull(System.getenv("TMPDIR"))).toPath(), "host-study-").toFile()
    val namespace = "host_study_${UUID.randomUUID()}"
    val external = child("external")
    val internal = child("internal")
    val preferences = child("preferences")
    var externalAvailable = true
    var failExport = false
    val helpers = mutableListOf<SessionDatabase>()
    val opened = mutableListOf<SQLiteDatabase>()
    private val prefs = mutableMapOf<String, SharedPreferences>()
    private val managers = mutableListOf<SessionManager>()
    private val engines = mutableListOf<VisionEngine>()
    private val benchmarks = mutableListOf<BenchmarkMode>()
    private var disposed = false
    val events = mutableListOf<String>()
    val activity = MainActivity()
    val owner = MainActivity.Initialization()
    var exportAcquisitions = 0
    private fun child(name: String): File = File(root, name).apply { check(mkdirs()); contained(this) }
    fun contained(file: File): File {
        check(file.canonicalPath.startsWith(root.canonicalPath + File.separator)) { "Fixture path escaped root" }
        check(file.absoluteFile.toPath().normalize() == file.canonicalFile.toPath()) { "Fixture symlink" }
        return file
    }
    val context = object : ContextWrapper(RuntimeEnvironment.getApplication()) {
        override fun getApplicationContext(): Context = this
        override fun getFilesDir() = internal
        override fun getExternalFilesDir(type: String?): File? = if (externalAvailable) external else null
        override fun getExternalFilesDirs(type: String?): Array<File> = if (externalAvailable) arrayOf(external) else emptyArray()
        override fun getDatabasePath(name: String): File {
            require(name.matches(Regex("[A-Za-z0-9_.-]+")))
            return contained(File(root, "databases/$name")).apply { parentFile!!.mkdirs() }
        }
        override fun openOrCreateDatabase(name: String, mode: Int, factory: SQLiteDatabase.CursorFactory?): SQLiteDatabase =
            openOrCreateDatabase(name, mode, factory, null)
        override fun openOrCreateDatabase(name: String, mode: Int, factory: SQLiteDatabase.CursorFactory?, handler: DatabaseErrorHandler?): SQLiteDatabase =
            SQLiteDatabase.openDatabase(getDatabasePath(name).path, factory, SQLiteDatabase.CREATE_IF_NECESSARY, handler).also { opened.add(it) }
        override fun deleteDatabase(name: String) = SQLiteDatabase.deleteDatabase(getDatabasePath(name))
        override fun getSharedPreferences(name: String, mode: Int): SharedPreferences = prefs.getOrPut(name) {
            require(name.matches(Regex("[A-Za-z0-9_.-]+")))
            // Actual Android preference implementation, explicitly file-scoped. No application preference API.
            val constructor = Class.forName("android.app.SharedPreferencesImpl").getDeclaredConstructor(File::class.java, Int::class.javaPrimitiveType)
            constructor.isAccessible = true
            constructor.newInstance(contained(File(preferences, "${namespace}_$name.xml")), mode) as SharedPreferences
        }
    }
    fun database(): SessionDatabase = SessionDatabase(context).also { helpers.add(it); opened.add(it.writableDatabase) }
    fun manager(): SessionManager = SessionManager(context) { database() }.also { managers.add(it) }
    val factory = object : ActivityResourceFactory {
        override fun session(): OwnedNative<SessionManager> { val value = manager(); return OwnedNative(value) { value.close() } }
        override fun exporter() = DataExporter(context, object : ExportPublication() {
            override fun open(file: File): java.io.OutputStream {
                if (failExport) throw java.io.IOException("synthetic export fault")
                return super.open(file)
            }
        })
        override fun benchmark(): OwnedNative<BenchmarkMode> {
            val value = BenchmarkMode(context).also { benchmarks.add(it) }
            return OwnedNative(value) { if (value.isActive) value.finish(); Unit }
        }
        override fun vision(): OwnedNative<VisionEngine> {
            val value = VisionEngine(context, resourceFactory = object : VisionResourceFactory {
                override fun pose() = OwnedNative<com.google.mediapipe.tasks.vision.poselandmarker.PoseLandmarker>(null) {}
                override fun hand() = OwnedNative<com.google.mediapipe.tasks.vision.handlandmarker.HandLandmarker>(null) {}
                override fun interpreter(model: java.nio.ByteBuffer) = OwnedNative<org.tensorflow.lite.Interpreter>(null) {}
                override fun asset(name: String) = ByteArrayInputStream(if (name.endsWith("json")) "{\"0\":{\"label\":\"SYNTHETIC\"}}".toByteArray() else byteArrayOf(1))
            }, onResult = {}).also { engines.add(it) }
            return OwnedNative(value) { value.close() }
        }
        override fun exportDatabase(): SessionDatabase { exportAcquisitions++; return database() }
    }
    fun initialize() = activity.initializeResources(factory, owner) {
        MainActivity::class.java.getDeclaredField("eventSink").apply { isAccessible = true }.set(activity, object : EventChannel.EventSink {
            override fun success(event: Any?) { events.add(event as String) }
            override fun error(code: String, message: String?, details: Any?) { error("Unexpected event error: $code") }
            override fun endOfStream() {}
        })
    }
    fun reloadPreferences() { prefs.clear() } // next manager reads committed isolated XML through a new real prefs instance
    fun closeOwners() = completeCleanup(listOf<() -> Unit>({
        val current = MainActivity::class.java.getDeclaredField("initialization").apply { isAccessible = true }.get(activity)
        if (current != null) {
            try {
                MainActivity::class.java.getDeclaredMethod("releaseInitialization", MainActivity.Initialization::class.java, Throwable::class.java)
                    .apply { isAccessible = true }.invoke(activity, current, null)
            } catch (wrapped: java.lang.reflect.InvocationTargetException) { throw wrapped.targetException }
        }
    }) + managers.map { manager -> { manager.close() } } + engines.map { engine -> { engine.close() } } +
        benchmarks.map { benchmark -> { if (benchmark.isActive) benchmark.finish(); Unit } } + helpers.map { helper -> { helper.close() } })
    override fun close() {
        if (disposed) return
        disposed = true
        completeCleanup(listOf<() -> Unit>({ closeOwners() }) + opened.map { database -> { if (database.isOpen) database.close() } } +
            prefs.values.map { preferences -> { check(preferences.edit().clear().commit()) } } + listOf({ check(root.deleteRecursively()) }))
    }
}
