"""T10: build matrix.csv (failure mode x brief-1b study x testnet layer) and matrix_summary.csv.
Stdlib only. Rules are written by hand from the evidence named in each cell; a cell with no verified evidence is UNKNOWN.
Run from the worktree root: python MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T10/t10_build_matrix.py"""
import csv, os
HERE = os.path.dirname(os.path.abspath(__file__))
H, NH, NA, UK = "HANDLED", "NOT HANDLED", "N/A", "UNKNOWN"

STUDIES = [
 "S01 session_extreme_fade", "S02 preopen_tops", "S03 mal_bb_mid_engulf", "S04 bb_mtf_center",
 "S05 weekly_low_round_sweep", "S06 wlow_bounce_bbrsi60", "S07 krown_malkan_counts", "S08 qriptal_calls",
 "S09 candle_close", "S10 levels_sizing", "S11 level_hold_lc1", "S12 orderflow_views",
 "S13 eur_low_us_sweep", "S14 mfe_exits", "S15 published_strats", "S16 tom_fabio_matrix"]
LAYERS = ['rsi|rsi_events|1h', 'rsi|rsi_events|15m', 'rsi|rsi_events|5m', 'fabio|cvd_absorption|1h', 'fabio|cvd_absorption|15m',
 'fabio|escalation|1h', 'fabio|volume_fvg|1h', 'session|session_momentum|15m', 'positioning|funding_cvd_fade|1h',
 'rsi|malkan_bull|1h', 'rsi|malkan_bear|1h', 'cryptocred|sr_flip|1h', 'cryptocred|fib_pullback|1h', 'cryptocred|failed_msb|1h',
 'turn_of_candle|turn_of_candle|1m', 'fabio|escalation|15m', 'fabio|volume_fvg|15m', 'cryptocred|sr_flip|15m',
 'cryptocred|fib_pullback|15m', 'cryptocred|failed_msb|15m', 'fabio|v3_grid|1m', 'wlow_bounce|bbrsi60|1h',
 'rsi_divergence|rsi_divergence|1h', 'bb_top_reversal|bb_top_reversal|15m', 'session_levels|session_levels|1m',
 'candle_close|candle_close|1m', 'levels|confluence|1m']
COLS = STUDIES + ["L " + x for x in LAYERS]
T02_UNDEC = {'wlow_bounce|bbrsi60|1h', 'session_levels|session_levels|1m', 'fabio|v3_grid|1m',
             'positioning|funding_cvd_fade|1h', 'rsi|malkan_bull|1h'}
YEAR_HOUR_USERS = {"S02", "S04", "S05", "S12", "S13"}  # study.py greps .year / .hour / weekday: stratification not verified
SCREEN_FAMILY = {"S01", "S02", "S03", "S04", "S05", "S06"}
NO_PNL = {"S07", "S08", "S11"}  # counts, n=0 scored, hold rates: no simulated P&L

