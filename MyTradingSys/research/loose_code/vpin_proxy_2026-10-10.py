# T01-F2: raw_1d is a distinct snapshot, NOT the 1m resample (905 of 912 DEV days differ on open, 847 on volume, max 12.01%); derive daily bars from 1m for new work. See MyTradingSys/research/dsa_backtest_audit_2026-10-16/T01_data_forensics.md
import sys
sys.dont_write_bytecode = True
import csv, statistics
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone
from math import sqrt
R = Path(r"C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed")
K = R/"Dumps/backtest/raw/klines"; D = R/"Dumps/backtest/raw_1d/klines"
OUT = R/"MyTradingSys/research/_archive/loose_2026-10/VPIN_PROXY_2026-10-10.md"
BV = 2500.0; RB = 50; PW = 180; SP = 0.90

def load_1m():
    rows = []
    for f in sorted(K.glob("*.csv")):
        with open(f, newline="", encoding="utf-8") as fh:
            r = csv.reader(fh); next(r, None)
            for row in r:
                try: rows.append((int(row[0]),float(row[1]),float(row[2]),float(row[3]),float(row[4]),float(row[5]),float(row[9])))
                except Exception: continue
    rows.sort(key=lambda x: x[0]); d = {}
    for r in rows: d[r[0]] = r
    return [d[k] for k in sorted(d)]

def build_vpin(bars):
    bs = []; av = 0.0; at = 0.0; ae = None
    for (t,o,h,l,c,v,tbv) in bars:
        av += v; at += tbv; ae = t
        if av >= BV:
            bs.append({"t": ae, "imb": abs(2.0*at-av)/av})
            av = 0.0; at = 0.0
    vm = {}
    for i, b in enumerate(bs):
        if i < RB-1: continue
        w = bs[i-RB+1:i+1]
        vm[b["t"]] = sum(x["imb"] for x in w)/RB
    return bs, vm
def load_daily():
    b = {}
    for f in sorted(D.glob("*.csv")):
        with open(f, newline="", encoding="utf-8") as fh:
            r = csv.reader(fh); next(r, None)
            for row in r:
                try: b[int(row[0])] = float(row[4])
                except Exception: continue
    ts = sorted(b); sm = {}
    for i in range(len(ts)):
        if i < 199: continue
        sm[ts[i]] = sum(b[ts[j]] for j in range(i-199, i+1))/200.0
    rg = {}
    for i in range(len(ts)):
        t = ts[i]
        if t not in sm or i < 220: continue
        p = ts[i-20]
        if p not in sm: continue
        if b[t] > sm[t] and sm[t] > sm[p]: rg[t] = "trend_up"
        elif b[t] < sm[t] and sm[t] < sm[p]: rg[t] = "trend_down"
        else: rg[t] = "range"
    return rg, ts

def near(ts, target):
    lo, hi, b = 0, len(ts)-1, None
    while lo <= hi:
        m = (lo+hi)//2
        if ts[m] <= target: b = ts[m]; lo = m+1
        else: hi = m-1
    return b

def rg_of(ms, rg, dts):
    dm = (ms//86400000)*86400000
    d = near(dts, dm-86400000)
    return rg.get(d, "unknown") if d else "unknown"