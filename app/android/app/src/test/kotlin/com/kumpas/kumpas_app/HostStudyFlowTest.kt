package com.kumpas.kumpas_app

import io.flutter.plugin.common.MethodCall
import io.flutter.plugin.common.MethodChannel
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class HostStudyFlowTest {
    private fun handler(activity: MainActivity, owner: MainActivity.Initialization): MethodChannel.MethodCallHandler {
        return activity.controlHandler(owner)
    }
    private class Reply : MethodChannel.Result {
        var code: String? = null
        var message: String? = null
        var value: Any? = null
        var replies = 0
        override fun success(result: Any?) { replies++; value = result }
        override fun error(errorCode: String, message: String?, details: Any?) { replies++; code = errorCode; this.message = message }
        override fun notImplemented() { replies++; code = "NOT_IMPLEMENTED" }
    }
    @Test fun actualControlExportUsesOnlyExplicitFixtureDatabaseAndClosesTemporaryHelper() {
        HostStudyFixture().use { fixture ->
            fixture.initialize()
            val control = handler(fixture.activity, fixture.owner)
            val assessment = Reply()
            control.onMethodCall(MethodCall("saveAssessment", mapOf("type" to "pre", "responses" to "{\"synthetic\":true}")), assessment)
            assertNull(assessment.code)
            val reply = Reply()
            control.onMethodCall(MethodCall("exportData", null), reply)
            assertNull("Export must acquire the fixture helper, never Activity.applicationContext: ${reply.code}", reply.code)
            val exported = fixture.contained(java.io.File(reply.value as String))
            val payload = org.json.JSONObject(exported.readText())
            assertEquals(1, payload.getJSONArray("assessments").length())
            assertEquals(1, fixture.exportAcquisitions)
            assertFalse(fixture.opened.last().isOpen)
        }
    }

    @Test fun omittedExportAcquisitionFailsClosedWithoutDefaultStoreFallback() {
        HostStudyFixture().use { f ->
            val factory = object : ActivityResourceFactory {
                override fun session() = f.factory.session()
                override fun exporter() = f.factory.exporter()
                override fun benchmark() = f.factory.benchmark()
                override fun vision() = f.factory.vision()
                // Deliberately omit exportDatabase: the default must fail, never use application stores.
            }
            f.activity.initializeResources(factory, f.owner) {}
            val control = f.activity.controlHandler(f.owner)
            val reply = Reply()
            control.onMethodCall(MethodCall("exportData", null), reply)
            assertEquals(1, reply.replies)
            assertEquals("EXPORT_FAILED", reply.code)
            assertEquals("Export database acquisition not configured", reply.message)
            assertEquals(0, f.exportAcquisitions)
            assertEquals(1, f.helpers.size) // only the explicitly isolated manager helper
            val newer = MainActivity.Initialization()
            f.activity.initializeResources(f.factory, newer) {}
            val stale = Reply()
            control.onMethodCall(MethodCall("startSession", null), stale)
            assertEquals("CONTROL_FAILED", stale.code)
            assertNull(stale.value)
        }
    }

    @Test fun executedStudyAndBenchmarkProducer() {
        val manifest = HostStudyProducer.execute()
        assertEquals("success", org.json.JSONObject(manifest.readText()).getString("producer_outcome"))
    }

    @Test fun publisherRejectsExistingEscapingDuplicateMissingTamperedAndStaleOutput() {
        HostStudyFixture().use { f ->
            val sources = java.io.File(f.root, "source-fixture").apply { mkdir() }
            for (name in listOf("main", "test")) java.io.File(sources, "app/android/app/src/$name/kotlin").mkdirs()
            val source = java.io.File(sources, "app/android/app/src/main/kotlin/Synthetic.kt").apply { writeText("synthetic source digest fixture") }
            java.io.File(sources, "app/android/app/build.gradle.kts").writeText("synthetic gradle digest fixture")
            val destination = java.io.File(f.root, "output")
            val run = HostArtifactRun(destination, sources)
            assertThrows(IllegalArgumentException::class.java) { HostArtifactRun(destination, sources) }
            assertThrows(IllegalArgumentException::class.java) { HostArtifactRun(java.io.File(f.root, "../escape"), sources) }
            val link = java.io.File(f.root, "link")
            java.nio.file.Files.createSymbolicLink(link.toPath(), f.internal.toPath())
            assertThrows(IllegalArgumentException::class.java) { HostArtifactRun(java.io.File(link, "escape"), sources) }
            assertThrows(IllegalArgumentException::class.java) { run.write("../escape", byteArrayOf(1), "study", "study") }
            assertThrows(IllegalArgumentException::class.java) { run.write("bad.json", byteArrayOf(1), "unknown", "study") }
            assertThrows(IllegalArgumentException::class.java) { run.write("bad.json", byteArrayOf(1), "study", "unknown") }
            run.write("study.json", "synthetic".toByteArray(), "study", "study")
            assertThrows(IllegalArgumentException::class.java) { run.write("study.json", byteArrayOf(1), "study", "study") }
            assertThrows(IllegalArgumentException::class.java) { run.publish(setOf("missing.json"), org.json.JSONObject()) }
            val artifact = java.io.File(run.root, "study.json")
            artifact.writeText("tampered")
            assertThrows(IllegalStateException::class.java) { run.publish(setOf("study.json"), org.json.JSONObject()) }
            artifact.delete()
            assertThrows(IllegalStateException::class.java) { run.publish(setOf("study.json"), org.json.JSONObject()) }
            artifact.writeText("synthetic")
            source.writeText("changed after snapshot")
            assertThrows(IllegalStateException::class.java) { run.publish(setOf("study.json"), org.json.JSONObject()) }
            assertFalse(java.io.File(run.root, "manifest.json").exists())
            source.writeText("synthetic source digest fixture")
            val manifest = run.publish(setOf("study.json"), org.json.JSONObject())
            val decoded = org.json.JSONObject(manifest.readText())
            assertEquals(1, decoded.get("test_schema_version"))
            assertEquals(run.runId, decoded.getString("run_id"))
            assertEquals(HostArtifactRun.sha(artifact.readBytes()), decoded.getJSONArray("artifacts").getJSONObject(0).getString("sha256"))
            assertThrows(IllegalStateException::class.java) { run.publish(setOf("study.json"), org.json.JSONObject()) }
            assertThrows(IllegalStateException::class.java) { run.write("later.json", byteArrayOf(1), "study", "study") }
        }
    }

    @Test fun staleControlOwnerFailsThroughProductionCallableWithoutDefaultStores() {
        val reply = Reply()
        handler(MainActivity(), MainActivity.Initialization()).onMethodCall(MethodCall("getParticipantId", null), reply)
        assertEquals(1, reply.replies)
        assertEquals("CONTROL_FAILED", reply.code)
        assertNull(reply.value)
    }
}
