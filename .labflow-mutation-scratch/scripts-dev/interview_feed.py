"""Interview feed: learning notes that may leave the repo for the Interview Prep project (RUN_MODEL.md section 7).

A note qualifies when MyTradingSys/learning/*.md starts with YAML front matter containing `interview: yes`. Before a copy leaves,
it is refused (reported and skipped) when it holds an absolute Windows path into a user folder, `.secrets`, a token or key
pattern, a runtime_data reference, or is over the size cap. Nothing outside the learning folder is read.

  python scripts/dev/interview_feed.py list
  python scripts/dev/interview_feed.py export [--to DIR] [--max-kb 200]
`export` without --to uses env MTS_INTERVIEW_DIR; with neither it only prints what would be exported (a dry run).
Exit code 0 always, also when notes were refused: refusals are in the report.
"""
import argparse
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LEARNING = REPO / "MyTradingSys" / "learning"
MAX_KB = 200
REFUSE = (
    ("absolute Windows user path", re.compile(r"[A-Za-z]:[\\/]+(?:Users|Documents and Settings)[\\/]", re.I)),
    ("absolute user path", re.compile(r"(?:/Users/|/home/)[\w.-]+/")),
    (".secrets reference", re.compile(r"\.secrets\b")),
    ("runtime_data reference", re.compile(r"runtime_data")),
    ("token or key", re.compile(
        r"\b(?:sk-[A-Za-z0-9_-]{16,}|ghp_[A-Za-z0-9]{20,}|github_pat_\w{20,}|AKIA[0-9A-Z]{12,}|xox[abprs]-[A-Za-z0-9-]{10,}|AIza[0-9A-Za-z_-]{30,})"
        r"|-----BEGIN [A-Z ]*PRIVATE KEY-----"
        r"|(?:api[_-]?key|secret|token|password|passwd)\s*[:=]\s*['\"]?[A-Za-z0-9+/_-]{12,}", re.I)),
)


def front_matter(text):
    """{key: value} of a leading `---` block, {} when there is none. Flat `key: value` lines only."""
    lines = text.lstrip("﻿").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    meta = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return meta
        m = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*?)\s*$", line)
        if m:
            meta[m.group(1).lower()] = m.group(2).strip("'\"")
    return {}       # never closed: not front matter


def wanted(meta):
    return meta.get("interview", "").lower() in ("yes", "true")


def problems(text, size_bytes, max_kb=MAX_KB):
    """Why a note may not leave the repo: list of reasons, empty when it may."""
    out = []
    if size_bytes > max_kb * 1024:
        out.append(f"over the size cap ({size_bytes // 1024} KB > {max_kb} KB)")
    for label, rx in REFUSE:
        m = rx.search(text)
        if m:
            out.append(f"{label}: {m.group(0)[:40]!r}")
    return out


def scan(folder=None, max_kb=MAX_KB):
    """[(path, meta, reasons)] for every learning note with `interview: yes`, sorted by name."""
    out = []
    for p in sorted(Path(folder or LEARNING).glob("*.md")):
        raw = p.read_bytes()
        text = raw.decode("utf-8", "replace")
        meta = front_matter(text)
        if wanted(meta):
            out.append((p, meta, problems(text, len(raw), max_kb)))
    return out


def index_md(items):
    lines = ["# Interview Prep inbox", "", "Exported by scripts/dev/interview_feed.py. One line per note.", ""]
    for p, meta in items:
        lines.append(f"- [{meta.get('topic') or p.stem}]({p.name}) | level: {meta.get('level', '?')} | date: {meta.get('date', '?')}")
    return "\n".join(lines) + "\n"


def cmd_list(folder=None, max_kb=MAX_KB, out=print):
    rows = scan(folder, max_kb)
    for p, meta, why in rows:
        out(f"{'REFUSED' if why else 'ok     '} {p.name}  {meta.get('topic', '')}" + (f"  <- {'; '.join(why)}" if why else ""))
    if not rows:
        out("no learning notes with `interview: yes`")
    return rows


def cmd_export(to=None, folder=None, max_kb=MAX_KB, out=print):
    rows = cmd_list(folder, max_kb, out)
    good = [(p, meta) for p, meta, why in rows if not why]
    refused = len(rows) - len(good)
    target = to or os.environ.get("MTS_INTERVIEW_DIR")
    if not target:
        out(f"dry run (no --to, no MTS_INTERVIEW_DIR): would export {len(good)} note(s), refuse {refused}")
        return 0
    d = Path(target)
    d.mkdir(parents=True, exist_ok=True)
    for p, _ in good:
        (d / p.name).write_text(p.read_text(encoding="utf-8", errors="replace"), encoding="utf-8", newline="\n")
    (d / "INDEX.md").write_text(index_md(good), encoding="utf-8", newline="\n")
    out(f"exported {len(good)} note(s) + INDEX.md to {d}; refused {refused}")
    return len(good)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    e = sub.add_parser("export")
    e.add_argument("--to")
    e.add_argument("--max-kb", type=int, default=MAX_KB)
    a = ap.parse_args(argv)
    if a.cmd == "list":
        cmd_list()
    else:
        cmd_export(a.to, max_kb=a.max_kb)
    return 0


if __name__ == "__main__":
    sys.exit(main())
