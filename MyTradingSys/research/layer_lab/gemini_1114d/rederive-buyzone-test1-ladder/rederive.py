"""Independent blind re-derivation of buyzone_test1_ladder_2026-11-14 from PRE_REG.md and FORMULAS.md."""

from __future__ import annotations

import datetime as dt
import json
import math
import os
import random
from collections import defaultdict
from pathlib import Path

CACHE_DIR = Path(
    os.environ.get("MTS_DATA_CACHE", "C:/Users/e-ngineers/MTS_data_cache/binance_spot_1d")
)

COINS = [
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "XRPUSDT",
    "ADAUSDT",
    "DOGEUSDT",
    "SOLUSDT",
    "LTCUSDT",
    "LINKUSDT",
    "TRXUSDT",
    "DOTUSDT",
    "AVAXUSDT",
    "ATOMUSDT",
    "ETCUSDT",
    "XLMUSDT",
    "BCHUSDT",
    "NEOUSDT",
    "UNIUSDT",
    "NEARUSDT",
    "FILUSDT",
    "ALGOUSDT",
    "VETUSDT",
]

WARMUP = 400
MAX_HOLD = 30
FEE_12 = 0.0012
FEE_6 = 0.0006
SEED = 1114
N_PLACEBO = 2000
N_BOOT = 10000


def load_bars(coin: str, today_utc: dt.date) -> list[dict]:
    path = CACHE_DIR / f"{coin}.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    bars = []
    for row in raw:
        d = dt.datetime.fromtimestamp(row[0] / 1000.0, tz=dt.timezone.utc).date()
        if d >= today_utc:
            continue
        bars.append(
            {
                "date": d,
                "open": float(row[1]),
                "high": float(row[2]),
                "low": float(row[3]),
                "close": float(row[4]),
            }
        )
    return bars


def compute_sma(values: list[float], period: int) -> list[float | None]:
    n = len(values)
    out: list[float | None] = [None] * n
    if n < period:
        return out
    s = sum(values[:period])
    out[period - 1] = s / period
    for i in range(period, n):
        s += values[i] - values[i - period]
        out[i] = s / period
    return out


def compute_rsi_wilder(closes: list[float], period: int = 14) -> list[float | None]:
    """Textbook Wilder RSI per FORMULAS.md section 1."""
    n = len(closes)
    out: list[float | None] = [None] * n
    if n <= period:
        return out
    deltas = [closes[i] - closes[i - 1] for i in range(1, n)]
    avg_gain = sum(max(d, 0.0) for d in deltas[:period]) / period
    avg_loss = sum(max(-d, 0.0) for d in deltas[:period]) / period

    def _rsi(ag: float, al: float) -> float:
        if al == 0.0:
            return 100.0 if ag > 0.0 else 50.0
        rs = ag / al
        return 100.0 - 100.0 / (1.0 + rs)

    out[period] = _rsi(avg_gain, avg_loss)
    for i in range(period + 1, n):
        d = deltas[i - 1]
        gain = max(d, 0.0)
        loss = max(-d, 0.0)
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
        out[i] = _rsi(avg_gain, avg_loss)
    return out


def compute_atr_wilder(bars: list[dict], period: int = 14) -> list[float | None]:
    """Wilder RMA of True Range per FORMULAS.md section 2."""
    n = len(bars)
    out: list[float | None] = [None] * n
    if n <= period:
        return out
    trs = [0.0] * n
    trs[0] = bars[0]["high"] - bars[0]["low"]
    for i in range(1, n):
        h = bars[i]["high"]
        l = bars[i]["low"]
        pc = bars[i - 1]["close"]
        trs[i] = max(h - l, abs(h - pc), abs(l - pc))
    rma = sum(trs[1 : period + 1]) / period
    out[period] = rma
    for i in range(period + 1, n):
        rma = (rma * (period - 1) + trs[i]) / period
        out[i] = rma
    return out


def compute_phases(bars: list[dict], sma200: list[float | None], sma350: list[float | None]) -> list[str | None]:
    """Phase at bar t per PRE_REG.md."""
    n = len(bars)
    phases: list[str | None] = [None] * n
    for t in range(379, n):
        s200 = sma200[t]
        s200_30 = sma200[t - 30]
        s350 = sma350[t]
        s350_30 = sma350[t - 30]
        if s200 is None or s200_30 is None or s350 is None or s350_30 is None:
            continue
        c = bars[t]["close"]
        max_h_365 = max(bars[k]["high"] for k in range(t - 364, t + 1))
        dd = 1.0 - c / max_h_365
        min_low_60 = min(bars[k]["low"] for k in range(t - 59, t + 1))
        min_low_120 = min(bars[k]["low"] for k in range(t - 179, t - 59))
        higher_low = min_low_60 >= min_low_120

        if c > s200 and s200 > s200_30:
            phases[t] = "UP"
        elif dd >= 0.40 and higher_low:
            phases[t] = "BASE"
        elif c < s350 and s350 < s350_30 and dd >= 0.40:
            phases[t] = "POSTPEAK_BEAR"
        elif c < s200 and s200 < s200_30:
            phases[t] = "DOWN"
        else:
            phases[t] = "RANGE"
    return phases


