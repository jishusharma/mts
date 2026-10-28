"""lab-verify-mtf-bias-ladder: grandfather/father/son MTF bias ladder + Malkan RSI 40-60 zone, fee-net, BTCUSDT.

Independent Sonnet/Claude-derived read (Lab_Analyst standing in for the closed DeepSeek/DSA bridge).
This is NOT a second-vendor (DeepSeek) cross-check of an existing DSA result -- there was no prior
DSA number on this card to cross-check. All numbers below are computed fresh from real Binance
spot klines by this session, per CLAUDE.md "fee-net out-of-sample results decide what trades".

Public read-only data: data-api.binance.vision (no key). Observation only, no live-path / order code.
"""
import json
import math
import time
import urllib.request
import datetime as dt
import statistics as st

UA = {"User-Agent": "Mozilla/5.0"}
BASE = "https://data-api.binance.vision/api/v3/klines"
OUT_DIR = "MyTradingSys/research/live_reads/2026-10-28_lab_verify_mtf_bias_ladder"

# DECISION (OURS): bound how far back we pull for the EXPENSIVE lower timeframes (1h, 15m) to keep
# this single run inside the session's tool-turn / wall-clock budget. The higher timeframes that
# define the ladder (1w/3d/1d/12h SOURCED Binance intervals; 5d/2d OURS aggregates of 1d) are pulled
# from genesis (as many years as the API gives, per the task brief) since those calls are cheap.
GENESIS = dt.datetime(2017, 8, 17, tzinfo=dt.timezone.utc)
LOWER_TF_START = dt.datetime(2022, 1, 1, tzinfo=dt.timezone.utc)  # DECISION (OURS): runtime cap for 1h/15m pulls
NOW = dt.datetime.now(dt.timezone.utc)

FEE_ROUND_TRIP = 0.002  # SOURCED: given directly in the task's DONE-when ("after 0.2% round-trip fee")
RSI_N = 14  # SOURCED: standard Wilder RSI length, matches existing registry script mtf_bias.py


def ms(d):
    return int(d.timestamp() * 1000)


def fetch_range(interval, start, end, pause=0.08):
    """Paginate klines [start, end) at 1000/bar limit. Returns list of raw kline rows."""
    out = []
    cur = ms(start)
    end_ms = ms(end)
    stall = 0
    while cur < end_ms:
        url = f"{BASE}?symbol=BTCUSDT&interval={interval}&startTime={cur}&limit=1000"
        for attempt in range(4):
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
                    batch = json.load(r)
                break
            except Exception as e:
                time.sleep(0.5 * (attempt + 1))
                batch = None
        if not batch:
            stall += 1
            if stall > 3:
                break
            cur += 1
            continue
        stall = 0
        out.extend(batch)
        last_open = batch[-1][0]
        if last_open <= cur and len(batch) < 2:
            break
        cur = last_open + 1
        if len(batch) < 2:
            break
        time.sleep(pause)
    # dedupe by open time, keep sorted
    seen = {}
    for row in out:
        seen[row[0]] = row
    return [seen[k] for k in sorted(seen)]


def to_ohlc(rows):
    return [(r[0], float(r[1]), float(r[2]), float(r[3]), float(r[4]), r[6]) for r in rows]
    # open_time, O, H, L, C, close_time


def agg_from_1d(d1, n):
    """OURS: build an n-day bucket from 1d candles, buckets anchored to the END (today's partial bucket
    is dropped so every bucket used downstream is closed)."""
    out = []
    i = len(d1)
    while i - n >= 0:
        chunk = d1[i - n:i]
        o = chunk[0][1]
        h = max(x[2] for x in chunk)
        l = min(x[3] for x in chunk)
        c = chunk[-1][4]
        out.append((chunk[0][0], o, h, l, c, chunk[-1][5]))
        i -= n
    return out[::-1]


