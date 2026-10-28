"""lab_verify_rsi4060_bb_15m_2026-10-28: independent Sonnet/Claude-derived read (NOT a DeepSeek/DSA
cross-check) of the operator's 2026-10-26 live teaching rule. See REPORT.md for the write-up; this
script computes everything in it from klines_15m.csv (fetch.py), independently (no borrowed numbers).

Rule (frozen before DEV is touched, from the task card's SOURCED+OURS note -- not tuned by this pass):
  RSI(14) Wilder, BB(20, 2) on close, trend filter = close > SMA200 (15m).
  LONG event: RSI breaks under 40 for 1-3 consecutive bars ("broke 40"), and during that break run the
    bar low touches <= lower band at least once ("tags band"), and RSI closes back >= 40 on the bar
    right after the run ends ("returns, takes support on 40"). Entry = open of the bar after the
    RSI-recovery bar. Trend filter checked on the recovery bar.
  SHORT (mirror, OURS interpretation of "the mirror at RSI 60 and the upper band"): downtrend
    (close < SMA200), RSI pops over 60 for 1-3 bars, high touches >= upper band during the pop, RSI
    closes back <= 60 on the bar after. Entry = open of the bar after.
  Cost: 0.2% round trip (OURS, as given in the done_when), net = gross - 0.2 (long), net = -gross - 0.2 (short).
  Horizons: 4, 8, 16 bars forward from entry.

DEV/VALIDATION split: chronological 70/30 by bar index, split line fixed BEFORE any event is computed or
viewed. The frozen rule above was written on the card before this script ran, so there is no HOLDOUT
peeking: DEV is used to report the primary result, VALIDATION is touched exactly once, after, to confirm.
Trial count: 1 (this single frozen specification; no parameter search was run by this pass).
"""
import csv
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
IN = os.path.join(HERE, "klines_15m.csv")
FEE_RT = 0.2  # % round trip, OURS (as given in the task done_when)
HORIZONS = (4, 8, 16)
RSI_N = 14
BB_N = 20
BB_K = 2
SMA_N = 200
DEV_FRAC = 0.70


def load():
    rows = []
    with open(IN, newline="") as f:
        rd = csv.reader(f)
        next(rd)
        for r in rd:
            rows.append((int(r[0]), float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5])))
    rows.sort()
    return rows


def rsi_wilder(closes, n=RSI_N):
    out = [None] * len(closes)
    if len(closes) <= n:
        return out
    gains = losses = 0.0
    for i in range(1, n + 1):
        d = closes[i] - closes[i - 1]
        gains += max(d, 0.0)
        losses += max(-d, 0.0)
    avg_g, avg_l = gains / n, losses / n
    out[n] = 100.0 if avg_l == 0 else 100 - 100 / (1 + avg_g / avg_l)
    for i in range(n + 1, len(closes)):
        d = closes[i] - closes[i - 1]
        g, l = max(d, 0.0), max(-d, 0.0)
        avg_g = (avg_g * (n - 1) + g) / n
        avg_l = (avg_l * (n - 1) + l) / n
        out[i] = 100.0 if avg_l == 0 else 100 - 100 / (1 + avg_g / avg_l)
    return out


def bollinger(closes, n=BB_N, k=BB_K):
    mid = [None] * len(closes)
    up = [None] * len(closes)
    lo = [None] * len(closes)
    for i in range(n - 1, len(closes)):
        w = closes[i - n + 1:i + 1]
        m = sum(w) / n
        var = sum((x - m) ** 2 for x in w) / n
        sd = math.sqrt(var)
        mid[i], up[i], lo[i] = m, m + k * sd, m - k * sd
    return mid, up, lo


def sma(closes, n=SMA_N):
    out = [None] * len(closes)
    for i in range(n - 1, len(closes)):
        out[i] = sum(closes[i - n + 1:i + 1]) / n
    return out


def find_events(rows, rsi, bb_up, bb_lo, sma200, side, lo_bound, hi_bound):
    """side='long': break under 40 then recover >=40, uptrend, tag lower band.
    side='short': break over 60 then recover <=60, downtrend, tag upper band."""
    n = len(rows)
    events = []
    i = SMA_N  # need SMA200 warm
    while i < n:
        r = rsi[i]
        if r is None or sma200[i] is None:
            i += 1
            continue
        if side == "long":
            breaking = r < 40
        else:
            breaking = r > 60
        if breaking:
            j = i
            while j + 1 < n and ((rsi[j + 1] < 40) if side == "long" else (rsi[j + 1] > 60)):
                j += 1
            run_len = j - i + 1
            if run_len <= 3 and j + 1 < n:
                rec = rsi[j + 1]
                recovered = (rec is not None and rec >= 40) if side == "long" else (rec is not None and rec <= 60)
                if recovered:
                    band_touch = False
                    for b in range(i, j + 1):
                        if side == "long" and bb_lo[b] is not None and rows[b][3] <= bb_lo[b]:
                            band_touch = True
                        if side == "short" and bb_up[b] is not None and rows[b][2] >= bb_up[b]:
                            band_touch = True
                    trend_ok = (rows[j + 1][4] > sma200[j + 1]) if side == "long" else (rows[j + 1][4] < sma200[j + 1])
                    if band_touch and trend_ok and j + 2 < n:
                        events.append({"break_i": i, "run_len": run_len, "recover_i": j + 1, "entry_i": j + 2})
                i = j + 2
                continue
            i = j + 1
            continue
        i += 1
    return events


