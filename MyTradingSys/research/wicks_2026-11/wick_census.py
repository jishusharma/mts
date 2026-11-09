"""Wick census v2, BTCUSDT perp (Bybit), 2026-10-03..2026-11-07. All thresholds OURS.
long wick (bar i): wick >= 60% of the bar range and range >= 1.5 x median range of the previous LOOK bars.
sweep (same bar): low < min(low of the previous 20 bars) and close > that prior low. Mirror for highs.
V-sweep (multi-bar, 5m matters): low < prior 20-bar low and within the next 3 bars a close back above that low: the wick is split over 2-4 bars.
outcome (R = 1): after a lower wick, long at the close, stop = wick low, target = close + (close - low). bought back = target before stop within H bars.
knife (context): over the 12 bars before the wick the drop from the highest high to the wick bar's open is <= -2.0% AND the largest counter-move
   inside those bars (close above the running low) is < 25% of that drop: a fall with no retracement. Mirror for upper wicks.
session (UTC): ASIA 00-08, EU 08-13, US 13-21, LATE 21-24.
"""
import json, statistics as st, datetime as dt, sys
U = lambda ms: dt.datetime.fromtimestamp(int(ms) / 1000, dt.UTC)
tf = sys.argv[1] if len(sys.argv) > 1 else "15m"
rows = [(int(r[0]), float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5])) for r in json.load(open(f"btc_{tf}_5w.json"))]
H = {"15m": 16, "5m": 24}[tf]
LOOK = 96 if tf == "15m" else 288
def session(t):
    h = U(t).hour
    return "ASIA" if h < 8 else "EU" if h < 13 else "US" if h < 21 else "LATE"
def week(t):
    d = U(t).date(); return (d - dt.timedelta(days=d.weekday())).isoformat()
def knife_state(i, side):
    pre = rows[i - 12:i]; o = rows[i][1]
    if side == "LOW":
        top = max(r[2] for r in pre); drop = (o / top - 1) * 100
        if drop > -2.0: return False
        run = pre[0][3]; bounce = 0.0
        for r in pre:
            run = min(run, r[3]); bounce = max(bounce, r[4] - run)
        return bounce < 0.25 * (top - o)
    bot = min(r[3] for r in pre); rise = (o / bot - 1) * 100
    if rise < 2.0: return False
    run = pre[0][2]; dip = 0.0
    for r in pre:
        run = max(run, r[2]); dip = max(dip, run - r[4])
    return dip < 0.25 * (o - bot)
def outcome(i, side, stop, target):
    for j in range(i + 1, min(i + 1 + H, len(rows))):
        if side == "LOW":
            if rows[j][3] < stop: return False
            if rows[j][2] >= target: return True
        else:
            if rows[j][2] > stop: return False
            if rows[j][3] <= target: return True
    return None
ev = []
for i in range(LOOK + 1, len(rows) - H):
    t, o, h, l, c, v = rows[i]
    rng = h - l
    if rng <= 0: continue
    med = st.median(r[2] - r[3] for r in rows[i - LOOK:i])
    if rng < 1.5 * med: continue
    lw = min(o, c) - l; uw = h - max(o, c)
    for side, wick in (("LOW", lw), ("UP", uw)):
        if wick < 0.6 * rng: continue
        prior = rows[i - 20:i]
        if side == "LOW":
            plow = min(r[3] for r in prior); sweep = l < plow and c > plow
            res = outcome(i, side, l, c + (c - l))
        else:
            phigh = max(r[2] for r in prior); sweep = h > phigh and c < phigh
            res = outcome(i, side, h, c - (h - c))
        vol_rel = v / st.median(r[5] for r in rows[i - LOOK:i])
        ev.append(dict(t=t, side=side, kind="1bar", wick_pct=wick / c * 100, rng_x=rng / med, sweep=sweep, bought=res, knife=knife_state(i, side),
                       session=session(t), week=week(t), vol_rel=vol_rel, low=l, high=h, close=c))
