"""T06 eh-h5-rsi-ma-cross-trigger: RSI14 cross under/over its SMA14 trigger, 4h spot BTC+ETH.

Rules: see PRE_REG.md (frozen). This file implements exactly that table.
Modes:  python rsi_ma_cross.py count   (events per year and side, DEV only, no returns)
        python rsi_ma_cross.py dev     (DEV screen + per-year + exploratory cells)
        python rsi_ma_cross.py val     (VALIDATION read once; refuses unless DEV screen passed)
Data is read from a cache OUTSIDE the repo (F:/MTS/Dumps/backtest/eh-h5-rsi-ma-cross-trigger, else %TEMP%).
"""
import bisect
import csv
import datetime as _dt
import glob
import importlib.util
import math
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True

H4 = 4 * 3600 * 1000
D1 = 24 * 3600 * 1000


def _ms(y, m, d):
    return int(_dt.datetime(y, m, d, tzinfo=_dt.timezone.utc).timestamp() * 1000)


# --- splits (brief s5: DEV = data start..2024-06-30; VAL = 2024-07-01..2025-06-30; HOLDOUT never loaded) ---
DEV_END_MS = _ms(2024, 7, 1)     # exclusive
VAL_END_MS = _ms(2025, 7, 1)     # exclusive: last bar opens 2025-06-30 20:00 UTC
HOLDOUT_START_MS = VAL_END_MS


class SplitRefusal(ValueError):
    pass


def guard_window(t_ms):
    """Refuse any timestamp at or past the frozen range end (HOLDOUT is never loaded)."""
    if t_ms >= VAL_END_MS:
        raise SplitRefusal("timestamp %s is at or past the HOLDOUT boundary %s" % (t_ms, VAL_END_MS))


def dev_only(bars):
    """Refuse bars at or past DEV end (used for the DEV run)."""
    for b in bars:
        if b["t"] >= DEV_END_MS:
            raise SplitRefusal("bar %s past DEV end" % b["t"])
    return bars


# --- constants ---
ARM_LEVEL = 60.0          # SOURCED 60/40 (malkan_40_60.py MLK-R1)
DISARM_LEVEL = 40.0
ARM_BARS = 6              # OURS
MA_N = 14                 # RSI MA = SMA14 of RSI14 (READING.md header)
STOP_BARS = 6             # OURS: swing incl. signal bar
TARGET_R = 2.5            # TRIALS.md T06
HOLD_BARS = 30            # OURS (counting the entry bar)
# fees.py is the single source (B081): taker per side x2 in bps, plus 2 bps RT slippage (FORMULAS s13, OURS value)
_FEES_SPEC = importlib.util.spec_from_file_location("fees_ro", Path(__file__).resolve().parents[4] / "backtest" / "fees.py")
_fees = importlib.util.module_from_spec(_FEES_SPEC)
_FEES_SPEC.loader.exec_module(_fees)
COST_RT_BPS = 2 * _fees.BINANCE_TAKER * 1e4 + 2.0   # regime A round trip = 10 bps taker + 2 bps slippage = 12 bps
M_HOLM = 15               # TRIALS.md
Z_MDE = 2.8               # 80 % power, two-sided 5 %: 2.8 x SE

# --- repo code, read-only ---
_REPO_BT = Path(__file__).resolve().parents[4] / "backtest"
_spec = importlib.util.spec_from_file_location("rsi_core_ro", _REPO_BT / "layers" / "rsi" / "rsi_core.py")
_rsi_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_rsi_mod)
REPO_RSI = _rsi_mod.rsi_core


def _data_root():
    f = Path("F:/MTS/Dumps/backtest")
    if f.exists():
        return f / "eh-h5-rsi-ma-cross-trigger"
    return Path(os.environ.get("TEMP", "/tmp")) / "mts_eh_cache" / "eh-h5-rsi-ma-cross-trigger"


DATA_ROOT = _data_root()


# --- indicators ---
def rsi14(closes):
    return list(REPO_RSI(list(closes), 14))


def sma(vals, n):
    out = [None] * len(vals)
    for i in range(len(vals)):
        if i - n + 1 < 0:
            continue
        w = vals[i - n + 1:i + 1]
        if any(x is None for x in w):
            continue
        out[i] = sum(w) / n
    return out


def _cond(rsi, ma, i, side):
    if i < 0 or rsi[i] is None or ma[i] is None:
        return False
    if side == "short":
        return rsi[i] < ma[i] and rsi[i] < ARM_LEVEL
    return rsi[i] > ma[i] and rsi[i] > DISARM_LEVEL


