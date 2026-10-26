import sys, os, glob, json, csv
sys.dont_write_bytecode = True

ROOT = r"C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed"
K1D  = os.path.join(ROOT, "Dumps", "backtest", "raw_1d", "klines")
KFD  = os.path.join(ROOT, "Dumps", "backtest", "raw_fund", "fundingRate")

def load_daily():
    bars = []
    for f in sorted(glob.glob(os.path.join(K1D, "BTCUSDT-1d-*.csv"))):
        with open(f) as fh:
            for row in csv.reader(fh):
                if not row or row[0] == "open_time": continue
                bars.append({"t": int(row[0]) // 86400000,
                             "o": float(row[1]), "h": float(row[2]),
                             "l": float(row[3]), "c": float(row[4])})
    bars.sort(key=lambda b: b["t"])
    return bars

def load_funding():
    out = {}
    for f in sorted(glob.glob(os.path.join(KFD, "BTCUSDT-fundingRate-*.csv"))):
        with open(f) as fh:
            r = csv.DictReader(fh)
            for row in r:
                d = int(row["calc_time"]) // 86400000
                out[d] = out.get(d, 0.0) + float(row["last_funding_rate"])
    return out

def sma(v, n):
    out = [None]*len(v); s = 0.0
    for i, x in enumerate(v):
        s += x
        if i >= n: s -= v[i-n]
        if i >= n-1: out[i] = s/n
    return out

def ema(v, n):
    out = [None]*len(v); k = 2.0/(n+1); prev = None
    for i, x in enumerate(v):
        prev = x if prev is None else x*k + prev*(1-k)
        if i >= n-1: out[i] = prev
    return out

def rsi(v, n):
    out = [None]*len(v); ag = al = 0.0
    for i in range(1, len(v)):
        d = v[i]-v[i-1]; g = max(d,0.0); l = max(-d,0.0)
        if i <= n:
            ag += g/n; al += l/n
            if i == n: out[i] = 100.0 if al == 0 else 100 - 100/(1+ag/al)
        else:
            ag = (ag*(n-1)+g)/n; al = (al*(n-1)+l)/n
            out[i] = 100.0 if al == 0 else 100 - 100/(1+ag/al)
    return out

def atr(bars, n):
    tr = [None]*len(bars)
    for i, b in enumerate(bars):
        if i == 0: tr[i] = b["h"]-b["l"]; continue
        pc = bars[i-1]["c"]
        tr[i] = max(b["h"]-b["l"], abs(b["h"]-pc), abs(b["l"]-pc))
    out = [None]*len(bars); s = 0.0
    for i, x in enumerate(tr):
        s += x
        if i >= n: s -= tr[i-n]
        if i >= n-1: out[i] = s/n
    return out

def donchian(bars, n):
    hi = [None]*len(bars); lo = [None]*len(bars)
    for i in range(n, len(bars)):
        w = bars[i-n:i]
        hi[i] = max(b["h"] for b in w); lo[i] = min(b["l"] for b in w)
    return hi, lo

def adx(bars, n):
    pdi = [None]*len(bars); mdi = [None]*len(bars); out = [None]*len(bars)
    trs = [0.0]*len(bars); pdm = [0.0]*len(bars); mdm = [0.0]*len(bars)
    for i in range(1, len(bars)):
        up = bars[i]["h"]-bars[i-1]["h"]; dn = bars[i-1]["l"]-bars[i]["l"]
        pdm[i] = up if (up > dn and up > 0) else 0.0
        mdm[i] = dn if (dn > up and dn > 0) else 0.0
        pc = bars[i-1]["c"]
        trs[i] = max(bars[i]["h"]-bars[i]["l"], abs(bars[i]["h"]-pc), abs(bars[i]["l"]-pc))
    at = 0.0; ap = 0.0; am = 0.0; dxs = []
    for i in range(1, len(bars)):
        if i <= n:
            at += trs[i]; ap += pdm[i]; am += mdm[i]
            if i == n:
                pdi[i] = 100*ap/at if at else 0.0; mdi[i] = 100*am/at if at else 0.0
                d = abs(pdi[i]-mdi[i])/(pdi[i]+mdi[i]) if (pdi[i]+mdi[i]) else 0.0
                dxs.append(d); out[i] = 100*sum(dxs)/len(dxs)
        else:
            at = at - at/n + trs[i]; ap = ap - ap/n + pdm[i]; am = am - am/n + mdm[i]
            pdi[i] = 100*ap/at if at else 0.0; mdi[i] = 100*am/at if at else 0.0
            d = abs(pdi[i]-mdi[i])/(pdi[i]+mdi[i]) if (pdi[i]+mdi[i]) else 0.0
            dxs.append(d); out[i] = 100*sum(dxs[-n:])/len(dxs[-n:])
    return out

def supertrend(bars, n=10, m=3.0):
    a = atr(bars, n); dirn = [1]*len(bars); st = [None]*len(bars)
    for i in range(len(bars)):
        if a[i] is None: continue
        hl2 = (bars[i]["h"]+bars[i]["l"])/2.0
        up = hl2 - m*a[i]; dn = hl2 + m*a[i]
        if i == 0 or st[i-1] is None:
            st[i] = up; dirn[i] = 1; continue
        if dirn[i-1] == 1:
            st[i] = max(up, st[i-1]); dirn[i] = 1 if bars[i]["c"] > st[i] else -1
            if dirn[i] == -1: st[i] = dn
        else:
            st[i] = min(dn, st[i-1]); dirn[i] = -1 if bars[i]["c"] < st[i] else 1
            if dirn[i] == 1: st[i] = up
    return st, dirn