# id, category, name, how it shows, test, source, covered_by
MODES = [
 ("F01","data","Duplicate or missing bars","event counts and returns change after de-duplication","count unique open_time and gaps per loader","model knowledge","T01"),
 ("F02","data","Time unit mix (microseconds read as milliseconds)","bars land in year 50000 or are dropped","assert stamp range per file","model knowledge","T01"),
 ("F03","data","Trade-price bars used where mark/index price decides stops or liquidation","stop hit on a print the exchange would not use","rerun stop logic on mark bars","model knowledge","T03 (bt_engine mark bars), section 1e L5"),
 ("F04","data","Spot data standing in for perp data","basis and funding ignored; session volume differs","compare spot vs perp close on overlap","model knowledge","T01 L10"),
 ("F05","data","Single-instrument universe (BTC only): result may be an instrument accident","no cross-asset check; edge vanishes on ETH","rerun the frozen rule on ETHUSDT DEV","https://www.columbia.edu/~nyc2107/papers/seven_sins_of_quantitative_investing.pdf","NONE"),
 ("F06","data","Point-in-time errors: OI, depth, funding or revised data used before it was published","signal uses a field stamped earlier than it was knowable","check publish lag of each derived column","https://arxiv.org/html/2512.22476v1","T02 partly (bar stamps)"),
 ("F07","data","Bad prints and flash wicks drive extremes","extreme-based signals fire on one-tick wicks","re-run with wicks > k ATR clipped","model knowledge","NONE"),
 ("F08","data","Data venue differs from trading venue (Binance bars, Deribit fills)","backtest on one venue, trade on another","compare bar close Binance vs Deribit on the same minutes","model knowledge","section 2 G8 (Deribit parity)"),
 ("T01","time","Look-ahead through resample labels, centred windows or pivot confirmation","signals differ when the future is cut off","truncation and poison test","https://arxiv.org/html/2512.22476v1","T02"),
 ("T02","time","Session clocks without DST or with fixed UTC","US open label shifts one hour for half the year","count events whose label flips under DST rule","model knowledge","T02 L6"),
 ("T03","time","Funding settlement window and sign mishandled","funding charged on wrong side or boundary","planted funding canary","https://arxiv.org/html/2512.22476v1","T03, T06 L1"),
 ("T04","time","Signal-to-fill latency: fill at the signal bar close","result worsens with a 1-2 bar delay","rerun with next-open and +1 bar fills (D1)","https://arxiv.org/html/2512.22476v1","section 2 partly; demonstrated here D1"),
 ("T05","time","Weekend and holiday liquidity seasonality ignored","edge lives only in thin hours","split events by hour/weekday; count per cell","model knowledge","NONE"),
 ("T06","time","Higher-timeframe join keyed on bar open","daily/weekly level known before it closed","merge_asof direction audit","model knowledge","T02"),
 ("C01","costs/fills","Flat cost where spread and slippage scale with volatility","cost under-charged in fast minutes","vol-scaled slippage rerun (D5)","https://www.binance.com/en/academy/articles/what-is-backtesting","section 2 G7 partly; demonstrated D5"),
 ("C02","costs/fills","Maker orders filled on touch","fill rate and adverse selection overstated","require trade-through by k ticks","model knowledge","section 2 G4 (through_ticks flag)"),
 ("C03","costs/fills","Gap through the stop booked at the stop price","stop loss smaller than live","book stop at next open when gapped","model knowledge","section 2 N2/G7, T03"),
 ("C04","costs/fills","Funding charged flat or on the wrong side","shorts pay where they receive","real per-settlement funding","https://arxiv.org/html/2512.22476v1","T06 L1, T03"),
 ("C05","costs/fills","Intrabar order ambiguity: stop and target both inside one bar","optimistic ordering inflates win rate","count bars where both are reachable (D2)","model knowledge","T03 convention only; demonstrated D2"),
 ("C06","costs/fills","Market impact and queue position ignored","size larger than top-of-book depth","compare clip size to bookDepth","model knowledge","NONE"),
 ("C07","costs/fills","Tick size, lot size and minimum notional ignored","orders rejected or rounded live","round to instrument grid","model knowledge","NONE (grep tick_size in backtest: 0 hits)"),
 ("C08","costs/fills","Fee tier, maker rebate and venue fee mismatch","net sign depends on 2 bp","single fee module","model knowledge","T06 L3, section 1a fees.py"),
 ("C09","costs/fills","Liquidation, margin and auto-deleveraging not simulated","leveraged path ends early live","simulate maintenance margin on worst bars","model knowledge","NONE (grep liquidat in backtest: 1 unrelated hit)"),
 ("S01","statistics","Multiple testing across arms, horizons and variants (family-wise error)","some arm passes by chance (D3)","placebo null across K arms","https://www.cxoadvisory.com/big-ideas/seven-habits-of-highly-ineffective-quants/","T05 L7; section 2 E1/E4; demonstrated D3"),
 ("S02","statistics","Overlapping holds and autocorrelated events inflate n","naive SE too small","cluster or block bootstrap","model knowledge","T05 L7"),
 ("S03","statistics","Trial count not recorded (garden of forking paths)","DSR cannot be computed","trial ledger completeness","https://bookdown.org/palomar/portfoliooptimizationbook/8.2-seven-sins.html","section 2 E1, T08"),
 ("S04","statistics","Fat tails and skew break the t-test","t=2 on a handful of outliers","trimmed mean and bootstrap CI","https://mathinvestor.org/2014/04/faqs-on-backtest-overfitting/","NONE"),
 ("S05","statistics","Low power: MDE bigger than the effect asked about","INCONCLUSIVE read as no effect","report MDE next to every null","model knowledge","section 2 G1"),
 ("S06","statistics","Control group that contains the signal","DIFF vs control is biased to zero","control purity check","model knowledge","T05 L8"),
 ("S07","statistics","Out-of-sample reuse and split leakage","validation read twice","exposure ledger per read","https://www.columbia.edu/~nyc2107/papers/seven_sins_of_quantitative_investing.pdf","T08 L2"),
 ("R01","regime","Regime drift: a long-biased arm rides the trend","per-year mean flips sign (D4)","per-year and long/short split","model knowledge","NONE; demonstrated D4"),
 ("R02","regime","Structural breaks: listing, halving, ETF flows, fee-schedule changes","rule works before a date only","rolling-window stability by quarter","model knowledge","NONE"),
 ("R03","regime","Exchange outages and extreme days (e.g. 2022-11 FTX, 2023-03 USDC depeg)","a few days carry the P&L","drop the top-5 days and rerun","model knowledge","NONE"),
 ("R04","regime","Liquidation cascades make stops unfillable","fills far from stop in cascade minutes","stress the 20 worst minutes","model knowledge","section 2 G7 partly"),
 ("E01","selection","Storytelling: rule invented after seeing the chart","parameters tuned to anecdotes","pre-registration with SOURCED/OURS labels","https://www.columbia.edu/~nyc2107/papers/seven_sins_of_quantitative_investing.pdf","CLAUDE.md numbers rule; PRE_REG files"),
 ("E02","selection","Selecting the timeframe, symbol or window after looking","only the best cell is reported","count cells examined vs reported","https://gainium.io/blog/common-backtesting-problems","section 2 E2, T08"),
 ("I01","implementation","Backtest code and live code are different implementations","live fires on different bars","run backtest function on the live log","https://arxiv.org/html/2512.22476v1","T09 (missing); section 1c parity.py"),
 ("I02","implementation","Cost in percent but risk in R: cost in R-units ignored","stop 0.044% vs cost 0.14% = 3.2R","cost-in-R gate","model knowledge","section 2 E3"),
 ("I03","implementation","Duplicate loaders and split schemes (25+ loaders, 8 splits)","same study differs by loader","single-source import test","model knowledge","T01, T08"),
 ("O01","operations","Exit reason misclassified in the ledger","target exits are really stops","re-derive exit class from prices","model knowledge","section 2 LEDGER_EXIT_AUDIT"),
 ("O02","operations","Stale feed: writer behind klines","signals on old window","staleness guard","model knowledge","NONE verified"),
 ("O03","operations","Restart or state loss mid-trade","position unknown after crash","restart test with open position","model knowledge","CLAUDE.md live-path rule"),
 ("O04","operations","API errors and rate limits","orders dropped, retries double-send","fault-injection test","model knowledge","CLAUDE.md live-path rule"),
 ("O05","operations","Testnet fills are synthetic and thin","testnet P&L not a cost estimate","compare testnet slippage to mainnet book","model knowledge","section 2 G3"),
 ("O06","operations","Tests not in the CI gate","a regression ships green","gate coverage diff","model knowledge","T07 L9 (missing)"),
]


