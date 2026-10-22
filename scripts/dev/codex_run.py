"""Layer lab runner: fires the Codex command line on the next ready CODEX card. No Claude session is involved (T0 script).

  python scripts/dev/codex_run.py tick                 # scheduler entry: refresh the lab work tree, then `next`
  python scripts/dev/codex_run.py next [--dry]         # run the first ready, unclaimed CODEX card
  python scripts/dev/codex_run.py run <card> [--dry] [--force]   # run one card by id (--force: past the lab spend guard)
  python scripts/dev/codex_run.py ask "<title>" --kind audit|build|run --scope <path> [--cmd ..] [--tests ..] [--goal ..] [--mutation-check path/test.py::test_x]
  python scripts/dev/codex_run.py index                # regenerate MyTradingSys/research/layer_lab/INDEX.md
  python scripts/dev/codex_run.py status               # plain words: allowance, queue, deliveries, last runs, NEEDS A LOOK
  python scripts/dev/codex_run.py stop "<why>" | resume
Spec, lanes and report format: MyTradingSys/system/LAYER_LAB.md. Model and effort come from the card (tasks.codex_setting):
luna low/medium by default, astra only for a `crucial` card. One card per tick, one run at a time (lab.lock), and a per-window
spend guard (LAB_WINDOW_PTS, LAB_RUNS_PER_WINDOW, ASTRA_RUNS_PER_WINDOW, LAB_WEEK_PTS): when it is spent the lab idles until the reset.
Environment (all optional): CODEX_HOME (F:/codex_home), MTS_CODEX_LAB_WT (F:/MTS/mts-codex-lab), MTS_CODEX_EXE,
MTS_CODEX_SANDBOX (workspace-write), MTS_CODEX_TIMEOUT_MIN (60).
lab.hold (in CODEX_HOME): written when a ship fails on a gate (no TIMEOUT line); `next` refuses new runs while it exists and `status` lists it under
NEEDS A LOOK. The operator clears it by deleting CODEX_HOME/lab.hold after the stuck commit in the lab work tree is fixed or shipped.
"""
import nowin  # B173: no console flash from git/python children under pythonw
nowin.install()
import argparse
import glob
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import codex_pack  # noqa: E402
import lane_health  # noqa: E402
import sync  # noqa: E402
import tasks  # noqa: E402

REPO = tasks.REPO
LAB = "MyTradingSys/research/layer_lab"
GENERATED = ("MyTradingSys/system/LAYERS.md",)   # tasks.py rewrites it after every card change (make_layers_md): closing a krown-/malkan-/tom-... card always dirties it
BAIL_S = 180             # a BLOCKED/INCOMPLETE run this short with no report is the model bailing, not the card failing
BAIL_FREE = 2             # such bails per card that are not charged as tries (a fresh run usually gets through)
STALL_S = 3 * 3600        # ready cards, lane up, no hold, and no run for this long = the lab is stalled (watchdog)
READING_STALE_S = 2 * 3600  # an allowance reading older than this may undercount (other machines spend the same week)
MAX_ATTEMPTS = 2          # runs of one card that did not end `done`; after that it is STUCK and skipped (no trial burn)
LOCK_STALE_S = 3 * 3600
WINDOW_STOP = 85          # % of the 5-hour window used: no new card until it resets
WEEK_STOP = 85            # % of the week used: the rest stays with the operator's own Codex app sessions
# Spend guard (operator 2026-10-13). 2026-10-12: one astra/high audit (5.1M tokens, 14 minutes) moved the 5-hour window 0 -> 90% and the
# week 14 points; the 85% pre-check above only looks at what is already used, so a card that starts at 16% may still empty the window.
WINDOW_S = 5 * 3600
WEEK_S = 7 * 86400
LAB_WINDOW_PTS = 65       # DECISION (OURS) 2026-10-21 Supervisor B: was 50, 65 is the most that keeps the 10-pt reserve and the tests; reading 3% window / 1% week on Plus; points of one 5-hour window the lab may spend (the rest stays with the operator's own sessions)
LAB_WEEK_PTS = 90         # DECISION (OURS) 2026-10-21: was 60, ~90% of the week; points of the week the lab may spend (operator 2026-10-16: was 35; GPT sat at 24% of the week while dev waited)
LAB_RUNS_PER_WINDOW = 14  # DECISION (OURS) 2026-10-21: was 10 (20-min gap allows 15); cards started per 5-hour window (operator 2026-10-16: was 4; luna/medium runs move 0-3 window pts, the 30-min tick allows 10)
ASTRA_RUNS_PER_WINDOW = 1
WINDOW_RESERVE = 10       # points of the window never planned away: a card starts only if its estimate fits below 100 - this
WEEK_RESERVE = 15
MIN_GAP_S = 20 * 60       # between two run starts (tick = 30 min); a manual run next to a tick cannot stack
COOLDOWN_S = 2 * 3600     # a card that ended INCOMPLETE is not picked again for this long
EST_WINDOW_PTS = {        # points of the 5-hour window one run moved (measured 2026-10-12 on the NUC; luna is an estimate until measured)
    ("gpt-6-astra", "high"): 90, ("gpt-6-astra", "medium"): 45, ("gpt-6-astra", "low"): 20,
    ("gpt-6.1-sol", "medium"): 10, ("gpt-6.1-sol", "low"): 5, ("gpt-6-luna", "medium"): 6, ("gpt-6-luna", "low"): 3}
EST_DEFAULT = 50          # a model/effort not in the table is assumed expensive until it has been measured
EST_WEEK_RATIO = 0.17     # week points per window point (13 / 81 and 1 / 7 on 2026-10-12)
MEASURED_RUNS = 8         # the cost of a setting is the max of its latest runs that carry a measurement
USAGE = "MyTradingSys/system/codex_usage.json"   # shipped with the run: what the Control Room "Claude-GPT cycle" shows
USAGE_RUNS = 10
# Time boxes (2026-10-15): JSON is not doc-only for sync.py ship, so every lane-state or usage commit runs the quick gate (minutes, and a hung
# pytest child never ends). A tick that waited on it never reached `next`: no card ran for 15 h. On expiry the whole process tree is killed; the commit
# stays on the lab branch and the next successful ship pushes it, so nothing is lost.
SWEEP_TIMEOUT_S = 10 * 60
SHIP_TIMEOUT_S = 25 * 60

TEMPLATES = {
    "audit": {
        "steps": ["Read every scope_in file and each source it cites (trade ledger rows, transcript quote file:line).",
                  "Check each rule, parameter and number against its source; where a backtest is involved apply the 12 items of MyTradingSys/backtest/PRE_REG_TEMPLATE.md.",
                  "Report findings as a table: severity HIGH/MED/LOW, file:line, what is wrong, evidence, proposed fix. Change no code and no spec.",
                  "A source you cannot reach (video frames, data on another machine) is a NOT_IN_DATA finding, not a reason for BLOCKED: finish the audit and mark the card done.",
                  "For each HIGH finding capture a follow-up card: python scripts/dev/tasks.py new \"<title>\" --lane SONNET."],
        "scope_out": ["code or spec changes", "holdout reads", "BTC runs of the current encoding (ROADMAP section 2)"],
        "done_when": "The report has the findings table (or 'no findings' plus what was checked) and one verdict line: SOUND / FIX-FIRST / BLOCKED."},
    "run": {
        "steps": ["Run the commands exactly as written, on development data only; never read a holdout (ROADMAP section 2).",
                  "Append one row per run to MyTradingSys/research/layer_lab/TRIALS.md (date, card, command, data range, headline number): every run is a counted trial.",
                  "Report each number with the command and output file behind it; a missing input is NOT_IN_DATA, never 0."],
        "scope_out": ["holdout reads", "changing the code under test", "tuning parameters"],
        "done_when": "The report has every command's headline numbers and TRIALS.md has one new row per run."},
    "build": {
        "steps": ["Write the test named in Tests first and see it fail on the current code.",
                  "Implement the goal inside scope_in only; new behaviour sits behind a flag that is off by default.",
                  "Before finishing run `python scripts/dev/lookahead_lint.py --new`; fix FAIL hits on your files: write forward bars as zip(times, times[1:]), not times[i + 1]; a truly causal pair gets one reviewed row in scripts/dev/lookahead_allowlist.tsv (name it in scope_in).",
                  "Run the test file you changed (PYTHONPATH = the work tree root) until it passes. Do not run scripts/dev/run_all_tests.py: tests that create git repositories are refused in the sandbox; the runner runs the quick gate when it ships."],
        "scope_out": ["the live path", "holdout reads", "parameters without a trader quote (NO-SOURCE)"],
        "done_when": "The named test passes and the report lists the changed files and the red-then-green test output (the runner's ship runs the quick gate)."},
}


