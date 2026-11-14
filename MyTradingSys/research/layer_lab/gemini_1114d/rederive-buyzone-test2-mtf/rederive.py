"""Independent blind re-derivation of buyzone_test2_mtf_2026-11-14 from PRE_REG.md and FORMULAS.md."""

import os
import datetime
import numpy as np

CACHE_DIR = os.path.expanduser("~/mts_cache/buyzone_test2")
COINS = [
    "BTC", "ETH", "BNB", "XRP", "ADA", "LTC", "TRX", "LINK", "XLM", "DOGE",
    "ETC", "DASH", "ZEC", "NEO", "IOTA", "VET", "ATOM", "EOS", "BCH", "QTUM",
]

MS_4H = 4 * 3600 * 1000
MS_1D = 24 * 3600 * 1000
MS_3D = 3 * MS_1D
MS_1W = 7 * MS_1D
DEV_END_MS = int(datetime.datetime(2024, 1, 1, tzinfo=datetime.timezone.utc).timestamp() * 1000)
VAL_START_MS = DEV_END_MS
RECENT_START_MS = int(datetime.datetime(2025, 7, 1, tzinfo=datetime.timezone.utc).timestamp() * 1000)


def load_klines(coin: str, tf: str) -> np.ndarray:
    return np.load(os.path.join(CACHE_DIR, f"{coin}USDT_{tf}.npy"))


def sma(arr: np.ndarray, period: int) -> np.ndarray:
    out = np.full(len(arr), np.nan, dtype=np.float64)
    if len(arr) < period:
        return out
    cs = np.cumsum(arr, dtype=np.float64)
    out[period - 1:] = (cs[period - 1:] - np.concatenate(([0.0], cs[:-period]))) / period
    return out


def ema_nan_aware(arr: np.ndarray, period: int) -> np.ndarray:
    """EMA per FORMULAS.md section 4: SMA seed of first `period` consecutive non-NaN values."""
    n = len(arr)
    out = np.full(n, np.nan, dtype=np.float64)
    alpha = 2.0 / (period + 1.0)
    start = 0
    while start < n and np.isnan(arr[start]):
        start += 1
    if start + period > n:
        return out
    val = float(np.mean(arr[start:start + period]))
    out[start + period - 1] = val
    for i in range(start + period, n):
        val = (arr[i] - val) * alpha + val
        out[i] = val
    return out


def wilder_rsi(closes: np.ndarray, period: int = 14) -> np.ndarray:
    """Textbook Wilder RSI per FORMULAS.md section 1."""
    n = len(closes)
    out = np.full(n, np.nan, dtype=np.float64)
    if n <= period:
        return out
    deltas = np.diff(closes)
    gains = np.maximum(deltas, 0.0)
    losses = np.maximum(-deltas, 0.0)
    avg_gain = float(np.mean(gains[:period]))
    avg_loss = float(np.mean(losses[:period]))

    def _rsi(ag: float, al: float) -> float:
        if al == 0.0:
            return 100.0 if ag > 0.0 else 50.0
        return 100.0 - 100.0 / (1.0 + ag / al)

    out[period] = _rsi(avg_gain, avg_loss)
    for i in range(period, len(deltas)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        out[i + 1] = _rsi(avg_gain, avg_loss)
    return out


def wavetrend(highs: np.ndarray, lows: np.ndarray, closes: np.ndarray, n1: int = 10, n2: int = 21) -> np.ndarray:
    hlc3 = (highs + lows + closes) / 3.0
    esa = ema_nan_aware(hlc3, n1)
    d = ema_nan_aware(np.abs(hlc3 - esa), n1)
    ci = np.full(len(closes), np.nan, dtype=np.float64)
    valid = (~np.isnan(esa)) & (~np.isnan(d))
    ci[valid] = np.where(d[valid] > 0.0, (hlc3[valid] - esa[valid]) / (0.015 * d[valid]), 0.0)
    return ema_nan_aware(ci, n2)


def wilder_rma(arr: np.ndarray, period: int) -> np.ndarray:
    n = len(arr)
    out = np.full(n, np.nan, dtype=np.float64)
    if n < period:
        return out
    val = float(np.mean(arr[:period]))
    out[period - 1] = val
    for i in range(period, n):
        val = (val * (period - 1) + arr[i]) / period
        out[i] = val
    return out


def wilder_atr(highs: np.ndarray, lows: np.ndarray, closes: np.ndarray, period: int = 14) -> np.ndarray:
    n = len(closes)
    out = np.full(n, np.nan, dtype=np.float64)
    if n <= period:
        return out
    tr = np.zeros(n - 1, dtype=np.float64)
    for i in range(1, n):
        tr[i - 1] = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i - 1]),
            abs(lows[i] - closes[i - 1]),
        )
    rma = wilder_rma(tr, period)
    out[1:] = rma
    return out


