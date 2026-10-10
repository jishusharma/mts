# TOM TRANSFER PROBE - why coded Tom shows no edge, and every way we test it (2026-10-11, Opus, JIS-NB)

Operator ask (chat 2026-10-11, paraphrased): coded Tom/Fabio show no edge; maybe we miss something basic about HOW the rules
are traded (selection, trade management, session timing); extraction may lose what Tom points at on the chart; try Tom on DAX,
his home market. "We need to foresee the ways in which we need to proceed, not just 1 fixed way/finding." Operator correction:
CME BTC futures now trade 24/7, so there are no CME weekend gaps; gap rules matter for DAX only.

## 1. What the record already says (no new runs)
| Fact | Source |
|---|---|
| Tom sensitivity run: gross R -0.15 [-0.29, 0.04] per trade BEFORE fees; random-entry null +0.223 | research/fast_track_2026-09-27/TOM_CORE_BT_RERUN_2026-10-06_full.md:6,121 |
| Median stop 0.082 % of price (DAX-scale stops on BTC), fees ~2.76 R | same :109; B146 |
| Live rule (SETUP_FORMING) 0 trades in 4.7 y; old run had 19; Tom holdout 2026-06-26.. read twice (burned) | B147 |
| Fabio layers: lift ~1.0 vs base rate on every TF | research/bigtrade_2026-10-09/CAPTURE_MATRIX.md |
| Backtest exit = fixed bracket: stop / target / timeout 8 TF bars, one trade at a time, every rule match taken, 15-min cadence 24/7 | backtest/tom_bt.py:11-19,204-217 |
| Tom's own trades: 21 rows, ~70 % short; DAX 8 rows; most are managed (re-entry after stop, partial take, stop moved, rest running) and sit at the open / pre-market | research/fast_track_2026-09-27/ANGLE_TRADE_CATALOG.md rows 8-19 |
| Partial size and trail frequency are not stated by Tom | conditions/risk_protocol.md:634-635 |
| Session rules for BTC are a research adaptation, not Tom's words | conditions/session_timing_rules.md:1-8 |
| Tom on gaps (DAX): 9 transcripts; none of it is in conditions/ | raw_transcripts_canonical: 3JqMyzE8jIQ, 5Ljfwvtktek, 96iPFDpXEcU, DVZVE9rXGtU, l8RZrBfzvp4, lO-Iptd29t4, Of_wlv3xaZo, ujedEcmvBMk, YopZ5ZDmMFw |

Reading: gross below random means the ENTRIES as coded are not Tom's entries, or Tom's edge lives in what we do not
model (which setups he takes, how he manages them, when he trades). Fees only make a bad gross worse.

## 2. The five places the edge can be lost (hypotheses, each with its own test)
| H | Hypothesis | Cheapest test that can refute it |
|---|---|---|
| H1 Encoding | The coded rules do not fire where Tom traded | Recall on his own DAX trades (card tom-dax-recall) |
| H2 Selection | Tom takes a few setups per session; we take every match | BTC rows: gross R of first-per-session vs the rest; by proof count (card tom-probe-diag-btc) |
| H3 Management | Edge comes from re-entry, partials, trailing; a fixed bracket throws it away | MFE/MAE in R per trade: if MFE before stop is rarely > 1 R, no management can help (same card) |
| H4 Session | Edge lives at the open (liquidity); 24/7 sampling dilutes it | Gross R by session start hour, DST-correct (same card) |
| H5 Transfer | Rules work on DAX, not on BTC (stop scale, fees, 24/7, no gaps) | Untuned DAX backtest vs BTC on the SAME proof set (card tom-dax-backtest) |
Data limit for H1/H5: free DAX history has no real volume / order flow, so the order-flow proofs cannot count there;
BTC must be re-run with the same reduced proof set for a fair comparison (matched-proof).

## 3. The option map (arms are declared BEFORE any run; one axis at a time against the baseline)
Arms are experimental conditions, not engine parameters. An arm only becomes a rule if it maps to a Tom quote + file:line;
otherwise it is labelled NO-SOURCE and needs an operator decision before it can go live.

