# Reproduction script

Save the following as measure.py beside this document and run it from this checkout. It writes the complete logs and receipt.

```python
"""Reproduce the shipping gate comparison; writes complete logs and a receipt."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def main():
    receipt = {"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
               "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
               "python": sys.version, "changed": ["scripts/dev/nowin.py"], "runs": []}
    for name in ["sync.py", "gate_impact.py", "gate_select.py", "run_all_tests.py"]:
        receipt.setdefault("sha256", {})[name] = hashlib.sha256((ROOT / "scripts/dev" / name).read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix="shipping_proof_") as temp:
        changed = Path(temp) / "changed.txt"
        changed.write_text("scripts/dev/nowin.py\n", encoding="utf-8", newline="\n")
        tests = [sys.executable, "-m", "unittest", "scripts.dev.test_gate_impact", "scripts.dev.test_gate_select", "scripts.dev.test_run_all_tests", "scripts.dev.test_sync"]
        base = [sys.executable, "scripts/dev/run_all_tests.py", "--quick", "--precheck", "--fail-fast", "--slot", "--smoke", "--changed-file", str(changed)]
        for name, command in [("regressions", tests), ("baseline_smoke", base), ("fast_smoke", base + ["--fast"])]:
            print("START", name, flush=True)
            start = time.perf_counter()
            with (OUT / (name + ".txt")).open("w", encoding="utf-8", newline="\n") as log:
                result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, env={**os.environ, "PYTHONIOENCODING": "utf-8"})
            receipt["runs"].append({"name": name, "command": command, "seconds": round(time.perf_counter()-start, 3), "exit_code": result.returncode})
            (OUT / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8", newline="\n")
            print("END", receipt["runs"][-1], flush=True)


if __name__ == "__main__":
    main()

```
