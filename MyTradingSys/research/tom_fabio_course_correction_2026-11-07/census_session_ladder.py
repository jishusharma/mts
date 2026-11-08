"""Card census-5m-15m-7y-session-ladder-1109: the traders' frame Argon never ran.
5m and 15m BTC bars (data.binance.vision, census_fetch_mirror.py), FAST_REJECTION events from the unmodified classifier
(auction_context.classify_level_interaction, delta = taker buy - taker sell now in the bars), in session blocks, HTF-ladder
aligned, targets at volume nodes, four management variants, fee-net under two fee models. Diagnostic only (phase-first).

Parameter labels (SOURCED = file:line, OURS = chosen here):
  levels VAL/VAH/PDL/PDH/PWL/PWH from the prior UTC day / week   auction_census.build_levels (OURS, as the 1h census)
  classifier thresholds                                           auction_context.py labels (rel_vol 2.0 OURS etc.)
  sessions LON 09:00-12:00 Europe/Berlin (Tom: DAX cash 9-12, TOM_VERBATIM 5Ljfwvtktek_raw.txt:7 SOURCED in kind, DST-aware = OURS)
           NY  09:30-12:30 America/New_York (Fabio NY only, Pz8f0wWW12M:655 SOURCED in kind; 3 h length OURS)
  ladder D = prior-day close vs SMA20 daily; W = last full ISO-week close vs SMA10 weekly; M = last full month close vs SMA6 monthly
           (idea SOURCED Tom TOM-053; every length OURS). align_n = count of D/W/M that agree with the trade direction.
           HEADLINE gate: align_n >= 2 (OURS, fixed before the run)
  stop = sweep extreme, no buffer (TOM-072, Is1HvdfQm5c:144 SOURCED in kind)
  targets: nodes = prior-day POC, VAH, VAL, HVNs (compute_volume_profile) + PDH/PDL/PWH/PWL beyond entry; T1 = nearest node >= 1.5R
           (Tom TOM-018 next high-volume price SOURCED; 1.5R floor OURS); T2 = next node. No node >= 1.5R: node variants skipped.
  variants: B1R fixed +-1R (the old census shape) | NODE (T1, no mgmt) | NODE_BE (BE once +1R traded, T1)
            HALF_BE (BE at +1R, half off at T1, rest to T2 else horizon; Fabio BE fZlNGWvd2Ko:43-61, Tom TOM-014 SOURCED in kind, split OURS)
            TRAIL (BE at +1R then stop trails 1R behind best price, no target; Fabio aggressive trail SOURCED in kind, 1R OURS)
  horizon 8 h (5m: 96 bars, 15m: 32 bars), cooldown 4 h per level, window 60 bars  OURS
  fees: model T = taker both legs 5 bps/side (fees.py:32 DERIBIT_TAKER); model D = FEES_DERIBIT (fees.py:48: entry+target maker 0,
        stop/BE-stop/timeout taker 5 bps; maker entry assumed filled at the signal close = optimistic);
        +2 bps RT slippage on both (FORMULAS s13). Fee gate fee_r(10 bps RT) <= 0.25 R SOURCED d-stops-follow-trade-1106.
  Bars: stop wins a same-bar tie; BE/trail take effect the bar after they are earned; T2 only on a later bar than T1.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import math
import statistics as st
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent


def _load(name):
    s = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


ac = _load("auction_context")
ax = _load("auction_census")
_fs = importlib.util.spec_from_file_location("mts_fees", HERE.parents[2] / "MyTradingSys" / "backtest" / "fees.py")
fees = importlib.util.module_from_spec(_fs)
_fs.loader.exec_module(fees)

BERLIN, NY = ZoneInfo("Europe/Berlin"), ZoneInfo("America/New_York")
MIN_NODE_R = 1.5
SLIP_BPS = 2.0
TAKER_SIDE_BPS = fees.DERIBIT_TAKER * 1e4  # 5 bps per side, fees.py:32
GATE_FEE_R = 0.25
BIBLE_PHASE_START = dt.datetime(2026, 10, 24, tzinfo=dt.UTC)
VARIANTS = ("B1R", "NODE", "NODE_BE", "HALF_BE", "TRAIL")
TF = {"5m": dict(horizon=96, cooldown=48), "15m": dict(horizon=32, cooldown=16)}


# ------------------------------------------------------------------ data
def load_5m(cache):
    rows = []
    for p in sorted(Path(cache).glob("20*.json")):
        rows += json.load(open(p))["rows"]
    rows.sort()
    out, last = [], None
    for t, o, h, l, c, v, tb in rows:
        if t == last:
            continue
        last = t
        out.append(dict(t=t, o=o, h=h, l=l, c=c, v=v, delta=2.0 * tb - v))
    return out


def to_15m(b5):
    out, cur = [], None
    for b in b5:
        k = b["t"] // 900000
        if cur is None or cur["k"] != k:
            if cur and cur["n"] == 3:
                out.append(cur)
            cur = dict(k=k, n=0, t=k * 900000, o=b["o"], h=b["h"], l=b["l"], c=b["c"], v=0.0, delta=0.0)
        cur["n"] += 1
        cur["h"], cur["l"], cur["c"] = max(cur["h"], b["h"]), min(cur["l"], b["l"]), b["c"]
        cur["v"] += b["v"]
        cur["delta"] += b["delta"]
    if cur and cur["n"] == 3:
        out.append(cur)
    return out


def ladder_maps(b5):
    """date -> dict(D, W, M = +1/-1, regime) known at the start of that date (prior complete day / week / month)."""
    days = {}
    for b in b5:
        days[ax.day_of(b["t"])] = b["c"]  # last 5m close of the day
    dd = sorted(days)
    dclose = [days[d] for d in dd]
    wk, mo = {}, {}
    for d in dd:
        wk[d.isocalendar()[:2]] = days[d]
        mo[(d.year, d.month)] = days[d]
    wkeys, mkeys = sorted(wk), sorted(mo)
    widx = {k: i for i, k in enumerate(wkeys)}
    midx = {k: i for i, k in enumerate(mkeys)}
    wcl, mcl = [wk[k] for k in wkeys], [mo[k] for k in mkeys]
    out = {}
    for i, d in enumerate(dd):
        e = {}
        if i >= 19:
            sma = sum(dclose[i - 19:i + 1]) / 20.0
            e["D"] = 1 if dclose[i] > sma else -1
            e["regime"] = "bull" if dclose[i] > sma * 1.02 else "bear" if dclose[i] < sma * 0.98 else "range"
        out[d + dt.timedelta(days=1)] = e
    for nxt, e in out.items():
        monday = nxt - dt.timedelta(days=nxt.weekday())
        prevw = (monday - dt.timedelta(days=1)).isocalendar()[:2]
        if prevw in widx and widx[prevw] >= 9:
            j = widx[prevw]
            e["W"] = 1 if wcl[j] > sum(wcl[j - 9:j + 1]) / 10.0 else -1
        first = nxt.replace(day=1)
        pm = (first - dt.timedelta(days=1))
        pk = (pm.year, pm.month)
        if pk in midx and midx[pk] >= 5:
            j = midx[pk]
            e["M"] = 1 if mcl[j] > sum(mcl[j - 5:j + 1]) / 6.0 else -1
    return out


def session_of(t_ms):
    u = dt.datetime.fromtimestamp(t_ms / 1000, dt.UTC)
    b, n = u.astimezone(BERLIN), u.astimezone(NY)
    if b.weekday() < 5 and dt.time(9, 0) <= b.time() < dt.time(12, 0):
        return "LON"
    if n.weekday() < 5 and dt.time(9, 30) <= n.time() < dt.time(12, 30):
        return "NY"
    return "OTHER"


# ------------------------------------------------------------------ levels and nodes
def build_nodes(day_bars, day, bin_frac):
    """Return (levels [(name, price, side)], node prices) for UTC `day` from bars before it, or ([], [])."""
    lv = ax.build_levels(day_bars, day, bin_frac)
    if not lv:
        return [], []
    prev = day_bars[day - dt.timedelta(days=1)]
    close = prev[-1]["c"]
    prof = ac.compute_volume_profile(prev, bin_size=max(1.0, round(close * bin_frac)), spread_range=True)
    nodes = [p for _, p, _ in lv]
    if prof:
        nodes += [float(prof["poc"]), *[float(x) for x in prof["hvns"]]]
    return lv, sorted(set(nodes))


# ------------------------------------------------------------------ trade simulation
def _better(d, a, b):
    """True when price a is a more protective stop than b for direction d."""
    return a > b if d > 0 else a < b


def run_trade(d, entry, stop, fut, variant, t1=None, t2=None):
    """Legs [(fraction, price, kind)] kind in target/stop/time, or None when the variant does not apply."""
    dist = (entry - stop) * d
    if dist <= 0 or not fut:
        return None
    if variant == "B1R":
        t1, t2 = entry + d * dist, None
    if variant in ("NODE", "NODE_BE", "HALF_BE") and t1 is None:
        return None
    if variant == "TRAIL":
        t1 = t2 = None
    half = variant == "HALF_BE"
    be = variant in ("NODE_BE", "HALF_BE", "TRAIL")
    trail = variant == "TRAIL"
    sp, rem, legs, best, t1_done, be_on = stop, 1.0, [], entry, False, False
    for b in fut:
        hi, lo = b["h"], b["l"]
        if (d > 0 and lo <= sp) or (d < 0 and hi >= sp):
            legs.append((rem, sp, "stop"))
            return legs
        fav = hi if d > 0 else lo
        if t1_done and t2 is not None and ((d > 0 and fav >= t2) or (d < 0 and fav <= t2)):
            legs.append((rem, t2, "target"))
            return legs
        if not t1_done and t1 is not None and ((d > 0 and fav >= t1) or (d < 0 and fav <= t1)):
            if half:
                legs.append((0.5, t1, "target"))
                rem, t1_done, be_on = 0.5, True, True
                if _better(d, entry, sp):
                    sp = entry
            else:
                legs.append((rem, t1, "target"))
                return legs
        best = max(best, fav) if d > 0 else min(best, fav)
        if be and (best - entry) * d >= dist:
            be_on = True
            if _better(d, entry, sp):
                sp = entry
        if trail and be_on:
            ts = best - d * dist
            if _better(d, ts, sp):
                sp = ts
    legs.append((rem, fut[-1]["c"], "time"))
    return legs


def score(d, entry, stop, legs):
    """-> [gross_r, net_T, net_D, last leg kind] with fees in R of the initial risk."""
    dist = (entry - stop) * d
    gross = sum(f * (p - entry) * d / dist for f, p, _ in legs)
    sbps = dist / entry * 1e4
    exit_t = sum(f * TAKER_SIDE_BPS for f, _, _ in legs)
    exit_d = sum(f * (TAKER_SIDE_BPS if k != "target" else 0.0) for f, _, k in legs)
    fee_t = (TAKER_SIDE_BPS + exit_t + SLIP_BPS) / sbps
    fee_d = (0.0 + exit_d + SLIP_BPS) / sbps
    return [gross, gross - fee_t, gross - fee_d, legs[-1][2]]


# ------------------------------------------------------------------ census
def run(bars, tf, ladder, start_day, end_day, count_only=False, prefilter=True):
    cfg = TF[tf]
    day_bars, by_day = {}, {}
    for i, b in enumerate(bars):
        dd = ax.day_of(b["t"])
        by_day.setdefault(dd, []).append(i)
        day_bars.setdefault(dd, []).append(b)
    events, day = [], start_day
    bin_frac = 50 / 75000
    while day <= end_day:
        idxs = by_day.get(day)
        lv, nodes = build_nodes(day_bars, day, bin_frac) if idxs else ([], [])
        last = {n: -10 ** 9 for n, _, _ in lv}
        lad = ladder.get(day, {})
        for t in (idxs or []):
            if t < ax.WINDOW:
                continue
            win = bars[t - ax.WINDOW + 1:t + 1]
            for name, price, side in lv:
                if t - last[name] < cfg["cooldown"]:
                    continue
                ref = win[-1 - ax.SETUP_BACK]["c"]
                if (side == "support" and ref <= price) or (side == "resistance" and ref >= price):
                    continue
                if prefilter and ((side == "support" and min(b["l"] for b in win[-8:]) > price)
                                  or (side == "resistance" and max(b["h"] for b in win[-8:]) < price)):
                    continue  # speed prefilter: FAST_REJECTION needs a probe beyond the level in the recent bars (checked on a sample)
                r = ac.classify_level_interaction(win, price, side)
                if r.get("verdict") != "FAST_REJECTION":
                    continue
                last[name] = t
                d = 1 if side == "support" else -1
                entry, stop = bars[t]["c"], r["sweep_extreme"]
                dist = (entry - stop) * d
                if dist <= 0:
                    continue
                u = dt.datetime.fromtimestamp(bars[t]["t"] / 1000, dt.UTC)
                ev = dict(tf=tf, t=bars[t]["t"], level=name, dir=d, session=session_of(bars[t]["t"]),
                          regime=lad.get("regime", "n/a"), sbps=dist / entry * 1e4,
                          phase="bible" if u >= BIBLE_PHASE_START else "pre", year=u.year)
                keys = [k for k in "DWM" if k in lad]
                ev["align_n"] = sum(1 for k in keys if lad[k] == d) if len(keys) == 3 else None
                ev["delta_opp"] = bool(bars[t]["delta"] * d < 0)  # delta of the signal bar points AGAINST the trade side (long with net selling)
                if not count_only:
                    fut = bars[t + 1:t + 1 + cfg["horizon"]]
                    beyond = sorted(n for n in nodes if (n - entry) * d >= MIN_NODE_R * dist * 1.0)
                    beyond = beyond if d > 0 else beyond[::-1]
                    t1 = beyond[0] if beyond else None
                    t2 = beyond[1] if len(beyond) > 1 else None
                    ev["has_node"] = t1 is not None
                    ev["res"] = {}
                    for v in VARIANTS:
                        legs = run_trade(d, entry, stop, fut, v, t1, t2)
                        if legs:
                            ev["res"][v] = score(d, entry, stop, legs)
                events.append(ev)
        day += dt.timedelta(days=1)
    return events


# ------------------------------------------------------------------ report
def cell(evs, v, idx):
    xs = [e["res"][v][idx] for e in evs if "res" in e and v in e["res"]]
    if not xs:
        return "-"
    se = st.stdev(xs) / math.sqrt(len(xs)) if len(xs) > 1 else float("nan")
    return f"{st.mean(xs):+.3f}+-{se:.3f} (n={len(xs)})"


def table(evs, groups, label, idx=2, variants=VARIANTS):
    out = [f"| {label} | events | " + " | ".join(variants) + " |", "|---|---|" + "---|" * len(variants)]
    for name, f in groups:
        sub = [e for e in evs if f(e)]
        out.append(f"| {name} | {len(sub)} | " + " | ".join(cell(sub, v, idx) for v in variants) + " |")
    return "\n".join(out)


def report(events):
    o = []
    for tf in ("5m", "15m"):
        ev = [e for e in events if e["tf"] == tf]
        head = [e for e in ev if e["session"] != "OTHER" and (e["align_n"] or 0) >= 2]
        o.append(f"## {tf}: {len(ev)} FAST_REJECTION events; in-session {sum(e['session'] != 'OTHER' for e in ev)}; "
                 f"headline set (LON/NY, align_n>=2) {len(head)}\n")
        for idx, nm in ((2, "FEES_DERIBIT model D, net R"), (1, "taker model T, net R"), (0, "gross R")):
            o.append(f"### {tf} HEADLINE set ({nm}); NODE variants need a node >= 1.5R\n")
            o.append(table(head, [("headline", lambda e: True)], "set", idx) + "\n")
        o.append(f"### {tf} by session block (all ladder states; model D net R)\n")
        o.append(table(ev, [(s, lambda e, s=s: e["session"] == s) for s in ("LON", "NY", "OTHER")], "session") + "\n")
        o.append(f"### {tf} by session block x ladder gate (align_n>=2), model D net R\n")
        gs = []
        for s in ("LON", "NY", "OTHER"):
            gs += [(f"{s} gate", lambda e, s=s: e["session"] == s and (e["align_n"] or 0) >= 2),
                   (f"{s} no-gate", lambda e, s=s: e["session"] == s and e["align_n"] is not None and e["align_n"] < 2)]
        o.append(table(ev, gs, "block") + "\n")
        o.append(f"### {tf} by align_n (0..3), in-session, model D net R\n")
        o.append(table(ev, [(f"align_n={k}", lambda e, k=k: e["session"] != "OTHER" and e["align_n"] == k) for k in range(4)], "ladder") + "\n")
        o.append(f"### {tf} headline set by regime (D SMA20 +-2%), model D net R\n")
        o.append(table(head, [(r, lambda e, r=r: e["regime"] == r) for r in ("bull", "bear", "range")], "regime") + "\n")
        o.append(f"### {tf} headline set by year, model D net R\n")
        o.append(table(head, [(str(y), lambda e, y=y: e["year"] == y) for y in range(2019, 2027)], "year",
                       variants=("B1R", "NODE_BE", "HALF_BE", "TRAIL")) + "\n")
        o.append(f"### {tf} Bible phase (range 75.4-80.9k since 2026-10-24) vs rest, in-session (any ladder), model D net R\n")
        o.append(table([e for e in ev if e["session"] != "OTHER"], [("bible phase", lambda e: e["phase"] == "bible"),
                                                                    ("rest", lambda e: e["phase"] == "pre")], "phase") + "\n")
        o.append(f"### {tf} headline set by fee gate (10 bps RT / stop bps <= 0.25 R, i.e. stop >= 40 bps), model D net R\n")
        o.append(table(head, [("gate-pass", lambda e: 10.0 / e["sbps"] <= GATE_FEE_R),
                              ("gate-fail", lambda e: 10.0 / e["sbps"] > GATE_FEE_R)], "fee gate") + "\n")
        o.append(f"### {tf} headline set by delta at the signal bar, model D net R\n")
        o.append(table(head, [("delta against trade side (absorbed flow)", lambda e: e["delta_opp"]),
                              ("delta with trade side or zero", lambda e: not e["delta_opp"])], "delta") + "\n")
        sb = sorted(e["sbps"] for e in head)
        if sb:
            o.append(f"Stop bps in headline set: p25 {sb[len(sb)//4]:.1f}, median {sb[len(sb)//2]:.1f}, p75 {sb[3*len(sb)//4]:.1f}; "
                     f"with node {sum(e.get('has_node', False) for e in head)}/{len(head)}\n")
    return "\n".join(o)


def regime_mix(ladder, a, b):
    ds = [d for d in sorted(ladder) if a <= d <= b and "regime" in ladder[d]]
    return " / ".join(f"{r} {sum(1 for d in ds if ladder[d]['regime'] == r)}/{len(ds)}" for r in ("bull", "bear", "range"))


def main(cache, out_json, count_only=False, report_only=False):
    if report_only:  # re-render the tables from a saved event list (no recompute)
        print(report(json.load(open(out_json))))
        return
    b5 = load_5m(cache)
    ladder = ladder_maps(b5)
    end = ax.day_of(b5[-1]["t"]) - dt.timedelta(days=1)
    start = dt.date(2019, 11, 8)
    print(f"# 5m bars {len(b5)} {dt.datetime.fromtimestamp(b5[0]['t']/1000, dt.UTC):%Y-%m-%d} .. "
          f"{dt.datetime.fromtimestamp(b5[-1]['t']/1000, dt.UTC):%Y-%m-%d %H:%M}; window {start}..{end}", flush=True)
    events = []
    for tf in ("5m", "15m"):
        bars = b5 if tf == "5m" else to_15m(b5)
        ev = run(bars, tf, ladder, start, end, count_only)
        print(f"# {tf}: bars {len(bars)} events {len(ev)}", flush=True)
        events += ev
    json.dump(events, open(out_json, "w"))
    if count_only:
        for tf in TF:
            ev = [e for e in events if e["tf"] == tf]
            head = [e for e in ev if e["session"] != "OTHER" and (e["align_n"] or 0) >= 2]
            print(tf, "events", len(ev), "in-session", sum(e["session"] != "OTHER" for e in ev), "headline", len(head))
        return
    print("\nRegime mix (window days, D SMA20 +-2%, OURS): " + regime_mix(ladder, start, end) + "\n")
    print(report(events))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], "--count-only" in sys.argv, "--report-only" in sys.argv)
