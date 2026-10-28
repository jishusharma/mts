"""Status dashboard: `python scripts/dev/status_board.py` prints the operator's whole status as markdown tables, to be pasted inline in chat.

Operator 2026-10-28 (d-status-is-inline-dashboard): "status" means this board, in the chat, no links. Stdlib only. Every section runs in its
own try/except, so one failure prints `NOT_IN_DATA: <why>` and the rest still print. Reads only: git log, task cards, signal lines,
disk_usage, top-level Temp entries (no tree scans). Numbers come from commands run now; what cannot be measured says NOT_IN_DATA.
"""
import functools
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))
ND = "NOT_IN_DATA"
STUCK_H = 24


def table(headers, rows):
    """Markdown table lines; cells are stringified, pipes escaped."""
    cell = lambda v: str(v).replace("|", "/").replace("\n", " ")
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    out += ["| " + " | ".join(cell(c) for c in r) + " |" for r in rows]
    return out


def nd(why):
    return f"{ND}: {why}"


def run(cmd, timeout=15, cwd=None):
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=str(cwd or REPO), encoding="utf-8", errors="replace")
    return p.stdout


# ---- pure parsers / formatters (tested with fake inputs) ---------------------------------------------------------------------------

BUDGET_RE = re.compile(r"^(\d{4})Z\s+\S+\s+\[note\]\s+BUDGET login=(\w+) 5h=(\d+)% week=(\d+)%(?: reset=(\S+))?")


def parse_budget(text):
    """Newest BUDGET line per login from `mts_signal.py read` text (oldest first). {login: (hhmm, five, week, reset)}."""
    out = {}
    for ln in text.splitlines():
        m = BUDGET_RE.match(ln.strip())
        if m:
            out[m.group(2)] = (m.group(1), int(m.group(3)), int(m.group(4)), m.group(5) or "?")
    return out


def fmt_budget(budget, closed_today, closed_yday, commits_today, commits_yday):
    lines = []
    if budget:
        lines += table(["Login", "5h used", "Week used", "Seen (UTC)", "Week resets"],
                       [[k, f"{v[1]}%", f"{v[2]}%", v[0][:2] + ":" + v[0][2:], v[3]] for k, v in sorted(budget.items())])
    else:
        lines.append(nd("no BUDGET lines in the signal read"))
    lines += [""] + table(["What it bought", "Today", "Yesterday"],
                          [["Cards closed", closed_today, closed_yday], ["Commits on trunk", commits_today, commits_yday]])
    lines.append("Spend vs output per login: NOT_IN_DATA (cards carry no login; a `closed_by_login` field would measure it).")
    return lines


def per_day(dates, days):
    """[(day, count)] for the given ISO day strings, in the order given."""
    return [(d, sum(1 for x in dates if x == d)) for d in days]


def gate_summary(rows, last=5, gap_s=300):
    """Wall seconds of each ship: rows sorted by utc, a new ship starts after a gap over gap_s; (median, [secs] of the last N) or None."""
    stamps = []
    for r in rows:
        try:
            stamps.append((datetime.fromisoformat(r["utc"].replace("Z", "+00:00")).timestamp(), float(r["secs"])))
        except (KeyError, ValueError, TypeError):
            pass
    ships, prev = [], None
    for ts, secs in sorted(stamps):
        if prev is None or ts - prev > gap_s:
            ships.append(0.0)
        ships[-1] += secs
        prev = ts
    ships = ships[-last:]
    return (statistics.median(ships), [round(x) for x in ships]) if ships else None


