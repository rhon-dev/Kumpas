"""Finalize D preservation, complete dirty/new-file review and evidence freeze."""
import datetime,hashlib,json,os,re,shutil,subprocess
from pathlib import Path
import run
D=run.D;ROOT=run.ROOT;E=D.parent
NEW_DOCS=['docs/host-completion-2026-10-18.md','docs/host-reproducible-handoff.md','docs/decisions/2026-10-18-host-scope-deviations.md']
# Exact current checkout preservation, excluding only the three authorized docs.
before=json.loads((D/'source-before.json').read_text())
after=run.snapshot()
changed=[p for p in set(before)|set(after) if before.get(p)!=after.get(p) and p not in NEW_DOCS]
assert not changed,changed
run.write(D/'source-after.json',after)
protected_before=json.loads((D/'protected-before.json').read_text())['hashes']
protected={p:run.sha(ROOT/p) for p in protected_before}
assert protected==protected_before and len(protected)==82
run.write(D/'protected-after.json',{'count':len(protected),'hashes':protected,'mismatches':[]})
# Accepted later source hardening supersedes prior reviewed postimages only;
# historical execution manifests remain unchanged.
accepted={};decisions=[]
for path in sorted((E/'controller').glob('*acceptance*.json'),key=lambda p:json.loads(p.read_text()).get('at','')):
 obj=json.loads(path.read_text());mapping=obj.get('source_hashes',{})
 if path.name=='a3a-acceptance-and-consumer-binding.json':
  assert run.sha(ROOT/obj['manifest'])==obj['manifest_sha256']
  mapping=json.loads((ROOT/obj['manifest']).read_text())['source_hashes']
 for name,h in mapping.items():accepted[name]={'sha256':h,'authority':path.name}
 decisions.append({'path':str(path.relative_to(ROOT)),'sha256':run.sha(path),'at':obj.get('at'),'decision':obj['decision']})
assert all(run.sha(ROOT/p)==row['sha256'] for p,row in accepted.items())
run.write(D/'current-accepted-source-readback.json',{'sources':accepted,'count':len(accepted),'mismatches':[],'authorities':decisions,'limits':'Latest accepted postimage per path, not retroactive rebinding of historical A/B/C fixture or campaign identities.'})
# Parse exactly16 document rows for a matching machine disposition.
text=(ROOT/NEW_DOCS[0]).read_text()
rows=[]
for line in text.splitlines():
 if re.match(r'^\|\d{2} ',line):
  cells=line.strip('|').split('|')
  assert len(cells)==3
  number,title=cells[0].split(' ',1)
  rows.append({'host':number,'title':title,'implemented_execution_review':cells[1],'disposition_and_dependency':cells[2]})
assert [r['host'] for r in rows]==[f'{n:02}' for n in range(1,17)]
run.write(D/'dispositions.json',{'schema_version':1,'items':rows,'count':len(rows),'parent_whole_package_review':'PENDING','all16_complete':False,'physical_or_study_acceptance':False})
# Actual results, no cached-test assumption.
labels=['flutter-analyze','flutter-full','benchmark-full','evaluation-full','training-full','holistic-compatible','jvm-full','debug-test-build-fresh3','release-build-retry4','accepted-producer-preflight','historical-artifact-readback']
results={label:json.loads((D/(label+'-result.json')).read_text()) for label in labels}
assert all(row['exit']==0 and not row['source_changes'] for row in results.values())
assert len({r['source_manifest_sha256'] for r in results.values()})==1
for label,r in results.items():assert run.sha(D/r['log'])==r['log_sha256']
jvm=results['jvm-full'];assert all(jvm['required_executed_tasks'].values())
assert all(jvm['totals'][k]==0 for k in ('failures','errors','skipped'))
flutter=results['flutter-full'];assert flutter['failures']==flutter['skipped']==0 and flutter['done_events'][-1]['success']
for label in ('training-full','evaluation-full','holistic-compatible'):assert results[label]['summary']==['OK'] and not results[label]['skip_lines']
assert results['benchmark-full']['summary']==['OK (skipped=2)'] and len(results['benchmark-full']['skip_lines'])==2
# Require genuinely executed debug compilation+packaging lines.
debug_log=(D/'debug-test-build-fresh3.log').read_text().splitlines()
required=[':app:compileFlutterBuildDebug',':app:compileDebugKotlin',':app:compileDebugAndroidTestKotlin',':app:packageDebug',':app:packageDebugAndroidTest']
assert all('> Task '+task in debug_log for task in required)
release_log=(D/'release-build-retry4.log').read_text().splitlines()
assert '> Task :app:packageRelease' in release_log and '> Task :app:assembleRelease' in release_log
assert '> Task :app:compileReleaseKotlin' in (D/'release-build-retry2.log').read_text().splitlines()
assert '> Task :app:minifyReleaseWithR8' in (D/'release-build-retry3.log').read_text().splitlines()
artifacts=json.loads((D/'artifact-readback.json').read_text())
for kind,row in artifacts['artifacts'].items():
 assert run.sha(ROOT/row['path'])==run.sha(row['snapshot'])==row['sha256']
 producer=results[row['build_result'].removesuffix('-result.json')]
 assert producer['artifacts'][row['path']]['sha256']==row['sha256']
 if kind!='android_test':assert row['accepted_inspector']['exit']==0 and len(row['assets'])==5
