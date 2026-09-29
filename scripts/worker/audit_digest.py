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
    # entries may be the bare finding hash or the displayed '<task_id>:<hash>' form
    return {str(x).rsplit(":", 1)[-1] for x in json.loads(CLOSED_PATH.read_text(encoding="utf-8"))}

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
        tm = re.match(r"Audit \((A[1-7])\)", task.get("task", ""))
        yield (task_id, reply.get("response") or "", reply.get("finished_utc") or "", tm.group(1) if tm else "")

FINDING_START_RE = re.compile(r"^[\s>*_#`-]*FINDING\s*#?\s*\d*[\s*_]*[|:]", re.I)
FINDINGS_LINE_RE = re.compile(r"^[\s>*_#`-]*FINDINGS\b", re.I)
PATHLINE_RE = re.compile(r"([A-Za-z0-9_./\\-]+\.[A-Za-z0-9]+):(\d+)(?:\s*-\s*\d+)?")
SEV_RE = re.compile(r"\b(HIGH|MEDIUM|LOW|H|M|L)\b", re.I)
TEMPLATE_RE = re.compile(r"^[*_` ]*A([1-7])[*_` ]*$")
FIELD_RE = re.compile(r"^[\s>*_#`-]*(QUOTE|WHY|FIX)\s*[*_]*\s*:\s*[*_]*\s*(.*)$", re.I)


def _clean_quote(q: str) -> str:
    q = q.strip().strip("*_").strip()
    for _ in range(2):
        if len(q) >= 2 and q[0] == q[-1] and q[0] in "\"'`":
            q = q[1:-1].strip()
    return q


def _parse_header(line: str):
    """Return (template, severity, path, lineno, tail_parts) or None."""
    body = FINDING_START_RE.sub("", line, count=1)
    parts = [x.strip() for x in body.split("|")]
    pidx = -1
    for idx, part in enumerate(parts):
        m = PATHLINE_RE.search(part)
        if m:
            pidx = idx
            break
    if pidx < 0:
        return None
    path = m.group(1).replace("\\", "/").strip("`*_ ")
    lineno = int(m.group(2))
    template = ""
    sev = None
    for part in parts[:pidx]:
        t = TEMPLATE_RE.match(part)
        if t and not template:
            template = "A" + t.group(1)
            continue
        s = SEV_RE.search(part)
        if s and sev is None:
            sev = s.group(1).upper()[0]
    return template, sev or "M", path, lineno, parts[pidx + 1:]


def parse_findings_ex(task_id: str, response_text: str, default_template: str = ""):
    """Return (findings, n_malformed). Tolerates markdown bold, quoted QUOTE values, HIGH/MEDIUM/LOW
    or H/M/L severities, non-A1..A7 ids, blank lines between fields, and the one-line pipe form."""
    lines = response_text.splitlines()
    findings = []
    malformed = 0
    i = 0
    while i < len(lines):
        if FINDINGS_LINE_RE.match(lines[i]) or not FINDING_START_RE.match(lines[i]):
            i += 1
            continue
        hdr = _parse_header(lines[i])
        j = i + 1
        fields = {}
        while (j < len(lines) and not FINDING_START_RE.match(lines[j])
               and lines[j].strip().strip("*_ ") != "NO FINDINGS"
               and not re.match(r"^(<<<|===)", lines[j])):
            fm = FIELD_RE.match(lines[j])
            if fm:
                fields.setdefault(fm.group(1).upper(), fm.group(2).strip().strip("*_").strip())
            j += 1
        if hdr is None:
            malformed += 1
            i = j
            continue
        template, sev, path, lineno, tail = hdr
        if not fields and len(tail) >= 3:
            fields = {"QUOTE": tail[0], "WHY": tail[1], "FIX": " | ".join(tail[2:])}
        if not all(k in fields for k in ("QUOTE", "WHY", "FIX")) or not _clean_quote(fields["QUOTE"]):
            malformed += 1
            i = j
            continue
        findings.append({
            "task_id": task_id,
            "template": template or default_template or "A?",
            "severity": sev,
            "path": path,
            "line": lineno,
            "quote": _clean_quote(fields["QUOTE"]),
            "why": fields["WHY"],
            "fix": fields["FIX"],
        })
        i = j
    return findings, malformed


