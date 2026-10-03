import sys
sys.dont_write_bytecode = True

"""Queue dispatcher: pick the next QUEUED row of BUILD_PIPELINE.md and write a ready-to-run CL prompt.

One wake, one pick. Reads the pipeline fresh each run, so stale rows drop out. No Claude call, no network.
Writes MyTradingSys/runtime/queue/{next_task.txt, next_task.json, pick_log.jsonl}; a prior next_task.* is renamed
next_task_<prior_composed_utc>.* first. Prints `PICK <id> wave=<n> slug=<slug> surface=<App|CLI>` or `IDLE no pickable row`.
Exit 0 on PICK or IDLE, 1 on disk error (reason on stderr).
Test hook: env MTS_PICK_ROOT replaces the repo root.
Usage (repo root): python scripts/sched/pick_task.py
"""
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ.get("MTS_PICK_ROOT") or Path(__file__).resolve().parents[2])
PIPE = ROOT / "MyTradingSys" / "runtime" / "BUILD_PIPELINE.md"
BUGS = ROOT / "MyTradingSys" / "research" / "BUGS.md"
ITEMS = ROOT / "MyTradingSys" / "items"
QUEUE = ROOT / "MyTradingSys" / "runtime" / "queue"
BUG_ID = re.compile(r"^[BT]\d+$")
WAVE_RE = re.compile(r"^## WAVE (\d+)")
FILE_RE = re.compile(r"[\w./\\-]+\.(?:md|py|java|ps1|json|csv)\b")
ROWNUM_RE = re.compile(r"\b\d+\.\d+\b")
PICKABLE_BUGS = ("OPEN", "IN-FIX")
SURFACE = "App"

SIGNATURE = '"P.S : All Access, Change Repo/Device/All that you need!"'
DIRECTIVE = ('"I need all pending tasks to be in the continuous build and test workflow."\n'
             '"No step in the CI CD to stop."\n'
             '"Prefer simple accurate design that unblocks AI on Disk and Cloud."')


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def parse_pipeline(text):
    rows, wave = [], None
    for line in text.splitlines():
        m = WAVE_RE.match(line)
        if m:
            wave = int(m.group(1))
            continue
        if wave is None or not line.startswith("|"):
            continue
        c = cells(line)
        if len(c) >= 6 and re.match(r"^\d+\.\d+$", c[0]):
            rows.append({"num": c[0], "wave": wave, "id": c[1], "slug": c[2], "status": c[3], "blocker": c[4],
                         "next": "|".join(c[5:])})
    return rows


def parse_bugs(text):
    out = {}
    for line in text.splitlines():
        c = cells(line) if line.startswith("|") else []
        if len(c) >= 4 and BUG_ID.match(c[0]):
            out[c[0]] = c[2]
    return out