assert artifacts['artifacts']['release']['strict_arm64_probe']['exit']==1
# Historical outputs are in snapshots now, not expected to remain at build paths.
historical=json.loads((D/'historical-apk-preservation.json').read_text())
assert all(run.sha(row['snapshot'])==row['sha256'] for row in historical.values())
incidents=[
 {'label':'debug-test-build-fresh','exit':None,'tool_timeout_seconds':420,'status':'No observed completion result; retained partial log and start record. Not counted successful.'},
 {'label':'quarantine-generated.py','exit':1,'error':'AssertionError after same-volume TTF rename: flags changed; recovery records observed postimage and does not assert unchanged flags/preimage digest.'},
 {'label':'quarantine-recovery.py','exit':1,'error':'TimeoutError Errno60 moving DATALESS app 2.so outside provider; source remained, destination absent. Same-provider exact-file recovery succeeded.'},
 {'label':'inspect-artifacts.py','exit':1,'error':'Actual debug inspector exit1 on two suffixed generated snapshot ZIP entries. Unsuccessful APK preserved; narrow source/canonical/hash quarantine, then rebuild.'},
 {'label':'inspect-final-artifacts.py','exit':1,'error':'Actual release inspector exit1 on generated NativeAssetsManifest suffix. Unsuccessful APK preserved; narrow same-inode/hash quarantine, then rebuild.'},
 {'label':'kill -INT 7744','exit':1,'error':'No such process; owned managed build had already completed. No signal delivered, no daemon killed.'},
]
run.write(D/'execution-incidents.json',{'recorded_at':datetime.datetime.now().astimezone().isoformat(),'origin':'Actual tool results observed during D, not fresh replays or synthesized command output','incidents':incidents})
run.append({'event':'completion-recovery-notes','incidents_file':'execution-incidents.json','sha256':run.sha(D/'execution-incidents.json'),'no_unobserved_exit_claimed':True})
# All complete new source files and all changed tracked postimages are supplied.
review=D/'review';review.mkdir()
tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().strip('\0').split('\0'))
new=sorted(p for p in after if p not in tracked)
modified=set(subprocess.check_output(['git','diff','--name-only','HEAD','-z'],cwd=ROOT).decode().strip('\0').split('\0'))
modified=sorted(p for p in after if p in modified)
postimages={}
for category,paths in [('new-files',new),('tracked-postimages',modified)]:
 for name in paths:
  target=review/category/name;target.parent.mkdir(parents=True,exist_ok=True)
  shutil.copy2(ROOT/name,target)
  assert run.sha(target)==after[name]
  postimages[name]={'snapshot':str(target.relative_to(ROOT)),'sha256':after[name],'kind':category}
with (review/'tracked-head-diff.patch').open('xb') as f:
 subprocess.run(['git','diff','--binary','HEAD'],cwd=ROOT,stdout=f,check=True)
