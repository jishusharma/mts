"""P0: the operator's daily-level rule, daily-bar simulator. Conventions frozen in PRE_REG_CANDLE_PILOT.md section 3 + Addendum A.

Variants: P0a long touch-entry / close-exit; P0c long close-confirmed entry; P0s short mirror of P0a; P0e entry ablation.
Bars: contiguous list of day bars {t,o,h,l,c}, t = bar open ms; `day_ms` = bar length (86400000 for a UTC day; the same code runs on shifted-anchor days).
Per-trade net = sign*ln(exit/entry) - 2*(fee+slip) - sign*funding.
"""
import sys
sys.dont_write_bytecode = True
import math
import random

FEE = 0.0005     # backtest/fees.py BINANCE_TAKER per side
SLIP = 0.0002    # per side, PRE_REG section 2


def _exit_hit(side, bars, j):
    return bars[j]["c"] < bars[j - 1]["c"] if side > 0 else bars[j]["c"] > bars[j - 1]["c"]


def simulate(bars, variant, funding, day_ms=86400000, fee=FEE, slip=SLIP):
    if variant not in ("P0a", "P0c", "P0s", "P0e"):
        raise ValueError(variant)
    side = -1 if variant == "P0s" else 1
    n = len(bars)
    trades = []
    i = 1
    open_at_end = False
    while i < n:
        b, L = bars[i], bars[i - 1]["o"]
        if variant in ("P0a", "P0s"):
            if side > 0:
                if b["o"] >= L:
                    e_px, t_e = b["o"], b["t"]
                elif b["h"] >= L:
                    e_px, t_e = L, b["t"] + day_ms // 2
                else:
                    i += 1
                    continue
            else:
                if b["o"] <= L:
                    e_px, t_e = b["o"], b["t"]
                elif b["l"] <= L:
                    e_px, t_e = L, b["t"] + day_ms // 2
                else:
                    i += 1
                    continue
            start = i
        elif variant == "P0c":
            if b["c"] > L:
                e_px, t_e, start = b["c"], b["t"] + day_ms - 1, i + 1
            else:
                i += 1
                continue
        else:  # P0e
            e_px, t_e, start = b["o"], b["t"], i
        j = start
        while j < n and not _exit_hit(side, bars, j):
            j += 1
        if j >= n:
            open_at_end = True
            break
        x_px, t_x = bars[j]["c"], bars[j]["t"] + day_ms - 1
        gross = side * math.log(x_px / e_px)
        fund = funding.sum(t_e, t_x)
        net = gross - 2 * (fee + slip) - side * fund
        trades.append({"entry_i": i, "exit_i": j, "entry_px": e_px, "exit_px": x_px, "t_entry": t_e, "t_exit": t_x,
                       "gross": gross, "fund": fund, "net": net, "days": j - i + 1})
        i = j + 1
    gross_d, net_d = [0.0] * n, [0.0] * n
    for tr in trades:
        e, x = tr["entry_i"], tr["exit_i"]
        for d in range(e, x + 1):
            ref0 = tr["entry_px"] if d == e else bars[d - 1]["c"]
            ref1 = tr["exit_px"] if d == x else bars[d]["c"]
            r = side * math.log(ref1 / ref0)
            w0 = tr["t_entry"] if d == e else bars[d]["t"] - 1
            w1 = tr["t_exit"] if d == x else bars[d]["t"] + day_ms - 1
            cost = (fee + slip if d == e else 0.0) + (fee + slip if d == x else 0.0)
            gross_d[d] += r
            net_d[d] += r - cost - side * funding.sum(w0, w1)
    return {"trades": trades, "gross_d": gross_d, "net_d": net_d, "side": side, "open_at_end": open_at_end}


def curve_stats(daily, periods=365):
    n = len(daily)
    mean = sum(daily) / n
    sd = math.sqrt(sum((x - mean) ** 2 for x in daily) / (n - 1)) if n > 1 else 0.0
    eq, peak, mdd = 0.0, 0.0, 0.0
    for x in daily:
        eq += x
        peak = max(peak, eq)
        mdd = min(mdd, eq - peak)
    return {"total_log": sum(daily), "sharpe": (mean / sd * math.sqrt(periods)) if sd > 0 else 0.0, "max_dd_log": mdd}


def random_null(bars, lens, side, n_perm=2000, seed=12345):
    """Mean GROSS log return per block for random non-overlapping placements of blocks with the given lengths
    (entry open of first day, exit close of last day). Returns the list of null means."""
    n, k = len(bars), len(lens)
    lo = [math.log(b["o"]) for b in bars]
    lc = [math.log(b["c"]) for b in bars]
    slack = n - sum(lens)
    if slack < 0:
        raise ValueError("blocks do not fit")
    rng = random.Random(seed)
    out = []
    for _ in range(n_perm):
        order = lens[:]
        rng.shuffle(order)
        pos = sorted(rng.sample(range(slack + k), k))
        s, acc = 0.0, 0
        for idx, L in enumerate(order):
            start = pos[idx] - idx + acc
            s += side * (lc[start + L - 1] - lo[start])
            acc += L
        out.append(s / k)
    return out