def wilder_di(highs: np.ndarray, lows: np.ndarray, closes: np.ndarray, period: int = 14):
    n = len(closes)
    di_plus = np.full(n, np.nan, dtype=np.float64)
    di_minus = np.full(n, np.nan, dtype=np.float64)
    if n <= period:
        return di_plus, di_minus
    tr = np.zeros(n - 1, dtype=np.float64)
    pdm = np.zeros(n - 1, dtype=np.float64)
    mdm = np.zeros(n - 1, dtype=np.float64)
    for i in range(1, n):
        tr[i - 1] = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i - 1]),
            abs(lows[i] - closes[i - 1]),
        )
        up = highs[i] - highs[i - 1]
        dn = lows[i - 1] - lows[i]
        if up > dn and up > 0.0:
            pdm[i - 1] = up
        if dn > up and dn > 0.0:
            mdm[i - 1] = dn
    tr_rma = wilder_rma(tr, period)
    pdm_rma = wilder_rma(pdm, period)
    mdm_rma = wilder_rma(mdm, period)
    for i in range(period - 1, n - 1):
        if tr_rma[i] > 0.0:
            di_plus[i + 1] = 100.0 * pdm_rma[i] / tr_rma[i]
            di_minus[i + 1] = 100.0 * mdm_rma[i] / tr_rma[i]
        else:
            di_plus[i + 1] = 0.0
            di_minus[i + 1] = 0.0
    return di_plus, di_minus


def compute_daily_phases(d_arr: np.ndarray) -> dict[int, str]:
    n = len(d_arr)
    ts = d_arr[:, 0].astype(np.int64)
    highs = d_arr[:, 2]
    closes = d_arr[:, 4]
    sma200 = sma(closes, 200)
    sma350 = sma(closes, 350)
    di_p, di_m = wilder_di(highs, d_arr[:, 3], closes, 14)

    phase_map = {}
    for i in range(350, n):
        c = closes[i]
        s200 = sma200[i]
        s200_prev20 = sma200[i - 20]
        s350 = sma350[i]
        h540 = float(np.max(highs[max(0, i - 539):i + 1]))

        if c > s200 and s200 > s200_prev20 and di_p[i] > di_m[i]:
            p = "UP"
        elif c <= 0.6 * h540 and all(closes[j] > sma200[j] for j in range(i - 19, i + 1)):
            p = "BASE"
        elif c <= 0.6 * h540 and c < s350:
            p = "BEAR"
        elif c < s200 and di_m[i] > di_p[i]:
            p = "DOWN"
        else:
            p = "RANGE"
        phase_map[int(ts[i])] = p
    return phase_map


def find_pivots(highs: np.ndarray, lows: np.ndarray, hw: int):
    """Causal pivots: pivot at p is confirmed at p + hw."""
    n = len(highs)
    ph = []  # (pivot_idx, confirm_idx, price)
    pl = []
    for p in range(hw, n - hw):
        h_win_l = highs[p - hw:p]
        h_win_r = highs[p + 1:p + hw + 1]
        if highs[p] > np.max(h_win_l) and highs[p] > np.max(h_win_r):
            ph.append((p, p + hw, float(highs[p])))
        l_win_l = lows[p - hw:p]
        l_win_r = lows[p + 1:p + hw + 1]
        if lows[p] < np.min(l_win_l) and lows[p] < np.min(l_win_r):
            pl.append((p, p + hw, float(lows[p])))
    return ph, pl


