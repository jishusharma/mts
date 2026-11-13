"""routines_due.py: which regular routines (MyTradingSys/system/ROUTINES.md) are due now, as `supervisor.py plan` lines.

One table (ROUTINES) of id, ROUTINES.md row, model, due test. `lines()` returns (runs, notes): a `RUN <cmd>` line per
due routine, a `NOTE` line for state that needs no command. No network, no subprocess over 2 s, no routine is run here.
A due test that raises is NOT due and prints one NOTE (fail closed). Daily routines with no output file of their own keep a
marker `<loop_home>/routines/<id>.done` (UTC date), written by the RUN line's tail: `supervisor.py routine-done <id>`.
No scheduler: the only trigger is the coordinator reading the plan (SCHEDULING_POLICY.md).
"""
from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path

BEHIND_LIMIT = 50                 # row 20: commits the main checkout may trail origin/fast-track before the NOTE
GIT_TIMEOUT_S = 2
US_PHASES = {"P1": (9, 0), "P2": (13, 15), "P3": (14, 45), "P4": (21, 15)}   # same as us_prep.PHASE_UTC
US_WINDOW_MIN = 90                # a phase is due from its start for this long, then it is missed (the brief is about that moment)
LEARNER_AFTER_UTC = 21
_NOWIN = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def day(now: datetime) -> str:
    return now.astimezone(timezone.utc).strftime("%Y-%m-%d")


def marker(home: Path, rid: str) -> Path:
    return Path(home) / "routines" / f"{rid}.done"


def marked_today(home: Path, rid: str, now: datetime) -> bool:
    try:
        return marker(home, rid).read_text(encoding="utf-8").strip() == day(now)
    except OSError:
        return False


def write_marker(home: Path, rid: str, now: datetime) -> Path:
    p = marker(home, rid)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(day(now), encoding="utf-8", newline="\n")
    return p


def _git(repo: Path, *args) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=GIT_TIMEOUT_S, creationflags=_NOWIN)
    if r.returncode != 0:
        raise RuntimeError(f"git {args[0]} rc {r.returncode}")
    return r.stdout.strip()


def main_checkout(repo: Path) -> Path:
    out = _git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir").splitlines()
    if not out:
        raise RuntimeError("no git common dir")
    return Path(out[-1]).parent


# ---- due tests: (repo, home, now) -> command to RUN (str), a NOTE (("note", text)), or None (not due) ----------------------
def due_daily(rid: str, cmd: str):
    def f(repo, home, now):
        return None if marked_today(home, rid, now) else f"{cmd}; python scripts/dev/supervisor.py routine-done {rid}"
    return f


def due_learner(repo, home, now):
    d = day(now)
    if now.astimezone(timezone.utc).hour < LEARNER_AFTER_UTC:
        return None
    if (Path(repo) / "MyTradingSys" / "research" / "live_aid_learning" / f"{d}.md").exists():
        return None
    return f"python scripts/dev/live_aid_learn.py --date {d} --log runtime_data/live_aid/flag_log_*.csv --klines auto"


def due_us_prep(repo, home, now):
    n = now.astimezone(timezone.utc)
    if n.weekday() > 4:
        return None
    mins = n.hour * 60 + n.minute
    for ph, (h, m) in US_PHASES.items():
        if 0 <= mins - (h * 60 + m) < US_WINDOW_MIN and \
                not (Path(repo) / "MyTradingSys" / "runtime" / "us_prep" / f"{day(now)}_{ph}.md").exists():
            return f"python scripts/dev/us_prep.py --phase {ph}"
    return None


def due_main_refresh(repo, home, now):
    main = main_checkout(repo)
    behind = int(_git(main, "rev-list", "--count", "HEAD..origin/fast-track").splitlines()[-1])
    if behind <= BEHIND_LIMIT:
        return None
    # refresh_main_checkout.py --apply stashes and merges in the checkout other sessions use: coordinator's call, so a NOTE
    return ("note", f"main checkout {main} is {behind} commits behind (limit {BEHIND_LIMIT}); when no session uses it: "
                    "python scripts/dev/refresh_main_checkout.py (dry run), then --apply")


def due_shots(repo, home, now):
    import shot
    n = len(shot.status_line(shot.fold(shot.load_events(shot.store_dir())))[1])
    if not n:
        return None
    if n >= SHOT_SWEEP_AT:   # a NOTE had no reader (450 overdue on 11-13): a RUN line puts the sweep on a worker
        return (f"python scripts/dev/shot.py list --status pending   # sweep {n} overdue screenshot(s): per id classify, "
                f"read --extract <file>, done --outcome <text>; stop when `shot.py status` shows overdue under {SHOT_SWEEP_AT}")
    return ("note", f"{n} screenshot(s) overdue (>24h): `python scripts/dev/shot.py status` lists them; Haiku classifies and closes")


SHOT_SWEEP_AT = 20   # OURS (card routine-shot-overdue-no-reader-1113): at 20+ overdue the plan prints a RUN sweep line


# id, ROUTINES.md row, cheapest model, due test
ROUTINES = [
    ("hygiene", 5, "T0 script, background (minutes)", due_daily("hygiene", "python scripts/dev/daily_hygiene.py")),
    ("shots_overdue", 9, "Haiku", due_shots),
    ("live_aid_learn", 7, "Sonnet", due_learner),
    ("scenario_score", 10, "Haiku", due_daily("scenario_score", "python MyTradingSys/research/eagle_eyes_picture_2026-10-28/scenario_ledger.py score")),
    ("tasks_stale", 12, "T0 script", due_daily("tasks_stale", "python scripts/dev/tasks.py stale")),
    ("us_prep", 17, "Sonnet", due_us_prep),
    ("main_refresh", 20, "T0 script", due_main_refresh),
]


def lines(repo: Path, home: Path, now: datetime, table=None) -> tuple[list, list]:
    """-> (RUN lines, NOTE lines). Never raises."""
    runs, notes = [], []
    for rid, row, model, test in (ROUTINES if table is None else table):
        try:
            r = test(Path(repo), Path(home), now)
        except Exception as e:   # fail closed: not due, say why once
            notes.append(f"NOTE routine {rid} (ROUTINES row {row}) due-check failed ({type(e).__name__}: {str(e)[:60]}): not run this wake")
            continue
        if r is None:
            continue
        if isinstance(r, tuple):
            notes.append(f"NOTE routine {rid} (row {row}): {r[1]}")
        else:
            runs.append(f"RUN {r}   (routine {rid}, ROUTINES row {row}; cheapest: {model})")
    return runs, notes
