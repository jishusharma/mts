import sys
sys.dont_write_bytecode = True

"""Queue dispatcher: pick the next QUEUED row of BUILD_PIPELINE.md and write a ready-to-run CL prompt.

One wake, one or more picks (B093). Reads the pipeline fresh each run, so stale rows drop out. No Claude call, no network.
Writes MyTradingSys/runtime/queue/{next_task.txt, next_task.json, pick_log.jsonl, pick_state.json}; a prior next_task.*
is renamed next_task_<prior_composed_utc>.* first. Prints `PICK <id> wave=<n> slug=<slug> surface=<App|CLI>`,
`HOLD <id> ...` or `IDLE no pickable row`.
Bug sweep (B089): an OPEN or IN-FIX id in BUGS.md with no pipeline row in any wave is a candidate too, in one wave
after the last pipeline wave (file order), so a bug filed without a pipeline row is never invisible. Pipeline rows
always go first; an id with any pipeline row is governed by that row only.
Parallel dispatch (B093, shape B, by file set): a wake keeps up to MTS_PICK_SLOTS (default 3) rows active. A new row
is picked only when its file set (file_set: names in its Next cell and item doc, shared registers excluded) is disjoint
from every held and newly picked row; an unknown (empty) file set conflicts with all, so one writer per file set holds
(B086). Each active row has its prompt in queue/slots/<id>.txt|json; next_task.* mirrors the first active row, so
`mts go` is unchanged. Slots of rows that leave the active set move to slots/released/. Output: one PICK/HOLD line
per active row.
Re-pick guard (B087a): pick_state.json records each pick. A picked row that is still pickable is HELD (its prompt left
untouched; rows on a conflicting file set are not offered: one writer per file set) for the cooldown (env MTS_PICK_COOLDOWN_H hours; default
= check_sessions.MAX_OPEN, the window after which an open session counts as stale, SCHEDULER_PLAN_2026-10-02 s5 #5;
B088). After the cooldown it is offered again, so a row whose session died never starves. A row that stops being
pickable (landed, blocked, status change) drops out of the state at once.
Session id (B088): MTS-<UTC>-CLI-BLD-<slug>; CLI is the SURFACE_POLICY section 4 code; go.py builds names here.
Exit 0 on PICK or IDLE, 1 on disk error (reason on stderr).
Test hook: env MTS_PICK_ROOT replaces the repo root.
Usage (repo root): python scripts/sched/pick_task.py
"""
import json
import os
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_sessions import MAX_OPEN as STALE_SESSION  # B088: one definition of a dead session

ROOT =Path(os.environ.get("MTS_PICK_ROOT") or Path(__file__).resolve().parents[2])
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
SURF, ROLE = "CLI", "BLD"  # session-id codes, SURFACE_POLICY section 4
SLUG_MAX = 20
STATE_NAME = "pick_state.json"
SLOTS = QUEUE / "slots"  # B093: one prompt per active pick, slots/<id>.txt + .json; next_task.* mirrors the first
SLOT_CAP = 3
# Register and index files every close touches (append-only rows); not a file set, never a collision key.
SHARED = {"bugs.md", "build_pipeline.md", "index.md", "status.md", "lessons_learned.md", "03_file_index.md",
          "supervisor_log.md"}

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


def parse_bug_rows(text):
    """[(id, status, title)] in file order, both register tables."""
    out = []
    for line in text.splitlines():
        c = cells(line) if line.startswith("|") else []
        if len(c) >= 4 and BUG_ID.match(c[0]):
            out.append((c[0], c[2], c[4] if len(c) > 4 else ""))
    return out


def parse_bugs(text):
    return {rid: status for rid, status, _ in parse_bug_rows(text)}


def sweep_rows(rows, bug_rows):
    """B089: OPEN / IN-FIX register ids with no pipeline row, as QUEUED rows of one wave after the last."""
    have = {r["id"] for r in rows}
    wave = max((r["wave"] for r in rows), default=0) + 1
    out = []
    for rid, status, title in bug_rows:
        if status in PICKABLE_BUGS and rid not in have:
            have.add(rid)
            out.append({"num": "%d.%d" % (wave, len(out) + 1), "wave": wave, "id": rid, "slug": title or rid,
                        "status": "QUEUED", "blocker": "-", "next": "MyTradingSys/research/BUGS.md row " + rid,
                        "source": "bugs"})
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
    return "-".join([re.sub(r"[^a-z0-9]+", "", r["id"].lower())] + words)[:SLUG_MAX].rstrip("-")