def parse_findings(task_id: str, response_text: str, default_template: str = "") -> list:
    return parse_findings_ex(task_id, response_text, default_template)[0]


def _norm(s: str) -> str:
    return " ".join(s.split())


def quote_status(path: str, line: int, quote: str) -> str:
    """'ok', 'file_missing', 'line_off' or 'quote_not_found' (quote must appear in a line within +-3)."""
    target = REPO / path
    if not target.exists() or not target.is_file():
        return "file_missing"
    try:
        lines = target.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return "file_missing"
    q = _norm(quote)
    n = len(lines)
    for ln in range(max(1, line - 3), min(n, line + 3) + 1):
        if q and q in _norm(lines[ln - 1]):
            return "ok"
    if any(q and q in _norm(x) for x in lines):
        return "line_off"  # quote is in the file but not within +-3 of the claimed line
    return "quote_not_found"


def quote_matches(path: str, line: int, quote: str) -> bool:
    return quote_status(path, line, quote) == "ok"


def finding_id(path: str, quote: str) -> str:
    return hashlib.sha1((path + "|" + quote).encode("utf-8")).hexdigest()[:10]

def render_digest(findings: list, closed_count: int, dropped_unconfirmed, dup_count: int = 0) -> str:
    reasons = {}
    if isinstance(dropped_unconfirmed, dict):
        reasons = {k: v for k, v in dropped_unconfirmed.items() if v}
        dropped_unconfirmed = sum(reasons.values())
    sev_rank = {"H": 0, "M": 1, "L": 2}
    findings = sorted(findings, key=lambda f: f.get("finished_utc") or "", reverse=True)
    findings = sorted(findings, key=lambda f: sev_rank.get(f["severity"], 3))
    findings = findings[:MAX_FINDINGS]
    now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).strftime('%Y-%m-%dT%H:%M:%SZ')
    lines = [
        "# Audit digest (T056)",
        f"Generated: {now}",
        f"Open findings shown: {len(findings)} (capped at {MAX_FINDINGS}). Closed: {closed_count}."
    ]
    if dropped_unconfirmed:
        lines.append(f"Dropped (QUOTE not confirmed near the claimed line): {dropped_unconfirmed}.")
    if reasons:
        lines.append("Dropped by reason: " + ", ".join(f"{k}={v}" for k, v in sorted(reasons.items()))
                     + f"; duplicates merged={dup_count}.")
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
    reasons = {"malformed": 0, "file_missing": 0, "line_off": 0, "quote_not_found": 0}
    for task_id, response, ts, tmpl in iter_audit_tasks():
        found, bad = parse_findings_ex(task_id, response, tmpl)
        reasons["malformed"] += bad
        for f in found:
            f["finished_utc"] = ts
            st = quote_status(f["path"], f["line"], f["quote"])
            if st != "ok":
                reasons[st] += 1
                continue
            fid = finding_id(f["path"], f["quote"])
            if fid in closed:
                continue
            f["_id"] = fid
            all_found.append(f)
    dropped = sum(reasons.values())
    # Dedupe by _id, keeping first occurrence
    seen = set()
    deduped = []
    for f in all_found:
        if f["_id"] not in seen:
            seen.add(f["_id"])
            deduped.append(f)
    dup_count = len(all_found) - len(deduped)
    sev_rank = {"H": 0, "M": 1, "L": 2}
    deduped.sort(key=lambda f: f["finished_utc"], reverse=True)
    deduped.sort(key=lambda f: sev_rank.get(f["severity"], 3))
    deduped = deduped[:MAX_FINDINGS]
    rendered = render_digest(deduped, len(closed), reasons, dup_count)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT_PATH.with_name("." + OUT_PATH.name + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(rendered)
    os.replace(tmp, OUT_PATH)
    shown = len(deduped) if deduped else 0
    print(f"WROTE {OUT_PATH}: {shown} shown, {len(closed)} closed, {dropped} dropped")
    print("dropped by reason: " + ", ".join(f"{k}={v}" for k, v in reasons.items()) + f"; duplicates merged={dup_count}")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(run_digest())