# V-sweeps (multi-bar)
vs = []
i = LOOK + 1
while i < len(rows) - H - 4:
    t, o, h, l, c, v = rows[i]
    prior = rows[i - 20:i]; plow = min(r[3] for r in prior); phigh = max(r[2] for r in prior)
    if l < plow and c <= plow:
        for k in range(1, 4):
            if rows[i + k][4] > plow:
                lo = min(r[3] for r in rows[i:i + k + 1]); cc = rows[i + k][4]
                vs.append(dict(t=t, side="LOW", kind=f"V{k+1}", wick_pct=(cc - lo) / cc * 100, sweep=True, bought=outcome(i + k, "LOW", lo, cc + (cc - lo)),
                               knife=knife_state(i, "LOW"), session=session(t), week=week(t), vol_rel=max(r[5] for r in rows[i:i + k + 1]) / st.median(r[5] for r in rows[i - LOOK:i]),
                               low=lo, high=max(r[2] for r in rows[i:i + k + 1]), close=cc, rng_x=0))
                i += k; break
    elif h > phigh and c >= phigh:
        for k in range(1, 4):
            if rows[i + k][4] < phigh:
                hi = max(r[2] for r in rows[i:i + k + 1]); cc = rows[i + k][4]
                vs.append(dict(t=t, side="UP", kind=f"V{k+1}", wick_pct=(hi - cc) / cc * 100, sweep=True, bought=outcome(i + k, "UP", hi, cc - (hi - cc)),
                               knife=knife_state(i, "UP"), session=session(t), week=week(t), vol_rel=max(r[5] for r in rows[i:i + k + 1]) / st.median(r[5] for r in rows[i - LOOK:i]),
                               low=min(r[3] for r in rows[i:i + k + 1]), high=hi, close=cc, rng_x=0))
                i += k; break
    i += 1
def tab(key, rows_):
    groups = {}
    for e in rows_: groups.setdefault(e[key], []).append(e)
    print(f"| {key} | n | sweeps | target first (R=1) | stop first | open | median wick % | median rel vol |")
    print("|---|---|---|---|---|---|---|---|")
    for k in sorted(groups, key=str):
        g = groups[k]; b = sum(1 for e in g if e['bought'] is True); f = sum(1 for e in g if e['bought'] is False)
        print(f"| {k} | {len(g)} | {sum(e['sweep'] for e in g)} | {b} ({b/len(g)*100:.0f}%) | {f} | {len(g)-b-f} | {st.median(e['wick_pct'] for e in g):.2f} | {st.median(e['vol_rel'] for e in g):.1f} |")
print(f"# {tf}: {len(rows)} bars, {len(ev)} single-bar long wicks ({sum(e['side']=='LOW' for e in ev)} lower, {sum(e['side']=='UP' for e in ev)} upper), {len(vs)} multi-bar V-sweeps; H={H} bars; entry at the close, stop at the wick, target R=1")
for side in ("LOW", "UP"):
    sub = [e for e in ev if e["side"] == side]
    print(f"\n## {side} single-bar wicks by week"); tab("week", sub)
    print(f"\n## {side} single-bar wicks by session"); tab("session", sub)
    print(f"\n## {side} single-bar wicks: knife context"); tab("knife", sub)
    print(f"\n## {side} single-bar wicks: sweep vs not"); tab("sweep", sub)
    sv = [e for e in vs if e["side"] == side]
    print(f"\n## {side} V-sweeps (multi-bar) by week"); tab("week", sv)
    print(f"\n## {side} V-sweeps: knife context"); tab("knife", sv)
    print(f"\n## {side} V-sweeps by session"); tab("session", sv)
print("\n## Fri 2026-11-06 13:00-18:00 UTC: wicks and V-sweeps")
for e in sorted(ev + vs, key=lambda e: e['t']):
    if U(e['t']).date() == dt.date(2026, 11, 6) and 13 <= U(e['t']).hour < 18:
        print(f"{U(e['t']).strftime('%H:%M')} {e['side']} {e['kind']} low {e['low']:.0f} high {e['high']:.0f} close {e['close']:.0f} wick {e['wick_pct']:.2f}% relvol {e['vol_rel']:.1f} sweep={e['sweep']} knife={e['knife']} target_first={e['bought']}")
if tf == "5m":
    print("\n## Fri 2026-11-06 14:50-15:30 UTC, 5m bars")
    for r in rows:
        d = U(r[0])
        if d.date() == dt.date(2026, 11, 6) and (d.hour == 14 and d.minute >= 50 or d.hour == 15 and d.minute <= 30):
            print(f"{d.strftime('%H:%M')} O {r[1]:.0f} H {r[2]:.0f} L {r[3]:.0f} C {r[4]:.0f} V {r[5]:.0f}")
