package com.kumpas.kumpas_app

import android.content.pm.ApplicationInfo
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.RuntimeEnvironment
import org.robolectric.annotation.Config
import org.xmlpull.v1.XmlPullParser

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class StudyBackupPolicyTest {
    @Test
    fun mergedApplicationAndResources_excludeStudyStoresFromBackupAndTransfer() {
        val context = RuntimeEnvironment.getApplication()
        assertEquals(0, context.applicationInfo.flags and ApplicationInfo.FLAG_ALLOW_BACKUP)
        val expected = setOf(
            "database:.", "sharedpref:kumpas_session_prefs.xml",
            "file:attempt_history.jsonl", "file:attempt_history.jsonl.migrated",
            "file:exports", "external:."
        )
        for ((resource, sections) in mapOf(
            "study_backup_rules" to setOf("full-backup-content"),
            "study_data_extraction_rules" to setOf("cloud-backup", "device-transfer")
        )) {
            val id = context.resources.getIdentifier(resource, "xml", context.packageName)
            assertNotEquals("missing packaged rules $resource", 0, id)
            val found = mutableMapOf<String, MutableSet<String>>()
            context.resources.getXml(id).use { xml ->
                var section = ""
                while (xml.eventType != XmlPullParser.END_DOCUMENT) {
                    if (xml.eventType == XmlPullParser.START_TAG) {
                        if (xml.name in sections) section = xml.name
                        if (xml.name == "exclude") found.getOrPut(section) { mutableSetOf() }
                            .add("${xml.getAttributeValue(null, "domain")}:${xml.getAttributeValue(null, "path")}")
                    }
                    xml.next()
                }
            }
            for (section in sections) assertEquals("rules for $section", expected, found[section])
        }
    }
}
