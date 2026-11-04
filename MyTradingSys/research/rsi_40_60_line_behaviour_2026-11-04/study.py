"""rsi_40_60_line_behaviour_2026-11-04: how RSI14 behaves around the 40 and 60 lines on 1h/4h/12h/1d (hold / break / range), the cushion that
separates hold from break, what changes the odds (higher-TF bias, other TFs at the same line, regime/phase) and two plays.

See PRE_REG.md (frozen before any outcome). Passes: count (events and days only, no outcome), dev (rates, picks on DEV only), val (picks only, once).
Data: public SPOT klines 2017-08.. BTCUSDT + ETHUSDT (F:/MTS/Dumps/backtest/spot_2017); 12h is built from 1h (closed, complete buckets only),
1w from 1d. HOLDOUT is never loaded (loader end = window end). Every tuned parameter below is OURS. Times are UTC milliseconds.
"""
import argparse
import csv
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SIB = _load("rsi4060_sibling", REPO / "MyTradingSys/research/bear_proxy_context_tuning_2026-11-04/study.py")
G = SIB.G
L, S, rk, splits, DAY = SIB.L, SIB.S, SIB.rk, SIB.splits, SIB.DAY
from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core  # noqa: E402

COST = rk.TAKER_RT_PCT                      # 0.14 % round trip, SOURCED research_kit
SYMS = ("BTCUSDT", "ETHUSDT")
LONG_START = L.LONG_START                   # 2017-08-01
HOUR = 3600000
TF_MS = {"1h": HOUR, "4h": 4 * HOUR, "12h": 12 * HOUR, "1d": DAY, "1w": 7 * DAY}
TFS = ("1h", "4h", "12h", "1d")
LINES = (40, 60)                            # SOURCED Malkan lines; the cushion around them is OURS
CUSH = (1, 2, 3, 5)                         # OURS, RSI points
N_BARS = {"1h": 24, "4h": 18, "12h": 14, "1d": 10}   # OURS: outcome window AND holding period, bars
HTF = {"1h": "4h", "4h": "12h", "12h": "1d", "1d": "1w"}
CHOP_X = 2                                  # OURS: >= 2 crossings of the line before the band exit = RANGE (chop)
SEP_MIN_N, SEP_MIN_DAYS = 100, 40           # OURS: a cushion is pickable only with this many events/days
MIN_N, MIN_DAYS = 30, 20                    # OURS: play pick eligibility (as sibling)
MAX_PICKS = 6                               # OURS: VALIDATION tests, Holm m = 6
FAMILY_M = MAX_PICKS
SD = {"1h": 2.9, "4h": 5.4, "12h": 8.2, "1d": 10.0}   # OURS: sd (%) of the N-bar return, sibling 10-bar sd scaled by sqrt(time), see PRE_REG
MAX_GROSS = G.MAX_PLAUSIBLE_GROSS           # 0.30 %, OURS (prereg_gate)
FRESH_DAYS = SIB.FRESH_DAYS                 # 60, OURS
CTXS = ("ALL", "htf_up", "htf_down", "confl_0", "confl_1plus", "reg_bull", "reg_range", "reg_bear", "ph_fresh", "ph_mature")
PLAYS = ("bounce", "wait")
NULL_BARS = 200000


# ---------------------------------------------------------------- series ----------------------------------------------------------
def rsi_arr(closes, n=14):
    """Wilder RSI14 (rsi_core) per bar, nan where undefined."""
    r = rsi_core(list(closes), n)
    return np.array([np.nan if x is None else x for x in r], float)


def resample_12h(h1):
    """12h bars from 1h: bucket = floor(t / 12h); a bucket is kept only when all 12 hourly bars are present (closed, complete)."""
    out, cur, key = [], [], None
    for b in h1:
        kb = b["t"] // TF_MS["12h"]
        if kb != key:
            if cur and len(cur) == 12:
                out.append(_agg(cur, key))
            cur, key = [], kb
        cur.append(b)
    if cur and len(cur) == 12:
        out.append(_agg(cur, key))
    return out


