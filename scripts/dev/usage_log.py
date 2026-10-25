"""Per-step usage ledger (MyTradingSys/research/USAGE_PILOT.csv): row, idle, summary.

  python scripts/dev/usage_log.py row --card C --step S --lane L --model M --before "five,week,fable" --after "five,week,fable"
         [--transcript P] [--minutes N] [--source get_usage] [--codex5h N --codexweek N --gemini X] [--csv PATH]
  python scripts/dev/usage_log.py idle --reset <UTC ISO> [--csv PATH]
  python scripts/dev/usage_log.py summary [--csv PATH]

row exits 1 and writes nothing when either usage read is missing. A missing or malformed transcript leaves the token cells
blank (exit 0). Idle thresholds are OURS (usage_metering Pilot design): 5h < 40 %, week under the elapsed share of 7 days,
within 60 minutes before the reset.
"""
import argparse
import csv
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DEFAULT_CSV = os.path.join(ROOT, "MyTradingSys", "research", "USAGE_PILOT.csv")
TASKS_DIR = os.path.join(ROOT, "MyTradingSys", "system", "tasks")
HEADER = ["ts_utc", "lane", "model", "card", "step", "pct5h_before", "pct5h_after", "pctweek_before", "pctweek_after",
          "fable_week_before", "fable_week_after", "tokens_in", "tokens_out", "tokens_cache", "minutes", "source",
          "codex_5h_pct", "codex_week_pct", "gemini"]
IDLE_FIVE_PCT = 40.0     # OURS
IDLE_WINDOW_MIN = 60     # OURS


def _read3(s):
    parts = [p.strip() for p in (s or "").split(",")]
    if len(parts) != 3 or not all(re.fullmatch(r"\d+(\.\d+)?", p) for p in parts):
        return None
    return parts


def parse_transcript(path):
    """(tokens_in, tokens_out, tokens_cache) summed over distinct assistant message ids, or None when unreadable."""
    seen, tin, tout, tcache, found = set(), 0, 0, 0, False
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                m = d.get("message") if isinstance(d, dict) else None
                u = m.get("usage") if isinstance(m, dict) else None
                if not isinstance(u, dict) or d.get("type") != "assistant":
                    continue
                mid = m.get("id")
                if mid is not None:
                    if mid in seen:
                        continue
                    seen.add(mid)
                found = True
                tin += int(u.get("input_tokens") or 0)
                tout += int(u.get("output_tokens") or 0)
                tcache += int(u.get("cache_read_input_tokens") or 0) + int(u.get("cache_creation_input_tokens") or 0)
    except (OSError, ValueError, TypeError):
        return None
    return (tin, tout, tcache) if found else None


def idle_lanes(last_rows, ready_lanes, claimed_lanes, now, reset):
    """Lanes to wake: inside the 60 minutes before the reset, and (5h < 40 % with a ready card) or (week under pace, no claim)."""
    left = reset - now
    if left < timedelta(0) or left > timedelta(minutes=IDLE_WINDOW_MIN):
        return []
    pace = max(0.0, min(100.0, (1 - left / timedelta(days=7)) * 100))
    out = []
    for lane, r in sorted(last_rows.items()):
        try:
            five, week = float(r["pct5h_after"]), float(r["pctweek_after"])
        except (KeyError, ValueError, TypeError):
            continue
        if (five < IDLE_FIVE_PCT and lane in ready_lanes) or (week < pace and lane not in claimed_lanes):
            out.append(lane)
    return out


def summarize(rows, card_kind):
    """{kind: (rows_with_tokens, mean tokens_in+out+cache)}."""
    acc = {}
    for r in rows:
        cells = [r.get("tokens_in", ""), r.get("tokens_out", ""), r.get("tokens_cache", "")]
        if not any(c.strip() for c in cells):
            continue
        tot = sum(int(c) for c in cells if c.strip())
        kind = card_kind.get(r.get("card", ""), "?")
        n, s = acc.get(kind, (0, 0))
        acc[kind] = (n + 1, s + tot)
    return {k: (n, s / n) for k, (n, s) in acc.items()}


def _cards():
    for fn in sorted(os.listdir(TASKS_DIR)) if os.path.isdir(TASKS_DIR) else []:
        if fn.endswith(".json"):
            try:
                with open(os.path.join(TASKS_DIR, fn), encoding="utf-8") as f:
                    c = json.load(f)
                if isinstance(c, dict):
                    c.setdefault("id", fn[:-5])
                    yield c
            except (OSError, ValueError):
                continue


def _read_rows(path):
    try:
        with open(path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except OSError:
        return []


def cmd_row(a):
    before, after = _read3(a.before), _read3(a.after)
    if not before or not after:
        print("usage_log row: need both --before and --after as 'five,week,fable' numbers; nothing written", file=sys.stderr)
        return 1
    tok = parse_transcript(a.transcript) if a.transcript else None
    new = not os.path.exists(a.csv) or os.path.getsize(a.csv) == 0
    row = [datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), a.lane, a.model, a.card, a.step,
           before[0], after[0], before[1], after[1], before[2], after[2],
           *(["", "", ""] if tok is None else [str(x) for x in tok]), a.minutes, a.source,
           a.codex5h, a.codexweek, a.gemini]
    with open(a.csv, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        if new:
            w.writerow(HEADER)
        w.writerow(row)
    return 0


def cmd_idle(a):
    last = {}
    for r in _read_rows(a.csv):
        last[r["lane"].lower()] = r
    ready = {str(x).lower() for c in _cards() if c.get("state") == "ready" for x in (c.get("lane"), c.get("worker")) if x}
    claimed = set()
    try:
        out = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "dev", "sync.py"), "claims"], capture_output=True,
                             text=True, timeout=60).stdout.lower()
        claimed = {w for w in last if re.search(r"\b" + re.escape(w) + r"\b", out)}
    except (OSError, subprocess.SubprocessError):
        pass
    reset = datetime.fromisoformat(a.reset.replace("Z", "+00:00"))
    if reset.tzinfo is None:
        reset = reset.replace(tzinfo=timezone.utc)
    lanes = idle_lanes(last, ready, claimed, datetime.now(timezone.utc), reset)
    for ln in lanes:
        print("IDLE " + ln)
    if not lanes:
        print("no idle lane")
    return 0


def cmd_summary(a):
    rows = _read_rows(a.csv)
    kinds = {c["id"]: str(c.get("worker") or c.get("lane") or "?") for c in _cards()}
    print("rows: %d" % len(rows))
    for k, (n, mean) in sorted(summarize(rows, kinds).items()):
        print("%s: %d rows with tokens, mean %.0f" % (k, n, mean))
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("row", "idle", "summary"):
        s = sub.add_parser(name)
        s.add_argument("--csv", default=DEFAULT_CSV)
        if name == "row":
            for k in ("card", "step", "lane", "model"):
                s.add_argument("--" + k, required=True)
            s.add_argument("--before", default="")
            s.add_argument("--after", default="")
            s.add_argument("--transcript")
            s.add_argument("--minutes", default="")
            s.add_argument("--source", default="get_usage")
            s.add_argument("--codex5h", default="")
            s.add_argument("--codexweek", default="")
            s.add_argument("--gemini", default="")
        if name == "idle":
            s.add_argument("--reset", required=True)
    a = p.parse_args(argv)
    return {"row": cmd_row, "idle": cmd_idle, "summary": cmd_summary}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