def find_htf_divergences(arr: np.ndarray, tf_ms: int, osc: np.ndarray):
    """Return sorted list of confirm_close_ms for bullish and bearish divergences."""
    ph, pl = find_pivots(arr[:, 2], arr[:, 3], 2)
    ts = arr[:, 0].astype(np.int64)
    bull_times = []
    bear_times = []

    for idx in range(1, len(pl)):
        p1, _, v1 = pl[idx - 1]
        p2, c2, v2 = pl[idx]
        if 3 <= (p2 - p1) <= 30:
            if not (np.isnan(osc[p1]) or np.isnan(osc[p2])):
                if v2 < v1 and osc[p2] > osc[p1]:
                    bull_times.append(int(ts[c2]) + tf_ms)

    for idx in range(1, len(ph)):
        p1, _, v1 = ph[idx - 1]
        p2, c2, v2 = ph[idx]
        if 3 <= (p2 - p1) <= 30:
            if not (np.isnan(osc[p1]) or np.isnan(osc[p2])):
                if v2 > v1 and osc[p2] < osc[p1]:
                    bear_times.append(int(ts[c2]) + tf_ms)

    return bull_times, bear_times


def has_recent_div(div_times: list[int], t_close: int, window_ms: int = 28 * MS_1D) -> bool:
    for tc in div_times:
        if 0 <= (t_close - tc) <= window_ms:
            return True
        if tc > t_close:
            break
    return False


