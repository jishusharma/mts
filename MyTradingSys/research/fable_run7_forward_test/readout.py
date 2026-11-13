"""Krown S8 forward test, weekly readout (card krown-s8-forward-weekly-readout; FORWARD_PREREG.md s3-s4).

Reads (read-only): execution/auto_trades.jsonl (decisions: trade_attempt, skipped_busy, skipped_floor, ...) and
execution/trade_ledger.jsonl (one fee-net row per closed trade, built from the exchange fills + plan journal).
Scope: source prefix layer:krown:s8_break:4h AND account krown_s8; a Krown-source row on another account is
CONTAMINATED (listed, excluded). Per trade net R = net_pnl_usd / risk USD (forward_readout.row_r: fee- and funding-net).
FAIL-A/B/C and the 90 % bounds come from forward_readout (loaded, not copied) over every in-scope trade whose entry is
before the end of the readout week. PARITY check (OURS, s3 words made exact):
  - replay events = krown_live.s8_events on closed Binance BTCUSDT 4h bars (--replay-json file, or public klines);
  - non_replay: a Krown trade whose (bar-open ms, side) is not a replay event (cumulative): PARITY-FAIL, the trade stays
    in A-C; a stop in the log row that differs by more than 1e-6 relative counts as non_replay too;
  - missed: a replay event whose bar closed inside the week [Mon 00:00, next Mon 00:00 UTC) with no trade_attempt,
    skipped_busy, skipped_floor, skipped_halt or skipped_auto_pause row for its key = PARITY-FAIL (brakes are
    counted as skipped_brake, never a build fault). No replay available = parity "unknown" (not ok, not fail).
Counts: skipped_busy, skipped_floor, same_bar_both (ledger row exiting on both a stop and a target label), CONTAMINATED,
entered_unrecorded (attempt without a ledger row: still open or not yet booked), mean slip bp where the row logs it.
Writes READOUT_<week>.md and replaces/appends the week's FORWARD_LOG.csv row. Exit code 2 on FAIL or PARITY-FAIL.
Never trades, never edits the blocklist (a FAIL needs a coordinator stop card: tasks.py new).

Run: python MyTradingSys/research/fable_run7_forward_test/readout.py --week <Monday YYYY-MM-DD> [--root DIR] [--replay-json F]
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import forward_readout as fr  # noqa: E402

ROOT = fr.ROOT
SOURCE = "layer:krown:s8_break:4h"
ACCOUNT = "krown_s8"
BAR_MS = 4 * 3600 * 1000
COVER = ("trade_attempt", "skipped_busy", "skipped_floor")
BRAKES = ("skipped_halt", "skipped_auto_pause")
PHASE = "post-bottom recovery (cycle low 2026-07-01 57,800; BIBLE.md s3/s5, FORWARD_PREREG context)"
KLINES = "https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=4h&limit=1000"
CSV_COLS = ["week", "asof", "n", "mean_net_r", "se", "lower90", "upper90", "dd_r", "streak", "fail", "parity",
            "missed", "non_replay", "contaminated", "skipped_busy", "skipped_floor", "skipped_brake",
            "same_bar_both", "entered_unrecorded", "mean_slip_bp", "phase"]


def _ms(dt):
    return int(dt.timestamp() * 1000)


def key_ms(key):
    """Bar-open ms from an auto_trades key '<layer>:<sub>:<event>:<tf>:<t_close>', else None."""
    try:
        return int(str(key).rsplit(":", 1)[1])
    except (IndexError, ValueError):
        return None


def _is_krown(src):
    return str(src or "").startswith(SOURCE)


def _iso_dt(s):
    try:
        return fr._ts(s)
    except (TypeError, ValueError):
        return None


def _same_stop(a, b):
    return a is None or b is None or abs(float(a) - float(b)) <= 1e-6 * abs(float(b))


def fetch_replay(week_end):
    """Replay events from public closed 4h klines (network). Returns list of {t, side, stop} or None on any failure."""
    try:
        import urllib.request
        sys.path.insert(0, str(ROOT / "MyTradingSys/backtest/layers/krown"))
        import krown_live as kl
        with urllib.request.urlopen(KLINES, timeout=20) as r:
            raw = json.loads(r.read().decode())
        cut = min(_ms(week_end), _ms(datetime.now(timezone.utc)))
        bars = [{"t": int(k[0]), "o": float(k[1]), "h": float(k[2]), "l": float(k[3]), "c": float(k[4])}
                for k in raw if int(k[0]) + BAR_MS <= cut]
        return [{"t": e["t"], "side": e["side"], "stop": e["stop"]} for e in kl.s8_events(bars)]
    except Exception:  # noqa: BLE001 - parity then reads "unknown", never a guess
        return None


def analyse(auto_rows, ledger_rows, week_start, replay):
    """Pure. week_start: aware UTC Monday datetime. replay: list of {t, side, stop} or None. Returns a result dict."""
    week_end = week_start + timedelta(days=7)
    w0, w1 = _ms(week_start), _ms(week_end)
    contaminated = {}
    trades = []                                   # (entry datetime, net R, plan_id, key, side, stop, row)
    for row in ledger_rows:
        if not _is_krown(row.get("source")):
            continue
        pid = row.get("plan_id")
        if row.get("account") != ACCOUNT:
            contaminated[pid] = {"plan_id": pid, "account": row.get("account"), "from": "ledger"}
            continue
        ts = _iso_dt((row.get("entry") or {}).get("ts") or row.get("ts"))
        r = fr.row_r(row)
        if row.get("unresolved") or r is None or ts is None or ts >= week_end:
            continue
        trades.append((ts, r, pid, row.get("alert_key"), row.get("side"), row.get("stop"), row))
    trades.sort(key=lambda t: t[0])
    attempts, covered, brakes = {}, set(), set()
    busy = floor = 0
    ledger_pids = {t[2] for t in trades}
    unrecorded = []
    for row in auto_rows:
        if not _is_krown(row.get("source")):
            continue
        ev, k = row.get("event"), key_ms(row.get("key"))
        if ev == "trade_attempt":
            if row.get("account") != ACCOUNT:
                contaminated.setdefault(row.get("plan_id"), {"plan_id": row.get("plan_id"),
                                                             "account": row.get("account"), "from": "auto_trades"})
                continue
            if row.get("outcome") == "entered":
                attempts[row.get("plan_id")] = row
                if row.get("plan_id") not in ledger_pids:
                    unrecorded.append(row.get("plan_id"))
        if k is not None and ev in COVER:
            covered.add((k, row.get("side")))
        if k is not None and ev in BRAKES:
            brakes.add((k, row.get("side")))
        if k is not None and w0 <= k + BAR_MS < w1:
            busy += ev == "skipped_busy"
            floor += ev == "skipped_floor"
    # an auto_trades-contaminated plan may also sit in the ledger: drop it from the scored list
    trades = [t for t in trades if t[2] not in contaminated]
    rs = [t[1] for t in trades]
    n = len(rs)
    mean, se = fr.mean_se(rs)
    dd, streak = fr.drawdown_and_streak(rs)
    fail = fr.krown_fail(rs)
    lower = mean - fr.FAIL_C_Z * se if n >= 2 else float("nan")
    upper = mean + fr.FAIL_C_Z * se if n >= 2 else float("nan")
    non_replay, missed = [], []
    if replay is not None:
        rmap = {(e["t"], e["side"]): e.get("stop") for e in replay}
        for ts, r, pid, key, side, stop, row in trades:
            at = attempts.get(pid) or {}
            k = key_ms(key) if key else key_ms(at.get("key"))
            side = side or at.get("side")
            if (k, side) not in rmap or not _same_stop(stop, rmap[(k, side)]):
                non_replay.append(pid)
        for e in replay:
            if w0 <= e["t"] + BAR_MS < w1:
                k = (e["t"], e["side"])
                if k not in covered and k not in brakes:
                    missed.append({"t": e["t"], "side": e["side"]})
    nonrep_set = set(non_replay)
    parity = "unknown" if replay is None else ("fail" if (non_replay or missed) else "ok")
    same_bar = 0
    slips = []
    for t in trades:
        row = t[6]
        labels = [str(x.get("label") or "") for x in row.get("exits") or []]
        if any(lb.endswith(":stop") for lb in labels) and any(not lb.endswith(":stop") for lb in labels):
            same_bar += 1
        if isinstance(row.get("slip_bp"), (int, float)):
            slips.append(float(row["slip_bp"]))
    return {"week": week_start.date().isoformat(), "week_end": week_end.date().isoformat(), "n": n, "mean": mean,
            "se": se, "lower90": lower, "upper90": upper, "dd_r": dd, "streak": streak, "fail": fail,
            "parity": parity, "missed": missed, "non_replay": non_replay, "contaminated": list(contaminated.values()),
            "skipped_busy": busy, "skipped_floor": floor, "skipped_brake": len(brakes), "same_bar_both": same_bar,
            "entered_unrecorded": unrecorded, "mean_slip_bp": sum(slips) / len(slips) if slips else None,
            "trades": [{"entry": t[0].strftime("%Y-%m-%dT%H:%M:%SZ"), "net_r": round(t[1], 4), "plan_id": t[2],
                        "non_replay": t[2] in nonrep_set} for t in trades]}


def _f(x, nd=3):
    return "n/a" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{nd}f}"


def to_markdown(res, phase=PHASE, note=""):
    flags = []
    if res["fail"]:
        flags.append(f"**{res['fail']}**: stop the source (coordinator stop card)")
    if res["parity"] == "fail":
        flags.append("**PARITY-FAIL**: coordinator pauses the source until the parity card fixes it")
    L = [f"# Krown S8 forward readout, week {res['week']} to {res['week_end']} (UTC, end exclusive)", "",
         f"**Result: n {res['n']} trades, mean net R {_f(res['mean'])}, DD {_f(res['dd_r'], 2)} R, streak "
         f"{res['streak']}, parity {res['parity']}" + (f", {res['fail']}" if res["fail"] else "") + "**", ""]
    L += flags + ([""] if flags else [])
    L += ["| measure | value |", "|---|---|", f"| trades (cumulative to week end) | {res['n']} |",
          f"| mean net R | {_f(res['mean'])} |", f"| SE | {_f(res['se'])} |",
          f"| one-sided 90 % lower bound (mean - 1.28 SE) | {_f(res['lower90'])} |",
          f"| FAIL-C upper bound (mean + 1.28 SE) | {_f(res['upper90'])} |",
          f"| drawdown from peak (FAIL-A at 12.00) | {_f(res['dd_r'], 2)} R |",
          f"| longest loser streak (FAIL-B at 12) | {res['streak']} |",
          f"| FAIL rule hit | {res['fail'] or 'none'} |", f"| parity | {res['parity']} |",
          f"| replay events missed this week | {len(res['missed'])} |",
          f"| non_replay trades (kept in A-C) | {len(res['non_replay'])} |",
          f"| CONTAMINATED (other account, excluded) | {len(res['contaminated'])} |",
          f"| skipped_busy (week) | {res['skipped_busy']} |", f"| skipped_floor (week) | {res['skipped_floor']} |",
          f"| skipped by brake (HALT / auto pause) | {res['skipped_brake']} |",
          f"| same_bar_both | {res['same_bar_both']} |",
          f"| entered, no ledger row yet | {len(res['entered_unrecorded'])} |",
          f"| mean slip bp per leg (check column, never an input) | {_f(res['mean_slip_bp'], 2)} |",
          f"| phase tag | {phase} |", ""]
    for m in res["missed"]:
        L.append(f"- missed replay event: bar open {m['t']} {m['side']}")
    for c in res["contaminated"]:
        L.append(f"- CONTAMINATED: plan {c['plan_id']} account {c['account']} ({c['from']})")
    for t in res["trades"]:
        if t["non_replay"]:
            L.append(f"- non_replay: plan {t['plan_id']} entry {t['entry']} net R {t['net_r']}")
    L += [""] + ([note, ""] if note else [])
    L += ["Rules (FORWARD_PREREG s3, all OURS): FAIL-A 12 R drawdown, FAIL-B 12 straight losers, FAIL-C n >= 30 and "
          "mean + 1.28 SE < 0. No PASS exists; numbers only. Fee-net R from real fills, BTC only."]
    return "\n".join(L) + "\n"


def write_log_row(path, res, phase=PHASE):
    fail = res["fail"].replace("FAIL-", "FAIL ") if res["fail"] else "none"
    row = {"week": res["week"], "asof": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "n": res["n"],
           "mean_net_r": _f(res["mean"], 4), "se": _f(res["se"], 4), "lower90": _f(res["lower90"], 4),
           "upper90": _f(res["upper90"], 4), "dd_r": _f(res["dd_r"], 2), "streak": res["streak"],
           "fail": fail, "parity": res["parity"],
           "missed": len(res["missed"]), "non_replay": len(res["non_replay"]),
           "contaminated": len(res["contaminated"]), "skipped_busy": res["skipped_busy"],
           "skipped_floor": res["skipped_floor"], "skipped_brake": res["skipped_brake"],
           "same_bar_both": res["same_bar_both"], "entered_unrecorded": len(res["entered_unrecorded"]),
           "mean_slip_bp": _f(res["mean_slip_bp"], 2), "phase": phase}
    path = Path(path)
    rows = []
    if path.exists():
        with open(path, encoding="utf-8", newline="") as f:
            rows = [r for r in csv.DictReader(f) if r.get("week") != res["week"]]
    rows.append(row)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_COLS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in CSV_COLS})


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--week", required=True, help="Monday of the readout week, YYYY-MM-DD (UTC)")
    ap.add_argument("--root", default=str(ROOT), help="tree holding MyTradingSys/execution (live tree for real data)")
    ap.add_argument("--auto-log")
    ap.add_argument("--ledger")
    ap.add_argument("--replay-json", help="list of {t, side, stop} replay events (default: public Binance klines)")
    ap.add_argument("--outdir", default=str(HERE))
    ap.add_argument("--no-write", action="store_true")
    a = ap.parse_args(argv)
    start = datetime.strptime(a.week, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    if start.weekday() != 0:
        ap.error("--week must be a Monday")
    ex = Path(a.root) / "MyTradingSys/execution"
    auto_p, led_p = Path(a.auto_log or ex / "auto_trades.jsonl"), Path(a.ledger or ex / "trade_ledger.jsonl")
    note = ""
    if not auto_p.exists() or not led_p.exists():
        miss = "auto_trades.jsonl" if not auto_p.exists() else "trade_ledger.jsonl"
        note = (f"Data note: {miss} not found under {ex}; counts for the missing file are n 0, not evidence. "
                "The live tree holds the data.")
    replay = (json.loads(Path(a.replay_json).read_text(encoding="utf-8")) if a.replay_json
              else fetch_replay(start + timedelta(days=7)))
    if replay is None:
        note += " Replay unavailable (klines fetch failed): parity unknown."
    if not auto_p.exists():
        replay = None                           # no decision log to compare with: parity unknown, never a fail
        note += " No decision log: parity unknown."
    res = analyse(fr.read_jsonl(auto_p) if auto_p.exists() else [], fr.read_jsonl(led_p) if led_p.exists() else [],
                  start, replay)
    md = to_markdown(res, note=note.strip())
    if not a.no_write:
        out = Path(a.outdir)
        (out / f"READOUT_{res['week']}.md").write_text(md, encoding="utf-8", newline="\n")
        write_log_row(out / "FORWARD_LOG.csv", res)
    sys.stdout.write(md)
    return 2 if (res["fail"] or res["parity"] == "fail") else 0


if __name__ == "__main__":
    raise SystemExit(main())
