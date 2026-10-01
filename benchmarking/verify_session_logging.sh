#!/bin/bash
# Phase 8, Task 16 — on-emulator verification of session logging.
#
# Verifies, against a running emulator/device:
#   1. Legacy attempt_history.jsonl is migrated into SQLite on first launch
#   2. The schema (tables + indexes) is created as specified
#   3. Attempts are grouped under a session with computed summaries
#   4. Malformed/blank JSONL lines are skipped, original file is renamed
#
# Usage: benchmarking/verify_session_logging.sh
set -euo pipefail

export PATH="$PATH:$HOME/Library/Android/sdk/platform-tools"
PKG=com.kumpas.kumpas_app
DB=/data/data/$PKG/databases/kumpas_sessions.db
FILES=/data/data/$PKG/files

say() { printf '\n=== %s ===\n' "$1"; }
sq() { adb shell "run-as $PKG sqlite3 $DB \"$1\"" | tr -d '\r'; }

say "Device"
adb devices | sed -n '2p'
adb shell getprop ro.build.version.sdk | tr -d '\r'

say "Reset app state"
adb shell pm clear "$PKG" > /dev/null
echo "cleared"

say "Seed legacy JSONL (2 valid rows, 1 blank, 1 malformed)"
NOW=$(( $(date +%s) * 1000 ))
LEGACY=$(mktemp)
{
  echo "{\"targetClass\":1,\"targetLabel\":\"AKO\",\"predictedLabel\":\"AKO\",\"predictedConfidence\":0.91,\"recognizedAsTarget\":true,\"overallMatch\":0.82,\"items\":[],\"timestamp\":$NOW}"
  echo "{\"targetClass\":2,\"targetLabel\":\"IKAW\",\"predictedLabel\":\"AKO\",\"predictedConfidence\":0.44,\"recognizedAsTarget\":false,\"overallMatch\":0.39,\"items\":[],\"timestamp\":$(( NOW + 1000 ))}"
  echo ""
  echo "{ this line is malformed"
} > "$LEGACY"

adb push "$LEGACY" /data/local/tmp/legacy.jsonl > /dev/null
adb shell "run-as $PKG sh -c 'mkdir -p $FILES && cp /data/local/tmp/legacy.jsonl $FILES/attempt_history.jsonl'"
adb shell "run-as $PKG ls $FILES" | tr -d '\r'

say "Launch app (triggers SessionManager init + migration)"
adb shell monkey -p "$PKG" -c android.intent.category.LAUNCHER 1 > /dev/null 2>&1
sleep 12

say "Schema: tables and indexes"
sq "SELECT type||' '||name FROM sqlite_master WHERE name NOT LIKE 'sqlite_%' ORDER BY type, name;"

say "Migration: files dir after launch (jsonl should be renamed)"
adb shell "run-as $PKG ls $FILES" | tr -d '\r'

say "Participants"
sq "SELECT COUNT(*)||' participant(s)' FROM participants;"

say "Sessions (source | attempts | distinct signs | avg_match)"
sq "SELECT source||' | '||attempt_count||' | '||signs_attempted||' | '||ROUND(avg_match,3) FROM sessions;"

say "Migrated attempts (newest first)"
sq "SELECT target_label||' -> '||predicted_label||' match='||overall_match FROM attempts ORDER BY timestamp DESC;"

say "Crash check (last 40 lines of app logcat)"
adb logcat -d -s KumpasSession:* AndroidRuntime:E flutter:E | tail -40 | tr -d '\r'

rm -f "$LEGACY"
echo
echo "done"
