"""Final read-only host context and accepted producer binding checks."""
from pathlib import Path
import run
py='/opt/homebrew/bin/python3.11'
checks=[
 ('host-tool-versions',['/bin/bash','-c','/opt/homebrew/bin/flutter --version --machine; "$JAVA_HOME/bin/java" -version; /usr/bin/sw_vers; /usr/sbin/sysctl -n hw.memsize hw.logicalcpu'],run.ROOT,'plain'),
 ('historical-artifact-readback',[py,'-B','-E',str(run.D/'readback-history.py'),'--check-only'],run.ROOT,'plain'),
 ('accepted-producer-preflight',[py,'-B','-E','benchmarking/host_fixture_replay.py','preflight'],run.ROOT,'plain'),
]
for label,cmd,cwd,kind in checks:
 if run.execute(label,cmd,cwd,kind):raise SystemExit(1)