def utc():
    return datetime.now(timezone.utc)


def codex_home(env=os.environ):
    return Path(env.get("CODEX_HOME") or "F:/codex_home")


def gate_step(text):
    """The last `Step N: ... FAIL` line of a sync.py ship log ('' if none)."""
    steps = re.findall(r"^(Step \S+: .*?: FAIL)\s*$", text or "", re.M)
    return steps[-1] if steps else ""


def record_ship_failure(home, cid, text):
    """A gate-red SHIP_FAILED leaves the run commit on the lab branch, where it makes every later lab ship fail. git reset is forbidden,
    so write `lab.hold` (card id + gate step): cmd_next refuses new runs and `status` prints it under NEEDS A LOOK. The operator clears
    it by deleting lab.hold once the commit is fixed or shipped. A TIMEOUT ship (the box killed the gate) keeps the old behaviour: the
    next successful ship pushes the commit. Returns True when a hold was written."""
    if "TIMEOUT" in (text or ""):
        return False
    home = Path(home)
    home.mkdir(parents=True, exist_ok=True)
    (home / "lab.hold").write_text(f"{cid}: ship gate failed ({gate_step(text) or 'step unknown, see log.ship.txt'}); delete lab.hold to clear" + chr(10),
                                   encoding="utf-8", newline=chr(10))
    return True


def read_hold(home):
    f = Path(home) / "lab.hold"
    return f.read_text(encoding="utf-8").strip() or "lab.hold present" if f.is_file() else ""


def lab_wt(env=os.environ):
    return Path(env.get("MTS_CODEX_LAB_WT") or "F:/MTS/mts-codex-lab")


def find_exe(env=os.environ, which=shutil.which, globber=glob.glob):
    """The Codex CLI: env, PATH, else the newest binary the desktop app ships (its folder name changes on app updates)."""
    if env.get("MTS_CODEX_EXE"):
        return env["MTS_CODEX_EXE"]
    hit = which("codex")
    if hit:
        return hit
    found = globber(os.path.join(env.get("LOCALAPPDATA", ""), "OpenAI", "Codex", "bin", "*", "codex.exe"))
    if not found:
        raise SystemExit("codex_run: no Codex CLI (set MTS_CODEX_EXE)")
    return max(found, key=lambda p: os.path.getmtime(p) if os.path.exists(p) else 0)


def is_bail(r):
    """The run ended BLOCKED/INCOMPLETE within BAIL_S with no report and no note: the model gave up early."""
    return (r.get("outcome") in ("BLOCKED", "INCOMPLETE") and 0 < (r.get("seconds") or 0) < BAIL_S
            and not r.get("report") and not r.get("note"))


def attempts(home):
    """{card: runs that did not end done} from the run log. The first BAIL_FREE early bails of a card are not tries."""
    out, bails = {}, {}
    p = Path(home) / "lab_runs" / "runs.jsonl"
    if p.is_file():
        for line in p.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("outcome") == "REOPENED" and not r.get("dry"):
                # a session fixed the cause (e.g. a red gate) and stamped the card: earlier failed tries no longer count
                out.pop(r["card"], None)
                bails.pop(r["card"], None)
            elif r.get("outcome") not in ("DONE", "LIMIT") and not r.get("dry"):
                if is_bail(r):
                    bails[r["card"]] = bails.get(r["card"], 0) + 1
                    if bails[r["card"]] <= BAIL_FREE:
                        continue
                out[r["card"]] = out.get(r["card"], 0) + 1
    return out


def reading_age(home, now):
    """Seconds since the newest Codex session file was written (the age of the allowance reading), or None."""
    files = list(Path(home).glob("sessions/**/*.jsonl"))
    return now - max(p.stat().st_mtime for p in files) if files else None


def stall_findings(rows, ready, tried, lane_up, held, now, age=None):
    """The watchdog: what is silently wrong although nothing 'failed'. [] = healthy."""
    L = []
    left = [c for c in ready if tried.get(c["id"], 0) < MAX_ATTEMPTS]
    runs = [r for r in rows if not r.get("dry")]
    if left and lane_up and not held and runs:
        last = max(epoch_of(r.get("at")) for r in runs)
        if last and now - last > STALL_S:
            L.append(f"STALLED: {len(left)} card(s) ready, lane up, no allowance hold, but nothing ran for {(now - last) / 3600:.1f} h: "
                     "read last_tick.txt and last_lane.txt on the lab host")
    tail = runs[-3:]
    if len(tail) == 3 and all(is_bail(r) for r in tail):
        L.append("the model bailed early 3 runs in a row (" + ", ".join(r["card"] for r in tail) + "): the lab environment, not the cards, is the suspect")
    if age is not None and age > READING_STALE_S:
        L.append(f"the allowance reading is {age / 3600:.1f} h old: spend from other machines is not in it, so the week may be higher than shown")
    return L


