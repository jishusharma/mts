"""Clean-room twin of mal_bb_mid_engulf arm A1 (SHORT, h=60). Built from PRE_REG.md only."""
import sys
sys.dont_write_bytecode = True
import csv
import numpy as np
from twin_common import *

H = 60
ROUND_TIES = True   # False = v2 before fix T2: float noise (1e-12) turned exact ties mid[i] == mid[i-10] into spurious "lower"


def build(d=None):
    d = d or load_dev()
    b5, b1h, b4h = agg(5, d), agg(60, d), agg(240, d)
    n5 = len(b5["c"])
    mid, up, lo = bb(b5["c"])
    mid = np.round(mid, 6) if ROUND_TIES else mid
    delta = 2 * b5["tbv"] - b5["v"]
    dcs = np.cumsum(np.insert(delta, 0, 0.0))
    sum6 = np.full(len(delta), np.nan)
    sum6[5:] = dcs[6:] - dcs[:-6]          # net taker delta of the 6 bars ending at each bar (signal bar included)
    rsi1, rsi4 = rsi_wilder(b1h["c"]), rsi_wilder(b4h["c"])
    mid1h, _, _ = bb(b1h["c"])
    mid1h = np.round(mid1h, 6) if ROUND_TIES else mid1h
    falling = np.zeros(n5, bool)
    touch = np.zeros(n5, bool)
    htf = np.zeros(n5, bool)
    eng = np.zeros(n5, bool)
    for i in range(30, n5):
        if np.isnan(mid[i]) or np.isnan(mid[i - 10]):
            continue
        falling[i] = mid[i] < mid[i - 10] and sum6[i] < 0
        touch[i] = any(b5["h"][k] >= mid[k] for k in (i - 2, i - 1, i))
        j = (5 * i + 5) // 60 - 1       # last 1h bar closed by the signal bar close
        jj = (5 * i + 5) // 240 - 1
        if j >= 0 and jj >= 0 and not (np.isnan(rsi1[j]) or np.isnan(rsi4[jj]) or np.isnan(mid1h[j])):
            htf[i] = rsi1[j] < 50 and rsi4[jj] < 50 and b5["c"][i] < mid1h[j]
        eng[i] = (b5["c"][i - 1] > b5["o"][i - 1]) and (b5["c"][i] < b5["o"][i]) and (b5["c"][i] < b5["o"][i - 1])
    return d, b5, dict(falling=falling, touch=touch, htf=htf, eng=eng)


def second_break_outcome(lows, idx):
    """Event ids whose NEXT 5m bar trades below the engulf-bar low (arm A2 membership; an outcome, not a signal)."""
    return [i for i in idx if i + 1 < len(lows) and lows[i + 1] < lows[i]]


def run(d=None, strict_cd=False):
    d, b5, f = build(d)
    S = f["falling"] & f["touch"] & f["htf"]
    counts = dict(falling=int(f["falling"].sum()), falling_touch=int((f["falling"] & f["touch"]).sum()), falling_touch_htf=int(S.sum()))
    a1_idx = cooldown(np.nonzero(S & f["eng"])[0], 12, strict_cd)
    ct_idx = cooldown(np.nonzero(S & ~f["eng"])[0], 12, strict_cd)
    counts.update(a1=len(a1_idx), ctrl=len(ct_idx))
    N = len(d["t"])
    def events(idx, off5=0, label=""):
        rows = []
        for i in idx:
            e = 5 * (i + off5) + 6
            x = e + H
            if x >= N:
                continue
            pe, px, g, net = trade(d, e, x, -1)
            rows.append(dict(arm=label, sig_ts=int(d["t"][5 * (i + off5) + 4]) + 60000, side="SHORT", entry_ts=int(d["t"][e]), entry_px=pe,
                             exit_ts=int(d["t"][x]), exit_px=px, G=g, net=net, day=e // 1440))
        return rows
    a1 = events(a1_idx, 0, "A1")
    ct = events(ct_idx, 0, "CTL_A1")
    sb = second_break_outcome(b5["l"], a1_idx)
    counts["a2"] = len(sb)
    return d, a1, ct, counts


def summarise(a1, ct, d):
    G = np.array([r["G"] for r in a1]); Gc = np.array([r["G"] for r in ct])
    return verdict(G, [r["day"] for r in a1], None, Gc, [r["day"] for r in ct], mdd_bh(d["c"]))


def write(rows, path):
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader(); w.writerows(rows)


if __name__ == "__main__":
    d, a1, ct, counts = run()
    print(counts)
    print(summarise(a1, ct, d))
    write(a1, __file__.replace("twin_mal_bb.py", "out/twin_mal_bb_A1_events.csv"))
