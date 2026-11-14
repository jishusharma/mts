"""T5 step A: read the wave2 cache, build the event list for the fresh universe, write trades.csv and coverage.json.
Prints COUNTS only. No pooled statistic of any return is computed here (step C is t5_stats.py).

    python t5_trades.py [--cache F:/MTS/data_cache/binance/wave2-1114] [--out <folder>]
"""
import argparse
import csv
import datetime as dt
import json
import os
import sys
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import t5_core as T  # noqa: E402

CACHE = "F:/MTS/data_cache/binance/wave2-1114"
PHASE_CSV = "F:/MTS/data_cache/mts_brains/phase_daily.csv"
CANDIDATES = ("NEAR FIL ALGO MATIC SAND MANA AXS THETA EOS XTZ IOTA ONT QTUM ZIL ENJ BAT CHZ ICX WAVES KNC OMG RVN HBAR EGLD FTM "
              "GRT AAVE COMP SNX MKR CRV YFI SUSHI 1INCH RUNE KAVA ZRX IOST ONE CELR ANKR STORJ BAND LUNA FTT XMR DASH OCEAN").split()
SOURCE22_OVERLAP = ("NEAR", "FIL", "ALGO")
FRESH = [s for s in CANDIDATES if s not in SOURCE22_OVERLAP]
MIN_DAILY = 350

COLUMNS = ["coin", "sig_ts", "sig_utc", "entry_ts", "entry_utc", "entry_px", "stop0", "r", "exit_ts", "exit_utc", "exit_px",
           "exit_reason", "bars_held", "gross", "cost12", "cost6", "funding", "fund_covered", "fund_gap",
           "net12_nofund", "net12_fund", "net6_nofund", "net6_fund",
           "R12_nofund", "R12_fund", "R6_nofund", "R6_fund",
           "split", "recent", "bear", "t1_label", "btc_label", "btc_cycle", "iso_week", "year"]


def lower_priority():
    try:
        import psutil
        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    except Exception:
        pass


def load_klines(path):
    a = np.loadtxt(path, delimiter=",", skiprows=1, usecols=range(5), ndmin=2)
    return a[:-1]          # the last (possibly partial) bar of each series is dropped (PRE_REG)


def load_funding(path):
    if not os.path.isfile(path):
        return None
    a = np.loadtxt(path, delimiter=",", skiprows=1, ndmin=2)
    if a.size == 0:
        return []
    a = a[np.argsort(a[:, 0], kind="stable")]
    return [(int(s), float(r)) for s, r in a]


def load_btc_phase(path):
    out = {}
    if not os.path.isfile(path):
        return out
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            out[row["date"]] = (row.get("label") or "", row.get("cycle") or "")
    return out


def utc(ts_ms):
    return dt.datetime.fromtimestamp(ts_ms / 1000.0, dt.timezone.utc).strftime("%Y-%m-%d %H:%M")


