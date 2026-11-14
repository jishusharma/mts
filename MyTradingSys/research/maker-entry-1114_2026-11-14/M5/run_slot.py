"""Acquire a maker slot (atomic mkdir), run study.py at BelowNormal priority, always release the slot."""
import os, sys, time, subprocess, shutil
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = Path(r"F:\MTS\maker_slots")
ROOT.mkdir(parents=True, exist_ok=True)
slot = None
while slot is None:
    for i in range(4):
        try:
            (ROOT / f"slot{i}").mkdir()
            slot = ROOT / f"slot{i}"
            break
        except FileExistsError:
            pass
    if slot is None:
        time.sleep(20)
print("slot", slot, flush=True)
try:
    with open(HERE / "run.log", "w") as out, open(HERE / "run.err", "w") as err:
        p = subprocess.Popen([sys.executable, "-I", "study.py"], cwd=HERE, stdout=out, stderr=err,
                             creationflags=0x00004000)  # BELOW_NORMAL_PRIORITY_CLASS
        rc = p.wait()
    print("exit", rc)
finally:
    shutil.rmtree(slot, ignore_errors=True)