def red_minutes(runs, now=None):
    """Minutes the newest finished CI run has been red (since the oldest run of the current failing streak); 0 when green."""
    now = now or datetime.now(timezone.utc)
    first = None
    for r in (r for r in runs if r.get("conclusion") in ("success", "failure", "timed_out", "startup_failure")):
        if r["conclusion"] == "success":
            break
        first = r
    if not first:
        return 0
    return int((now - datetime.fromisoformat(first["created_at"].replace("Z", "+00:00"))).total_seconds() // 60)


def fmt_speed(commit_days, ci_runs, red_min, gate, ships):
    lines = table(["Trunk day (UTC)", "Commits"], commit_days) + [""]
    if ci_runs:
        lines += table(["CI last 6 (UTC)", "Result", "Commit"],
                       [[r.get("created_at", "?")[5:16].replace("T", " "), r.get("conclusion") or "running", r.get("head_sha", "")[:8]] for r in ci_runs[:6]])
        lines.append(f"Red now: {red_min} min" if red_min else "Red now: 0 min (green)")
    else:
        lines.append(nd("CI runs unavailable (offline or rate limited)"))
    lines.append(f"Gate wall time, median of last {len(gate[1])} ships: {gate[0]:.0f} s {gate[1]}" if gate else "Gate wall time: " + nd("no gate_timing.jsonl rows"))
    lines.append(ships)
    return lines


def old_hours(utc, now):
    try:
        return (now - datetime.fromisoformat(utc.replace("Z", "+00:00"))).total_seconds() / 3600
    except (ValueError, AttributeError):
        return 0.0


def fmt_value(done_titles, cleanup, stuck, stale_claims):
    lines = table(["Solved today (top 5)"], [[t[:90]] for t in done_titles[:5]]) if done_titles else ["Solved today: none yet"]
    lines += ["", f"Dedupe/cleanup commits today: {len(cleanup)}" + ("  e.g. " + "; ".join(c[:60] for c in cleanup[:2]) if cleanup else ""),
              f"Stuck: {len(stuck)} active card(s) older than {STUCK_H} h" + ("  " + ", ".join(stuck[:3]) if stuck else ""),
              f"Stale claims (over {STUCK_H} h): {len(stale_claims)}" + ("  " + "; ".join(s[:70] for s in stale_claims[:3]) if stale_claims else "")]
    return lines


def stale_claims(text):
    """['owner: task (Nh)'] from `sync.py claims` lines ending STALE."""
    out = []
    for ln in text.splitlines():
        m = re.match(r"claim (\S+): (\S+) / \S+ - .*?(\d+)h old STALE", ln)
        if m:
            out.append(f"{m.group(2)}: {m.group(1)} ({m.group(3)}h)")
    return out


def count_open(cards, weights=("CRITICAL", "CRUCIAL")):
    openc = [c for c in cards if c.get("state") not in ("done", "dropped")]
    return {w: sum(1 for c in openc if c.get("weight") == w) for w in weights}


def fmt_missing(open_w, parked, raw, blocked):
    return table(["Still missing", "Count"], [["Open CRITICAL cards", open_w.get("CRITICAL", 0)], ["Open CRUCIAL cards", open_w.get("CRUCIAL", 0)],
                                              ["Parked (need review or no tries left)", parked], ["Raw cards", raw], ["Blocked cards", blocked]])


def fmt_hygiene(disks, temp_n, mts_run, bundle, trees, strays):
    rows = [[d, f"{g:.1f} GB" if g is not None else ND] for d, g in disks]
    rows += [["Temp top-level entries", temp_n], ["mts_run_* leftovers", mts_run], ["Worktrees (holding unshipped work)", trees],
             ["Old stray processes", strays], ["VM bundle folder", bundle]]
    return table(["Hygiene", "Value"], rows)


def fmt_sessions():
    return ["Sessions running/idle/archived: NOT_IN_DATA (coordinator adds)",
            "Compaction count: NOT_IN_DATA (would measure: count compaction events in the session transcript .jsonl)",
            "Sonnet vs Opus value: NOT_IN_DATA (would measure: cards closed per login 5h-% by model)"]


def result_line(budget, red_min, open_w, failures):
    wk = max((v[2] for v in budget.values()), default=None)
    bits = [f"week budget up to {wk}%" if wk is not None else "budget " + ND, f"CI red {red_min} min" if red_min else "CI green",
            f"{open_w.get('CRITICAL', 0) + open_w.get('CRUCIAL', 0)} CRITICAL/CRUCIAL cards open"]
    if failures:
        bits.append(f"{failures} section(s) NOT_IN_DATA")
    return "**Status: " + "; ".join(bits) + "**"


# ---- collectors (touch the machine) ------------------------------------------------------------------------------------------------

@functools.lru_cache(maxsize=None)
def signal_text():
    return run([sys.executable, str(HERE / "mts_signal.py"), "read"], 20)


@functools.lru_cache(maxsize=None)
def ci_runs():
    import ci_watch
    return ci_watch.fetch()


@functools.lru_cache(maxsize=None)
def cards():
    out = []
    for f in (REPO / "MyTradingSys" / "system" / "tasks").glob("*.json"):
        try:
            out.append(json.loads(f.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            pass
    return out


def utc_day(offset=0):
    return (datetime.now(timezone.utc) + timedelta(days=offset)).strftime("%Y-%m-%d")


@functools.lru_cache(maxsize=None)
def git_days():
    return run(["git", "log", "origin/fast-track", "--no-merges", "--since=8.days", "--format=%cd", "--date=format-local:%Y-%m-%d"], 20).split()


def common_dir():
    p = Path(run(["git", "rev-parse", "--git-common-dir"]).strip() or ".git")
    return str(p if p.is_absolute() else REPO / p)


def sec_budget():
    cs, t, y, d = cards(), utc_day(), utc_day(-1), git_days()
    closed = [str(c.get("closed", ""))[:10] for c in cs if c.get("state") == "done"]
    return fmt_budget(parse_budget(signal_text()), closed.count(t), closed.count(y), d.count(t), d.count(y))


def sec_speed():
    runs = []
    try:
        runs = ci_runs()
    except Exception:
        pass
    rows = []
    for base in (REPO, Path(common_dir()).resolve().parent):
        p = base / "runtime_data" / "gate_timing.jsonl"
        if p.exists():
            for ln in p.read_text(encoding="utf-8", errors="replace").splitlines()[-400:]:
                try:
                    rows.append(json.loads(ln))
                except ValueError:
                    pass
            break
    import host_health as hh
    now = time.time()
    ships = [p for p in hh.snapshot() if "sync.py" in p["cmd"] and " ship" in p["cmd"] and p["name"].lower().startswith("python")]
    stalled = [p for p in ships if p["created"] and now - p["created"] > 1800]
    return fmt_speed(per_day(git_days(), [utc_day(-i) for i in range(6)]), runs, red_minutes(runs), gate_summary(rows),
                     f"Ships running now: {len(ships)}; stalled over 30 min: {len(stalled)}")


def sec_value():
    now = datetime.now(timezone.utc)
    done = sorted((c for c in cards() if c.get("state") == "done" and str(c.get("closed", ""))[:10] == utc_day()), key=lambda c: c.get("closed", ""), reverse=True)
    subj = run(["git", "log", "origin/fast-track", "--no-merges", "--since=midnight", "--format=%s"], 20).splitlines()
    clean = [s for s in subj if re.search(r"(dedupe|clean-?up|declutter|retire[sd]?|prune[sd]?)", s, re.I)]
    stuck = [c["id"] for c in cards() if c.get("state") == "active" and old_hours(c.get("taken", ""), now) > STUCK_H]
    stale = stale_claims(run([sys.executable, str(HERE / "sync.py"), "claims"], 30))
    return fmt_value([c.get("title", c["id"]) for c in done], clean, stuck, stale)


def sec_missing():
    cs = cards()
    m = re.search(r"parked=(\d+)", run([sys.executable, str(HERE / "tasks.py"), "status"], 20))
    return fmt_missing(count_open(cs), m.group(1) if m else nd("tasks.py status has no parked="),
                       sum(1 for c in cs if c.get("state") == "raw"), sum(1 for c in cs if c.get("state") == "blocked"))


def sec_hygiene():
    disks = []
    for d in ("C:\\", "D:\\", "F:\\"):
        try:
            disks.append((d[:2] + " free", shutil.disk_usage(d).free / 1e9))
        except OSError:
            disks.append((d[:2] + " free", None))
    temp = Path(os.environ.get("TEMP") or os.environ.get("TMP") or "")
    names = os.listdir(temp) if temp.is_dir() else []
    vm = Path(os.environ.get("LOCALAPPDATA", "")) / "Claude-Data" / "claude_pzs8sxrjxfjjc" / "vm_bundles"
    if vm.exists() or vm.is_symlink():
        real = os.path.realpath(vm)
        bundle = f"{vm} (real folder, not a junction)" if os.path.normcase(real) == os.path.normcase(str(vm)) else f"junction {vm} -> {real}"
    else:
        bundle = nd("vm_bundles path not present")
    n_trees = len([ln for ln in run(["git", "worktree", "list"]).splitlines() if ln.strip()])
    report = Path(common_dir()).resolve().parent / "Dumps" / "worktree_report.txt"
    try:
        m = re.search(r"worktree report (\S+ \S+).*?: (\d+)", report.read_text(encoding="utf-8"), re.S)
        trees = f"{n_trees} ({m.group(2)} with unshipped work, report {m.group(1)})" if m else nd("worktree_report.txt unparsed")
    except OSError:
        trees = f"{n_trees} (unshipped count {ND}: no Dumps/worktree_report.txt)"
    try:
        import c_drive_guard
        m2 = re.match(r"(\d+) KILL", c_drive_guard.procs_summary())
        strays = f"{m2.group(1)} kill candidate(s)" if m2 else nd("procs_summary unavailable")
    except Exception as e:
        strays = nd(type(e).__name__)
    return fmt_hygiene(disks, len(names), sum(1 for n in names if n.startswith("mts_run_")), bundle, trees, strays)


SECTIONS = [("Resources: budget and what it bought", sec_budget), ("Speed and health", sec_speed), ("Value added", sec_value),
            ("Still missing", sec_missing), ("Hygiene", sec_hygiene)]


def build(sections=None):
    """(failure count, body lines); a failing section prints NOT_IN_DATA and the rest still run."""
    body, fails = [], 0
    for title, fn in (SECTIONS if sections is None else sections):
        try:
            lines = fn()
        except Exception as e:
            fails += 1
            lines = [nd(f"{type(e).__name__}: {str(e)[:100]}")]
        body += [f"**{title}**"] + lines + [""]
    return fails, body + ["**Sessions and measurement**"] + fmt_sessions()


def main():
    t0 = time.time()
    fails, body = build()
    try:
        red = red_minutes(ci_runs())
    except Exception:
        red = 0
    print(result_line(parse_budget(signal_text()), red, count_open(cards()), fails))
    print("\n".join(body))
    print(f"\n(board built in {time.time() - t0:.0f} s)")


if __name__ == "__main__":
    main()
