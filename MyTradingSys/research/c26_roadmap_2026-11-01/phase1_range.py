"""C26 Candidate C (martingale short inside a range): the measure-first step on the RECENT design window (SEEN; never a test).

Q1 the range: after a held high is taken (lows mirrored), how far beyond H1 does price go BEFORE it comes back, and how often
   does it not come back at all within 24h (a range break)? For candidate range tops X the grid shows the share of take-outs a
   ladder with its one stop at H1 + X would lose, and how many of those came back to L1 anyway (false stops).
Q2 the ladder's fuel: RSI(14) bearish divergence signals on 1m / 2m / 3m / 5m bars between the take-out and the exit: how many
   legs a divergence-triggered ladder would have had, when the first one came and how far above H1 it sold.
Definitions (all OURS): events and bars = phase1_recent.py (C26 15m, Binance spot). Excursion window = the take-out bar .. exit,
   exit = the first 15m bar whose low reaches L1, else 96 bars (24h) after the take-out, else the end of the data.
   excursion = highest high in the window, % above H1. Divergence on TF bars: pivot high p = highest high of +-K bars (K=3),
   known at the close of bar p+K; prior pivot q within LB=60 TF bars with high[q] < high[p] and RSI14[q] > RSI14[p]. A signal
   is counted at its confirmation close if that falls after the 1m bar that broke H1 and before the exit, and high[p] > H1.
Usage: python phase1_range.py <repo> <cache_dir> [--until 2026-11-01T07:45] [--sim-json FILE] > PHASE1_RANGE.md
   (cache_dir holds btc15m_recent.json and btc1m_recent.json, public klines, never committed; fetch_1m.py fills the 1m file)
"""
import importlib.util, json, os, sys
from bisect import bisect_left, bisect_right

HERE = os.path.dirname(os.path.abspath(__file__))
P = None  # phase1_recent, loaded by main(): it reads sys.argv[1:] (repo, cache, --until, --sim-json) and fetches bars


def _load():
    global P
    spec = importlib.util.spec_from_file_location("phase1_recent", os.path.join(HERE, "phase1_recent.py"))
    P = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(P)

K, LB, HOLD = 3, 60, 96  # pivot half-width (TF bars), divergence look-back (TF bars), 24h hold in 15m bars; OURS
TFS = (1, 2, 3, 5)
TOPS = (0.3, 0.5, 0.65, 0.8, 1.0, 1.5, 2.0)
GROUPS = (("UP", "H"), ("UP", "L"), ("DOWN", "H"), ("DOWN", "L"))


def bearish_divs(H, R):
    """Indices p of pivot highs (+-K) with a prior pivot q (p-q <= LB) lower in price and higher in RSI; each is known at
    the close of bar p+K. Pure function of the mirrored high series H and RSI series R (None = warm-up)."""
    piv, out = [], []
    for p in range(K, len(H) - K):
        if H[p] != max(H[p - K:p + K + 1]):
            continue
        if R[p] is not None and any(R[q] is not None and H[q] < H[p] and R[q] > R[p] for q in piv if p - q <= LB):
            out.append(p)
        piv.append(p)
    return out


def tf_bars(m1, tf):
    """Aggregate 1m rows [t, o, h, l, c, v, taker_buy] into tf-minute bars aligned to the epoch: [t_open, h, l, c]."""
    out, span = [], tf * 60000
    for r in m1:
        b = r[0] // span * span
        if out and out[-1][0] == b:
            o = out[-1]; o[1] = max(o[1], r[2]); o[2] = min(o[2], r[3]); o[3] = r[4]
        else:
            out.append([b, r[2], r[3], r[4]])
    return out


def excursion(e):
    """Window take-out .. exit on the mirrored 15m series; returns dict with exc (% above H1), bars to the extreme, exit kind."""
    s = 1 if e["side"] == "H" else -1
    Hs = [h if s > 0 else -l for h, l in zip(P.H, P.L)]
    Ls = [l if s > 0 else -h for h, l in zip(P.H, P.L)]
    Cs = [c * s for c in P.C]
    lvl, l1, take = e["h1"] * s, e["l1"] * s, e["_take"]
    end = min(P.N - 1, take + HOLD)
    reach = next((m for m in range(take, end + 1) if Ls[m] < l1), None)
    back = next((m for m in range(take, end + 1) if Cs[m] < lvl), None)
    exit_ = reach if reach is not None else end
    seg = Hs[take:exit_ + 1]
    k = max(range(len(seg)), key=seg.__getitem__)
    return dict(exc=(seg[k] - lvl) / abs(lvl) * 100, exc_bars=k, reach=reach is not None, back=back is not None,
                exc_to_back=(max(Hs[take:back + 1]) - lvl) / abs(lvl) * 100 if back is not None else None,
                exit_i=exit_, cut=exit_ == P.N - 1 and reach is None)


