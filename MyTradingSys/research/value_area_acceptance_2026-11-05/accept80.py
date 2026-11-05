"""Value-area acceptance on BTC (Dalton 80% rule, as Tom/Fabio use 'acceptance back inside value').
Prior UTC day value area (70% of volume around POC, 1m close-binned, $50 bins).
Event R (re-entry): today's price is outside prior VA at some point, then two consecutive 30m closes inside VA
 -> success = touches the far edge of VA later the same UTC day.
Event A (acceptance outside below): two consecutive 30m closes below VAL (after being inside) -> continuation =
 trades a further 1x VA-width/2 below VAL same day, vs return = closes back above POC same day.
Read-only, public data only."""
import gzip, csv, glob, os, sys, json, urllib.request, datetime as dt
from collections import defaultdict

BIN = 50.0
def va(bars):
    vol = defaultdict(float)
    for (_, o, h, l, c, v) in bars:
        vol[round(c / BIN) * BIN] += v
    if not vol: return None
    tot = sum(vol.values()); px = sorted(vol)
    poc = max(px, key=lambda p: vol[p]); i = j = px.index(poc); acc = vol[poc]
    while acc < 0.7 * tot:
        up = vol[px[j + 1]] if j + 1 < len(px) else -1
        dn = vol[px[i - 1]] if i > 0 else -1
        if up >= dn: j += 1; acc += up
        else: i -= 1; acc += dn
    return px[i], poc, px[j]

def days_local():
    out = {}
    for f in sorted(glob.glob("F:/MTS/data/orderflow_1m/*.csv.gz")):
        d = os.path.basename(f)[:10]; rows = []
        with gzip.open(f, "rt") as fh:
            for r in csv.DictReader(fh):
                rows.append((int(r["t"]), float(r["o"]), float(r["h"]), float(r["l"]), float(r["c"]),
                             float(r["buy_vol"]) + float(r["sell_vol"])))
        if len(rows) > 1300: out[d] = rows
    return out

def m30(bars):
    g = defaultdict(list)
    for b in bars: g[b[0] // 1800000].append(b)
    return [g[k] for k in sorted(g)]

def study(days):
    keys = sorted(days); R = []; A = []
    for p, d in zip(keys, keys[1:]):
        if (dt.date.fromisoformat(d) - dt.date.fromisoformat(p)).days != 1: continue
        v = va(days[p]);
        if not v: continue
        val, poc, vah = v; w = vah - val
        if w <= 0: continue
        segs = m30(days[d]); outside = False; inside_run = 0; r_done = False
        below_run = 0; was_inside = False; a_done = False
        for k, s in enumerate(segs):
            hi = max(b[2] for b in s); lo = min(b[3] for b in s); c = s[-1][4]
            rest = [b for seg in segs[k + 1:] for b in seg]
            if not r_done:
                if hi > vah or lo < val: outside = True
                if outside and val <= c <= vah:
                    inside_run += 1
                    if inside_run == 2:
                        r_done = True
                        # which side came from: far edge = opposite of the side last outside
                        prev = [b for seg in segs[:k + 1] for b in seg]
                        last_out = next((b for b in reversed(prev) if b[2] > vah or b[3] < val), None)
                        far = val if last_out and last_out[2] > vah else vah
                        hit = any((b[3] <= far) if far == val else (b[2] >= far) for b in rest)
                        R.append(hit)
                else: inside_run = 0
            if not a_done:
                if val <= c <= vah: was_inside = True
                if was_inside and c < val:
                    below_run += 1
                    if below_run == 2:
                        a_done = True
                        cont = any(b[3] <= val - w / 2 for b in rest)
                        ret = any(b[4] >= poc for b in rest)
                        A.append((cont, ret))
                else: below_run = 0
    return R, A

def wilson(k, n, z=1.96):
    if n == 0: return (0, 0)
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); m = z * ((p * (1 - p) + z * z / (4 * n)) / n) ** 0.5
    return ((c - m) / d, (c + m) / d)

def live_today():
    out = []
    for start in ["2026-11-04T00:00:00", "2026-11-04T16:40:00", "2026-11-05T00:00:00", "2026-11-05T16:40:00"]:
        ms = int(dt.datetime.fromisoformat(start).replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
        u = f"https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1m&startTime={ms}&limit=1000"
        out += json.load(urllib.request.urlopen(u, timeout=20))
    seen = {}; [seen.setdefault(r[0], r) for r in out]
    rows = [(r[0], float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5])) for r in sorted(seen.values())]
    by = defaultdict(list)
    for r in rows: by[dt.datetime.fromtimestamp(r[0] / 1000, dt.timezone.utc).date().isoformat()].append(r)
    return by

if __name__ == "__main__":
    days = days_local(); R, A = study(days)
    k = sum(R); print(f"days {len(days)}  R re-entry events {len(R)} far-edge hit {k} = {k/len(R):.0%} CI {wilson(k,len(R))[0]:.0%}..{wilson(k,len(R))[1]:.0%}")
    n = len(A); c = sum(a[0] for a in A); r = sum(a[1] for a in A)
    print(f"A accepted-below-VAL events {n}: continue half-width lower {c} = {c/n:.0%} CI {wilson(c,n)[0]:.0%}..{wilson(c,n)[1]:.0%}; back to POC {r} = {r/n:.0%}")
    by = live_today()
    v = va(by["2026-11-04"]); print("11-04 VA (VAL,POC,VAH):", v, "bars", len(by["2026-11-04"]))
    # balance since the US-open rally: 11-04 16:00 -> 11-05 11:59
    bal = [b for d in by for b in by[d] if dt.datetime(2026,11,4,16,tzinfo=dt.timezone.utc).timestamp()*1000 <= b[0] < dt.datetime(2026,11,5,12,tzinfo=dt.timezone.utc).timestamp()*1000]
    print("20h balance VA:", va(bal))
    t = by["2026-11-05"]; print("11-05 so far: low", min(b[3] for b in t), "high", max(b[2] for b in t), "last", t[-1][4], dt.datetime.fromtimestamp(t[-1][0]/1000, dt.timezone.utc))
    for s in m30(t)[-6:]:
        print(dt.datetime.fromtimestamp(s[0][0]/1000, dt.timezone.utc).strftime("%H:%M"), "30m close", s[-1][4])
