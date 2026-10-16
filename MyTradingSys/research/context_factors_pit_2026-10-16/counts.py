"""COUNTS.md + trials.csv from grid_context.csv (count-only; the csv has no outcome column and none is computed here).

  python counts.py                     # reads grid_context.csv (written by run_compare.py --full), writes COUNTS.md, trials.csv

Decision event (per side) = a 1h-grid row with at_level True: the nearest side-aware level (support strictly below the
price for a long, resistance strictly above for a short) lies within K_ZONE x ATR14(4h). "episode" = the rows whose level is
touched for the first time (first_touch). Every table counts events per factor value, per side, per DEV year
(2022, 2023, 2024H1), and flags buckets below n_needed (section 0). Nothing here reads bars after the decision bar.
"""
import csv
import math
import os
import sys
from collections import Counter, defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, REPO)
from MyTradingSys.backtest import research_kit as RK   # noqa: E402  (power_check, holm, cost_in_r; reused not copied)
sys.path.insert(0, HERE)
import context_asof as CA   # noqa: E402  (parameters only)

GRID = os.path.join(HERE, "grid_context.csv")
OUT = os.path.join(HERE, "COUNTS.md")
TRIALS = os.path.join(HERE, "trials.csv")

# ---- power inputs (all OURS unless noted; see COUNTS.md section 0)
TARGET_R = 1.5             # fixed R target of the PRE_REG outcome (OURS)
SD_R_MAX = (1.0 + TARGET_R) / 2.0   # sd of a {-1, +T} outcome is at most (1+T)/2 (p = 0.5)
PLAUSIBLE_R = 0.15         # net effect in R a context filter could plausibly add (OURS; 0.12 sd at the bound)
SD_PCT_H240 = 1.97         # per-trade sd in % at h=240, FABLE_RUNS_AUDIT.md:73 (SOURCED, re-derived there from RESULT.md)
SD_PCT_H60 = 0.93          # per-trade sd in % at h=60, FABLE_RUNS_AUDIT.md:73 (SOURCED)
PLAUSIBLE_PCT = 2 * RK.TAKER_RT_PCT   # 0.28 %: the "MDE > 2C" bar wlow_bounce RESULT.md used (OURS, reused)
YEARS = ("2022", "2023", "2024H1")


def year_of(t):
    d = int(t) // 1440
    return "2022" if d < 365 else "2023" if d < 730 else "2024H1"


