# Cross-vendor review: Gemini canonical formula audit

Date: 2026-10-24. Reviewer: GPT. Task: gx2-check-gemini-formulas.

Reviewed the requested absolute file:
`F:/MTS/gq/gb-formulas-audit/MyTradingSys/research/gemini_burn_2026-10-24/formulas_canonical_audit.md`.
Below, **G:line** refers to that exact file; **F:line** refers to
`MyTradingSys/backtest/layers/FORMULAS.md` in this worktree. Other paths are repo-relative.

The three distinct MISMATCH claims yield **2 CONFIRMED, 0 WRONG CLAIM, 1 UNCLEAR**.
These are comparisons with external conventions, not three implementation defects:
the inspected implementations reproduce the repo's chosen definitions. Gemini also
overstates its coverage and does not establish its claimed native flat-series RSI value.

## Method and reproduction

Read the complete input files programmatically, then counted: FORMULAS.md has 582
lines and 24 numbered sections; Gemini has 217 lines and 15 indicator matrix rows.
There are eight occurrences of `MISMATCH`, including the table legend and repeated
claims, but only three matrix rows with that verdict: G:34, G:37, G:39. G:19-21 and
G:114 repeat them. No conclusion depends on clipped terminal output.

All repo expected numbers below were derived from FORMULAS.md before importing
the implementing functions. Alternative calculations change only the convention
under discussion. Examples use small OURS diagnostic periods, not tuned strategy
parameters. The script disables bytecode writes and performs no file writes.

Run from `F:/MTS/gq/gx2-check-gemini-formulas`:

```powershell
python -B MyTradingSys/research/gpt_burn_2026-10-24/gx2-check-gemini-formulas/reproduce.py --sources
```

Result: seven implementation comparisons passed: two RSI functions, two EMA
functions, ATR, WaveTrend, and the illustrative MACD calculation. Java core ATR
was checked directly in source; the script executes the matching Python ATR
implementation, not Java. No Pine runtime execution or chart export was performed.

The optional `--sources` check reads TradingView's own public reference asset,
which supplies the examples dynamically to its reference page. It found the
first-value EMA seed and the unguarded RSI RMA ratio, and did not find Gemini's
RSI ternary in the RSI entry. Asset bytes: 1,406,257; SHA-256:
`47d8410c197538c25740b8783b8bc1898e1b3fa4ecd68ce1b126265aa476f3fe`.
The check is a documentation check, not proof of a native runtime edge case.

## Every claimed MISMATCH

### 1. Flat-series RSI: UNCLEAR — severity LOW

**Claim locations:** G:19, G:34, G:114; repeated in parameter prose G:129.
**Spec:** F:14-25 explicitly seeds from `period` changes and returns 50 when
both average gain and average loss are zero. F:22-24 already calls this a
deliberate deviation from TradingView.

**Implementations inspected:**

- `MyTradingSys/backtest/layers/rsi/rsi_core.py:26` constructs the seed inputs;
  `:29` and `:30` divide by period; `:33` and `:34` select 50 on flat input;
  `:46` and `:50` apply smoothing and the same guard afterwards.
- `MyTradingSys/backtest/layers/krown/krown_core.py:295` constructs changes;
  `:297` and `:298` divide by period; `:300` through `:303` implement the same guard.

**Independent example, period 2, closes [10,10,10]:** changes [0,0], average
gain 0, average loss 0. F:21 selects **50** at index 2; both implementations
return `[None,None,50]`. Gemini's asserted `down==0` first branch would select
**100** on these exact averages, a 50-point difference. Ordinary unguarded RSI
instead reaches `RS=0/0`; it cannot independently produce the claimed 100.