def _agg(cur, key):
    return {"t": key * TF_MS["12h"], "o": cur[0]["o"], "h": max(b["h"] for b in cur), "l": min(b["l"] for b in cur),
            "c": cur[-1]["c"], "v": sum(b["v"] for b in cur)}


def load_series(sym, hi_ms, registry, root=L.SPOT_ROOT):
    """tf -> (bars, tcl, rsi): tcl = t + bar length (the instant the bar is closed); tfs 1h 4h 12h 1d 1w."""
    from MyTradingSys.backtest.layers.timeframe.tf_resample import resample
    h1 = L.load_spot("1h", hi_ms, root, sym)
    d1 = L.load_spot("1d", hi_ms, root, sym)
    bars = {"1h": h1, "4h": L.load_spot("4h", hi_ms, root, sym), "12h": resample_12h(h1), "1d": d1, "1w": resample(d1, "1w", registry)}
    out = {}
    for tf, bs in bars.items():
        out[tf] = (bs, np.array([b["t"] + TF_MS[tf] for b in bs], float), rsi_arr([b["c"] for b in bs]))
    return out


def day_ctx(d1, registry, hi_ms):
    """Per UTC day (as-of 00:00 UTC): regime (primary Malkan, research_kit.regime_tag) and phase (SMA200 side age, fresh <= 60 / mature)."""
    daily, wk, mo = L.build_context(d1, registry)
    reg = L.make_regime_at(daily, wk, mo)
    tcl = np.array([b["t"] + DAY for b in d1], float)
    side, age = SIB.sma_side_age([b["c"] for b in d1])
    day0, day1 = int(d1[0]["t"] // DAY), int(hi_ms // DAY)
    days = np.arange(day0, day1 + 1)
    regime = np.empty(len(days), object)
    phase = np.empty(len(days), object)
    for x, D in enumerate(days):
        regime[x] = reg(D * DAY)
        k = SIB.asof_idx(tcl, D * DAY)
        phase[x] = None if (k < 0 or side[k] == 0) else ("fresh" if age[k] <= FRESH_DAYS else "mature")
    return {"day0": day0, "n": len(days), "regime": regime, "phase": phase}


def ctx_at(st, key, t):
    """Day context at instant t; None before the first data day or past the last (never a negative-index wrap)."""
    x = int(t // DAY) - st["day0"]
    return st[key][x] if 0 <= x < st["n"] else None


# ---------------------------------------------------------------- events ---------------------------------------------------------
def zone_of(x, line, c):
    """+1 above the band, -1 below it, 0 inside [line - c, line + c]."""
    return 1 if x > line + c else (-1 if x < line - c else 0)


def find_entries(r, line, c):
    """(k, origin) for every bar k whose RSI is inside the band while bar k-1 was outside it; origin = side of bar k-1 (+1 above, -1 below)."""
    z = np.full(len(r), 9, int)
    ok = ~np.isnan(r)
    z[ok] = np.where(r[ok] > line + c, 1, np.where(r[ok] < line - c, -1, 0))
    ks = np.nonzero((z[1:] == 0) & ((z[:-1] == 1) | (z[:-1] == -1)))[0] + 1
    return [(int(k), int(z[k - 1])) for k in ks]


def classify(r, k, origin, line, c, n):
    """(cls, e, crossings) for the entry at bar k, or None when bar k+n is not available.
    Scan bars k..k+n; crossings = changes of the side of RSI vs the line, counted from bar k-1 (side = origin) up to the exit bar.
    First bar j > k outside the band: crossings >= CHOP_X -> range_chop; else back on the origin side -> hold; far side -> break.
    No exit in n bars -> range_inside (classified at bar k+n)."""
    if k + n >= len(r):
        return None
    prev, cross = origin, 0
    for j in range(k, k + n + 1):
        s = 1 if r[j] > line else (-1 if r[j] < line else 0)
        if s != 0:
            if s != prev:
                cross += 1
            prev = s
        if j > k and zone_of(r[j], line, c) != 0:
            if cross >= CHOP_X:
                return "range_chop", j, cross
            return ("hold" if zone_of(r[j], line, c) == origin else "break"), j, cross
    return "range_inside", k + n, cross


def asof_vals(ser, tf2, tev):
    tcl, r = ser[tf2][1], ser[tf2][2]
    idx = np.searchsorted(tcl, tev, side="right") - 1
    v = np.where(idx >= 0, r[np.clip(idx, 0, None)], np.nan)
    return v


def build_events(sym, ser, st, lo_ms, hi_ms, combos=None, classify_on=True):
    """Event rows for one symbol. combos = list of (tf, line, c) or None for the full grid. classify_on False = count pass (no outcome)."""
    rows = []
    for tf in TFS:
        bars, _tcl, r = ser[tf]
        n = N_BARS[tf]
        for line in LINES:
            for c in CUSH:
                if combos is not None and (tf, line, c) not in combos:
                    continue
                ents = []
                for k, origin in find_entries(r, line, c):
                    tev = bars[k]["t"] + TF_MS[tf]
                    if tev < lo_ms or tev >= hi_ms:
                        continue
                    if not classify_on:
                        if k + n < len(r):
                            ents.append((k, origin, "", k, 0.0, tev))
                        continue
                    res = classify(r, k, origin, line, c, n)
                    if res is None:
                        continue
                    cls, e, _x = res
                    if e + n >= len(bars):
                        continue
                    ent = bars[e + 1]["o"]
                    ret = (bars[e + n]["c"] - ent) / ent * 100.0                # long gross %, entry next bar open, exit close of bar e+n
                    ents.append((k, origin, cls, e, ret, tev))
                if not ents:
                    continue
                tev = np.array([x[5] for x in ents], float)
                conf = np.zeros(len(ents), int)
                with np.errstate(invalid="ignore"):
                    for tf2 in TFS:
                        if tf2 != tf:
                            conf += (np.abs(asof_vals(ser, tf2, tev) - line) <= c).astype(int)
                    hv = asof_vals(ser, HTF[tf], tev)
                    htf = np.where(hv > 50, 1, np.where(hv < 50, -1, 0))
                    htf = np.where(np.isnan(hv), 0, htf)
                for q, (k, origin, cls, e, ret, t) in enumerate(ents):
                    eday = int(bars[e + 1]["t"] // DAY) if e + 1 < len(bars) else int(t // DAY)
                    rows.append((sym, tf, line, c, origin, cls, t, int(t // DAY), eday, ret, int(htf[q]), int(conf[q]),
                                 ctx_at(st, "regime", t), ctx_at(st, "phase", t)))
    return pd.DataFrame(rows, columns=["sym", "tf", "L", "c", "origin", "cls", "tev", "day", "eday", "ret", "htf", "confl", "regime", "phase"])


def all_events(registry, lo_ms, hi_ms, root=L.SPOT_ROOT, combos=None, classify_on=True):
    frames, states = [], {}
    for sym in SYMS:
        ser = load_series(sym, hi_ms, registry, root)
        st = day_ctx(ser["1d"][0], registry, hi_ms)
        states[sym] = st
        frames.append(build_events(sym, ser, st, lo_ms, hi_ms, combos, classify_on))
        print(sym, "events done", file=sys.stderr, flush=True)
    return pd.concat(frames, ignore_index=True), states


# ---------------------------------------------------------------- statistics ----------------------------------------------------
def ctx_mask(df, ctx):
    if ctx == "ALL":
        return np.ones(len(df), bool)
    if ctx == "htf_up":
        return (df["htf"] == 1).to_numpy()
    if ctx == "htf_down":
        return (df["htf"] == -1).to_numpy()
    if ctx == "confl_0":
        return (df["confl"] == 0).to_numpy()
    if ctx == "confl_1plus":
        return (df["confl"] >= 1).to_numpy()
    if ctx.startswith("reg_"):
        return (df["regime"] == ctx[4:]).to_numpy()
    if ctx.startswith("ph_"):
        return (df["phase"] == ctx[3:]).to_numpy()
    raise ValueError(ctx)


def rates(df):
    n = len(df)
    if n == 0:
        return {"n": 0, "days": 0}
    cl = df["cls"]
    ch, ci = int((cl == "range_chop").sum()), int((cl == "range_inside").sum())
    h, b = int((cl == "hold").sum()), int((cl == "break").sum())
    return {"n": n, "days": int(df["day"].nunique()), "hold": h / n, "brk": b / n, "rng": (ch + ci) / n, "chop": ch / n, "inside": ci / n,
            "sep": abs(h - b) / n}


def power(n_days, tf):
    """Count-only gate (prereg_gate formula): BLOCK when MDE + cost > 0.30 %. Unit %, sd OURS per TF, Holm m = FAMILY_M."""
    if n_days <= 0:
        return {"mde": float("nan"), "gate": "BLOCK"}
    m = G.mde(n_days, SD[tf], FAMILY_M)
    return {"mde": m, "gate": "BLOCK" if m + COST > MAX_GROSS else "PASS"}


def pick_cushion(rows):
    """rows = per-c rate dicts of one TF x line x side. Best = max |hold - break| share among c with n >= 100 and days >= 40; tie = smaller c."""
    ok = [r for r in sorted(rows, key=lambda x: x["c"]) if r["n"] >= SEP_MIN_N and r["days"] >= SEP_MIN_DAYS]
    return max(ok, key=lambda r: r["sep"]) if ok else None


def play_dir(play, origin):
    """bounce: trade in the direction RSI left the band on the origin side (origin above -> long). wait: opposite (break direction)."""
    return origin if play == "bounce" else -origin


def play_cell(df, play):
    """Events that confirm the play (bounce = hold, wait = break), gross % in the play direction."""
    sub = df[df["cls"] == ("hold" if play == "bounce" else "break")]
    g = (play_dir(play, sub["origin"].to_numpy()) * sub["ret"].to_numpy()) if len(sub) else np.array([])
    return sub, g


def null_rates(seed=11):
    """Random-walk benchmark: iid normal log returns, same classify rules and N per TF. -> {(tf, line, origin, c): rates dict}."""
    out = {}
    for ti, tf in enumerate(TFS):
        rng = np.random.default_rng(seed + ti)
        px = 100.0 * np.exp(np.cumsum(rng.normal(0, 0.01, NULL_BARS)))
        r = rsi_arr(px)
        for line in LINES:
            for c in CUSH:
                cnt = {1: {"hold": 0, "break": 0, "rng": 0, "n": 0}, -1: {"hold": 0, "break": 0, "rng": 0, "n": 0}}
                for k, origin in find_entries(r, line, c):
                    res = classify(r, k, origin, line, c, N_BARS[tf])
                    if res is None:
                        continue
                    key = res[0] if res[0] in ("hold", "break") else "rng"
                    cnt[origin][key] += 1
                    cnt[origin]["n"] += 1
                for o in (1, -1):
                    d = cnt[o]
                    out[(tf, line, o, c)] = {"hold": d["hold"] / d["n"], "brk": d["break"] / d["n"], "rng": d["rng"] / d["n"], "n": d["n"]} if d["n"] else None
    return out


def write_csv(path, rows):
    keys = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with open(path, "w", newline="\n", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def side_name(o):
    return "above" if o == 1 else "below"


# ---------------------------------------------------------------- passes ---------------------------------------------------------
def behaviour_rows(df, null=None):
    out = []
    for tf in TFS:
        for line in LINES:
            for o in (1, -1):
                for c in CUSH:
                    sub = df[(df["tf"] == tf) & (df["L"] == line) & (df["origin"] == o) & (df["c"] == c)]
                    row = {"tf": tf, "L": line, "side": side_name(o), "c": c}
                    row.update(rates(sub))
                    if null is not None and null.get((tf, line, o, c)):
                        nn = null[(tf, line, o, c)]
                        row.update({"null_hold": nn["hold"], "null_brk": nn["brk"], "null_rng": nn["rng"], "null_n": nn["n"]})
                    out.append(row)
    return out


def contrast_rows(df, picks):
    """Table 2: hold-rate difference (percentage points) with day-clustered 95 % CI, pooled per TF over the picked (line, side, cushion) cells."""
    out = []
    for tf in TFS:
        parts = []
        for line in LINES:
            for o in (1, -1):
                p = picks.get("%s|%d|%s" % (tf, line, side_name(o)))
                if p:
                    parts.append(df[(df["tf"] == tf) & (df["L"] == line) & (df["origin"] == o) & (df["c"] == p["c"])])
        if not parts:
            continue
        d = pd.concat(parts)
        hold = (d["cls"] == "hold").to_numpy().astype(float)
        day = d["day"].to_numpy()
        pairs = [("htf_aligned_vs_opposed", ((d["htf"] == d["origin"]) & (d["htf"] != 0)).to_numpy(), ((d["htf"] == -d["origin"]) & (d["htf"] != 0)).to_numpy()),
                 ("confl_1plus_vs_0", (d["confl"] >= 1).to_numpy(), (d["confl"] == 0).to_numpy()),
                 ("fresh_vs_mature", (d["phase"] == "fresh").to_numpy(), (d["phase"] == "mature").to_numpy()),
                 ("bull_vs_range", (d["regime"] == "bull").to_numpy(), (d["regime"] == "range").to_numpy())]
        for name, a, b in pairs:
            row = {"tf": tf, "contrast": name, "n_a": int(a.sum()), "n_b": int(b.sum())}
            if a.sum() > 1 and b.sum() > 1:
                df_, se = rk.cluster_diff(hold[a], day[a], hold[b], day[b])
                row.update({"hold_a": float(hold[a].mean()), "hold_b": float(hold[b].mean()), "diff_pp": df_ * 100,
                            "lo_pp": (df_ - 1.96 * se) * 100, "hi_pp": (df_ + 1.96 * se) * 100})
            out.append(row)
    return out


def context_play_rows(df, picks):
    """At the picked cushion: rates per context value, and both plays per context value."""
    ctx_rows, play_rows = [], []
    for tf in TFS:
        for line in LINES:
            for o in (1, -1):
                p = picks.get("%s|%d|%s" % (tf, line, side_name(o)))
                if not p:
                    continue
                cell = df[(df["tf"] == tf) & (df["L"] == line) & (df["origin"] == o) & (df["c"] == p["c"])]
                for ctx in CTXS:
                    sub = cell[ctx_mask(cell, ctx)]
                    row = {"tf": tf, "L": line, "side": side_name(o), "c": p["c"], "ctx": ctx}
                    row.update(rates(sub))
                    ctx_rows.append(row)
                    for play in PLAYS:
                        s2, g = play_cell(sub, play)
                        pr = {"tf": tf, "L": line, "side": side_name(o), "c": p["c"], "ctx": ctx, "play": play}
                        st = SIB.stat(g, s2["eday"].to_numpy()) if len(s2) else {"n": 0, "days": 0}
                        pr.update(st)
                        pw = power(pr["days"], tf)
                        pr.update({"mde": pw["mde"], "gate": pw["gate"]})
                        play_rows.append(pr)
    return ctx_rows, play_rows


def pick_plays(play_rows):
    """Top MAX_PICKS by DEV fee-net among n >= 30 and >= 20 days, at most one per (tf, line, side)."""
    ok = [r for r in play_rows if r["n"] >= MIN_N and r["days"] >= MIN_DAYS and r.get("net", float("nan")) == r.get("net", float("nan"))]
    ok.sort(key=lambda r: -r["net"])
    chosen, seen = [], set()
    for r in ok:
        key = (r["tf"], r["L"], r["side"])
        if key in seen:
            continue
        seen.add(key)
        chosen.append(r)
        if len(chosen) == MAX_PICKS:
            break
    return chosen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass", dest="pass_", required=True, choices=("count", "dev", "val"))
    ap.add_argument("--root", default=L.SPOT_ROOT)
    a = ap.parse_args()
    registry = json.loads((REPO / "MyTradingSys/backtest/layers/timeframe/registry.json").read_text(encoding="utf-8"))
    if a.pass_ == "val":
        if (HERE / "plays_val.csv").exists():
            print("VALIDATION already read once; refusing")
            return 3
        return run_val(registry, a.root)
    lo_ms, hi_ms = S.ms(pd.Timestamp(LONG_START)), S.ms(splits.DEV_END)
    if a.pass_ == "count":
        df, _ = all_events(registry, lo_ms, hi_ms, a.root, classify_on=False)
        rows = []
        for tf in TFS:
            for line in LINES:
                for o in (1, -1):
                    for c in CUSH:
                        sub = df[(df["tf"] == tf) & (df["L"] == line) & (df["origin"] == o) & (df["c"] == c)]
                        d = int(sub["day"].nunique())
                        pw = power(d, tf)
                        rows.append({"tf": tf, "L": line, "side": side_name(o), "c": c, "n_events": len(sub), "days": d,
                                     "mde": pw["mde"], "gate": pw["gate"]})
        write_csv(HERE / "count_dev.csv", rows)
        print("count rows", len(rows), "PASS", sum(r["gate"] == "PASS" for r in rows))
        return 0
    df, states = all_events(registry, lo_ms, hi_ms, a.root)
    null = null_rates()
    beh = behaviour_rows(df, null)
    write_csv(HERE / "behaviour_dev.csv", beh)
    picks = {}
    for tf in TFS:
        for line in LINES:
            for o in (1, -1):
                r = pick_cushion([x for x in beh if x["tf"] == tf and x["L"] == line and x["side"] == side_name(o)])
                picks["%s|%d|%s" % (tf, line, side_name(o))] = ({"c": r["c"], "n": r["n"], "hold": r["hold"], "brk": r["brk"], "rng": r["rng"], "sep": r["sep"]}
                                                                if r else None)
    ctx_rows, play_rows = context_play_rows(df, picks)
    write_csv(HERE / "context_dev.csv", ctx_rows)
    write_csv(HERE / "plays_dev.csv", play_rows)
    con = contrast_rows(df, picks)
    write_csv(HERE / "contrast_dev.csv", con)
    chosen = pick_plays(play_rows)
    (HERE / "picks_dev.json").write_text(json.dumps({"cushion": picks, "plays": [
        {k: r[k] for k in ("tf", "L", "side", "c", "ctx", "play", "n", "days", "net", "ci_lo", "ci_hi", "gate")} for r in chosen]}, indent=1),
        encoding="utf-8", newline="\n")
    st = states["BTCUSDT"]
    starts = S.week_starts(lo_ms, hi_ms)
    regs = [ctx_at(st, "regime", t) for t in starts]
    line = rk.regime_mix_line(regs) + " (BTCUSDT, regime as of Monday 00:00 UTC)"
    (HERE / "regime_mix_dev.txt").write_text(line + "\n", encoding="utf-8", newline="\n")
    print(line)
    print("picked cushions:", sum(1 for v in picks.values() if v), "of", len(picks), "| picked plays:", len(chosen))
    return 0


def run_val(registry, root):
    picks = json.loads((HERE / "picks_dev.json").read_text(encoding="utf-8"))
    lo_ms, hi_ms = S.ms(splits.VALIDATION_START), S.ms(splits.VALIDATION_END)
    combos = {(p["tf"], p["L"], p["c"]) for p in picks["plays"]}
    for k, v in picks["cushion"].items():
        if v:
            tf, line, _side = k.split("|")
            combos.add((tf, int(line), v["c"]))
    df, _ = all_events(registry, lo_ms, hi_ms, root, combos=combos)
    stab = []
    for k, v in picks["cushion"].items():
        if v:
            tf, line, side = k.split("|")
            o = 1 if side == "above" else -1
            sub = df[(df["tf"] == tf) & (df["L"] == int(line)) & (df["origin"] == o) & (df["c"] == v["c"])]
            row = {"tf": tf, "L": int(line), "side": side, "c": v["c"], "dev_hold": v["hold"], "dev_brk": v["brk"], "dev_rng": v["rng"]}
            row.update(rates(sub))
            stab.append(row)
    write_csv(HERE / "behaviour_val.csv", stab)
    tested = []
    for p in picks["plays"]:
        o = 1 if p["side"] == "above" else -1
        cell = df[(df["tf"] == p["tf"]) & (df["L"] == p["L"]) & (df["origin"] == o) & (df["c"] == p["c"])]
        sub = cell[ctx_mask(cell, p["ctx"])]
        s2, g = play_cell(sub, p["play"])
        st = SIB.stat(g, s2["eday"].to_numpy()) if len(s2) else {"n": 0, "days": 0}
        tested.append((p, st))
    return finish_val(tested, picks)


def finish_val(tested, picks):
    """Holm over the tested picks (family m = FAMILY_M, untested slots count as p = 1); verdict per pick; rules.json."""
    ps = [t[1].get("p") for t in tested]
    real = [(i, p) for i, p in enumerate(ps) if p is not None and p == p]
    adj = rk.holm([p for _, p in real], m=FAMILY_M) if real else []
    holm_of = {i: float(q) for (i, _), q in zip(real, adj)}
    rows, verdicts = [], {}
    for i, (p, st) in enumerate(tested):
        lo = st.get("ci_lo", float("nan"))
        q = holm_of.get(i)
        if p["gate"] == "BLOCK":
            v, why = "INCONCLUSIVE", "power gate BLOCK on the picked cell (capped; MDE too large for its DEV days)"
        elif st["n"] and lo == lo and lo > 0 and q is not None and q < 0.05:
            v, why = "DEFAULT", "VALIDATION fee-net CI above 0, Holm %.3f" % q
        else:
            v, why = "FAIL", "powered but VALIDATION fee-net CI not above 0 (n %s, CI lo %s, Holm %s)" % (st["n"], lo, q)
        key = "%s|%d|%s|%s|%s" % (p["tf"], p["L"], p["side"], p["ctx"], p["play"])
        verdicts[key] = {"verdict": v, "why": why, "holm": q, "dev_gate": p["gate"]}
        row = dict(p)
        row.update({("val_" + k): val for k, val in st.items()})
        row.update({"holm": q, "verdict": v})
        rows.append(row)
    write_csv(HERE / "plays_val.csv", rows)
    (HERE / "verdicts_val.json").write_text(json.dumps(verdicts, indent=1), encoding="utf-8", newline="\n")
    dflt = {"%s|%s|%s|%s" % (p["tf"], p["L"], p["side"], p["play"]): p["ctx"] for p, _ in tested if verdicts["%s|%d|%s|%s|%s" % (
        p["tf"], p["L"], p["side"], p["ctx"], p["play"])]["verdict"] == "DEFAULT"}
    rules = {"labels": "OURS (cushion, N, classification rules); lines 40/60 SOURCED (Malkan)", "cells": {}}
    for k, v in picks["cushion"].items():
        tf, line, side = k.split("|")
        play = next(({"play": pp["play"], "context": pp["ctx"]} for pp, _ in tested if pp["tf"] == tf and str(pp["L"]) == line and pp["side"] == side and
                     "%s|%s|%s|%s" % (pp["tf"], pp["L"], pp["side"], pp["play"]) in dflt), None)
        rules["cells"][k] = {"cushion": v["c"] if v else None, "dev_hold": v["hold"] if v else None, "dev_break": v["brk"] if v else None,
                             "dev_range": v["rng"] if v else None, "behaviour": None if not v else ("hold-dominant" if v["hold"] > v["brk"] else "break-dominant"),
                             "default_play": play}
    (HERE / "rules.json").write_text(json.dumps(rules, indent=1), encoding="utf-8", newline="\n")
    for k, v in verdicts.items():
        print(k, v)
    return 0


if __name__ == "__main__":
    sys.exit(main())