def cooldown():
    try:
        return timedelta(hours=float(os.environ["MTS_PICK_COOLDOWN_H"]))
    except (KeyError, ValueError):
        return STALE_SESSION


def session_id(slug, now):
    return "MTS-%s-%sZ-%s-%s-%s" % (now.strftime("%Y-%m-%d"), now.strftime("%H%M"), SURF, ROLE, slug)


def load_state():
    """{id: {"picked_utc": iso, "count": n}}; missing or corrupt file means no history (a pick is never blocked by it)."""
    try:
        d = json.loads((QUEUE / STATE_NAME).read_text(encoding="utf-8"))
        return {k: v for k, v in d.items() if isinstance(v, dict) and isinstance(v.get("picked_utc"), str)}
    except (OSError, ValueError, AttributeError):
        return {}


def held_rows(candidates, state, now):
    """Every pickable row picked within the cooldown, in order. Unparseable stamps count as expired."""
    out = []
    for r in candidates:
        e = state.get(r["id"])
        if not e:
            continue
        try:
            at = datetime.strptime(e["picked_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        if timedelta(0) <= now - at < cooldown():
            out.append(r)
    return out


def held_row(candidates, state, now):
    """First held row, else None."""
    h = held_rows(candidates, state, now)
    return h[0] if h else None


def slot_cap():
    try:
        return max(1, int(os.environ["MTS_PICK_SLOTS"]))
    except (KeyError, ValueError):
        return SLOT_CAP


def file_set(r):
    """B093: lower-cased basenames the row writes: files named in its Next cell and its item doc, minus the item doc
    itself and the shared registers. Over-inclusion only costs parallelism; an empty set is unknown and fails closed
    (see conflicts)."""
    doc = item_doc(r["id"]) if BUG_ID.match(r["id"]) else None
    text = r["next"] + (" " + doc.read_text(encoding="utf-8", errors="replace") if doc else "")
    names = {f.replace("\\", "/").rsplit("/", 1)[-1].lower() for f in FILE_RE.findall(text)}
    if doc:
        names.discard(doc.name.lower())
    return names - SHARED


def conflicts(a, b):
    """True when two file sets may share a writer. An empty (unknown) set conflicts with everything."""
    return not a or not b or bool(a & b)


def pick_more(pickable, held, cap):
    """B093 shape B: new picks, in queue order, whose file set is disjoint from every held and already-new pick,
    up to cap active rows in all. A row blocked by a held file set is skipped, not waited on, so it never blocks
    the rows behind it; it is offered again once the holder lands, goes stale or leaves the queue."""
    claimed = [file_set(r) for r in held]
    held_ids = {r["id"] for r in held}
    out = []
    for r in pickable:
        if len(held) + len(out) >= cap:
            break
        if r["id"] in held_ids:
            continue
        fs = file_set(r)
        if any(conflicts(fs, c) for c in claimed):
            continue
        claimed.append(fs)
        out.append(r)
    return out


def compose(r, now, doc, session_id):
    read_first = [str(doc.relative_to(ROOT)).replace("\\", "/")] if doc else []
    read_first += [f.replace("\\", "/") for f in FILE_RE.findall(r["next"]) if f.replace("\\", "/") not in read_first]
    if r.get("source") == "bugs":
        read_first += ["MyTradingSys/runtime/BUILD_PIPELINE.md (no row: swept from BUGS.md, B089; on close add a "
                       "LANDED row for the record)"]
    else:
        read_first += ["MyTradingSys/runtime/BUILD_PIPELINE.md (row %s)" % r["num"]]
    rid = r["id"]
    return "\n".join([
        "SURFACE: APP",
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
        "== T4 CLOSE == Update the register row (receipt on CLOSED), the pipeline row, the",
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


def current_pick_id():
    """Id in next_task.json, or None when there is no live prompt (IDLE, missing, unreadable)."""
    try:
        return json.loads((QUEUE / "next_task.json").read_text(encoding="utf-8")).get("id")
    except (OSError, ValueError, AttributeError):
        return None


def write_slot(r, now, iso):
    slug = slug_of(r)
    sid = session_id(slug, now)
    doc = item_doc(r["id"]) if BUG_ID.match(r["id"]) else None
    meta = {"id": r["id"], "wave": r["wave"], "slug": slug, "surface": SURFACE,
            "item_doc": str(doc.relative_to(ROOT)).replace("\\", "/") if doc else None, "composed_utc": iso,
            "session_id": sid, "source": r.get("source", "pipeline")}
    atomic_write(SLOTS / (r["id"] + ".txt"), compose(r, now, doc, sid))
    atomic_write(SLOTS / (r["id"] + ".json"), json.dumps(meta, indent=1) + chr(10))
    return meta


def release_slots(active_ids, now):
    """Move slot prompts of rows that are no longer active into slots/released/ (moves, never deletes)."""
    rel = SLOTS / "released"
    for p in sorted(SLOTS.glob("*.*")):
        if p.suffix in (".txt", ".json") and p.stem not in active_ids:
            rel.mkdir(exist_ok=True)
            dest = rel / ("%s_%s%s" % (p.stem, now.strftime("%Y%m%dT%H%M%SZ"), p.suffix))
            n = 1
            while dest.exists():
                dest = rel / ("%s_%s_%d%s" % (p.stem, now.strftime("%Y%m%dT%H%M%SZ"), n, p.suffix))
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
        bug_rows = parse_bug_rows(BUGS.read_text(encoding="utf-8")) if BUGS.exists() else []
    except OSError as e:
        print("pick_task: cannot read inputs: %s" % e, file=sys.stderr)
        return 1
    bugs = {rid: status for rid, status, _ in bug_rows}
    by_num = {r["num"]: r for r in rows}  # pipeline rows only: a swept row never satisfies or blocks a dependency
    ordered = sorted(rows + sweep_rows(rows, bug_rows),
                     key=lambda r: (r["wave"], [int(x) for x in r["num"].split(".")]))
    pickable = [r for r in ordered if skip_reason(r, bugs, by_num) is None]
    state = load_state()
    state = {k: v for k, v in state.items() if k in {r["id"] for r in pickable}}
    held = held_rows(pickable, state, now)
    fresh = pick_more(pickable, held, slot_cap())
    active = [r for r in pickable if r in held or r in fresh]
    lines = []
    try:
        QUEUE.mkdir(parents=True, exist_ok=True)
        SLOTS.mkdir(parents=True, exist_ok=True)
        release_slots({r["id"] for r in active}, now)
        if not active:
            archive_prior(now)
            atomic_write(QUEUE / STATE_NAME, "{}" + chr(10))
            atomic_write(QUEUE / "next_task.txt", "IDLE no pickable row" + chr(10))
            log_line({"ts": iso, "result": "IDLE"})
            print("IDLE no pickable row")
            return 0
        first = active[0]["id"]
        for r in active:
            rid = r["id"]
            slot_ok = (SLOTS / (rid + ".txt")).is_file() and (SLOTS / (rid + ".json")).is_file()
            if rid in {h["id"] for h in held} and slot_ok and (rid != first or current_pick_id() is not None):
                lines.append("HOLD %s picked %s, cooldown %sh" % (rid, state[rid]["picked_utc"],
                                                                  cooldown().total_seconds() / 3600))
                log_line({"ts": iso, "result": "HOLD", "id": rid})
                continue
            meta = write_slot(r, now, iso)
            state[rid] = {"picked_utc": iso, "count": state.get(rid, {}).get("count", 0) + 1}
            log_line({"ts": iso, "result": "PICK", **{k: meta[k] for k in ("id", "wave", "slug", "surface", "source")}})
            lines.append("PICK %s wave=%d slug=%s surface=%s source=%s slot=%s" % (
                rid, r["wave"], meta["slug"], SURFACE, meta["source"], "queue/slots/" + rid + ".txt"))
        if current_pick_id() != first:
            archive_prior(now)
            for ext in (".txt", ".json"):
                atomic_write(QUEUE / ("next_task" + ext), (SLOTS / (first + ext)).read_text(encoding="utf-8"))
        atomic_write(QUEUE / STATE_NAME, json.dumps(state, indent=1, sort_keys=True) + chr(10))
    except OSError as e:
        print("pick_task: disk error: %s" % e, file=sys.stderr)
        return 1
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