Session arms (S), defined in exchange-local time, converted to UTC with DST:
- S0 all hours (current baseline). S1 Tom's literal window on DAX: Xetra open 09:00 CET + pre-market (catalog rows 9, 18).
- S2 BTC, each session open as the start, first 2 h and first 4 h: Asia 09:00 JST, Europe 09:00 CET (DAX open),
  London 08:00 UK, US equity open 09:30 ET, US close 16:00 ET. S3 weekday vs weekend.
- S4 cadence: 15-min snapshots (now) vs 1-min evaluation inside the S2 windows (signal lag up to 15 min today).
Source status: Tom trades the open for liquidity (to be quoted by the gap/recall cards); the BTC session that plays that
role is a translation, so S2 is NO-SOURCE until the operator picks it from the results.

Selection arms (Q): Q0 every match (baseline); Q1 first signal per session; Q2 highest proof count per session;
Q3 only with Tom's market state / day type in conditions/market_state_rules.md; Q4 only with the HTF bias; Q5 max N
trades per day (N from a Tom quote, else NO-SOURCE). Descriptive check first: do observable features separate winners
from losers at all on hist+dev? If nothing separates them, skip Q2-Q5.

Management arms (M): M0 fixed bracket (baseline); M1 trail to the last 5-min volume level (risk_protocol 2.11,
4MoNjEQ2Dd8), updated per 5-min close (frequency NO-SOURCE); M2 partial on rotation (risk_protocol 5.4; size
NO-SOURCE, test 50 %); M3 one re-entry after a stop at the same zone (catalog rows 9-10, 14-15, 19); M4 no timeout
(the 8-bar timeout is itself unsourced: flag it). Gate: run M arms only if the MFE diagnostic leaves room.

Stop/fee arms (F, with B146): stop-width buckets <0.1, 0.1-0.2, 0.2-0.4, >0.4 %; maker vs taker legs.

Market arms: DAX (home), BTC; Nasdaq future only if the DAX result is positive (Tom has 2 Nasdaq rows).

## 4. Order, decisions and stop rules (the tree)
1. In parallel, no new data needed: tom-probe-diag-btc (H2/H3/H4 descriptive, hist+dev only, holdout untouched).
2. tom-dax-recall (H1). If recall < 3 of 8 DAX trades for reasons that are not data limits: STOP all backtests;
   fix the extraction first (video frames at each "here / this level", read with the sentence). Data-limited misses are
   NOT_IN_DATA, not failures.
3. tom-gap-rules-extract: Tom's gap rules as a DAX-only layer, sourced quotes, frames for pointing words.
4. tom-dax-backtest (H5), untuned, matched-proof BTC rerun alongside.
5. tom-probe-prereg: freeze the arms of section 3 that survived steps 1-4, trial count, DSR/PBO, then one runner card.
Branches after step 4:
- DAX edge, BTC none -> transfer problem: run S/F arms on BTC first (stop scale, session), then M.
- No DAX edge, recall fine -> the edge is discretionary: run Q and M arms on DAX first (home market, cleaner), then BTC.
- No edge anywhere and MFE rarely > 1 R -> entries no better than random: back to extraction (frames), no tuning.
- Edge in one BTC session only -> pre-register that window and forward-test on testnet; no live change before that.
Holdout: Tom's 2026-06-26.. window is burned (B147). New BTC holdout = data from 2026-09-27 onward, read once when it
holds >= 100 trades of the frozen arm. DAX: last 6 months of the downloaded history, untouched until step 5.
Trial count: every arm run is a registry row in bt_runs/TRIAL_REGISTRY.csv; DSR uses the honest count.

## 5. What this plan does not do
No "tune on DAX, then copy to BTC": tuning breaks the provenance rule and spends the evidence. DAX is a diagnosis of
where the edge is lost. No live or testnet change comes out of this plan without a pre-registered pass and the supervisor.
