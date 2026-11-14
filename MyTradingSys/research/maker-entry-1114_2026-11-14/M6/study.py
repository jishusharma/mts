"""M6: Europe-low sweep reclaim in the US session, maker entry at the swept low (PRE_REG maker-entry-1114).

Original: edge-session-sweep-reclaim-1113 (eur_low_sweep_reclaim_pooled_2026-11-13), best maker cell = LONG, exit HIGH (EH).
Signal (SOURCED, evaluated exactly as the original, on 5m bars aggregated from Binance spot 1m):
  weekdays; Europe 07:00-13:30Z EL/EH; first US-window (13:30-20:00Z) 5m bar with low < EL = sweep; reclaim = first 5m close > EL
  within 12 bars (sweep bar counts); stop S = lowest low sweep..reclaim bar; min risk 0.15 %; target EH; time stop 20:00Z.
Maker mapping (OURS, PRE_REG): resting buy limit at L = EL placed at the reclaim-bar close, fill model lib/maker_fill.simulate_maker.
Taker baseline = the original next-open entry, original machinery (touch stop/target, stop wins ties, exit last 5m close), 12 bp.

    python study.py            full run (acquires a slot dir F:\\MTS\\maker_slots\\slotN, BelowNormal)
"""
import ctypes, json, os, sys, time
from datetime import datetime, timezone
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import maker_fill as MF  # noqa: E402

M5, DAY = 300000, 86400000
EU0, EU1, US0, US1 = 84, 162, 162, 240           # 5m slots: 07:00, 13:30, 13:30, 20:00 UTC
RECLAIM_BARS = 12
MIN_RISK = 0.0015
SYMS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
START_MS = {"BTCUSDT": 1583020800000,            # 2020-03-01Z (original)
            "ETHUSDT": 1614556800000,            # 2021-03-01Z (original Bybit listing)
            "SOLUSDT": 1633046400000}            # 2021-10-01Z (original Bybit listing)
DEV_END = "2023-12-31"                           # PRE_REG split
ATR_N = 14
N_DRAWS = 1000
TAKER_FEE_12, TAKER_FEE_10 = 0.0006, 0.0005      # per side; 12 bp spec baseline, 10 bp = original RESULT fees