def div_counts(e, x, bars_by_tf, rsi_by_tf, m1):
    """Per TF: divergence signals inside the excursion window and above H1; first signal's delay (min) and level (% above H1)."""
    s = 1 if e["side"] == "H" else -1
    lvl = e["h1"] * s
    t0, t1 = P.T[e["_take"]], P.T[x["exit_i"]] + P.TF
    k0 = bisect_left([r[0] for r in m1], t0)
    broke = next((r[0] + 60000 for r in m1[k0:] if r[0] < t0 + P.TF and (r[2] if s > 0 else -r[3]) > lvl), None)
    if broke is None:  # 1m data missing for this bar: fall back to the 15m bar close
        broke = t0 + P.TF
    out = {}
    for tf in TFS:
        bars, divs = bars_by_tf[tf], rsi_by_tf[tf]
        Ht = [b[1] if s > 0 else -b[2] for b in bars]
        hits = [p for p in divs[s] if broke <= bars[p + K][0] + tf * 60000 < t1 and Ht[p] > lvl]
        first = hits[0] if hits else None
        out[tf] = dict(n=len(hits), first_min=(bars[first + K][0] + tf * 60000 - broke) / 60000 if first is not None else None,
                       first_lvl=(Ht[first] - lvl) / abs(lvl) * 100 if first is not None else None)
    return out


