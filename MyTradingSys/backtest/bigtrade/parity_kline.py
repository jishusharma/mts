"""
MyTradingSys/backtest/bigtrade/parity_kline.py - PARITY GATE of worker B1.

Replays the kline-only live layers over the newest days of history (fires_kline.replay_range_rows) and compares them
with what the live runner really logged (MyTradingSys/runtime/alerts/<tf>.jsonl): matched / only-live / only-replay
per registry key. A key under 95 % match is NOT trusted.

Two corrections that are not tuning, both printed in the report:
  * UPTIME: the live runner (and the whole testnet system) is sometimes not running (machine off overnight). A replay
    fire that no running poll could have seen is not a parity failure of the code. Dark windows are read from the
    turn_of_candle heartbeat (a fire every 15 minutes, so >= 2 consecutive missing slots = the runner was down) and
    cross-checked against MyTradingSys/execution/auto_trades.jsonl (read only: no events at all in the window).
  * VENUE: the live runner polls SPOT api.binance.com klines, history is USD-M PERP. The gate reports how large the
    venue difference is (logged alert fields vs the same bars on perp) so a miss can be attributed, not guessed.
Read-only on every live file.
"""
import sys
sys.dont_write_bytecode = True

import csv
import datetime as dt
import json
import re
from pathlib import Path

import numpy as np

from MyTradingSys.backtest.bigtrade import fires_kline as fk

TOC_KEY = "turn_of_candle|turn_of_candle|1m"
SLOT_MS = 900000
AUTO_TRADES = fk.REPO / "MyTradingSys" / "execution" / "auto_trades.jsonl"
GATE_PCT = 95.0


def iso(ms):
    return dt.datetime.fromtimestamp(int(ms) / 1000.0, dt.timezone.utc).strftime("%Y-%m-%d %H:%M")


def dark_windows(replay_toc_t_events, live_toc_t_events, min_slots=2):
    """Runs of >= min_slots consecutive turn_of_candle slots (15 min apart) that replay has and live lacks.
    Returns [(first_slot_open_ms, last_slot_open_ms), ...]. A single missing slot is NOT dark (a lost poll)."""
    live = set(live_toc_t_events)
    missing = [t for t in sorted(replay_toc_t_events) if t not in live]
    groups = []
    for t in missing:
        if groups and t - groups[-1][-1] == SLOT_MS:
            groups[-1].append(t)
        else:
            groups.append([t])
    return [(g[0], g[-1]) for g in groups if len(g) >= min_slots]


def in_dark(t_confirm_close_ms, windows):
    """True if the instant falls in a dark window (slot open of the first miss .. close of the last miss, +/- 1 min)."""
    for a, b in windows:
        if a - 60000 <= t_confirm_close_ms <= b + SLOT_MS:
            return True
    return False


def auto_trader_silent_hours(windows, path=AUTO_TRADES):
    """Cross-check: number of auto_trader events whose ts falls inside each dark window (expect 0)."""
    if not Path(path).exists():
        return None
    ts = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                s = json.loads(line).get("ts")
                ts.append(int(dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc).timestamp() * 1000))
            except (ValueError, TypeError):
                continue
    ts.sort()
    out = []
    for a, b in windows:
        lo, hi = a + 15 * 60000, b  # strictly inside the dark span
        out.append(sum(1 for t in ts if lo <= t <= hi))
    return out


def rsi_band_distance(arrays, conf_open_ms, level=40.0, tol=0.5):
    """min over the last 3 closed bars (incl. the confirm bar) of the RSI distance to the nearer band edge, using the
    99-bar window the live runner would see. None if the bar is not found."""
    from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core
    i = int(np.searchsorted(arrays["t"], conf_open_ms))
    if i >= len(arrays["t"]) or arrays["t"][i] != conf_open_ms or i < fk.WINDOW:
        return None
    rs = rsi_core(arrays["c"][i - fk.WINDOW + 1: i + 1].tolist(), 14)
    d = []
    for v in rs[-3:]:
        if v is not None:
            d.append(min(abs(v - (level - tol)), abs(v - (level + tol))))
    return min(d) if d else None


def venue_rsi_diffs(live_rows, tf):
    """|logged live rsi - perp rsi| per alert of one tf that carries rsi and t_confirm (spot vs perp, same formula)."""
    from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core
    a = fk.load_tf(tf)
    out = []
    for r in live_rows:
        raw = r["raw"]
        if raw.get("tf") != tf or raw.get("rsi") is None or raw.get("t_confirm") is None:
            continue
        i = int(np.searchsorted(a["t"], raw["t_confirm"]))
        if i >= len(a["t"]) or a["t"][i] != raw["t_confirm"] or i < fk.WINDOW:
            continue
        rs = rsi_core(a["c"][i - fk.WINDOW + 1: i + 1].tolist(), 14)
        out.append(abs(rs[-1] - raw["rsi"]))
    return out


