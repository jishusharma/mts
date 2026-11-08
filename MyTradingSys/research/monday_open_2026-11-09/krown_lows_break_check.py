"""Helper script for gemini-argon-krown-lows-break-check-1109.

Independently measures Eric Krown's 'lows break -> ~10% more downside' claim on BTC daily history
(blockchain.info 2010-08-18..2017-08-16 + Binance BTCUSDT 1d 2017-08-17..2026-11-08, topped up via
public data-api.binance.vision).

Computes:
1. Current November 2026 reference levels (Oct low 76,325.98, Sep-15 low 74,967.97, Nov-6 low 74,888.00,
   200-day SMA, 200-week SMA, -10% and -10.6% target prices).
2. Monthly-low break study (Krown's e2-KjJdWbgM / M4mTHyPxMUM framing: calendar month trading below
   prior month's low): frequency of >=10% and >=10.6% further downside, quartiles (25th/50th/75th),
   and split by first-break day outcome (sweep & daily close back above prior month's low vs daily
   close below prior month's low), across full history (2011-02..2026-10, 188 months) and Binance spot
   era (2017-09..2026-10, 109 months).
3. Daily rolling N-day first-break study (N in {14, 20, 30, 50} days, forward windows F in {7, 14, 30} days)
   on Binance true daily high/low bars (2017-08-17..2026-11-08), split by sweep-reclaim (close > prior_low)
   vs close-breakdown (close <= prior_low).
4. Confirmed fractal swing-low break study (k in {5, 7, 10} days left/right, forward windows F in {7, 14, 30}
   days) on Binance daily bars, split by sweep-reclaim vs close-breakdown.
"""
import argparse
import csv
import datetime as dt
import json
import pathlib
import statistics
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[3]
DAILY_CSV = ROOT / "MyTradingSys" / "research" / "btc_cycles_2026-11" / "btc_daily.csv"
BINANCE_START = "2017-08-17"
CUTOFF_DATE = "2026-11-08"


