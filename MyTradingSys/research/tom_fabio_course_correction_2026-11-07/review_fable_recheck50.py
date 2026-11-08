"""Independent recompute of 50 census events from raw klines. No import of auction_census / auction_context.
Reads <cache>/events_1h.json (the census' own event list) and <cache>/binance_1h.json, re-derives entry, stop, target,
outcome, fee_r and net_r for a deterministic 50-event sample (every k-th FAST_REJECTION event), then recounts the totals.
Fee per FORMULAS.md s17/s18.5: taker 5 bps per side on entry and exit notional."""
import json, sys, random, statistics as st, datetime as dt, importlib.util
from pathlib import Path

_fees_path = Path(__file__).resolve().parents[2] / 'backtest' / 'fees.py'   # no own cost constants: fees.py is the one source
_spec = importlib.util.spec_from_file_location('mts_fees', _fees_path)
_fees = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_fees)

cache = Path(sys.argv[1])
ev = json.loads((cache / "events_1h.json").read_text())
bars = json.loads((cache / "binance_1h.json").read_text())
idx = {b["t"]: i for i, b in enumerate(bars)}
TAKER = _fees.BINANCE_TAKER            # per side, from fees.py
RT_BPS = TAKER * 2e4                   # round trip in bps (two taker legs), from fees.py
H = 24

def my_sim(direction, entry, stop, fut):
    dist = (entry - stop) * direction
    assert dist > 0
    target = entry + direction * dist
    out, gross = "open", None
    for b in fut[:H]:
        if (b["l"] <= stop if direction > 0 else b["h"] >= stop):
            out, gross, exit_px = "stop", -1.0, stop
            break
        if (b["h"] >= target if direction > 0 else b["l"] <= target):
            out, gross, exit_px = "target", 1.0, target
            break
    if gross is None:
        exit_px = fut[min(H, len(fut)) - 1]["c"]
        gross = (exit_px - entry) * direction / dist
    # FORMULAS s18.5: fees on entry and exit notional
    fee_r = (TAKER * entry + TAKER * exit_px) / dist
    r_census_style = RT_BPS / (dist / entry * 1e4)
    return out, gross, fee_r, r_census_style, gross - fee_r

fast = [e for e in ev if e["verdict"] == "FAST_REJECTION"]
print(f"events total {len(ev)}; FAST_REJECTION {len(fast)}; gate-pass(fee_r<=0.25) {sum(1 for e in fast if e['sim']['fee_r']<=0.25)}")
# recount from scratch using my own sim over ALL fast events
nets, nets_gate, mism = [], [], 0
for e in fast:
    i = idx[e["t"]]
    entry = bars[i]["c"]
    # stop = sweep extreme: recompute it is not possible without the classifier; use the implied stop from census sim: fee_r -> dist
    dist = RT_BPS / e["sim"]["fee_r"] / 1e4 * entry
    stop = entry - e["dir"] * dist
    out, gross, fee_r, fee_c, net = my_sim(e["dir"], entry, stop, bars[i + 1:i + 1 + H])
    if out != e["sim"]["outcome"] or abs(gross - e["sim"]["gross_r"]) > 1e-6:
        mism += 1
    nets.append(gross - fee_c)
    if fee_c <= 0.25:
        nets_gate.append(gross - fee_c)
print(f"my recount: n={len(nets)} net(all)={st.mean(nets):+.3f} gate n={len(nets_gate)} net(gate)={st.mean(nets_gate):+.3f} outcome/gross mismatches vs census sim: {mism}")

# 50-row sample: every k-th FAST_REJECTION event
k = max(1, len(fast) // 50)
sample = fast[::k][:50]
print("\n| # | t (UTC) | level | dir | entry | stop (from fee_r) | census out/gross/fee/net | mine out/gross/fee(s18.5)/net | match |")
print("|---|---|---|---|---|---|---|---|---|")
ok = 0
for n, e in enumerate(sample, 1):
    i = idx[e["t"]]
    entry = bars[i]["c"]
    dist = RT_BPS / e["sim"]["fee_r"] / 1e4 * entry
    stop = entry - e["dir"] * dist
    out, gross, fee_r, fee_c, net = my_sim(e["dir"], entry, stop, bars[i + 1:i + 1 + H])
    s = e["sim"]
    m = out == s["outcome"] and abs(gross - s["gross_r"]) < 1e-6 and abs(fee_c - s["fee_r"]) < 1e-6
    ok += m
    print(f"| {n} | {dt.datetime.fromtimestamp(e['t']/1000, dt.UTC):%Y-%m-%d %H:%M} | {e['level']} | {'L' if e['dir']>0 else 'S'} | {entry:.0f} | {stop:.0f} | "
          f"{s['outcome']}/{s['gross_r']:+.2f}/{s['fee_r']:.3f}/{s['net_r']:+.3f} | {out}/{gross:+.2f}/{fee_r:.3f}/{gross-fee_r:+.3f} | {'yes' if m else 'NO'} |")
print(f"\nsample match {ok}/{len(sample)}")
# stop-distance geometry
dists = [RT_BPS / e["sim"]["fee_r"] for e in fast]
print(f"FAST stop distance bps: median {st.median(dists):.1f}, p25 {sorted(dists)[len(dists)//4]:.1f}, p75 {sorted(dists)[3*len(dists)//4]:.1f}")
# hour-of-day split (UTC) of gate-pass FAST net R: session effect
byh = {}
for e in fast:
    if e["sim"]["fee_r"] <= 0.25:
        h = dt.datetime.fromtimestamp(e["t"]/1000, dt.UTC).hour
        byh.setdefault(h // 4 * 4, []).append(e["sim"]["net_r"])
print("\n| UTC 4h block | n | net R gate-pass |\n|---|---|---|")
for h in sorted(byh):
    print(f"| {h:02d}-{h+4:02d} | {len(byh[h])} | {st.mean(byh[h]):+.3f} |")
# with-trend split already in report; add target 2R counterfactual (Fabio: low win rate, high RR)
for rr in (2.0, 3.0):
    nn = []
    for e in fast:
        if e["sim"]["fee_r"] > 0.25:
            continue
        i = idx[e["t"]]; entry = bars[i]["c"]; dist = RT_BPS / e["sim"]["fee_r"] / 1e4 * entry; stop = entry - e["dir"] * dist
        target = entry + e["dir"] * rr * dist
        gross = None
        fut = bars[i + 1:i + 1 + H]
        for b in fut:
            if (b["l"] <= stop if e["dir"] > 0 else b["h"] >= stop):
                gross = -1.0; break
            if (b["h"] >= target if e["dir"] > 0 else b["l"] <= target):
                gross = rr; break
        if gross is None:
            gross = (fut[-1]["c"] - entry) * e["dir"] / dist
        nn.append(gross - e["sim"]["fee_r"])
    print(f"target {rr:.0f}R, H=24, gate-pass: n={len(nn)} net={st.mean(nn):+.3f} SE={st.stdev(nn)/len(nn)**0.5:.3f}")