# ------------------------------------------------------------------ data
def agg5(m1, start_ms):
    """Aggregate 1m (t_ms,o,h,l,c) to aligned 5m arrays from the UTC day containing start_ms. Returns t0,o,h,l,c (nan = no 1m)."""
    t0 = start_ms - start_ms % DAY
    t = m1["t_ms"]
    k = int(np.searchsorted(t, t0, side="left"))
    t, o, h, l, c = t[k:], m1["o"][k:], m1["h"][k:], m1["l"][k:], m1["c"][k:]
    idx = ((t - t0) // M5).astype(np.int64)
    first = np.r_[0, np.nonzero(np.diff(idx))[0] + 1]
    last = np.r_[first[1:] - 1, len(idx) - 1]
    bi = idx[first]
    n = int(bi[-1]) + 1
    n += (-n) % 288
    A = np.full((4, n), np.nan)
    A[0, bi] = o[first]
    A[1, bi] = np.maximum.reduceat(h, first)
    A[2, bi] = np.minimum.reduceat(l, first)
    A[3, bi] = c[last]
    return t0, A[0], A[1], A[2], A[3]


def atr_at(h, l, c, j, n=ATR_N):
    """Mean true range of the n 5m bars ending at j (inclusive); uses only bars <= j."""
    if j - n < 0:
        return float("nan")
    hh, ll, pc = h[j - n + 1:j + 1], l[j - n + 1:j + 1], c[j - n:j]
    tr = np.maximum(hh - ll, np.maximum(np.abs(hh - pc), np.abs(ll - pc)))
    return float(np.nanmean(tr)) if np.isfinite(tr).any() else float("nan")


# ------------------------------------------------------------------ signal (SOURCED: exactly the original)
def day_levels(h, l, d0):
    h_eu, l_eu = h[d0 + EU0:d0 + EU1], l[d0 + EU0:d0 + EU1]
    if np.isnan(h_eu).sum() > 3 or np.isnan(l_eu).sum() > 3:
        return None
    return float(np.nanmin(l_eu)), float(np.nanmax(h_eu))


def find_event_long(o, h, l, c, d0, EL, EH):
    """Decision-time only: nothing after the reclaim bar j is read."""
    i0 = None
    for i in range(d0 + US0, d0 + US1):
        if np.isnan(l[i]) or np.isnan(h[i]):
            continue
        if l[i] < EL:
            i0 = i
            break
    if i0 is None:
        return None
    j = None
    for k in range(i0, min(i0 + RECLAIM_BARS, d0 + US1)):
        if np.isnan(c[k]):
            continue
        if c[k] > EL:
            j = k
            break
    if j is None or j + 1 >= d0 + US1 or np.isnan(o[j + 1]):
        return None
    S = float(np.nanmin(l[i0:j + 1]))
    return dict(i0=i0, j=j, S=S, EL=EL, EH=EH)


# ------------------------------------------------------------------ ORIGINAL taker baseline (next-open entry)
def taker_baseline(ev, o, h, l, c, d0, fee=TAKER_FEE_12):
    """Original machinery: entry at open of j+1, stop S (touch), target EH (touch), stop wins ties, exit at last 5m close.
    Returns dict(gross_R, net_R) or None when the original would not trade (min risk / target not beyond entry)."""
    e = ev["j"] + 1
    entry = float(o[e])
    risk = entry - ev["S"]
    if risk <= 0 or risk / entry < MIN_RISK or not ev["EH"] > entry:
        return None
    end = d0 + US1
    lo, hi = l[e:end], h[e:end]
    s_hit = np.nonzero(lo <= ev["S"])[0]
    t_hit = np.nonzero(hi >= ev["EH"])[0]
    si = s_hit[0] if len(s_hit) else 10 ** 9
    ti = t_hit[0] if len(t_hit) else 10 ** 9
    if si == 10 ** 9 and ti == 10 ** 9:
        v = c[e:end]
        v = v[~np.isnan(v)]
        xit = float(v[-1])
    else:
        xit = ev["S"] if si <= ti else ev["EH"]
    gross = (xit - entry) / risk
    return dict(gross_R=float(gross), net_R=float(gross - fee * (entry + xit) / risk), risk_pct=risk / entry)


# ------------------------------------------------------------------ MAKER mapping (OURS)
def maker_trade(ev, t0, d0, m1, tick, life_ms=M5, fill_bar_target=True):
    """Resting buy limit at L = EL placed at the reclaim-bar close; PRE_REG fill model via lib simulate_maker."""
    L, S, EH = ev["EL"], ev["S"], ev["EH"]
    if (L - S) / L < MIN_RISK:
        r = MF._miss("min_risk")
    elif not EH > L:
        r = MF._miss("no_target")
    else:
        sig_close = t0 + (ev["j"] + 1) * M5               # open time of the first 1m bar after the reclaim (signal) bar
        r = MF.simulate_maker(1, L, S, EH, sig_close, life_ms, t0 + (d0 + US1) * M5, False, m1, tick=tick,
                              fill_bar_target=fill_bar_target)
    return r


def split_of(date):
    return "DEV" if date <= DEV_END else "VAL"


def regime_by_day(m1_btc, t0):
    """OURS rule of the original: prior-day close vs SMA20 of prior daily closes: >+2 % up, <-2 % down, else range. Descriptive."""
    t0b, o, h, l, c = agg5(m1_btc, t0)
    nd = len(c) // 288
    dc = np.array([c[d * 288:(d + 1) * 288][~np.isnan(c[d * 288:(d + 1) * 288])][-1] for d in range(nd)])
    out = {}
    for d in range(20, nd):
        r = dc[d - 1] / dc[d - 20:d].mean() - 1
        out[int((t0b + d * DAY) // DAY)] = "up" if r > 0.02 else "down" if r < -0.02 else "range"
    return out


# ------------------------------------------------------------------ run
def collect(sym, m1, regimes):
    t0, o, h, l, c = agg5(m1, START_MS[sym])
    tick = MF.estimate_tick(m1)
    rows = []
    for d in range(len(o) // 288):
        d0 = d * 288
        dayms = t0 + d * DAY
        if datetime.fromtimestamp(dayms / 1000, timezone.utc).weekday() >= 5:
            continue
        lv = day_levels(h, l, d0)
        if lv is None:
            continue
        ev = find_event_long(o, h, l, c, d0, *lv)
        if ev is None:
            continue
        tk = taker_baseline(ev, o, h, l, c, d0)
        if tk is None:                                    # not an original signal (no original trade)
            continue
        tk10 = taker_baseline(ev, o, h, l, c, d0, fee=TAKER_FEE_10)
        date = datetime.fromtimestamp(dayms / 1000, timezone.utc).strftime("%Y-%m-%d")
        mk = maker_trade(ev, t0, d0, m1, tick)
        mk60 = maker_trade(ev, t0, d0, m1, tick, life_ms=12 * M5)
        atr = atr_at(h, l, c, ev["j"])
        rows.append(dict(sym=sym, date=date, split=split_of(date), day=int(dayms // DAY), regime=regimes.get(int(dayms // DAY), "na"),
                         ev=ev, d0=d0, t0=t0, tk=tk, tk10=tk10, mk=mk, mk60=mk60, atr=atr,
                         close_j=float(c[ev["j"]]), signal_close_ms=float(t0 + (ev["j"] + 1) * M5)))
    return rows, (t0, o, h, l, c), tick


def placebo_candidates(arrs, sym, t0, rows_val_days):
    """Random bars: weekday US-window 5m bars in VALIDATION with prior-level condition close > that day's EL (as the original
    placebo), valid ATR, bar must close before 19:55 so the order has a chance. Returns list of dict."""
    _, o, h, l, c = arrs
    out = []
    for d in range(len(o) // 288):
        d0 = d * 288
        dayms = t0 + d * DAY
        dt = datetime.fromtimestamp(dayms / 1000, timezone.utc)
        if dt.weekday() >= 5 or dt.strftime("%Y-%m-%d") <= DEV_END:
            continue
        lv = day_levels(h, l, d0)
        if lv is None:
            continue
        for k in range(d0 + US0, d0 + US1 - 1):
            if np.isnan(c[k]) or not c[k] > lv[0]:
                continue
            a = atr_at(h, l, c, k)
            if not np.isfinite(a) or a <= 0:
                continue
            out.append(dict(sym=sym, close=float(c[k]), atr=a, signal_close_ms=float(t0 + (k + 1) * M5),
                            time_stop_ms=float(t0 + (d0 + US1) * M5), day=int(dayms // DAY)))
    return out


def placebo(sig_val, cands, m1s, ticks, n_filled, n_draws=N_DRAWS, seed=7):
    """Like-for-like placebo. Each draw: pick a real VAL signal (its passive offset in ATR, stop % of L, target in R, symbol),
    pick a random same-symbol candidate bar, build L = close - offset*ATR, same stop %/target R, SAME simulate_maker; collect
    n_filled filled trades; statistic = mean net R. p = (1+#(draw >= observed))/(n_draws+1)."""
    rng = np.random.default_rng(seed)
    by_sym = {s: [x for x in cands if x["sym"] == s] for s in SYMS}
    prof = []
    for r in sig_val:
        ev = r["ev"]
        L, S, EH = ev["EL"], ev["S"], ev["EH"]
        if not r["atr"] > 0 or not (L - S) > 0 or not EH > L:
            continue
        prof.append(dict(sym=r["sym"], off=(r["close_j"] - L) / r["atr"], rpct=(L - S) / L, tR=(EH - L) / (L - S)))
    prof = [p for p in prof if by_sym[p["sym"]]]
    draws = np.empty(n_draws)
    for d in range(n_draws):
        got, tries, acc = 0, 0, 0.0
        while got < n_filled:
            tries += 1
            if tries > 400 * n_filled:
                raise RuntimeError("placebo fill rate too low")
            p = prof[int(rng.integers(len(prof)))]
            lst = by_sym[p["sym"]]
            cd = lst[int(rng.integers(len(lst)))]
            L = MF.placebo_limit(1, cd["close"], cd["atr"], p["off"])
            risk = L * p["rpct"]
            r = MF.simulate_maker(1, L, L - risk, L + p["tR"] * risk, cd["signal_close_ms"], M5, cd["time_stop_ms"], False,
                                  m1s[p["sym"]], tick=ticks[p["sym"]])
            if r["filled"]:
                got += 1
                acc += r["net_R"]
        draws[d] = acc / n_filled
    return draws


def lower_priority():
    try:
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
    except Exception:
        pass


def acquire_slot():
    os.makedirs(r"F:\MTS\maker_slots", exist_ok=True)
    while True:
        for i in range(4):
            p = rf"F:\MTS\maker_slots\slot{i}"
            try:
                os.mkdir(p)
                return p
            except FileExistsError:
                pass
        time.sleep(20)


def mean_or_nan(x):
    return float(np.mean(x)) if len(x) else float("nan")


def stats_block(rows, key="mk"):
    res = [dict(r[key], day=r["day"], signal_close_ms=r["signal_close_ms"]) for r in rows]
    s = MF.summarize(res)
    flt = [r for r in rows if r[key]["filled"]]
    tk12 = [r["tk"]["net_R"] for r in rows]
    tk10 = [r["tk10"]["net_R"] for r in rows]
    g_all = mean_or_nan([r["tk"]["gross_R"] for r in rows])
    g_flt = mean_or_nan([r["tk"]["gross_R"] for r in flt])
    s.update(taker12_net_R_all=mean_or_nan(tk12), taker10_net_R_all=mean_or_nan(tk10), taker_gross_R_all=g_all,
             taker12_net_R_on_filled=mean_or_nan([r["tk"]["net_R"] for r in flt]), taker_gross_R_on_filled=g_flt,
             adverse_selection_R=(g_flt - g_all) if flt else float("nan"),
             maker_gross_R_filled=s["mean_gross_R_filled"],
             net_R_per_signal=s["per_signal_R"])
    mix = {k: sum(1 for r in rows if r["regime"] == k) for k in ("up", "down", "range", "na")}
    s["regime_counts_signals"] = mix
    s["regime_counts_filled"] = {k: sum(1 for r in flt if r["regime"] == k) for k in ("up", "down", "range", "na")}
    s["miss_reasons"] = {}
    for r in rows:
        if not r[key]["filled"]:
            s["miss_reasons"][r[key]["reason_missed"]] = s["miss_reasons"].get(r[key]["reason_missed"], 0) + 1
    s["exit_types"] = {}
    for r in flt:
        s["exit_types"][r[key]["exit_type"]] = s["exit_types"].get(r[key]["exit_type"], 0) + 1
    s["hit_rate_filled"] = mean_or_nan([1.0 if r[key]["net_R"] > 0 else 0.0 for r in flt])
    return s


def main():
    lower_priority()
    slot = acquire_slot()
    try:
        m1s, ticks, rows, arrs = {}, {}, [], {}
        reg = None
        for sym in SYMS:
            m1s[sym] = MF.load_m1(sym)
            if sym == "BTCUSDT":
                reg = regime_by_day(m1s[sym], START_MS["BTCUSDT"] - 30 * DAY)
        for sym in SYMS:
            rr, a, tick = collect(sym, m1s[sym], reg)
            rows += rr
            arrs[sym] = a
            ticks[sym] = tick
            print(sym, "signals", len(rr), "tick", tick, flush=True)
        dev = [r for r in rows if r["split"] == "DEV"]
        val = [r for r in rows if r["split"] == "VAL"]
        out = dict(ticks=ticks, DEV=stats_block(dev), VAL=stats_block(val),
                   VAL_life60_sensitivity=stats_block(val, "mk60"), DEV_life60_sensitivity=stats_block(dev, "mk60"))
        out["VAL_per_symbol"] = {s: stats_block([r for r in val if r["sym"] == s]) for s in SYMS}
        out["VAL_per_regime"] = {g: stats_block([r for r in val if r["regime"] == g]) for g in ("up", "down", "range")
                                 if any(r["regime"] == g for r in val)}
        # placebo
        nf = out["VAL"]["n_filled"]
        if nf > 0:
            cands = []
            for sym in SYMS:
                cands += placebo_candidates(arrs[sym], sym, arrs[sym][0], None)
            draws = placebo(val, cands, m1s, ticks, nf)
            obs = out["VAL"]["mean_net_R_filled"]
            p = float((1 + np.sum(draws >= obs)) / (len(draws) + 1))
            out["placebo"] = dict(p=p, draw_mean=float(draws.mean()), draw_p95=float(np.percentile(draws, 95)), n_cands=len(cands),
                                  n_draws=len(draws), observed=obs)
        else:
            p = None
            out["placebo"] = dict(p=None)
        bh_rej, bh_adj = MF.benjamini_hochberg([p if p is not None else 1.0])
        g = MF.gates(out["VAL"], p, bh_rej[0])
        out["gates"] = dict(gates={str(k): v for k, v in g["gates"].items()}, passed=g["passed"], failed=g["failed"], thin=g["thin"],
                            note_gate5="BH computed over this single row only (m=1); lead must recompute over the 6 rows' placebo p")
        # raw per-signal rows for audit
        out["rows"] = [dict(sym=r["sym"], date=r["date"], split=r["split"], regime=r["regime"], EL=r["ev"]["EL"], EH=r["ev"]["EH"],
                            S=r["ev"]["S"], j=r["ev"]["j"], tk_gross=r["tk"]["gross_R"], tk_net12=r["tk"]["net_R"],
                            filled=r["mk"]["filled"], reason=r["mk"]["reason_missed"], exit=r["mk"]["exit_type"],
                            mk_gross=r["mk"]["gross_R"], mk_net=r["mk"]["net_R"]) for r in rows]
        json.dump(out, open(os.path.join(HERE, "results.json"), "w"), indent=1, default=float)
        print("ok")
    finally:
        try:
            os.rmdir(slot)
        except OSError:
            pass


if __name__ == "__main__":
    main()
