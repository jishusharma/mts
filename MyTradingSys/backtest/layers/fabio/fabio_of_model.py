"""
MyTradingSys/backtest/layers/fabio/fabio_of_model.py - Fabio's CONDITIONAL model on true order-flow 1m bars.

Offline research module (never imported by live code; Fabio stays a separate layer, never a Tom filter).
Replaces the fixed-horizon "every trigger fire" test of FABIO_L1 with the model the videos describe
(state -> location -> trigger -> management), simulated bar by bar on 1m.

State   : session (UTC), fixed base Asia 00:00-08:00, London 08:00-13:30, NY 13:30-21:00 shifted by DST per B102 in
          session_bounds (London opens 07:00 in UK BST; NY opens 13:30 in US DST, else 14:30; widths kept). Prior session = the previous session in
          that sequence (Asia's prior = previous day's NY). Prior-session volume profile (10 USD bins, real footprint
          volume) -> POC, 70% value area (VAH/VAL), LVNs (interior local minima <= 0.5 x median bin) and HVNs
          (local maxima >= 0.6 x POC). Session state is fixed from the close of the first STATE_MIN minutes:
          close > VAH -> IMB_UP, close < VAL -> IMB_DN, else BALANCE. Trades only after that (causal).
Location: level in {VAH, VAL, POC, LVN} within TOL (0.1%).
Trigger : evaluated at tf-bar close (5m or 15m), all inputs known at close.
  BALANCE fade (absorption): bar approaches the level from one side, bar delta into the level >= k x mean |delta| of the
          previous 20 bars, big-trade delta on that side (>= 2 big prints, big buy vol > big sell vol for an up
          approach) [true flow only], and price fails: extreme within TOL of level, close back on the approach side.
  IMBALANCE with-break (aggression): aggression bar (open at/below the level for up, close beyond it, delta >= k x
          mean, big-trade delta same side), then within RETEST_BARS a bar that retests (extreme within TOL of the level)
          and holds (closes beyond). Entry after the retest bar closes.
Manage  : stop 1 tick beyond the trigger extreme (fade: trigger bar extreme; break: min/max of aggression and retest
          bar); +1R -> stop to breakeven; target = min(3R, nearest HVN/POC >= 1R away); optional trail (1R behind the
          running extreme) after +2R; exit at session end close. Within one 1m bar the stop is assumed hit before the
          target (worst case). Entry 'mkt' = next 1m open (taker); 'limit' (fades only) = limit at the level, fills
          if touched within 3 tf bars (maker). All exits taker.
Fees    : taker 0.05%/side, maker 0.02%; net R = gross R - (fee_in + fee_out) * entry / risk.
"""
import math
from bisect import bisect_left
from datetime import datetime, timezone

from MyTradingSys.backtest.layers.fabio.orderflow_bars import parse_fp

TICK = 0.1
TOL = 0.001
BIN = 10.0
STATE_MIN = 15
RETEST_BARS = 6
FILL_TF_BARS = 3
# Deribit BTC-PERPETUAL (API-verified 2026-09-26, fees.py): taker 5 bps/side (10 bps round trip), maker 0. B081 residue
# fixed 2026-10-06 (was the legacy 3.5 bp taker / -1.5 bp maker rebate pair). Resting limits fill only if price trades THROUGH the level by 1 tick
# (BACKTEST_PROTOCOL.md stress rule). Optional slippage (bps) is applied to taker legs by net_at().
from MyTradingSys.backtest.layers.fabio.v3.day_gates import us_dst, uk_bst  # B102: DST rules behind ny_open_utc/london_open_utc
SESSIONS = (("asia", 0, 480), ("london", 480, 810), ("ny", 810, 1260))  # fixed-UTC base [start, end); see session_bounds()
from MyTradingSys.backtest.fees import DERIBIT_TAKER as FEE_TAKER, DERIBIT_MAKER as FEE_MAKER  # B081
DAY_MS = 86400000