def landed_in_git(rid):
    try:
        p = subprocess.run(["git", "log", "-n", "1", "--format=%h", "-i", "-E", "--grep=^" + rid + ":"],
                           cwd=ROOT, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return False
    return p.returncode == 0 and bool(p.stdout.strip())


def item_doc(rid):
    hits = sorted(ITEMS.glob(rid + "_*.md")) if ITEMS.is_dir() else []
    return hits[0] if hits else None


def skip_reason(r, bugs, by_num):
    """None if pickable, else why not."""
    if r["status"] != "QUEUED":
        return "status " + r["status"]
    if "operator" in r["blocker"].lower():
        return "blocker names operator"
    for n in ROWNUM_RE.findall(r["blocker"]):
        dep = by_num.get(n)
        if dep is not None and dep["status"] != "LANDED":
            return "blocked on row " + n
    rid = r["id"]
    if BUG_ID.match(rid):
        if rid not in bugs:
            return "no BUGS row"
        if bugs[rid] not in PICKABLE_BUGS:
            return "BUGS status " + bugs[rid]
        if item_doc(rid) is None:
            return "no item doc"
        if landed_in_git(rid):
            return "commit already landed"
        return None
    if rid == "-":
        return "no id"
    if not FILE_RE.search(r["next"]):
        return "wave-only slug without a named file"
    return None


def slug_of(r):
    words = re.sub(r"[^a-z0-9]+", " ", r["slug"].lower()).split()[:3]
    return "-".join([re.sub(r"[^a-z0-9]+", "", r["id"].lower())] + words)


def compose(r, now, doc, session_id):
    read_first = [str(doc.relative_to(ROOT)).replace("\\", "/")] if doc else []
    read_first += [f.replace("\\", "/") for f in FILE_RE.findall(r["next"]) if f.replace("\\", "/") not in read_first]
    read_first += ["MyTradingSys/runtime/BUILD_PIPELINE.md (row %s)" % r["num"]]
    rid = r["id"]
    return "\n".join([
        "Session ID: " + session_id,
        "Surface: Claude Win App, Code mode. Where the App cannot reach the local repo filesystem or run a child",
        "process, state which, use CLI, and write the reason in the session record. CLI is fallback, not default.",
        "Repo root: " + str(ROOT) + "   Branch: fast-track",
        "",
        "OPERATOR SIGNATURE (verbatim): " + SIGNATURE,
        "OPERATOR DIRECTIVE (verbatim, 2026-10-03):",
        DIRECTIVE,
        "",
        "TASK: %s (wave %d, row %s) - %s" % (rid, r["wave"], r["num"], r["slug"]),
        "Blocker: %s | Next: %s" % (r["blocker"], r["next"]),
        "",
        "READ FIRST (CLAUDE.md, STATUS.md, LESSONS_LEARNED.md, then):",
        *["  " + p for p in read_first],
        "",
        "== T0 CONTRACT == Quote from disk, each with file and line number: the code or doc the row names, its current",
        "behaviour, and the register row for " + rid + ". Stop only on BLOCKED.",
        "== T1 WORK == Implement the fix named by the item doc and the row's Next cell. Staged work is <file>.new for any",
        "file a live process imports; back up to .pre_<tag> before promoting.",
        "== T2 TESTS == Tests derived from the spec; each must fail on the pre-change code at least once.",
        "== T3 GATE == python scripts/dev/run_all_tests.py --quick; Build-Check where the area needs it.",
        "== T4 CLOSE == Update the register row (receipt on CLOSED), the pipeline row, 03_FILE_INDEX for new files, the",
        "session record; commit on fast-track with prefix \"" + rid + ": \".",
        "== T5 MISSED == Name every deviation.",
        "",
        "MARKERS: '== T<n> <name> ==' at start, 'T<n> PASS|FAIL|BLOCKED <result>' at end, no wait between tasks.",
        "SPAWNING: CL runs commands as subprocesses (python, PowerShell, git). Spawning is expected; stopping to ask",
        "whether it is allowed is a defect.",
        "DO NOT STOP OR KILL: java, auto_trader, daily_loss_monitor, live_runner_cli, orderflow_live, supervisor,",
        "the loop wrapper.",
        "STAGE DISCIPLINE: stage only the exact paths you wrote; list staged paths before committing; a staged path you",
        "did not write means stop and do not commit.",
        "",
        "Every file: LF, no BOM, no trailing whitespace. All timestamps UTC. Reply 25 lines max.",
        ""])


def atomic_write(path, text):
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    tmp.replace(path)


def archive_prior(now):
    txt, js = QUEUE / "next_task.txt", QUEUE / "next_task.json"
    if not txt.exists() and not js.exists():
        return
    stamp = None
    try:
        stamp = json.loads(js.read_text(encoding="utf-8")).get("composed_utc")
    except (OSError, ValueError, AttributeError):
        pass
    if stamp:
        stamp = re.sub(r"[-:]", "", stamp)
    else:
        src = txt if txt.exists() else js
        stamp = datetime.fromtimestamp(src.stat().st_mtime, timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for p in (txt, js):
        if p.exists():
            dest = QUEUE / ("next_task_%s%s" % (stamp, p.suffix))
            n = 1
            while dest.exists():
                dest = QUEUE / ("next_task_%s_%d%s" % (stamp, n, p.suffix))
                n += 1
            p.replace(dest)


def log_line(entry):
    with open(QUEUE / "pick_log.jsonl", "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")


def main():
    now = datetime.now(timezone.utc)
    iso = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        rows = parse_pipeline(PIPE.read_text(encoding="utf-8"))
        bugs = parse_bugs(BUGS.read_text(encoding="utf-8")) if BUGS.exists() else {}
    except OSError as e:
        print("pick_task: cannot read inputs: %s" % e, file=sys.stderr)
        return 1
    by_num = {r["num"]: r for r in rows}
    chosen = next((r for r in sorted(rows, key=lambda r: (r["wave"], [int(x) for x in r["num"].split(".")]))
                   if skip_reason(r, bugs, by_num) is None), None)
    try:
        QUEUE.mkdir(parents=True, exist_ok=True)
        archive_prior(now)
        if chosen is None:
            atomic_write(QUEUE / "next_task.txt", "IDLE no pickable row\n")
            log_line({"ts": iso, "result": "IDLE"})
            print("IDLE no pickable row")
            return 0
        slug = slug_of(chosen)
        session_id = "MTS-%s-%sZ-CL-BLD-%s" % (now.strftime("%Y-%m-%d"), now.strftime("%H%M"), slug)
        doc = item_doc(chosen["id"]) if BUG_ID.match(chosen["id"]) else None
        meta = {"id": chosen["id"], "wave": chosen["wave"], "slug": slug, "surface": SURFACE,
                "item_doc": str(doc.relative_to(ROOT)).replace("\\", "/") if doc else None, "composed_utc": iso,
                "session_id": session_id}
        atomic_write(QUEUE / "next_task.txt", compose(chosen, now, doc, session_id))
        atomic_write(QUEUE / "next_task.json", json.dumps(meta, indent=1) + "\n")
        log_line({"ts": iso, "result": "PICK", **{k: meta[k] for k in ("id", "wave", "slug", "surface")}})
    except OSError as e:
        print("pick_task: disk error: %s" % e, file=sys.stderr)
        return 1
    print("PICK %s wave=%d slug=%s surface=%s" % (chosen["id"], chosen["wave"], slug, SURFACE))
    return 0


if __name__ == "__main__":
    sys.exit(main())
