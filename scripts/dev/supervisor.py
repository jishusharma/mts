"""Supervisor CLI (MyTradingSys/system/SUPERVISOR.md, SV2): one call per wake.

Usage:
  python scripts/dev/supervisor.py tick [--json] [--shas <sha1,sha2...>] [--no-fetch]

Runs `git fetch origin` first (unless `--no-fetch`), then reads trunk refs and outputs one JSON object:
  - dispatch: top 8 ready cards from tasks.py dispatch
  - desk: counts from desk.py sweep
  - ci: state from ci_watch.py (red: bool, streak, message, ...)
  - gate_slots: busy slot count from sync.py gate_slot directory
  - shas: per sha in --shas, {"on_trunk": bool, "on_green": bool} via git merge-base --is-ancestor
  - lanes: ready counts for CODEX, SONNET, GEMINI, HAIKU
  - budget: age in seconds/hours and state from ~/.claude/mts-budget.json (or {"error": "missing"})

Every sub-read fails closed: any exception or unexpected failure sets that sub-field to {"error": "..."},
never to a success value.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import socket
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPT_DIR = Path(__file__).resolve().parent
REPO = SCRIPT_DIR.parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
SCHED_DIR = REPO / "scripts" / "sched"
if str(SCHED_DIR) not in sys.path:
    sys.path.insert(0, str(SCHED_DIR))

TRUNK_REF = "origin/fast-track"
GREEN_REF = "origin/green/fast-track"
TOP_DISPATCH_N = 8


def _now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def fetch_origin(repo: Path = REPO) -> None:
    r = subprocess.run(
        ["git", "-C", str(repo), "fetch", "--quiet", "origin"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if r.returncode != 0:
        raise RuntimeError(f"git fetch origin failed (rc={r.returncode}): {(r.stderr or r.stdout).strip()}")


def is_ancestor(repo: Path, sha: str, ref: str) -> bool:
    if not sha or not sha.strip():
        raise ValueError("empty sha")
    # Verify both sha and ref resolve to commit objects first; an unknown ref/sha or bad repo raises or returns False.
    r = subprocess.run(
        ["git", "-C", str(repo), "merge-base", "--is-ancestor", sha.strip(), ref],
        capture_output=True,
        text=True,
        timeout=15,
    )
    if r.returncode == 0:
        return True
    if r.returncode == 1:
        return False
    raise RuntimeError(f"git merge-base --is-ancestor {sha} {ref} failed (rc={r.returncode}): {(r.stderr or r.stdout).strip()}")


def read_shas(repo: Path, shas: list[str]) -> dict:
    out = {}
    for raw in shas:
        for sha in str(raw).split(","):
            s = sha.strip()
            if not s:
                continue
            try:
                on_trunk = bool(is_ancestor(repo, s, TRUNK_REF))
                try:
                    on_green = bool(is_ancestor(repo, s, GREEN_REF))
                except Exception:
                    on_green = False
                out[s] = {"on_trunk": on_trunk, "on_green": on_green}
            except (Exception, SystemExit) as e:
                out[s] = {"error": str(e), "on_trunk": False, "on_green": False}
    return out


def _dispatch_raw(repo: Path, as_of: datetime, host: str | None = None, login: str | None = None,
                  logins: list | None = None) -> dict:
    import tasks
    import lane_health
    cards = tasks.load_all(repo)
    reg = tasks.registry(repo)
    holds = tasks.active_holds(repo)
    claims = tasks.open_claims(repo)
    lane_st = lane_health.load(repo)
    return tasks.dispatch(cards, reg, holds, claims, lane_st, as_of, host or socket.gethostname(), repo,
                          login=login, logins=logins)


def read_dispatch(repo: Path = REPO, as_of: datetime | None = None, host: str | None = None,
                  login: str | None = None, logins: list | None = None) -> dict:
    try:
        as_of = as_of or _now_utc()
        try:
            if login:
                snap = _dispatch_raw(repo, as_of, host=host, login=login, logins=logins)
            else:
                snap = _dispatch_raw(repo, as_of, host=host)
        except TypeError:
            snap = _dispatch_raw(repo, as_of)
        disp = snap.get("dispatch", [])
        exc = snap.get("excluded", [])
        by_reason = {}
        for e in exc:
            rc = e.get("reason_code", "other")
            by_reason[rc] = by_reason.get(rc, 0) + 1
        return {
            "as_of": snap.get("as_of", as_of.strftime("%Y-%m-%dT%H:%M:%SZ")),
            "top": disp[:TOP_DISPATCH_N],
            "total_ready": len(disp),
            "excluded_count": len(exc),
            "excluded_by_reason": by_reason,
        }
    except (Exception, SystemExit) as e:
        return {"error": f"{type(e).__name__}: {e}"}


def _desk_raw(repo: Path, as_of: datetime) -> dict:
    import desk
    return desk.sweep(repo, ref=TRUNK_REF, as_of=as_of)


def read_desk(repo: Path = REPO, as_of: datetime | None = None) -> dict:
    try:
        as_of = as_of or _now_utc()
        res = _desk_raw(repo, as_of)
        return {
            "trunk": res.get("trunk", ""),
            "pending": res.get("pending", 0),
            "taken": res.get("taken", 0),
            "counts": res.get("counts", {}),
            "pending_per_target": res.get("pending_per_target", {}),
            "stale_claims_count": len(res.get("stale_claims", [])),
            "stale_claims": res.get("stale_claims", []),
        }
    except (Exception, SystemExit) as e:
        return {"error": f"{type(e).__name__}: {e}"}


def _ci_raw(use_cache: bool = False) -> list:
    import ci_watch
    return ci_watch.current(use_cache=use_cache)


def read_ci(now: datetime | None = None, use_cache: bool = False) -> dict:
    try:
        import ci_watch
        runs = _ci_raw(use_cache=use_cache)
        if not isinstance(runs, list):
            return {"error": "no workflow_runs returned"}
        n, bad, ok = ci_watch.streak(runs)
        is_red = n >= ci_watch.MIN_STREAK
        msg = ci_watch.message(runs, now=now) if is_red else f"CI ok: {n} failed run(s) in a row"
        return {
            "red": bool(is_red),
            "streak": n,
            "newest_failed_sha": (bad.get("head_sha") or "")[:8] if bad else "",
            "last_green_sha": (ok.get("head_sha") or "")[:8] if ok else "",
            "message": msg,
        }
    except (Exception, SystemExit) as e:
        return {"error": f"{type(e).__name__}: {e}"}


def gate_slots_dir(repo: Path = REPO) -> Path:
    import sync
    return sync.gate_slot(repo)._dir()


def pid_alive(pid: int) -> bool:
    import sync
    return sync.pid_alive(pid)


def _gate_slots_raw(repo: Path = REPO) -> dict:
    import sync
    d = gate_slots_dir(repo)
    total = sync.GATE_SLOTS
    busy = 0
    pids = []
    for i in range(total):
        p = d / f"slot-{i}"
        if not p.exists():
            continue
        try:
            raw = p.read_text(encoding="utf-8").strip()
            owner = int(raw) if raw else (0 if time.time() - p.stat().st_mtime > 10 else None)
        except (OSError, ValueError):
            owner = None
        if owner is None:
            busy += 1
        elif owner > 0 and pid_alive(owner):
            busy += 1
            pids.append(owner)
    return {"busy": busy, "total": total, "free": max(0, total - busy), "pids": pids}


def read_gate_slots(repo: Path = REPO) -> dict:
    try:
        return _gate_slots_raw(repo)
    except (Exception, SystemExit) as e:
        return {"error": f"{type(e).__name__}: {e}"}


def _ready_for_lane(repo: Path, lane: str) -> list:
    import tasks
    if lane == "GEMINI":
        cards = tasks.load_all(repo)
        reg = tasks.registry(repo)
        return [
            c for c in cards
            if c.get("state") == "ready"
            and (str(c.get("lane", "")).upper() == "GEMINI" or str(c.get("vendor", "")).lower() == "gemini")
            and not tasks.problems(c, cards, reg, repo)
        ]
    ready, _ = tasks.ready_cards(repo, lane=lane)
    return ready


def _lanes_raw(repo: Path = REPO) -> dict:
    codex = len(_ready_for_lane(repo, "CODEX"))
    sonnet = len(_ready_for_lane(repo, "SONNET"))
    gemini = len(_ready_for_lane(repo, "GEMINI"))
    haiku = len(_ready_for_lane(repo, "HAIKU"))
    return {
        "CODEX": codex,
        "SONNET": sonnet,
        "GEMINI": gemini,
        "HAIKU": haiku,
        "codex": codex,
        "sonnet": sonnet,
        "gemini": gemini,
        "haiku": haiku,
    }


def read_lanes(repo: Path = REPO) -> dict:
    try:
        return _lanes_raw(repo)
    except (Exception, SystemExit) as e:
        return {"error": f"{type(e).__name__}: {e}"}


def _budget_raw(as_of: datetime, home: Path | None = None) -> dict:
    import budget as budget_mod
    h = Path(home) if home is not None else budget_mod.home()
    p = h / "mts-budget.json"
    if not p.is_file():
        return {"error": "missing"}
    raw = json.loads(p.read_text(encoding="utf-8"))
    taken = budget_mod.parse(raw["utc"])
    age_s = max(0, int(round((as_of - taken).total_seconds())))
    age_h = round(age_s / 3600.0, 2)
    st, why = budget_mod.compute(raw, as_of)
    return {
        "state": st,
        "why": why,
        "age_s": age_s,
        "age_h": age_h,
        "utc": raw.get("utc", ""),
        "weekly_all_pct": raw.get("weekly_all_pct"),
        "five_hour_pct": raw.get("five_hour_pct"),
        "weekly_resets_at": raw.get("weekly_resets_at", ""),
    }


def read_budget(as_of: datetime | None = None, home: Path | None = None) -> dict:
    try:
        as_of = as_of or _now_utc()
        return _budget_raw(as_of, home=home)
    except (Exception, SystemExit) as e:
        return {"error": f"{type(e).__name__}: {e}"}


def read_peers(login: str | None, as_of: datetime, do_fetch: bool = True) -> dict:
    """The other logins' supervisors, seen only through their BUDGET signal lines (the app cannot message across logins).
    `active` = logins whose supervisor heartbeat (BUDGET line with sup=, < 75 min) has free slots, plus this one: the list dispatch shards over.
    Fails soft: {"error": ...} and dispatch then runs unsharded."""
    try:
        import traffic
        view, errs = traffic.budget_view(do_fetch=do_fetch, now=as_of)
        fresh = traffic.BUDGET_FRESH_H * 3600
        rows = {}
        for lg, r in view["logins"].items():
            at = traffic.utc(r.get("at"))
            age_h = round((as_of - at).total_seconds() / 3600, 1) if at else None
            rows[lg] = {"state": r["state"], "five_h": r.get("five_h"), "week": r.get("week"), "age_h": age_h,
                        "fresh": bool(at and (as_of - at).total_seconds() <= fresh)}
        sigs, _e = traffic.read_signals(as_of - timedelta(minutes=HEARTBEAT_MIN), as_of + timedelta(minutes=5))
        live = live_supervisors(sigs, as_of)
        active = {lg for lg, s in live.items() if s["free"] > 0}   # shard only over supervisors that can start work (SUPER_LOOP.md)
        if login:
            active.add(login)
        return {"self": login, "logins": rows, "active": sorted(active), "live": live, "overall": view["overall"],
                "missing": [x for x in "ABC" if x not in rows and x != login], "errors": errs}
    except (Exception, SystemExit) as e:
        return {"self": login, "error": f"{type(e).__name__}: {e}"}


def tick(
    repo: Path = REPO,
    shas: list[str] | None = None,
    no_fetch: bool = False,
    as_of: datetime | None = None,
    home: Path | None = None,
    login: str | None = None,
) -> dict:
    as_of = as_of or _now_utc()
    login = (login or os.environ.get("MTS_LOGIN") or "").strip().upper()[:1] or None
    peers = read_peers(login, as_of, do_fetch=not no_fetch) if login else {
        "self": None, "error": "login unknown: set env MTS_LOGIN=A|B|C (or pass --login) so budget and card shards work"}
    active = peers.get("active") if isinstance(peers, dict) else None
    fetch_status = {"ok": True, "skipped": bool(no_fetch)}
    if not no_fetch:
        try:
            fetch_origin(repo)
        except Exception as e:
            fetch_status = {"error": f"{type(e).__name__}: {e}"}

    try:
        shas_res = read_shas(repo, shas or [])
    except Exception as e:
        shas_res = {"error": f"{type(e).__name__}: {e}"}

    out = {
        "as_of": as_of.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "fetch": fetch_status,
        "login": login,
        "peers": peers,
        "dispatch": read_dispatch(repo, as_of=as_of, login=login, logins=active),
        "desk": read_desk(repo, as_of=as_of),
        "ci": read_ci(now=as_of),
        "gate_slots": read_gate_slots(repo),
        "shas": shas_res,
        "lanes": read_lanes(repo),
        "budget": read_budget(as_of=as_of, home=home),
    }
    return out


def parse_shas_arg(values: list[str] | None) -> list[str]:
    if not values:
        return []
    out = []
    for v in values:
        for item in str(v).split(","):
            s = item.strip()
            if s:
                out.append(s)
    return out


def parse_duration(val: str | int | float) -> int:
    if isinstance(val, (int, float)):
        return max(0, int(val))
    s = str(val).strip().lower()
    if s.endswith("m"):
        return max(0, int(float(s[:-1]) * 60))
    if s.endswith("h"):
        return max(0, int(float(s[:-1]) * 3600))
    if s.endswith("s"):
        return max(0, int(float(s[:-1])))
    return max(0, int(float(s)))


def _probe_wait_state(repo: Path, shas: list[str]) -> dict:
    shas_map = read_shas(repo, shas)
    sha_on_trunk = {s: bool(info.get("on_trunk")) if isinstance(info, dict) and "error" not in info else False for s, info in shas_map.items()}
    ci_info = read_ci(use_cache=False)
    ci_red = bool(ci_info["red"]) if isinstance(ci_info, dict) and "red" in ci_info else None
    gs_info = read_gate_slots(repo)
    busy_slots = int(gs_info["busy"]) if isinstance(gs_info, dict) and "busy" in gs_info else None
    total_slots = int(gs_info["total"]) if isinstance(gs_info, dict) and "total" in gs_info else None
    return {"shas": sha_on_trunk, "ci_red": ci_red, "busy_slots": busy_slots, "total_slots": total_slots}


STUCK_MAX = 2   # plans in a row with a free worker slot and no new worker: stop the actionable wake (no 5 min wake loop; OURS)
PLAN_MAX_MIN = 60   # a last plan older than this (watcher 50 min + one wake) is another run's: never acted on (OURS)


def _plan_fresh(last: dict, now: datetime | None = None) -> bool:
    at = _utc(last.get("at"))
    return bool(at) and 0 <= ((now or _now_utc()) - at).total_seconds() <= PLAN_MAX_MIN * 60


def _actionable(last: dict, current: dict, now: datetime | None = None) -> str | None:
    """d-six-slots-poll (operator 2026-10-23, option A): not a change but a state worth a wake. The last plan left worker slots free
    with more ready cards than it picked (RAMP), the window may spend, CI is green now and this machine has a free gate.
    Unknown CI or gates = no wake (fail closed); STUCK_MAX plans that spawned nothing or a plan older than PLAN_MAX_MIN = no wake."""
    try:
        if not _plan_fresh(last, now):
            return None
        pl = last.get("plan") or {}
        spare, ready = int(last.get("spare") or 0), int(last.get("ready_more") or 0)
        if pl.get("mode") not in ("SPEND", "NORMAL") or spare <= 0 or ready <= 0 or int(last.get("stuck") or 0) >= STUCK_MAX:
            return None
    except (TypeError, ValueError, AttributeError):
        return None         # a damaged plan file never wakes anyone and never kills the watcher
    busy, total = current.get("busy_slots"), current.get("total_slots")
    if current.get("ci_red") is not False or busy is None or total is None or busy >= total:
        return None
    return f"ACTIONABLE {spare} worker slot(s) free, {ready} more card(s) ready, CI green, gates {busy}/{total}: run plan and spawn"


def _woke_on(login: str, home=None) -> str:
    try:
        return (loop_home(home) / f"{login}-woke.txt").read_text(encoding="utf-8").strip()
    except (OSError, ValueError):     # missing or garbled (UnicodeDecodeError): never kills the watcher
        return ""


def _mark_woke(login: str, at: str, home=None) -> None:
    """One ACTIONABLE wake per plan: a watcher restarted without a new `plan` (compaction, a slip) never wakes again on the same one."""
    try:
        loop_home(home).mkdir(parents=True, exist_ok=True)
        (loop_home(home) / f"{login}-woke.txt").write_text(str(at), encoding="utf-8", newline="\n")
    except OSError:
        pass


def _last_plan(login: str | None, home=None) -> dict:
    if not login:
        return {}
    try:
        d = json.loads((loop_home(home) / f"{login}-last-plan.json").read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def _detect_transition(baseline: dict, current: dict) -> str | None:
    base_shas = baseline.get("shas", {})
    cur_shas = current.get("shas", {})
    for sha, now_on in cur_shas.items():
        was_on = bool(base_shas.get(sha, False))
        if not was_on and now_on:
            return f"TRANSITION sha {sha} landed on {TRUNK_REF}"

    base_ci = baseline.get("ci_red")
    cur_ci = current.get("ci_red")
    if base_ci is not None and cur_ci is not None and base_ci != cur_ci:
        state_str = "RED" if cur_ci else "GREEN"
        prev_str = "RED" if base_ci else "GREEN"
        return f"TRANSITION CI flipped {prev_str} -> {state_str}"

    base_busy = baseline.get("busy_slots")
    cur_busy = current.get("busy_slots")
    if base_busy is not None and cur_busy is not None and base_busy > 0 and cur_busy < base_busy:
        return f"TRANSITION gate slot freed ({base_busy} -> {cur_busy} busy)"

    return None


def wait_for_transition(
    repo: Path = REPO,
    shas: list[str] | None = None,
    timeout: int | str = 3000,
    interval: int | str = 300,
    probe=None,
    fetcher=None,
    sleeper=None,
    login: str | None = None,
    home=None,
) -> tuple[int, str]:
    """Record baseline at start and poll every `interval` seconds after fetching.
    Exits (0, reason) on the FIRST transition from baseline; never exits on a state that already held at baseline;
    with `login`, also exits (0, ACTIONABLE ...) from the first poll on when that login's last plan left a worker slot and ready cards
    unused (_actionable), at most once per plan (`<login>-woke.txt`); exits (3, reason) when `timeout` seconds elapse with no transition.
    """
    sha_list = parse_shas_arg(shas)
    timeout_s = parse_duration(timeout)
    interval_s = max(1, parse_duration(interval))
    probe_fn = probe or _probe_wait_state
    fetch_fn = fetcher or fetch_origin
    sleep_fn = sleeper or time.sleep

    try:
        fetch_fn(repo)
    except Exception:
        pass
    baseline = probe_fn(repo, sha_list)
    elapsed = 0

    while elapsed < timeout_s:
        step = min(interval_s, timeout_s - elapsed)
        sleep_fn(step)
        elapsed += step
        try:
            fetch_fn(repo)
        except Exception:
            pass
        current = probe_fn(repo, sha_list)
        reason = _detect_transition(baseline, current)
        b, c = baseline.get("busy_slots"), current.get("busy_slots")
        if not reason and c is not None and (b is None or c > b):     # unknown at the start: the first count read is the baseline
            baseline = {**baseline, "busy_slots": c}    # a ship that starts during the watch: its gate freeing (worker done) wakes too
        if not reason and login:
            last = _last_plan(login, home)
            if last.get("at") and str(last.get("at")) != _woke_on(login, home):
                reason = _actionable(last, current)
                if reason:
                    _mark_woke(login, last["at"], home)
        if reason:
            return 0, reason

    return 3, f"TIMEOUT after {timeout_s}s with no transition"


def brief(card_id: str, role: str | None = None, repo: Path = REPO, card: dict | None = None) -> str:
    """supervisor.py brief <card> [--role <role>]
    Generates the exact start prompt for a worker session.
    """
    import tasks
    if card is None:
        card = tasks.get(repo, card_id)

    # Determine role
    worker_role = role or card.get("role") or tasks.card_role(card) or "Builder"

    # Line 1: You are <Role>.
    line1 = f"You are {worker_role}."

    # Line 2: Card: <card_id>[, <chained_ids>...]. Boot: python <main_checkout>/scripts/dev/sync.py start <slug>; work only in the printed WORKTREE.
    # Note: <main_checkout> is the path to repo
    slug = card_id.lower()
    line2 = f"Card: {card_id}. Boot: python {repo}/scripts/dev/sync.py start {slug}; work only in the printed WORKTREE."

    lines = [line1, line2]

    # Followed by card goal, scope_in, defaults for open questions, and the standard stop lines
    goal = card.get("goal") or card.get("title") or ""
    if goal:
        lines.append(f"Goal: {goal}")

    scope_in = card.get("scope_in") or []
    if scope_in:
        # Filter out any secrets paths from display for defense in depth
        clean_scope = [s for s in scope_in if not any(x in s for x in (".secrets", ".env", "keys"))]
        if clean_scope:
            lines.append(f"Scope in: {'; '.join(clean_scope)}")

    # Defaults for open questions
    lines.append("Defaults for open questions: on any ambiguity take the most conservative default, never ask the operator.")

    # Standard stop line
    lines.append("Run with zero operator input: never ask; take the conservative default, log DECISION (OURS), continue")
    lines.append("Your final report starts with your ROLE LOADED banner line, then Result: and the content sha, at most 6 lines.")

    return "\n".join(lines)


# ---------- the five-hour loop (MyTradingSys/system/SUPER_LOOP.md): one `plan` call per wake, heartbeat, lanes, hand-over ----------
LOOP_DIR = "mts-superloop"      # under ~/.claude: this login's get_usage readings (local, never in git)
HEARTBEAT_MIN = 75              # a supervisor's heartbeat older than this = it is gone (watcher <= 50 min + slack; OURS)
SPAWN_CEIL = 80                 # 5 h % at which no Claude worker starts (SUPERVISOR.md pacing)
K_DEFAULT = 0.12                # weekly points per 5 h point until two readings in one window measure it (GUESS)
TRANSIT_MIN = 20                # write the hand-over this many minutes before the 5 h window resets (OURS)
DSA_DOWN_H = 24                 # a DSA target whose oldest pending row is older than this has no working bridge (OURS)
CLAUDE_LANES = ("SONNET", "HAIKU")
NB, NUC = "JIS-NB", "JIS-NUC"
LIVE_HOST_FILE = REPO / "MyTradingSys" / "system" / "live_host.txt"   # one line, the host that holds the live tree (LIVE_HOST_MOVE.md); same file as live_mirror.py


def live_host() -> str:
    """The live host's name; the JIS-NB lane runs there (JIS-NB until the cutover writes the laptop into the file)."""
    try:
        name = LIVE_HOST_FILE.read_text(encoding="utf-8").strip().upper()
    except OSError:
        name = ""
    return name or NB


