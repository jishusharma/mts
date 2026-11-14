"""Step A: write trades.csv (one row per trade) per PRE_REG.md. Prints counts only, no outcome statistics."""
import csv
import datetime as dt
import os
import sys
from collections import Counter

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib  # noqa: E402

CACHE = "F:/MTS/data_cache"
CORE = "ADA ALGO ATOM AVAX BCH BNB BTC DOGE DOT ETC ETH FIL LINK LTC NEAR SOL TRX UNI XLM XRP".split()
FRESH = "AAVE ENJ GRT HBAR MANA SAND THETA XTZ".split()
VAL_START_MS = int(dt.datetime(2024, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
MIN5 = 300_000
MIN15 = 900_000


def load_raw(path):
    z = np.load(path)
    if "a" in z.files:
        a = z["a"]
        return a[:, 0].astype(np.int64), a[:, 1], a[:, 2], a[:, 3], a[:, 4], a[:, 5]
    tk = "t" if "t" in z.files else "ts"
    return (z[tk].astype(np.int64), z["o"], z["h"], z["l"], z["c"], z["v"])


def check_layout(raw, base_ms, label):
    t = raw[0]
    assert 1.4e12 < t[0] < 2.0e12 and t[-1] < 2.0e12, f"{label}: timestamps not ms"
    assert int(np.median(np.diff(t))) == base_ms, f"{label}: base interval {np.median(np.diff(t))} != {base_ms}"
    assert (raw[2] >= raw[3]).mean() > 0.999, f"{label}: high<low column order"


def load_hourly(coin, group):
    if group == "core":
        raw = load_raw(f"{CACHE}/binance_spot/{coin}USDT_15m.npz")
        base = MIN15
    else:
        raw = load_raw(f"{CACHE}/binance_fresh/nk5_nyasia/{coin}USDT_5m.npz")
        base = MIN5
    check_layout(raw, base, coin)
    t, o, h, l, c, v = lib.aggregate(*raw, base, lib.HOUR_MS)
    return lib.to_grid(t, o, h, l, c, v, lib.HOUR_MS)


def load_btc_4h():
    raw = load_raw(f"{CACHE}/binance_spot/BTCUSDT_15m.npz")
    check_layout(raw, MIN15, "BTC4h")
    t, o, h, l, c, v = lib.aggregate(*raw, MIN15, lib.H4_MS)
    g = lib.to_grid(t, o, h, l, c, v, lib.H4_MS)
    rsi = lib.wilder_rsi(g["c"], 14)
    starts = g["t0"] + np.arange(g["n"], dtype=np.int64) * lib.H4_MS
    return starts, rsi


def load_phase():
    days, cyc, lab = [], [], []
    with open(f"{CACHE}/mts_brains/phase_daily.csv", newline="") as f:
        for r in csv.DictReader(f):
            d = dt.datetime.strptime(r["date"], "%Y-%m-%d").replace(tzinfo=dt.timezone.utc)
            days.append(int(d.timestamp() * 1000))
            cyc.append(r["cycle"])
            lab.append(r["label"] or "NA")
    return np.array(days, dtype=np.int64), np.array(cyc), np.array(lab)


def iso(ms):
    return dt.datetime.fromtimestamp(ms / 1000, tz=dt.timezone.utc).strftime("%Y-%m-%d %H:%M")


COLS = ["coin", "group", "trap_time", "signal_time", "entry_time", "entry", "stop", "D", "trap_low", "exit_time",
        "exit_price", "exit_reason", "R_gross", "R_net12", "R_net6", "cycle", "phase_label", "split", "btc_rsi4h",
        "episode", "episode_cycle", "trap_ms", "signal_ms", "entry_ms", "exit_ms", "entry_idx", "exit_idx"]


def main():
    h4_starts, h4_rsi = load_btc_4h()
    pdays, pcyc, plab = load_phase()
    rows = []
    skip_tot = Counter()
    notes = Counter()
    for group, coins in (("core", CORE), ("fresh", FRESH)):
        for coin in coins:
            g = load_hourly(coin, group)
            hours = g["t0"] + np.arange(g["n"], dtype=np.int64) * lib.HOUR_MS
            gate = lib.gate_series(hours, h4_starts, h4_rsi)
            trades, skips = lib.scan_coin(g, gate)
            skip_tot.update(skips)
            print(f"{coin:6s} {group:5s} bars={int(np.sum(~np.isnan(g['c'])))} grid={g['n']} trades={len(trades)} skips={skips}")
            for t in trades:
                trap_ms = int(hours[t["trap_idx"]])
                cy = lib.lookup_day(pdays, pcyc, trap_ms)
                lb = lib.lookup_day(pdays, plab, trap_ms)
                if cy is None:
                    notes["no_phase_row"] += 1
                    cy, lb = "NA", "NA"
                r, rn12 = lib.fee_net_r(t["entry"], t["exit_price"], t["D"], lib.FEE_RT_12)
                _, rn6 = lib.fee_net_r(t["entry"], t["exit_price"], t["D"], lib.FEE_RT_6)
                rows.append({
                    "coin": coin, "group": group, "trap_time": iso(trap_ms),
                    "signal_time": iso(int(hours[t["signal_idx"]])), "entry_time": iso(int(hours[t["entry_idx"]])),
                    "entry": t["entry"], "stop": t["stop"], "D": t["D"], "trap_low": t["trap_low"],
                    "exit_time": iso(int(hours[t["exit_idx"]])), "exit_price": t["exit_price"],
                    "exit_reason": t["exit_reason"], "R_gross": r, "R_net12": rn12, "R_net6": rn6,
                    "cycle": cy, "phase_label": lb, "split": "DEV" if trap_ms < VAL_START_MS else "VAL",
                    "btc_rsi4h": t["btc_rsi4h"], "trap_ms": trap_ms, "signal_ms": int(hours[t["signal_idx"]]),
                    "entry_ms": int(hours[t["entry_idx"]]), "exit_ms": int(hours[t["exit_idx"]]),
                    "entry_idx": t["entry_idx"], "exit_idx": t["exit_idx"],
                })
    rows.sort(key=lambda r: (r["signal_ms"], r["coin"]))
    ids = lib.assign_episodes([r["signal_ms"] for r in rows])
    first_cycle = {}
    for r, e in zip(rows, ids):
        r["episode"] = int(e)
        first_cycle.setdefault(int(e), r["cycle"])
    for r in rows:
        r["episode_cycle"] = first_cycle[r["episode"]]
    with open(os.path.join(HERE, "trades.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)

    print("\nTOTAL trades", len(rows), "episodes", len(first_cycle))
    print("skips", dict(skip_tot), "notes", dict(notes))
    print("by cycle", dict(Counter(r["cycle"] for r in rows)))
    print("by split", dict(Counter(r["split"] for r in rows)))
    print("by group", dict(Counter(r["group"] for r in rows)))
    print("by cycle x split x group")
    for k, v in sorted(Counter((r["cycle"], r["split"], r["group"]) for r in rows).items()):
        print("  ", k, v)
    print("by coin", dict(sorted(Counter(r["coin"] for r in rows).items())))
    print("episodes by episode_cycle", dict(Counter(first_cycle.values())))
    print("exit reasons", dict(Counter(r["exit_reason"] for r in rows)))


if __name__ == "__main__":
    main()
