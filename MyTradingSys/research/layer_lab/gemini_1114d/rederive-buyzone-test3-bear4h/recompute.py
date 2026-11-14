"""Blind re-derivation of buyzone_test3_bear4h_2026-11-14 from PRE_REG.md and FORMULAS.md."""

import json
import math
import os
import random
from datetime import datetime, timezone
from pathlib import Path

CACHE_ROOT = Path(os.environ.get("MTS_DATA_CACHE", "C:/Users/e-ngineers/MTS_data_cache"))
DIR_1D = CACHE_ROOT / "binance_spot_1d"
DIR_4H = CACHE_ROOT / "binance_spot_4h"
DIR_FUND = CACHE_ROOT / "bybit_funding"

COINS = [
    "BTC", "ETH", "BNB", "XRP", "ADA", "DOGE", "SOL", "LTC", "LINK", "TRX",
    "DOT", "AVAX", "ATOM", "ETC", "XLM", "BCH", "NEO", "UNI", "NEAR", "FIL",
    "ALGO", "VET",
]

FOUR_H_MS = 4 * 3600 * 1000
DAY_MS = 24 * 3600 * 1000


def utc_date_str(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d")


def utc_day_num(ms: int) -> int:
    return ms // DAY_MS


def sma(values, length):
    out = [None] * len(values)
    if len(values) < length:
        return out
    s = sum(values[:length])
    out[length - 1] = s / length
    for i in range(length, len(values)):
        s += values[i] - values[i - length]
        out[i] = s / length
    return out


def wilder_rsi(closes, period=14):
    """Textbook Wilder RSI per FORMULAS.md section 1."""
    n = len(closes)
    out = [None] * n
    if n <= period:
        return out
    deltas = [closes[i] - closes[i - 1] for i in range(1, n)]
    avg_gain = sum(max(d, 0.0) for d in deltas[:period]) / period
    avg_loss = sum(max(-d, 0.0) for d in deltas[:period]) / period

    def calc_rsi(ag, al):
        if al == 0.0:
            return 100.0 if ag > 0.0 else 50.0
        rs = ag / al
        return 100.0 - 100.0 / (1.0 + rs)

    out[period] = calc_rsi(avg_gain, avg_loss)
    for i in range(period, len(deltas)):
        d = deltas[i]
        gain = max(d, 0.0)
        loss = max(-d, 0.0)
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
        out[i + 1] = calc_rsi(avg_gain, avg_loss)
    return out


def wilder_atr(bars, period=14):
    """Wilder ATR (RMA of TR, SMA seed of first `period` TRs starting at i=1)."""
    n = len(bars)
    out = [None] * n
    if n <= period:
        return out
    tr = [0.0] * n
    for i in range(1, n):
        h = bars[i][2]
        l = bars[i][3]
        pc = bars[i - 1][4]
        tr[i] = max(h - l, abs(h - pc), abs(l - pc))
    atr = sum(tr[1 : period + 1]) / period
    out[period] = atr
    for i in range(period + 1, n):
        atr = (atr * (period - 1) + tr[i]) / period
        out[i] = atr
    return out


def bollinger_upper(closes, length=20, mult=2.0):
    """Upper Bollinger Band using population stdev per FORMULAS.md section 22."""
    n = len(closes)
    out = [None] * n
    for i in range(length - 1, n):
        win = closes[i - length + 1 : i + 1]
        mean = sum(win) / length
        var = sum((x - mean) ** 2 for x in win) / length
        sd = math.sqrt(var)
        out[i] = mean + mult * sd
    return out


def compute_daily_phases(bars_1d):
    """Return dict: day_num -> (bear_flag, test1_phase)."""
    n = len(bars_1d)
    closes = [b[4] for b in bars_1d]
    highs = [b[2] for b in bars_1d]
    lows = [b[3] for b in bars_1d]
    sma200 = sma(closes, 200)
    sma350 = sma(closes, 350)

    out = {}
    for t in range(n):
        if t < 349 or sma350[t] is None:
            continue
        # Check all required windows for Test 1 phases
        # DD over last 365 bars (or available if >= 350)
        dd_start = max(0, t - 364)
        max_h = max(highs[dd_start : t + 1])
        dd = 1.0 - closes[t] / max_h if max_h > 0 else 0.0

        up = (
            sma200[t] is not None
            and t >= 229
            and sma200[t - 30] is not None
            and closes[t] > sma200[t]
            and sma200[t] > sma200[t - 30]
        )

        higher_low = False
        if t >= 179:
            recent_low = min(lows[t - 59 : t + 1])
            prior_low = min(lows[t - 179 : t - 59])
            higher_low = recent_low >= prior_low

        base = (not up) and (dd >= 0.40) and higher_low

        postpeak_bear = (
            (not up)
            and (not base)
            and closes[t] < sma350[t]
            and t >= 379
            and sma350[t - 30] is not None
            and sma350[t] < sma350[t - 30]
            and dd >= 0.40
        )

        down = (
            (not up)
            and (not base)
            and (not postpeak_bear)
            and sma200[t] is not None
            and t >= 229
            and sma200[t - 30] is not None
            and closes[t] < sma200[t]
            and sma200[t] < sma200[t - 30]
        )

        if up:
            phase = "UP"
        elif base:
            phase = "BASE"
        elif postpeak_bear:
            phase = "POSTPEAK_BEAR"
        elif down:
            phase = "DOWN"
        else:
            phase = "RANGE"

        bear = (closes[t] < sma350[t]) and (not base) and (not up)
        out[utc_day_num(bars_1d[t][0])] = (bear, phase)
    return out


def load_coin_data(coin):
    sym = f"{coin}USDT"
    with open(DIR_1D / f"{sym}.json", "r", encoding="utf-8") as f:
        b1d = json.load(f)[:-1]  # drop last (possibly partial) bar
    with open(DIR_4H / f"{sym}.json", "r", encoding="utf-8") as f:
        b4h = json.load(f)[:-1]  # drop last (possibly partial) bar
    fund_path = DIR_FUND / f"{sym}.json"
    if fund_path.exists():
        with open(fund_path, "r", encoding="utf-8") as f:
            fund = json.load(f)
    else:
        fund = []
    return b1d, b4h, fund


def build_funding_per_bar(b4h, fund):
    """Map each 4H bar index to sum of funding settlements in [open, open+4h)."""
    bar_fund = [0.0] * len(b4h)
    if not fund or not b4h:
        return bar_fund, None
    first_fund_ts = fund[0][0]
    # Use pointer merge (both sorted ascending)
    fi = 0
    nf = len(fund)
    for bi, bar in enumerate(b4h):
        t0 = bar[0]
        t1 = t0 + FOUR_H_MS
        while fi < nf and fund[fi][0] < t0:
            fi += 1
        s = 0.0
        while fi < nf and fund[fi][0] < t1:
            s += fund[fi][1]
            fi += 1
        bar_fund[bi] = s
    return bar_fund, first_fund_ts


def simulate_short_exit(b4h, atr, e, stop0):
    """Simulate short exit from entry bar e with initial stop0. Returns (exit_bar, exit_price) or None."""
    n = len(b4h)
    # On entry bar e, only stop0 is checked
    if b4h[e][2] >= stop0:
        return e, max(b4h[e][1], stop0)

    min_low = b4h[e][3]
    last_bar = e + 41
    for t in range(e + 1, min(last_bar + 1, n)):
        trail = min_low + 2.0 * atr[t - 1]
        level = min(stop0, trail)
        if b4h[t][2] >= level:
            return t, max(b4h[t][1], level)
        if b4h[t][3] < min_low:
            min_low = b4h[t][3]

    if last_bar < n:
        return last_bar, b4h[last_bar][4]
    return None


def split_of(date_str):
    if date_str <= "2023-12-31":
        return "DEV"
    return "VAL"


def percentile(sorted_vals, pct):
    """Linear-interpolated percentile (0..100)."""
    if not sorted_vals:
        return float("nan")
    k = (len(sorted_vals) - 1) * (pct / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_vals[int(k)]
    return sorted_vals[f] * (c - k) + sorted_vals[c] * (k - f)


def block_bootstrap_ci(trades, key_r, n_resamples=10000, seed=1114):
    if not trades:
        return float("nan"), float("nan")
    blocks = {}
    for tr in trades:
        b = tr["entry_day_num"] // 7
        blocks.setdefault(b, []).append(tr[key_r])
    block_list = list(blocks.values())
    m = len(block_list)
    rng = random.Random(seed)
    means = []
    for _ in range(n_resamples):
        total = 0.0
        cnt = 0
        for _ in range(m):
            blk = block_list[rng.randrange(m)]
            total += sum(blk)
            cnt += len(blk)
        means.append(total / cnt)
    means.sort()
    return percentile(means, 2.5), percentile(means, 97.5)


def run_placebo(trades, eligible_by_coin, coin_data, fee, use_funding, n_draws=2000, seed=1114):
    if not trades:
        return float("nan"), float("nan"), float("nan")
    rng = random.Random(seed)
    draw_means = []
    # Pre-index eligible bars per (coin, split, bear_flag)
    for _ in range(n_draws):
        total_r = 0.0
        for tr in trades:
            pool = eligible_by_coin[(tr["coin"], tr["split"], tr["bear"])]
            e = pool[rng.randrange(len(pool))]
            b4h, atr, bar_fund, first_fund_ts = coin_data[tr["coin"]]
            entry = b4h[e][1]
            stop0 = entry * (1.0 + tr["r"])
            res = simulate_short_exit(b4h, atr, e, stop0)
            x, exit_px = res
            gross = (entry - exit_px) / entry
            fund_ret = 0.0
            if use_funding and first_fund_ts is not None and b4h[e][0] >= first_fund_ts:
                fund_ret = sum(bar_fund[e + 1 : x + 1])
            total_r += (gross - fee + fund_ret) / tr["r"]
        draw_means.append(total_r / len(trades))
    draw_means.sort()
    actual_key = "r12_fund" if (fee == 0.0012 and use_funding) else "r12_nofund"
    actual_mean = sum(t[actual_key] for t in trades) / len(trades)
    below = sum(1 for m in draw_means if m <= actual_mean)
    pct_rank = 100.0 * below / len(draw_means)
    return percentile(draw_means, 2.5), percentile(draw_means, 97.5), pct_rank


def main():
    all_trades = []
    dropped_stop0 = 0
    dropped_data_end = 0
    dropped_lockout = 0
    no_fund_cov = []
    coin_data = {}
    eligible_by_coin = {}

    for coin in COINS:
        b1d, b4h, fund = load_coin_data(coin)
        daily_map = compute_daily_phases(b1d)
        closes = [b[4] for b in b4h]
        rsi = wilder_rsi(closes, 14)
        atr = wilder_atr(b4h, 14)
        bb_up = bollinger_upper(closes, 20, 2.0)
        bar_fund, first_fund_ts = build_funding_per_bar(b4h, fund)
        coin_data[coin] = (b4h, atr, bar_fund, first_fund_ts)

        # Build eligible bars for placebo (past warm-up e >= 100, has daily phase, exit inside data)
        for sp in ("DEV", "VAL"):
            for bf in (True, False):
                eligible_by_coin[(coin, sp, bf)] = []

        n4 = len(b4h)
        for e in range(100, n4):
            if atr[e - 1] is None:
                continue
            d_prev = utc_day_num(b4h[e][0]) - 1
            if d_prev not in daily_map:
                continue
            bear, _phase = daily_map[d_prev]
            # Exit inside data check: worst case 42 bars -> e + 41 < n4, or stop hits earlier
            # Note: PRE_REG says "with the exit inside the data". Safest is e + 41 < n4
            if e + 41 >= n4:
                continue
            sp = split_of(utc_date_str(b4h[e][0]))
            eligible_by_coin[(coin, sp, bear)].append(e)

        # Find swing highs (k = 3)
        pivots = []
        for i in range(3, n4 - 3):
            hi = b4h[i][2]
            if all(hi > b4h[i - k][2] for k in (1, 2, 3)) and all(
                hi > b4h[i + k][2] for k in (1, 2, 3)
            ):
                pivots.append(i)

        prev_kept_e = None
        prev_kept_x = None

        for idx in range(1, len(pivots)):
            p = pivots[idx - 1]
            j = pivots[idx]
            if not (6 <= j - p <= 60):
                continue
            c = j + 3
            e = c + 1
            if e < 100 or e >= n4:
                continue
            if rsi[p] is None or rsi[j] is None or bb_up[j] is None or atr[c] is None:
                continue
            if not (b4h[j][2] > b4h[p][2] and rsi[j] < rsi[p] and b4h[j][2] > bb_up[j]):
                continue

            d_prev = utc_day_num(b4h[e][0]) - 1
            if d_prev not in daily_map:
                continue
            bear, phase = daily_map[d_prev]

            entry = b4h[e][1]
            stop0 = b4h[j][2] + max(0.6 * atr[c], 0.005 * b4h[j][2])
            if entry >= stop0:
                dropped_stop0 += 1
                continue
            r = (stop0 - entry) / entry

            # Lockout check: within 60 4H bars of prev kept entry, or e <= prev kept exit
            if prev_kept_e is not None:
                if (e - prev_kept_e) < 60 or e <= prev_kept_x:
                    dropped_lockout += 1
                    continue

            res = simulate_short_exit(b4h, atr, e, stop0)
            if res is None:
                dropped_data_end += 1
                continue
            x, exit_px = res

            prev_kept_e = e
            prev_kept_x = x

            gross = (entry - exit_px) / entry
            has_fund_cov = (first_fund_ts is not None) and (b4h[e][0] >= first_fund_ts)
            fund_ret = sum(bar_fund[e + 1 : x + 1]) if has_fund_cov else 0.0

            entry_date = utc_date_str(b4h[e][0])
            sp = split_of(entry_date)
            is_recent = entry_date >= "2025-07-01"

            if bear and not has_fund_cov:
                no_fund_cov.append((coin, entry_date))

            all_trades.append(
                {
                    "coin": coin,
                    "e": e,
                    "x": x,
                    "entry_date": entry_date,
                    "entry_day_num": utc_day_num(b4h[e][0]),
                    "split": sp,
                    "recent": is_recent,
                    "bear": bear,
                    "phase": phase,
                    "r": r,
                    "gross": gross,
                    "fund": fund_ret,
                    "has_fund_cov": has_fund_cov,
                    "r12_nofund": (gross - 0.0012) / r,
                    "r12_fund": (gross - 0.0012 + fund_ret) / r,
                    "r6_nofund": (gross - 0.0006) / r,
                    "r6_fund": (gross - 0.0006 + fund_ret) / r,
                }
            )

    print(f"Total kept trades (all): {len(all_trades)}")
    print(f"Dropped: stop0={dropped_stop0}, lockout={dropped_lockout}, data_end={dropped_data_end}")
    print(f"BEAR no funding coverage: {len(no_fund_cov)} -> {no_fund_cov[:10]}")

    for label, subset in [
        ("BEAR DEV", [t for t in all_trades if t["bear"] and t["split"] == "DEV"]),
        ("BEAR VAL", [t for t in all_trades if t["bear"] and t["split"] == "VAL"]),
        ("BEAR RECENT", [t for t in all_trades if t["bear"] and t["recent"]]),
        ("BEAR VAL BTC", [t for t in all_trades if t["bear"] and t["split"] == "VAL" and t["coin"] == "BTC"]),
        ("BEAR ALL BTC", [t for t in all_trades if t["bear"] and t["coin"] == "BTC"]),
        ("CTRL(!BEAR) VAL", [t for t in all_trades if (not t["bear"]) and t["split"] == "VAL"]),
    ]:
        n = len(subset)
        if n == 0:
            print(f"{label}: n=0")
            continue
        m12_nf = sum(t["r12_nofund"] for t in subset) / n
        m12_f = sum(t["r12_fund"] for t in subset) / n
        m6_nf = sum(t["r6_nofund"] for t in subset) / n
        m6_f = sum(t["r6_fund"] for t in subset) / n
        win12_nf = 100.0 * sum(1 for t in subset if t["r12_nofund"] > 0) / n
        win12_f = 100.0 * sum(1 for t in subset if t["r12_fund"] > 0) / n
        print(
            f"{label}: n={n}, win12_nf={win12_nf:.1f}%, win12_f={win12_f:.1f}%, "
            f"mean12_nf={m12_nf:+.4f}, mean12_f={m12_f:+.4f}, "
            f"mean6_nf={m6_nf:+.4f}, mean6_f={m6_f:+.4f}"
        )

    # Primary verdict stats: BEAR DEV and BEAR VAL
    bear_dev = [t for t in all_trades if t["bear"] and t["split"] == "DEV"]
    bear_val = [t for t in all_trades if t["bear"] and t["split"] == "VAL"]

    for name, trs in [("BEAR DEV", bear_dev), ("BEAR VAL", bear_val)]:
        ci_nf = block_bootstrap_ci(trs, "r12_nofund")
        ci_f = block_bootstrap_ci(trs, "r12_fund")
        p_nf = run_placebo(trs, eligible_by_coin, coin_data, 0.0012, False)
        p_f = run_placebo(trs, eligible_by_coin, coin_data, 0.0012, True)
        print(f"{name} CI_nf=({ci_nf[0]:+.4f}, {ci_nf[1]:+.4f}) placebo_nf={p_nf}")
        print(f"{name} CI_f =({ci_f[0]:+.4f}, {ci_f[1]:+.4f}) placebo_f ={p_f}")

    # Verdict
    m_dev_nf = sum(t["r12_nofund"] for t in bear_dev) / len(bear_dev)
    m_dev_f = sum(t["r12_fund"] for t in bear_dev) / len(bear_dev)
    m_val_nf = sum(t["r12_nofund"] for t in bear_val) / len(bear_val)
    m_val_f = sum(t["r12_fund"] for t in bear_val) / len(bear_val)
    ci_val_nf = block_bootstrap_ci(bear_val, "r12_nofund")
    ci_val_f = block_bootstrap_ci(bear_val, "r12_fund")
    p_val_nf = run_placebo(bear_val, eligible_by_coin, coin_data, 0.0012, False)
    p_val_f = run_placebo(bear_val, eligible_by_coin, coin_data, 0.0012, True)

    if len(bear_val) < 30:
        verdict = "UNDERPOWERED"
    elif (
        m_val_nf > 0
        and m_val_f > 0
        and ci_val_nf[0] > 0
        and ci_val_f[0] > 0
        and m_val_nf > p_val_nf[1]
        and m_val_f > p_val_f[1]
        and m_dev_nf > 0
        and m_dev_f > 0
    ):
        verdict = "PASS"
    else:
        verdict = "KILL"
    print(f"VERDICT: {verdict}")


if __name__ == "__main__":
    main()