HANDOVER_REL = "MyTradingSys/system/handover/SUPERVISOR_{}.md"
NUC_GATE = "ssh -i ~/.ssh/nuc_gate -o BatchMode=yes e-ngineers@192.168.29.110 ps"
HB_RE = re.compile(r"\bBUDGET login=([ABC])\b.*\bsup=\S+")


def _utc(s):
    """'2026-10-19T14:00Z', '...:00Z', '...:00.239Z' or '+00:00' -> aware datetime; anything else -> None."""
    try:
        d = datetime.fromisoformat(str(s).strip().replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


LAST_DAY_H = 24      # weekly room left this close to the reset is lost if unused (OURS)
LAST_DAY_CAP = 99    # operator 2026-10-22, login A at 97% with 15 h to reset: "do not exhaust it completely, but still use it ... slowly"


def weekly_cap(login: str, host: str, h_to_reset: float | None = None) -> int:
    """SUPER_SESSION.md rule 12: logins B and C stop at 75% of the week when they run on JIS-NB (operator choice); else 95%, raised to
    LAST_DAY_CAP in the last LAST_DAY_H before the weekly reset, so the last points are spent slowly instead of lost (pace_plan spreads them)."""
    if host.upper() == NB and login in ("B", "C"):
        return 75
    return LAST_DAY_CAP if h_to_reset is not None and 0 < h_to_reset <= LAST_DAY_H else 95


def loop_home(home=None) -> Path:
    return Path(home) if home else Path(os.environ.get("MTS_RELAY_HOME") or Path.home() / ".claude") / LOOP_DIR


def record_reading(login: str, rd: dict, home=None) -> list:
    """Append this reading to <home>/<login>.jsonl and return the last 50 (oldest first). A write error keeps the reading in memory only."""
    p = loop_home(home) / f"{login}.jsonl"
    rows = []
    try:
        rows = [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]
    except (OSError, ValueError):
        rows = []
    rows = (rows + [rd])[-50:]
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows), encoding="utf-8", newline="\n")
    except OSError:
        pass
    return rows


