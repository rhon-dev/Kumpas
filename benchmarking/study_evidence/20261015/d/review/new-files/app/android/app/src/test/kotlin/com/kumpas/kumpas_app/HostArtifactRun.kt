package com.kumpas.kumpas_app

import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.nio.file.Files
import java.nio.file.LinkOption.NOFOLLOW_LINKS
import java.nio.file.StandardOpenOption.CREATE_NEW
import java.nio.file.StandardOpenOption.WRITE
import java.security.MessageDigest
import java.util.UUID

/** Versioned TEST handoff publisher, not a production benchmark schema or consumer. */
internal class HostArtifactRun(destination: File, private val sourceRoot: File) {
    companion object {
        const val SCHEMA = 1
        fun sha(bytes: ByteArray) = MessageDigest.getInstance("SHA-256").digest(bytes).joinToString("") { "%02x".format(it.toInt() and 255) }
        fun freshDestination(): File = System.getProperty("kumpas.hostFixtureDir")?.let(::File)
            ?: File(Files.createTempDirectory(File(checkNotNull(System.getenv("TMPDIR"))).toPath(), "host-handoff-").toFile(), "output")
        fun sourceRoot() = File(checkNotNull(System.getProperty("kumpas.hostSourceRoot")) { "Missing Gradle source root" })
    }
    val runId = UUID.randomUUID().toString()
    val root: File
    private val artifacts = linkedMapOf<String, JSONObject>()
    private val sourceHashes: Map<String, String>
    private var published = false
    init {
        require(destination.isAbsolute && destination.toPath().normalize() == destination.toPath()) { "Absolute normalized destination required" }
        var ancestor: File? = destination
        while (ancestor != null) { require(!Files.isSymbolicLink(ancestor.toPath())) { "Symlink destination" }; ancestor = ancestor.parentFile }
        require(destination.parentFile!!.isDirectory) { "Destination parent missing" }
        require(!Files.exists(destination.toPath(), NOFOLLOW_LINKS)) { "Refusing pre-existing destination" }
        require(destination.mkdir()) { "Cannot reserve destination" }
        root = File(destination, runId)
        check(root.mkdir())
        sourceHashes = sources()
    }
    private fun sources(): Map<String, String> {
        val inputs = listOf("app/android/app/src/main/kotlin", "app/android/app/src/test/kotlin").flatMap { directory ->
            val base = File(sourceRoot, directory)
            check(base.isDirectory) { "Missing source directory" }
            base.walkTopDown().filter { it.isFile && it.extension == "kt" }.toList()
        } + File(sourceRoot, "app/android/app/build.gradle.kts")
        check(inputs.isNotEmpty())
        return inputs.sortedBy { it.path }.associate { file ->
            check(file.canonicalPath.startsWith(sourceRoot.canonicalPath + File.separator))
            file.relativeTo(sourceRoot).invariantSeparatorsPath to sha(file.readBytes())
        }
    }
    fun write(name: String, bytes: ByteArray, kind: String, identity: String) {
        check(!published) { "Already published" }
        require(name.matches(Regex("[a-z0-9][a-z0-9.-]*")) && name !in setOf("manifest.json", "failure.log")) { "Invalid artifact path" }
        require(kind in setOf("study", "event", "export", "benchmark_report", "benchmark_control", "benchmark_index")) { "Invalid artifact kind" }
        require(identity == "study" || identity in setOf("confirmed", "unconfirmed", "faulted")) { "Invalid artifact identity" }
        require(!artifacts.containsKey(name)) { "Duplicate artifact" }
        val file = File(root, name)
        Files.write(file.toPath(), bytes, CREATE_NEW, WRITE)
        check(file.readBytes().contentEquals(bytes))
        artifacts[name] = JSONObject().put("path", name).put("sha256", sha(bytes)).put("bytes", bytes.size).put("kind", kind).put("identity", identity)
    }
    fun publish(required: Set<String>, scenarios: JSONObject): File {
        check(!published)
        require(required.isNotEmpty() && artifacts.keys == required) { "Missing or unexpected artifacts" }
        check(root.listFiles()!!.map { it.name }.toSet() == required) { "Unexpected output" }
        check(sources() == sourceHashes) { "Stale source snapshot" }
        artifacts.forEach { (name, record) ->
            val file = File(root, name)
            check(Files.isRegularFile(file.toPath(), NOFOLLOW_LINKS) && sha(file.readBytes()) == record.getString("sha256")) { "Missing or tampered artifact" }
        }
        val manifest = JSONObject().put("test_schema_version", SCHEMA).put("run_id", runId)
            .put("synthetic_origin", true).put("producer_outcome", "success")
            .put("transport", "host-native-callable-and-handler; later consumer transport is mocked")
            .put("source_hashes", JSONObject(sourceHashes)).put("source_hash_stage", "JVM runtime snapshot; runner independently compares before compile and after execution")
            .put("artifacts", JSONArray(artifacts.values.toList())).put("scenarios", scenarios)
        val file = File(root, "manifest.json")
        val bytes = manifest.toString(2).toByteArray(Charsets.UTF_8)
        Files.write(file.toPath(), bytes, CREATE_NEW, WRITE)
        check(file.readBytes().contentEquals(bytes))
        published = true
        return file
    }
    fun failure(error: Throwable) {
        if (!published) Files.write(File(root, "failure.log").toPath(), error.stackTraceToString().toByteArray(), CREATE_NEW, WRITE)
    }
}
