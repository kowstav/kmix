"""Record the actual local check run with source hashes and command results."""
from pathlib import Path
import hashlib
import json
import platform
import subprocess
import sys
import time

P = Path(__file__).resolve().parent
commands = [[sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
            [str(P / "hutter_research/integer_mixer_selftest.exe")]]
M = {"id": "R10-local-correctness", "status": "RUNNING", "started": time.time(),
     "platform": platform.platform(), "python": sys.version, "commands": [], "source_hashes": {}}
for path in [*sorted((P / "tests").glob("*.py")),
             *sorted(path for path in (P / "hutter_research").iterdir()
                     if path.suffix in [".py", ".h", ".cpp", ".inc", ".bin"])]:
    M["source_hashes"][path.relative_to(P).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
for command in commands:
    started = time.monotonic()
    result = subprocess.run(command, cwd=P, capture_output=True, text=True)
    M["commands"].append({"command": command, "return_code": result.returncode,
                          "wall_seconds": time.monotonic() - started, "output": result.stdout + result.stderr})
    assert result.returncode == 0, M["commands"][-1]
M.update(status="COMPLETE_LOCAL_CORRECTNESS_CHECKS_PASS", finished=time.time(),
         limits="Property/unit checks and storage validation; no native warm quality or qualifying compression claim.")
(P / "research_round10_local_checks_results.json").write_text(json.dumps(M, indent=2), encoding="utf-8")
print(json.dumps({"status": M["status"], "commands": len(commands)}))