def _same_window(a: dict, b: dict) -> bool:
    ra, rb = _utc(a.get("five_reset")), _utc(b.get("five_reset"))
    return bool(ra and rb and abs((ra - rb).total_seconds()) <= 600)


def estimate_k(hist) -> float | None:
    """Weekly points per 5 h point, from consecutive readings inside one 5 h window (>= 5 points of 5 h use seen); None = not measured yet."""
    dp = dw = 0.0
    for a, b in zip(hist, hist[1:]):
        wa, wb = _utc(a.get("week_reset")), _utc(b.get("week_reset"))
        if _same_window(a, b) and wa and wb and abs((wa - wb).total_seconds()) <= 600:
            d5, d7 = float(b["five"]) - float(a["five"]), float(b["week"]) - float(a["week"])
            if d5 > 0 and d7 >= 0:
                dp, dw = dp + d5, dw + d7
    return round(dw / dp, 3) if dp >= 5 else None


RAMP = 1    # operator 2026-10-22 ("starts with minimum workers ... the operator can build on it"): at most one new worker per wake


def pace_plan(now: datetime, rd: dict, cap: float, hist=(), running: int = 0) -> dict:
    """Pure: the 5 h plan from one get_usage reading. Spread the weekly room (cap - week%) evenly over the 5 h windows left before the
    weekly reset, convert it to 5 h points (k), never past SPAWN_CEIL; then a feedback check: the burn since this window's first reading,
    projected to the window end, shrinks or grows the worker count. Start light: at most RAMP new workers per wake, so a fresh
    Supervisor opens with one worker and grows one per wake up to `slots`. Returns mode, slots (max Claude workers at once), new (start now), target."""
    five, week = float(rd["five"]), float(rd["week"])
    r5, rw = _utc(rd.get("five_reset")), _utc(rd.get("week_reset"))
    h_left = (r5 - now).total_seconds() / 3600 if r5 else 5.0
    if h_left <= 0:
        five, h_left, r5 = 0.0, 5.0, now + timedelta(hours=5)     # window already reset: the next call opens a fresh one
    h_left = min(h_left, 5.0)
    wk_h = (rw - now).total_seconds() / 3600 if rw else 168.0
    if wk_h <= 0:
        week, wk_h = 0.0, 168.0
    windows = max(1, math.ceil(wk_h / 5))
    share = max(0.0, cap - week) / windows
    k_meas = estimate_k(list(hist))
    k = k_meas or K_DEFAULT
    room = max(0.0, min(share / k, SPAWN_CEIL - five))
    target = five + room
    first = next((h for h in hist if _same_window(h, rd)), None)
    burn = projected = None
    if first and _utc(first.get("at")):
        dt = (now - _utc(first["at"])).total_seconds() / 3600
        if dt >= 0.25:
            burn = max(0.0, (five - float(first["five"])) / dt)
            projected = five + burn * h_left
    slots = 4 if room >= 40 else 3 if room >= 20 else 2 if room >= 10 else 1 if room >= 4 else 0
    why = [f"week {week:.0f}% of cap {cap:.0f} over {windows} window(s) = {share:.1f} wk pts here, k {k}"
           f"{'' if k_meas else ' (GUESS)'} -> room {room:.0f} pts of 5 h"]
    if projected is not None:
        if projected > target + 3:
            slots = min(slots, max(0, running - 1))
            why.append(f"burn {burn:.1f}/h projects {projected:.0f}% > target {target:.0f}%: shrink")
        elif projected < target - 10 and running < 4:
            slots = max(slots, min(4, running + 1))
            why.append(f"burn {burn:.1f}/h projects {projected:.0f}% < target {target:.0f}%: grow")
    if five >= SPAWN_CEIL or room < 2:
        mode, slots = "STOP", 0
    elif five >= 70:
        mode, slots = "SUPERVISOR-ONLY", 0
    elif five >= 60:
        mode, slots = "CRUCIAL-ONLY", min(slots, 1)
    else:
        mode = "SPEND" if room >= 30 else "NORMAL"
    return {"mode": mode, "slots": slots, "new": min(RAMP, max(0, slots - running)), "running": running, "five": five, "week": week,
            "cap": cap, "k": k, "k_measured": bool(k_meas), "room": round(room, 1), "target": round(target), "h_left": round(h_left, 2),
            "burn": None if burn is None else round(burn, 2), "projected": None if projected is None else round(projected),
            "five_reset": r5.strftime("%Y-%m-%dT%H:%MZ"), "week_reset": (rw or now + timedelta(days=7)).strftime("%Y-%m-%dT%H:%MZ"),
            "transit": (r5 - timedelta(minutes=TRANSIT_MIN)).strftime("%Y-%m-%dT%H:%MZ"), "why": "; ".join(why)}