def trade_row(ev, btc):
    day = utc(ev["sig_ts"])[:10]
    lab, cyc = btc.get(day, ("", ""))
    nf12, nf6 = ev["gross"] - T.RT_COST, ev["gross"] - T.RT_COST_HALF
    r = ev["r"]
    return dict(coin=ev["coin"], sig_ts=ev["sig_ts"], sig_utc=utc(ev["sig_ts"]), entry_ts=ev["entry_ts"], entry_utc=utc(ev["entry_ts"]),
                entry_px=repr(ev["entry"]), stop0=repr(ev["stop0"]), r=repr(r), exit_ts=ev["exit_ts"], exit_utc=utc(ev["exit_ts"]),
                exit_px=repr(ev["px"]), exit_reason=ev["reason"], bars_held=ev["bars_held"], gross=repr(ev["gross"]),
                cost12=repr(T.RT_COST), cost6=repr(T.RT_COST_HALF), funding=repr(ev["fund"]), fund_covered=int(ev["covered"]),
                fund_gap=int(ev["fund_gap"]), net12_nofund=repr(nf12), net12_fund=repr(nf12 + ev["fund"]),
                net6_nofund=repr(nf6), net6_fund=repr(nf6 + ev["fund"]),
                R12_nofund=repr(nf12 / r), R12_fund=repr((nf12 + ev["fund"]) / r), R6_nofund=repr(nf6 / r), R6_fund=repr((nf6 + ev["fund"]) / r),
                split=T.split_of(ev["sig_ts"]), recent=int(T.in_recent(ev["sig_ts"])), bear=int(ev["bear"]), t1_label=ev["label"],
                btc_label=lab, btc_cycle=cyc, iso_week=T.iso_week(ev["entry_ts"]), year=T.utc_year(ev["entry_ts"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=CACHE)
    ap.add_argument("--out", default=HERE)
    a = ap.parse_args()
    lower_priority()
    btc = load_btc_phase(PHASE_CSV)
    rows, cov = [], {}
    drops = {}
    for sym in FRESH:
        f4 = os.path.join(a.cache, "spot_4h", sym + "USDT.csv")
        f1 = os.path.join(a.cache, "spot_1d", sym + "USDT.csv")
        if not (os.path.isfile(f4) and os.path.isfile(f1)):
            drops[sym] = "no 4h or 1d file"
            continue
        k4, k1 = load_klines(f4), load_klines(f1)
        if len(k1) < MIN_DAILY:
            drops[sym] = "fewer than %d daily bars (%d)" % (MIN_DAILY, len(k1))
            continue
        ts, o, h, l, c = (k4[:, i] for i in range(5))
        ts = ts.astype(np.int64)
        dts, dh, dl, dc = k1[:, 0].astype(np.int64), k1[:, 2], k1[:, 3], k1[:, 4]
        bear_d, lab_d = T.daily_bear(dh, dl, dc)
        bearA = T.map_day_flag(ts, dts, bear_d, False)
        labA = T.map_day_flag(ts, dts, lab_d, "")
        fund = load_funding(os.path.join(a.cache, "funding", sym + "USDT.csv"))
        G, first_f, last_f = T.funding_cum(ts, fund or [])
        ev, cnt = T.build_events(sym, ts, o, h, l, c, bearA, labA, G, first_f, last_f)
        for e in ev:
            rows.append(trade_row(e, btc))
        cov[sym] = dict(bars_4h=int(len(k4)), first_4h=utc(ts[0]), last_4h=utc(ts[-1]), bars_1d=int(len(k1)),
                        first_1d=utc(dts[0]), last_1d=utc(dts[-1]), n_gaps_4h=int((np.diff(ts) != T.BAR).sum()),
                        bear_bars_4h=int(bearA[T.WARM4:].sum()), phase_bars_4h=int((labA[T.WARM4:] != "").sum()),
                        funding_file=fund is not None, n_prints=0 if fund is None else len(fund),
                        funding_first=None if first_f is None else utc(first_f), funding_last=None if last_f is None else utc(last_f),
                        events=len(ev), events_bear=sum(1 for e in ev if e["bear"]),
                        trades_no_funding_cover=sum(1 for e in ev if not e["covered"]),
                        trades_hold_past_funding_end=sum(1 for e in ev if e["fund_gap"]), **cnt)
    rows.sort(key=lambda r: (r["sig_ts"], r["coin"]))
    out_csv = os.path.join(a.out, "trades.csv")
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    summary = dict(fresh_universe=FRESH, n_fresh=len(FRESH), kept=sorted(cov), dropped=drops, n_kept=len(cov),
                   n_events_all=len(rows), per_coin=cov)
    with open(os.path.join(a.out, "coverage.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1, sort_keys=False)
    bear = [r for r in rows if r["bear"] == 1]
    print("fresh listed %d, kept %d, dropped %d" % (len(FRESH), len(cov), len(drops)))
    for s, why in drops.items():
        print("  dropped", s, why)
    print("events (all labelled): %d, BEAR true: %d, BEAR false: %d" % (len(rows), len(bear), len(rows) - len(bear)))
    print("BEAR true per split:", dict(Counter(r["split"] for r in bear)), "recent:", sum(r["recent"] for r in bear))
    print("BEAR true per year:", dict(sorted(Counter(r["year"] for r in bear).items())))
    print("BEAR true per coin:", dict(sorted(Counter(r["coin"] for r in bear).items())))
    print("no funding cover (BEAR):", sum(1 for r in bear if r["fund_covered"] == 0), "hold past funding end (BEAR):",
          sum(1 for r in bear if r["fund_gap"] == 1))
    print("wrote", out_csv, os.path.getsize(out_csv), "bytes")


if __name__ == "__main__":
    main()