def find_swing_lows(bars: list[dict], k: int = 3) -> list[int]:
    n = len(bars)
    swings = []
    for i in range(k, n - k):
        li = bars[i]["low"]
        if all(li < bars[i - d]["low"] for d in range(1, k + 1)) and all(
            li < bars[i + d]["low"] for d in range(1, k + 1)
        ):
            swings.append(i)
    return swings


def simulate_exit(bars: list[dict], atr14: list[float | None], e: int, init_stop: float) -> tuple[int, float] | None:
    """Simulate trailing stop / 30d exit from entry bar e. Returns (exit_idx, exit_price) or None if exit bar not in data."""
    n = len(bars)
    if e + MAX_HOLD - 1 >= n:
        return None
    # Bar e: only initial stop checked
    if bars[e]["low"] <= init_stop:
        return e, min(bars[e]["open"], init_stop)
    max_high = bars[e]["high"]
    for t in range(e + 1, e + MAX_HOLD):
        atr_prev = atr14[t - 1]
        assert atr_prev is not None
        level = max(init_stop, max_high - 2.0 * atr_prev)
        if bars[t]["low"] <= level:
            return t, min(bars[t]["open"], level)
        if bars[t]["high"] > max_high:
            max_high = bars[t]["high"]
    return e + MAX_HOLD - 1, bars[e + MAX_HOLD - 1]["close"]


def extract_events(
    coin: str,
    bars: list[dict],
    rsi14: list[float | None],
    atr14: list[float | None],
    phases: list[str | None],
    swings: list[int],
    kind: str,
) -> tuple[list[dict], dict[str, int]]:
    """Extract candidate A (HL_BREAK) or B (BULL_DIV) events with lockout."""
    n = len(bars)
    raw_signals = []
    stats = {"dropped_stop": 0, "dropped_no_exit": 0, "dropped_lockout": 0}

    for idx in range(1, len(swings)):
        p = swings[idx - 1]
        j = swings[idx]
        if not (10 <= j - p <= 60):
            continue
        if kind == "HL_BREAK":
            if not (bars[j]["low"] > bars[p]["low"]):
                continue
        elif kind == "BULL_DIV":
            if rsi14[j] is None or rsi14[p] is None:
                continue
            if not (bars[j]["low"] < bars[p]["low"] and rsi14[j] > rsi14[p]):
                continue
        else:
            raise ValueError(kind)

        h_level = max(bars[k]["high"] for k in range(p, j + 1))
        low_j = bars[j]["low"]

        # Check j+1 .. j+2 for violation only (closes above H here don't count or consume setup)
        violated = False
        for k in range(j + 1, min(j + 3, n)):
            if bars[k]["low"] <= low_j:
                violated = True
                break
        if violated:
            continue

        # Scan c in j+3 .. min(j+33, n-1)
        for c in range(j + 3, min(j + 34, n)):
            if bars[c]["low"] <= low_j:
                break
            if bars[c]["close"] > h_level:
                raw_signals.append((c, j, p))
                break

    # Sort by signal bar c (in case multiple pairs share order)
    raw_signals.sort(key=lambda x: x[0])

    kept: list[dict] = []
    prev_c = -10**9
    prev_exit = -10**9

    for c, j, p in raw_signals:
        e = c + 1
        if e < WARMUP or e >= n:
            continue
        if c - prev_c < 10 or e <= prev_exit:
            stats["dropped_lockout"] += 1
            continue
        atr_c = atr14[c]
        if atr_c is None:
            continue
        entry = bars[e]["open"]
        low_j = bars[j]["low"]
        init_stop = low_j - max(0.6 * atr_c, 0.005 * low_j)
        if entry <= init_stop:
            stats["dropped_stop"] += 1
            continue
        r_frac = (entry - init_stop) / entry
        sim = simulate_exit(bars, atr14, e, init_stop)
        if sim is None:
            stats["dropped_no_exit"] += 1
            continue
        exit_idx, exit_price = sim
        phase = phases[e - 1]
        if phase is None:
            continue

        gross = exit_price / entry - 1.0
        r12 = (gross - FEE_12) / r_frac
        r6 = (gross - FEE_6) / r_frac

        kept.append(
            {
                "coin": coin,
                "c": c,
                "e": e,
                "exit_idx": exit_idx,
                "entry_date": bars[e]["date"],
                "phase": phase,
                "r_frac": r_frac,
                "r12": r12,
                "r6": r6,
                "gross": gross,
            }
        )
        prev_c = c
        prev_exit = exit_idx

    return kept, stats


