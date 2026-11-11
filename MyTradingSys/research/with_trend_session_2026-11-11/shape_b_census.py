"""Shape B of PRE_REG.md (Opus D1 "trend pullback to value"), DEV window 2022-01-01..2024-06-30 ONLY.

Everything reused by path, nothing copied: the pure functions of wavetrend_dots (ema, wavetrend), wt_context (structure) and wt_rsi_div
(rsi, divergence) are pulled out of the C30 source files by AST (those modules read argv/caches at import, so a plain import is impossible);
adx_di from backtest/layers/adx/adx.py; PhaseLabeler from eh-o2-phase-lens/phase_label.py; census_session_ladder (load_5m, to_15m, fees, ax).
Costs only from fees.py. Count pass first (no return is computed in it); returns only if final n >= 30. Run:
  python shape_b_census.py <cache_dir_of_5m_json> [out_dir]
"""
from __future__ import annotations

import ast
import bisect
import datetime as dt
import importlib.util
import math
import random
import shutil
import statistics as st
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
RES = HERE.parent                      # MyTradingSys/research
TF_DIR = RES / "tom_fabio_course_correction_2026-11-07"
EE_DIR = RES / "eagle_eyes_picture_2026-10-28"


def _load_path(name, path):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def _extract(path, names, ns):
    """Compile only the named top-level functions of a source file into ns (no import-time side effects)."""
    tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    keep = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    assert {n.name for n in keep} == set(names), (path, names)
    exec(compile(ast.Module(body=keep, type_ignores=[]), str(path), "exec"), ns)
    return ns


csl = _load_path("census_session_ladder", TF_DIR / "census_session_ladder.py")
fees, ax = csl.fees, csl.ax
_ns = {}
_extract(EE_DIR / "wavetrend_dots.py", ("ema", "wavetrend"), _ns)
assert "FEE, W, CAP = WD.FEE, 5, 60" in (EE_DIR / "wt_context.py").read_text(encoding="utf-8")
_ns["W"] = 5   # wt_context.W, asserted on the line above
_extract(EE_DIR / "wt_context.py", ("structure",), _ns)
_extract(EE_DIR / "wt_rsi_div.py", ("rsi", "divergence"), _ns)
wavetrend, structure, rsi, divergence = _ns["wavetrend"], _ns["structure"], _ns["rsi"], _ns["divergence"]
adx_di = _load_path("mts_adx", RES.parent / "backtest" / "layers" / "adx" / "adx.py").adx_di
phase_mod = _load_path("phase_label", RES / "edge_hunt_2026-11-09" / "results" / "eh-o2-phase-lens" / "phase_label.py")

UTC = dt.timezone.utc
DEV_START_MS = int(dt.datetime(2022, 1, 1, tzinfo=UTC).timestamp() * 1000)
DEV_END_MS = int(dt.datetime(2024, 7, 1, tzinfo=UTC).timestamp() * 1000)   # exclusive; nothing at/after this is loaded
WARMUP_MS = int(dt.datetime(2021, 10, 1, tzinfo=UTC).timestamp() * 1000)    # indicator warm-up only (DECISION OURS)
WT_LEVEL = 53          # C30 buy dot wt1 <= -53
ADX_MIN = 20           # OPUS 1 (OURS)
SLOPE_BARS = 5         # OPUS 2
FILL_BARS = 3          # OPUS 6
CAP = 60               # C30 X1 cap (bars)
BE_R = 1.0
MIN_VAH_R = 1.5
MIN_STOP = 0.0040      # size rule, reported only
MIN_MOVE = 0.0062
BIN_FRAC = 50 / 75000  # as the census
DRAWS = 30
SEED = 1111
MIN_N = 30
BLOCKS = ("asia", "london", "ny", "late")
BAD_PHASES = ("BEAR", "PEAK_WINDOW")
STAGES = ("0 C30 H2 trigger", "1 4h ADX>=20 & DI+>DI-", "2 ADX 5-bar slope>=0", "3 phase not BEAR/PEAK_WINDOW",
          "4 low in [VAL, POC]", "5 maker fill within 3 bars")


