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
import os
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
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


def _dispatch_raw(repo: Path, as_of: datetime, host: str | None = None) -> dict:
    import tasks
    import lane_health
    cards = tasks.load_all(repo)
    reg = tasks.registry(repo)
    holds = tasks.active_holds(repo)
    claims = tasks.open_claims(repo)
    lane_st = lane_health.load(repo)
    return tasks.dispatch(cards, reg, holds, claims, lane_st, as_of, host or socket.gethostname(), repo)


def read_dispatch(repo: Path = REPO, as_of: datetime | None = None, host: str | None = None) -> dict:
    try:
        as_of = as_of or _now_utc()
        try:
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


def tick(
    repo: Path = REPO,
    shas: list[str] | None = None,
    no_fetch: bool = False,
    as_of: datetime | None = None,
    home: Path | None = None,
) -> dict:
    as_of = as_of or _now_utc()
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
        "dispatch": read_dispatch(repo, as_of=as_of),
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
    return {"shas": sha_on_trunk, "ci_red": ci_red, "busy_slots": busy_slots}


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
) -> tuple[int, str]:
    """Record baseline at start and poll every `interval` seconds after fetching.
    Exits (0, reason) on the FIRST transition from baseline; never exits on a state that already held at baseline;
    exits (3, reason) when `timeout` seconds elapse with no transition.
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
        if reason:
            return 0, reason

    return 3, f"TIMEOUT after {timeout_s}s with no transition"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_tick = sub.add_parser("tick", help="one read-only supervisor status snapshot per wake")
    p_tick.add_argument("--json", action="store_true", help="output JSON (default format)")
    p_tick.add_argument("--shas", nargs="*", default=[], help="comma- or space-separated commit shas to check on trunk/green")
    p_tick.add_argument("--no-fetch", action="store_true", help="skip git fetch origin before reading refs")

    p_wait = sub.add_parser("wait", help="background watcher: exits 0 on first transition from baseline, 3 on timeout")
    p_wait.add_argument("--shas", nargs="*", default=[], help="comma- or space-separated commit shas to watch for landing on trunk")
    p_wait.add_argument("--timeout", default="3000", help="timeout in seconds or with s/m/h suffix (default 3000)")
    p_wait.add_argument("--interval", default="300", help="poll interval in seconds or with s/m/h suffix (default 300)")

    args = ap.parse_args(argv)
    if args.cmd == "tick":
        sha_list = parse_shas_arg(args.shas)
        res = tick(repo=REPO, shas=sha_list, no_fetch=args.no_fetch)
        print(json.dumps(res, indent=2, sort_keys=True))
        return 0
    if args.cmd == "wait":
        rc, reason = wait_for_transition(
            repo=REPO,
            shas=args.shas,
            timeout=args.timeout,
            interval=args.interval,
        )
        print(reason)
        return rc
    return 2


if __name__ == "__main__":
    sys.exit(main())