def fwd_returns(rows, entry_i, side):
    out = {}
    n = len(rows)
    entry_px = rows[entry_i][1]  # open of entry bar
    for h in HORIZONS:
        k = entry_i + h - 1  # close of bar h-1 after entry bar (entry bar counts as bar 1 held)
        if k >= n:
            out[h] = None
            continue
        exit_px = rows[k][4]
        gross = (exit_px / entry_px - 1) * 100 if side == "long" else (1 - exit_px / entry_px) * 100
        out[h] = gross
    return out


def mean(xs):
    return sum(xs) / len(xs) if xs else float("nan")


def sd(xs):
    if len(xs) < 2:
        return float("nan")
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def tstat_vs(xs, mu0=0.0):
    n = len(xs)
    if n < 2:
        return float("nan"), float("nan")
    s = sd(xs)
    se = s / math.sqrt(n)
    t = (mean(xs) - mu0) / se if se > 0 else float("nan")
    return t, se


def unconditional_baseline(rows, side, start, end):
    """mean forward return over ALL bars in [start,end) regardless of rule, same horizons."""
    out = {h: [] for h in HORIZONS}
    n = len(rows)
    for i in range(start, end):
        entry_px = rows[i][1]
        for h in HORIZONS:
            k = i + h - 1
            if k >= n or k >= end:
                continue
            exit_px = rows[k][4]
            gross = (exit_px / entry_px - 1) * 100 if side == "long" else (1 - exit_px / entry_px) * 100
            out[h].append(gross)
    return out


def run_segment(rows, rsi, bb_up, bb_lo, sma200, start, end, label):
    lines = [f"### {label} (bars [{start}:{end}), n_bars={end-start})"]
    all_rows = {}
    for side in ("long", "short"):
        evs = [e for e in find_events(rows, rsi, bb_up, bb_lo, sma200, side, start, end)
               if start <= e["entry_i"] < end]
        recs = []
        for e in evs:
            fr = fwd_returns(rows, e["entry_i"], side)
            if all(fr[h] is not None for h in HORIZONS):
                recs.append(fr)
        lines.append(f"\n**{side.upper()} events: {len(evs)} found, {len(recs)} with full forward window**\n")
        lines.append("| h (bars) | n | gross mean % | gross t-stat | fee-net mean % (0.2% RT) | fee-net t-stat | unconditional baseline mean % |")
        lines.append("|---|---|---|---|---|---|---|")
        base = unconditional_baseline(rows, side, start, end)
        for h in HORIZONS:
            vals = [r[h] for r in recs]
            t, se = tstat_vs(vals)
            net = [v - FEE_RT for v in vals]
            tn, sen = tstat_vs(net)
            b = base[h]
            lines.append(f"| {h} | {len(vals)} | {mean(vals):.4f} | {t:.2f} | {mean(net):.4f} | {tn:.2f} | {mean(b):.4f} |")
        all_rows[side] = (evs, recs)
    return "\n".join(lines), all_rows


def main():
    rows = load()
    closes = [r[4] for r in rows]
    rsi = rsi_wilder(closes)
    _, bb_up, bb_lo = bollinger(closes)
    sma200 = sma(closes)
    n = len(rows)
    split = int(n * DEV_FRAC)
    import datetime as dt
    def iso(ms):
        return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    print(f"total bars {n}, {iso(rows[0][0])} .. {iso(rows[-1][0])}")
    print(f"DEV [0:{split}) {iso(rows[0][0])}..{iso(rows[split-1][0])}; VALIDATION [{split}:{n}) {iso(rows[split][0])}..{iso(rows[-1][0])}")

    dev_txt, dev_rows = run_segment(rows, rsi, bb_up, bb_lo, sma200, 0, split, "DEV")
    val_txt, val_rows = run_segment(rows, rsi, bb_up, bb_lo, sma200, split, n, "VALIDATION (confirmation run, touched once)")

    out = [dev_txt, "", val_txt]
    with open(os.path.join(HERE, "RESULT.md"), "w", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