with (D/'diff-check.log').open('x') as f:
 check=subprocess.run(['git','diff','--check'],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
assert check.returncode==0
# New files need their own whitespace check (HEAD diff omits them).
whitespace=[]
for name in new:
 for n,line in enumerate((ROOT/name).read_text().splitlines(),1):
  if line.rstrip()!=line:whitespace.append({'path':name,'line':n})
assert not whitespace,whitespace
review_package={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'tracked_modified_count':len(modified),'new_complete_files_count':len(new),'source_inventory_count':len(after),'postimages':postimages,'tracked_diff':str((review/'tracked-head-diff.patch').relative_to(ROOT)),'tracked_diff_sha256':run.sha(review/'tracked-head-diff.patch'),'new_file_whitespace_findings':whitespace,'limitations':'No commits were created; BASE..HEAD would omit the work. Full dirty tracked diff plus complete new source/test/docs snapshots provided. Generated outputs/caches/environments/evidence directories excluded from source inventory; protected binary assets separately checked.'}
run.write(D/'review-package.json',review_package)
summary={'at':datetime.datetime.now().astimezone().isoformat(),'head':review_package['head'],'status':'HOST_EVIDENCE_PREPARED_PARENT_VERIFICATION_AND_WHOLE_PACKAGE_REVIEW_PENDING','test_source_manifest_sha256':results['jvm-full']['source_manifest_sha256'],'source_before_count':len(before),'source_after_count':len(after),'non_document_source_changes':changed,'authorized_new_documents':NEW_DOCS,'protected_count':len(protected),'protected_mismatches':[],'current_accepted_source_count':len(accepted),'current_accepted_source_mismatches':[],'tests':{'flutter':{k:flutter[k] for k in ('tests','failures','skipped')},'jvm':{'suites':len(jvm['xml']),**jvm['totals']},'benchmarking':{'discovered':results['benchmark-full']['tests'],'passed':results['benchmark-full']['tests']-len(results['benchmark-full']['skip_lines']),'skipped':len(results['benchmark-full']['skip_lines']),'skip_lines':results['benchmark-full']['skip_lines']},'evaluation':{'tests':results['evaluation-full']['tests'],'failures':0,'skipped':0},'training':{'tests':results['training-full']['tests'],'failures':0,'skipped':0},'compatible_holistic':{'tests':results['holistic-compatible']['tests'],'failures':0,'skipped':0,'overlaps_broad_suite':True}},'results':{k:{'result_file':k+'-result.json','log_sha256':v['log_sha256'],'exit':v['exit']} for k,v in results.items()},'artifacts':{k:{n:r[n] for n in ('path','snapshot','sha256','bytes','build_result','source_manifest_sha256','all_native_abis','flutter_abis')} for k,r in artifacts['artifacts'].items()},'strict_arm64_only_accepted':False,'historical_apk_snapshot_count':len(historical),'review':{'tracked_modified_files':len(modified),'complete_new_files':len(new),'parent_verification':'PENDING','spec_review':'PENDING','quality_review':'PENDING'},'all16_complete':False,'installed_runtime_verified':False,'physical_or_study_acceptance':False}
run.write(D/'verification-summary.json',summary)
with (D/'report.md').open('a') as f:
 f.write('''

## Final outcome — host evidence prepared, parent acceptance pending

No application/model/benchmark/training/evaluation source or tests were edited by D. Created only the three named new documentation files and new D evidence/review snapshots. All16 dispositions are in `dispositions.json` and the new status document; **all16 complete is false**. Parent independent verification and whole-package spec/quality review remain mandatory. Parent-owned progress/readiness/phase-gates files were untouched.

''')
 f.write(f"Actual final counts: Flutter {flutter['tests']} passed with0 failures/skips; JVM {jvm['totals']['tests']} tests/{len(jvm['xml'])} suites with0 failures/errors/skips; benchmarking {results['benchmark-full']['tests']} discovered, {results['benchmark-full']['tests']-2} passed and2 explicit Holistic capability skips; compatible parity/campaign {results['holistic-compatible']['tests']} passed0 skips (overlapping suite, includes both detector cases); evaluation {results['evaluation-full']['tests']} and training {results['training-full']['tests']} passed0 skips. Flutter analysis exited0 with no issues. JVM and instrumentation Kotlin targets have exact fresh execution lines, and XML/binary results were copied while holding the shared flock. Commands/exits/env/source/log hashes are in the append-only ledger and per-label JSON.\n\n")
 f.write('''Successful final artifact identities and independent inspection:

''')
 for kind,row in artifacts['artifacts'].items():
  f.write(f"- {kind}: `{row['path']}`, {row['bytes']} bytes, SHA256 `{row['sha256']}`; actual producer `{row['build_result']}`; external snapshot `{row['snapshot']}`.\n")
 f.write('''
Debug/test freshness uses `debug-test-build-fresh3`: Flutter/application/instrumentation compile and both package tasks executed. Release freshness uses `release-build-retry4`: actual ARM64-targeted offline assets/package/assembly, bound to the unchanged-source full compile/minification chain in retry2/retry3. Earlier debug/test commands only observed release bytes and are not release producers; earlier release commands only observed debug/test bytes and are not their producers. Latest independent `artifact-readback.json` and current inspector outputs are authoritative; intermediate manifests retain unsuccessful or historical artifacts.

Independent ZIP CRC/duplicate-member checks and all five protected asset digests passed for each app APK. Test APK has no native/models requirement. Debug has Flutter libraries in3 ABI namespaces; release libapp/libflutter only ARM64 but13 total native paths in3 dependency namespaces. Current debug and retained historical-three-ABI release expectations passed; strict ARM64-only release probe exited1 as expected, not an approved policy failure or automatic Gradle configuration defect. Inspector-only build provenance remains false by design; the separate real command/source/log/producer composition establishes host build-run provenance. No signature/ELF/install/startup/runtime claim.

### Incidents retained, not concealed

Release initial/retry1/retry2 exited1 on generated DATALESS suffix files TTF/SO/DEX. Narrow quarantine manifests preserve exact objects; no broad deletion/clean/reset or source fix. The TTF script exited1 on a flags-equality assertion after rename: the flag changed, so recovery records actual postimage/hash rather than inventing a preimage hash. External SO rename timed out Errno60; same-provider relocation preserved inode/device/size/flags. SO/DEX DATALESS digests remain null; this is not byte-hash verification. Resident debug snapshot and release JSON duplicates were hash-compared to canonical files before exact-file quarantine. Duplication origin is unknown.

The first stronger debug tool call timed out420s with no observed completion exit and is not counted successful. Managed fresh2 completed, but the accepted inspector rejected two suffixed generated ZIP snapshot entries. After preservation/rebuild, fresh3 debug passed. The first fresh release inspector rejected the suffixed NativeAssetsManifest entry; after preservation and retry4, current release passed. Both unsuccessful APKs are preserved in external `fresh-apks`/`final-apks` snapshots. The attempted SIGINT found no such process after managed completion: no signal was delivered or daemon killed. Exact observed incidents are in `execution-incidents.json`; source-script assertion failures are not fake build or source-test failures. Retained Kotlin/SDK/Gradle/upstream dependency warnings are nonfatal in the successful commands.

### Historical-safe readback and remaining blockers

`historical-readback.json` verifies six historical B1 fixtures/180 PNGs and original comparator-before identity without opening raw video/NPZ. B2 retained150 historical validation records/model,144 correct each,134 missing metadata records, incomplete binding and all13 source-code roles checked against the correct historical helper/test/comparator snapshots. Current repaired sources match the latest accepted records separately. No old source-complete verifier, inference/retraining or hydration of raw data was run; no manifests were rebound. Follow-ups B1-R1/C1-Q1/C2-L1 are accepted closed.

Host09 actual retraining remains unapproved and its isolated runner unimplemented. Host10 full-source provenance remains blocked134 DATALESS source pairs. Host11/12 human rubric/scoring/inference remains blocked on instruments, raters, missingness and analysis/consent approvals; synthetic descriptors do not satisfy it. Host13–16 artifacts are prepared/executed but review pending. Installed continuous camera/channel/SQLite/export/delete/reopen, physical FPS/latency/thermal/all signs/signers, expert/anatomical, untouched/signer-independent evaluation and participant authorization remain open.

''')
 f.write(f"Preservation: all{len(protected)} protected originals unchanged; {len(before)} initial reviewable source/config/docs files unchanged except the three new authorized docs ({len(after)} final inventory); {len(accepted)} latest accepted source postimages matched. Six pre-build APK path snapshots rehashed successfully. `review-package.json` supplies {len(modified)} changed tracked postimages plus complete contents of {len(new)} new files and the nonempty dirty HEAD diff. `git diff --check` exit0; separate new-file whitespace scan clean. External media/vectors/APK bytes remain outside Git; no participant stores were copied.\n\n")
 f.write('''Deliverables: `docs/host-completion-2026-10-18.md`, `docs/host-reproducible-handoff.md`, `docs/decisions/2026-10-18-host-scope-deviations.md` (proposed/approval pending). Exact final source/document/helper/report hashes follow in `source-freeze.json`; freeze this package for parent whole-change review. No commits/push/deployment/installations/device transport/real-model conversion or model/reference/math/XP/layout edits. Blank hardware/trial/approval forms remain unchanged.
''')
# Freeze after the report is final; never self-hash a mutable report prematurely.
freeze=dict(after)
for p in sorted(D.glob('*.py')):freeze[str(p.relative_to(ROOT))]=run.sha(p)
for name in ('report.md','taskbrief.md'):
 freeze[str((D/name).relative_to(ROOT))]=run.sha(D/name)
run.write(D/'source-freeze.json',{'at':datetime.datetime.now().astimezone().isoformat(),'head':review_package['head'],'files':freeze,'count':len(freeze),'test_source_manifest_sha256':results['jvm-full']['source_manifest_sha256'],'parent_review_status':'PENDING','no_application_source_changes':True})
# Evidence inventory excludes itself and any later parent verification records.
evidence={str(p.relative_to(ROOT)):run.sha(p) for p in sorted(D.rglob('*')) if p.is_file()}
run.write(D/'evidence-freeze.json',{'files':evidence,'count':len(evidence),'source_freeze_sha256':run.sha(D/'source-freeze.json'),'limits':'Subsequent parent review/status records must be separate; no self-hash.'})
print(json.dumps({'status':summary['status'],'tests':summary['tests'],'protected':len(protected),'accepted_sources':len(accepted),'source_inventory':len(after),'frozen_files':len(freeze),'review_tracked':len(modified),'review_new_complete':len(new),'artifacts':summary['artifacts'],'source_freeze_sha256':run.sha(D/'source-freeze.json')},indent=2))