def split_of(d: dt.date) -> list[str]:
    out = []
    if d <= dt.date(2023, 12, 31):
        out.append("DEV")
    else:
        out.append("VAL")
        if d >= dt.date(2025, 7, 1):
            out.append("RECENT")
    return out


def block_bootstrap_ci(events: list[dict], key: str = "r12", n_boot: int = N_BOOT, seed: int = SEED) -> tuple[float, float]:
    if not events:
        return (float("nan"), float("nan"))
    min_d = min(ev["entry_date"] for ev in events)
    blocks: dict[int, list[float]] = defaultdict(list)
    for ev in events:
        b = (ev["entry_date"] - min_d).days // 30
        blocks[b].append(ev[key])
    block_list = list(blocks.values())
    m = len(block_list)
    rng = random.Random(seed)
    means = []
    for _ in range(n_boot):
        tot = 0.0
        cnt = 0
        for _ in range(m):
            blk = block_list[rng.randrange(m)]
            tot += sum(blk)
            cnt += len(blk)
        means.append(tot / cnt)
    means.sort()
    lo_idx = int(0.025 * (n_boot - 1))
    hi_idx = int(0.975 * (n_boot - 1))
    # Linear interpolation
    def pct(p: float) -> float:
        pos = p * (n_boot - 1)
        lo = int(math.floor(pos))
        hi = int(math.ceil(pos))
        if lo == hi:
            return means[lo]
        return means[lo] + (pos - lo) * (means[hi] - means[lo])

    return pct(0.025), pct(0.975)


def percentile_linear(sorted_vals: list[float], p: float) -> float:
    n = len(sorted_vals)
    if n == 0:
        return float("nan")
    pos = p * (n - 1)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return sorted_vals[lo]
    return sorted_vals[lo] + (pos - lo) * (sorted_vals[hi] - sorted_vals[lo])


def run_placebo(
    events: list[dict],
    eligible_days: dict[tuple[str, str, str], list[int]],
    coin_data: dict[str, tuple[list[dict], list[float | None]]],
    split_name: str,
    n_draws: int = N_PLACEBO,
    seed: int = SEED,
) -> dict:
    if not events:
        return {"p025": float("nan"), "p975": float("nan"), "pct": float("nan")}
    # Precompute placebo R12 pool per (coin, phase, r_frac) or directly per event?
    # Note: each event has its own r_frac, so simulate for sampled day e
    rng = random.Random(seed)
    # Cache (coin, e_idx, r_frac) -> r12 if repeated? Even simpler, there are ~200-500 events * 2000 draws;
    # let's cache exit simulation per (coin, e_idx, round(r_frac, 12)) or just compute directly (fast enough in Python: ~30 bars).
    draw_means = []
    ev_pools = []
    for ev in events:
        pool = eligible_days[(ev["coin"], split_name, ev["phase"])]
        ev_pools.append((ev["coin"], ev["r_frac"], pool))

    cache: dict[tuple[str, int, float], float] = {}
    for _ in range(n_draws):
        tot = 0.0
        for coin, r_frac, pool in ev_pools:
            e = pool[rng.randrange(len(pool))]
            ck = (coin, e, r_frac)
            val = cache.get(ck)
            if val is None:
                bars, atr14 = coin_data[coin]
                entry = bars[e]["open"]
                init_stop = entry * (1.0 - r_frac)
                sim = simulate_exit(bars, atr14, e, init_stop)
                assert sim is not None
                _, exit_price = sim
                val = ((exit_price / entry - 1.0) - FEE_12) / r_frac
                cache[ck] = val
            tot += val
        draw_means.append(tot / len(events))

    actual_mean = sum(ev["r12"] for ev in events) / len(events)
    draw_means.sort()
    p025 = percentile_linear(draw_means, 0.025)
    p975 = percentile_linear(draw_means, 0.975)
    pct = 100.0 * sum(1 for m in draw_means if m <= actual_mean) / len(draw_means)
    return {"p025": p025, "p975": p975, "pct": pct}