def table(cols, rows):
    return "\n".join(["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)] + ["| " + " | ".join(r) + " |" for r in rows])


def main():
    _load()
    ev = [e for e in P.run(1) + P.run(-1) if e["_take"] is not None]
    for e in ev:
        e["_x"] = excursion(e)
    m1_path = os.path.join(P.CACHE, "btc1m_recent.json")
    m1 = json.load(open(m1_path)) if os.path.exists(m1_path) else []
    if P.UNTIL:
        m1 = [r for r in m1 if r[0] + 60000 <= P.UNTIL]
    bars_by_tf, rsi_by_tf = {}, {}
    if m1:
        for tf in TFS:
            bars = tf_bars(m1, tf)
            bars_by_tf[tf] = bars
            Rh = P.rsi_core([b[3] for b in bars], 14)
            Rl = [100 - r if r is not None else None for r in Rh]
            rsi_by_tf[tf] = {1: bearish_divs([b[1] for b in bars], Rh), -1: bearish_divs([-b[2] for b in bars], Rl)}
        for e in ev:
            e["_d"] = div_counts(e, e["_x"], bars_by_tf, rsi_by_tf, m1)
    f1 = lambda x: "%.2f" % x
    g = lambda ph, sd: [e for e in ev if e["phase"] == ph and e["side"] == sd]
    name = lambda ph, sd: "%s %s" % (ph, "highs" if sd == "H" else "lows")
    # Q1a: excursion before the exit
    rows = []
    for ph, sd in GROUPS:
        G = [e for e in g(ph, sd) if not e["_x"]["cut"]]
        came = [e["_x"]["exc"] for e in G if e["_x"]["reach"]]
        kept = [e["_x"]["exc"] for e in G if not e["_x"]["reach"]]
        tb = [e["_x"]["exc_to_back"] for e in G if e["_x"]["back"]]
        rows.append([name(ph, sd), str(len(G)), "%d (%d %%)" % (len(came), 100 * len(came) / len(G)) if G else "-",
                     "%s / %s / %s" % (f1(P.pctl(came, .5)), f1(P.pctl(came, .8)), f1(max(came))) if came else "-",
                     "%s / %s" % (f1(P.pctl(kept, .5)), f1(P.pctl(kept, .8))) if kept else "-",
                     "%s / %s" % (f1(P.pctl(tb, .5)), f1(P.pctl(tb, .8))) if tb else "-",
                     "%.1f h" % (P.pctl([e["_x"]["exc_bars"] for e in G if e["_x"]["reach"]], .5) / 4) if came else "-"])
    print("## Q1a. How far beyond H1 before it came back (take-outs, 24h window, bars to %s)\n" % P.utc(P.T[-1]).strftime("%Y-%m-%d %H:%M"))
    print(table(["group", "take-outs", "back to L1 <=24h", "excursion of those that came back: median / 80th / max",
                 "excursion of those that did not (24h): median / 80th", "excursion before the 15m close back under H1: median / 80th",
                 "time to the extreme (median, came back)"], rows))
    # Q1b: range-top grid
    rows = []
    for ph, sd in GROUPS:
        G = [e for e in g(ph, sd) if not e["_x"]["cut"]]
        for X in TOPS:
            st = [e for e in G if e["_x"]["exc"] > X]
            ok = [e for e in G if e["_x"]["exc"] <= X]
            rows.append([name(ph, sd), "%.2f %%" % X, "%d/%d (%d %%)" % (len(st), len(G), 100 * len(st) / len(G)) if G else "-",
                         "%d" % sum(1 for e in st if e["_x"]["reach"]), "%d/%d" % (sum(1 for e in ok if e["_x"]["reach"]), len(ok))])
    print("\n## Q1b. Range top X: what a ladder with its one stop at H1 + X would meet\n")
    print(table(["group", "range top X", "stopped out (excursion > X)", "...of which came back to L1 anyway (false stops)",
                 "not stopped: back to L1 / n"], rows))
    # Q2: divergence legs
    if m1:
        rows = []
        for ph, sd in GROUPS:
            G = [e for e in g(ph, sd) if not e["_x"]["cut"]]
            for tf in TFS:
                d = [e["_d"][tf] for e in G]
                has = [x for x in d if x["n"]]
                rows.append([name(ph, sd), "%dm" % tf, "%d/%d (%d %%)" % (len(has), len(d), 100 * len(has) / len(d)) if d else "-",
                             "%s / %s" % (f1(P.pctl([x["n"] for x in has], .5)), str(max(x["n"] for x in has))) if has else "-",
                             "%.0f min" % P.pctl([x["first_min"] for x in has], .5) if has else "-",
                             "%s %% / %s %%" % (f1(P.pctl([x["first_lvl"] for x in has], .5)), f1(P.pctl([x["first_lvl"] for x in has], .8))) if has else "-",
                             "%d/%d" % (sum(1 for e in G if e["_d"][tf]["n"] and e["_x"]["reach"]), len(has)) if has else "-"])
        print("\n## Q2. RSI(14) bearish-divergence legs above H1 between the take-out and the exit (1m bars %s .. %s)\n" % (
            P.utc(m1[0][0]).date(), P.utc(m1[-1][0]).strftime("%Y-%m-%d %H:%M")))
        print(table(["group", "TF", "take-outs with >= 1 signal", "signals per take-out: median / max", "first signal after the break (median)",
                     "first signal above H1: median / 80th", "with a signal: back to L1 / n"], rows))
        print("\nK=%d, LB=%d bars, divergence = pivot high above a prior pivot high (<= LB bars back) with a lower RSI; known %d bars after the pivot." % (K, LB, K))
    else:
        print("\n## Q2. skipped: %s missing" % m1_path)
    print("\nAll numbers OURS, design window (SEEN). cut = exit beyond the data end, excluded.")
    if P.SIM_JSON:
        write_card(ev, bars_by_tf)


def write_card(ev, bars_by_tf):
    g = lambda ph, sd: [e for e in ev if e["phase"] == ph and e["side"] == sd and not e["_x"]["cut"]]
    dn = g("DOWN", "H")
    came = [e for e in dn if e["_x"]["reach"]]
    kept = [e for e in dn if not e["_x"]["reach"]]
    exc_c = [e["_x"]["exc"] for e in came]
    pick = []
    if came:
        pick.append(("worst DOWN high that still came back", "the widest range a ladder had to survive", max(came, key=lambda e: e["_x"]["exc"])))
        pick.append(("typical DOWN high", "median excursion, back to L1", min(came, key=lambda e: abs(e["_x"]["exc"] - P.pctl(exc_c, .5)))))
    if kept:
        pick.append(("DOWN high range break", "never came back to L1 within 24h: the ladder's loss case", max(kept, key=lambda e: e["_x"]["exc"])))
    items = [{"kind": "event", "label": lab, "note": note,
              "svg": P.event_svg(e, P._caption(e) + ", beyond H1 %.2f%%" % e["_x"]["exc"])} for lab, note, e in pick]
    grid = []
    for X in TOPS:
        st = [e for e in dn if e["_x"]["exc"] > X]
        grid.append(["%.2f %%" % X, "%d/%d" % (len(st), len(dn)), str(sum(1 for e in st if e["_x"]["reach"])),
                     "%d/%d" % (sum(1 for e in dn if e["_x"]["exc"] <= X and e["_x"]["reach"]), len(dn) - len(st))])
    legs = []
    for tf in TFS:
        d = [e["_d"][tf] for e in dn if "_d" in e]
        has = [x for x in d if x["n"]]
        legs.append(["%dm" % tf, "%d/%d" % (len(has), len(d)), "%.0f" % P.pctl([x["n"] for x in has], .5) if has else "-",
                     "%.0f min" % P.pctl([x["first_min"] for x in has], .5) if has else "-",
                     "%.2f %%" % P.pctl([x["first_lvl"] for x in has], .5) if has else "-"])
    card = {
        "id": "c26-range-ladder", "kind": "backtest", "family": "Eagle_Eyes chart ideas (operator, 10-30/31)", "provenance": "run",
        "title": "C26 Candidate C, measure first: the range above a taken high and the divergence legs inside it (recent design window)",
        "date": "2026-11-01",
        "what": [
            {"name": "Source", "value_plain": "operator 2026-11-01: martingale shorts on 1m-5m RSI divergence inside a range above the "
             "taken high, no per-leg stop inside it; card c26-scenario-roadmap-sequence Candidate C", "label": "SOURCED"},
            {"name": "Events", "value_plain": "C26 held highs (lows mirrored) that were taken, phase1_recent.py, 15m Binance spot", "label": "OURS"},
            {"name": "Range measured", "value_plain": "highest high from the take-out to the exit (low reaches L1, else 24h), in % above H1", "label": "OURS"},
            {"name": "Legs", "value_plain": "RSI(14) bearish divergence on 1m/2m/3m/5m bars: pivot +-3 bars, prior pivot within 60 bars lower "
             "in price and higher in RSI, counted at its confirmation close, above H1, after the 1m bar that broke H1", "label": "OURS"},
            {"name": "Trades", "value_plain": "none: counts and distances, no size ladder, no fees, no P&L", "label": "OURS"},
        ],
        "how": "phase1_range.py <repo> <cache> --until %s --sim-json <this file>; 1m bars from data-api.binance.vision (fetch_1m.py)." % P.utc(P.T[-1]).strftime("%Y-%m-%dT%H:%M"),
        "window": "RECENT design window %s .. %s (SEEN: tuned here, tested on DEV later)" % (P.utc(P.T[P.i0]).date(), P.utc(P.T[-1]).date()),
        "verdict": {"label": "Measure only: DOWN highs that came back to L1 went %.2f %% (median) / %.2f %% (80th) beyond H1 first; %d of %d did not come back in 24h" % (
            P.pctl(exc_c, .5) if exc_c else 0, P.pctl(exc_c, .8) if exc_c else 0, len(kept), len(dn)), "tone": "warn"},
        "why": [
            "The range a ladder must survive is the excursion of the take-outs that DO come back; the ones that do not are the ladder's loss.",
            "A range top X stops the ladder on every take-out whose excursion exceeds X; the grid shows how many of those were false stops.",
            "Divergence legs: how many 1m-5m signals fired inside the window says how many legs a martingale would have carried.",
            "Nothing frozen: Phase 2 picks X, leg count and size step from this, then DEV 2022-04..2024-06 scores the book vs a single short.",
        ],
        "kpis": [
            {"label": "DOWN-high take-outs", "value": str(len(dn))},
            {"label": "came back to L1 <=24h", "value": "%d %%" % (100 * len(came) / len(dn)) if dn else "-", "tone": "warn"},
            {"label": "range of those (median / 80th)", "value": "%.2f / %.2f %%" % (P.pctl(exc_c, .5), P.pctl(exc_c, .8)) if exc_c else "-"},
            {"label": "widest that still came back", "value": "%.2f %%" % max(exc_c) if exc_c else "-"},
            {"label": "did not come back (range break)", "value": str(len(kept)), "tone": "bad" if kept else "good"},
        ],
        "examples": [
            {"kind": "charts", "title": "DOWN highs: the range a ladder had to survive (percent from the held high)", "items": items,
             "caption": "Grey dot = the high, blue dot = retest held, cross = taken; dashed = H1, blue line = L1. 24h after the take-out shown."},
            {"kind": "table", "title": "Range top X for DOWN highs", "cols": ["X above H1", "stopped out", "false stops (came back anyway)", "not stopped: back to L1 / n"],
             "rows": grid, "caption": "stopped = excursion > X before the exit"},
            {"kind": "table", "title": "Divergence legs inside the window, DOWN highs", "cols": ["TF", "take-outs with a signal", "signals (median)", "first signal after the break", "first signal above H1 (median)"],
             "rows": legs, "caption": "no 1m data = no rows" if not bars_by_tf else "1m-5m bars aggregated from Binance spot 1m"},
        ],
        "source_files": ["MyTradingSys/research/c26_roadmap_2026-11-01/PHASE1_RANGE.md", "MyTradingSys/research/c26_roadmap_2026-11-01/phase1_range.py"],
        "commit": "this card",
    }
    with open(P.SIM_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(card, f, indent=1, ensure_ascii=False); f.write("\n")


if __name__ == "__main__":
    main()