def heartbeat_text(login: str, host: str, plan: dict, dsa: str | None = None, free: int | None = None, mode: str | None = None,
                   gates: dict | None = None) -> str:
    """The one line every supervisor sends per wake: a BUDGET line (traffic.py budget parses its head) plus who runs where and
    `gates=busy/total` of its machine (read_gate_slots), so every supervisor sees all machines' gates (operator 2026-10-23).
    No card ids (the public signal cleaner cuts long tokens); under 200 chars."""
    t = (f"BUDGET login={login} 5h={round(plan['five'])}% week={round(plan['week'])}% reset={plan['week_reset']} "
         f"sup={host.upper()} mode={mode or plan['mode']} run={plan['running']} free={plan['new'] if free is None else free} "
         f"end={plan['five_reset'][11:]}")
    if gates and "busy" in gates:
        t += f" gates={gates['busy']}/{gates['total']}"
    return t + (f" dsa={dsa}" if dsa else "")


def gates_line(live: dict) -> str:
    """One GATES line over every machine with a live supervisor: a gate tests code on the machine that holds it, so a worker
    started where gates are free ships sooner. Machines with no supervisor heartbeat (or an old one without gates=) read `?`."""
    by_host = {}
    for s in live.values():
        g = s.get("gates")
        if s["host"] not in by_host or (g and not by_host[s["host"]]):
            by_host[s["host"]] = g
    parts, free, total = [], 0, 0
    for h, g in sorted(by_host.items()):
        if g:
            b, t = g
            parts.append(f"{h} {b}/{t} busy")
            free, total = free + max(0, t - b), total + t
        else:
            parts.append(f"{h} ?")
    return f"GATES {'; '.join(parts)}; free {free} of {total} known"


