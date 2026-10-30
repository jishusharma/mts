"""T053 step 3: hedge-variant backtest on local 1m BTCUSDT, DEV only (2022-01..2025-08). Never reads 2025-09+.
Fees: backtest/fees.py BINANCE_TAKER (SOURCED). Funding: no local funding-rate file (see report); not modelled.
All trade params are OURS. Run: python hedge_bt.py > results.txt"""
import sys, os, glob
sys.dont_write_bytecode = True
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "backtest"))
from fees import BINANCE_TAKER as FEE

KL = "F:/MTS/data/tom_raw/klines"
W = 1440           # time exit, minutes (OURS)
SL = 0.01          # long-leg stop (OURS)
SS = 0.005         # b2 short-leg stop (OURS)
ENTRY_EVERY = 240  # entry every 4h bar open (OURS; no signal, isolates the hedge effect)
FEE_COVER = 4 * FEE  # 4 taker sides = 20 bps (T053 research D1)


def load():
    fs = sorted(glob.glob(f"{KL}/BTCUSDT-1m-20??-??.csv"))  # monthly files only
    fs = [f for f in fs if "2022-01" <= os.path.basename(f)[11:18] <= "2025-08"]
    assert fs and not any("2025-09" in f for f in fs)
    df = pd.concat([pd.read_csv(f, usecols=["open_time", "open", "high", "low", "close"]) for f in fs], ignore_index=True)
    df = df.drop_duplicates("open_time").sort_values("open_time").reset_index(drop=True)
    assert df.open_time.max() < 1756684800000  # < 2025-09-01
    return df


def bands(c, n, k):
    s = pd.Series(c)
    m = s.rolling(n).mean()
    sd = s.rolling(n).std(ddof=0)
    return (m + k * sd).values, (m - k * sd).values, m.values


def run():
    df = load()
    o, h, l, c, t = (df[x].values.astype(float) for x in ("open", "high", "low", "close", "open_time"))
    N = len(df)
    bb = {20: bands(c, 20, 2.0), 60: bands(c, 60, 2.0)}
    rows = []
    for i in range(100, N - W - 1, ENTRY_EVERY):
        if t[i + W] - t[i] != W * 60000:  # gap in data -> skip
            continue
        E = o[i]
        sl = slice(i, i + W)
        yr = pd.Timestamp(t[i], unit="ms").year
        for d in (1, -1):
            if d == 1:
                adv = l[sl] / E - 1; fav = h[sl] / E - 1; cl = c[sl] / E - 1
            else:
                adv = -(h[sl] / E - 1); fav = -(l[sl] / E - 1); cl = -(c[sl] / E - 1)
            hit = adv <= -SL
            stop_idx = int(np.argmax(hit)) if hit.any() else W
            end_ret = cl[-1]
            u = (-SL - 2 * FEE) if stop_idx < W else (end_ret - 2 * FEE)
            rec = {"yr": yr, "d": d, "U": u}
            for kk in (1.5, 2.0, 3.0):
                hl = kk * FEE_COVER
                m = fav >= hl
                trig = int(np.argmax(m)) if m.any() else W
                if trig < W and trig < stop_idx:  # same bar as stop: stop wins (worst case)
                    rec[f"A_lock_{kk}"] = hl - 4 * FEE  # long+short locked: pnl = hl, 4 taker sides
                    L = FEE_COVER
                    rest = cl[trig + 1:]
                    mm = rest <= hl - L
                    if not mm.any():
                        rec[f"A_lift_{kk}"] = hl - 4 * FEE
                    else:
                        li = trig + 1 + int(np.argmax(mm))
                        ra = adv[li + 1:]
                        s2 = (int(np.argmax(ra <= -SL)) + li + 1) if (ra <= -SL).any() else W
                        long_pnl = -SL if s2 < W else end_ret
                        rec[f"A_lift_{kk}"] = long_pnl + L - 4 * FEE
                else:
                    rec[f"A_lock_{kk}"] = u
                    rec[f"A_lift_{kk}"] = u
            for n, (up, lo, mid) in bb.items():
                if d == 1:
                    brk = c[sl] > up[sl]; back = c[sl] <= mid[sl]
                else:
                    brk = c[sl] < lo[sl]; back = c[sl] >= mid[sl]
                brk = brk & (cl > 0)  # only when the long leg is in profit
                for cap, cname in ((10**9, 'unl'), (1, '1x')):
                    # B1: hedge on break, lift on return to mid; stop suspended while hedged
                    pnl = 0.0; fees = 0.0; ncy = 0; hedged = False; hr = 0.0; stopped = False
                    for j in range(W):
                        if not hedged:
                            if j == stop_idx:
                                stopped = True
                                break
                            if brk[j] and ncy < cap:
                                hedged = True; hr = cl[j]; fees += 2 * FEE; ncy += 1
                        elif back[j]:
                            pnl += -(cl[j] - hr); fees += 2 * FEE; hedged = False
                    long_end = -SL if stopped else end_ret
                    if hedged:
                        pnl += -(cl[-1] - hr)
                    rec[f"B1_bb{n}_{cname}"] = long_end + pnl - 2 * FEE - fees
                    # B2: independent opposite position on break, own stop SS, exit at mid return; long as baseline
                    spnl = 0.0; sfees = 0.0; ncs = 0; inpos = False; er = 0.0
                    for j in range(W):
                        if not inpos:
                            if brk[j] and ncs < cap:
                                inpos = True; er = cl[j]; sfees += 2 * FEE; ncs += 1
                        else:
                            if fav[j] - er >= SS:
                                spnl += -SS; inpos = False
                            elif back[j]:
                                spnl += -(cl[j] - er); inpos = False
                    if inpos:
                        spnl += -(cl[-1] - er)
                    rec[f"B2_bb{n}_{cname}"] = u + spnl - sfees
            rows.append(rec)
    return pd.DataFrame(rows)


def summarize(r):
    out = []
    cols = [x for x in r.columns if x not in ("yr", "d")]
    for name, g in (("ALL dev 2022-01..2025-08", r), ("early 2022-2023", r[r.yr <= 2023]), ("late 2024-2025(Jan-Aug)", r[r.yr >= 2024])):
        out.append(f"\n## {name} (n={len(g)} long+short trades)")
        out.append("| variant | mean net bps/trade | win % | total net % | incr vs U bps | incr t-stat |")
        out.append("|---|---|---|---|---|---|")
        for cn in cols:
            x = g[cn].values; dlt = x - g["U"].values
            tt = dlt.mean() / (dlt.std(ddof=1) / np.sqrt(len(dlt))) if dlt.std() > 0 else float("nan")
            out.append(f"| {cn} | {x.mean()*1e4:.2f} | {100*(x>0).mean():.1f} | {100*x.sum():.1f} | {dlt.mean()*1e4:.2f} | {tt:.2f} |")
    return "\n".join(out)


if __name__ == "__main__":
    r = run()
    print("fee per side (SOURCED fees.py BINANCE_TAKER):", FEE, "| W", W, "SL", SL, "SS", SS, "entry every", ENTRY_EVERY, "min")
    print(summarize(r))
    for dd, nm in ((1, "LONG entries only"), (-1, "SHORT entries only")):
        print("\n### " + nm)
        print(summarize(r[r.d == dd]).split("## early")[0])