def _armed(rsi, i, side):
    for j in range(max(0, i - ARM_BARS), i):
        r = rsi[j]
        if r is None:
            continue
        if side == "short" and r >= ARM_LEVEL:
            return True
        if side == "long" and r <= DISARM_LEVEL:
            return True
    return False


def find_events(rsi, ma, side):
    """Signal-bar indices: first bar of a run where the signal holds, and armed in the 6 bars before it (OURS)."""
    ev = []
    for i in range(len(rsi)):
        if _cond(rsi, ma, i, side) and not _cond(rsi, ma, i - 1, side) and _armed(rsi, i, side):
            ev.append(i)
    return ev


# --- trade simulation (no lookahead: entry and exit use bars at or after the signal bar + 1) ---
def simulate(bars, events, side, busy_until=-1, n_bars=HOLD_BARS):
    trades = []
    last = len(bars) - 1
    busy = busy_until
    for i in events:
        e = i + 1
        if e > last or e <= busy:
            continue
        o_i = bars[i]["o"]
        if side == "short":
            if not bars[e]["l"] < o_i:          # sell-stop at open[i] must trade through
                continue
            fill = min(bars[e]["o"], o_i)
            stop = max(b["h"] for b in bars[max(0, i - STOP_BARS + 1):i + 1])
            risk = stop - fill
            tgt = fill - TARGET_R * risk
        else:
            if not bars[e]["h"] > o_i:
                continue
            fill = max(bars[e]["o"], o_i)
            stop = min(b["l"] for b in bars[max(0, i - STOP_BARS + 1):i + 1])
            risk = fill - stop
            tgt = fill + TARGET_R * risk
        if risk <= 0:
            continue
        time_end = e + n_bars - 1
        exit_idx, reason, px = None, None, None
        for j in range(e, min(time_end, last) + 1):
            b = bars[j]
            if side == "short":
                if b["h"] >= stop:                       # stop first (tie -> stop)
                    exit_idx, reason, px = j, "stop", max(stop, b["o"])
                    break
                if b["l"] <= tgt:
                    exit_idx, reason, px = j, "target", min(tgt, b["o"])
                    break
            else:
                if b["l"] <= stop:
                    exit_idx, reason, px = j, "stop", min(stop, b["o"])
                    break
                if b["h"] >= tgt:
                    exit_idx, reason, px = j, "target", max(tgt, b["o"])
                    break
        if exit_idx is None:
            if time_end <= last:
                exit_idx, reason, px = time_end, "time", bars[time_end]["c"]
            else:
                exit_idx, reason, px = last, "open_at_end", bars[last]["c"]   # dropped by the caller
        gross = (fill - px) / risk if side == "short" else (px - fill) / risk
        trades.append({"side": side, "signal_t": bars[i]["t"], "entry_t": bars[e]["t"], "exit_t": bars[exit_idx]["t"],
                       "fill": fill, "stop": stop, "risk": risk, "exit_px": px, "exit_reason": reason,
                       "gross_r": gross, "entry_bar": e, "exit_bar": exit_idx})
        busy = exit_idx
    return trades


# --- costs ---
def fee_r(stop_bps):
    """Round-trip cost in R: 12 bps / stop distance in bps (regime A + slippage)."""
    return COST_RT_BPS / stop_bps


def funding_r(entry_ms, exit_ms, fill, risk, side, funding):
    """Funding cost in R. cost = side_sign x sum(rate, settlement in (entry, exit]); long pays +rate, short receives it."""
    if not funding:
        return 0.0
    sign = 1.0 if side == "long" else -1.0
    s = sum(r for (t, r) in funding if entry_ms < t <= exit_ms)
    return sign * s / (risk / fill)


# --- data ---
def load_spot_4h(symbol, end_ms=VAL_END_MS):
    if end_ms > VAL_END_MS:
        raise SplitRefusal("load end %s past the VALIDATION end" % end_ms)
    files = sorted(glob.glob(str(DATA_ROOT / "spot_2017" / symbol / "4h" / "klines" / ("%s-4h-*.csv" % symbol))))
    if not files:
        raise FileNotFoundError("no 4h cache for %s under %s" % (symbol, DATA_ROOT))
    bars = {}
    for f in files:
        with open(f, newline="", encoding="utf-8") as fh:
            for row in csv.reader(fh):
                if not row or not row[0].isdigit():
                    continue
                t = int(row[0])
                if t >= end_ms:
                    continue
                guard_window(t)
                bars[t] = {"t": t, "o": float(row[1]), "h": float(row[2]), "l": float(row[3]), "c": float(row[4])}
    out = [bars[k] for k in sorted(bars)]
    return out