def _gates_kv(v):
    m = re.fullmatch(r"(\d+)/(\d+)", v or "")
    return (int(m.group(1)), int(m.group(2))) if m else None


def live_supervisors(sigs, now: datetime, minutes: int = HEARTBEAT_MIN) -> dict:
    """{login: {host, at, mode, run, free, dsa}} from the newest heartbeat per login younger than `minutes` (sigs = traffic.read_signals rows)."""
    out = {}
    for t, _s, _k, x in sorted(sigs, key=lambda r: r[0]):
        m = HB_RE.search(x)
        if not m or (now - t).total_seconds() > minutes * 60:
            continue
        kv = dict(re.findall(r"(\w+)=(\S+)", x))
        if kv.get("mode") == "ENDED":
            out.pop(m.group(1), None)
            continue
        out[m.group(1)] = {"host": kv.get("sup", "?").upper(), "at": t.strftime("%Y-%m-%dT%H:%MZ"), "mode": kv.get("mode", "?"),
                           "run": int(kv.get("run", 0) or 0) if str(kv.get("run", "0")).isdigit() else 0,
                           "free": int(kv["free"]) if str(kv.get("free", "")).isdigit() else 0, "dsa": kv.get("dsa"),
                           "gates": _gates_kv(kv.get("gates"))}
    return out


def lane_owner(live: dict, host: str | None = None) -> str | None:
    """Who runs a shared lane action this wake: the lowest login letter among live supervisors on `host` (if any), else the lowest
    live login anywhere. Same answer on every machine from the same signals, so exactly one supervisor acts."""
    on = sorted(l for l, h in live.items() if host and h["host"] == host.upper())
    return on[0] if on else (sorted(live)[0] if live else None)


def pick_cards(rows, host: str, n: int, crucial_only: bool = False, live: str | None = None) -> list:
    """The first n dispatch rows a Claude worker on `host` can run: lanes SONNET/HAIKU (JIS-NB lane only on the live host), Lab_Guy cards only on
    JIS-NUC, CRUCIAL/CRITICAL only when the window says so. Rows are already ranked (pinned CI first, own shard first)."""
    h = host.upper()
    live = (live or live_host()).upper()
    ok = []
    for r in rows:
        lane = str(r.get("lane", "")).upper()
        if not (lane in CLAUDE_LANES or (lane == NB and h == live)):
            continue
        if r.get("role") == "Lab_Guy" and h != NUC:
            continue
        if crucial_only and str(r.get("weight", "")).upper() not in ("CRUCIAL", "CRITICAL"):
            continue
        ok.append(r)
    return ok[:max(0, n)]


def dsa_targets_state(rows, now: datetime) -> dict:
    """{target: {pending, oldest_h, down}} for the DeepSeek targets from trunk desk rows; down = oldest pending older than DSA_DOWN_H."""
    out = {}
    for r in rows:
        tg = str(r.get("target", ""))
        if r.get("status") != "pending" or not tg.startswith("DSA"):
            continue
        at = _utc(r.get("posted"))
        age = (now - at).total_seconds() / 3600 if at else 0.0
        d = out.setdefault(tg, {"pending": 0, "oldest_h": 0.0})
        d["pending"] += 1
        d["oldest_h"] = round(max(d["oldest_h"], age), 1)
    for d in out.values():
        d["down"] = d["oldest_h"] > DSA_DOWN_H
    return out


def plan_lines(login: str, host: str, plan: dict, live: dict, ctx: dict, gate_key: bool) -> list:
    """Pure: the text a supervisor reads each wake. PLAN/PEER/BOARD lines are state; RUN lines are commands to run now in one Bash call;
    SPAWN is who to start; NOTE needs nothing from you; OPERATOR is the only thing the operator must do."""
    h = host.upper()
    L = [f"PLAN login={login} host={h} mode={plan['mode']} 5h={plan['five']:.0f}% -> target {plan['target']}% by {plan['five_reset']} "
         f"week={plan['week']:.0f}%/{plan['cap']:.0f} slots={plan['slots']} running={plan['running']} new={plan['new']} ({plan['why']})"]
    for lg, s in sorted(live.items()):
        if lg != login:
            g = s.get("gates")
            L.append(f"PEER {lg} on {s['host']} mode={s['mode']} run={s['run']} free={s['free']} gates={f'{g[0]}/{g[1]}' if g else '?'} "
                     f"seen {s['at']}")
    L.append(gates_line(live))
    mine = (live.get(login) or {}).get("gates")
    if mine and mine[0] >= mine[1]:
        roomy = sorted({s["host"] for lg, s in live.items() if s["host"] != h and s.get("gates") and s["gates"][0] < s["gates"][1]})
        if roomy:
            L.append(f"NOTE your {mine[1]} gates are all busy; free gates on {', '.join(roomy)}: a worker started now waits in the "
                     "gate queue, so spawn build cards first and let their peers take ship-ready ones")
    unknown = bool(ctx.get("peers_unknown"))
    if unknown:
        L.append("PEERS UNKNOWN (signals not read): shared-lane actions below are NOTE only this wake; do not touch NEXT_SESSION.md")
    elif len(live) <= 1:
        L.append("PEER none live (no heartbeat < 75 min): you are alone; NEXT_SESSION.md is yours to update at transit")
    for hid, kind, title in ctx.get("holds", []):
        L.append(f"BOARD {kind} {hid}: {title} (no card of that kind)")
    if ctx.get("handover"):
        L.append(f"HANDOVER {ctx['handover']}")
    ci = ctx.get("ci") or {}
    if ci.get("error"):
        L.append(f"NOTE CI unknown ({ci['error'][:80]}): treat as red for live-path cards")
    if ci.get("red"):
        L.append(f"SPAWN CI RED: one worker on the pinned ci-* card only; nothing else ships ({ci.get('message', '')[:80]})")
    picks = ctx.get("picks", [])
    if plan["new"] and picks and not ci.get("red"):
        L.append(f"SPAWN {len(picks)}: " + ", ".join(f"{p['id']} ({p.get('role') or 'Builder'}, {p.get('worker') or '?'}, "
                                                  f"{'own' if p.get('own', True) else 'peer'})" for p in picks)
                 + "  [operator turn: sessions, 2 chained cards each; event turn: size-S Agents only]")
    elif plan["new"] and not picks:
        L.append("NOTE no Claude card fits this host: Session_Planner (foreground Agent) refines raw cards, or idle")
    # shared lanes: exactly one live supervisor (lane_owner) acts on each
    me_codex, me_any = lane_owner(live, NUC) == login, lane_owner(live) == login
    claude_ok = plan["mode"] not in ("STOP", "SUPERVISOR-ONLY") and not ci.get("red")
    if unknown:
        if lane_owner(live, NUC) == login and ctx.get("codex_ready"):
            L.append(f"NOTE GPT lab: {ctx['codex_ready']} CODEX card(s) ready; owner unknown this wake")
        me_codex = me_any = False
    if ctx.get("refine_raw") and claude_ok:
        L.append(f"RUN Session_Planner (Agent, sonnet): refine {ctx['refine_raw']} raw cards")
    cx = ctx.get("codex_ready", 0)
    if me_codex and cx:
        if h == NUC:
            L.append("RUN python scripts/dev/codex_run.py tick")
        elif gate_key:
            L.append(f"RUN printf 'Set-Location F:/MTS/mts-codex-lab; python scripts/dev/codex_run.py tick\\n' | {NUC_GATE}")
        else:
            L.append(f"NOTE GPT lab: {cx} CODEX card(s) ready, no NUC supervisor and no gate key here: lab idle until one boots on JIS-NUC")
    if me_codex and claude_ok and ctx.get("gemini_ready") and h == NUC:
        L.append(f"SPAWN Lab_Guy for {ctx['gemini_ready']} Gemini card(s) (gemini_queue.py run <card>:medium, reviews the branch)")
    if me_codex and 0 <= cx < 8:
        L.append(f"NOTE CODEX lane {cx} ready (< 8): Session_Planner refines CODEX cards this wake")
    if me_any and ctx.get("dsa_unposted"):
        L.append(f"RUN python -u scripts/dev/desk.py assign > ~/.claude/{LOOP_DIR}/assign.log 2>&1 &   "
                 f"({ctx['dsa_unposted']} ready DSA-lane card(s) without a desk row)")
    for tg, d in sorted(ctx.get("dsa", {}).items()):
        if d["down"]:
            L.append(f"OPERATOR DeepSeek {tg}: oldest pending row {d['oldest_h']:.0f} h untaken: open the DeepSeek chat on that machine "
                     f"and arm hands-free; post no more rows to {tg} until it moves")
    for lg, s in sorted(live.items()):
        if s.get("dsa") == "down":
            L.append(f"OPERATOR AIBridge agent down on {s['host']} (heartbeat of {lg}): run scripts/dev/aibridge_health.py there")
    if me_any and claude_ok and ctx.get("pipeliner_free") and ctx.get("desk_pending"):
        L.append(f"SPAWN Pipeliner on the next operator turn (`You are Pipeliner.`, lease free, {ctx['desk_pending']} desk rows pending)")
    if me_any and gate_key and ctx.get("nuc_ok") and not any(s["host"] == NUC for s in live.values()) and ctx.get("spare"):
        L.append(f"RUN python scripts/dev/nuc_wake.py --card {ctx['spare']} --name {ctx['spare'][:20]}   (NUC has no supervisor: one headless "
                 f"worker there, the NUC login's budget)")
    if me_any:
        for ih, logins, n in ctx.get("idle_hosts", []):
            L.append(f"OPERATOR start a Supervisor on {ih}: no heartbeat < {HEARTBEAT_MIN} min, {n} card(s) ready for it, budget on "
                     f"login {'/'.join(logins)}: `You are Supervisor. Login {logins[0]}.`")
    L.append(f"RUN (background) python scripts/dev/supervisor.py wait --timeout 50m --login {login}{ctx.get('shas_arg', '')}   then end the turn")
    L.append(f"TRANSIT at {plan['transit']}: python scripts/dev/supervisor.py handover --login {login} --note \"<one line>\"; ship it; "
             f"successor line: You are Supervisor. Login {login}. Continue from {HANDOVER_REL.format(login)}")
    return L


