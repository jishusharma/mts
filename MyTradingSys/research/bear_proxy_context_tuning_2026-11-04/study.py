"""bear_proxy_context_tuning_2026-11-04: per-context OURS bear-proxy setting (Part A) and per-timeframe fake-out filter (Part B).

See PRE_REG.md (frozen before any return). Passes: count (no returns; power gate), dev (picks on DEV only), val (picks only, once).
Data: public SPOT klines 2017-08.. BTCUSDT + ETHUSDT (F:/MTS/Dumps/backtest/spot_2017), no futures splice. HOLDOUT is never loaded
(loader end = window end). Every tuned parameter below is OURS. Times are UTC milliseconds.
"""
import argparse
import csv
import importlib.util
import json
import sys
from bisect import bisect_right
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


L = _load("bear_ctx_study_long", REPO / "MyTradingSys/research/rsi_divergence_mtf_gated_2026-11-04/study_long.py")
G = _load("bear_ctx_prereg_gate", REPO / "scripts/dev/prereg_gate.py")
S, rk, splits, DAY = L.S, L.rk, L.splits, L.DAY
from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core  # noqa: E402

COST = rk.TAKER_RT_PCT                      # 0.14 % round trip, SOURCED research_kit
H = 10                                      # exit H bars after entry (OURS, as the sibling studies)
RETEST_N = 10                               # OURS
SYMS = ("BTCUSDT", "ETHUSDT")
LONG_START = L.LONG_START                   # 2017-08-01
TF_MS = S.TF_MS
MIN_N, MIN_DAYS = 30, 20                    # OURS: pick / default eligibility
FRESH_DAYS = 60                             # OURS: SMA200 side age (daily closes) up to which a trend is "fresh"
A_TF = "15m"                                # signal timeframe for Part A (best powered in the siblings)
SD = {"15m": 0.8, "1h": 1.9, "4h": 4.0, "1d": 10.0}   # OURS, % sd of the 10-bar return (carried from PRE_REG_LONG.md)
A_SETTINGS = [(n, t, tf, sma) for n in (14, 21) for t in (35, 40, 45) for tf in ("1d", "1w") for sma in (True, False)]
A_BASELINE = (14, 40, "1w", True)
CELLS = ["ALL"] + ["%s|%s" % (r, p) for r in ("bull", "range", "bear") for p in ("fresh", "mature")]
B_TFS = ("15m", "1h", "4h", "1d")
B_FILTERS = ("none", "confirm1", "htf_rsi", "volume", "retest")
HTF = {"15m": "1h", "1h": "4h", "4h": "1d", "1d": "1w"}
FAMILY_M = len(CELLS) + len(B_TFS)          # 7 + 4 = 11 VALIDATION tests
MAX_GROSS = G.MAX_PLAUSIBLE_GROSS           # 0.30 %, OURS (prereg_gate)
ATR_N = 14                                  # OURS, simple mean of true range
FAKE_ATR = 1.0                              # OURS, fake-out = adverse move >= 1 ATR before a +1 ATR favourable move


def skey(s):
    return "rsi%d<=%d|%s|sma%s" % (s[0], s[1], s[2], "on" if s[3] else "off")


# ---------------------------------------------------------------- Part A: state per UTC day -----------------------------------
def rsi_pairs(bars, length):
    """(t_close ms array, rsi array) with t_close = the next bar's open; the final bar is dropped (close time unknown)."""
    closes = [b["c"] for b in bars]
    if len(closes) <= length:
        return np.array([], float), np.array([], float)
    r = rsi_core(closes, length)
    keep = [k for k in range(len(bars) - 1) if r[k] is not None]
    return np.array([bars[k + 1]["t"] for k in keep], float), np.array([r[k] for k in keep], float)


def asof_idx(tcl, t):
    """Index of the latest entry with t_close <= t, or -1."""
    return int(np.searchsorted(tcl, t, side="right")) - 1