# ---------------------------------------------------------------- profile / levels
def build_profile(bars, flow="true"):
    """dict bin_low -> volume. flow 'true' = real footprint (fp column); 'proxy' = each bar's volume spread
    uniformly over [low, high] (the kline approximation)."""
    prof = {}
    for b in bars:
        if flow == "true":
            for k, bu, se in parse_fp(b["fp"]):
                prof[k] = prof.get(k, 0.0) + bu + se
        else:
            v = b["buy_vol"] + b["sell_vol"]
            lo, hi = b["l"], b["h"]
            k0, k1 = math.floor(lo / BIN) * BIN, math.floor(hi / BIN) * BIN
            if hi <= lo or k0 == k1:
                prof[k0] = prof.get(k0, 0.0) + v
                continue
            k = k0
            while k <= k1 + 1e-9:
                ov = min(hi, k + BIN) - max(lo, k)
                if ov > 0:
                    prof[k] = prof.get(k, 0.0) + v * ov / (hi - lo)
                k += BIN
    return prof


def profile_levels(prof, va_pct=0.70):
    """-> dict(poc, vah, val, lvns[list], hvns[list incl poc]) from a bin->volume dict; None if empty."""
    if not prof:
        return None
    lo = min(prof)
    n = int(round((max(prof) - lo) / BIN)) + 1
    v = [prof.get(lo + i * BIN, 0.0) for i in range(n)]
    total = sum(v)
    if total <= 0:
        return None
    poc_i = max(range(n), key=lambda i: (v[i], -i))
    a = z = poc_i
    acc = v[poc_i]
    while acc < va_pct * total and (a > 0 or z < n - 1):
        up = (v[z + 1] if z + 1 < n else 0.0) + (v[z + 2] if z + 2 < n else 0.0)
        dn = (v[a - 1] if a - 1 >= 0 else 0.0) + (v[a - 2] if a - 2 >= 0 else 0.0)
        if z >= n - 1 or (a > 0 and dn > up):
            take = min(2, a)
            for _ in range(take):
                a -= 1
                acc += v[a]
        else:
            take = min(2, n - 1 - z)
            for _ in range(take):
                z += 1
                acc += v[z]
    s = [(v[max(i - 1, 0)] + v[i] + v[min(i + 1, n - 1)]) / 3.0 for i in range(n)]
    nz = sorted(x for x in v if x > 0)
    med = nz[len(nz) // 2] if nz else 0.0
    lvns = [lo + i * BIN + BIN / 2 for i in range(1, n - 1)
            if v[i] < v[i - 1] and v[i] <= v[i + 1] and v[i] <= 0.5 * med]
    poc = lo + poc_i * BIN + BIN / 2
    hvns = sorted({poc} | {lo + i * BIN + BIN / 2 for i in range(1, n - 1)
                           if s[i] >= s[i - 1] and s[i] >= s[i + 1] and s[i] >= 0.6 * v[poc_i]})
    return {"poc": poc, "vah": lo + z * BIN + BIN, "val": lo + a * BIN, "lvns": lvns, "hvns": hvns}


def location_list(lv):
    out = [("VAH", lv["vah"]), ("VAL", lv["val"]), ("POC", lv["poc"])]
    out += [("LVN", p) for p in lv["lvns"]]
    return out


# ---------------------------------------------------------------- sessions
def session_bounds(date):
    """DST-aware UTC minute-of-day (name, start, end) for a UTC date (B102). london opens 07:00 UTC in UK BST else
    08:00, ny 13:30 in US DST else 14:30 (day_gates rules); the fixed-UTC widths 330/450 min and contiguity are kept,
    so asia = [0, london open). Applied on weekends too (24/7 data)."""
    ny = 810 if us_dst(date) else 870
    ln = 420 if uk_bst(date) else 480
    return (("asia", 0, ln), ("london", ln, ny), ("ny", ny, ny + 450))


def session_sequence(day_starts_ms):
    """Chronological [(name, start_ms, end_ms)] for the given UTC day-start timestamps (DST-aware, B102)."""
    seq = []
    for d0 in sorted(day_starts_ms):
        date = datetime.fromtimestamp(d0 / 1000, tz=timezone.utc).date()
        for name, a, b in session_bounds(date):
            seq.append((name, d0 + a * 60000, d0 + b * 60000))
    return seq


def session_state(close_at_state, lv):
    if close_at_state > lv["vah"]:
        return "imb_up"
    if close_at_state < lv["val"]:
        return "imb_dn"
    return "balance"


# ---------------------------------------------------------------- tf bars
def build_tf_bars(bars, tf):
    """Aligned tf-minute bars (complete buckets only) with 1m index range [i0, i1) and big-trade sums."""
    step = tf * 60000
    out, i, n = [], 0, len(bars)
    while i < n:
        t0 = bars[i]["t"] // step * step
        j = i
        while j < n and bars[j]["t"] < t0 + step:
            j += 1
        if j - i == tf and bars[i]["t"] == t0:
            sl = bars[i:j]
            out.append({"t": t0, "t_end": t0 + step, "i0": i, "i1": j, "o": sl[0]["o"], "c": sl[-1]["c"],
                        "h": max(x["h"] for x in sl), "l": min(x["l"] for x in sl),
                        "delta": sum(x["delta"] for x in sl),
                        "vol": sum(x["buy_vol"] + x["sell_vol"] for x in sl),
                        "big": {p: (sum(x[f"b{p}_buy_vol"] for x in sl), sum(x[f"b{p}_sell_vol"] for x in sl),
                                    sum(x[f"b{p}_buy_n"] for x in sl), sum(x[f"b{p}_sell_n"] for x in sl))
                                for p in ("99", "999")}})
        i = j
    return out


def mean_abs_delta_prev(tfbars, n=20):
    """avg[i] = mean |delta| of the previous n tf bars (None until n exist)."""
    a = [abs(b["delta"]) for b in tfbars]
    out, run = [], 0.0
    for i in range(len(a)):
        out.append(run / n if i >= n else None)
        run += a[i]
        if i >= n:
            run -= a[i - n]
    return out


def _big_ok(b, pct, direction, flow):
    """big-trade delta on `direction` side (+1 buy / -1 sell) with >= 2 prints; always True for proxy flow."""
    if flow != "true":
        return True
    bb, bs, nb, ns = b["big"][pct]
    return (bb > bs and nb >= 2) if direction > 0 else (bs > bb and ns >= 2)


# ---------------------------------------------------------------- events
def fade_events(tfbars, avg, levels, sess_lo, sess_hi, k, pct, flow):
    """BALANCE absorption fades over tf bars with index range [sess_lo, sess_hi). One event per bar."""
    ev = []
    for bi in range(sess_lo, sess_hi):
        b, av = tfbars[bi], avg[bi]
        if av is None or av <= 0:
            continue
        best = None
        for kind, p in levels:
            if b["o"] < p and p * (1 - TOL) <= b["h"] <= p * (1 + TOL) and b["c"] < p \
                    and b["delta"] >= k * av and _big_ok(b, pct, +1, flow):
                cand = (abs(p - b["o"]), "short", kind, p, b["h"] + TICK)
            elif b["o"] > p and p * (1 - TOL) <= b["l"] <= p * (1 + TOL) and b["c"] > p \
                    and -b["delta"] >= k * av and _big_ok(b, pct, -1, flow):
                cand = (abs(p - b["o"]), "long", kind, p, b["l"] - TICK)
            else:
                continue
            if best is None or cand[0] < best[0]:
                best = cand
        if best:
            ev.append({"bi": bi, "model": "balance_fade", "side": best[1], "kind": best[2], "level": best[3],
                       "stop": best[4]})
    return ev


def break_events(tfbars, avg, levels, sess_lo, sess_hi, direction, k, pct, flow):
    """IMBALANCE with-break: aggression bar through a level, then a retest bar that holds. direction +1 up / -1 down."""
    ev, used = [], set()
    for bi in range(sess_lo, sess_hi):
        a, av = tfbars[bi], avg[bi]
        if av is None or av <= 0:
            continue
        for kind, p in levels:
            if direction > 0:
                agg = a["o"] <= p * (1 + TOL) and a["c"] > p and a["delta"] >= k * av
            else:
                agg = a["o"] >= p * (1 - TOL) and a["c"] < p and -a["delta"] >= k * av
            if not agg or not _big_ok(a, pct, direction, flow):
                continue
            for ri in range(bi + 1, min(bi + 1 + RETEST_BARS, sess_hi)):
                r = tfbars[ri]
                if direction > 0:
                    if r["c"] < p * (1 - TOL):
                        break
                    if p * (1 - TOL) <= r["l"] <= p * (1 + TOL) and r["c"] > p:
                        if (ri, kind, p) not in used:
                            used.add((ri, kind, p))
                            ev.append({"bi": ri, "model": "imb_break", "side": "long", "kind": kind, "level": p,
                                       "stop": min(a["l"], r["l"]) - TICK})
                        break
                else:
                    if r["c"] > p * (1 + TOL):
                        break
                    if p * (1 - TOL) <= r["h"] <= p * (1 + TOL) and r["c"] < p:
                        if (ri, kind, p) not in used:
                            used.add((ri, kind, p))
                            ev.append({"bi": ri, "model": "imb_break", "side": "short", "kind": kind, "level": p,
                                       "stop": max(a["h"], r["h"]) + TICK})
                        break
    return ev


def break_limit_events(tfbars, avg, levels, sess_lo, sess_hi, direction, k, pct, flow):
    """IMBALANCE with-break, LIMIT version (causal): at the aggression bar close, rest a limit at the broken level
    (fills only if price trades through it by 1 tick within RETEST_BARS tf bars); stop 1 tick beyond the aggression
    bar extreme or the level, whichever is farther. No 'retest holds' information is used."""
    ev = []
    for bi in range(sess_lo, sess_hi):
        a, av = tfbars[bi], avg[bi]
        if av is None or av <= 0:
            continue
        for kind, p in levels:
            if direction > 0:
                agg = a["o"] <= p * (1 + TOL) and a["c"] > p and a["delta"] >= k * av
            else:
                agg = a["o"] >= p * (1 - TOL) and a["c"] < p and -a["delta"] >= k * av
            if not agg or not _big_ok(a, pct, direction, flow):
                continue
            if direction > 0:
                ev.append({"bi": bi, "model": "imb_break", "side": "long", "kind": kind, "level": p,
                           "stop": min(a["l"], p) - TICK})
            else:
                ev.append({"bi": bi, "model": "imb_break", "side": "short", "kind": kind, "level": p,
                           "stop": max(a["h"], p) + TICK})
    return ev


# ---------------------------------------------------------------- trade simulation
def simulate_trade(bars, first, last, side, entry_mode, level, stop, hvns, trail, fill_bars, min_risk_frac=0.0):
    """
    bars: 1m dicts. first = index of the first tradable 1m bar (entry bar), last = last tradable index (session end
    bar, inclusive; forced close-out at its close). Returns None (no fill / invalid) or a dict:
    gross_R, net_R, reason in {stop,be,trail,target,time,stop_fill_bar}, entry, risk, n_bars, exit_idx.
    min_risk_frac > 0 widens the stop to at least that fraction of the entry price (fee-survivable variant; 0 = the
    spec's tight stop just beyond the trigger extreme).
    """
    sgn = 1 if side == "long" else -1
    if first > last:
        return None
    if min_risk_frac > 0:
        ref = level if entry_mode == "limit" else bars[first]["o"]
        if abs(ref - stop) < min_risk_frac * ref:
            stop = ref - sgn * min_risk_frac * ref
    if entry_mode == "limit":
        j = None
        for q in range(first, min(first + fill_bars, last + 1)):
            if (sgn < 0 and bars[q]["h"] >= level + TICK) or (sgn > 0 and bars[q]["l"] <= level - TICK):
                j = q
                break
        if j is None:
            return None
        entry, fee_in, start = level, FEE_MAKER, j
        risk = abs(entry - stop)
        if risk <= 0 or (sgn > 0 and stop >= entry) or (sgn < 0 and stop <= entry):
            return None
        hit = bars[j]["l"] <= stop if sgn > 0 else bars[j]["h"] >= stop
        if hit:
            return _finish(-1.0, "stop_fill_bar", entry, risk, fee_in, j, j)
        start = j + 1
    else:
        entry, fee_in, start = bars[first]["o"], FEE_TAKER, first
        risk = abs(entry - stop)
        if risk <= 0 or (sgn > 0 and stop >= entry) or (sgn < 0 and stop <= entry):
            return None
    tgt = entry + sgn * 3 * risk
    cands = [h for h in hvns if sgn * (h - entry) >= risk]
    if cands:
        near = min(cands) if sgn > 0 else max(cands)
        tgt = min(tgt, near) if sgn > 0 else max(tgt, near)
    cur_stop, moved_be, trailing, ext = stop, False, False, entry
    for q in range(start, last + 1):
        b = bars[q]
        stopped = b["l"] <= cur_stop if sgn > 0 else b["h"] >= cur_stop
        if stopped:
            px = cur_stop
            if sgn > 0 and b["o"] < cur_stop or sgn < 0 and b["o"] > cur_stop:
                px = b["o"]
            reason = "trail" if trailing else ("be" if moved_be else "stop")
            return _finish(sgn * (px - entry) / risk, reason, entry, risk, fee_in, first, q)
        if (b["h"] >= tgt + TICK) if sgn > 0 else (b["l"] <= tgt - TICK):
            return _finish(sgn * (tgt - entry) / risk, "target", entry, risk, fee_in, first, q)
        ext = max(ext, b["h"]) if sgn > 0 else min(ext, b["l"])
        fav = sgn * (ext - entry) / risk
        if fav >= 1.0 and not moved_be:
            moved_be = True
            cur_stop = entry if sgn > 0 and cur_stop < entry or sgn < 0 and cur_stop > entry else cur_stop
        if trail and fav >= 2.0:
            trailing = True
            tr = ext - sgn * risk
            cur_stop = max(cur_stop, tr) if sgn > 0 else min(cur_stop, tr)
    return _finish(sgn * (bars[last]["c"] - entry) / risk, "time", entry, risk, fee_in, first, last)


def _finish(gross_r, reason, entry, risk, fee_in, i_in, i_out):
    """Exit fee: a resting target is maker; stops, breakeven/trail stops and the session-end exit are taker."""
    fee_out = FEE_MAKER if reason == "target" else FEE_TAKER
    legs = (1 if fee_in == FEE_TAKER else 0) + (0 if reason == "target" else 1)
    fees_r = (fee_in + fee_out) * entry / risk
    return {"gross_R": gross_r, "net_R": gross_r - fees_r, "reason": reason, "entry": entry, "risk": risk,
            "n_bars": i_out - i_in + 1, "exit_idx": i_out, "taker_legs": legs}


def net_at(t, slip=0.0):
    """Net R of a simulated trade with `slip` (fraction of price, e.g. 0.0002 = 2 bps) charged on each taker leg."""
    return t["net_R"] - t["taker_legs"] * slip * t["entry"] / t["risk"]


# ---------------------------------------------------------------- metrics
def trade_stats(net_rs, gross_rs=None, reasons=None):
    n = len(net_rs)
    if n == 0:
        return {"n": 0, "win": None, "avg_gross_R": None, "exp_net_R": None, "pf": None, "max_dd_R": None,
                "be_share": None}
    wins = [x for x in net_rs if x > 0]
    losses = [x for x in net_rs if x < 0]
    cum = peak = dd = 0.0
    for x in net_rs:
        cum += x
        peak = max(peak, cum)
        dd = max(dd, peak - cum)
    return {"n": n, "win": len(wins) / n,
            "avg_gross_R": (sum(gross_rs) / n) if gross_rs else None,
            "exp_net_R": sum(net_rs) / n,
            "pf": (sum(wins) / -sum(losses)) if losses else None,
            "max_dd_R": dd,
            "be_share": (sum(1 for r in reasons if r == "be") / n) if reasons else None}
