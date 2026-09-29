import sys; sys.dont_write_bytecode = True
"""T056 Qwen-audit rotation script, backfill half.

Packs least-recently-audited targets from audit_targets.json as NUC queue tasks,
but only when the queue is currently idle (zero waiting tasks). The --t0 flag
delegates to audit_t0_checks.py module (built separately, T056 spec 095).
"""

from pathlib import Path
import json
import os
import re
import argparse
import subprocess
import datetime

REPO = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO / "scripts" / "worker" / "audit_targets.json"
QUEUE = REPO / "Dumps" / "workers" / "NUC-QUEUE"
QUEUE_TOOL = REPO / "scripts" / "worker" / "queue_tool.py"
SPECS_DIR = QUEUE / "specs"
BACKFILL_BATCH = 6
AUDIT_ID_MIN = 900

TEMPLATE_HINT = {
    "A1": "code line differs from canonical formula",
    "A2": "branch/edge case with no test (empty input, NaN, boundary)",
    "A3": "ambiguity, missing EXPECT, output won't fit OUTPUT_TOKENS",
    "A4": "quote + GPS answering it, or \"not in corpus\"",
    "A5": "Tom logic used as a filter, or layer importing Tom internals",
    "A6": "doc claim the code does not do",
    "A7": "path that could reach mainnet or skip a guard"
}

REPLY_FORMAT = """FINDING <n> | <A-id> | severity H/M/L | <path>:<line>
QUOTE: <exact line from that file>
WHY: <one sentence>
FIX: <one sentence>
or, if nothing found:
NO FINDINGS
"""
NO_FINDINGS = "NO FINDINGS"

def load_registry() -> dict:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

def save_registry(reg: dict) -> None:
    tmp = REGISTRY_PATH.with_name("." + REGISTRY_PATH.name + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(reg, ensure_ascii=True, indent=1) + "\n")
    os.replace(tmp, REGISTRY_PATH)

def utc_now_stamp() -> str:
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")

def targets_due(reg: dict, n: int) -> list:
    def sort_key(target):
        la = target.get("last_audited")
        if la is None:
            return (0, 0)
        else:
            return (1, la)
    return sorted(reg["targets"], key=sort_key)[:n]

def queue_waiting_count() -> int:
    incoming = QUEUE / "incoming"
    claimed = QUEUE / "claimed"
    count = 0
    if incoming.exists():
        count += len(list(incoming.glob("*.task.json")))
    if claimed.exists():
        count += len(list(claimed.glob("*.task.json")))
    return count

def build_spec_text(target: dict) -> str:
    scope_str = ",".join(target["paths"])
    note = target.get("note", "")
    return f"""TASK: Audit ({target["template"]}) -- {TEMPLATE_HINT[target["template"]]}\nSCOPE: {scope_str}\nOUTPUT: reply using the format given in the task body below, nothing else\nOUTPUT_TOKENS: 1536\nMODEL: qwen3-coder:30b\n\nNOTE: {note}\n\n{REPLY_FORMAT}\n"""

def next_audit_spec_id(slug: str) -> str:
    SPECS_DIR.mkdir(parents=True, exist_ok=True)
    pattern = re.compile(r"(\d+)-audit-.+\.md")
    ids = []
    for p in SPECS_DIR.glob("9*-audit-*.md"):
        match = pattern.match(p.name)
        if match:
            try:
                ids.append(int(match.group(1)))
            except ValueError:
                continue
    next_n = max([AUDIT_ID_MIN - 1] + ids) + 1
    return f"{next_n}-audit-{slug}"

def pack_one(target: dict) -> bool:
    slug = re.sub(r"[^a-z0-9]+", "-", target["id"].lower()).strip("-")
    spec_id = next_audit_spec_id(slug)
    path = SPECS_DIR / f"{spec_id}.md"
    text = build_spec_text(target)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    result = subprocess.run([sys.executable, str(QUEUE_TOOL), "pack", str(path)], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        return False
    return True

def cmd_backfill(reg: dict) -> int:
    waiting = queue_waiting_count()
    if waiting > 0:
        print(f"SKIP backfill: {waiting} task(s) already waiting")
        return 0
    for target in targets_due(reg, BACKFILL_BATCH):
        success = pack_one(target)
        if success:
            target["last_audited"] = utc_now_stamp()
            print(f"AUDITED {target['id']}")
        else:
            print(f"FAILED  {target['id']}")
    save_registry(reg)
    return 0

def cmd_t0(reg: dict) -> int:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        import audit_t0_checks
    except ImportError:
        print("T0 checks: audit_t0_checks.py not present yet (see 095)")
        return 1
    return audit_t0_checks.run_t0_checks()

def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--backfill", action="store_true")
    p.add_argument("--t0", action="store_true")
    args = p.parse_args(argv)
    if not (args.backfill or args.t0):
        p.print_help()
        return 2
    reg = load_registry()
    rc = 0
    if args.backfill:
        rc = cmd_backfill(reg)
    if args.t0:
        rc = cmd_t0(reg)
    return rc

if __name__ == "__main__":
    sys.exit(main())
