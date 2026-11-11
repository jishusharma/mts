"""Shape A of PRE_REG.md: acceptance continuation in the D+W bias direction, by session, with a random-entry control.

Frozen by PRE_REG.md (commit precedes every result). Reuses census_session_ladder (loaded by path, not copied): load_5m, to_15m,
ladder_maps, levels via auction_census.build_levels. Costs only from backtest/fees.py. Run:
  python with_trend_census.py <cache_dir_of_5m_json> [out_dir]
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import math
import random
import statistics as st
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TF_DIR = HERE.parent / "tom_fabio_course_correction_2026-11-07"
_s = importlib.util.spec_from_file_location("census_session_ladder", TF_DIR / "census_session_ladder.py")
csl = importlib.util.module_from_spec(_s)
_s.loader.exec_module(csl)
fees = csl.fees
ax = csl.ax

ACCEPT_BARS = 4           # OURS: 4 closed 15m closes = 1 h acceptance
MIN_STOP = 0.0040         # EDGE_PLAN size rule: stop >= 40 bp
MIN_TARGET = 0.0062       # EDGE_PLAN size rule: 500 USD at 80,000 = 62 bp
RR = 2.0
HORIZON = 96              # 24 h of 15m bars
DRAWS = 200
SEED = 1111
BIN_FRAC = 50 / 75000     # as the census
BLOCKS = ("asia", "london", "ny", "late")


def block_of(t_ms):
    h = dt.datetime.fromtimestamp(t_ms / 1000, dt.UTC).hour
    return "asia" if h < 7 else "london" if h < 13 else "ny" if h < 21 else "late"


def cost_frac(model, exit_kind):
    f = fees.FEES_ALL_TAKER if model == "T" else fees.FEES_DERIBIT
    return f["entry"] + f[exit_kind] + fees.SLIPPAGE_RT_S13


def simulate_trade(d, entry, stop, bars):
    """bars = the bars AFTER the entry bar. Same-bar stop+target: stop first. Time stop: close of bar HORIZON.
    Returns a dict, or None when the stop is under MIN_STOP or there are no later bars."""
    stop_frac = abs(entry - stop) / entry
    if stop_frac < MIN_STOP:
        return None
    target = entry + d * RR * abs(entry - stop)
    assert abs(target - entry) / entry >= MIN_TARGET - 1e-12  # 2 x 40 bp = 80 bp >= 62 bp
    kind, exit_px = "time", None
    seg = bars[:HORIZON]
    for b in seg:
        hit_stop = b["l"] <= stop if d > 0 else b["h"] >= stop
        hit_tgt = b["h"] >= target if d > 0 else b["l"] <= target
        if hit_stop:
            kind, exit_px = "stop", stop
            break
        if hit_tgt:
            kind, exit_px = "target", target
            break
    if exit_px is None:
        if not seg:
            return None
        exit_px = seg[-1]["c"]
    gross = d * (exit_px - entry) / entry
    ek = {"stop": "stop", "target": "target", "time": "timeout"}[kind]
    return dict(kind=kind, gross_frac=gross, stop_frac=stop_frac, gross_r=gross / stop_frac,
                net_r_T=(gross - cost_frac("T", ek)) / stop_frac, net_r_D=(gross - cost_frac("D", ek)) / stop_frac)


def find_events(day_bars, day, lv, bias_ok):
    """First 4-in-a-row closes beyond prior-day VAH (long) / VAL (short) per direction per UTC day.
    Returns [(direction, start_idx, entry_idx, stop)] with indices into day_bars[day]."""
    bars = day_bars.get(day, [])
    levels = {n: p for n, p, _ in lv}
    out = []
    for d, name in ((1, "VAH"), (-1, "VAL")):
        if name not in levels or not bias_ok(d):
            continue
        lvl = levels[name]
        for j in range(0, len(bars) - ACCEPT_BARS + 1):
            win = bars[j:j + ACCEPT_BARS]
            if block_of(win[0]["t"]) == "late":
                continue
            if all((b["c"] > lvl) if d > 0 else (b["c"] < lvl) for b in win):
                stop = min(lvl, min(b["l"] for b in win)) if d > 0 else max(lvl, max(b["h"] for b in win))
                out.append((d, j, j + ACCEPT_BARS - 1, stop))
                break
    return out


def bias_fn(lad):
    return lambda d: lad.get("D") == d and lad.get("W") == d


def mean_se(xs):
    n = len(xs)
    if n == 0:
        return float("nan"), float("nan")
    m = sum(xs) / n
    return m, (st.stdev(xs) / math.sqrt(n) if n > 1 else float("nan"))


def run(bars15, ladder, start_day, end_day):
    day_bars, pos = {}, {}
    for i, b in enumerate(bars15):
        dd = ax.day_of(b["t"])
        day_bars.setdefault(dd, []).append(b)
        pos.setdefault(dd, i)
    rng = random.Random(SEED)
    events, skipped = [], 0
    day = start_day
    while day <= end_day:
        if day in day_bars:
            lv = ax.build_levels(day_bars, day, BIN_FRAC)
            lad = ladder.get(day, {})
            if lv and "D" in lad and "W" in lad:
                for d, j, k, stop in find_events(day_bars, day, lv, bias_fn(lad)):
                    g = pos[day] + k
                    entry = bars15[g]["c"]
                    res = simulate_trade(d, entry, stop, bars15[g + 1:g + 1 + HORIZON])
                    if res is None:
                        skipped += 1
                        continue
                    blk = block_of(bars15[g]["t"])
                    pool = [pos[day] + x for x, bb in enumerate(day_bars[day]) if block_of(bb["t"]) == blk]
                    ctrl = []
                    for _ in range(DRAWS):
                        gi = rng.choice(pool)
                        e2 = bars15[gi]["c"]
                        dist = res["stop_frac"] * e2
                        r2 = simulate_trade(d, e2, e2 - d * dist, bars15[gi + 1:gi + 1 + HORIZON])
                        ctrl.append(r2["net_r_T"] if r2 else None)
                    events.append(dict(day=str(day), dir=d, block=blk, year=day.year, regime=lad.get("regime"),
                                       M=lad.get("M"), stop_bp=res["stop_frac"] * 1e4, ctrl=ctrl,
                                       range_1024=day >= dt.date(2026, 10, 24), **res))
        day += dt.timedelta(days=1)
    return events, skipped


def cell(evs):
    if not evs:
        return dict(n=0)
    T = [e["net_r_T"] for e in evs]
    D = [e["net_r_D"] for e in evs]
    G = [e["gross_r"] for e in evs]
    mT, seT = mean_se(T)
    mD, _ = mean_se(D)
    ctrl_means = []
    for k in range(DRAWS):
        xs = [e["ctrl"][k] for e in evs if e["ctrl"][k] is not None]
        if xs:
            ctrl_means.append(sum(xs) / len(xs))
    frac = (sum(1 for c in ctrl_means if c >= mT) / len(ctrl_means)) if ctrl_means else float("nan")
    return dict(n=len(evs), gross=sum(G) / len(G), net_T=mT, se_T=seT, net_D=mD,
                win=sum(e["kind"] == "target" for e in evs) / len(evs),
                ctrl_mean=sum(ctrl_means) / len(ctrl_means) if ctrl_means else float("nan"), ctrl_ge=frac)


def verdict(c):
    if c["n"] < 100:
        return "INCONCLUSIVE (n<100)"
    ok = c["net_T"] > 0 and c["net_T"] > 2 * c["se_T"] and c["net_D"] > 0 and c["ctrl_ge"] <= 0.05
    return "EDGE-CANDIDATE" if ok else "FAIL"


def fmt(c):
    if c["n"] == 0:
        return "| 0 | | | | | | | | |"
    return (f"| {c['n']} | {c['gross']:+.3f} | {c['net_T']:+.3f} | {c['se_T']:.3f} | {c['net_D']:+.3f} | {c['win'] * 100:.0f} % "
            f"| {c['ctrl_mean']:+.3f} | {c['ctrl_ge'] * 100:.0f} % | {verdict(c)} |")


def report(events, skipped):
    lines = ["| group | n | gross R | net R taker | SE | net R Deribit | win | control net R | control >= event | verdict |",
             "|---|---|---|---|---|---|---|---|---|---|"]

    def row(label, evs):
        lines.append(f"| {label} " + fmt(cell(evs)))

    row("ALL", events)
    for b in BLOCKS:
        row(f"session {b}", [e for e in events if e["block"] == b])
    for d, nm in ((1, "long"), (-1, "short")):
        row(f"direction {nm}", [e for e in events if e["dir"] == d])
    for y in sorted({e["year"] for e in events}):
        row(f"year {y}", [e for e in events if e["year"] == y])
    for r in ("bull", "range", "bear"):
        row(f"regime {r}", [e for e in events if e["regime"] == r])
    row("range_1024 (reported, not judged)", [e for e in events if e["range_1024"]])
    med = st.median([e["stop_bp"] for e in events]) if events else float("nan")
    return "\n".join(lines) + f"\n\nSkipped for stop < 40 bp: {skipped}. Median stop {med:.0f} bp."


def main(cache, out_dir=HERE):
    b5 = csl.load_5m(cache)
    ladder = csl.ladder_maps(b5)
    b15 = csl.to_15m(b5)
    end = ax.day_of(b15[-1]["t"]) - dt.timedelta(days=1)
    start = dt.date(2019, 11, 8)
    events, skipped = run(b15, ladder, start, end)
    json.dump([{k: v for k, v in e.items() if k != "ctrl"} for e in events], open(Path(out_dir) / "result_a.json", "w"))
    mix = csl.regime_mix(ladder, start, end)
    text = (f"# Shape A result (PRE_REG.md)\n\nWindow {start}..{end}, 15m bars {len(b15)}. "
            f"Regime mix: window days by D SMA20 +-2 % (OURS), {mix}\n\n" + report(events, skipped))
    (Path(out_dir) / "RESULT_A.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else HERE)