**What is wrong or unresolved:** the repo result is confirmed, but Gemini labels
the ternary a verbatim `ta.rsi` reference quote. The official reference's RSI
example uses an unguarded RMA ratio, as does TradingView's support calculation.
Neither is the quoted guard. FORMULAS.md's own assertion of native 100 cannot
serve as independent evidence for Gemini's same assertion. This review therefore
does not certify that native `ta.rsi` returns 100 on an entirely flat series.
It also does not assert that native `ta.rsi` must return NaN; that needs an actual
runtime fixture. **UNCLEAR** applies to the external-runtime claim, with the
quote attribution unsupported. No repo implementation fix follows from it.

**Reproduction:** the command above prints `RSI`, including repo 50, alleged
guard 100, and the undefined unguarded ratio; `OFFICIAL_REFERENCE` prints
`rsi_has_unguarded_RMA_ratio=true` and `rsi_has_Gemini_ternary=false`.
[Official RSI calculation](https://www.tradingview.com/support/solutions/43000502338-relative-strength-index-rsi/),
[official dynamic reference asset](https://static.tradingview.com/static/bundles/11967.f28d44b63e7af1f5c57f.js).

### 2. EMA seeding: CONFIRMED, scoped to RSI MA / Krown — severity LOW

**Claim locations:** G:21, G:37, G:63-65. **Spec:** F:87-89 chooses an SMA seed;
F:95-102 explains the choice; F:539 makes the same choice for Krown.
**Implementations:** `MyTradingSys/backtest/layers/rsi/rsi_ma.py:49` through
`:59`, especially the SMA seed at `:56`; and
`MyTradingSys/backtest/layers/krown/krown_core.py:28` through `:36`, seed at `:34`.

**Independent example, length 3, x=[50,55,45,60]:** alpha=1/2. Repo seed at
index 2 = (50+55+45)/3 = **50**; next = 50+(60-50)/2 = **55**.
First-value seeding gives **[50,52.5,48.75,54.375]**. Thus repo minus
first-value EMA is +1.25 at index 2 and +0.625 at index 3. Both inspected
repo functions return **[None,None,50,55]**.

**What is wrong:** cross-platform early-series parity does differ, and
FORMULAS.md:92 incorrectly attributes an SMA-style first seed to TradingView.
TradingView's official reference example selects the source as its initial
state; this is independently verified in its dynamic reference asset.
The code follows the chosen repo definition, so this is a documentation/parity
issue, not a failure to implement F:87. The TA-Lib historical assertion in
F:98 and Gemini's TA-Lib comparison were not needed to establish this verdict
and were not verified here.

**Important scope:** Gemini's broad wording must not be read as an all-repo EMA
rule. F:515 explicitly chooses **first-valid-value seeding for WaveTrend**.
`MyTradingSys/backtest/layers/wavetrend/wavetrend.py:93` and `:95` implement it;
`:101` seeds TCI from the first valid CI. For ap=[10,12], alpha=2/11:
ESA[1]=114/11, deviation=18/11, smoothed deviation=36/121,
CI=(18/11)/(0.015*36/121)=**366.6666667**. WaveTrend produces that value in
the diagnostic run with warmup=0; an SMA-seeded length-10 EMA would still have
no seed after two bars. Default warmup remains 200. This exception is a chosen
spec convention, not an inconsistency requiring harmonization.

**Reproduction:** command above, `EMA` and `WAVETREND` rows.
[Official EMA reference entry](https://www.tradingview.com/pine-script-reference/v6/#fun_ta.ema),
[official reference asset](https://static.tradingview.com/static/bundles/11967.f28d44b63e7af1f5c57f.js).

### 3. Core ATR smoothing: CONFIRMED deliberate choice — severity LOW

**Claim locations:** G:20, G:39, G:104-106. **Spec:** F:327-328 defines TR
from index 1, and F:330-335 explicitly mandates a simple mean for the core.
F:495 reuses it for trend lines.

**Implementations:** `src/main/java/datafeed/SetupCandidatesBuilder.java:911`
through `:918`: iterate `[start,end)`, sum true ranges at `:915` and `:916`,
divide by count at `:918`. The implementing expression is a simple average.
`MyTradingSys/backtest/layers/krown/krown_context.py:44` through `:51` also
uses a rolling TR mean, with no TR at index 0.

**Independent example, period 3:** highs=[10,11,12,11,14,12],
lows=[9,9,10,9,8,10], closes=[9.5,10.5,11.5,10,11,11]. TR at bars
1..5 = **[2,2,2.5,6,2]**. Both smoothing conventions can share the bar-3
seed (2+2+2.5)/3 = **13/6 = 2.1666667**. Thereafter:

| Bar | Repo rolling SMA | Wilder RMA, same seed |
|---|---:|---:|
| 4 | (2+2.5+6)/3 = 3.5 | ((13/6)*2+6)/3 = 31/9 = 3.4444444 |
| 5 | (2.5+6+2)/3 = 3.5 | ((31/9)*2+2)/3 = 80/27 = 2.9629630 |

**What is wrong:** there is no spec violation in this core implementation.
Comparison with default RMA ATR differs by design. Gemini's numerical claim
of 10%-25% discrepancies on volatile swings at G:106 has no supplied dataset,
denominator, or reproduction; it must not be treated as a measured range or
bound. In this small example bar-5 SMA is 18.125% above same-seed RMA. The
example isolates smoothing, not native TradingView's different bar-0 TR rule.

**Reproduction:** command above, `ATR` row. The shared seed is essential:
the original F:337-341 seed-only example cannot alone demonstrate a difference
between the smoothing methods.
[TradingView ATR calculation and default RMA smoothing](https://www.tradingview.com/support/solutions/43000501823-average-true-range-atr/).

## Other material findings about Gemini's report

### Incomplete coverage presented as complete — severity HIGH

**Locations:** G:12 claims every indicator formula was evaluated; G:30 calls its
matrix comprehensive; G:124 claims an inventory of every indicator parameter;
G:212 claims all referenced files were inspected line by line. These statements
exceed the supplied evidence. Fifteen matrix rows are not a complete review of
the 24 specification sections. Several omitted sections contain indicator,
signal, or event definitions as well as execution and statistical formulas.
Even a narrower indicator-only reading skips Krown and Kurisko event math.

**Reproduction/count:** the command prints all file and matrix counts plus the
manual coverage classification: **9 wholly omitted sections, 7 partially
reviewed sections, 8 remaining sections discussed**. This is section-level
coverage, not a count of atomic formulas or a certification of the other eight.
The following is the complete omission inventory against the 24 section headings.
It lists omissions, not newly proven bugs in their implementations.

| Spec location | Omitted formulas / rules | Coverage in Gemini |
|---|---|---|
| F:121, section 6 | Tolerance-band classification, run tracking, support/rejection/failure/cross events and gap semantics | Wholly omitted |
| F:133, section 7 | Signed forward return, close-only MAE, positive-return hit rate, horizon eligibility and aggregation | Wholly omitted |
| F:151, section 8 | Epoch/calendar/week/month bucket anchoring, OHLCV aggregation, closed-bucket eligibility | Wholly omitted |
| F:163, section 9 | Strict fractal swings, MSB prior-sequence gates, retest tolerance/invalidation, R-target | Wholly omitted |
| F:179, section 10 | PSR, DSR, expected maximum Sharpe, CSCV split selection, OOS rank/logit and PBO boundary | Partial: Sharpe population stdev only, G:89-90 |
| F:205, section 11 | Directional tick snapping; contract amount floor/minimum; ladder rung spacing; inverse harmonic fill mean; inverse stop loss/PnL; target inversion; notional cap | Wholly omitted as an audit; G:40 merely distinguishes harmonic fills from VWAP |
| F:343, section 13 | Signed gross/net return, round-trip fees/slippage, funding sign and (entry,exit] funding interval | Wholly omitted |
| F:356, section 14 | Inclusive funding percentile, funding availability, strict CVD/price divergence, combined and funding-only signal rules | Partial: delta/CVD algebra only, G:47 |
| F:372, section 15 | UTC session window, first-window return, threshold side, exact entry-close timing | Wholly omitted |
| F:385, section 16 | Minute-of-quarter, per-minute returns and means, lead-minute event rule | Wholly omitted |
| F:400, section 17 | Fee-adjusted net R:R, fee constant parity and zero-risk guard | Wholly omitted |
| F:408, section 18 | 18.2 strict pivots/confirmation; 18.3 ATR size filter; 18.4 anchor sets/refresh; 18.5 touch, barriers, stop-first resolution and net R; 18.6 placebo shifts; 18.7 day-block bootstrap | Partial: 18.1 volume allocation/POC/VA only, G:48 |
| F:485, section 19 | Strict pivots; linear/log line geometry; ATR/log slopes; contact/poke/break thresholds; contact reset; prior-volume ratio; third-anchor tolerance | Partial: 19.3 ATR referenced in G:39; contract rules omitted |
| F:509, section 20 | Tie-skipping crosses, side reset, zone boundaries, available_at and closed-HTF selection | Partial: oscillator arithmetic, guard and warmup discussed; event/timing rules omitted |
| F:525, section 21 | Zone construction/ranking/confirmation; prior/same-slot volume baselines; strict engulfing and candle ratios; dominant-level structure and reversal; leash state/event; range position/width, coil score; tops window/count transition and RSI divergence | Partial: BBWP, EMA/RSI reviewed; some parameters named without checking these formulas |
| F:559, section 24 | RSI-arm numeric example; gap/NaN window splitting; double-smoothed variant; strict episode entry and turn rule; one event per episode; mirrored short and event timestamps | Partial: stochastic raw/D line reviewed, RSI arm named, events not audited |

For example, F:404 independently gives net R:R at entry=100, target=104,
stop=98, fee/side=0.0005: cost=0.1, net R:R=3.9/2.1=**1.857142857**.
This money-relevant formula does not appear in Gemini's matrix. No judgment
about the implementation of this skipped formula is made here.

### Missing VWAP / MACD definitions: CONFIRMED documentation gaps — severity LOW

**Locations:** G:22-23, G:40, G:42; spec F:545. Full-file token counting finds
**zero VWAP occurrences** and **one MACD occurrence**, at F:545. Indicator VWAP
has no mathematical definition in this file. MACD is named as a tops condition,
without a standalone line/signal/histogram or seeding contract. Section 11's
harmonic inverse fill price is a different execution quantity.

There is MACD code: `MyTradingSys/backtest/layers/krown/krown_core.py:323`
through `:335` computes fast EMA minus slow EMA and an SMA-seeded EMA of
valid MACD values. For [1,2,3,4,5], illustrative periods (2,3,2), the section-4
SMA-seed convention independently gives fast-minus-slow **0.5** at indices
2..4, and signal **0.5** at indices 3..4; code agrees. First-value EMA would
instead give line[2]=**0.30555556**, line[4]=**0.44367284**. This illustrates
why the absent MACD seeding definition matters, but is not a new authoritative
MACD test oracle. Reproduction: `INVENTORY` and `MACD_ILLUSTRATION` rows.

## Scope and disposition

Preserve the explicitly chosen RSI, core ATR, RSI-MA/Krown EMA, and separate
WaveTrend contracts. Correct the EMA reference attribution if documentation
is later edited; verify flat-series native RSI using an actual Pine fixture
before repeating 100 as a runtime fact. Gemini's MATCH rows were inventoried
for coverage, not independently certified as an exhaustive second audit.
All report and script writes were restricted to this task directory. No git,
sync, push, existing code/test/card edits, or live-system actions were run.

Result: 3 distinct MISMATCH claims reviewed: 2 CONFIRMED and 1 UNCLEAR; repo examples pass; 9 sections wholly skipped and 7 partially reviewed by Gemini.
