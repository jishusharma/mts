"""
MyTradingSys/backtest/bt/bt_engine.py - 1m bar trade simulator (T051 L3). Opus 5.5, 2026-09-27.
(NUC draft 012 rejected: wrong R accounting and tests that contradicted the gap rule; see BT_BUILD_NOTES.md.)
Stdlib only. Bars: dicts {t,o,h,l,c}, t = open time epoch ms. Conventions per BACKTEST_PROTOCOL.md §4:
- scanning starts at the first bar with t > entry_t (no look-ahead);
- stop tested on mark bars when given (fallback: trade bar), targets on trade bars;
- same-bar stop+target: stop_first=True -> stop takes the whole remaining size (conservative);
- gap through the stop -> fill at the bar open (worse); targets fill at their limit price (maker),
  and only when price trades THROUGH the limit by `target_through` (default 0.0 = touch; B151 callers pass the tick);
- entry, stop and timeout pay taker; funding charged at each settlement s with t_in < s <= t_out while size
  remains (FORMULAS 13): t_in = open of the first scanned bar (the entry instant), t_out = close instant of the
  exit bar (open + 60000). funding is REQUIRED (B103, as trade_costs.funding_paid): None raises, a non-empty list
  that does not span [t_in, t_out] raises, funding=[] is the explicit "no funding model" (charges 0, never raises).
All R figures are per unit size 1.0: R = abs(entry - stop).
"""
import bisect


def simulate_trade(side, entry_price, entry_t, stop, targets, bars, mark_bars=None, funding=None,
                   taker_fee=0.0005, maker_fee=0.0, max_bars=1440, stop_first=True, target_through=0.0):
    if side not in ("long", "short"):
        raise ValueError("side must be long or short")
    if funding is None:
        raise ValueError("funding=None: pass the funding records covering the hold, or [] for the explicit "
                         "no-funding model (B103 fail closed)")
    if targets and abs(sum(f for _, f in targets) - 1.0) > 1e-9:
        raise ValueError("target fractions must sum to 1.0")
    sgn = 1.0 if side == "long" else -1.0
    risk = abs(entry_price - stop)
    if risk <= 0:
        raise ValueError("stop must differ from entry")
    if sgn * (stop - entry_price) >= 0:
        raise ValueError("stop on the wrong side of entry")

    def r_of(px):
        return sgn * (px - entry_price) / risk

    open_t = sorted(targets, key=lambda x: sgn * x[0])  # nearest target first
    remaining = 1.0
    fills = []            # (t, price, fraction, kind)
    gross_r = 0.0
    fee_r = taker_fee * entry_price / risk        # entry on size 1.0
    ambiguous = 0
    mae = mfe = 0.0
    fund_evt = sorted(funding)
    fund_times = [t for t, _ in fund_evt]
    funding_paid_pct = 0.0
    last_t = entry_t
    t_in = None                                   # entry instant = open of the first scanned bar
    scanned = 0
    exit_t = None

    def fill(t, px, frac, kind):
        nonlocal remaining, gross_r, fee_r
        fills.append((t, px, frac, kind))
        gross_r += frac * r_of(px)
        fee_r += frac * (maker_fee if kind == "target" else taker_fee) * px / risk
        remaining -= frac
        if remaining < 1e-12:
            remaining = 0.0

    for b in bars:
        if b["t"] <= entry_t:
            continue
        scanned += 1
        if t_in is None:
            t_in = last_t = b["t"]
        # funding settlements s with last_t < s <= bar close instant (open + 60000); first bar: t_in < s
        bar_end = b["t"] + 60000
        i = bisect.bisect_right(fund_times, last_t)
        while i < len(fund_times) and fund_times[i] <= bar_end and remaining > 0:
            rate = fund_evt[i][1]
            paid = sgn * rate * remaining * b["c"] / entry_price   # fraction of entry notional
            funding_paid_pct += paid * 100.0
            i += 1
        last_t = bar_end

        mk = (mark_bars or {}).get(b["t"], b)
        # excursions on trade bars
        mae = min(mae, r_of(b["l"] if sgn > 0 else b["h"]))
        mfe = max(mfe, r_of(b["h"] if sgn > 0 else b["l"]))

        stop_hit = (mk["l"] <= stop) if sgn > 0 else (mk["h"] >= stop)
        hit_targets = [(p, f) for p, f in open_t
                       if ((b["h"] >= p + target_through) if sgn > 0 else (b["l"] <= p - target_through))]
        if stop_hit and hit_targets:
            ambiguous += 1
        gapped = (b["o"] <= stop) if sgn > 0 else (b["o"] >= stop)
        stop_px = b["o"] if gapped else stop

        if stop_hit and (stop_first or not hit_targets):
            fill(b["t"], stop_px, remaining, "stop")
        else:
            for p, f in hit_targets:
                fill(b["t"], p, min(f, remaining), "target")
                open_t.remove((p, f))
            if stop_hit and remaining > 0:
                fill(b["t"], stop_px, remaining, "stop")
        if remaining == 0:
            exit_t = b["t"]
            break
        if scanned >= max_bars:
            fill(b["t"], b["c"], remaining, "timeout")
            exit_t = b["t"]
            break

    if fund_evt and t_in is not None and (t_in < fund_evt[0][0] or last_t > fund_evt[-1][0]):
        raise ValueError(f"funding records cover [{fund_evt[0][0]}, {fund_evt[-1][0]}] but the hold is "
                         f"({t_in}, {last_t}]; load funding for the whole hold (B103) or pass [] for no funding model")

    if exit_t is None:  # ran out of data
        return {"exit_reason": "open_at_end", "exit_t": None, "bars_held": scanned, "gross_r": gross_r,
                "net_r": None, "pnl_pct_net": None, "fills": fills, "mae_r": mae, "mfe_r": mfe,
                "ambiguous_bars": ambiguous, "funding_paid_pct": funding_paid_pct, "remaining": remaining}

    kinds = {k for *_, k in fills}
    reason = kinds.pop() if len(kinds) == 1 else "mixed"
    reason = {"target": "targets"}.get(reason, reason)
    funding_r = (funding_paid_pct / 100.0) * entry_price / risk
    net_r = gross_r - fee_r - funding_r
    return {"exit_reason": reason, "exit_t": exit_t, "bars_held": scanned, "gross_r": gross_r, "net_r": net_r,
            "pnl_pct_net": net_r * risk / entry_price * 100.0, "fills": fills, "mae_r": mae, "mfe_r": mfe,
            "ambiguous_bars": ambiguous, "funding_paid_pct": funding_paid_pct, "remaining": 0.0}