def run_series(bars, fund, signal, stop_mult=2.0, trail_mult=2.0, fee=0.0005):
    a = atr(bars, 14); eq = 1.0; curve = []; trades = []
    pos = False; entry = 0.0; stop = 0.0; hw = 0.0; ei = 0
    for i in range(len(bars)):
        c = bars[i]["c"]
        if pos:
            f = fund.get(bars[i]["t"], 0.0); eq *= (1 - f)
            if c > hw:
                hw = c
                if hw >= entry + a[ei]:
                    stop = max(stop, hw - trail_mult*a[ei])
            if c <= stop:
                eq *= (1 - fee); eq *= (c/entry); eq *= (1 - fee)
                trades.append(c/entry - 1 - 2*fee); pos = False
        if (not pos) and signal[i] and a[i] is not None:
            entry = c; ei = i; stop = c - stop_mult*a[i]; hw = c
            eq *= (1 - fee); pos = True
        curve.append(eq)
    return eq, curve, trades

def maxdd(curve):
    pk = curve[0]; m = 0.0
    for x in curve:
        pk = max(pk, x); m = max(m, 1 - x/pk)
    return m

def metrics(eq, curve, trades, days):
    yrs = days/365.25
    cagr = eq**(1/yrs) - 1 if yrs > 0 and eq > 0 else -1.0
    wins = sum(1 for t in trades if t > 0)
    gains = sum(t for t in trades if t > 0); losses = -sum(t for t in trades if t < 0)
    pf = gains/losses if losses > 0 else float("inf")
    return {"cagr": cagr, "maxdd": maxdd(curve), "pf": pf,
            "wr": wins/len(trades) if trades else 0.0, "n": len(trades)}

def build_signals(bars):
    c = [b["c"] for b in bars]
    s200 = sma(c, 200); e7 = ema(c, 7); e20 = ema(c, 20); e50 = ema(c, 50)
    r2 = rsi(c, 2); d2 = adx(bars, 2); d14 = adx(bars, 14)
    dh, dl = donchian(bars, 20); _, sdir = supertrend(bars, 10, 3.0)
    n = len(bars)
    sig = {"a": [False]*n, "b": [False]*n, "c": [False]*n}
    for i in range(1, n):
        if None in (s200[i], e7[i], r2[i], d2[i]):
            pass
        else:
            sig["a"][i] = c[i] > s200[i] and c[i] > e7[i] and r2[i] > d2[i]
        if None in (s200[i], e20[i], d14[i]):
            pass
        else:
            sig["b"][i] = c[i] > s200[i] and c[i] > e20[i] and d14[i] > 20
        if sdir[i] == 1 and sdir[i-1] == -1:
            sig["c"][i] = True
    return sig

def main():
    bars = load_daily(); fund = load_funding()
    sig = build_signals(bars)
    days = bars[-1]["t"] - bars[0]["t"]
    out = {}
    for k in ("a", "b", "c"):
        eq, curve, trades = run_series(bars, fund, sig[k])
        out[k] = metrics(eq, curve, trades, days)
    bh = bars[-1]["c"]/bars[0]["c"]
    out["bh"] = {"cagr": bh**(365.25/days)-1, "maxdd": maxdd([b["c"] for b in bars]), "n": 1,
                 "wr": 1.0, "pf": float("inf")}
    out["_range"] = {"start": bars[0]["t"], "end": bars[-1]["t"], "bars": len(bars), "days": days}
    print(json.dumps(out, indent=2, default=str))
    dst = os.path.join(ROOT, "MyTradingSys", "research", "setup_alpha_beta_2026-10-10", "ALPHA_RESULTS.md")
    with open(dst, "w", encoding="utf-8", newline="\n") as f:
        f.write("# Alpha results (NO-SOURCE)\n\n")
        f.write("Daily long-flat SMA200 variants, Binance BTCUSDT 1d, fee 0.05% per side + funding.\n")
        f.write("NO-SOURCE: the setup numbers come from a chatbot handoff, not a trader transcript.\n\n")
        f.write("| variant | CAGR | maxDD | PF | win rate | trades |\n|---|---|---|---|---|---|\n")
        for k, name in (("a","A: SMA200+EMA7+RSI2>ADX2"),("b","B: SMA200+EMA20+ADX14>20"),("c","C: Supertrend(10,3)")):
            m = out[k]
            f.write("| %s | %.2f%% | %.2f%% | %.2f | %.1f%% | %d |\n" % (name, m["cagr"]*100, m["maxdd"]*100, m["pf"], m["wr"]*100, m["n"]))
        f.write("| buy-and-hold | %.2f%% | %.2f%% | - | - | 1 |\n" % (out["bh"]["cagr"]*100, out["bh"]["maxdd"]*100))
    return 0

if __name__ == "__main__":
    sys.exit(main())
# T01-F2: raw_1d is a distinct snapshot, NOT the 1m resample (905 of 912 DEV days differ on open, 847 on volume, max 12.01%); derive daily bars from 1m for new work. See MyTradingSys/research/dsa_backtest_audit_2026-10-16/T01_data_forensics.md