def prepare_coin_data(coin: str):
    d_arr = load_klines(coin, "1d")
    phase_map = compute_daily_phases(d_arr)

    w_arr = load_klines(coin, "1w")
    w_rsi = wilder_rsi(w_arr[:, 4], 14)
    w_wt = wavetrend(w_arr[:, 2], w_arr[:, 3], w_arr[:, 4], 10, 21)
    w_bull_rsi, w_bear_rsi = find_htf_divergences(w_arr, MS_1W, w_rsi)
    w_bull_wt, w_bear_wt = find_htf_divergences(w_arr, MS_1W, w_wt)

    d3_arr = load_klines(coin, "3d")
    d3_rsi = wilder_rsi(d3_arr[:, 4], 14)
    d3_wt = wavetrend(d3_arr[:, 2], d3_arr[:, 3], d3_arr[:, 4], 10, 21)
    d3_bull_rsi, d3_bear_rsi = find_htf_divergences(d3_arr, MS_3D, d3_rsi)
    d3_bull_wt, d3_bear_wt = find_htf_divergences(d3_arr, MS_3D, d3_wt)

    h4 = load_klines(coin, "4h")
    ts4 = h4[:, 0].astype(np.int64)
    o4, h4_hi, l4_lo, c4 = h4[:, 1], h4[:, 2], h4[:, 3], h4[:, 4]
    atr4 = wilder_atr(h4_hi, l4_lo, c4, 14)
    ph4, pl4 = find_pivots(h4_hi, l4_lo, 3)

    # Precompute most recent confirmed pivot at each 4H bar i
    n4 = len(h4)
    last_ph = np.full(n4, -1, dtype=np.int64)
    last_pl = np.full(n4, -1, dtype=np.int64)
    j = 0
    cur = -1
    for i in range(n4):
        while j < len(ph4) and ph4[j][1] <= i:
            cur = ph4[j][0]
            j += 1
        last_ph[i] = cur
    j = 0
    cur = -1
    for i in range(n4):
        while j < len(pl4) and pl4[j][1] <= i:
            cur = pl4[j][0]
            j += 1
        last_pl[i] = cur

    # Precompute daily phase for each 4H bar (day BEFORE open day)
    phases4 = ["n/a"] * n4
    for i in range(n4):
        day_ms = (int(ts4[i]) // MS_1D) * MS_1D
        phases4[i] = phase_map.get(day_ms - MS_1D, "n/a")

    bull_rsi = sorted(w_bull_rsi + d3_bull_rsi)
    bear_rsi = sorted(w_bear_rsi + d3_bear_rsi)
    bull_wt = sorted(w_bull_wt + d3_bull_wt)
    bear_wt = sorted(w_bear_wt + d3_bear_wt)

    return {
        "coin": coin,
        "ts4": ts4, "o4": o4, "h4": h4_hi, "l4": l4_lo, "c4": c4,
        "atr4": atr4, "last_ph": last_ph, "last_pl": last_pl,
        "phases4": phases4,
        "bull_rsi": bull_rsi, "bear_rsi": bear_rsi,
        "bull_wt": bull_wt, "bear_wt": bear_wt,
    }


def simulate_variant(coin_data: dict, variant: str) -> list[dict]:
    trades = []
    for coin, cd in coin_data.items():
        ts4, o4, h4, l4, c4 = cd["ts4"], cd["o4"], cd["h4"], cd["l4"], cd["c4"]
        atr4, last_ph, last_pl, phases4 = cd["atr4"], cd["last_ph"], cd["last_pl"], cd["phases4"]
        n4 = len(ts4)

        broken_ph = -1
        broken_pl = -1
        last_entry_ms = -10**18

        for i in range(n4 - 2):
            ph_idx = int(last_ph[i])
            pl_idx = int(last_pl[i])
            if ph_idx < 0 or pl_idx < 0 or np.isnan(atr4[i]):
                continue

            bull_break = False
            bear_break = False
            if c4[i] > h4[ph_idx] and ph_idx != broken_ph:
                bull_break = True
                broken_ph = ph_idx
            if c4[i] < l4[pl_idx] and pl_idx != broken_pl:
                bear_break = True
                broken_pl = pl_idx

            phase = phases4[i]
            if phase in ("UP", "BASE"):
                side = 1
                if not bull_break:
                    continue
            elif phase in ("DOWN", "BEAR"):
                side = -1
                if not bear_break:
                    continue
            else:
                continue

            entry_ms = int(ts4[i + 1])
            if entry_ms - last_entry_ms < 10 * MS_1D:
                continue

            # Context check at signal bar close
            t_close = int(ts4[i]) + MS_4H
            if variant == "PRIMARY":
                divs = cd["bull_rsi"] if side == 1 else cd["bear_rsi"]
                if not has_recent_div(divs, t_close):
                    continue
            elif variant == "SEC_WT":
                divs = cd["bull_wt"] if side == 1 else cd["bear_wt"]
                if not has_recent_div(divs, t_close):
                    continue
            elif variant == "CONTROL":
                pass

            entry_price = float(o4[i + 1])
            pad = max(0.6 * float(atr4[i]), 0.005 * entry_price)
            if side == 1:
                stop_price = float(l4[pl_idx]) - pad
                risk = entry_price - stop_price
            else:
                stop_price = float(h4[ph_idx]) + pad
                risk = stop_price - entry_price

            if risk <= 0.0 or risk > 0.10 * entry_price:
                continue

            # Simulate exit
            i_entry = i + 1
            exit_price = None
            exit_bar = None
            planned_hold = 60  # max 60 bars if no opposite break
            max_k = min(n4 - 1, i_entry + 60)

            for k in range(i_entry, max_k):
                # 1. Stop check
                if side == 1:
                    if o4[k] <= stop_price:
                        exit_price = float(o4[k])
                        exit_bar = k
                        break
                    elif l4[k] <= stop_price:
                        exit_price = stop_price
                        exit_bar = k
                        break
                else:
                    if o4[k] >= stop_price:
                        exit_price = float(o4[k])
                        exit_bar = k
                        break
                    elif h4[k] >= stop_price:
                        exit_price = stop_price
                        exit_bar = k
                        break

                # 2. Opposite raw 4H break (close, exit at next open)
                if side == 1:
                    pl_k = int(last_pl[k])
                    if pl_k >= 0 and c4[k] < l4[pl_k]:
                        exit_price = float(o4[k + 1])
                        exit_bar = k + 1
                        planned_hold = (k + 1) - i_entry
                        break
                else:
                    ph_k = int(last_ph[k])
                    if ph_k >= 0 and c4[k] > h4[ph_k]:
                        exit_price = float(o4[k + 1])
                        exit_bar = k + 1
                        planned_hold = (k + 1) - i_entry
                        break

            if exit_price is None:
                if i_entry + 60 < n4:
                    exit_price = float(o4[i_entry + 60])
                    exit_bar = i_entry + 60
                    planned_hold = 60
                else:
                    continue  # incomplete trade at end of dataset

            # Compute planned_hold if stopped out early (for placebo):
            # "bars until its exit signal or 10 days, stop ignored for the hold length"
            if exit_bar <= i_entry + 60 and planned_hold == 60:
                for k in range(i_entry, min(n4 - 1, i_entry + 60)):
                    if side == 1:
                        pl_k = int(last_pl[k])
                        if pl_k >= 0 and c4[k] < l4[pl_k]:
                            planned_hold = (k + 1) - i_entry
                            break
                    else:
                        ph_k = int(last_ph[k])
                        if ph_k >= 0 and c4[k] > h4[ph_k]:
                            planned_hold = (k + 1) - i_entry
                            break

            raw_r = side * (exit_price - entry_price) / risk
            r_12 = raw_r - 0.0012 * entry_price / risk
            r_06 = raw_r - 0.0006 * entry_price / risk

            if entry_ms < DEV_END_MS:
                period = "DEV"
            elif entry_ms < RECENT_START_MS:
                period = "MID"
            else:
                period = "RECENT"

            last_entry_ms = entry_ms
            trades.append({
                "coin": coin,
                "side": side,
                "phase": phase,
                "entry_ms": entry_ms,
                "period": period,
                "is_val": entry_ms >= VAL_START_MS,
                "is_recent": entry_ms >= RECENT_START_MS,
                "planned_hold": max(1, planned_hold),
                "raw_r": raw_r,
                "r_12": r_12,
                "r_06": r_06,
            })
    return trades


def block_bootstrap_ci(trades: list[dict], key: str = "r_12", n_boot: int = 2000, seed: int = 1114):
    if not trades:
        return (np.nan, np.nan)
    rng = np.random.default_rng(seed)
    blocks = {}
    block_ms = 10 * MS_1D
    for t in trades:
        b = t["entry_ms"] // block_ms
        blocks.setdefault(b, []).append(t[key])
    block_sums = np.array([sum(v) for v in blocks.values()], dtype=np.float64)
    block_cnts = np.array([len(v) for v in blocks.values()], dtype=np.float64)
    nb = len(block_sums)
    means = np.empty(n_boot, dtype=np.float64)
    for b in range(n_boot):
        idx = rng.integers(0, nb, size=nb)
        means[b] = np.sum(block_sums[idx]) / np.sum(block_cnts[idx])
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def build_placebo_pool(coin_data: dict):
    """Precompute valid placebo entry bars grouped by (side, phase, period)."""
    pool = {}
    for coin, cd in coin_data.items():
        ts4, o4, h4, l4 = cd["ts4"], cd["o4"], cd["h4"], cd["l4"]
        atr4, last_ph, last_pl, phases4 = cd["atr4"], cd["last_ph"], cd["last_pl"], cd["phases4"]
        n4 = len(ts4)
        for i in range(n4 - 2):
            ph_idx = int(last_ph[i])
            pl_idx = int(last_pl[i])
            if ph_idx < 0 or pl_idx < 0 or np.isnan(atr4[i]):
                continue
            phase = phases4[i]
            if phase in ("UP", "BASE"):
                side = 1
            elif phase in ("DOWN", "BEAR"):
                side = -1
            else:
                continue
            entry_ms = int(ts4[i + 1])
            entry_price = float(o4[i + 1])
            pad = max(0.6 * float(atr4[i]), 0.005 * entry_price)
            if side == 1:
                stop_price = float(l4[pl_idx]) - pad
                risk = entry_price - stop_price
            else:
                stop_price = float(h4[ph_idx]) + pad
                risk = stop_price - entry_price
            if risk <= 0.0 or risk > 0.10 * entry_price:
                continue
            if entry_ms < DEV_END_MS:
                period = "DEV"
            elif entry_ms < RECENT_START_MS:
                period = "MID"
            else:
                period = "RECENT"
            pool.setdefault((side, phase, period), []).append((coin, i + 1, entry_price, stop_price, risk))
    return pool


def run_placebo(trades: list[dict], coin_data: dict, pool: dict, n_draws: int = 1000, seed: int = 1114):
    if not trades:
        return np.nan, np.nan, np.nan
    rng = np.random.default_rng(seed)
    # Precompute R for each trade's (side, phase, period, planned_hold) or sample directly
    real_mean = float(np.mean([t["r_12"] for t in trades]))

    # Group trades by (side, phase, period, planned_hold) to vectorize/cache
    draw_sums = np.zeros(n_draws, dtype=np.float64)
    for t in trades:
        key = (t["side"], t["phase"], t["period"], t["planned_hold"])
        candidates = pool.get((t["side"], t["phase"], t["period"]), [])
        if not candidates:
            continue
        hold = t["planned_hold"]
        side = t["side"]
        idxs = rng.integers(0, len(candidates), size=n_draws)
        for d_i, c_idx in enumerate(idxs):
            coin, i_entry, ep, sp, risk = candidates[c_idx]
            cd = coin_data[coin]
            o4, h4, l4 = cd["o4"], cd["h4"], cd["l4"]
            n4 = len(o4)
            end_k = min(n4 - 1, i_entry + hold)
            ex = None
            for k in range(i_entry, end_k):
                if side == 1:
                    if o4[k] <= sp:
                        ex = float(o4[k])
                        break
                    if l4[k] <= sp:
                        ex = sp
                        break
                else:
                    if o4[k] >= sp:
                        ex = float(o4[k])
                        break
                    if h4[k] >= sp:
                        ex = sp
                        break
            if ex is None:
                ex = float(o4[end_k])
            raw_r = side * (ex - ep) / risk
            draw_sums[d_i] += raw_r - 0.0012 * ep / risk

    draw_means = draw_sums / len(trades)
    pctl = float(np.mean(draw_means <= real_mean) * 100.0)
    lo = float(np.percentile(draw_means, 2.5))
    hi = float(np.percentile(draw_means, 97.5))
    return pctl, lo, hi


def summarize(label: str, trades: list[dict], coin_data: dict, pool: dict, do_placebo: bool = True):
    if not trades:
        print(f"{label}: n=0")
        return
    r12 = np.array([t["r_12"] for t in trades])
    r06 = np.array([t["r_06"] for t in trades])
    win = float(np.mean(r12 > 0) * 100.0)
    ci_lo, ci_hi = block_bootstrap_ci(trades, "r_12")
    p_str = ""
    if do_placebo:
        pctl, plo, phi = run_placebo(trades, coin_data, pool)
        p_str = f" | placebo pctl={pctl:.1f}% [{plo:+.4f}, {phi:+.4f}]"
    print(f"{label}: n={len(trades)}, win={win:.1f}%, mean12={np.mean(r12):+.4f} CI=[{ci_lo:+.4f}, {ci_hi:+.4f}], mean06={np.mean(r06):+.4f}{p_str}")


def main():
    print("Loading 20 coins...")
    coin_data = {c: prepare_coin_data(c) for c in COINS}
    print("Building placebo pool...")
    pool = build_placebo_pool(coin_data)

    for var in ["PRIMARY", "SEC_WT", "CONTROL"]:
        print(f"\n=== {var} ===")
        tr = simulate_variant(coin_data, var)
        dev = [t for t in tr if t["period"] == "DEV"]
        val = [t for t in tr if t["is_val"]]
        rec = [t for t in tr if t["is_recent"]]

        summarize(f"{var} DEV both", dev, coin_data, pool)
        summarize(f"{var} VAL both", val, coin_data, pool)
        summarize(f"{var} RECENT both", rec, coin_data, pool)

        summarize(f"{var} DEV long", [t for t in dev if t["side"] == 1], coin_data, pool, do_placebo=False)
        summarize(f"{var} VAL long", [t for t in val if t["side"] == 1], coin_data, pool)
        summarize(f"{var} DEV short", [t for t in dev if t["side"] == -1], coin_data, pool, do_placebo=False)
        summarize(f"{var} VAL short", [t for t in val if t["side"] == -1], coin_data, pool)

        if var == "PRIMARY" and val:
            by_coin = {}
            for t in val:
                by_coin[t["coin"]] = by_coin.get(t["coin"], 0.0) + t["r_12"]
            top_coin = max(by_coin, key=by_coin.get)
            val_no_top = [t for t in val if t["coin"] != top_coin]
            ci_lo, ci_hi = block_bootstrap_ci(val_no_top, "r_12")
            print(f"PRIMARY VAL top coin={top_coin} (sum={by_coin[top_coin]:+.4f}) -> without top: n={len(val_no_top)}, mean12={np.mean([t['r_12'] for t in val_no_top]):+.4f}, CI=[{ci_lo:+.4f}, {ci_hi:+.4f}]")


if __name__ == "__main__":
    main()