def _local_bridge(host: str) -> str | None:
    if host.upper() not in (NB, NUC):
        return None
    import socket as _s
    try:
        _s.create_connection(("127.0.0.1", 7181), timeout=2).close()
        return "up"
    except OSError:
        return "down"


def _git_show(repo: Path, rel: str) -> str | None:
    r = subprocess.run(["git", "-C", str(repo), "show", f"{TRUNK_REF}:{rel}"], capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=30)
    return r.stdout if r.returncode == 0 else None


def nuc_budget_ok(login: str, mode: str, now: datetime, no_fetch: bool = True, view=None, inv=None) -> bool:
    """A headless NUC worker (nuc_wake.py) spends whichever login is signed in on the NUC, which no script can see. So it is allowed only
    when EVERY login the NUC may run (traffic_inventory.json) has a fresh BUDGET reading that is not THROTTLE, and this login, if it is one
    of them, is not in STOP. Unknown = no (fail closed)."""
    try:
        import traffic
        inv = inv or traffic.inv_cache()
        view = view if view is not None else traffic.budget_view(do_fetch=not no_fetch, now=now)[0]
        for lg in inv["machines"][NUC]["logins"]:
            r = view["logins"].get(lg)
            at = traffic.utc((r or {}).get("at"))
            if not r or not at or (now - at).total_seconds() > traffic.BUDGET_FRESH_H * 3600 or r["state"] == "THROTTLE":
                return False
            if lg == login and mode in ("STOP", "SUPERVISOR-ONLY"):
                return False
        return True
    except Exception:
        return False


IDLE_NAG_H = 2      # the same "start a Supervisor on <host>" line at most once per this many hours per machine (OURS)


def idle_hosts(live: dict, dispatch, now: datetime, no_fetch: bool = True, view=None, inv=None) -> list:
    """d-six-slots-poll (operator 2026-10-23, option C): [(host, [logins], ready)] for each machine with no live supervisor, at least one
    ready card it can run and a login it may run that has no live supervisor, a fresh SPEND/NORMAL BUDGET reading and weekly room under
    its cap on that machine (weekly_cap). Nothing can start a session on another machine (SCHEDULING_POLICY.md), so the answer is an
    OPERATOR line. Unreadable signals or inventory = [] (no line). plan() already fetched the signals: no_fetch by default."""
    try:
        import traffic
        inv = inv or traffic.inv_cache()
        if view is None:
            view, errs = traffic.budget_view(do_fetch=not no_fetch, now=now)
            if errs:
                return []
        busy_hosts = {str(s.get("host", "")).upper() for s in live.values()}
        out, used = [], set()       # one login runs one supervisor: never offer the same login for two machines
        for h, m in sorted(inv["machines"].items()):
            if h.upper() in busy_hosts:
                continue
            ok = []
            for lg in m.get("logins", []):
                r = view["logins"].get(lg) or {}
                at = traffic.utc(r.get("at"))
                fresh = bool(at) and 0 <= (now - at).total_seconds() <= traffic.BUDGET_FRESH_H * 3600
                rs = traffic.utc(r.get("reset"))
                try:
                    room = r.get("week") is not None and float(r["week"]) < weekly_cap(lg, h, (rs - now).total_seconds() / 3600 if rs else None)
                except (TypeError, ValueError):
                    room = False
                if lg not in live and lg not in used and fresh and r.get("state") in ("SPEND", "NORMAL") and room:
                    ok.append(lg)
            n = len(pick_cards(dispatch, h, 99))
            if ok and n:
                out.append((h.upper(), ok, n))
                used.add(ok[0])
        return out
    except (Exception, SystemExit):
        return []


def _idle_nag_due(hosts: list, now: datetime, home=None) -> list:
    """Drop machines told within IDLE_NAG_H (stamp per machine under loop_home); unreadable stamp = due."""
    due = []
    for row in hosts:
        try:
            t = _utc((loop_home(home) / f"idle_{row[0]}.last").read_text(encoding="utf-8").strip())
        except (OSError, ValueError):
            t = None
        if not t or (now - t).total_seconds() >= IDLE_NAG_H * 3600:
            due.append(row)
    return due