def sma_side_age(closes, n=200):
    """Per daily bar: side of the close vs its n-bar SMA (+1 above, -1 below, 0 none/equal) and the run length of that side."""
    c = np.asarray(closes, float)
    cs = np.concatenate(([0.0], np.cumsum(c)))
    side = np.zeros(len(c), int)
    age = np.zeros(len(c), int)
    for k in range(n - 1, len(c)):
        avg = (cs[k + 1] - cs[k + 1 - n]) / n
        side[k] = 1 if c[k] > avg else (-1 if c[k] < avg else 0)
        age[k] = (age[k - 1] + 1) if (k > 0 and side[k] == side[k - 1] and side[k] != 0) else (1 if side[k] != 0 else 0)
    return side, age


def day_state(d1, registry, hi_ms):
    """Day-level as-of state for day D at instant D*DAY: regime (primary Malkan), phase (SMA200 side age), proxy_on per setting.
    Daily/weekly bars close at 00:00 UTC, so the state is constant inside a UTC day (computed at the day's first instant)."""
    from MyTradingSys.backtest.layers.timeframe.tf_resample import resample
    daily, wk, mo = L.build_context(d1, registry)
    reg = L.make_regime_at(daily, wk, mo)
    wk_bars = resample(d1, "1w", registry)
    tcl_d = np.array([b["t"] + DAY for b in d1], float)
    side, age = sma_side_age([b["c"] for b in d1])
    day0, day1 = int(d1[0]["t"] // DAY), int(hi_ms // DAY)
    days = np.arange(day0, day1 + 1)
    regime = np.empty(len(days), object)
    phase = np.empty(len(days), object)
    kk = np.array([asof_idx(tcl_d, D * DAY) for D in days])
    for x, D in enumerate(days):
        regime[x] = reg(D * DAY)
        k = kk[x]
        phase[x] = None if (k < 0 or side[k] == 0) else ("fresh" if age[k] <= FRESH_DAYS else "mature")
    rs = {}
    for n in (14, 21):
        rs[(n, "1d")] = rsi_pairs(d1, n)
        rs[(n, "1w")] = rsi_pairs(wk_bars, n)
    proxy = {}
    for s in A_SETTINGS:
        tcl, v = rs[(s[0], s[2])]
        on = np.zeros(len(days), bool)
        for x, D in enumerate(days):
            j = asof_idx(tcl, D * DAY)
            if j < 0 or not v[j] <= s[1]:
                continue
            if s[3] and not (kk[x] >= 0 and side[kk[x]] == -1):
                continue
            on[x] = True
        proxy[s] = on
    closes = np.array([b["c"] for b in d1], float)
    return {"day0": day0, "days": days, "regime": regime, "phase": phase, "proxy": proxy, "kk": kk, "closes": closes, "tcl": tcl_d}


def week_hits(st, setting, lo_ms, hi_ms):
    """Per Monday week start D in the window with a known regime/phase: (cell flags, gated, lower close 4 weeks later)."""
    out = []
    for x, D in enumerate(st["days"]):
        if (D - 4) % 7 != 0 or D * DAY < lo_ms or (D + 28) * DAY > hi_ms:
            continue
        if st["regime"][x] is None or st["phase"][x] is None:
            continue
        k0 = st["kk"][x]
        k1 = asof_idx(st["tcl"], (D + 28) * DAY)
        if k0 < 0 or k1 <= k0:
            continue
        out.append((st["regime"][x], st["phase"][x], bool(st["proxy"][setting][x]), bool(st["closes"][k1] < st["closes"][k0])))
    return out


def stat(g, days):
    g = np.asarray(g, float)
    if len(g) == 0:
        return {"n": 0, "days": 0}
    net = g - COST
    m, se = rk.cluster_mean_se(net, days)
    t = rk.t_stat(m, se)
    return {"n": len(g), "days": len(set(days)), "gross": float(g.mean()), "net": m, "se": se, "t": t, "p": rk.norm_p_two(t),
            "ci_lo": m - 1.96 * se, "ci_hi": m + 1.96 * se, "hit_net": float((net > 0).mean())}


def power(n_days, tf):
    """Count-only gate (prereg_gate formula): BLOCK when MDE + cost > 0.30 %. Unit %, sd OURS per TF."""
    if n_days <= 0:
        return {"mde": float("nan"), "gate": "BLOCK"}
    m = G.mde(n_days, SD[tf], FAMILY_M)
    return {"mde": m, "gate": "BLOCK" if m + COST > MAX_GROSS else "PASS"}


def cell_mask(regime, phase, cell):
    if cell == "ALL":
        return np.ones(len(regime), bool)
    r, p = cell.split("|")
    return (regime == r) & (phase == p)


def a_events(registry, lo_ms, hi_ms, root=L.SPOT_ROOT):
    """Bearish W12 close-pivot divergence on A_TF, per symbol; entry = close of the event bar, exit H bars later."""
    rows, states = [], {}
    for sym in SYMS:
        d1 = L.load_spot("1d", hi_ms, root, sym)
        st = day_state(d1, registry, hi_ms)
        states[sym] = st
        bars = L.load_spot(A_TF, hi_ms, root, sym)
        evs = S.find_events(bars, "bearish", "W12", A_TF)
        for e in evs:
            i = e["i"]
            if e["t_close"] < lo_ms or e["t_close"] >= hi_ms or i + H >= len(bars):
                continue
            x = int(e["t_close"] // DAY) - st["day0"]
            reg, ph = st["regime"][x], st["phase"][x]
            if reg is None or ph is None:
                continue
            g = -(bars[i + H]["c"] - bars[i]["c"]) / bars[i]["c"] * 100.0
            rows.append({"sym": sym, "day": int(bars[i]["t"] // DAY), "gross": g, "regime": reg, "phase": ph,
                         "in": np.array([st["proxy"][s][x] for s in A_SETTINGS], bool)})
        print(sym, "A events done", file=sys.stderr, flush=True)
    return rows, states


def a_table(rows, states, lo_ms, hi_ms, only=None, counts=False):
    """Per (setting, cell, group in/out): trade stats and the gate's hit rate. only = list of (setting key, cell) or None."""
    reg = np.array([r["regime"] for r in rows], object)
    ph = np.array([r["phase"] for r in rows], object)
    gross = np.array([r["gross"] for r in rows], float)
    day = np.array([r["day"] for r in rows])
    ins = np.array([r["in"] for r in rows]) if rows else np.zeros((0, len(A_SETTINGS)), bool)
    out = []
    for si, s in enumerate(A_SETTINGS):
        wk = [w for sym in SYMS for w in week_hits(states[sym], s, lo_ms, hi_ms)]
        for cell in CELLS:
            if only is not None and (skey(s), cell) not in only:
                continue
            cm = cell_mask(reg, ph, cell) if len(rows) else np.zeros(0, bool)
            a = cm & ins[:, si] if len(rows) else cm
            b = cm & ~ins[:, si] if len(rows) else cm
            row = {"setting": skey(s), "cell": cell, "baseline": s == A_BASELINE}
            ia = stat(gross[a], day[a]) if not counts else {"n": int(a.sum()), "days": len(set(day[a]))}
            row.update({"in_" + k: v for k, v in ia.items()})
            pw = power(ia["days"], A_TF)
            row.update({"mde": pw["mde"], "gate": pw["gate"]})
            if not counts:
                ib = stat(gross[b], day[b])
                row.update({"out_" + k: v for k, v in ib.items()})
                if ia["n"] > 1 and ib["n"] > 1:
                    df, se = rk.cluster_diff(gross[a], day[a], gross[b], day[b])
                    row.update({"excess_in_minus_out": df, "excess_t": rk.t_stat(df, se)})
            ws = [w for w in wk if cell == "ALL" or (w[0] == cell.split("|")[0] and w[1] == cell.split("|")[1])]
            gw = [w for w in ws if w[2]]
            row.update({"weeks": len(ws), "gated_weeks": len(gw), "gate_hit_rate": (sum(w[3] for w in gw) / len(gw)) if gw else float("nan"),
                        "base_hit_rate": (sum(w[3] for w in ws) / len(ws)) if ws else float("nan")})
            out.append(row)
    return out


# ---------------------------------------------------------------- Part B: fake-out filter per TF ------------------------------
def atr_series(bars, n=ATR_N):
    """Simple mean of the true range over the last n bars (index k uses bars k-n+1..k); None until n+1 bars exist."""
    tr = [None] * len(bars)
    for k in range(1, len(bars)):
        tr[k] = max(bars[k]["h"] - bars[k]["l"], abs(bars[k]["h"] - bars[k - 1]["c"]), abs(bars[k]["l"] - bars[k - 1]["c"]))
    out = [None] * len(bars)
    for k in range(n, len(bars)):
        out[k] = sum(tr[k - n + 1:k + 1]) / n
    return out


def entry_for(filt, bars, e, sgn, htf=None, vol_n=20):
    """(entry bar index j, entry price) or None. none: close of the event bar i. confirm1: bar i+1 must close beyond bar i's close
    in the signal direction, enter at its close. htf_rsi: last closed HTF RSI14 moved with the signal (long: rising vs the prior
    closed HTF bar; short: falling), enter at close of i. volume: v[i] > mean(v[i-20..i-1]). retest: research_kit.retest_entry."""
    i = e["i"]
    if filt == "none":
        return i, bars[i]["c"]
    if filt == "confirm1":
        if i + 1 >= len(bars):
            return None
        return (i + 1, bars[i + 1]["c"]) if sgn * (bars[i + 1]["c"] - bars[i]["c"]) > 0 else None
    if filt == "htf_rsi":
        tcl, v = htf
        k = asof_idx(tcl, e["t_close"])
        if k < 1:
            return None
        return (i, bars[i]["c"]) if sgn * (v[k] - v[k - 1]) > 0 else None
    if filt == "volume":
        if i < vol_n:
            return None
        return (i, bars[i]["c"]) if bars[i]["v"] > sum(b["v"] for b in bars[i - vol_n:i]) / vol_n else None
    if filt == "retest":
        ohlc = [(b["o"], b["h"], b["l"], b["c"]) for b in bars[i:min(len(bars), i + RETEST_N + 2)]]
        r = rk.retest_entry(ohlc, 0, e["close_b"], int(sgn), RETEST_N)
        return None if r is None else (i + r[0], r[1])
    raise ValueError(filt)


def simulate(bars, atr, j, px, sgn, h=H):
    """(gross % after H bars, fake_out flag) or None. Fake-out: within bars j+1..j+h price reaches px - sgn*1 ATR (adverse) before
    px + sgn*1 ATR (favourable); a bar touching both counts as adverse first (conservative). ATR is read at the entry bar j."""
    a = atr[j]
    if a is None or j + h >= len(bars):
        return None
    adv, fav = px - sgn * FAKE_ATR * a, px + sgn * FAKE_ATR * a
    fake = False
    for k in range(j + 1, j + h + 1):
        hit_adv = bars[k]["l"] <= adv if sgn > 0 else bars[k]["h"] >= adv
        hit_fav = bars[k]["h"] >= fav if sgn > 0 else bars[k]["l"] <= fav
        if hit_adv:
            fake = True
            break
        if hit_fav:
            break
    return sgn * (bars[j + h]["c"] - px) / px * 100.0, fake


def b_rows(registry, lo_ms, hi_ms, root=L.SPOT_ROOT):
    from MyTradingSys.backtest.layers.timeframe.tf_resample import resample
    rows = []
    for sym in SYMS:
        d1 = L.load_spot("1d", hi_ms, root, sym)
        for tf in B_TFS:
            bars = d1 if tf == "1d" else L.load_spot(tf, hi_ms, root, sym)
            hb = HTF[tf]
            hbars = resample(d1, "1w", registry) if hb == "1w" else (d1 if hb == "1d" else L.load_spot(hb, hi_ms, root, sym))
            htf = rsi_pairs(hbars, 14)
            atr = atr_series(bars)
            for kind, (sgn, _a) in S.KINDS.items():
                for e in S.find_events(bars, kind, "W12", tf):
                    if e["t_close"] < lo_ms or e["t_close"] >= hi_ms:
                        continue
                    for f in B_FILTERS:
                        en = entry_for(f, bars, e, sgn, htf)
                        if en is None:
                            continue
                        r = simulate(bars, atr, en[0], en[1], sgn)
                        if r is None:
                            continue
                        rows.append({"tf": tf, "filter": f, "sym": sym, "kind": kind, "day": int(bars[en[0]]["t"] // DAY),
                                     "gross": r[0], "fake": r[1]})
            print(sym, tf, "B done", file=sys.stderr, flush=True)
    return rows


def b_table(rows, counts=False):
    out = []
    for tf in B_TFS:
        for f in B_FILTERS:
            sel = [r for r in rows if r["tf"] == tf and r["filter"] == f]
            g = [r["gross"] for r in sel]
            d = [r["day"] for r in sel]
            row = {"tf": tf, "filter": f}
            row.update({"n": len(g), "days": len(set(d))} if counts else stat(g, d))
            row["fakeout_rate"] = (sum(r["fake"] for r in sel) / len(sel)) if sel else float("nan")
            pw = power(len(set(d)), tf)
            row.update({"mde": pw["mde"], "gate": pw["gate"]})
            out.append(row)
    return out


def pick(rows, keyfn):
    """Best by DEV in-sample net among rows with n >= MIN_N and days >= MIN_DAYS (first wins ties). None when no row qualifies."""
    ok = [r for r in rows if keyfn(r)[0] >= MIN_N and keyfn(r)[1] >= MIN_DAYS and keyfn(r)[2] == keyfn(r)[2]]
    return max(ok, key=lambda r: keyfn(r)[2]) if ok else None


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass", dest="pass_", required=True, choices=("count", "dev", "val"))
    ap.add_argument("--root", default=L.SPOT_ROOT)
    a = ap.parse_args()
    registry = json.loads((REPO / "MyTradingSys/backtest/layers/timeframe/registry.json").read_text(encoding="utf-8"))
    if a.pass_ == "val":
        if (HERE / "A_val.csv").exists():
            print("VALIDATION already read once; refusing")
            return 3
        picks = json.loads((HERE / "picks_dev.json").read_text(encoding="utf-8"))
        lo_ms, hi_ms = S.ms(splits.VALIDATION_START), S.ms(splits.VALIDATION_END)
    else:
        lo_ms, hi_ms = S.ms(pd.Timestamp(LONG_START)), S.ms(splits.DEV_END)
    counts = a.pass_ == "count"
    arows, states = a_events(registry, lo_ms, hi_ms, a.root)
    brows = b_rows(registry, lo_ms, hi_ms, a.root)
    if a.pass_ == "val":
        only = {(picks["A"][c]["setting"], c) for c in CELLS if picks["A"].get(c)}
        atab = a_table(arows, states, lo_ms, hi_ms, only=only)
        btab = [r for r in b_table(brows) if picks["B"].get(r["tf"]) and r["filter"] in ("none", picks["B"][r["tf"]]["filter"])]
        write_csv(HERE / "A_val.csv", atab)
        write_csv(HERE / "B_val.csv", btab)
        return finish_val(picks, atab, btab)
    atab = a_table(arows, states, lo_ms, hi_ms, counts=counts)
    btab = b_table(brows, counts=counts)
    tag = "count" if counts else "dev"
    write_csv(HERE / ("A_%s.csv" % tag), atab)
    write_csv(HERE / ("B_%s.csv" % tag), btab)
    if not counts:
        pa = {}
        for c in CELLS:
            r = pick([x for x in atab if x["cell"] == c], lambda x: (x["in_n"], x["in_days"], x.get("in_net", float("nan"))))
            pa[c] = {"setting": r["setting"], "dev_net": r["in_net"], "dev_n": r["in_n"], "gate": r["gate"]} if r else None
        pb = {}
        for tf in B_TFS:
            r = pick([x for x in btab if x["tf"] == tf], lambda x: (x["n"], x["days"], x.get("net", float("nan"))))
            pb[tf] = {"filter": r["filter"], "dev_net": r["net"], "dev_n": r["n"], "gate": r["gate"]} if r else None
        (HERE / "picks_dev.json").write_text(json.dumps({"A": pa, "B": pb}, indent=1), encoding="utf-8", newline="\n")
        st = states["BTCUSDT"]
        starts = S.week_starts(lo_ms, hi_ms)
        regs = [st["regime"][int(t // DAY) - st["day0"]] for t in starts]
        px = [bool(st["proxy"][A_BASELINE][int(t // DAY) - st["day0"]]) for t in starts]
        line = (rk.regime_mix_line(regs) + " | baseline proxy (1w, RSI14<=40, below SMA200, OURS) on in %d of %d weeks, BTCUSDT" % (sum(px), len(px)))
        (HERE / "regime_mix_dev.txt").write_text(line + "\n", encoding="utf-8", newline="\n")
        print(line)
    return 0


def finish_val(picks, atab, btab):
    """Holm over every pick tested (family m = FAMILY_M), verdict per cell, defaults.json."""
    tested = []
    for c in CELLS:
        p = picks["A"].get(c)
        r = next((x for x in atab if x["cell"] == c and p and x["setting"] == p["setting"]), None)
        tested.append(("A", c, p, r))
    for tf in B_TFS:
        p = picks["B"].get(tf)
        r = next((x for x in btab if x["tf"] == tf and p and x["filter"] == p["filter"]), None)
        tested.append(("B", tf, p, r))
    ps = [(t[3].get("in_p", t[3].get("p")) if t[3] else None) for t in tested]
    real = [(i, p) for i, p in enumerate(ps) if p is not None and p == p]
    adj = rk.holm([p for _, p in real], m=FAMILY_M) if real else []
    holm_of = {i: float(q) for (i, _), q in zip(real, adj)}
    verdicts = {}
    defaults = {"A": {}, "B": {}, "baseline": "rsi14<=40|1w|smaon", "labels": "OURS", "note": "null = keep d-bear-proxy-1104 baseline / no filter default"}
    for idx, (part, key, p, r) in enumerate(tested):
        if p is None:
            v, why = "no default: underpowered", "no setting reached n>=30 and >=20 days on DEV"
        else:
            lo = r.get("in_ci_lo", r.get("ci_lo")) if r else float("nan")
            n = r.get("in_n", r.get("n")) if r else 0
            q = holm_of.get(idx)
            if p["gate"] == "BLOCK":
                v, why = "no default: underpowered", "power gate BLOCK on the picked cell (capped INCONCLUSIVE)"
            elif n and lo == lo and lo > 0 and q is not None and q < 0.05:
                v, why = "DEFAULT", "VALIDATION fee-net CI above 0, Holm %.3f" % q
            else:
                v, why = "FAIL", "powered but VALIDATION fee-net CI not above 0 (n %s, CI lo %s, Holm %s)" % (n, lo, q)
        verdicts[(part, key)] = (v, why, holm_of.get(idx))
        if part == "A":
            defaults["A"][key] = p["setting"] if v == "DEFAULT" else None
        else:
            defaults["B"][key] = p["filter"] if v == "DEFAULT" else None
    (HERE / "defaults.json").write_text(json.dumps(defaults, indent=1), encoding="utf-8", newline="\n")
    (HERE / "verdicts_val.json").write_text(json.dumps({"%s:%s" % k: {"verdict": v[0], "why": v[1], "holm": v[2]} for k, v in verdicts.items()},
                                                       indent=1), encoding="utf-8", newline="\n")
    for k, v in verdicts.items():
        print(k, v)
    return 0


if __name__ == "__main__":
    sys.exit(main())
