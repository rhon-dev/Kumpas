"""Execute a named check and append its exact exit/log to the C2 ledger."""
import datetime, json, subprocess, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
label=sys.argv[1]
if not label.replace('-','').isalnum(): raise SystemExit(2)
cmd=sys.argv[2:]
with (HERE/(label+'.log')).open('x') as log:
    result=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
with (HERE/'command-ledger.jsonl').open('a') as f:
    f.write(json.dumps({'time':datetime.datetime.now().astimezone().isoformat(),'label':label,'argv':cmd,'exit':result.returncode,'log':label+'.log'})+'\n')
print(json.dumps({'label':label,'exit':result.returncode}))
raise SystemExit(result.returncode)