def rsi_series(closes, n=RSI_N):
    """Closed-candle Wilder RSI, index i depends only on closes[0..i] -- no look-ahead."""
    if len(closes) < n + 1:
        return [None] * len(closes)
    out = [None] * n
    gains = [max(closes[i] - closes[i - 1], 0) for i in range(1, len(closes))]
    losses = [max(closes[i - 1] - closes[i], 0) for i in range(1, len(closes))]
    ag = sum(gains[:n]) / n
    al = sum(losses[:n]) / n
    out.append(100 - 100 / (1 + ag / al) if al else 100.0)
    for i in range(n, len(gains)):
        ag = (ag * (n - 1) + gains[i]) / n
        al = (al * (n - 1) + losses[i]) / n
        out.append(100 - 100 / (1 + ag / al) if al else 100.0)
    return out


def build_tf_state(ohlc):
    """Per-bar: (close_time_ms, color 'G'/'R', rsi_zone bool-in-40-60) using ONLY that bar's own
    closed data (bar i's rsi uses closes[0..i]); no peeking at the bar that is still forming."""
    closes = [x[4] for x in ohlc]
    opens = [x[1] for x in ohlc]
    close_times = [x[5] for x in ohlc]
    rsis = rsi_series(closes)
    states = []
    for i in range(len(ohlc)):
        color = "G" if closes[i] > opens[i] else "R"
        zone = (rsis[i] is not None) and (40.0 <= rsis[i] <= 60.0)
        states.append((close_times[i], color, zone))
    return states


def asof_state(states, t_ms):
    """Last higher-TF state whose close_time < t_ms (strictly closed before the lower bar opened).
    states sorted by close_time ascending. Linear-scan with cached pointer is fine at this scale,
    but we binary-search since 15m bars are numerous."""
    lo, hi = 0, len(states)
    while lo < hi:
        mid = (lo + hi) // 2
        if states[mid][0] < t_ms:
            lo = mid + 1
        else:
            hi = mid
    idx = lo - 1
    return states[idx] if idx >= 0 else None


def ladder_bucket(green_count, zone_count, total=6):
    if green_count <= 2:
        gb = "mostly-RED"
    elif green_count >= total - 2:
        gb = "mostly-GREEN"
    else:
        gb = "mixed"
    zb = "RSI-few-40-60" if zone_count <= total // 2 else "RSI-many-40-60"
    return f"{gb} / {zb}"


def mean_std(xs):
    n = len(xs)
    if n == 0:
        return 0.0, 0.0, 0
    m = sum(xs) / n
    if n < 2:
        return m, 0.0, n
    v = sum((x - m) ** 2 for x in xs) / (n - 1)
    return m, math.sqrt(v), n


def welch_t(xs, ys):
    mx, sx, nx = mean_std(xs)
    my, sy, ny = mean_std(ys)
    if nx < 2 or ny < 2:
        return float("nan"), float("nan")
    se = math.sqrt((sx ** 2) / nx + (sy ** 2) / ny)
    if se == 0:
        return 0.0, mx - my
    t = (mx - my) / se
    return t, mx - my


def fwd_returns(ohlc, horizons=(4, 8, 16)):
    """For each closed bar i (entry at close[i]), forward return to close[i+h]. Returns dict
    h -> list aligned with bar index i (None where未 out of range)."""
    closes = [x[4] for x in ohlc]
    n = len(closes)
    out = {h: [None] * n for h in horizons}
    for h in horizons:
        for i in range(n - h):
            out[h][i] = closes[i + h] / closes[i] - 1.0
    return out