def block_of(t_ms):
    h = dt.datetime.fromtimestamp(t_ms / 1000, UTC).hour
    return "asia" if h < 7 else "london" if h < 13 else "ny" if h < 21 else "late"


def agg_k(b15, k):
    """k x 15m bars bucketed by timestamp, incomplete buckets dropped (as wavetrend_dots.agg)."""
    B = {}
    for b in b15:
        B.setdefault(b["t"] // (k * 900000), []).append(b)
    return [dict(t=g[0]["t"], o=g[0]["o"], h=max(x["h"] for x in g), l=min(x["l"] for x in g), c=g[-1]["c"])
            for _, g in sorted(B.items()) if len(g) == k]


def _last_closed(bars, width_ms, b15):
    """index of the last bar of `bars` closed by each 15m bar's close (-1 if none); closed bars only, no look-ahead."""
    closes = [x["t"] + width_ms for x in bars]
    return [bisect.bisect_right(closes, b["t"] + 900000) - 1 for b in b15]


def prepare(b15, phase_fn):
    """All indicator arrays aligned to b15, each value known at the CLOSE of that 15m bar."""
    assert b15 and b15[-1]["t"] < DEV_END_MS, "bars at/after 2024-07-01 must never be loaded"
    tup = [(b["t"], b["o"], b["h"], b["l"], b["c"]) for b in b15]
    w1, w2 = wavetrend(tup)
    R = rsi([b["c"] for b in b15])
    h2 = agg_k(b15, 8)
    tr2 = structure([(x["t"], x["o"], x["h"], x["l"], x["c"]) for x in h2])
    j2 = _last_closed(h2, 7200000, b15)
    h4 = agg_k(b15, 16)
    dip, dim, adx = adx_di([x["h"] for x in h4], [x["l"] for x in h4], [x["c"] for x in h4], 14)
    j4 = _last_closed(h4, 4 * 3600000, b15)
    day_bars = {}
    for b in b15:
        day_bars.setdefault(ax.day_of(b["t"]), []).append(b)
    return dict(b=b15, n=len(b15), T=[b["t"] for b in b15], O=[b["o"] for b in b15], H=[b["h"] for b in b15],
                L=[b["l"] for b in b15], C=[b["c"] for b in b15], w1=w1, w2=w2, R=R,
                tr2=[tr2[j] if j >= 0 else 0 for j in j2], h4=h4, dip=dip, dim=dim, adx=adx, j4=j4,
                day_bars=day_bars, phase_fn=phase_fn, _lv={})


def levels(P, t):
    day = ax.day_of(t)
    if day not in P["_lv"]:
        lv = ax.build_levels(P["day_bars"], day, BIN_FRAC)
        P["_lv"][day] = {n: p for n, p, _ in lv}
    return P["_lv"][day]


def adx_state(P, i):
    j = P["j4"][i]
    if j < 0 or P["adx"][j] is None:
        return "na", None
    a = P["adx"][j]
    sl = (a - P["adx"][j - SLOPE_BARS]) if j - SLOPE_BARS >= 0 and P["adx"][j - SLOPE_BARS] is not None else None
    if a >= ADX_MIN and P["dip"][j] > P["dim"][j]:
        return "ADX>=20 DI+>DI-", sl
    return ("ADX>=20 DI-" if a >= ADX_MIN else "ADX<20"), sl


def trigger(P, i):
    """C30 H2 on closed bars <= i: buy dot (wt1 crosses above wt2, wt1 <= -53) + bullish RSI divergence + 2h structure up."""
    w1, w2 = P["w1"], P["w2"]
    if i < 100 or w2[i] is None or w2[i - 1] is None:
        return False
    dot = w1[i] > w2[i] and w1[i - 1] <= w2[i - 1] and w1[i] <= -WT_LEVEL
    return bool(dot and divergence(P["H"], P["L"], P["R"], i, 1) and P["tr2"][i] == 1)


def gates(P, i):
    """Conditions 1-4 for bar i -> number passed in sequence (0..4), plus context. Closed bars only."""
    state, sl = adx_state(P, i)
    ctx = dict(adx_state=state, phase=P["phase_fn"](P["T"][i]), block=block_of(P["T"][i]))
    if state != "ADX>=20 DI+>DI-":
        return 0, ctx, None
    if sl is None or sl < 0:
        return 1, ctx, None
    if ctx["phase"] in BAD_PHASES:
        return 2, ctx, None
    lv = levels(P, P["T"][i])
    if "VAL" not in lv or "POC" not in lv or not (lv["VAL"] <= P["L"][i] <= lv["POC"]):
        return 3, ctx, None
    return 4, ctx, lv


def maker_fill(P, i):
    """Limit buy at the trigger close; filled by the first of the next 3 bars whose low trades THROUGH it (low < limit): DECISION OURS."""
    for f in range(i + 1, min(P["n"], i + 1 + FILL_BARS)):
        if P["L"][f] < P["C"][i]:
            return f
    return None


def stop_for(P, i, lv):
    q = min(range(i - 7, i + 1), key=lambda m: P["L"][m])
    return min(P["L"][q], lv["VAL"])


def scan(P, t_lo=DEV_START_MS, t_hi=DEV_END_MS):
    """Count pass: one record per C30 H2 trigger with the number of stages passed. Stages 0-4 use closed bars <= i only; the fill
    (stage 5) is an execution test. No return is computed."""
    out = []
    for i in range(100, P["n"] - 2):
        t = P["T"][i]
        if not (t_lo <= t < t_hi) or not trigger(P, i):
            continue
        g, ctx, lv = gates(P, i)
        rec = dict(i=i, t=t, reach=1 + g, lv=lv, **ctx)
        if g == 4:
            f = maker_fill(P, i)
            rec["fill"] = f
            if f is not None:
                rec["reach"] += 1
        out.append(rec)
    return out


def stage_counts(evs):
    return [sum(1 for e in evs if e["reach"] >= k + 1) for k in range(len(STAGES))]


def count_report(evs, P, t_lo=DEV_START_MS, t_hi=DEV_END_MS):
    lines = ["| stage | n |", "|---|---|"]
    for name, c in zip(STAGES, stage_counts(evs)):
        lines.append(f"| {name} | {c} |")
    for title, key, vals in (("phase", "phase", sorted({e["phase"] for e in evs})),
                             ("ADX state", "adx_state", sorted({e["adx_state"] for e in evs})),
                             ("session block (UTC)", "block", BLOCKS)):
        lines += ["", f"By {title} (cell = triggers that reached that stage):", "",
                  "| " + title + " | " + " | ".join(f"s{k}" for k in range(len(STAGES))) + " |", "|---|" + "---|" * len(STAGES)]
        for v in vals:
            sub = [e for e in evs if e[key] == v]
            lines.append(f"| {v} | " + " | ".join(str(sum(1 for e in sub if e["reach"] >= k + 1)) for k in range(len(STAGES))) + " |")
    pc = {}
    for d in range((t_hi - t_lo) // 86400000):
        ph = P["phase_fn"](t_lo + d * 86400000)
        pc[ph] = pc.get(ph, 0) + 1
    idx = {x["t"]: k for k, x in enumerate(P["h4"])}
    h4 = [x for x in P["h4"] if t_lo <= x["t"] < t_hi]
    ok = sum(1 for x in h4 if P["adx"][idx[x["t"]]] is not None and P["adx"][idx[x["t"]]] >= ADX_MIN)
    lines += ["", f"Regime mix: PHASE_LABEL days of DEV = {dict(sorted(pc.items()))} (research_kit.regime_tag not used).",
              f"ADX >= 20 share of 4h bars in DEV: {ok}/{len(h4)} = {100 * ok / max(1, len(h4)):.1f} %."]
    return "\n".join(lines)


# ------------------------------------------------------------------ returns (only reached when final n >= 30)
def cost_frac(model, exit_kind):
    f = fees.FEES_ALL_TAKER if model == "T" else fees.FEES_DERIBIT
    return f["entry"] + f[exit_kind] + fees.SLIPPAGE_RT_S13


def _finish(entry, stop, px, kind, kx, model, vah=None):
    stop_frac = (entry - stop) / entry
    gross = (px - entry) / entry
    net = gross - cost_frac(model, kind)
    return dict(kind=kind, k=kx, gross=gross, net=net, stop_frac=stop_frac, net_r=net / stop_frac, gross_r=gross / stop_frac,
                below_rule=stop_frac < MIN_STOP or (vah is not None and (vah - entry) / entry < MIN_MOVE))


def arm_a(P, i, s, stop, model):
    """C30 X1 exit unchanged: first closed bar k with wt1 > 0 (exit at open k+1) or 2h trend down; cap 60; stop first."""
    entry, n, O, L = P["C"][i], P["n"], P["O"], P["L"]
    if entry - stop <= 0:
        return None
    for k in range(s, min(n - 1, s + CAP)):
        if L[k] <= stop:
            return _finish(entry, stop, min(stop, O[k]), "stop", k, model)
        if P["w1"][k] > 0 or P["tr2"][k] == -1:
            return _finish(entry, stop, O[k + 1], "timeout", k + 1, model)
    kk = min(n - 1, s + CAP)
    if kk < s:
        return None
    return _finish(entry, stop, O[kk], "timeout", kk, model)


def arm_b(P, i, s, stop, vah, model):
    """Target prior-day VAH, stop to entry once high >= +1R (effective next bar), skip if VAH < 1.5R away; stop first; cap 60."""
    entry, n, O, H, L = P["C"][i], P["n"], P["O"], P["H"], P["L"]
    risk = entry - stop
    if vah is None or risk <= 0 or vah - entry < MIN_VAH_R * risk:
        return None
    be = False
    for k in range(s, min(n - 1, s + CAP)):
        se = entry if be else stop
        if L[k] <= se:
            return _finish(entry, stop, min(se, O[k]), "stop", k, model, vah)
        if H[k] >= vah:
            return _finish(entry, stop, vah, "target", k, model, vah)
        if H[k] >= entry + BE_R * risk:
            be = True
    kk = min(n - 1, s + CAP)
    if kk < s:
        return None
    return _finish(entry, stop, O[kk], "timeout", kk, model, vah)


def trade(P, arm, i, stop, vah, mode):
    """mode 'maker' (limit at close, model D, fill needed) or 'taker' (market at the trigger close, model T)."""
    if mode == "maker":
        s = maker_fill(P, i)
        if s is None:
            return None
        model = "D"
    else:
        s, model = i + 1, "T"
    return arm_a(P, i, s, stop, model) if arm == "A" else arm_b(P, i, s, stop, vah, model)


def run_arm(P, evs, arm, mode):
    """evs: events with gates 1-4 passed. One trade at a time per arm; unfilled / skipped (VAH<1.5R) counted."""
    res, busy, skipped = [], -1, 0
    for e in evs:
        if e["i"] <= busy:
            continue
        r = trade(P, arm, e["i"], stop_for(P, e["i"], e["lv"]), e["lv"].get("VAH"), mode)
        if r is None:
            skipped += 1
            continue
        busy = r["k"]
        res.append(r)
    return res, skipped


def trigger_alone(P, t_lo=DEV_START_MS, t_hi=DEV_END_MS):
    """C30 H2 exactly: entry open i+1, X1 exit (2h-trend guard), cap 60, one at a time; net RETURN under the taker model (no stop)."""
    out, busy = [], -1
    for i in range(100, P["n"] - 2):
        if not (t_lo <= P["T"][i] < t_hi) or i <= busy or not trigger(P, i):
            continue
        E, n = P["O"][i + 1], P["n"]
        kx = None
        for k in range(i + 1, min(n - 1, i + 1 + CAP)):
            if P["w1"][k] > 0 or P["tr2"][k] == -1:
                kx = k
                break
        px = P["O"][kx + 1] if kx is not None else None
        if kx is None:
            kx = min(n - 2, i + CAP)
            px = P["O"][kx + 1]
        busy = kx
        out.append((px - E) / E - cost_frac("T", "timeout"))
    return out


def mean_se(xs):
    n = len(xs)
    if n == 0:
        return float("nan"), float("nan")
    m = sum(xs) / n
    return m, (st.stdev(xs) / math.sqrt(n) if n > 1 else float("nan"))


def p_one_sided(xs):
    m, se = mean_se(xs)
    return 0.5 * math.erfc((m / se) / math.sqrt(2)) if se == se and se > 0 else float("nan")


def holm(ps):
    order = sorted(range(len(ps)), key=lambda k: ps[k])
    adj, run = [None] * len(ps), 0.0
    for r, k in enumerate(order):
        run = max(run, min(1.0, (len(ps) - r) * ps[k]))
        adj[k] = run
    return adj


def random_control(P, pool, n_ev, arm, draws=DRAWS, seed=SEED):
    """Random entries under the same gates 1-4 (no trigger): same maker procedure, stop = lower of last-8-bar low and VAL."""
    rng = random.Random(seed)
    means = []
    for _ in range(draws):
        xs = []
        for i in rng.sample(pool, min(n_ev, len(pool))):
            lv = levels(P, P["T"][i])
            r = trade(P, arm, i, stop_for(P, i, lv), lv.get("VAH"), "maker")
            if r:
                xs.append(r["net_r"])
        if xs:
            means.append(sum(xs) / len(xs))
    return means


def gated_pool(P, t_lo=DEV_START_MS, t_hi=DEV_END_MS):
    return [i for i in range(100, P["n"] - 2) if t_lo <= P["T"][i] < t_hi and gates(P, i)[0] == 4]


def evaluate(P, evs):
    s4 = [e for e in evs if e["reach"] >= 5]
    out, pool = {}, gated_pool(P)
    for arm in ("A", "B"):
        mk, sk = run_arm(P, s4, arm, "maker")
        tk, skt = run_arm(P, s4, arm, "taker")
        out[arm] = dict(maker=mk, taker=tk, skip_maker=sk, skip_taker=skt, ctrl=random_control(P, pool, len(mk), arm))
    out["alone"] = trigger_alone(P)
    pa = [p_one_sided([r["net_r"] for r in out[a]["maker"]]) for a in ("A", "B")]
    out["holm"] = dict(p=pa, adj=holm(pa) if all(p == p for p in pa) else [float("nan")] * 2)
    return out


def verdict(ev):
    lines, refuted = [], False
    for a in ("A", "B"):
        m, se = mean_se([r["net_r"] for r in ev[a]["maker"]])
        t, _ = mean_se([r["net_r"] for r in ev[a]["taker"]])
        ctrl = ev[a]["ctrl"]
        ge = (sum(1 for c in ctrl if c >= m) / len(ctrl)) if ctrl else float("nan")
        r1, r2, r3 = not (m > 0), not (t > 0), not (ge <= 0.05)
        lines.append(f"- Arm {a} maker net R {m:+.3f} (SE {se:.3f}, n {len(ev[a]['maker'])}) <= 0 ? {'REFUTED' if r1 else 'not refuted'}")
        lines.append(f"- Arm {a} taker net R {t:+.3f} (n {len(ev[a]['taker'])}) <= 0 ? {'REFUTED' if r2 else 'not refuted'}")
        lines.append(f"- Arm {a} beats random entries (control >= event in {100 * ge:.0f} % of {len(ctrl)} draws; need <= 5 %)? "
                     f"{'REFUTED' if r3 else 'not refuted'}")
        refuted = refuted or r1 or r2 or r3
    ta, sa = mean_se(ev["alone"])
    fm, fse = mean_se([r["net"] for r in ev["A"]["taker"]])
    se_d = math.sqrt((sa if sa == sa else 0) ** 2 + (fse if fse == fse else 0) ** 2)
    r4 = not (fm - ta >= se_d)
    lines.append(f"- Filtered taker arm A mean net return {100 * fm:+.3f} % vs C30 trigger alone {100 * ta:+.3f} % (n {len(ev['alone'])}); "
                 f"difference {100 * (fm - ta):+.3f} % vs 1 SE of the difference {100 * se_d:.3f} %: {'REFUTED' if r4 else 'not refuted'}")
    refuted = refuted or r4
    adj = ev["holm"]["adj"]
    lines.append(f"- Holm (m=2) adjusted one-sided p, arms A/B: {adj[0]:.3f} / {adj[1]:.3f}")
    lines.append("- Testnet: net R <= 0 after 30 trades: PENDING (forward slot)")
    inconclusive = not all(a == a and a < 0.05 for a in adj)
    return ("FAIL" if refuted else ("INCONCLUSIVE" if inconclusive else "PASS-CANDIDATE")), lines


def result_report(ev):
    word, vl = verdict(ev)
    rows = ["| arm / model | n | skipped | mean net R | SE | win | BELOW-SIZE-RULE n |", "|---|---|---|---|---|---|---|"]
    for a in ("A", "B"):
        for mode in ("maker", "taker"):
            rs = ev[a][mode]
            m, se = mean_se([r["net_r"] for r in rs])
            w = sum(1 for r in rs if r["net"] > 0) / len(rs) if rs else float("nan")
            rows.append(f"| {a} {mode} | {len(rs)} | {ev[a]['skip_' + mode]} | {m:+.3f} | {se:.3f} | {100 * w:.0f} % | "
                        f"{sum(1 for r in rs if r['below_rule'])} |")
    return word, f"# Shape B result\n\n**{word}**\n\n" + "\n".join(rows) + "\n\n## Refutation lines\n\n" + "\n".join(vl) + "\n"


def load_dev(cache):
    """csl.load_5m on a temp copy of ONLY the monthly files before 2024-07 (the sealed window is never opened), then t < DEV_END_MS."""
    tmp = Path(tempfile.mkdtemp(prefix="shape_b_dev_"))
    for p in sorted(Path(cache).glob("20*.json")):
        if p.stem < "2024-07":
            shutil.copy(p, tmp / p.name)
    b5 = [b for b in csl.load_5m(tmp) if b["t"] < DEV_END_MS]
    shutil.rmtree(tmp, ignore_errors=True)
    assert b5 and max(b["t"] for b in b5) < DEV_END_MS
    return b5


def daily_from_5m(b5):
    days = {}
    for b in b5:
        d = (b["t"] // 86400000) * 86400000
        x = days.setdefault(d, [d, b["h"], b["l"], b["c"]])
        x[1], x[2], x[3] = max(x[1], b["h"]), min(x[2], b["l"]), b["c"]
    return [tuple(days[d]) for d in sorted(days)]


def main(cache, out_dir=HERE):
    out_dir = Path(out_dir)
    b5 = load_dev(cache)
    lab = phase_mod.PhaseLabeler(daily_from_5m(b5))
    b15 = [b for b in csl.to_15m(b5) if b["t"] >= WARMUP_MS]
    P = prepare(b15, lab.phase)
    evs = scan(P)
    final_n = stage_counts(evs)[-1]
    txt = ("# Shape B counts (DEV 2022-01-01..2024-06-30, no returns)\n\n"
           f"15m bars {len(b15)} (warm-up from 2021-10-01). Overlap (one trade at a time) NOT removed in this table.\n\n"
           + count_report(evs, P) + f"\n\nFinal n (after maker fill) = {final_n}; gate n >= {MIN_N}.\n")
    (out_dir / "SHAPE_B_COUNTS.md").write_text(txt, encoding="utf-8")
    print(txt)
    if final_n < MIN_N:
        res = (f"# Shape B result\n\n**INSUFFICIENT n**: final n = {final_n} < {MIN_N} on DEV. No backtest; no return computed. "
               "Shape B goes straight to the testnet-forward slot (PRE_REG.md, OPUS.md D1 step 2).\n")
        (out_dir / "SHAPE_B_RESULT.md").write_text(res, encoding="utf-8")
        print(res)
        return
    word, res = result_report(evaluate(P, evs))
    (out_dir / "SHAPE_B_RESULT.md").write_text(res, encoding="utf-8")
    print(res)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else HERE)