def plan(repo: Path, login: str, rd: dict, running: int = 0, send: bool = True, no_fetch: bool = False, host: str | None = None,
         home=None, now: datetime | None = None, shas: list | None = None) -> tuple[list, dict]:
    """One call per wake (boot included): records the reading, sends the heartbeat, reads peers, board, hand-over, CI, dispatch,
    lanes and desk from trunk, and returns (lines, data). Every sub-read fails soft into a NOTE line, never into a success value."""
    import tasks
    import traffic
    now = now or _now_utc()
    host = (host or socket.gethostname()).upper()
    login = login.strip().upper()[:1]
    rd = {**rd, "at": now.strftime("%Y-%m-%dT%H:%M:%SZ")}
    hist = record_reading(login, rd, home)
    rw = _utc(rd.get("week_reset"))
    gs = read_gate_slots(repo)
    pl = pace_plan(now, rd, weekly_cap(login, host, (rw - now).total_seconds() / 3600 if rw else None), hist[:-1], running)
    prev = _last_plan(login, home)
    notes, ctx = [], {}
    if not no_fetch:
        try:
            fetch_origin(repo)
        except Exception as e:
            ctx["peers_unknown"] = True
            notes.append(f"NOTE fetch failed ({e}): state below may be old")
    dsa_local = _local_bridge(host)
    sent = None
    try:
        if not no_fetch:
            traffic.refresh_signals()
        sigs, _e = traffic.read_signals(now - timedelta(minutes=HEARTBEAT_MIN), now + timedelta(minutes=5))
        if _e:
            ctx["peers_unknown"] = True
    except (Exception, SystemExit) as e:
        sigs = []
        ctx["peers_unknown"] = True
        notes.append(f"NOTE signals unreadable ({type(e).__name__}): peers unknown")
    live = live_supervisors(sigs, now)
    live[login] = {"host": host, "at": now.strftime("%Y-%m-%dT%H:%MZ"), "mode": pl["mode"], "run": running, "free": pl["new"], "dsa": dsa_local,
                   "gates": (gs["busy"], gs["total"]) if "busy" in gs else None}
    shard = sorted(l for l, s in live.items() if s["free"] > 0) or [login]
    try:
        import desk
        board = _git_show(repo, "MyTradingSys/system/ANNOUNCEMENTS.md")
        if board is None:
            raise OSError("ANNOUNCEMENTS.md not on trunk")
        ctx["holds"] = desk.active_holds(board)
    except (Exception, SystemExit) as e:
        notes.append(f"NOTE board unreadable ({type(e).__name__}): read ANNOUNCEMENTS.md ACTIVE by hand")
    ho = _git_show(repo, HANDOVER_REL.format(login))
    if ho:
        nxt = [x.strip() for x in ho.splitlines() if x.strip().startswith(("- Next", "Next", "- next"))][:1]
        ctx["handover"] = HANDOVER_REL.format(login) + " on trunk" + (": " + nxt[0][:160] if nxt else "")
    ctx["ci"] = read_ci(now=now)
    try:
        snap = _dispatch_raw(repo, now, host=host, login=login, logins=shard)
        ctx["picks"] = pick_cards(snap.get("dispatch", []), host, pl["new"], pl["mode"] == "CRUCIAL-ONLY")
        rest = pick_cards(snap.get("dispatch", []), NUC, 10)
        spare = [r["id"] for r in rest if r["id"] not in {p["id"] for p in ctx["picks"]}]
        ctx["spare"] = spare[0] if spare else None
        ctx["ready_here"] = len(pick_cards(snap.get("dispatch", []), host, 99, pl["mode"] == "CRUCIAL-ONLY"))
        if not ctx.get("peers_unknown"):
            ctx["idle_hosts"] = _idle_nag_due(idle_hosts(live, snap.get("dispatch", []), now), now, home)
    except (Exception, SystemExit) as e:
        ctx["picks"] = []
        notes.append(f"NOTE dispatch failed ({type(e).__name__}: {str(e)[:80]})")
    try:
        cards, reg = tasks.load_all(repo), tasks.registry(repo)
        ready = [c for c in cards if c.get("state") == "ready" and not tasks.problems(c, cards, reg, repo)]
        ctx["codex_ready"] = sum(1 for c in ready if str(c.get("lane", "")).upper() == "CODEX")
        ctx["refine_raw"] = len(tasks.stale_raw(cards))
        ctx["gemini_ready"] = sum(1 for c in ready if str(c.get("vendor", "")).lower() == "gemini")
        import desk
        rows = desk.trunk_rows(repo, TRUNK_REF)
        have = {r.get("card") for r in rows}
        ctx["dsa_unposted"] = sum(1 for c in ready if str(c.get("lane", "")) in desk.DSA_LANES and c["id"] not in have)
        ctx["dsa"] = dsa_targets_state(rows, now)
        ctx["desk_pending"] = sum(1 for r in rows if r.get("status") == "pending")
    except (Exception, SystemExit) as e:
        notes.append(f"NOTE lanes/desk unreadable ({type(e).__name__}: {str(e)[:80]})")
    try:
        import lease
        ctx["pipeliner_free"] = lease.status(repo, roles=("Pipeliner",), do_fetch=False)["Pipeliner"].get("state") in ("free", "expired")
    except (Exception, SystemExit):
        ctx["pipeliner_free"] = False
    ctx["nuc_ok"] = nuc_budget_ok(login, pl["mode"], now, no_fetch)
    stamp = loop_home(home) / "nuc_wake.last"
    try:
        last_wake = _utc(stamp.read_text(encoding="utf-8").strip())
    except OSError:
        last_wake = None
    if last_wake and (now - last_wake).total_seconds() < 5 * 3600:
        ctx["nuc_ok"] = False
    free = 0 if (ctx["ci"] or {}).get("red") else min(pl["new"], len(ctx.get("picks", [])))
    if send:
        try:
            import mts_signal
            sent = mts_signal.send(heartbeat_text(login, host, pl, dsa_local, free=free, gates=gs), to="all", kind="note")
        except Exception as e:
            sent = False
            notes.append(f"NOTE heartbeat error {type(e).__name__}")
        if not sent:
            notes.append("NOTE heartbeat NOT sent: peers will not count you; your claims still lock your cards")
        try:
            budget_rec = {"utc": rd["at"], "weekly_all_pct": pl["week"], "weekly_resets_at": pl["week_reset"], "five_hour_pct": pl["five"]}
            bh = Path(os.environ.get("MTS_RELAY_HOME") or Path.home() / ".claude")
            bh.mkdir(parents=True, exist_ok=True)
            (bh / "mts-budget.json").write_text(json.dumps(budget_rec, sort_keys=True), encoding="utf-8", newline="\n")
        except OSError:
            pass
    if shas:
        ctx["shas_arg"] = " --shas " + ",".join(shas)
    live[login]["free"] = free
    lines = plan_lines(login, host, pl, live, ctx, (Path.home() / ".ssh" / "nuc_gate").exists()) + notes
    loop_home(home).mkdir(parents=True, exist_ok=True)
    for ih, _lg, _n in (ctx.get("idle_hosts", []) if send else []):     # a dry run never silences the line
        if any(x.startswith(f"OPERATOR start a Supervisor on {ih}:") for x in lines):
            try:
                (loop_home(home) / f"idle_{ih}.last").write_text(now.strftime("%Y-%m-%dT%H:%M:%SZ"), encoding="utf-8", newline="\n")
            except OSError:
                pass
    if any("nuc_wake.py" in x for x in lines):
        try:
            stamp.write_text(now.strftime("%Y-%m-%dT%H:%M:%SZ"), encoding="utf-8", newline="\n")
        except OSError:
            pass
    spare_slots = max(0, pl["slots"] - running - pl["new"])
    try:    # stuck: plans in a row that told you to start workers (free > 0: CI green, cards picked) and running did not grow
        asked = _plan_fresh(prev, now) and int(prev.get("free") or 0) > 0
        stuck = int(prev.get("stuck") or 0) + 1 if asked and running <= int((prev.get("plan") or {}).get("running") or 0) else 0
    except (TypeError, ValueError, AttributeError):
        stuck = 0       # a damaged last plan never blocks this one
    data = {"plan": pl, "live": live, "shard": shard, "heartbeat_sent": sent, "picks": [p["id"] for p in ctx.get("picks", [])],
            "lines": lines, "spare": spare_slots, "ready_more": max(0, ctx.get("ready_here", 0) - len(ctx.get("picks", []))),
            "stuck": stuck, "free": free, "at": now.strftime("%Y-%m-%dT%H:%M:%SZ")}
    try:
        # a --no-send dry run never replaces the real plan: its `at`, `running` and `stuck` drive the ACTIONABLE wake and the hand-over
        (loop_home(home) / f"{login}-{'last' if send else 'dryrun'}-plan.json").write_text(json.dumps(data, indent=1, sort_keys=True, default=str),
                                                                 encoding="utf-8", newline="\n")
    except OSError:
        pass
    return lines, data


