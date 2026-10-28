#!/usr/bin/env python3
"""Check EVIDENCE_REGISTER.json: every citation resolves, every row has the required fields.

Exit 0 only if all rows are complete and every (path, needle, line) still matches.
A sha256 change is reported as DRIFT (warning, exit 0): the cited line still resolves
but the file moved on since the register was built; rebuild with build_register.py.
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REQUIRED = ("id", "system", "identity", "source_role", "fidelity", "statistics", "calibration",
            "deployment", "unknowns", "missing_inputs", "next_gate", "citations")
FIDELITY = {"FAITHFUL", "PARTIAL", "MISMATCH", "UNKNOWN", "NA"}


def check(reg_path=None, root=None):
    reg = json.loads(Path(reg_path or HERE / "EVIDENCE_REGISTER.json").read_text(encoding="utf-8"))
    root = Path(root) if root else ROOT
    errors, drift, ids = [], [], set()
    for r in reg["rows"]:
        rid = r.get("id", "?")
        for k in REQUIRED:
            if k not in r or r[k] in (None, "", [], {}):
                if k == "unknowns" and r.get("unknowns") == []:
                    errors.append("%s: empty unknowns (state UNKNOWN or why none)" % rid)
                elif k not in r or r[k] in (None, ""):
                    errors.append("%s: missing %s" % (rid, k))
        if rid in ids:
            errors.append("%s: duplicate id" % rid)
        ids.add(rid)
        if r.get("fidelity") not in FIDELITY:
            errors.append("%s: bad fidelity %r" % (rid, r.get("fidelity")))
        for field in ("historical", "current"):
            if not r.get("statistics", {}).get(field):
                errors.append("%s: statistics.%s missing" % (rid, field))
        n = 0
        for kind, cites in r.get("citations", {}).items():
            for c in cites:
                n += 1
                p = root / c["path"]
                if not p.is_file():
                    errors.append("%s: %s file missing: %s" % (rid, kind, c["path"]))
                    continue
                data = p.read_bytes()
                lines = data.decode("utf-8", "replace").splitlines()
                line = c.get("line", 0)
                if c.get("needle"):
                    if not (1 <= line <= len(lines)) or c["needle"] not in lines[line - 1]:
                        errors.append("%s: %s needle not at %s:%s" % (rid, kind, c["path"], line))
                if c.get("sha256") and hashlib.sha256(data).hexdigest() != c["sha256"]:
                    drift.append("%s: %s changed since build" % (rid, c["path"]))
        if n == 0:
            errors.append("%s: no citations" % rid)
    return reg, errors, sorted(set(drift))


def main():
    reg, errors, drift = check()
    for d in drift:
        print("DRIFT", d)
    for e in errors:
        print("FAIL", e)
    print("rows=%d errors=%d drift=%d" % (len(reg["rows"]), len(errors), len(drift)))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
