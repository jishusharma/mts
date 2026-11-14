"""Independent re-derivation of combo-edge-miner-1114 from PRE_REG.md and FORMULAS.md.

Uses local MTS_data_cache (binance_spot_1d, binance_spot_4h) for available OHLCV
features (19/20 coins; ZEC, col-9 taker-buy volume, Binance 8h funding, Binance
daily OI, and cycle file d200w are absent on this laptop because F:\\MTS\\data_cache
is not mounted).
"""
from __future__ import annotations

import json
import math
import statistics
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

CACHE_DIR = Path(r"C:\Users\e-ngineers\MTS_data_cache")
COINS = (
    "BTC ETH BNB XRP ADA DOGE SOL LTC TRX LINK "
    "DOT AVAX ATOM ETC XLM BCH UNI VET ZEC NEO"
).split()
HALVINGS = ["2016-07-09", "2020-05-11", "2024-04-20"]
HALVING_DAYS = [
    int(datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() // 86400)
    for d in HALVINGS
]
DEV_START_DAY = "2020-01-01"
DEV_END_DAY = "2023-12-31"
VAL_START_DAY = "2024-01-01"
LAST_CLOSED_MS = int(
    datetime(2026, 11, 13, 20, 0, tzinfo=timezone.utc).timestamp() * 1000
)
COST_12BP = 2 * 0.0005 + 0.0002  # 0.0012 (fees.BINANCE_TAKER*2 + fees.SLIPPAGE_RT_S13)
COST_6BP = 0.0006
M_TRIALS = 210684


def load_klines(coin: str, tf: str):
    p = CACHE_DIR / f"binance_spot_{tf}" / f"{coin}USDT.json"
    if not p.exists():
        return None
    rows = json.loads(p.read_text(encoding="utf-8"))
    bar_ms = 86400_000 if tf == "1d" else 4 * 3600_000
    return [r for r in rows if r[0] + bar_ms <= LAST_CLOSED_MS]


def day_str(ts_ms: int) -> str:
    return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d")


def epoch_day(ts_ms: int) -> int:
    return ts_ms // 86400_000


def compute_phase_labels(btc_1d):
    n = len(btc_1d)
    closes = [r[4] for r in btc_1d]
    sma200 = [None] * n
    for i in range(199, n):
        sma200[i] = sum(closes[i - 199 : i + 1]) / 200.0

    labels_by_day = {}
    for i in range(219, n - 1):
        c = closes[i]
        s_now = sma200[i]
        s_prev = sma200[i - 20]
        if s_now is None or s_prev is None:
            continue
        slope = s_now - s_prev
        if c > s_now and slope > 0:
            struct = "UP"
        elif c < s_now and slope < 0:
            struct = "DOWN"
        else:
            struct = "MIX"

        ed = epoch_day(btc_1d[i][0])
        last_h = max(h for h in HALVING_DAYS if h <= ed)
        cyc = "E" if (ed - last_h) < 540 else "L"
        next_day = datetime.fromtimestamp(
            (ed + 1) * 86400, tz=timezone.utc
        ).strftime("%Y-%m-%d")
        labels_by_day[next_day] = f"{struct}_{cyc}"
    return labels_by_day


def atr14_sma(bars):
    n = len(bars)
    tr = [None] * n
    for i in range(1, n):
        h, l, pc = bars[i][2], bars[i][3], bars[i - 1][4]
        tr[i] = max(h - l, abs(h - pc), abs(l - pc))
    atr = [None] * n
    for i in range(14, n):
        atr[i] = sum(tr[i - 13 : i + 1]) / 14.0
    return atr


def rsi14_wilder(closes):
    n = len(closes)
    out = [None] * n
    if n <= 14:
        return out
    deltas = [closes[i] - closes[i - 1] for i in range(1, n)]
    ag = sum(max(d, 0.0) for d in deltas[:14]) / 14.0
    al = sum(max(-d, 0.0) for d in deltas[:14]) / 14.0
    for i in range(14, n):
        if i > 14:
            d = deltas[i - 1]
            ag = (ag * 13.0 + max(d, 0.0)) / 14.0
            al = (al * 13.0 + max(-d, 0.0)) / 14.0
        if al == 0.0:
            out[i] = 100.0 if ag > 0.0 else 50.0
        else:
            out[i] = 100.0 - 100.0 / (1.0 + ag / al)
    return out


def adx14_wilder(bars):
    n = len(bars)
    adx = [None] * n
    dip = [None] * n
    dim = [None] * n
    if n < 28:
        return adx, dip, dim
    tr = [0.0] * n
    pdm = [0.0] * n
    ndm = [0.0] * n
    for i in range(1, n):
        h, l, pc = bars[i][2], bars[i][3], bars[i - 1][4]
        tr[i] = max(h - l, abs(h - pc), abs(l - pc))
        up = h - bars[i - 1][2]
        dn = bars[i - 1][3] - l
        pdm[i] = up if (up > dn and up > 0.0) else 0.0
        ndm[i] = dn if (dn > up and dn > 0.0) else 0.0
    str_s = sum(tr[1:15])
    sp_s = sum(pdm[1:15])
    sn_s = sum(ndm[1:15])
    dx = [None] * n
    for i in range(14, n):
        if i > 14:
            str_s = str_s - str_s / 14.0 + tr[i]
            sp_s = sp_s - sp_s / 14.0 + pdm[i]
            sn_s = sn_s - sn_s / 14.0 + ndm[i]
        p = 100.0 * sp_s / str_s if str_s > 0 else 0.0
        m = 100.0 * sn_s / str_s if str_s > 0 else 0.0
        dip[i] = p
        dim[i] = m
        dx[i] = 100.0 * abs(p - m) / (p + m) if (p + m) > 0 else 0.0
    adx[27] = sum(dx[14:28]) / 14.0
    for i in range(28, n):
        adx[i] = (adx[i - 1] * 13.0 + dx[i]) / 14.0
    return adx, dip, dim


def compute_features_long(bars, tf: str):
    nb = 6 if tf == "4h" else 1
    n = len(bars)
    closes = [b[4] for b in bars]
    highs = [b[2] for b in bars]
    vols = [b[5] for b in bars]

    rsi = rsi14_wilder(closes)
    adx, dip, dim = adx14_wilder(bars)

    w5 = 5 * nb
    w50 = 50 * nb
    w10 = 10 * nb
    w30 = 30 * nb

    sma50 = [None] * n
    if n >= w50:
        cs = np.cumsum([0.0] + closes)
        for i in range(w50 - 1, n):
            sma50[i] = (cs[i + 1] - cs[i + 1 - w50]) / w50

    feats = {k: [False] * n for k in ("BRK5", "RSI_MOM", "ADX_DI", "TREND_MA", "VOLX")}
    for i in range(n):
        if i >= w5:
            feats["BRK5"][i] = closes[i] > max(highs[i - w5 : i])
        if rsi[i] is not None:
            feats["RSI_MOM"][i] = rsi[i] >= 60.0
        if adx[i] is not None:
            feats["ADX_DI"][i] = adx[i] >= 20.0 and dip[i] > dim[i]
        if i >= w10 and sma50[i] is not None and sma50[i - w10] is not None:
            feats["TREND_MA"][i] = closes[i] > sma50[i] and sma50[i] > sma50[i - w10]
        if i >= w30:
            med_v = statistics.median(vols[i - w30 : i])
            feats["VOLX"][i] = vols[i] >= 2.0 * med_v
    return feats


def sim_trades(bars, atr, signals_idx, direction, exit_mode, tf, cost_rt):
    nb = 6 if tf == "4h" else 1
    n = len(bars)
    side = 1 if direction == "LONG" else -1
    max_hold = 30 * nb if exit_mode == "T3R" else 60 * nb
    trades = []
    next_allowed = 0
    w10 = 10 * nb
    highs = [b[2] for b in bars]
    lows = [b[3] for b in bars]

    for sig_i in signals_idx:
        if sig_i < next_allowed:
            continue
        ent_i = sig_i + 1
        if ent_i >= n or atr[sig_i] is None:
            continue
        entry = bars[ent_i][1]
        stop_dist = max(2.5 * atr[sig_i], 0.02 * entry)
        stop_px = entry - side * stop_dist
        target_px = entry + side * 3.0 * stop_dist
        trail_px = stop_px
        best_close = entry
        exit_i = None
        exit_px = None
        ride_exit_next_open = False

        last_j = min(n - 1, ent_i + max_hold - 1)
        for j in range(ent_i, last_j + 1):
            o, h, l, c = bars[j][1], bars[j][2], bars[j][3], bars[j][4]
            if ride_exit_next_open:
                exit_i = j
                exit_px = o
                break
            cur_stop = trail_px if exit_mode == "TRAIL" else stop_px
            if side == 1 and l <= cur_stop:
                exit_i = j
                exit_px = min(o, cur_stop)
                break
            if side == -1 and h >= cur_stop:
                exit_i = j
                exit_px = max(o, cur_stop)
                break

            if exit_mode == "T3R":
                if (side == 1 and h >= target_px) or (side == -1 and l <= target_px):
                    exit_i = j
                    exit_px = target_px
                    break
            elif exit_mode == "TRAIL":
                if side == 1:
                    if c > best_close:
                        best_close = c
                    if best_close - entry >= stop_dist and atr[j] is not None:
                        trail_px = max(trail_px, best_close - 3.0 * atr[j])
                else:
                    if c < best_close:
                        best_close = c
                    if entry - best_close >= stop_dist and atr[j] is not None:
                        trail_px = min(trail_px, best_close + 3.0 * atr[j])
            elif exit_mode == "RIDE":
                if j >= w10:
                    if side == 1 and c < min(lows[j - w10 : j]):
                        ride_exit_next_open = True
                    elif side == -1 and c > max(highs[j - w10 : j]):
                        ride_exit_next_open = True

            if j == ent_i + max_hold - 1:
                exit_i = j
                exit_px = c
                break

        if exit_i is None:
            continue

        gross = side * (exit_px - entry) / entry
        net_r = (gross - cost_rt) / (stop_dist / entry)
        trades.append(
            {
                "entry_day": day_str(bars[ent_i][0]),
                "net_r": net_r,
                "stop_pct": stop_dist / entry,
            }
        )
        next_allowed = exit_i
    return trades


def day_cluster_stats(trades):
    n = len(trades)
    if n == 0:
        return 0, float("nan"), float("nan"), float("nan")
    vals = [t["net_r"] for t in trades]
    mean_r = sum(vals) / n
    by_day = {}
    for t in trades:
        by_day.setdefault(t["entry_day"], []).append(t["net_r"])
    g = len(by_day)
    if g < 2:
        return n, mean_r, float("nan"), float("nan")
    s_sq = sum((sum(r - mean_r for r in rs)) ** 2 for rs in by_day.values())
    cr1 = (g / (g - 1)) * ((n - 1) / max(1, n - 1))  # CR1 = G/(G-1) * (N-1)/(N-1)
    se = math.sqrt(cr1 * s_sq) / n
    return n, mean_r, mean_r - 1.96 * se, mean_r + 1.96 * se


def val_bootstrap_ci_and_ex5(trades, seed=42):
    if not trades:
        return float("nan"), float("nan"), float("nan")
    by_day = {}
    for t in trades:
        by_day.setdefault(t["entry_day"], []).append(t["net_r"])
    days = sorted(by_day)
    day_sums = np.array([sum(by_day[d]) for d in days])
    day_cnts = np.array([len(by_day[d]) for d in days])
    g = len(days)

    rng = np.random.default_rng(seed)
    idx = rng.integers(0, g, size=(2000, g))
    boot_means = day_sums[idx].sum(axis=1) / day_cnts[idx].sum(axis=1)
    lo, hi = np.percentile(boot_means, [2.5, 97.5])

    # ex-best-5 UTC days (by sum of net R on that day)
    order = np.argsort(day_sums)
    keep = order[:-5] if g > 5 else np.array([], dtype=int)
    ex5 = float(day_sums[keep].sum() / day_cnts[keep].sum()) if len(keep) else float("nan")
    return float(lo), float(hi), ex5


def main():
    btc_1d = load_klines("BTC", "1d")
    labels = compute_phase_labels(btc_1d)

    # Preload data and features for available coins (19/20; ZEC missing)
    data = {}
    for tf in ("1d", "4h"):
        data[tf] = {}
        for coin in COINS:
            bars = load_klines(coin, tf)
            if bars is None:
                continue
            data[tf][coin] = (bars, atr14_sma(bars), compute_features_long(bars, tf))

    top10_specs = [
        (1, "1d", "UP_E", "RIDE", ("ADX_DI", "VOLX")),
        (2, "1d", "UP_E", "RIDE", ("RSI_MOM", "ADX_DI", "VOLX")),
        (3, "1d", "UP_E", "RIDE", ("ADX_DI", "TREND_MA", "VOLX")),
        (4, "4h", "UP_E", "RIDE", ("ADX_DI", "VOLX")),
        (5, "4h", "UP_E", "RIDE", ("RSI_MOM", "VOLX")),
        (6, "1d", "UP_E", "RIDE", ("RSI_MOM", "VOLX")),
        (7, "1d", "UP_E", "RIDE", ("RSI_MOM", "TREND_MA", "VOLX")),
        (8, "1d", "UP_E", "RIDE", ("BRK5", "ADX_DI", "VOLX")),
        (9, "4h", "UP_E", "RIDE", ("BRK5", "RSI_MOM", "ADX_DI")),
        (10, "1d", "UP_E", "RIDE", ("BRK5", "VOLX")),
    ]

    print("Top 10 recompute (19/20 coins, no ZEC, no funding):")
    for rank, tf, phase, exit_mode, combo in top10_specs:
        dev_trades, val_trades = [], []
        for coin, (bars, atr, feats) in data[tf].items():
            n_b = len(bars)
            onsets = []
            prev = False
            for i in range(n_b - 1):
                cur = all(feats[f][i] for f in combo)
                if cur and not prev:
                    ent_day = day_str(bars[i + 1][0])
                    if labels.get(ent_day) == phase:
                        onsets.append(i)
                prev = cur
            dev_sigs = [i for i in onsets if DEV_START_DAY <= day_str(bars[i + 1][0]) <= DEV_END_DAY]
            val_sigs = [i for i in onsets if day_str(bars[i + 1][0]) >= VAL_START_DAY]
            dev_trades.extend(sim_trades(bars, atr, dev_sigs, "LONG", exit_mode, tf, COST_12BP))
            val_trades.extend(sim_trades(bars, atr, val_sigs, "LONG", exit_mode, tf, COST_12BP))

        dn, dm, dlo, dhi = day_cluster_stats(dev_trades)
        vn = len(val_trades)
        vm = sum(t["net_r"] for t in val_trades) / vn if vn else float("nan")
        vlo, vhi, ex5 = val_bootstrap_ci_and_ex5(val_trades)
        print(
            f"#{rank:2d} {tf} {'+'.join(combo):22s} | "
            f"DEV n={dn:3d} mean={dm:.3f} [{dlo:.3f}, {dhi:.3f}] | "
            f"VAL n={vn:3d} mean={vm:.3f} [{vlo:.3f}, {vhi:.3f}] ex5={ex5:.3f}"
        )


if __name__ == "__main__":
    main()