def kind(col):
    return col.split()[0] if col[0] == "S" else "L"


def cell(mid, col):
    k = kind(col)
    layer = col[2:] if k == "L" else None
    if mid == "F01":
        return (UK, "layers read live REST bars; no dedup test seen") if k == "L" else (UK, "")
    if mid == "F02":
        return (UK, "")
    if mid == "F03":
        if k == "L" or k in NO_PNL:
            return (NA, "signal-only or no P&L")
        return (UK, "")
    if mid == "F04":
        if k == "S07":
            return (NH, "krown_daily is spot (brief 1d, L10)")
        return (NA, "perp 1m data")
    if mid == "F05":
        return (NH, "BTCUSDT only; no ETH rerun found")
    if mid == "F06":
        if k == "S12":
            return (NH, "OI/depth only 2025-09+, outside DEV (brief 1d)")
        if layer in T02_UNDEC:
            return (UK, "T02 not decisive")
        return (UK, "")
    if mid == "F07":
        return (UK, "")
    if mid == "F08":
        return (NH, "Binance bars vs Deribit test fills; no tool compares (brief 1c)")
    if mid in ("T01", "T06"):
        if k == "L":
            if layer in T02_UNDEC:
                return (UK, "T02 table 3a: 0 events on synthetic bars")
            return (H, "T02_lookahead_time.md table 3a: truncation+poison PASS")
        if k == "S06":
            return (UK, "T02: detector NOT DECISIVE; DEV run BLOCKED-DATA")
        return (UK, "T02: study detectors BLOCKED-DATA on Lenovo")
    if mid == "T02":
        return (UK, "T02 clock table not DEV-complete") if k == "L" else (UK, "")
    if mid == "T03":
        if k in NO_PNL:
            return (NA, "no funding in the number")
        if k == "L":
            return (NA, "layer emits signals; carry sits in the executor")
        if k == "S14":
            return (H, "mfe_exit_study.py:12 funding actually paid")
        if k == "S01":
            return (NH, "screen.py:451 flat 1 bp, shorts mischarged (L1)")
        if k == "S15":
            return (UK, "brief 1b #15 charges funding; sign not verified")
        return (UK, "")
    if mid == "T04":
        if k in NO_PNL:
            return (NA, "no fill")
        if k == "L":
            return (NH, "execution/ records no decision price (brief 1c)")
        if k == "S06":
            return (H, "study.py:97-101 entry open[t+1] (T02 row 6)")
        return (UK, "")
    if mid in ("T05", "R01", "R02") and k in YEAR_HOUR_USERS:
        return (UK, "study.py uses .year/.hour/weekday; stratified result not verified")
    if mid == "T05":
        if k in NO_PNL - {"S11"}:
            return (NA, "no per-hour result")
        return (NH, "no hour/weekday stratification found") if k in SCREEN_FAMILY else (UK, "")
    if mid == "C01":
        if k in NO_PNL:
            return (NA, "no cost")
        if k == "L":
            return (NH, "no decision price vs fill record (brief 1c)")
        if k in SCREEN_FAMILY:
            return (NH, "screen.py:30 C_PCT=0.14 flat")
        return (NH, "flat per-study cost literal (brief 1a)")
    if mid == "C02":
        if k in NO_PNL:
            return (NA, "")
        if k == "S01":
            return (NH, "screen.py maker readout: fill on a 0.1 USDT trade-through, no queue")
        return (UK, "")
    if mid == "C03":
        if k in NO_PNL:
            return (NA, "")
        if k == "S12":
            return (NH, "orderflow_views books gap at stop price (N2, unfixed)")
        return (UK, "executor stop type not read") if k == "L" else (UK, "")
    if mid == "C04":
        if k in NO_PNL or k == "L":
            return (NA, "")
        if k == "S14":
            return (H, "mfe_exit_study.py:12")
        if k == "S01":
            return (NH, "screen.py:451 flat +1 bp both sides")
        return (UK, "")
    if mid == "C05":
        if k in NO_PNL:
            return (NA, "")
        if k == "L":
            return (NH, "no intrabar model; executor fills real")
        return (UK, "ambiguity rate on 1m bars 0.16-3.27% (D2); engine convention per T03")
    if mid == "C06":
        return (NA, "no P&L") if k in NO_PNL else (NH, "no size-vs-depth model; bookDepth only 2025-09+")
    if mid == "C07":
        return (NA, "no P&L") if k in NO_PNL else (NH, "no tick/lot rounding in backtest code (grep 0 hits)")
    if mid == "C08":
        if k in NO_PNL:
            return (NA, "")
        if k in SCREEN_FAMILY | {"S09"}:
            return (UK, "0.14 literal; fees.py not imported (L3)")
        return (UK, "executor fee on Deribit test") if k == "L" else (NH, "own cost literal (brief 1a L3)")
    if mid == "C09":
        return (NA, "no P&L") if k in NO_PNL else (NH, "no margin or liquidation model")
    if mid == "S01":
        if k == "L" or k in NO_PNL:
            return (NA, "")
        if k == "S15":
            return (H, "BH q<=0.10 over 62 strategies (brief 1b #15)")
        if k == "S16":
            return (H, "336 cells, min q 0.62 (brief 1b #16)")
        return (NH, "any-arm pass, no correction across arms (L7, D3)")
    if mid == "S02":
        if k == "L" or k in NO_PNL:
            return (NA, "")
        if k == "S01":
            return (H, "screen.py:183 cluster_mean_se (day-clustered)")
        return (UK, "")
    if mid == "S03":
        if k == "S03":
            return (H, "mal_bb_mid_engulf_2026-10-16/trials.csv (40 rows)")
        return (NA, "") if k == "L" else (UK, "")
    if mid == "S04":
        if k == "L" or k in NO_PNL:
            return (NA, "")
        return (NH, "t-test with day-cluster SE; no trimmed/robust check found")
    if mid == "S05":
        if k == "S01":
            return (H, "screen.py:430 MDE = 2.8 SE reported")
        if k == "S07":
            return (H, "EVENT_COUNTS.md MDE 0.24R ENOUGH/THIN")
        return (NA, "") if k == "L" else (UK, "")
    if mid == "S06":
        if k == "S11":
            return (NH, "levels_hold.py:78-93 controls include the real level (L8)")
        if k == "S01":
            return (H, "screen.py:193 diff_cluster vs control")
        return (NA, "") if (k == "L" or k in NO_PNL) else (UK, "")
    if mid == "S07":
        if k == "S01":
            return (H, "screen.py:55 refuses bars >= 2024-07-01")
        if k == "S12":
            return (NH, "study.py:213 calendar years incl. HOLDOUT published (N/T08)")
        return (NA, "") if k == "L" else (UK, "")
    if mid == "R01":
        if k == "L" or k in NO_PNL:
            return (NA, "")
        return (NH, "no per-year or long/short split found; D4 shows drift -0.06..+0.08%")
    if mid in ("R02", "R03"):
        if k == "L":
            return (NH, "no regime guard on live signals") if mid == "R02" else (UK, "")
        return (NH, "no stability-by-quarter or top-days-removed run found")
    if mid == "R04":
        return (NA, "") if k in NO_PNL else (NH, "no cascade-minute stress run found")
    if mid == "E01":
        if k == "L":
            return (UK, "params_id dated; SOURCED/OURS not recorded per layer")
        return (H, "PRE_REG + SOURCED/OURS rule (CLAUDE.md numbers)") if k in SCREEN_FAMILY else (UK, "")
    if mid == "E02":
        if k == "L":
            return (NA, "")
        return (H, "PRE_REG primary cell fixed (screen.py:422)") if k == "S01" else (UK, "")
    if mid == "I01":
        if k == "L":
            return (NH, "no tool compares backtest fills with testnet fills (brief 1c)")
        return (UK, "parity.py covers verdict vs live log only")
    if mid == "I02":
        if k in NO_PNL:
            return (NA, "")
        if k == "L":
            return (NH, "executor sizing not cost-in-R gated")
        return (UK, "E3 gate in FABLE audit; per-study not checked")
    if mid == "I03":
        return (NA, "") if k == "L" else (NH, "own loader/split per study (brief 1c)")
    if mid == "O01":
        return (UK, "classify_exit fixed, old rows not rewritten") if k == "L" else (NA, "")
    if mid == "O02":
        return (H, "live_runner_cli.py:195 stale window stays silent") if k == "L" else (NA, "")
    if mid in ("O03", "O04"):
        return (UK, "CLAUDE.md requires tests; none verified per layer") if k == "L" else (NA, "")
    if mid == "O05":
        return (NH, "testnet fills thin/synthetic (G3)") if k == "L" else (NA, "")
    return (UK, "")


def fmt(s, e):
    return f"{s} ({e})" if e else s


def main():
    rows = []
    for m in MODES:
        rows.append(list(m) + [fmt(*cell(m[0], c)) for c in COLS])
    hdr = ["id", "category", "failure_mode", "how_it_shows", "test", "source", "covered_by"] + COLS
    with open(os.path.join(HERE, "matrix.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(hdr)
        w.writerows(rows)
    statuses = [H, NH, NA, UK]

    def cnt(vals):
        return [sum(1 for v in vals if v.split(" (")[0] == s) for s in statuses]
    with open(os.path.join(HERE, "matrix_summary.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["axis", "name"] + statuses)
        for r in rows:
            w.writerow(["row", r[0] + " " + r[2]] + cnt(r[7:]))
        for i, c in enumerate(COLS):
            off = 7 + i
            w.writerow(["column", c] + cnt([r[off] for r in rows]))
        w.writerow(["total", "all cells"] + cnt([v for r in rows for v in r[7:]]))
    print(len(rows), "modes x", len(COLS), "columns")


if __name__ == "__main__":
    main()
