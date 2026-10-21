"""Record the actual local check run with source hashes and command results."""

# Resolve local assets after the repository directory reorganization.
try:
    if __package__ == "scripts":
        from ._workspace_layout import project_root, project_path, project_glob, project_iterdir
    else:
        from _workspace_layout import project_root, project_path, project_glob, project_iterdir
except ModuleNotFoundError as _layout_error:
    if _layout_error.name != "_workspace_layout":
        raise
    # Standalone workers retain their original layout on remote machines.
    from pathlib import Path as _LayoutPath
    def project_root(filename):
        return _LayoutPath(filename).resolve().parent
    def project_path(name="", *, base=None):
        return (base if base is not None else project_root(__file__)) / name
    def project_glob(pattern, *, base=None):
        return (base if base is not None else project_root(__file__)).glob(pattern)
    def project_iterdir(*, base=None):
        return (base if base is not None else project_root(__file__)).iterdir()

from pathlib import Path
import hashlib
import json
import platform
import subprocess
import sys
import time

P = project_root(__file__)
commands = [[sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
            [str(project_path("hutter_research/integer_mixer_selftest.exe", base=P))]]
M = {"id": "R10-local-correctness", "status": "RUNNING", "started": time.time(),
     "platform": platform.platform(), "python": sys.version, "commands": [], "source_hashes": {}}
for path in [*sorted((project_path("tests", base=P)).glob("*.py")),
             *sorted(path for path in (project_path("hutter_research", base=P)).iterdir()
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
(project_path("research_round10_local_checks_results.json", base=P)).write_text(json.dumps(M, indent=2), encoding="utf-8")
print(json.dumps({"status": M["status"], "commands": len(commands)}))