def main():
    log = []

    def dec(msg):
        log.append(msg)
        print(msg)

    dec(f"run start {dt.datetime.now(dt.timezone.utc):%Y-%m-%dT%H:%MZ}")

    # --- higher-TF ladder data: SOURCED exchange intervals, genesis -> now ---
    dec("fetching 1w/3d/1d/12h from genesis (SOURCED exchange intervals)...")
    w1 = to_ohlc(fetch_range("1w", GENESIS, NOW))
    d3 = to_ohlc(fetch_range("3d", GENESIS, NOW))
    d1 = to_ohlc(fetch_range("1d", GENESIS, NOW))
    h12 = to_ohlc(fetch_range("12h", GENESIS, NOW))
    dec(f"  1w={len(w1)} bars, 3d={len(d3)} bars, 1d={len(d1)} bars, 12h={len(h12)} bars")

    # OURS aggregates from 1d
    d5 = agg_from_1d(d1, 5)
    d2 = agg_from_1d(d1, 2)
    dec(f"  5d*(OURS)={len(d5)} buckets, 2d*(OURS)={len(d2)} buckets")

    ladder_tfs = [("1w", w1), ("5d*", d5), ("3d", d3), ("2d*", d2), ("1d", d1), ("12h", h12)]
    ladder_states = {name: build_tf_state(ohlc) for name, ohlc in ladder_tfs}

    # --- lower-TF data for the forward-return test: DECISION(OURS) bounded window ---
    dec(f"fetching 1h/15m from {LOWER_TF_START:%Y-%m-%d} (DECISION OURS: runtime cap) -> now ...")
    h1 = to_ohlc(fetch_range("1h", LOWER_TF_START, NOW))
    m15 = to_ohlc(fetch_range("15m", LOWER_TF_START, NOW))
    dec(f"  1h={len(h1)} bars, 15m={len(m15)} bars")

    results = {}  # (lower_tf) -> list of per-bar dict
    trial_ledger_rows = []

    for lower_name, lower_ohlc in (("1h", h1), ("15m", m15)):
        fr = fwd_returns(lower_ohlc, (4, 8, 16))
        n = len(lower_ohlc)
        rows = []
        for i in range(n):
            t_open = lower_ohlc[i][0]
            green = 0
            zone = 0
            ok = True
            for name, states in ladder_states.items():
                s = asof_state(states, t_open)
                if s is None:
                    ok = False
                    break
                if s[1] == "G":
                    green += 1
                if s[2]:
                    zone += 1
            if not ok:
                continue
            bucket = ladder_bucket(green, zone)
            rows.append({"i": i, "t": t_open, "green": green, "zone": zone, "bucket": bucket,
                         "r4": fr[4][i], "r8": fr[8][i], "r16": fr[16][i]})
        results[lower_name] = rows

    # --- DEV / VALIDATION split (time-based, 70/30), on the bounded lower-TF window ---
    all_times = sorted(set(r["t"] for rows in results.values() for r in rows))
    t0, t1 = all_times[0], all_times[-1]
    cutoff = t0 + int(0.7 * (t1 - t0))
    dev_lo = dt.datetime.fromtimestamp(t0 / 1000, dt.timezone.utc)
    dev_hi = dt.datetime.fromtimestamp(cutoff / 1000, dt.timezone.utc)
    val_hi = dt.datetime.fromtimestamp(t1 / 1000, dt.timezone.utc)
    dec(f"DEV window: {dev_lo:%Y-%m-%d} -> {dev_hi:%Y-%m-%d}  |  VALIDATION window: {dev_hi:%Y-%m-%d} -> {val_hi:%Y-%m-%d}")

    # ONE pre-specified design: bucket scheme + horizons fixed above before looking at any split's
    # numbers -> trial_count = 1 (no binning search / no pick-the-best-horizon across the two splits).
    trial_ledger_rows.append({
        "trial": 1,
        "design": "ladder_bucket(green<=2 mostly-RED / 3-3 mixed / >=4 mostly-GREEN) x (zone<=3 few / >3 many), "
                  "horizons 4/8/16 bars, lower_tf in {1h,15m}, fee 0.2% round trip",
        "pre_specified": True,
        "note": "single design, computed on DEV then VALIDATION once; no search over alternative bucket edges or horizons",
    })

    report_lines = []
    report_lines.append("# lab-verify-mtf-bias-ladder -- fee-net MTF bias ladder + Malkan RSI 40-60 zone (BTCUSDT)\n")
    report_lines.append("**Author**: Lab_Analyst (Sonnet/Claude), standing in for the DeepSeek/DSA bridge, which "
                         "the operator is holding closed. This is an independent Sonnet-derived read computed "
                         "fresh from real klines; it is **not** a second-vendor cross-check of a prior DeepSeek "
                         "number (no DSA number exists yet on this card).\n")
    report_lines.append("## Parameters (labelled)\n")
    report_lines.append("- Ladder timeframes (grandfather->father->son), higher side: 1w, 5d*, 3d, 2d*, 1d, 12h "
                         "(SOURCED exchange intervals: 1w/3d/1d/12h; OURS aggregates built from 1d closes: 5d*, 2d*)")
    report_lines.append("- Lower / tradable timeframes tested: 1h, 15m (SOURCED exchange intervals)")
    report_lines.append(f"- RSI length: {RSI_N} (SOURCED, standard Wilder RSI, matches registry script mtf_bias.py); "
                         "40-60 zone threshold is SOURCED from the operator's brief (Malkan 40-60 state), not re-derived here")
    report_lines.append(f"- Fee: {FEE_ROUND_TRIP*100:.2f}% round trip (SOURCED, given directly in the task's DONE-when)")
    report_lines.append(f"- Higher-TF history: genesis {GENESIS:%Y-%m-%d} -> {NOW:%Y-%m-%d} (as many years as the API gives)")
    report_lines.append(f"- Lower-TF (1h/15m) history: {LOWER_TF_START:%Y-%m-%d} -> {NOW:%Y-%m-%d} "
                         "(DECISION OURS: bounded to keep this single run inside the session's time budget; "
                         "full history for 1w/3d/1d/12h/5d*/2d* was pulled, the cap only applies to the two "
                         "expensive lower timeframes used for the forward-return test)")
    report_lines.append(f"- Bucket scheme and horizons were fixed BEFORE looking at DEV or VALIDATION numbers "
                         "(trial_count = 1, see trial_ledger.csv) -- no search over alternative bucket edges")
    report_lines.append("")

    baseline_cache = {}

    def split_rows(rows, lo, hi):
        return [r for r in rows if lo <= r["t"] < hi]

    for split_name, lo, hi in (("DEV", t0, cutoff), ("VALIDATION", cutoff, t1 + 1)):
        report_lines.append(f"## {split_name} ({dt.datetime.fromtimestamp(lo/1000, dt.timezone.utc):%Y-%m-%d} -> "
                             f"{dt.datetime.fromtimestamp(min(hi, t1)/1000, dt.timezone.utc):%Y-%m-%d})\n")
        for lower_name in ("1h", "15m"):
            rows = split_rows(results[lower_name], lo, hi)
            if not rows:
                report_lines.append(f"### {lower_name}: no rows in split\n")
                continue
            buckets = sorted(set(r["bucket"] for r in rows))
            baseline = {h: [r[f"r{h}"] for r in rows if r[f"r{h}"] is not None] for h in (4, 8, 16)}
            base_mean = {h: (sum(v) / len(v) if v else float("nan")) for h, v in baseline.items()}
            n_base = {h: len(v) for h, v in baseline.items()}
            report_lines.append(f"### {lower_name} -- n={len(rows)} bars, {len(buckets)} ladder states\n")
            report_lines.append("| ladder state | n | horizon | gross fwd ret (mean) | fee-net fwd ret | baseline (unconditional) | fee-net edge vs baseline | t-stat (Welch, vs complement) |")
            report_lines.append("|---|---|---|---|---|---|---|---|")
            for b in buckets:
                sub = [r for r in rows if r["bucket"] == b]
                comp = [r for r in rows if r["bucket"] != b]
                for h in (4, 8, 16):
                    xs = [r[f"r{h}"] for r in sub if r[f"r{h}"] is not None]
                    ys = [r[f"r{h}"] for r in comp if r[f"r{h}"] is not None]
                    if not xs:
                        continue
                    gm = sum(xs) / len(xs)
                    net = gm - FEE_ROUND_TRIP
                    bnet = base_mean[h] - FEE_ROUND_TRIP
                    t, diff = welch_t(xs, ys)
                    report_lines.append(
                        f"| {b} | {len(xs)} | {h} | {gm*100:+.3f}% | {net*100:+.3f}% | {base_mean[h]*100:+.3f}% (net {bnet*100:+.3f}%) | {(net-bnet)*100:+.3f}% | {t:+.2f} |"
                    )
            report_lines.append("")

    # --- verdict: judged ONLY on VALIDATION fee-net edge + significance, DEV used only to pick the design ---
    verdict_rows = []
    for lower_name in ("1h", "15m"):
        rows = split_rows(results[lower_name], cutoff, t1 + 1)
        if not rows:
            continue
        buckets = sorted(set(r["bucket"] for r in rows))
        for b in buckets:
            sub = [r for r in rows if r["bucket"] == b]
            comp = [r for r in rows if r["bucket"] != b]
            for h in (4, 8, 16):
                xs = [r[f"r{h}"] for r in sub if r[f"r{h}"] is not None]
                ys = [r[f"r{h}"] for r in comp if r[f"r{h}"] is not None]
                if len(xs) < 30:
                    continue
                gm = sum(xs) / len(xs)
                net = gm - FEE_ROUND_TRIP
                t, diff = welch_t(xs, ys)
                verdict_rows.append((lower_name, b, h, len(xs), net, t))

    worth = [r for r in verdict_rows if r[4] > 0 and abs(r[5]) >= 1.96]
    report_lines.append("## Verdict\n")
    if worth:
        report_lines.append(f"**WORTH-A-LAYER-CANDIDATE (tentative)**: {len(worth)} / {len(verdict_rows)} "
                             "VALIDATION (ladder-state, horizon, timeframe) cells clear fee-net-positive at "
                             "|t|>=1.96, n>=30. Needs a dedicated layer card with its own pre-registered design "
                             "and a fresh OOS slice before it trades anything -- this card is observation only.")
        for r in worth:
            report_lines.append(f"  - {r[0]} / {r[1]} / {r[2]}-bar: n={r[3]}, fee-net={r[4]*100:+.3f}%, t={r[5]:+.2f}")
    else:
        report_lines.append(f"**NOT WORTH A LAYER on this read**: 0 / {len(verdict_rows)} VALIDATION cells with "
                             "n>=30 clear both fee-net-positive AND |t|>=1.96. The ladder state (grandfather/"
                             "father/son higher-TF bias count, crossed with Malkan 40-60 RSI zone count) does not "
                             "show a reliable fee-net edge over the unconditional baseline on 1h/15m BTCUSDT "
                             "forward returns in the VALIDATION window. Close the card; do not open a layer card "
                             "from this result alone.")
    report_lines.append("")
    report_lines.append(f"Trial count: 1 pre-specified design (see trial_ledger.csv); DEV used only to sanity-check "
                         "the pipeline runs and produces non-degenerate bucket counts, not to pick thresholds; "
                         "verdict above is judged on VALIDATION only.")
    report_lines.append("")
    report_lines.append("## Run log\n")
    report_lines.append("```")
    report_lines.extend(log)
    report_lines.append("```")

    with open(f"{OUT_DIR}/REPORT.md", "w", newline="\n", encoding="utf-8") as f:
        f.write("\n".join(report_lines) + "\n")

    with open(f"{OUT_DIR}/trial_ledger.csv", "w", newline="\n", encoding="utf-8") as f:
        f.write("trial,design,pre_specified,note\n")
        for r in trial_ledger_rows:
            f.write(f"{r['trial']},\"{r['design']}\",{r['pre_specified']},\"{r['note']}\"\n")

    dec("wrote REPORT.md and trial_ledger.csv")


if __name__ == "__main__":
    main()
