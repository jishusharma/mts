import sys
sys.dont_write_bytecode = True

import json
import os
import re
import hashlib
import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DONE_DIR = REPO / "Dumps" / "workers" / "NUC-QUEUE" / "done"
OUT_PATH = REPO / "MyTradingSys" / "research" / "audits" / "AUDIT_DIGEST.md"
CLOSED_PATH = REPO / "MyTradingSys" / "research" / "audits" / "AUDIT_DIGEST_CLOSED.json"
MAX_FINDINGS = 40
FINDING_HEADER_RE = re.compile(r"^FINDING\s+\d+\s*\|\s*(A[1-7])\s*\|\s*severity\s+([HML])\s*\|\s*(.+):(\d+)\s*$")

def load_closed_ids() -> set:
    if not CLOSED_PATH.exists():
        return set()
    return set(json.loads(CLOSED_PATH.read_text(encoding="utf-8")))

def iter_audit_tasks():
    if not DONE_DIR.exists():
        return
    for p in sorted(DONE_DIR.glob("*.task.json")):
        task_id = p.name[:-len(".task.json")]
        task = json.loads(p.read_text(encoding="utf-8"))
        if not task.get("task", "").startswith("Audit ("):
            continue
        verdict_path = DONE_DIR / f"{task_id}.verdict.txt"
        if not verdict_path.exists():
            continue
        verdict_text = verdict_path.read_text(encoding="utf-8")
        if "verdict FAIL" in verdict_text:
            continue
        reply_path = DONE_DIR / f"{task_id}.reply.json"
        if not reply_path.exists():
            continue
        reply = json.loads(reply_path.read_text(encoding="utf-8"))
        yield (task_id, reply.get("response") or "", reply.get("finished_utc") or "")

def parse_findings(task_id: str, response_text: str) -> list:
    lines = response_text.splitlines()
    findings = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = FINDING_HEADER_RE.match(line)
        if not m:
            i += 1
            continue
        if i + 3 >= len(lines):
            i += 1
            continue
        quote_line = lines[i + 1]
        why_line = lines[i + 2]
        fix_line = lines[i + 3]
        if not quote_line.startswith("QUOTE:"):
            i += 1
            continue
        if not why_line.startswith("WHY:"):
            i += 1
            continue
        if not fix_line.startswith("FIX:"):
            i += 1
            continue
        findings.append({
            "task_id": task_id,
            "template": m.group(1),
            "severity": m.group(2),
            "path": m.group(3).strip(),
            "line": int(m.group(4)),
            "quote": quote_line[6:].strip(),
            "why": why_line[4:].strip(),
            "fix": fix_line[4:].strip()
        })
        i += 4
    if not findings and any(line.strip() == "NO FINDINGS" for line in lines):
        return []
    return findings

def quote_matches(path: str, line: int, quote: str) -> bool:
    target = REPO / path
    if not target.exists() or not target.is_file():
        return False
    try:
        lines = target.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return False
    n = len(lines)
    for ln in range(max(1, line - 3), min(n, line + 3) + 1):
        if lines[ln - 1].strip() == quote.strip():
            return True
    return False

def finding_id(path: str, quote: str) -> str:
    return hashlib.sha1((path + "|" + quote).encode("utf-8")).hexdigest()[:10]

def render_digest(findings: list, closed_count: int, dropped_unconfirmed: int) -> str:
    findings = sorted(findings, key=lambda f: f.get("finished_utc") or "", reverse=True)[:MAX_FINDINGS]
    now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).strftime('%Y-%m-%dT%H:%M:%SZ')
    lines = [
        "# Audit digest (T056)",
        f"Generated: {now}",
        f"Open findings shown: {len(findings)} (capped at {MAX_FINDINGS}). Closed: {closed_count}."
    ]
    if dropped_unconfirmed:
        lines.append(f"Dropped (QUOTE not confirmed near the claimed line): {dropped_unconfirmed}.")
    lines.append("")
    if not findings:
        lines.append("(no open findings)")
    else:
        for f in findings:
            lines.append(
                f"- [{f['task_id']}:{finding_id(f['path'], f['quote'])}] {f['template']} {f['severity']} "
                f"{f['path']}:{f['line']} | {f['why']} | fix: {f['fix']}"
            )
    return "\n".join(lines)

def run_digest() -> int:
    closed = load_closed_ids()
    all_found = []
    dropped = 0
    for task_id, response, ts in iter_audit_tasks():
        for f in parse_findings(task_id, response):
            f["finished_utc"] = ts
            if not quote_matches(f["path"], f["line"], f["quote"]):
                dropped += 1
                continue
            fid = finding_id(f["path"], f["quote"])
            if fid in closed:
                continue
            f["_id"] = fid
            all_found.append(f)
    # Dedupe by _id, keeping first occurrence
    seen = set()
    deduped = []
    for f in all_found:
        if f["_id"] not in seen:
            seen.add(f["_id"])
            deduped.append(f)
    # Sort by finished_utc descending (most recent first)
    deduped.sort(key=lambda f: f["finished_utc"], reverse=True)
    # Truncate to MAX_FINDINGS
    deduped = deduped[:MAX_FINDINGS]
    rendered = render_digest(deduped, len(closed), dropped)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT_PATH.with_name("." + OUT_PATH.name + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(rendered)
    os.replace(tmp, OUT_PATH)
    shown = len(deduped) if deduped else 0
    print(f"WROTE {OUT_PATH}: {shown} shown, {len(closed)} closed, {dropped} dropped")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(run_digest())