def main() -> None:
    today_utc = dt.date(2026, 11, 14)
    coin_data: dict[str, tuple[list[dict], list[float | None]]] = {}
    eligible_days: dict[tuple[str, str, str], list[int]] = defaultdict(list)

    events_by_kind: dict[str, list[dict]] = {"HL_BREAK": [], "BULL_DIV": []}
    drop_totals: dict[str, dict[str, int]] = {
        "HL_BREAK": defaultdict(int),
        "BULL_DIV": defaultdict(int),
    }

    for coin in COINS:
        bars = load_bars(coin, today_utc)
        closes = [b["close"] for b in bars]
        sma200 = compute_sma(closes, 200)
        sma350 = compute_sma(closes, 350)
        rsi14 = compute_rsi_wilder(closes, 14)
        atr14 = compute_atr_wilder(bars, 14)
        phases = compute_phases(bars, sma200, sma350)
        swings = find_swing_lows(bars, 3)

        coin_data[coin] = (bars, atr14)

        # Eligible placebo entry days: past warm-up (e >= 400), exit in data (e + 29 < len(bars)), phase defined at e-1
        n = len(bars)
        for e in range(WARMUP, n - MAX_HOLD + 1):
            ph = phases[e - 1]
            if ph is None:
                continue
            for sp in split_of(bars[e]["date"]):
                eligible_days[(coin, sp, ph)].append(e)

        for kind in ("HL_BREAK", "BULL_DIV"):
            evs, st = extract_events(coin, bars, rsi14, atr14, phases, swings, kind)
            events_by_kind[kind].extend(evs)
            for k, v in st.items():
                drop_totals[kind][k] += v

    print(f"Coins loaded: {len(COINS)}")
    for kind in ("HL_BREAK", "BULL_DIV"):
        print(f"\n=== {kind} (drops: {dict(drop_totals[kind])}) ===")
        evs_all = events_by_kind[kind]
        for group_name, allowed_phases in [
            ("UP+BASE", {"UP", "BASE"}),
            ("UP", {"UP"}),
            ("BASE", {"BASE"}),
            ("RANGE", {"RANGE"}),
            ("DOWN", {"DOWN"}),
            ("POSTPEAK_BEAR", {"POSTPEAK_BEAR"}),
        ]:
            for sp in ("DEV", "VAL", "RECENT"):
                cell = [
                    ev
                    for ev in evs_all
                    if ev["phase"] in allowed_phases and sp in split_of(ev["entry_date"])
                ]
                n_ev = len(cell)
                if n_ev == 0:
                    print(f"  {group_name:14s} {sp:6s}: n=0")
                    continue
                win_pct = 100.0 * sum(1 for ev in cell if ev["r12"] > 0) / n_ev
                mean12 = sum(ev["r12"] for ev in cell) / n_ev
                mean6 = sum(ev["r6"] for ev in cell) / n_ev
                if group_name == "UP+BASE":
                    ci_lo, ci_hi = block_bootstrap_ci(cell, "r12")
                    plac = run_placebo(cell, eligible_days, coin_data, sp)
                    yr_counts = defaultdict(int)
                    for ev in cell:
                        yr_counts[ev["entry_date"].year] += 1
                    max_yr_share = max(yr_counts.values()) / n_ev
                    print(
                        f"  {group_name:14s} {sp:6s}: n={n_ev:4d} win={win_pct:5.2f}% "
                        f"meanR12={mean12:+.4f} meanR6={mean6:+.4f} "
                        f"CI=[{ci_lo:+.4f}, {ci_hi:+.4f}] "
                        f"plac=[{plac['p025']:+.4f}, {plac['p975']:+.4f}] pct={plac['pct']:.2f}% "
                        f"maxYrShare={max_yr_share:.3f}"
                    )
                else:
                    print(
                        f"  {group_name:14s} {sp:6s}: n={n_ev:4d} win={win_pct:5.2f}% "
                        f"meanR12={mean12:+.4f} meanR6={mean6:+.4f}"
                    )

        # Verdict check on UP+BASE
        dev_ub = [ev for ev in evs_all if ev["phase"] in {"UP", "BASE"} and "DEV" in split_of(ev["entry_date"])]
        val_ub = [ev for ev in evs_all if ev["phase"] in {"UP", "BASE"} and "VAL" in split_of(ev["entry_date"])]
        dev_m12 = sum(ev["r12"] for ev in dev_ub) / len(dev_ub)
        val_m12 = sum(ev["r12"] for ev in val_ub) / len(val_ub)
        ci_lo, _ = block_bootstrap_ci(val_ub, "r12")
        plac = run_placebo(val_ub, eligible_days, coin_data, "VAL")
        if len(val_ub) < 30:
            verdict = "UNDERPOWERED"
        elif val_m12 > 0 and ci_lo > 0 and val_m12 > plac["p975"] and dev_m12 > 0:
            verdict = "PASS"
        else:
            verdict = "KILL"
        print(f"  --> VERDICT ({kind}): {verdict}")


if __name__ == "__main__":
    main()