def render_handover(login: str, host: str, now: datetime, last: dict, claims: list, note: str = "") -> str:
    """Pure: the per-login hand-over file the next `You are Supervisor.` boot reads (plan prints its Next line)."""
    pl = last.get("plan", {})
    peers = ", ".join(f"{lg}@{s.get('host', '?')}" for lg, s in sorted(last.get("live", {}).items()) if lg != login)
    L = [f"# Supervisor hand-over, login {login} ({host}, {now.strftime('%Y-%m-%dT%H:%MZ')})", "",
         f"- Next: {note or 'continue the dispatch order; nothing pending from this run'}",
         f"- Budget at hand-over: 5h {pl.get('five', '?')}% (reset {pl.get('five_reset', '?')}), week {pl.get('week', '?')}% of cap "
         f"{pl.get('cap', '?')} (reset {pl.get('week_reset', '?')}), mode {pl.get('mode', '?')}, k {pl.get('k', '?')}"
         f"{'' if pl.get('k_measured') else ' (GUESS)'}",
         f"- Peers live at hand-over: {peers or 'none'}",
         f"- Last picks: {', '.join(last.get('picks', [])) or 'none'}",
         f"- Open claims from {host}: {', '.join(claims) or 'none'} (finish, hand over in the card, or release by the claim rules)",
         "", f"Successor: `You are Supervisor. Login {login}. Continue from {HANDOVER_REL.format(login)}`", ""]
    return "\n".join(L)


def handover(repo: Path, login: str, note: str = "", host: str | None = None, home=None, now: datetime | None = None,
             send: bool = False) -> Path:
    import sync
    now = now or _now_utc()
    host = (host or socket.gethostname()).upper()
    login = login.strip().upper()[:1]
    try:
        last = json.loads((loop_home(home) / f"{login}-last-plan.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        last = {}
    try:
        claims = [s for s, kv in sync.read_claims(repo, TRUNK_REF) if (kv.get("host") or "").upper() == host]
    except Exception:
        claims = ["(claims unreadable)"]
    p = Path(repo) / HANDOVER_REL.format(login)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(render_handover(login, host, now, last, claims, note), encoding="utf-8", newline="\n")
    if send and last.get("plan"):
        try:
            import mts_signal
            mts_signal.send(heartbeat_text(login, host, {**last["plan"], "running": 0}, free=0, mode="ENDED"), to="all", kind="note")
        except Exception:
            pass   # the 75 min heartbeat age still removes this supervisor
    return p


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_tick = sub.add_parser("tick", help="one read-only supervisor status snapshot per wake")
    p_tick.add_argument("--json", action="store_true", help="output JSON (default format)")
    p_tick.add_argument("--shas", nargs="*", default=[], help="comma- or space-separated commit shas to check on trunk/green")
    p_tick.add_argument("--login", default=None, help="this session's login letter A|B|C (default env MTS_LOGIN)")
    p_tick.add_argument("--no-fetch", action="store_true", help="skip git fetch origin before reading refs")

    p_wait = sub.add_parser("wait", help="background watcher: exits 0 on first transition from baseline, 3 on timeout")
    p_wait.add_argument("--shas", nargs="*", default=[], help="comma- or space-separated commit shas to watch for landing on trunk")
    p_wait.add_argument("--timeout", default="3000", help="timeout in seconds or with s/m/h suffix (default 3000)")
    p_wait.add_argument("--interval", default="300", help="poll interval in seconds or with s/m/h suffix (default 300)")
    p_wait.add_argument("--login", default=os.environ.get("MTS_LOGIN"), help="A|B|C: also wake when its last plan left a slot and cards unused")

    p_brief = sub.add_parser("brief", help="generate exact start prompt text for a worker session")
    p_brief.add_argument("card", help="card id to brief")
    p_brief.add_argument("--role", default=None, help="role to start worker as (defaults to Builder)")

    p_plan = sub.add_parser("plan", help="every wake incl. boot: record get_usage, heartbeat, peers, lanes; prints PLAN/RUN/SPAWN lines")
    p_plan.add_argument("--login", default=os.environ.get("MTS_LOGIN"), help="A|B|C (your account email in CLOUD_ACCOUNTS.md; default env MTS_LOGIN)")
    p_plan.add_argument("--five", type=float, required=True, help="get_usage 5-hour limit percentUsed")
    p_plan.add_argument("--five-reset", required=True, help="get_usage 5-hour resetsAt (UTC)")
    p_plan.add_argument("--week", type=float, required=True, help="get_usage Weekly all models percentUsed")
    p_plan.add_argument("--week-reset", required=True, help="get_usage Weekly all models resetsAt (UTC)")
    p_plan.add_argument("--running", type=int, default=0, help="Claude workers you have running now")
    p_plan.add_argument("--shas", nargs="*", default=[], help="reported shas, passed on to the watcher line")
    p_plan.add_argument("--no-send", action="store_true", help="do not send the heartbeat (tests, dry runs)")
    p_plan.add_argument("--no-fetch", action="store_true")
    p_plan.add_argument("--json", action="store_true")

    p_ho = sub.add_parser("handover", help="write handover/SUPERVISOR_<login>.md from the last plan (ship it once)")
    p_ho.add_argument("--login", default=os.environ.get("MTS_LOGIN"))
    p_ho.add_argument("--note", default="", help="one line: what the successor does first")
    p_ho.add_argument("--no-send", action="store_true", help="do not send the ENDED heartbeat")

    args = ap.parse_args(argv)
    if args.cmd in ("plan", "handover") and (not args.login or args.login.strip().upper()[:1] not in ("A", "B", "C")):
        print("login must be A, B or C: match your account email to CLOUD_ACCOUNTS.md LOGINS (or set env MTS_LOGIN)")
        return 2
    if args.cmd == "plan":
        bad = [n for n, v in (("--five-reset", args.five_reset), ("--week-reset", args.week_reset)) if _utc(v) is None]
        if bad:
            print(f"{', '.join(bad)}: UTC time like 2026-10-19T14:00Z")
            return 2
        if not (0 <= args.five <= 100 and 0 <= args.week <= 100 and args.running >= 0):
            print("--five and --week are percentages 0-100 (get_usage percentUsed); --running >= 0")
            return 2
        rd = {"five": args.five, "five_reset": args.five_reset, "week": args.week, "week_reset": args.week_reset}
        lines, data = plan(REPO, args.login, rd, running=args.running, send=not args.no_send, no_fetch=args.no_fetch,
                           shas=parse_shas_arg(args.shas))
        print(json.dumps(data, indent=1, sort_keys=True, default=str) if args.json else chr(10).join(lines))
        return 0
    if args.cmd == "handover":
        p = handover(Path.cwd() if (Path.cwd() / "MyTradingSys").is_dir() else REPO, args.login, note=args.note, send=not args.no_send)
        print(f"wrote {p}; ship it once (sync.py ship, docs only)")
        return 0
    if args.cmd == "tick":
        sha_list = parse_shas_arg(args.shas)
        res = tick(repo=REPO, shas=sha_list, no_fetch=args.no_fetch, login=args.login)
        print(json.dumps(res, indent=2, sort_keys=True))
        return 0
    if args.cmd == "wait":
        rc, reason = wait_for_transition(
            repo=REPO,
            shas=args.shas,
            timeout=args.timeout,
            interval=args.interval,
            login=(args.login or "").strip().upper()[:1] or None,
        )
        print(reason)
        return rc
    if args.cmd == "brief":
        out = brief(args.card, role=args.role, repo=REPO)
        print(out)
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