def load_daily(csv_path=DAILY_CSV, fetch_recent=True, cutoff=CUTOFF_DATE):
    """Load daily (high, low, close, source) keyed by YYYY-MM-DD up to `cutoff`."""
    rows = {}
    with open(csv_path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["date"] <= cutoff:
                rows[r["date"]] = (
                    float(r["high"]),
                    float(r["low"]),
                    float(r["close"]),
                    r["source"],
                )
    if fetch_recent:
        last_dt = dt.date.fromisoformat(max(rows.keys()))
        start_ms = int(
            dt.datetime.combine(last_dt, dt.time(), dt.timezone.utc).timestamp() * 1000
        )
        url = (
            "https://data-api.binance.vision/api/v3/klines"
            f"?symbol=BTCUSDT&interval=1d&startTime={start_ms}&limit=30"
        )
        try:
            with urllib.request.urlopen(url, timeout=15) as resp:
                klines = json.loads(resp.read())
            for k in klines:
                d_str = (
                    dt.datetime.fromtimestamp(k[0] // 1000, dt.timezone.utc)
                    .date()
                    .isoformat()
                )
                if d_str <= cutoff:
                    rows[d_str] = (
                        float(k[2]),
                        float(k[3]),
                        float(k[4]),
                        "binance",
                    )
        except OSError:
            pass
    return dict(sorted(rows.items()))


def percentiles(vals):
    """Return (q25_worst, median, q75_mild) for negative percentage drops using inclusive quartiles."""
    if not vals:
        return (0.0, 0.0, 0.0)
    s = sorted(vals)
    if len(s) < 4:
        med = statistics.median(s)
        return (s[0], med, s[-1])
    qs = statistics.quantiles(s, n=4, method="inclusive")
    return (qs[0], qs[1], qs[2])


def monthly_low_breaks(rows, start_ym="2011-02", end_ym="2026-10"):
    """Evaluate calendar months in [start_ym, end_ym] that trade below the prior month's low."""
    by_month = {}
    for d, (h, l, c, src) in rows.items():
        by_month.setdefault(d[:7], []).append((d, h, l, c))
    all_months = sorted(by_month.keys())
    eval_months = [m for m in all_months if start_ym <= m <= end_ym]

    events = []
    for m in eval_months:
        idx = all_months.index(m)
        if idx == 0:
            continue
        prev_m = all_months[idx - 1]
        prev_low = min(x[2] for x in by_month[prev_m])
        cur_days = by_month[m]
        cur_low = min(x[2] for x in cur_days)
        if cur_low < prev_low:
            # Find the first day in month m that broke below prev_low
            first_brk = next(x for x in cur_days if x[2] < prev_low)
            reclaimed_day1 = first_brk[3] > prev_low
            drop_pct = (cur_low / prev_low - 1.0) * 100.0
            # Also measure forward drop from first_brk close to rest-of-month low
            brk_idx = cur_days.index(first_brk)
            rem_low = min(x[2] for x in cur_days[brk_idx:])
            rem_drop_from_prev = (rem_low / prev_low - 1.0) * 100.0
            events.append(
                {
                    "month": m,
                    "prev_month": prev_m,
                    "prev_low": prev_low,
                    "month_low": cur_low,
                    "first_break_date": first_brk[0],
                    "first_break_low": first_brk[2],
                    "first_break_close": first_brk[3],
                    "reclaimed_day1": reclaimed_day1,
                    "drop_pct": drop_pct,
                    "rem_drop_pct": rem_drop_from_prev,
                }
            )
    return len(eval_months), events


def summarize_monthly(total_months, events):
    drops = [e["drop_pct"] for e in events]
    q25, med, q75 = percentiles(drops)
    ge10 = sum(1 for d in drops if d <= -10.0)
    ge106 = sum(1 for d in drops if d <= -10.6)
    rec = [e["drop_pct"] for e in events if e["reclaimed_day1"]]
    brk = [e["drop_pct"] for e in events if not e["reclaimed_day1"]]
    return {
        "total_months": total_months,
        "n_breaks": len(events),
        "break_rate_pct": round(len(events) / total_months * 100.0, 1) if total_months else 0.0,
        "ge10_n": ge10,
        "ge10_pct": round(ge10 / len(events) * 100.0, 1) if events else 0.0,
        "ge106_n": ge106,
        "ge106_pct": round(ge106 / len(events) * 100.0, 1) if events else 0.0,
        "q25_worst_pct": round(q25, 2),
        "median_pct": round(med, 2),
        "q75_mild_pct": round(q75, 2),
        "sweep_n": len(rec),
        "sweep_ge10_n": sum(1 for d in rec if d <= -10.0),
        "sweep_ge10_pct": round(sum(1 for d in rec if d <= -10.0) / len(rec) * 100.0, 1) if rec else 0.0,
        "sweep_median_pct": round(statistics.median(rec), 2) if rec else 0.0,
        "close_below_n": len(brk),
        "close_below_ge10_n": sum(1 for d in brk if d <= -10.0),
        "close_below_ge10_pct": round(sum(1 for d in brk if d <= -10.0) / len(brk) * 100.0, 1) if brk else 0.0,
        "close_below_median_pct": round(statistics.median(brk), 2) if brk else 0.0,
    }


def rolling_nday_breaks(rows, lookback_n, fwd_days, start_date=BINANCE_START):
    """First-break events where day i breaks below the prior `lookback_n`-day low (and day i-1 did not)."""
    dates = [d for d in sorted(rows.keys()) if d >= start_date]
    events = []
    for i in range(lookback_n, len(dates) - fwd_days):
        prior_low = min(rows[dates[j]][1] for j in range(i - lookback_n, i))
        prev_prior_low = min(rows[dates[j - 1]][1] for j in range(i - lookback_n, i))
        cur_low = rows[dates[i]][1]
        cur_close = rows[dates[i]][2]
        prev_low = rows[dates[i - 1]][1]
        if cur_low < prior_low and prev_low >= prev_prior_low:
            fwd_low_inc = min(rows[dates[j]][1] for j in range(i, i + fwd_days + 1))
            fwd_low_after = min(rows[dates[j]][1] for j in range(i + 1, i + fwd_days + 1))
            drop_inc = (fwd_low_inc / prior_low - 1.0) * 100.0
            drop_after = (fwd_low_after / prior_low - 1.0) * 100.0
            reclaim = cur_close > prior_low
            events.append(
                {
                    "date": dates[i],
                    "prior_low": prior_low,
                    "cur_low": cur_low,
                    "cur_close": cur_close,
                    "drop_inc_pct": drop_inc,
                    "drop_after_pct": drop_after,
                    "reclaim": reclaim,
                }
            )
    return summarize_break_events(events)


def fractal_swing_breaks(rows, k_bars, fwd_days, start_date=BINANCE_START):
    """Breaks of the most recent confirmed k-bar fractal swing low (strictly lower than k bars left, <= k bars right)."""
    dates = [d for d in sorted(rows.keys()) if d >= start_date]
    active_low = None
    active_date = None
    events = []
    for i in range(k_bars, len(dates) - fwd_days):
        cand = i - k_bars
        if cand >= k_bars:
            c_low = rows[dates[cand]][1]
            left_ok = all(rows[dates[j]][1] > c_low for j in range(cand - k_bars, cand))
            right_ok = all(rows[dates[j]][1] >= c_low for j in range(cand + 1, cand + k_bars + 1))
            if left_ok and right_ok:
                active_low = c_low
                active_date = dates[cand]
        if active_low is not None and rows[dates[i]][1] < active_low:
            cur_low = rows[dates[i]][1]
            cur_close = rows[dates[i]][2]
            fwd_low_inc = min(rows[dates[j]][1] for j in range(i, i + fwd_days + 1))
            fwd_low_after = min(rows[dates[j]][1] for j in range(i + 1, i + fwd_days + 1))
            drop_inc = (fwd_low_inc / active_low - 1.0) * 100.0
            drop_after = (fwd_low_after / active_low - 1.0) * 100.0
            reclaim = cur_close > active_low
            events.append(
                {
                    "date": dates[i],
                    "swing_date": active_date,
                    "prior_low": active_low,
                    "cur_low": cur_low,
                    "cur_close": cur_close,
                    "drop_inc_pct": drop_inc,
                    "drop_after_pct": drop_after,
                    "reclaim": reclaim,
                }
            )
            active_low = None
    return summarize_break_events(events)


def summarize_break_events(events):
    drops = [e["drop_inc_pct"] for e in events]
    q25, med, q75 = percentiles(drops)
    ge10 = sum(1 for d in drops if d <= -10.0)
    rec = [e["drop_inc_pct"] for e in events if e["reclaim"]]
    brk = [e["drop_inc_pct"] for e in events if not e["reclaim"]]
    return {
        "n": len(events),
        "ge10_n": ge10,
        "ge10_pct": round(ge10 / len(events) * 100.0, 1) if events else 0.0,
        "q25_worst_pct": round(q25, 2),
        "median_pct": round(med, 2),
        "q75_mild_pct": round(q75, 2),
        "sweep_n": len(rec),
        "sweep_ge10_n": sum(1 for d in rec if d <= -10.0),
        "sweep_ge10_pct": round(sum(1 for d in rec if d <= -10.0) / len(rec) * 100.0, 1) if rec else 0.0,
        "sweep_median_pct": round(statistics.median(rec), 2) if rec else 0.0,
        "close_below_n": len(brk),
        "close_below_ge10_n": sum(1 for d in brk if d <= -10.0),
        "close_below_ge10_pct": round(sum(1 for d in brk if d <= -10.0) / len(brk) * 100.0, 1) if brk else 0.0,
        "close_below_median_pct": round(statistics.median(brk), 2) if brk else 0.0,
    }


def current_context(rows):
    dates = sorted(rows.keys())
    closes = [rows[d][2] for d in dates]
    sma200d = sum(closes[-200:]) / 200.0
    # Weekly closes (Sunday UTC closes) for 200-week SMA
    sundays = [rows[d][2] for d in dates if dt.date.fromisoformat(d).weekday() == 6]
    sma200w = sum(sundays[-200:]) / 200.0

    sep_low_d, sep_low = min(
        ((d, rows[d][1]) for d in dates if d.startswith("2026-09")), key=lambda x: x[1]
    )
    oct_low_d, oct_low = min(
        ((d, rows[d][1]) for d in dates if d.startswith("2026-10")), key=lambda x: x[1]
    )
    nov_low_d, nov_low = min(
        ((d, rows[d][1]) for d in dates if d.startswith("2026-11")), key=lambda x: x[1]
    )
    return {
        "last_date": dates[-1],
        "last_close": closes[-1],
        "sep_low_date": sep_low_d,
        "sep_low": sep_low,
        "oct_low_date": oct_low_d,
        "oct_low": oct_low,
        "nov_low_date": nov_low_d,
        "nov_low": nov_low,
        "nov_6_close": rows["2026-11-06"][2],
        "sma200d": round(sma200d, 2),
        "sma200w": round(sma200w, 2),
        "target_10pct_from_74888": round(nov_low * 0.90, 2),
        "target_106pct_from_74888": round(nov_low * (1.0 - 0.106), 2),
        "target_10pct_from_oct_low": round(oct_low * 0.90, 2),
        "target_106pct_from_oct_low": round(oct_low * (1.0 - 0.106), 2),
    }


def run_all(fetch_recent=True):
    rows = load_daily(fetch_recent=fetch_recent)
    ctx = current_context(rows)
    m_188_total, m_188_ev = monthly_low_breaks(rows, "2011-02", "2026-10")
    m_185_total, m_185_ev = monthly_low_breaks(rows, "2011-05", "2026-09")
    m_bn_total, m_bn_ev = monthly_low_breaks(rows, "2017-09", "2026-10")

    nday_results = {}
    for n in (14, 20, 30, 50):
        for f in (7, 14, 30):
            nday_results[f"N{n}_F{f}"] = rolling_nday_breaks(rows, n, f)

    fractal_results = {}
    for k in (5, 7, 10):
        for f in (7, 14, 30):
            fractal_results[f"k{k}_F{f}"] = fractal_swing_breaks(rows, k, f)

    return {
        "context": ctx,
        "monthly_188": summarize_monthly(m_188_total, m_188_ev),
        "monthly_185_krown63": summarize_monthly(m_185_total, m_185_ev),
        "monthly_binance": summarize_monthly(m_bn_total, m_bn_ev),
        "nday": nday_results,
        "fractal": fractal_results,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true", help="Do not top up from Binance REST")
    args = ap.parse_args()
    res = run_all(fetch_recent=not args.offline)
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