def load_funding(symbol, end_ms=VAL_END_MS):
    rows = []
    for f in sorted(glob.glob(str(DATA_ROOT / "raw" / "fundingRate" / ("%s-fundingRate-*.csv" % symbol)))):
        with open(f, newline="", encoding="utf-8") as fh:
            for row in csv.reader(fh):
                if not row or not row[0].isdigit():
                    continue
                t = int(row[0])
                t -= t % 1000
                if t < end_ms:
                    rows.append((t, float(row[2])))
    rows.sort()
    return rows


def daily_closes(bars):
    """(open_ms, close) per UTC day from 4h bars; the day's close is its last 4h close."""
    out = []
    for b in bars:
        d = b["t"] // D1 * D1
        if out and out[-1][0] == d:
            out[-1] = (d, b["c"])
        else:
            out.append((d, b["c"]))
    return out


def daily_value_asof(rows, t):
    """Last (open_ms, value) whose day is CLOSED at t, i.e. open_ms + 1 day <= t (no lookahead)."""
    keys = [r[0] for r in rows]
    k = bisect.bisect_right(keys, t - D1) - 1
    return rows[k][1] if k >= 0 else None


# --- statistics (cluster by ISO week) ---
def _phi(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def stats(trades):
    n = len(trades)
    if n == 0:
        return {"n": 0}
    net = [t["net_r"] for t in trades]
    mean = sum(net) / n
    groups = {}
    for t, x in zip(trades, net):
        k = _dt.datetime.fromtimestamp(t["entry_t"] / 1000, _dt.timezone.utc).isocalendar()[:2]
        groups[k] = groups.get(k, 0.0) + (x - mean)
    se = math.sqrt(sum(g * g for g in groups.values())) / n
    p = 1.0 - _phi(mean / se) if se > 0 else float("nan")
    return {"n": n, "hit": sum(1 for x in net if x > 0) / n,
            "gross": sum(t["gross_r"] for t in trades) / n, "fee": sum(t["fee_r"] for t in trades) / n,
            "fund": sum(t["fund_r"] for t in trades) / n, "net": mean, "se": se,
            "ci_lo": mean - 1.96 * se, "ci_hi": mean + 1.96 * se, "mde": Z_MDE * se,
            "p_one": p, "holm15": min(1.0, M_HOLM * p) if p == p else float("nan"),
            "clusters": len(groups)}


def dev_screen_pass(s):
    return s.get("n", 0) >= 30 and s["net"] > 0 and s["ci_lo"] > 0


# --- regime tag (re-implements research_kit.regime_tag rule; copied, not imported, to avoid side effects) ---
def _iso_week_start(day_open):
    days = day_open // D1
    wd = (days + 3) % 7          # 1970-01-01 was a Thursday; Monday = 0
    return day_open - wd * D1


def regime_tags(bars, week_starts):
    dc = daily_closes(bars)
    # weekly closes (week start, close = last daily close, usable at week start + 7d)
    wk = {}
    for d, c in dc:
        wk[_iso_week_start(d)] = c
    wk_keys = sorted(wk)
    wk_rsi = list(zip([k + 7 * D1 for k in wk_keys], rsi14([wk[k] for k in wk_keys])))
    mo = {}
    for d, c in dc:
        dt = _dt.datetime.fromtimestamp(d / 1000, _dt.timezone.utc)
        mo[(dt.year, dt.month)] = (c, d)
    mo_keys = sorted(mo, key=lambda k: mo[k][1])
    mo_close_t = []
    for k in mo_keys:
        y, m = k
        nxt = _ms(y + (m == 12), (m % 12) + 1, 1)
        mo_close_t.append(nxt)
    mo_rsi = list(zip(mo_close_t, rsi14([mo[k][0] for k in mo_keys])))
    out = []
    for t in week_starts:
        sma200 = None
        cl = [c for (d, c) in dc if d + D1 <= t]
        if len(cl) >= 200:
            sma200 = sum(cl[-200:]) / 200
        last_close = cl[-1] if cl else None
        side = None if sma200 is None else ("above" if last_close > sma200 else "below")
        w = [r for (ct, r) in wk_rsi if ct <= t]
        m = [r for (ct, r) in mo_rsi if ct <= t]
        wr = w[-1] if w else None
        mr = m[-1] if m else None
        if side is None or wr is None or mr is None or wr is None:
            out.append(None)
            continue
        if wr >= 60 and mr >= 60:
            band = "bull"
        elif wr <= 40 and mr <= 40:
            band = "bear"
        else:
            band = "mid"
        if band == "bull" and side == "above":
            out.append("bull")
        elif band == "bear" and side == "below":
            out.append("bear")
        else:
            out.append("range")
    return out


# --- run one symbol / side ---
def events_for(bars, side):
    closes = [b["c"] for b in bars]
    r = rsi14(closes)
    ma = sma(r, MA_N)
    return find_events(r, ma, side)


def run(symbols, side_list, lo_ms, hi_ms, funding_on=True):
    """All trades whose SIGNAL bar lies in [lo_ms, hi_ms). Bars are loaded to hi_ms (exclusive)."""
    out = []
    dropped = {"open_at_end": 0}
    for sym in symbols:
        bars = load_spot_4h(sym, end_ms=hi_ms)
        if hi_ms <= DEV_END_MS:
            dev_only(bars)
        fund = load_funding(sym, end_ms=hi_ms) if funding_on else []
        dc = daily_closes(bars)
        drows = list(zip([d for d, _ in dc], rsi14([c for _, c in dc])))
        for side in side_list:
            ev = [i for i in events_for(bars, side) if lo_ms <= bars[i]["t"] < hi_ms]
            trs = simulate(bars, ev, side)
            for tr in trs:
                if tr["exit_reason"] == "open_at_end":
                    dropped["open_at_end"] += 1
                    continue
                tr["symbol"] = sym
                tr["year"] = _dt.datetime.fromtimestamp(tr["entry_t"] / 1000, _dt.timezone.utc).year
                stop_bps = tr["risk"] / tr["fill"] * 1e4
                tr["fee_r"] = fee_r(stop_bps)
                tr["fund_r"] = funding_r(tr["entry_t"], tr["exit_t"], tr["fill"], tr["risk"], side, fund)
                tr["net_r"] = tr["gross_r"] - tr["fee_r"] - tr["fund_r"]
                dr = daily_value_asof(drows, tr["signal_t"] + H4)   # last day closed by the signal bar's close
                tr["daily_rsi"] = dr
                tr["daily_ok"] = (dr is not None) and ((dr < ARM_LEVEL) if side == "short" else (dr > DISARM_LEVEL))
                out.append(tr)
    return out, dropped


def main(argv):
    mode = argv[1] if len(argv) > 1 else "dev"
    syms = ["BTCUSDT", "ETHUSDT"]
    if mode == "count":
        for side in ("short", "long"):
            for sym in syms:
                bars = load_spot_4h(sym, end_ms=DEV_END_MS)
                ev = [i for i in events_for(bars, side)]
                by = {}
                for i in ev:
                    y = _dt.datetime.fromtimestamp(bars[i]["t"] / 1000, _dt.timezone.utc).year
                    by[y] = by.get(y, 0) + 1
                print("COUNT", side, sym, "DEV events", len(ev), sorted(by.items()))
        return 0
    if mode == "dev":
        tr, dropped = run(syms, ["short", "long"], _ms(2017, 8, 1), DEV_END_MS)
        print("DEV dropped (open at data end):", dropped)
        print("DEV pooled T06", stats(tr))
        for side in ("short", "long"):
            print("DEV side", side, stats([t for t in tr if t["side"] == side]))
        for sym in syms:
            print("DEV sym", sym, stats([t for t in tr if t["symbol"] == sym]))
        for side in ("short", "long"):
            print("DEV EXPL daily-filter on", side, stats([t for t in tr if t["side"] == side and t["daily_ok"]]))
            print("DEV EXPL daily-filter off", side, stats([t for t in tr if t["side"] == side and not t["daily_ok"]]))
        print("DEV exit reasons", {r: sum(1 for t in tr if t["exit_reason"] == r) for r in ("stop", "target", "time")})
        for y in sorted({t["year"] for t in tr}):
            print("DEV year", y, stats([t for t in tr if t["year"] == y]))
        return 0
    if mode == "val":
        dev_tr, _ = run(syms, ["short", "long"], _ms(2017, 8, 1), DEV_END_MS)
        if not dev_screen_pass(stats(dev_tr)):
            print("VAL refused: DEV screen not passed; VALIDATION stays unread")
            return 2
        tr, dropped = run(syms, ["short", "long"], DEV_END_MS, VAL_END_MS)
        print("VAL dropped (open at data end):", dropped)
        print("VAL pooled T06", stats(tr))
        return 0
    raise SystemExit("unknown mode " + mode)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