def toc_side_agreement(replay_rows, live_rows):
    """Side agreement spot (live) vs perp (replay) on matched turn_of_candle fires, by |perp imbalance| bin."""
    liv = {r["t_event"]: r for r in live_rows if r["key"] == TOC_KEY}
    bins = [(0.0, 0.1), (0.1, 0.2), (0.2, 0.3), (0.3, 0.5), (0.5, 1.01)]
    acc = {b: [0, 0] for b in bins}
    tot = [0, 0]
    for r in replay_rows:
        if r["_reg_key"] != TOC_KEY:
            continue
        lv = liv.get(int(r["t_event_ms"]))
        if lv is None:
            continue
        ex = json.loads(r["extra"]) if r["extra"] else {}
        imb = ex.get("imbalance")
        if imb is None:
            continue
        same = 1 if (r["side"] or "") == (lv["side"] or "") else 0
        tot[0] += same
        tot[1] += 1
        for b in bins:
            if b[0] <= abs(imb) < b[1]:
                acc[b][0] += same
                acc[b][1] += 1
    return {"total": tot, "by_abs_imbalance": {"%.1f-%.1f" % b: acc[b] for b in bins}}


def run_parity(t0, t1, label, alerts_dir=None, keys=None):
    rows, errs = fk.replay_range_rows(t0, t1, keys=keys)
    live, dups = fk.load_live_alerts(alerts_dir)
    res = fk.compare(rows, live, t0, t1)
    toc_rep = [int(r["t_event_ms"]) for r in rows if r["_reg_key"] == TOC_KEY]
    toc_live = [r["t_event"] for r in live if r["key"] == TOC_KEY and t0 <= r["t_event"] <= t1]
    dark = dark_windows(toc_rep, toc_live)
    silent = auto_trader_silent_hours(dark)
    rep_by_key = {}
    for r in rows:
        rep_by_key.setdefault(r["_reg_key"], {})[(int(r["t_event_ms"]), r["event"])] = r
    table = {}
    for k, r in res.items():
        if (keys and k not in keys) or k in fk.B2_KEYS:  # B2 keys (order-flow / funding) are not replayed here
            continue
        tf_ms = fk.TF_MS[k.split("|")[2]]
        rep_dark = []
        only_rep_live_up = []
        for kk in r["only_replay"]:
            row = rep_by_key[k][kk]
            if in_dark(int(row["t_confirm_open_ms"]) + tf_ms, dark):
                rep_dark.append(kk)
            else:
                only_rep_live_up.append(kk)
        n_match, n_soft = r["matched"], len(r["soft"])
        n_ol, n_or = len(r["only_live"]), len(only_rep_live_up)
        union_strict = n_match + n_soft * 2 + n_ol + n_or
        union_soft = n_match + n_soft + n_ol + n_or
        table[k] = {
            "replay": r["replay"], "live": r["live"], "matched": n_match, "soft_pairs": n_soft, "only_live": n_ol,
            "only_replay": len(r["only_replay"]), "only_replay_dark": len(rep_dark), "only_replay_up": n_or,
            "side_mismatch": len(r["side_mismatch"]),
            "raw_parity_pct": fk.parity_pct(r),
            "adj_parity_pct": None if union_strict == 0 else 100.0 * n_match / union_strict,
            "adj_parity_soft_pct": None if union_soft == 0 else 100.0 * (n_match + n_soft) / union_soft,
            "diffs": {"only_live": r["only_live"], "only_replay_up": only_rep_live_up, "only_replay_dark": rep_dark,
                      "soft": r["soft"], "side_mismatch": r["side_mismatch"]},
        }
    return {"label": label, "t0": t0, "t1": t1, "window": "%s .. %s" % (iso(t0), iso(t1)), "table": table,
            "dark_windows": [(iso(a), iso(b), (b - a) // SLOT_MS + 1) for a, b in dark],
            "auto_trader_events_in_dark": silent, "live_duplicate_rows_dropped": dups, "replay_errors": errs,
            "rows": rows, "live": live, "res": res}


def explain_rsi(result, key):
    """For the unmatched events of one rsi-family key: share whose RSI path came within the venue noise of a band
    edge (flip-able by spot-vs-perp price noise) vs those that could not flip (would indicate a logic difference)."""
    tf = key.split("|")[2]
    a = fk.load_tf(tf)
    diffs = venue_rsi_diffs(result["live"], tf)
    noise = float(np.max(diffs)) if diffs else None
    tab = result["table"][key]["diffs"]
    rep = {(int(r["t_event_ms"]), r["event"]): r for r in result["rows"] if r["_reg_key"] == key}
    liv = result["res"][key]["liv_s"]
    out = {"venue_rsi_diff_n": len(diffs), "venue_rsi_diff_median": float(np.median(diffs)) if diffs else None,
           "venue_rsi_diff_p90": float(np.percentile(diffs, 90)) if diffs else None, "venue_rsi_diff_max": noise,
           "unmatched": 0, "near_edge": 0, "far_from_edge": []}
    for kk in tab["only_live"] + tab["only_replay_up"]:
        out["unmatched"] += 1
        if kk in rep:
            conf = int(rep[kk]["t_confirm_open_ms"])
        else:
            raw = liv[kk]["raw"]
            conf = raw.get("t_confirm") or kk[0]
        d = rsi_band_distance(a, conf)
        if d is not None and noise is not None and d <= noise:
            out["near_edge"] += 1
        else:
            out["far_from_edge"].append((iso(kk[0]), kk[1], None if d is None else round(d, 3)))
    return out


def write_diffs_csv(path, results):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["window", "key", "kind", "t_event_utc", "t_event_ms", "event", "other_event"])
        for res in results:
            for k, v in res["table"].items():
                d = v["diffs"]
                for kk in d["only_live"]:
                    w.writerow([res["label"], k, "only_live", iso(kk[0]), kk[0], kk[1], ""])
                for kk in d["only_replay_up"]:
                    w.writerow([res["label"], k, "only_replay", iso(kk[0]), kk[0], kk[1], ""])
                for kk in d["only_replay_dark"]:
                    w.writerow([res["label"], k, "only_replay_dark", iso(kk[0]), kk[0], kk[1], ""])
                for a_, b_ in d["soft"]:
                    w.writerow([res["label"], k, "name_differs", iso(a_[0]), a_[0], a_[1], b_[1]])
                for kk in d["side_mismatch"]:
                    w.writerow([res["label"], k, "side_differs", iso(kk[0]), kk[0], kk[1], ""])


def print_table(res):
    print("\n== %s: %s ==" % (res["label"], res["window"]))
    print("dark windows (>=2 missing TOC slots):", res["dark_windows"], "auto_trader events inside:",
          res["auto_trader_events_in_dark"])
    print("%-34s %5s %5s %5s %5s %5s %6s %5s %6s %7s %7s" % (
        "key", "rep", "live", "match", "name~", "onlyL", "onlyR", "dark", "side!", "raw%", "adj%"))
    for k, v in sorted(res["table"].items()):
        f = lambda x: "n/a" if x is None else "%.1f" % x
        print("%-34s %5d %5d %5d %5d %5d %6d %5d %6d %7s %7s" % (
            k, v["replay"], v["live"], v["matched"], v["soft_pairs"], v["only_live"], v["only_replay_up"],
            v["only_replay_dark"], v["side_mismatch"], f(v["raw_parity_pct"]), f(v["adj_parity_pct"])))


def main_parity(args):
    cov = fk.build_cache()
    t1 = cov["last_t"]
    wins = []
    wins.append(("last_%dd" % args.days, t1 - args.days * 86400000 + 60000, t1))
    if args.since_date:
        s = int(dt.datetime.strptime(args.since_date, "%Y-%m-%d").replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
        wins.append(("since_" + args.since_date, s, t1))
    results = []
    for label, a, b in wins:
        res = run_parity(a, b, label)
        print_table(res)
        results.append(res)
    out_dir = Path(args.out) if args.out else fk.FIRES_DIR
    write_diffs_csv(out_dir / "_parity_diffs_B1.csv", results)
    summary = []
    for res in results:
        rsi_explain = {k: explain_rsi(res, k) for k in res["table"]
                       if k.split("|")[1] in ("rsi_events", "malkan_bull", "malkan_bear")}
        toc_side = toc_side_agreement(res["rows"], res["live"])
        s = {k: v for k, v in res.items() if k not in ("rows", "live", "res")}
        s["table"] = {k: {a: b for a, b in v.items() if a != "diffs"} for k, v in res["table"].items()}
        s["rsi_explain"] = rsi_explain
        s["toc_side"] = toc_side
        summary.append(s)
    with open(out_dir / "_parity_B1.json", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(summary, fh, indent=1, sort_keys=True, default=str)
    print("wrote", out_dir / "_parity_B1.json", out_dir / "_parity_diffs_B1.csv")
    return 0
