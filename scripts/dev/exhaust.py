"""Exhaust phase (MyTradingSys/system/EXHAUST_PHASE.md): spend the paid quota in the last 2 hours before the weekly reset.

  python scripts/dev/exhaust.py plan --login C --week 99 --five 13 --reset 2026-10-23T09:00Z --read 2026-10-23T07:02Z [--model opus=10 ...]

Prints the phase (none | plan | exhaust | done), minutes to reset and the models to spend, most headroom first.
Reads numbers passed in (from get_usage); no scheduler, no network, changes nothing.
B199 (BUGS.md): a quota number names its source and read time. --read is the UTC time of the get_usage call; the JSON
echoes it as read_utc with source=get_usage. A reading older than READ_MAX_MIN, or from the future, exits 2 (no phase JSON);
without --read the JSON says read_utc=unstated, source=unstated.
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

PLAN_MIN = 120     # OURS (operator 2026-10-23: "within 2 hours of the reset")
EXHAUST_MIN = 60   # OURS (operator 2026-10-23: "around 1 hour")
READ_MAX_MIN = 10  # OURS (B199: a quota reading older than this is re-read with get_usage, not trusted)
READ_SKEW_MIN = 2  # OURS (clock skew between the reader and this host that is still accepted)
STALE_H = 6.0      # OURS: BUDGET signal reading older than 6h is flagged stale_reading=True
THRESHOLDS_H = ((2.0, "T-2"), (24.0, "T-24"), (48.0, "T-48"))
MIN_DRAIN_LEFT_PCT = 5.0
STATE_DIR_DEFAULT = Path(os.environ.get("MTS_RADAR_STATE_DIR") or (Path.home() / ".claude" / "mts-loop" / "radar"))
_WK_RE = re.compile(r"(?:wk|week)=(\d+(?:\.\d+)?)%(?:@|\s+reset=)([0-9T:\-\.+Z]+)")
_LOGIN_TXT_RE = re.compile(r"login=([ABC])\b")


def _parse_any_utc(text: str) -> datetime:
    s = text.strip()
    if re.fullmatch(r"\d{8}T\d{6}Z", s):
        return datetime.strptime(s, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    return parse_utc(s)


def roll_weekly_reset(reset_dt: datetime, now: datetime) -> tuple[datetime, int]:
    """Advance a past weekly reset timestamp in 7-day increments until strictly > now."""
    cur = reset_dt if reset_dt.tzinfo else reset_dt.replace(tzinfo=timezone.utc)
    now_u = now if now.tzinfo else now.replace(tzinfo=timezone.utc)
    steps = 0
    while cur <= now_u:
        cur += timedelta(days=7)
        steps += 1
    return cur, steps


def _threshold_for(hours_to_reset: float, week_left_pct: float) -> str | None:
    if week_left_pct <= MIN_DRAIN_LEFT_PCT or hours_to_reset <= 0:
        return None
    for limit_h, label in THRESHOLDS_H:
        if hours_to_reset <= limit_h:
            return label
    return None


def radar(rows: list[dict], now: datetime | None = None) -> dict[str, Any]:
    """Compute 48h/24h/2h weekly-reset radar across logins A, B, C from signal rows."""
    now = now or datetime.now(timezone.utc)
    now_u = now if now.tzinfo else now.replace(tzinfo=timezone.utc)
    latest_by_login: dict[str, dict[str, Any]] = {}
    for r in rows:
        txt = str(r.get("text") or "")
        if "BUDGET" not in txt:
            continue
        lane = str(r.get("lane") or r.get("login") or "").strip().upper()
        if lane.startswith("SUPERVISOR_"):
            lane = lane.split("_", 1)[1]
        if lane not in {"A", "B", "C"}:
            lm = _LOGIN_TXT_RE.search(txt)
            lane = lm.group(1) if lm else ""
        if lane not in {"A", "B", "C"}:
            continue
        m = _WK_RE.search(txt)
        if not m:
            continue
        ts_raw = str(r.get("ts") or r.get("t") or "")
        try:
            ts_dt = _parse_any_utc(ts_raw) if ts_raw else now_u
        except ValueError:
            ts_dt = now_u
        prev = latest_by_login.get(lane)
        if prev is None or ts_dt >= prev["ts_dt"]:
            latest_by_login[lane] = {
                "row": r,
                "ts_dt": ts_dt,
                "wk_used": float(m.group(1)),
                "wk_reset_raw": m.group(2),
            }

    out_logins: list[dict[str, Any]] = []
    alerts: list[dict[str, Any]] = []
    for login in ("A", "B", "C"):
        info = latest_by_login.get(login)
        if not info:
            out_logins.append({"login": login, "status": "missing", "threshold": None, "week_left_pct": None, "rolled_weeks": 0, "stale_reading": True})
            continue
        used = info["wk_used"]
        left = round(max(0.0, 100.0 - used), 1)
        try:
            reset_dt = parse_utc(info["wk_reset_raw"])
        except ValueError:
            out_logins.append({"login": login, "status": "bad_reset", "threshold": None, "week_left_pct": left, "rolled_weeks": 0, "stale_reading": True})
            continue
        rolled_dt, rolled_weeks = roll_weekly_reset(reset_dt, now_u)
        hrs = round((rolled_dt - now_u).total_seconds() / 3600.0, 2)
        age_h = round((now_u - info["ts_dt"]).total_seconds() / 3600.0, 2)
        stale_reading = age_h > STALE_H
        thresh = _threshold_for(hrs, left)
        rec = {
            "login": login,
            "status": "ok",
            "week_used_pct": used,
            "week_left_pct": left,
            "effective_reset": fmt_utc(rolled_dt),
            "hours_to_reset": hrs,
            "rolled_weeks": rolled_weeks,
            "age_hours": age_h,
            "stale_reading": stale_reading,
            "threshold": thresh,
        }
        out_logins.append(rec)
        if thresh:
            alerts.append(rec)
    return {"as_of": fmt_utc(now_u), "logins": out_logins, "alerts": alerts}


def _fitting_ready_cards(repo: Path | None, limit: int = 3) -> list[str]:
    root = repo or Path(__file__).resolve().parents[2]
    tasks_dir = root / "MyTradingSys" / "system" / "tasks"
    if not tasks_dir.is_dir():
        return []
    cards: list[tuple[int, str, str]] = []
    for p in sorted(tasks_dir.glob("*.json")):
        try:
            c = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if str(c.get("state") or "").lower() != "ready":
            continue
        est = int(c.get("est_turns") or 6)
        prio = str(c.get("priority") or "P2")
        cid = str(c.get("id") or p.stem)
        cards.append((est, prio, f"{cid}({est}t)"))
    cards.sort(key=lambda x: (x[1], x[0], x[2]))
    return [x[2] for x in cards[:limit]]


def radar_banner(
    rows: list[dict],
    *,
    now: datetime | None = None,
    state_dir: Path | None = None,
    repo: Path | None = None,
) -> str:
    """Return one-line RESET T-48/T-24/T-2 banners for any unannounced login thresholds."""
    now = now or datetime.now(timezone.utc)
    rep = radar(rows, now=now)
    alerts = rep.get("alerts") or []
    if not alerts:
        return ""
    sdir = Path(state_dir) if state_dir else STATE_DIR_DEFAULT
    seen_file = sdir / "seen_thresholds.json"
    seen: dict[str, str] = {}
    if seen_file.is_file():
        try:
            seen = json.loads(seen_file.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            seen = {}
    picks = _fitting_ready_cards(repo)
    pick_sfx = f" | drain with: {', '.join(picks)}" if picks else ""
    lines: list[str] = []
    rank = {"T-48": 1, "T-24": 2, "T-2": 3}
    changed = False
    for a in alerts:
        login = a["login"]
        eff_reset = a["effective_reset"]
        thresh = a["threshold"]
        key = f"{login}:{eff_reset}"
        prev = seen.get(key)
        if prev and rank.get(prev, 0) >= rank.get(thresh, 0):
            continue
        seen[key] = thresh
        changed = True
        stale_tag = " [STALE-READING]" if a.get("stale_reading") else ""
        lines.append(
            f"RESET {thresh} login={login}: {a['week_left_pct']}% left "
            f"(reset {eff_reset} in {a['hours_to_reset']}h){stale_tag}{pick_sfx}"
        )
    if changed:
        try:
            sdir.mkdir(parents=True, exist_ok=True)
            seen_file.write_text(json.dumps(seen, indent=2), encoding="utf-8")
        except OSError:
            pass
    return "\n".join(lines)


def parse_utc(text: str) -> datetime:
    """UTC time from 2026-10-23T09:00Z style text; a time without a zone is taken as UTC."""
    t = datetime.fromisoformat(text.strip().replace("Z", "+00:00"))
    return t if t.tzinfo else t.replace(tzinfo=timezone.utc)


def fmt_utc(t: datetime) -> str:
    t = t.astimezone(timezone.utc)
    return t.strftime("%Y-%m-%dT%H:%MZ" if t.second == 0 else "%Y-%m-%dT%H:%M:%SZ")


def check_read(read: datetime, now: datetime) -> float:
    """Age of the quota reading in minutes (negative = read time is ahead of this clock)."""
    return (now - read).total_seconds() / 60


def plan(login: str, week: float, five: float, reset: datetime, models: dict, now: datetime | None = None,
         read_utc: str = "unstated", source: str = "unstated") -> dict:
    now = now or datetime.now(timezone.utc)
    minutes = int((reset - now).total_seconds() // 60)
    if minutes <= 0 or week >= 100:
        phase = "done"
    elif minutes <= EXHAUST_MIN:
        phase = "exhaust"
    elif minutes <= PLAN_MIN:
        phase = "plan"
    else:
        phase = "none"
    order = sorted((m for m, used in models.items() if used < 100), key=lambda m: models[m])
    import traffic     # the one 5 h stop (SUPER_SESSION.md "Budget policy"): 95 inside the exhaust window, else 80
    return {"login": login, "phase": phase, "minutes_to_reset": minutes, "week": week, "five": five, "models": order,
            "five_stop": traffic.five_ceiling(minutes / 60),
            "read_utc": read_utc, "source": source}


def holder(login: str, claims) -> str:
    """Who holds the exhaust claim of `login` ('' = free): one actor per login, others carry on with their own task."""
    slug = f"exhaust-login-{login.lower()}"
    for s, kv in claims:
        if s == slug:
            return kv.get("host") or kv.get("who") or "unknown"
    return ""


def start(login: str) -> int:
    import sync
    repo = Path(__file__).resolve().parents[2]
    held = holder(login, sync.open_claims(repo))
    if held:
        print(f"HELD by {held}: do not act; ack told and carry on")
        return 3
    sync.claim(repo, f"exhaust-login-{login.lower()}")
    print(f"CLAIMED exhaust-login-{login.lower()}")
    return 0


def main(argv=None, now: datetime | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["plan", "start", "radar"])
    ap.add_argument("--login", required=False, default="A", choices=["A", "B", "C"])
    ap.add_argument("--week", type=float, default=0)
    ap.add_argument("--five", type=float, default=0)
    ap.add_argument("--reset", default="", help="UTC, e.g. 2026-10-23T09:00Z")
    ap.add_argument("--read", default="", help="UTC time of the get_usage call the numbers come from; older than %d min is refused" % READ_MAX_MIN)
    ap.add_argument("--model", action="append", default=[], help="name=percent used")
    ap.add_argument("--json", action="store_true", help="Emit JSON for radar")
    a = ap.parse_args(argv)
    if a.cmd == "radar":
        import mts_signal
        h = mts_signal.ensure()
        rows = mts_signal.load(h) if h else []
        rep = radar(rows, now=now)
        if a.json:
            print(json.dumps(rep, indent=2))
        else:
            for r in rep["logins"]:
                print(
                    f"{r['login']} status={r['status']} left={r.get('week_left_pct')}% "
                    f"reset={r.get('effective_reset')} in={r.get('hours_to_reset')}h "
                    f"threshold={r.get('threshold')} stale_reading={r.get('stale_reading')}"
                )
        return 0
    if a.cmd == "start":
        return start(a.login)
    now = now or datetime.now(timezone.utc)
    read_utc, source = "unstated", "unstated"
    if a.read:
        try:
            read = parse_utc(a.read)
        except ValueError:
            print(f"BAD --read {a.read!r}: want the UTC time of the get_usage call, e.g. 2026-10-23T07:02Z", file=sys.stderr)
            return 2
        read_utc, source = fmt_utc(read), "get_usage"
        age = check_read(read, now)
        if age > READ_MAX_MIN:
            print(f"STALE quota reading: read {read_utc}, {int(age)} min old, source {source}; re-run get_usage", file=sys.stderr)
            return 2
        if age < -READ_SKEW_MIN:
            print(f"quota reading is in the future: read {read_utc}, {int(-age)} min ahead of this clock, source {source}; re-run get_usage",
                  file=sys.stderr)
            return 2
    reset = datetime.fromisoformat(a.reset.replace("Z", "+00:00"))
    models = {k: float(v) for k, _, v in (s.partition("=") for s in a.model)}
    print(json.dumps(plan(a.login, a.week, a.five, reset, models, now, read_utc, source)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
