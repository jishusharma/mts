"""Shared helpers for scripts/sched detectors. Pure stdlib, read-only.

Detector contract (SCHEDULER_PLAN s5): stdout line 1 = `<CHECK> <OK|WARN|RED> <reason>`,
line 2 = `HASH <sha256 hex>` (check name + condition-relevant evidence only, never ages or clocks),
exit 0 OK / 1 WARN / 2 RED.
"""
import hashlib
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
EXIT = {"OK": 0, "WARN": 1, "RED": 2}


def state_hash(check, evidence_lines):
    body = check + "\n" + "\n".join(sorted(evidence_lines))
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def emit(check, status, reason, evidence_lines):
    print(f"{check} {status} {reason}")
    print(f"HASH {state_hash(check, evidence_lines)}")
    return EXIT[status]


def run(main):
    try:
        code = main()
    except Exception as exc:  # a broken detector must be loud, never silently OK
        code = emit("detector_error", "RED", f"{type(exc).__name__}: {exc}", [repr(exc)])
    sys.exit(code)