def budget(home, newest=5):
    """Latest Codex allowance reading ({'primary': 5-hour window, 'secondary': week}) from the newest session files, else None.
    The lab and the operator's own app sessions share CODEX_HOME, so the reading covers both."""
    files = sorted(Path(home).glob("sessions/**/*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)[:newest]
    for p in files:
        for line in reversed(p.read_text(encoding="utf-8", errors="replace").splitlines()):
            m = re.search(r'"rate_limits"\s*:\s*(?=\{)', line)
            if not m:
                continue
            try:
                rl, _ = json.JSONDecoder().raw_decode(line, m.end())
            except ValueError:
                continue
            if isinstance(rl.get("primary"), dict):
                return rl
    return None


def hold(rl, now):
    """Why no card may start on this reading, or ''. A window whose reset time has passed counts as empty; no reading = go."""
    for key, cap, name in (("primary", WINDOW_STOP, "5-hour window"), ("secondary", WEEK_STOP, "weekly allowance")):
        w = (rl or {}).get(key) or {}
        if (w.get("used_percent") or 0) >= cap and (w.get("resets_at") or 0) > now:
            return f"Codex {name} {w['used_percent']:.0f}% used, resets {datetime.fromtimestamp(w['resets_at'], timezone.utc).strftime('%Y-%m-%d %H:%MZ')}"
    return ""


def hold_until(rl, now):
    """Epoch second when the held allowance window resets (the latest one when both are held), else 0."""
    ends = [(rl or {}).get(k, {}).get("resets_at") or 0 for k, cap in (("primary", WINDOW_STOP), ("secondary", WEEK_STOP))
            if ((rl or {}).get(k) or {}).get("used_percent", 0) >= cap]
    return max([e for e in ends if e > now] or [0])


def mark_window_down(why, until_epoch, now_dt):
    """The allowance is spent: mark the GPT lane down until the reset so lane_health reroutes the ready CODEX cards (no card waits on GPT)."""
    lane = lane_health.load(REPO)
    until = datetime.fromtimestamp(until_epoch, timezone.utc)
    lane_health.save(REPO, lane_health.go_down(lane, "window", why, now_dt, until))


def budget_line(rl, now):
    if not rl:
        return "Codex allowance: no reading yet"
    part = []
    for key, name in (("primary", "5-hour window"), ("secondary", "week")):
        w = rl.get(key) or {}
        over = (w.get("resets_at") or 0) <= now
        part.append(f"{name} {0 if over else w.get('used_percent', 0):.0f}% used" + ("" if over else f" (resets {datetime.fromtimestamp(w['resets_at'], timezone.utc).strftime('%m-%d %H:%MZ')})"))
    return f"Codex allowance ({rl.get('plan_type') or 'plan ?'}): " + "; ".join(part)


def limit_hit(outcome, files, log_text):
    """A run that ended on the allowance / credit error is not a try of the card, even with partial files (those are salvaged).
    Only the log tail counts: the prompt and the files Codex read mention limits too (lane_health.classify)."""
    return outcome == "INCOMPLETE" and bool(lane_health.classify(log_text))


def epoch_of(at):
    try:
        return datetime.strptime(str(at), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()
    except ValueError:
        return 0


def setting_of(r):
    """(model, effort) a run really used: what the CLI printed when the runner captured it, else what was asked."""
    return (r.get("model_used") or r.get("model"), r.get("effort_used") or r.get("effort"))


def est_pts(model, effort, rows):
    """(window points, week points) one run of this setting is expected to move: the max of its latest measured runs, else the table."""
    got = [r for r in rows if not r.get("dry") and setting_of(r) == (model, effort) and r.get("window_pts") is not None][-MEASURED_RUNS:]
    if got:
        w = max(r["window_pts"] for r in got)
        k = [r["week_pts"] for r in got if r.get("week_pts") is not None]
        return float(w), float(max(k)) if k else round(w * EST_WEEK_RATIO, 2)
    w = EST_WINDOW_PTS.get((model, effort), EST_DEFAULT)
    return float(w), round(w * EST_WEEK_RATIO, 2)


def lab_spend(rows, since):
    """Points and run counts the lab spent in runs started at or after `since` (epoch). A run without a measurement counts its estimate."""
    out = {"window_pts": 0.0, "week_pts": 0.0, "runs": 0, "astra_runs": 0}
    for r in rows:
        if r.get("dry") or epoch_of(r.get("at")) < since:
            continue
        m, e = setting_of(r)
        w, k = est_pts(m, e, [])
        out["window_pts"] += r["window_pts"] if r.get("window_pts") is not None else w
        out["week_pts"] += r["week_pts"] if r.get("week_pts") is not None else k
        out["runs"] += 1
        out["astra_runs"] += 1 if m == "gpt-6-astra" else 0
    return out


def windows(rl, now):
    """(5-hour used %, its start epoch, its reset epoch, week used %, week start, week reset) from an allowance reading.
    A window whose reset time has passed counts as empty and starts at that reset, but never earlier than one window length ago: a stale
    reading (no Codex session wrote a newer one) must not pin the window to its old reset, or every run since then counts as "this window"
    and the guard blocks the runs that would refresh the reading (JIS-NUC 2026-10-15: 7/4 runs, idle 14 h). No reading: nothing used, window = the last 5 h / 7 d."""
    res = []
    for key, span in (("primary", WINDOW_S), ("secondary", WEEK_S)):
        w = (rl or {}).get(key) or {}
        end = w.get("resets_at") or 0
        if end > now:
            res += [w.get("used_percent") or 0, end - span, end]
        elif end > now - span:
            res += [0, end, end + span]
        else:
            res += [0, now - span, now + span]
    return tuple(res)


def budget_hold(model, effort, rl, rows, now, optimization=False):
    """Why one run of model/effort may not start now ('' = it may), and the epoch when the limiting window resets.
    Plain text; the lane is NOT marked down for this (no card is rerouted: the lab just waits for the window)."""
    est_w, est_k = est_pts(model, effort, rows)
    used_w, w_start, w_end, used_k, k_start, k_end = windows(rl, now)
    spent_w, spent_k = lab_spend(rows, w_start), lab_spend(rows, k_start)
    name = f"{model}/{effort}"
    if not optimization and spent_w["runs"] >= LAB_RUNS_PER_WINDOW:
        return f"{spent_w['runs']} lab runs in this window (cap {LAB_RUNS_PER_WINDOW})", int(w_end)
    if not optimization and model == "gpt-6-astra" and spent_w["astra_runs"] >= ASTRA_RUNS_PER_WINDOW:
        return f"astra already ran {spent_w['astra_runs']}x in this window (cap {ASTRA_RUNS_PER_WINDOW})", int(w_end)
    if used_w + est_w > 100 - WINDOW_RESERVE:
        return f"{name} needs about {est_w:.0f} points of the 5-hour window and {used_w:.0f}% is used (keeps {WINDOW_RESERVE} free)", int(w_end)
    if not optimization and spent_w["window_pts"] + est_w > LAB_WINDOW_PTS:
        return f"lab share of this 5-hour window: {spent_w['window_pts']:.0f} spent + {name} about {est_w:.0f} > {LAB_WINDOW_PTS}", int(w_end)
    if used_k + est_k > 100 - WEEK_RESERVE:
        return f"{name} would take the week past {100 - WEEK_RESERVE}% ({used_k:.0f}% used)", int(k_end)
    if not optimization and spent_k["week_pts"] + est_k > LAB_WEEK_PTS:
        return f"lab share of this week: {spent_k['week_pts']:.0f} spent + {name} about {est_k:.1f} > {LAB_WEEK_PTS}", int(k_end)
    return "", 0


def cooling(rows, cid, now):
    """A card whose last run ended INCOMPLETE (it ran out mid-run) is not picked again until the cool-down has passed."""
    mine = [r for r in rows if r.get("card") == cid and not r.get("dry")]
    return bool(mine) and mine[-1].get("outcome") == "INCOMPLETE" and now - epoch_of(mine[-1].get("at")) < COOLDOWN_S


def gap_hold(rows, now):
    real = [r for r in rows if not r.get("dry")]
    if real:
        ago = now - epoch_of(real[-1].get("at"))
        if 0 <= ago < MIN_GAP_S:
            return f"the last run started {ago / 60:.0f} minutes ago (minimum gap {MIN_GAP_S // 60})"
    return ""


def choose(cards, claimed, tried, rows, rl, now, probe=False):
    """-> (card, '') for the first ready card that is not cooling and whose estimated cost fits the budget; a cheaper card behind a held
    one still runs. (None, why) names the first card held and why."""
    left = [c for c in cards if not cooling(rows, c["id"], now)]
    first = ""
    while True:
        c = pick(left, claimed, tried, probe)
        if not c:
            return None, first
        model, effort = tasks.codex_setting(c)
        why, _ = budget_hold(model, effort, rl, rows, now, optimization=bool(c.get("flow")))
        if not why:
            return c, ""
        first = first or f"{c['id']}: {why}"
        left = [x for x in left if x["id"] != c["id"]]


def log_header(text):
    """Model, reasoning effort and session id the CLI printed in its header: what actually ran, whatever was asked for."""
    out = {}
    for line in text.splitlines()[:40]:
        for key, pat in (("model", r"^model:\s*(\S+)"), ("effort", r"^reasoning effort:\s*(\S+)"), ("session", r"^session id:\s*(\S+)")):
            m = re.match(pat, line.strip())
            if m and key not in out:
                out[key] = m.group(1)
    return out


def setting_mismatch(asked, hdr):
    if not hdr.get("model"):
        return ""
    got = (hdr["model"], hdr.get("effort") or asked[1])
    return "" if got == tuple(asked) else f"asked {asked[0]}/{asked[1]}, CLI used {got[0]}/{got[1]}"


def rollout_usage(home, session):
    """Tokens and allowance points of one run, from its Codex rollout file (<home>/sessions/**/*<session>.jsonl). {} if not found.
    Points are what the shared allowance showed between the run's first and last reading, so an operator app session that ran at the
    same time is included; tokens_total counts cached input too (the CLI's own 'tokens used' line leaves it out)."""
    if not session:
        return {}
    hits = glob.glob(os.path.join(str(home), "sessions", "**", f"*{session}.jsonl"), recursive=True) + \
        glob.glob(os.path.join(str(home), "archived_sessions", f"*{session}.jsonl"))
    if not hits:
        return {}
    total, first, last = None, None, None
    for line in Path(hits[0]).read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            o = json.loads(line)
        except ValueError:
            continue
        pl = o.get("payload") or {}
        if o.get("type") != "event_msg" or pl.get("type") != "token_count":
            continue
        t = (pl.get("info") or {}).get("total_token_usage")
        if t:
            total = t
        rl = pl.get("rate_limits")
        if isinstance(rl, dict) and isinstance(rl.get("primary"), dict):
            first = first or rl
            last = rl
    if not total:
        return {}
    out = {"tokens_total": total.get("total_tokens"), "tokens_cached": total.get("cached_input_tokens"),
           "tokens_uncached": (total.get("input_tokens") or 0) - (total.get("cached_input_tokens") or 0), "tokens_out": total.get("output_tokens")}
    if first and last:
        for key, name in (("primary", "window"), ("secondary", "week")):
            a, b = first.get(key) or {}, last.get(key) or {}
            before, after = a.get("used_percent"), b.get("used_percent")
            if before is None or after is None:
                continue
            # a different reset time with a higher reading is a stale first reading, not a reset (observed 2026-10-12 20:00Z)
            same = a.get("resets_at") == b.get("resets_at") or after >= before
            out[f"{name}_before"], out[f"{name}_after"] = before, after
            out[f"{name}_pts"] = round(max(0.0, after - before), 1) if same else after
    return out


def usage_doc(rows, rl, now, host):
    """The compact view the Control Room embeds (relay_board.board -> gpt_usage): allowance, the lab's spend and caps, latest runs."""
    used_w, w_start, w_end, used_k, k_start, k_end = windows(rl, now)
    sw, sk = lab_spend(rows, w_start), lab_spend(rows, k_start)
    keep = ("at", "card", "kind", "outcome", "seconds", "tokens_total", "tokens_uncached", "tokens_out", "window_pts", "week_pts")
    runs = []
    for r in [x for x in rows if not x.get("dry")][-USAGE_RUNS:][::-1]:
        m, e = setting_of(r)
        d = {k: r.get(k) for k in keep}
        d.update(model=m, effort=e, note=str(r.get("note") or "")[:160])
        if (r.get("model"), r.get("effort")) != (m, e):
            d["asked"] = f"{r.get('model')}/{r.get('effort')}"
        runs.append(d)
    return {"at": datetime.fromtimestamp(now, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "host": host,
            "allowance": {"plan": (rl or {}).get("plan_type"), "window_used": used_w, "window_resets": int(w_end), "week_used": used_k, "week_resets": int(k_end)},
            "lab": {"window_pts": round(sw["window_pts"], 1), "window_runs": sw["runs"], "astra_runs": sw["astra_runs"], "week_pts": round(sk["week_pts"], 1)},
            "caps": {"window_pts": LAB_WINDOW_PTS, "week_pts": LAB_WEEK_PTS, "runs_per_window": LAB_RUNS_PER_WINDOW, "astra_runs_per_window": ASTRA_RUNS_PER_WINDOW,
                     "min_gap_min": MIN_GAP_S // 60, "window_reserve": WINDOW_RESERVE},
            "runs": runs}


def write_usage(wt, rows, rl, now):
    p = Path(wt) / USAGE
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(usage_doc(rows, rl, now, socket.gethostname()), indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def salvage(wt, home, cid, when, files=None):
    """Move unfinished files out of the lab work tree into <home>/lab_runs/salvage/<stamp>_<card>/ so the next tick is not blocked.
    Moves, never deletes. Returns (destination, count)."""
    files = changed_files(wt) if files is None else files
    if not files:
        return None, 0
    dest = Path(home) / "lab_runs" / "salvage" / f"{when.strftime('%Y%m%dT%H%M%SZ')}_{cid}"
    for f in files:
        src = Path(wt) / f
        if src.is_file():
            (dest / f).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest / f)
        if git(wt, "cat-file", "-e", f"HEAD:{f}", check=False).returncode == 0:
            git(wt, "checkout", "--quiet", "HEAD", "--", f)   # from HEAD: also clears a staged or unmerged entry (plain checkout refuses those)
        else:
            git(wt, "rm", "--quiet", "--cached", "--ignore-unmatch", "--", f)   # staged new file: unstage, then move it out
            if src.is_file():
                src.unlink()
    return dest, len(files)



def pick(cards, claimed, tried, probe=False):
    """First ready CODEX card nobody holds and that has tries left. `cards` is already ranked and passes the Definition of Ready.
    A card lane_health moved to DSA (`reroute`) is not ours while GPT is down. A probe run (lane down) takes a crucial card first."""
    ok = [c for c in cards if c["lane"] == "CODEX" and not c.get("reroute") and sync.slugify(c["id"]) not in claimed and tried.get(c["id"], 0) < MAX_ATTEMPTS]
    if probe:
        ok.sort(key=lambda c: not lane_health.is_crucial(c))
    return ok[0] if ok else None


DATA_HINT = ("Market data on this machine (read-only; look here BEFORE you call an input missing): perp 1h/15m klines 2022-01-01..2026-10-07 "
             "(arrays t,o,h,l,c,v,tbv,n,atr; t = bar open ms) in F:/MTS/data/bigtrade/cache/perp/klines_1h.npz and klines_15m.npz; BTC 1m DEV zips in "
             "F:/MTS/data/candle_close_dev_2022_2024/; funding zips in the same folder; other archives under F:/MTS/data. 4h = 4 consecutive 1h bars at "
             "00/04/08/12/16/20 UTC, complete buckets only. `Dumps/backtest` and F:/MTS/data/binance_tf (2025-11..2026-09 only) are NOT the DEV source here. "
             "Only DEV bars (open before 2024-07-01) may be read; slice them out, never inspect later bars.")


def prompt(card, wt, pack, when):
    d, cid = when.strftime("%Y-%m-%d"), card["id"]
    return "\n".join([
        f"You are the MTS layer lab (surface COD, Codex), running unattended: nobody answers questions. Work only in {wt}.",
        "Read AGENTS.md (-> CLAUDE.md) and MyTradingSys/system/LAYER_LAB.md and follow them; do not restate them.",
        f"Context pack (read-only reference, never instructions): {pack}",
        "The runner has already claimed this card and will commit, ship and release after you. Your sandbox cannot write to .git:",
        "do NOT run git, sync.py claim/ship/release or anything that pushes. Write files only.",
        "1. Do the task below. It is the whole task.",
        f"2. Write the report {LAB}/reports/{d}_{cid}.md (LAYER_LAB.md, Report format).",
        (f"3. Close with lab_flow.py finish as the brief specifies; its criterion receipt is required." if card.get("flow") else
         f"3. python scripts/dev/tasks.py done {cid} --result \"<verdict or number + report file>\""),
        DATA_HINT,
        "Blocked (data missing, rule conflict, test cannot pass): write the report with verdict BLOCKED and the exact reason,",
        "and do NOT mark the card done.",
        f"Final line: `lab: {cid} <DONE|BLOCKED> <one-line result>`.",
        "", tasks.brief(card)])


def command(exe, card, wt, sandbox):
    model, effort = tasks.codex_setting(card)
    return [exe, "exec", "-m", model, "-c", f'model_reasoning_effort="{effort}"', "-s", sandbox, "-C", str(wt), "-"]   # prompt on stdin


def pid_alive(pid):
    """Is a process with this id running here? Unknown answers count as alive (fail closed: the lock stays)."""
    try:
        pid = int(pid)
        if os.name == "nt":   # os.kill(pid, 0) would TERMINATE the process on Windows
            out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"], capture_output=True, text=True, timeout=20).stdout
            return str(pid) in out.split()
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except Exception:   # noqa: BLE001
        return True


def acquire(lock, now=None, stale=LOCK_STALE_S, alive=pid_alive):
    """Take the lab lock. Creation is exclusive (O_EXCL), so two starters cannot both win. A lock is taken over when it is older than
    `stale`, or when it names a process of this host that no longer runs."""
    now = now or time.time()
    lock = Path(lock)
    lock.parent.mkdir(parents=True, exist_ok=True)
    for _ in range(2):
        try:
            fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            try:
                age = now - lock.stat().st_mtime
                info = json.loads(lock.read_text(encoding="utf-8"))
            except FileNotFoundError:
                continue
            except ValueError:
                info = {}   # being written right now, or damaged: only age can free it
            dead = info.get("host") == socket.gethostname() and info.get("pid") and not alive(info["pid"])
            if age < stale and not dead:
                return False
            lock.unlink(missing_ok=True)
            continue
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps({"pid": os.getpid(), "host": socket.gethostname(), "epoch": int(now)}))
        return True
    return False


def git(wt, *args, check=True):
    return subprocess.run(["git", "-C", str(wt), *args], capture_output=True, text=True, check=check)


def changed_files(wt):
    out = git(wt, "status", "--porcelain", "--untracked-files=all").stdout
    return [line[3:].strip().strip('"').split(" -> ")[-1] for line in out.splitlines() if line.strip()]


def out_of_scope(kind, files):
    """Files an audit or run card may not have written: those two kinds only report, log trials and capture follow-up cards.
    The generated LAYERS.md is allowed: without it every audit of a layer-family card ended OUT_OF_SCOPE (JIS-NUC 2026-10-15 16:00Z)."""
    if kind == "build":
        return []
    return [f for f in files if not (f.startswith(LAB + "/") or f.startswith(tasks.DIR + "/") or f in GENERATED)]


def judge(card_now, reports, kind, files):
    """Outcome of a run from what is in the work tree afterwards. Fail closed: only DONE and BLOCKED are shipped."""
    if out_of_scope(kind, files):
        return "OUT_OF_SCOPE"
    if card_now.get("flow") and card_now.get("state") == "done":
        import lab_flow
        if not lab_flow.accepted(card_now, REPO):
            return "BLOCKED" if reports else "INCOMPLETE"
    if card_now.get("state") == "done" and reports:
        return "DONE"
    return "BLOCKED" if reports else "INCOMPLETE"


def commit_message(card, outcome, result, when):
    model, effort = tasks.codex_setting(card)
    return "\n".join([f"lab {card['id']}: {outcome} ({card['kind']})", "",
                      f"Result: {result}", f"Codex: {model} / {effort}, sandbox run, committed by codex_run.py", "",
                      f"MTS-Session: MTS-{when.strftime('%Y-%m-%d-%H%M')}Z-COD-LAB-{card['id']}"])


def sh(wt, *args):
    return subprocess.run([sys.executable, *args], cwd=str(wt), capture_output=True, text=True)


# a lab run is always its own change: the 10-minute second-ship guard is for sessions that should batch, and it refused
# the lab-formula-spec-text run on 2026-10-22 (ship 528 s after a session shipped from the lab tree)
SHIP_ARGS = ("ship", "--again")


def boxed(cmd, cwd, timeout_s):
    """subprocess.run with a hard time box. On expiry the whole process tree is killed (a gate's pytest children hold the pipes, so killing
    only the parent would leave communicate() waiting) and the result has returncode 124 and a TIMEOUT line on stderr."""
    nt = os.name == "nt"
    p = subprocess.Popen(cmd, cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace",
                         start_new_session=not nt)
    try:
        out, err = p.communicate(timeout=timeout_s)
        return subprocess.CompletedProcess(cmd, p.returncode, out, err)
    except subprocess.TimeoutExpired:
        if nt:
            subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True)   # only the PID started here
        else:
            os.killpg(p.pid, 9)
        try:
            out, err = p.communicate(timeout=30)
        except subprocess.TimeoutExpired:
            out, err = "", ""
        return subprocess.CompletedProcess(cmd, 124, out or "", (err or "") + f"\nTIMEOUT after {timeout_s}s: process tree killed\n")


def run_sweep(wt, runs, *flags):
    """lane_health sweep for the tick, time-boxed. Its outcome goes to last_lane.txt; a failing or hung sweep must not stop the lab."""
    sw = boxed([sys.executable, str(wt / "scripts/dev/lane_health.py"), "sweep", *flags], wt, SWEEP_TIMEOUT_S)
    (runs / "last_lane.txt").write_text(sw.stdout + sw.stderr, encoding="utf-8", newline="\n")
    return sw


def refresh(wt):
    """Bring the lab work tree to origin/fast-track on its own branch. Refuses a dirty tree: unfinished work is never touched."""
    abort_pending_merge(wt)   # Supervisor pilot 2026-10-22: `git switch` refuses "while merging", so the tick died before merge_trunk ran
    if git(wt, "status", "--porcelain").stdout.strip():
        dest, n = salvage(wt, codex_home(), "tick", utc())   # an unfinished run (limit, crash) must not block the lab for good
        print(f"salvaged {n} unfinished file(s) to {dest}")
    git(wt, "fetch", "--quiet", "origin", sync.TRUNK)
    branch = f"{socket.gethostname().lower()}/codex-lab"
    if git(wt, "rev-parse", "--verify", "--quiet", branch, check=False).returncode:
        git(wt, "switch", "--quiet", "-c", branch, f"origin/{sync.TRUNK}")
    else:
        git(wt, "switch", "--quiet", branch)
        merge_trunk(wt, f"origin/{sync.TRUNK}")


def abort_pending_merge(wt):
    if git(wt, "rev-parse", "-q", "--verify", "MERGE_HEAD", check=False).returncode == 0:   # not .git/MERGE_HEAD: the lab tree is a worktree (.git is a file)
        git(wt, "merge", "--abort", check=False)


def merge_trunk(wt, ref):
    """Merge `ref` into the lab branch. A clash only on the generated INDEX.md takes the trunk's copy (the next delivery
    regenerates it); any other clash aborts the merge so the tree stays clean and says which files need a session.
    JIS-NUC 2026-10-14: a merge stopped on INDEX.md left MERGE_HEAD behind and every later tick died on it."""
    abort_pending_merge(wt)
    m = git(wt, "merge", "--quiet", "--no-edit", ref, check=False)
    if m.returncode == 0:
        return
    clash = git(wt, "diff", "--name-only", "--diff-filter=U", check=False).stdout.split()
    if clash and set(clash) <= {f"{LAB}/INDEX.md", lane_health.STATE}:
        # lane_state.json keeps the lab's copy: the lab wrote it after its own run, a Supervisor heartbeat on trunk is older news.
        # JIS-NUC 2026-10-21: this clash made the lab ship fail and the lab sat idle 34 h.
        for f, side in ((f"{LAB}/INDEX.md", "--theirs"), (lane_health.STATE, "--ours")):
            if f in clash:
                git(wt, "checkout", side, "--", f)
        git(wt, "add", "--", *clash)
        git(wt, "commit", "--quiet", "--no-edit")
        return
    git(wt, "merge", "--abort", check=False)
    raise SystemExit(f"codex_run: merging {ref} into the lab tree clashes on {', '.join(clash) or m.stderr.strip()[-200:]}; "
                     "merge aborted, tree clean; a session merges by hand")


def execute(cmd, text, log, timeout_s, env):
    """Run Codex with the prompt on stdin, all output into `log`. Returns (exit code or 'TIMEOUT', seconds)."""
    t0 = time.time()
    with open(log, "w", encoding="utf-8", newline="\n") as f:
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=f, stderr=subprocess.STDOUT, text=True, encoding="utf-8", env=env)
        try:
            p.communicate(text, timeout=timeout_s)
            code = p.returncode
        except subprocess.TimeoutExpired:
            subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True)   # only the PID started here
            code = "TIMEOUT"
    return code, int(time.time() - t0)


def run_card(card, dry=False, env=os.environ, probing=False):
    """Claim, let Codex write files in its sandbox, then commit + ship + release here. Codex never touches git."""
    home, wt, when, cid = codex_home(env), lab_wt(env), utc(), card["id"]
    sandbox = env.get("MTS_CODEX_SANDBOX") or "workspace-write"
    packs = home / "packs"
    packs.mkdir(parents=True, exist_ok=True)
    pack = packs / f"{cid}.md"
    pack.write_text(codex_pack.build(cid, 24), encoding="utf-8", newline="\n")
    cmd, text = command(find_exe(env), card, wt, sandbox), prompt(card, wt, pack, when)
    if dry:
        print("DRY " + " ".join(cmd) + "\n" + text)
        return 0
    runs = home / "lab_runs"
    runs.mkdir(parents=True, exist_ok=True)
    if not acquire(runs / "lab.lock"):
        print("IDLE a lab run holds the lock")
        return 0
    log = runs / f"{when.strftime('%Y%m%dT%H%MZ')}_{cid}.log"
    model, effort = tasks.codex_setting(card)
    try:
        c = sh(wt, "scripts/dev/sync.py", "claim", cid)
        if c.returncode:
            print(f"IDLE claim refused for {cid}: {(c.stdout + c.stderr).strip()[-200:]}")
            return 0
        code, secs = execute(cmd, text, log, int(env.get("MTS_CODEX_TIMEOUT_MIN") or 60) * 60, dict(env, CODEX_HOME=str(home)))
        files = changed_files(wt)
        now = json.loads((wt / tasks.DIR / f"{cid}.json").read_text(encoding="utf-8"))
        reports = sorted(f for f in files if f.startswith(f"{LAB}/reports/") and f.endswith(f"_{cid}.md"))
        outcome, note = judge(now, reports, card["kind"], files), ""
        logtext = log.read_text(encoding="utf-8", errors="replace")
        err = lane_health.classify(logtext) if outcome == "INCOMPLETE" else ""   # also when files were written: the 2026-10-12 astra run did 777 s of work, then hit the limit
        if limit_hit(outcome, files, logtext):
            outcome, note = "LIMIT", f"Codex {'credits' if err == 'credits' else 'allowance'} ran out; the card stays ready, is not charged a try, and the GPT lane is marked down"
            dest, n = salvage(wt, home, cid, when, files)   # partial files leave the lab tree so the next tick is not blocked
            if n:
                note += f" | {n} partial file(s) salvaged to {dest}"
            files = []
        hdr = log_header(logtext)
        use = rollout_usage(home, hdr.get("session"))
        bad = setting_mismatch((model, effort), hdr)
        if bad:
            note = (note + " | " if note else "") + bad
            if card.get("flow"):
                import lab_flow
                now = lab_flow.reject_run(wt, cid, bad)
                outcome = "BLOCKED" if reports else "INCOMPLETE"
        m = re.search(r"tokens used\s*\n\s*([\d,]+)", logtext)

        def make_row():
            return {"at": when.strftime("%Y-%m-%dT%H:%M:%SZ"), "card": cid, "kind": card["kind"], "model": model, "effort": effort,
                    "model_used": hdr.get("model"), "effort_used": hdr.get("effort"), "session": hdr.get("session"),
                    "exit": code, "seconds": secs, "tokens": int(m.group(1).replace(",", "")) if m else None, **use, "outcome": outcome,
                    "report": reports[-1] if reports else "", "note": note, "log": str(log)}
        write_usage(wt, run_rows(home) + [make_row()], budget(home), time.time())
        lane = lane_health.record_run({**lane_health.load(wt), "last_probe": lane_health.iso(when)} if probing else lane_health.load(wt), outcome, err, when,
                                      lane_health.error_line(logtext) if err else "")
        lane_health.save(wt, lane)   # DONE/BLOCKED: rides in the commit below; otherwise shipped on its own
        if outcome in ("DONE", "BLOCKED"):
            sh(wt, "scripts/dev/codex_run.py", "index")
            git(wt, "add", "-A")
            result = now.get("result") if outcome == "DONE" else f"BLOCKED, card stays ready: see {reports[-1]}"
            git(wt, "commit", "-q", "-m", commit_message(card, outcome, result, when))
            try:   # trunk moved during the run: take its changes here, where the lane_state/INDEX clashes resolve themselves
                git(wt, "fetch", "--quiet", "origin", sync.TRUNK)
                merge_trunk(wt, f"origin/{sync.TRUNK}")
            except SystemExit:
                pass   # a real clash: sync.py ship below reports it as SHIP_FAILED
            s = boxed([sys.executable, "scripts/dev/sync.py", *SHIP_ARGS], wt, SHIP_TIMEOUT_S)
            if s.returncode:
                outcome, note = "SHIP_FAILED", (s.stdout + s.stderr).strip()[-300:]
                Path(str(log) + ".ship.txt").write_text(s.stdout + s.stderr, encoding="utf-8", newline="\n")   # which gate step failed
        elif not files:
            lane_health.commit_ship(wt, [lane_health.STATE, USAGE], f"lane health: GPT {lane['status']}" + (f" ({lane['reason']})" if lane["reason"] else "") +
                                    f"\n\nResult: {lane_health.why_down(lane) if lane['status'] == 'down' else 'GPT lane up'}\n")
        else:
            note = f"{len(files)} uncommitted file(s) left in {wt}: " + ", ".join((out_of_scope(card['kind'], files) or files)[:5])
        r = sh(wt, "scripts/dev/sync.py", "release", sync.slugify(cid))
        if r.returncode:
            note += " | release failed: " + (r.stdout + r.stderr).strip()[-200:]
        row = make_row()
        with open(runs / "runs.jsonl", "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(row) + "\n")
    finally:
        (runs / "lab.lock").unlink(missing_ok=True)
    print(f"RAN {cid} {outcome} model={row['model_used'] or model} effort={row['effort_used'] or effort} {secs}s tokens={row.get('tokens_total') or '?'} "
          f"window+{row.get('window_pts', '?')} week+{row.get('week_pts', '?')} report={row['report'] or '-'}" + (f" note={note}" if note else ""))
    return 0 if outcome == "DONE" else 1


def cmd_next(a):
    home = codex_home()
    stop = home / "lab.stop"
    if stop.is_file():
        print("IDLE stopped: " + stop.read_text(encoding="utf-8").strip())
        return 0
    held = read_hold(home)
    if held:
        print("HOLD " + held)
        return 1
    cards, _ = tasks.ready_cards(REPO, "CODEX")
    claimed = {slug for slug, _ in sync.read_claims(REPO, f"origin/{sync.TRUNK}")}
    lane = lane_health.load(REPO)
    gate = "go" if a.dry else lane_health.allow(lane, utc())
    if not gate:
        print(f"IDLE {lane_health.why_down(lane)}; ready CODEX cards are moved to DSA/Claude or paused (lane_health.py status)")
        return 0
    tried = attempts(home)
    card = pick(cards, claimed, tried, gate == "probe")
    if not card:
        print(f"IDLE no CODEX card to run ({len(cards)} ready; claimed or out of tries are skipped)")
        return 0
    skip = a.dry or lane_health.override_active(lane, utc())   # operator override (lane_health.py up): the stored reading may be stale
    rl = None if a.dry else budget(home)
    why = "" if skip else hold(rl, time.time())
    if why:
        end = hold_until(rl, time.time())
        if end:
            mark_window_down(why, end, utc())
        print(f"IDLE {why}; lane marked down until the reset, cards move to DSA/Claude at the next sweep ({card['id']})")
        return 0
    if not a.dry:   # the spend guard also applies under the operator override: it looks at the cost of this card, not at the stale reading
        rows, now = run_rows(home), time.time()
        gap = gap_hold(rows, now)
        if gap:
            print(f"IDLE {gap}; one card per tick")
            return 0
        card, held = choose(cards, claimed, tried, rows, rl, now, gate == "probe")
        if not card:
            print(f"IDLE lab budget: {held}; the lab waits for the window (no card is rerouted)")
            return 0
    return run_card(card, a.dry, probing=gate == "probe")


def cmd_run(a):
    card = tasks.get(REPO, a.card)
    miss = tasks.problems(card, tasks.load_all(REPO), tasks.registry(REPO), repo=REPO)
    if card.get("lane") != "CODEX" or card["state"] != "ready" or miss:
        raise SystemExit(f"codex_run: {a.card} must be a ready CODEX card: " + ("; ".join(miss) or f"lane {card.get('lane')}, state {card['state']}"))
    if not (a.dry or a.force):
        why, _ = budget_hold(*tasks.codex_setting(card), budget(codex_home()), run_rows(codex_home()), time.time(), optimization=bool(card.get("flow")))
        if why:
            raise SystemExit(f"codex_run: lab budget: {why}. Wait for the window, or pass --force (operator decision).")
    return run_card(card, a.dry)


def cmd_tick(a):
    """Scheduler entry. A scheduled run has no console, so the outcome line goes to <CODEX_HOME>/lab_runs/last_tick.txt."""
    wt, runs = lab_wt(), codex_home() / "lab_runs"
    runs.mkdir(parents=True, exist_ok=True)
    try:
        refresh(wt)
        run_sweep(wt, runs, "--apply", "--ship", "--beat")   # failing or hung: the tick goes on to `next`
        r = subprocess.run([sys.executable, str(wt / "scripts/dev/codex_run.py"), "next"], cwd=str(wt), capture_output=True, text=True)
        code, line = r.returncode, (r.stdout.strip().splitlines() or [r.stderr.strip()[-300:] or "no output"])[-1]
        if "lane marked down" in line:   # next just found the window spent: reroute now, not at the next tick
            run_sweep(wt, runs, "--apply", "--ship")
    except SystemExit as e:
        code, line = 1, str(e)
    except subprocess.CalledProcessError as e:
        code, line = 1, f"ERROR git: {(e.stderr or '').strip()[-300:]}"
    (runs / "last_tick.txt").write_text(f"{utc().strftime('%Y-%m-%dT%H:%MZ')} {line}\n", encoding="utf-8", newline="\n")
    print(line)
    return code


def make_card(title, kind, scope, cid=None, goal="", cmds=(), tests="", size="S", prio=2, model="", effort="", mutation_check=""):
    t = TEMPLATES[kind]
    card = tasks.blank(cid or sync.slugify(title), title, prio=prio, lane="CODEX")
    card.update(kind=kind, size=size, goal=goal or title, scope_in=list(scope), scope_out=list(t["scope_out"]), steps=list(t["steps"]),
                commands=list(cmds), tests=tests, done_when=t["done_when"], refined_by="codex_run.py ask")
    if model:
        card["model"] = model
    if effort:
        card["effort"] = effort
    if mutation_check:
        card["mutation_check"] = mutation_check
    return card


def cmd_ask(a):
    card = make_card(a.title, a.kind, a.scope, a.id, a.goal, a.cmd or [], a.tests or "", a.size, a.prio, a.model or "", a.effort or "",
                     getattr(a, "mutation_check", None) or "")
    if tasks.path_of(REPO, card["id"]).exists():
        raise SystemExit(f"codex_run: card {card['id']} exists")
    miss = tasks.problems(card, tasks.load_all(REPO), tasks.registry(REPO), repo=REPO)
    if miss:
        hint = ""
        if card["kind"] == "build" and not card.get("mutation_check"):
            hint = "; build cards need --mutation-check path/to/test.py::test_name (a test that rejects dummy or shuffled output)"
        raise SystemExit("codex_run: not ready, nothing written: " + "; ".join(miss) + hint)
    card["state"] = "ready"
    print(f"wrote {tasks.save(REPO, card)} (ready, {' / '.join(tasks.codex_setting(card))}); commit and `sync.py ship` to queue it")
    return 0


def index_text(cards, report_names):
    """INDEX.md body: deliveries newest first, then what is queued. Deterministic (no generation time)."""
    lab = [c for c in cards if c.get("lane") == "CODEX"]
    L = ["# Layer lab deliveries", "", "Generated by `python scripts/dev/codex_run.py index`; do not edit. Spec: MyTradingSys/system/LAYER_LAB.md.", "",
         "## Delivered", "", "| closed (UTC) | card | kind | result | report |", "|---|---|---|---|---|"]
    for c in sorted((c for c in lab if c["state"] == "done"), key=lambda c: c.get("closed", ""), reverse=True):
        rep = sorted(n for n in report_names if n.endswith(f"_{c['id']}.md"))
        cell = f"[{rep[-1]}](reports/{rep[-1]})" if rep else "-"
        L.append(f"| {c.get('closed', '')[:16]} | {c['id']} | {c.get('kind', '')} | {str(c.get('result', '')).replace('|', '/')} | {cell} |")
    L += ["", "## Queued", "", "| state | card | kind | title |", "|---|---|---|---|"]
    for c in sorted((c for c in lab if c["state"] in tasks.SHOW), key=lambda c: (tasks.SHOW.index(c["state"]), tasks.rank(c))):
        L.append(f"| {c['state']} | {c['id']} | {c.get('kind', '')} | {c['title'].replace('|', '/')} |")
    return "\n".join(L) + "\n"


def cmd_index(a):
    d = REPO / LAB / "reports"
    names = sorted(p.name for p in d.glob("*.md")) if d.is_dir() else []
    out = REPO / LAB / "INDEX.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(index_text(tasks.load_all(REPO), names), encoding="utf-8", newline="\n")
    print(f"wrote {out}")
    return 0


def run_rows(home):
    p = Path(home) / "lab_runs" / "runs.jsonl"
    out = []
    for line in (p.read_text(encoding="utf-8").splitlines() if p.is_file() else []):
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out


def run_line(r):
    n = r.get("tokens_total") or r.get("tokens")
    tok = (f"{n / 1e6:.1f}M tokens" if n and n >= 1e6 else f"{n // 1000}k tokens") if n else "tokens ?"
    pts = f", window +{r['window_pts']:.0f} pts" if r.get("window_pts") is not None else ""
    m, e = setting_of(r)
    return f"{str(r.get('at', ''))[:16].replace('T', ' ')}Z {r.get('card')} {r.get('outcome')} ({m} / {e}, {tok}{pts}, {r.get('seconds', '?')}s)"


def reopened(ready, rows):
    """Ready cards a session reset (field `reopened`, UTC ISO) after their last run: that BLOCKED/failed run is dealt with."""
    at = {}
    for r in rows:
        if not r.get("dry"):
            at[r.get("card")] = r.get("at") or ""
    return {c["id"] for c in ready if c.get("reopened") and c["reopened"] > at.get(c["id"], "")}


def guard_hold(last_tick):
    """The spend guard is a hold too: the scheduler's own last line says so, and that is not a stall."""
    return "IDLE lab budget" if "IDLE lab budget" in (last_tick or "") else ""


def needs_look(ready, tried, rows, unshipped=0, stopped="", held="", closed=(), watch=(), lab_hold=""):
    """What the lab cannot fix by itself, in plain words. [] = nothing to do. Read by the operator and by STATUS.md."""
    L = []
    if stopped:
        L.append(f"the lab is switched off: {stopped} (`codex_run.py resume` turns it on)")
    if lab_hold:
        L.append(f"new runs are refused (lab.hold): {lab_hold}")
    if unshipped:
        L.append(f"the lab work tree holds {unshipped} unshipped file(s) or commit(s); it stays idle until a session checks and ships them")
    L += [f"{c['id']} failed {tried[c['id']]} times and is skipped: read its report and run log, then fix the card" for c in ready if tried.get(c["id"], 0) >= MAX_ATTEMPTS]
    last = [r for r in rows if not r.get("dry")][-1:]
    if last and last[0].get("outcome") not in ("DONE", "LIMIT") and last[0].get("card") not in closed:   # closed since = someone dealt with it
        L.append(f"the last run ended {last[0]['outcome']} ({last[0]['card']}): {last[0].get('note') or 'read ' + (last[0].get('report') or last[0].get('log', 'its log'))}")
    L += list(watch)
    left = [c for c in ready if tried.get(c["id"], 0) < MAX_ATTEMPTS]
    if not left:
        L.append("the queue is empty, so the Codex allowance goes unused: move scoped cards to lane CODEX (LAYER_LAB.md, Allowance)")
    elif len(left) < 3 and not held:
        L.append(f"only {len(left)} card(s) left in the queue: add scoped cards (LAYER_LAB.md, Allowance)")
    return L


def guard_line(rows, rl, now):
    _, w_start, w_end, _, k_start, _ = windows(rl, now)
    sw, sk = lab_spend(rows, w_start), lab_spend(rows, k_start)
    return (f"Lab spend guard: window {sw['window_pts']:.0f}/{LAB_WINDOW_PTS} pts, {sw['runs']}/{LAB_RUNS_PER_WINDOW} runs "
            f"(astra {sw['astra_runs']}/{ASTRA_RUNS_PER_WINDOW}); week {sk['week_pts']:.0f}/{LAB_WEEK_PTS} pts; "
            f"resets {datetime.fromtimestamp(w_end, timezone.utc).strftime('%H:%MZ')}")


def status_text(ready, done, tried, rows, rl, now, last_tick="", unshipped=0, stopped="", host_has_lab=True, age=None, lane_up=True, brief=False, lab_hold=""):
    """brief=True (STATUS.md) leaves out the Delivered block: those results are in layer_lab/INDEX.md."""
    L = [f"Layer lab (Codex) at {datetime.fromtimestamp(now, timezone.utc).strftime('%Y-%m-%d %H:%MZ')}: {'OFF' if stopped else 'on'}"]
    if not host_has_lab:
        L.append("  This machine does not run the lab (it runs on JIS-NUC): the queue below is from the repo; allowance, runs and what needs a look are only known there." if brief else
                 "  This machine does not run the lab (it runs on JIS-NUC): queue and deliveries below are from the repo; allowance, runs and what needs a look are only known there.")
    else:
        L += ["  " + budget_line(rl, now), "  " + guard_line(rows, rl, now), "  Last check by the scheduler: " + (last_tick or "none yet")]
    L.append(f"  Queue: {len(ready)} ready")
    L += [f"    {c['id']} [{c['kind']}, {' / '.join(tasks.codex_setting(c))}]" + (" SKIPPED after failed tries" if tried.get(c["id"], 0) >= MAX_ATTEMPTS else "") for c in ready]
    if not brief:
        L.append("  Delivered (latest 5; all in MyTradingSys/research/layer_lab/INDEX.md):")
        L += [f"    {c.get('closed', '')[:10]} {c['id']}: {c.get('result', '')}" for c in sorted(done, key=lambda c: c.get("closed", ""), reverse=True)[:5]] or ["    nothing yet"]
    if host_has_lab:
        L.append("  Last runs:")
        L += ["    " + run_line(r) for r in rows[-5:]] or ["    none"]
        look = needs_look(ready, tried, rows, unshipped, stopped, hold(rl, now), {c['id'] for c in done} | reopened(ready, rows),
                          stall_findings(rows, ready, tried, lane_up, hold(rl, now) or guard_hold(last_tick), now, age), lab_hold=lab_hold)
        L.append("  NEEDS A LOOK: " + ("nothing" if not look else ""))
        L += [f"    - {x}" for x in look]
    return "\n".join(L)


def cmd_status(a):
    home, wt = codex_home(), lab_wt()
    cards, _ = tasks.ready_cards(REPO, "CODEX")
    done = [c for c in tasks.load_all(REPO) if c.get("lane") == "CODEX" and c["state"] == "done"]
    here = (wt / ".git").exists()
    unshipped = 0
    if here:
        unshipped = len(git(wt, "status", "--porcelain", check=False).stdout.splitlines())
        ahead = git(wt, "rev-list", "--count", f"origin/{sync.TRUNK}..HEAD", check=False).stdout.strip()
        unshipped += int(ahead) if ahead.isdigit() else 0
    tick, stop = home / "lab_runs" / "last_tick.txt", home / "lab.stop"
    print(status_text(cards, done, attempts(home), run_rows(home), budget(home), time.time(),
                      tick.read_text(encoding="utf-8").strip() if tick.is_file() else "", unshipped,
                      stop.read_text(encoding="utf-8").strip() if stop.is_file() else "", here,
                      reading_age(home, time.time()), lane_health.allow(lane_health.load(REPO), utc()) != "", brief=a.brief, lab_hold=read_hold(home)))
    return 0


def cmd_stop(a):
    p = codex_home() / "lab.stop"
    p.write_text(f"{utc().strftime('%Y-%m-%dT%H:%MZ')} {a.why}\n", encoding="utf-8", newline="\n")
    print(f"lab stopped ({p}); `codex_run.py resume` turns it back on")
    return 0


def cmd_resume(a):
    (codex_home() / "lab.stop").unlink(missing_ok=True)
    print("lab on")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("tick").set_defaults(f=cmd_tick)
    n = sp.add_parser("next")
    n.add_argument("--dry", action="store_true")
    n.set_defaults(f=cmd_next)
    r = sp.add_parser("run")
    r.add_argument("card")
    r.add_argument("--dry", action="store_true")
    r.add_argument("--force", action="store_true", help="run although the lab spend guard says the budget is spent")
    r.set_defaults(f=cmd_run)
    k = sp.add_parser("ask")
    k.add_argument("title")
    k.add_argument("--kind", required=True, choices=tuple(TEMPLATES))
    k.add_argument("--scope", action="append", required=True, help="repo path the task reads or changes (repeatable)")
    k.add_argument("--id")
    k.add_argument("--goal")
    k.add_argument("--cmd", action="append")
    k.add_argument("--tests")
    k.add_argument("--size", default="S", choices=("S", "M"))
    k.add_argument("--prio", type=int, default=2, choices=range(1, 6))
    k.add_argument("--model")
    k.add_argument("--effort", choices=tasks.CODEX_EFFORTS)
    k.add_argument("--mutation-check", help="build cards: path/to/test.py::test_name that rejects dummy or shuffled output")
    k.set_defaults(f=cmd_ask)
    sp.add_parser("index").set_defaults(f=cmd_index)
    st = sp.add_parser("status")
    st.add_argument("--brief", action="store_true", help="leave out the Delivered block (what STATUS.md embeds)")
    st.set_defaults(f=cmd_status)
    s = sp.add_parser("stop")
    s.add_argument("why")
    s.set_defaults(f=cmd_stop)
    sp.add_parser("resume").set_defaults(f=cmd_resume)
    a = ap.parse_args(argv)
    return a.f(a)


if __name__ == "__main__":
    sys.exit(main())