def load_rows():
    with open(GRID, newline="", encoding="utf-8") as fh:
        r = csv.DictReader(fh)
        rows = list(r)
    if "t" not in rows[0]:
        # old layout (no t column): rows are (long, short) pairs in ascending grid order
        assert len(rows) % 2 == 0
        for i, row in enumerate(rows):
            row["t"] = str(59 + 60 * (i // 2))
    for row in rows:
        row["year"] = year_of(row["t"])
    return rows


def fl(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return float("nan")


def n_needed_r(cost_r):
    """Smallest n with power_check(n, SD_R_MAX, PLAUSIBLE_R, cost_r).proceed."""
    if not (cost_r == cost_r) or PLAUSIBLE_R <= cost_r:
        return None
    n = math.ceil((RK.MDE_Z * SD_R_MAX / (PLAUSIBLE_R - cost_r)) ** 2)
    assert RK.power_check(n, SD_R_MAX, PLAUSIBLE_R, cost_r)["proceed"]
    assert n == 1 or not RK.power_check(n - 1, SD_R_MAX, PLAUSIBLE_R, cost_r)["proceed"]
    return n


def n_needed_pct(sd):
    n = math.ceil((RK.MDE_Z * sd / (PLAUSIBLE_PCT - RK.TAKER_RT_PCT)) ** 2)
    assert RK.power_check(n, sd, PLAUSIBLE_PCT, RK.TAKER_RT_PCT)["proceed"]
    return n


def bucket_int(v, top=3):
    try:
        x = int(float(v))
    except ValueError:
        return "na"
    return f"{top}+" if x >= top else str(x)


def bucket_age(v):
    x = fl(v)
    if x != x:
        return "na"
    return "<24h" if x < 24 else "24-168h" if x < 168 else ">168h"


def bucket_touch(v):
    x = fl(v)
    if x != x or x < 0:
        return "na"
    return "3+" if x >= 3 else str(int(x))


def table(events, key, fn=lambda v: v, need=None, title=None, order=None):
    """Markdown count table: value x (side, year) with totals; buckets below `need` are flagged."""
    cnt = Counter()
    for e in events:
        cnt[(fn(e[key]), e["side"], e["year"])] += 1
    vals = sorted({k[0] for k in cnt}, key=lambda v: (order.index(v) if order and v in order else 99, str(v)))
    head = ["value"] + [f"{s} {y}" for s in ("long", "short") for y in YEARS] + ["long all", "short all"]
    lines = [f"**{title or key}**", "", "| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for v in vals:
        cells = [str(v)]
        for s in ("long", "short"):
            for y in YEARS:
                cells.append(str(cnt[(v, s, y)]))
        tots = []
        for s in ("long", "short"):
            n = sum(cnt[(v, s, y)] for y in YEARS)
            flag = " <n" if (need is not None and n < need) else ""
            tots.append(f"{n}{flag}")
        lines.append("| " + " | ".join(cells + tots) + " |")
    lines.append("")
    return lines


def pair_table(events, k1, k2, f1=lambda v: v, f2=lambda v: v, need=None, title=None):
    out = []
    for side in ("long", "short"):
        cnt = Counter((f1(e[k1]), f2(e[k2])) for e in events if e["side"] == side)
        v1 = sorted({a for a, _ in cnt}, key=str)
        v2 = sorted({b for _, b in cnt}, key=str)
        out += [f"**{title or k1 + ' x ' + k2}, {side}** (rows = {k1}, columns = {k2}; all three years)", "",
                "| " + k1 + " \\ " + k2 + " | " + " | ".join(map(str, v2)) + " |", "|" + "---|" * (len(v2) + 1)]
        for a in v1:
            cells = []
            for b in v2:
                n = cnt[(a, b)]
                cells.append(f"{n}{' <n' if need is not None and n < need else ''}")
            out.append(f"| {a} | " + " | ".join(cells) + " |")
        out.append("")
    return out


def pct(vals, q):
    v = np.array([x for x in vals if x == x], float)
    return float(np.percentile(v, q)) if len(v) else float("nan")


def rung_alt(e, W):
    """Ladder rung under an alternative W from the three stop columns (same rule as context_asof.ladder)."""
    stops = [("1d", fl(e["stop_d_pct"])), ("12h", fl(e["stop_12_pct"])), ("8h", fl(e["stop_8_pct"]))]
    valid = [(n, s) for n, s in stops if s == s]
    under = [x for x in valid if x[1] <= W]
    if under:
        return under[0][0]
    if valid:
        return min(valid, key=lambda x: x[1])[0]
    return "none"


def main():
    rows = load_rows()
    n_grid = len(rows)
    events = [r for r in rows if r["at_level"] == "True"]
    episodes = [r for r in events if r["first_touch"] == "True"]
    L = []
    L += ["# COUNTS: DEV decision events per context-factor value (count-only, no outcome column anywhere)", "",
          f"Input: `grid_context.csv` (VEC build at every 1h close of DEV, both sides; {n_grid} rows = {n_grid // 2} grid points x 2 sides).",
          "Decision event = grid row with `at_level` True (nearest side-aware level within K_ZONE = 0.5 x ATR14(4h)). Episode = event with",
          "`first_touch` True (the level had no earlier 1h touch since it became available, lookback 720 h). Rows at the same level on",
          "consecutive hours are correlated: the n_needed check should be read against episodes, the per-value tables use events.", ""]
    ev_c = Counter((e["side"], e["year"]) for e in events)
    ep_c = Counter((e["side"], e["year"]) for e in episodes)
    L += ["| side | events 2022 | 2023 | 2024H1 | all | episodes 2022 | 2023 | 2024H1 | all | grid rows |", "|---|---|---|---|---|---|---|---|---|---|"]
    for s in ("long", "short"):
        L.append(f"| {s} | " + " | ".join(str(ev_c[(s, y)]) for y in YEARS) + f" | {sum(ev_c[(s, y)] for y in YEARS)} | "
                 + " | ".join(str(ep_c[(s, y)]) for y in YEARS) + f" | {sum(ep_c[(s, y)] for y in YEARS)} | {n_grid // 2} |")
    L.append("")

    # ---- section 0: n needed
    cost_taker = [fl(e["ladder_cost_r"]) for e in events]
    cr_med = pct(cost_taker, 50)
    cr_maker = cr_med * RK.MAKER_IN_RT_PCT / RK.TAKER_RT_PCT
    need_r = n_needed_r(cr_med)
    need_r_m = n_needed_r(cr_maker)
    need_240 = n_needed_pct(SD_PCT_H240)
    need_60 = n_needed_pct(SD_PCT_H60)
    NEED = need_r
    L += ["## 0. n needed (research_kit.power_check: MDE = 2.8 x sd / sqrt(n); proceed iff MDE + cost <= plausible effect)", "",
          "| model | sd per trade | cost | plausible effect | n needed | label |", "|---|---|---|---|---|---|",
          f"| R units (PRE_REG outcome: stop ladder, target {TARGET_R} R) | <= {SD_R_MAX:.2f} R (bound for a -1/+{TARGET_R} outcome) | median ladder cost over events, all-taker 0.14 %: {cr_med:.3f} R | {PLAUSIBLE_R} R | **{need_r}** | sd bound: arithmetic; cost: events table below; plausible: OURS |",
          f"| R units, maker entry 0.09 % | same | {cr_maker:.3f} R | {PLAUSIBLE_R} R | {need_r_m} | same |",
          f"| % units, h = 240 min | {SD_PCT_H240} % (FABLE_RUNS_AUDIT.md:73) | 0.14 % | {PLAUSIBLE_PCT:.2f} % (2 x cost, wlow_bounce RESULT.md rule) | {need_240} | SOURCED sd, OURS plausible |",
          f"| % units, h = 60 min | {SD_PCT_H60} % (FABLE_RUNS_AUDIT.md:73) | 0.14 % | {PLAUSIBLE_PCT:.2f} % | {need_60} | same |", "",
          f"Flag rule: a bucket with fewer than **{NEED}** events (the R model, all-taker) is marked `<n` in every table below. A factor whose",
          "every value is flagged on one side cannot get a verdict on that side (PRE_REG section 4: INCONCLUSIVE by count, before any outcome).", ""]

    # ---- F1
    L += ["## F1. Side-aware levels", ""]
    L += table(events, "near_src", need=NEED, title="nearest level source (events)", order=list(CA.SOURCES))
    L += table(episodes, "near_src", need=NEED, title="nearest level source (episodes = first touch)", order=list(CA.SOURCES))
    L += table(events, "level_age_h", bucket_age, need=NEED, title="level age at the decision (hours since the level became available)")
    L += table(events, "touch_count", bucket_touch, need=NEED, title="earlier 1h touches of the level (0 = first touch)")
    L += table(events, "approach", need=NEED, title="approach speed over the last 4 closed 1h bars")
    L += table(events, "sweep", need=NEED, title="liquidity sweep: a wick through the level in the last 6 closed 1h bars with the close back on the right side")
    # ---- F2
    L += ["## F2. Confluence", ""]
    L += table(events, "n_layers", lambda v: bucket_int(v, 4), need=NEED, title="distinct layers within 0.5 x ATR (K_ZONE, OURS)")
    L += table(events, "n_layers_k1", lambda v: bucket_int(v, 4), need=NEED, title="distinct layers within 1.0 x ATR (K_ZONE_ALT, counted only)")
    L += table(events, "n_levels", lambda v: bucket_int(v, 12), need=NEED, title="ledger size (all levels on the map, both roles)")
    # ---- F3
    L += ["## F3. Operator's daily-candle stop ladder", "",
          "Stop = prior completed daily low (long) / high (short); if wider than W = 2.5 % (OURS) the prior 12h, then the prior 8h candle;",
          "every rung wider than W -> the tightest valid rung. Widths and counts only.", ""]
    L += table(events, "ladder_rung", need=NEED, title="rung chosen", order=["1d", "12h", "8h", "none"])
    L += table(events, "ladder_cond", need=NEED, title="operator condition (close rule): price has moved past the prior daily open")
    L += table(events, "ladder_cond_alt", need=NEED, title="operator condition (touch rule, counted only): the partial day's high/low moved past the prior open")
    L += table(events, "ladder_below_floor", need=NEED, title=f"stop narrower than the cost floor {CA.STOP_FLOOR_PCT} % (cost > 0.25 R)")
    L += ["**stop width distribution (% of price) and cost in R per rung, over events (both sides, all years)**", "",
          "| rung | n | stop p10 | p25 | p50 | p75 | p90 | cost R taker p50 (0.14 %/stop) | cost R maker-in p50 (0.09 %/stop) |", "|---|---|---|---|---|---|---|---|---|"]
    for rung, col in (("1d", "stop_d_pct"), ("12h", "stop_12_pct"), ("8h", "stop_8_pct")):
        v = [fl(e[col]) for e in events]
        v = [x for x in v if x == x]
        if v:
            L.append(f"| {rung} (all events where valid) | {len(v)} | {pct(v, 10):.2f} | {pct(v, 25):.2f} | {pct(v, 50):.2f} | {pct(v, 75):.2f} | {pct(v, 90):.2f} | "
                     f"{RK.cost_in_r(RK.TAKER_RT_PCT, pct(v, 50)):.3f} | {RK.cost_in_r(RK.MAKER_IN_RT_PCT, pct(v, 50)):.3f} |")
    for rung in ("1d", "12h", "8h"):
        v = [fl(e["ladder_stop_pct"]) for e in events if e["ladder_rung"] == rung]
        if v:
            L.append(f"| chosen = {rung} | {len(v)} | {pct(v, 10):.2f} | {pct(v, 25):.2f} | {pct(v, 50):.2f} | {pct(v, 75):.2f} | {pct(v, 90):.2f} | "
                     f"{RK.cost_in_r(RK.TAKER_RT_PCT, pct(v, 50)):.3f} | {RK.cost_in_r(RK.MAKER_IN_RT_PCT, pct(v, 50)):.3f} |")
    L.append("")
    # ---- F4
    L += ["## F4. Candle patterns on the last COMPLETED candle", ""]
    for tf in ("4h", "8h", "12h", "1d"):
        L += table(events, f"pat_{tf}", need=NEED, title=f"pattern on the last closed {tf} candle")
    # ---- F5
    L += ["## F5. Bollinger state (20, 2, closed bars; band walk = 3+ closes beyond the band while the bandwidth expands)", ""]
    L += table(events, "bb_4h_state", need=NEED, title="4h Bollinger state")
    L += table(events, "bb_1d_state", need=NEED, title="1d Bollinger state")
    L += table(events, "bb_long_conf", need=NEED, title="long confidence: 4h re-entry from below the lower band (long side only)")
    L += table(events, "bb_short_veto_walk", need=NEED, title="short veto: 4h band walk down in progress (short side only)")
    L += table(events, "bb_short_veto_band", need=NEED, title="short veto (alt, counted only): %b <= 0 on the last closed 4h bar")
    L += table(events, "squeeze", need=NEED, title="4h bandwidth squeeze (<= 10th trailing percentile over 180 closed 4h bars)")
    # ---- F6
    L += ["## F6. Bitcoin phase", ""]
    L += table(events, "phase_a", need=NEED, title="phase A: daily fractal pivots (HH&HL markup, LH&LL markdown, else distribution/accumulation by the last trend)")
    L += table(events, "phase_b", need=NEED, title="phase B (counted only): 30-day return +/- 7.5 % markup/markdown, else distribution above SMA50 / accumulation below")
    L += table(events, "intraday", need=NEED, title="intraday: 24h range <= 1.5 x ATR14(4h) = balance, else trend by the 24h close change")
    L += table(events, "intraday_alt", need=NEED, title="intraday (alt, counted only): last 12 1h closes inside the prior 12 bars' range = balance")
    agree = Counter((e["side"], e["phase_a"] == e["phase_b"]) for e in events if e["phase_a"] != "na" and e["phase_b"] != "na")
    L += ["phase A == phase B on events: " + ", ".join(f"{s}: {agree[(s, True)]} agree / {agree[(s, False)]} disagree" for s in ("long", "short")), ""]
    # ---- F7
    L += ["## F7. Own additions", ""]
    L += table(events, "vol_regime", need=NEED, title="volatility regime: ATR14(4h) tercile over the trailing 180 closed 4h bars", order=["low", "mid", "high", "na"])
    L += table(events, "session", need=NEED, title="session (UTC: asia 00-08, london 08-13, ny 13-21, late 21-24)")
    L += table(events, "weekend", need=NEED, title="weekend (Saturday/Sunday UTC)")
    L += table(events, "htf_align", need=NEED, title="HTF alignment: weekly close above (long) / below (short) the close 4 weeks earlier")
    L += table(events, "funding", need=NEED, title="last settled funding rate: neg / low (<= 0.01 %) / high", order=["neg", "low", "high", "na"])
    # ---- pairs
    L += ["## Pairs of the strongest factors (chosen by the operator's emphasis, not by outcome)", ""]
    L += pair_table(events, "n_layers", "bb_4h_state", f1=lambda v: bucket_int(v, 3), need=NEED, title="confluence x 4h Bollinger state")
    L += pair_table(events, "phase_a", "ladder_rung", need=NEED, title="phase A x ladder rung")
    L += pair_table(events, "pat_4h", "n_layers", f2=lambda v: bucket_int(v, 3), need=NEED, title="4h candle pattern x confluence")
    # ---- trials (angle e)
    trials = []

    def add(tid, factor, primary, alt, why, n_p, n_a):
        trials.append(dict(trial_id=tid, factor=factor, primary=primary, alternative=alt, reason=why,
                           n_primary_long=n_p[0], n_primary_short=n_p[1], n_alt_long=n_a[0], n_alt_short=n_a[1], outcome_read="no"))

    def nside(pred, pool=events):
        return (sum(1 for e in pool if e["side"] == "long" and pred(e)), sum(1 for e in pool if e["side"] == "short" and pred(e)))

    grid_long = [r for r in rows if r["side"] == "long"]
    grid_short = [r for r in rows if r["side"] == "short"]
    add("T1", "F1 role rule", "support iff last closed 1h close > level", "last closed 4h close > level",
        "the 1h close is the decision grid itself (no stale role up to 4 h); a 4h close flips later",
        nside(lambda e: True, rows), nside(lambda e: e["near_src"] == e["near_src_4hrule"] and e["n_layers"] == e["n_layers_4hrule"], rows))
    add("T2", "F2 zone width", "K_ZONE = 0.5 x ATR14(4h)", "1.0 x ATR14(4h)",
        "half an ATR keeps 'at the level' tighter than one 4h bar's typical range", nside(lambda e: True), nside(lambda r: fl(r["near_dist_atr"]) <= CA.K_ZONE_ALT, rows))
    add("T3", "F3 operator condition", "close rule: current close past the prior daily open", "touch rule: the partial day's extreme past the prior open",
        "the operator says 'has moved past the opening' at a decision; a close is the PIT reading a trader quotes",
        nside(lambda e: e["ladder_cond"] == "True"), nside(lambda e: e["ladder_cond_alt"] == "True"))
    add("T4", "F3 width W", "W = 2.5 % of price", "W = 1.5 %", "2.5 % is about one DEV median daily range; 1.5 % pushes most days to the 12h/8h rungs",
        nside(lambda e: e["ladder_rung"] == "1d"), nside(lambda e: rung_alt(e, 1.5) == "1d"))
    add("T5", "F5 short veto", "band walk down in progress (3+ closes beyond, bandwidth expanding)", "%b <= 0 on the last closed 4h bar",
        "the operator's 'dance' is the walk, not a single close outside", nside(lambda e: e["bb_short_veto_walk"] == "True"), nside(lambda e: e["bb_short_veto_band"] == "True"))
    add("T6", "F6 phase", "A: daily fractal pivots", "B: 30-day return vs 7.5 % + SMA50 split",
        "A is what a trader reads off swing highs/lows (markup = HH&HL); B is the repo's trend_tag reused", nside(lambda e: e["phase_a"] == "markup"), nside(lambda e: e["phase_b"] == "markup"))
    add("T7", "F6 intraday", "24h range <= 1.5 ATR = balance", "last 12 1h closes inside the prior 12 bars' range",
        "range-vs-ATR is one number a trader checks; the inside-range rule needs two windows", nside(lambda e: e["intraday"] == "balance"), nside(lambda e: e["intraday_alt"] == "balance"))
    with open(TRIALS, "w", newline="\n", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(trials[0].keys()))
        w.writeheader()
        w.writerows(trials)
    L += ["## Angle (e): two reasonable definitions, counts under both (trials.csv; T8 = PRIOR_RULE, counted by prior_rule_count.py)", "",
          "| id | factor | primary | alternative | n primary (long/short) | n alt (long/short) | why the primary |", "|---|---|---|---|---|---|---|"]
    for tr in trials:
        L.append(f"| {tr['trial_id']} | {tr['factor']} | {tr['primary']} | {tr['alternative']} | {tr['n_primary_long']}/{tr['n_primary_short']} | {tr['n_alt_long']}/{tr['n_alt_short']} | {tr['reason']} |")
    L += ["", "T1 counts grid rows (not events) whose nearest source and layer count agree under both role rules; T2 counts rows within the zone.", ""]
    with open(OUT, "w", newline="\n", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print(f"events long/short = {sum(ev_c[('long', y)] for y in YEARS)}/{sum(ev_c[('short', y)] for y in YEARS)}; episodes = "
          f"{sum(ep_c[('long', y)] for y in YEARS)}/{sum(ep_c[('short', y)] for y in YEARS)}; n_needed (R) = {NEED}; wrote COUNTS.md, trials.csv")


if __name__ == "__main__":
    main()
