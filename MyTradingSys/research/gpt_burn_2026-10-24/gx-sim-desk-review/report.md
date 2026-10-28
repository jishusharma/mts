# Simulator desk correctness audit

Audit date: 2026-10-24. Scope: `MyTradingSys/research/sim_desk/{DESIGN.md,desk.py,charts.py,fetch_klines.py,PLUGIN.md}`, the three study adapters, shared `_bars.py`, and the ladder implementation actually called by the levels adapter. Source was reviewed without modifying it. No git, sync, push, network fetch, real price data, or account data was used.

**10 findings: 7 HIGH, 3 LOW; no CRITICAL finding established.** The desk runs offline, but its outputs should not be treated as executable perpetual-futures returns without resolving the execution and cost assumptions below.

## Reproduction and independent expectations

From the repo root:

```powershell
python -B MyTradingSys/research/gpt_burn_2026-10-24/gx-sim-desk-review/audit.py
```

The script prints one complete JSON object per comparison and a final parsed-count summary. Final execution: **25 comparisons, 13 matched, 12 mismatched**, exit code 0. Mismatches are audit evidence, not an assertion that all comparisons should pass. Two target probes form one finding; two funding probes form one finding. No conclusion depends on a truncated output. The script uses real trade engines and study adapters. Detector outputs are injected only to isolate adapter execution; no claim is made that the injected setup is a natural RSI/WaveTrend event. The full `desk.run_setting(..., charts=True)` path also ran, with its ledger and cache redirected into a temporary directory inside this audit folder and removed afterward: **n=1, mean=+0.25 R, one chart, NOT ENOUGH DATA**.

Expected arithmetic was independently computed from `MyTradingSys/backtest/layers/FORMULAS.md`:

- Lines 151-161, section 8: UTC bucket arithmetic and closed buckets only.
- Lines 175-177, section 9: R target = entry +/- target_r * abs(entry-stop).
- Lines 345-354, section 13: explicit funding sign, `(entry, exit]` funding boundaries, and slippage. This section explicitly governs the T055 strategies; its costs are used here as **labelled sensitivity scenarios**, not as a claim that its default slippage is mandatory for every desk strategy.
- Lines 462-473, section 18.5: conservative level-touch-bar ordering; subsequent gap-stop fill at the open; `net_R = (side*(exit-entry)-fee_in*entry-fee_out*exit)/R`.
- Lines 513-515, section 20.2: WaveTrend availability at bar close and gap reset convention.

All invented bar paths, the 100/98/102 prices, and execution scenarios are **OURS audit fixtures**, not trader parameters. Causality expectations that FORMULAS does not expressly specify (market-open target eligibility and next-open execution after a close-dependent signal) are labelled below. No expected number was copied from an implementation or existing test.

## Findings

### 1. HIGH — K5 stop uses price action after the entry

**Locations:** `MyTradingSys/research/levels_confluence_2026-10-14/ladder.py:141` and `:174`; invoked by `MyTradingSys/research/sim_desk/studies/levels.py:186`. The desk offers this as “just past today's extreme” at `studies/levels.py:38`.

K5 takes the minimum/maximum through the **completed touch bar**, while the entry is filled at the touched level inside that same bar. The subsequent adverse wick therefore determines the original stop and R denominator. It can move the stop past the very excursion that should have stopped an already-open position.

**Reproducer:** `K5_uses_post_entry_touch_low`. Prior low=99, long entry=100, margin=0.1%. A feasible touch path is 105 -> 100 entry -> 90 -> 100 close. At entry, the day low known so far is 99, so a causal fixed stop is `99*0.999=98.901`. Actual stop is `90*0.999=89.91` and actual gross/net return with zero fees is 0 R. Changing only the post-entry low from 99.5 to 90 changes the initial stop from 98.901 to 89.91. This is intrabar look-ahead; waiting for the close would instead require a later entry.

### 2. HIGH — Levels stop gaps are filled at an unavailable trigger price

**Locations:** `MyTradingSys/research/levels_confluence_2026-10-14/ladder.py:182` and `:196`; desk call at `MyTradingSys/research/sim_desk/studies/levels.py:186`.

The ladder finds the first low/high beyond a price stop but always exits at the stop itself. It never adjusts that exit to the opening price when the minute opens beyond the stop. This conflicts with the gap-stop convention in FORMULAS section 18.5 and understates losses. The shared RSI/WaveTrend engine does perform this adjustment, so studies also disagree.

**Reproducer:** `levels_gap_stop_fills_trigger`. Long=100, L2=98, K2 stop=`98*0.999=97.902`, R=2.098, next minute OHLC=(95,96,94,95), fees=0. Actual exit=97.902 and net=-1 R; no price in that minute reaches 97.902. Expected gap exit=95, net=`-5/2.098=-2.3832221163 R`.

### 3. HIGH — “x risk” targets use a reference price instead of actual fill

**Locations:** `MyTradingSys/research/sim_desk/studies/wavetrend.py:103`, `studies/rsi.py:104`, `studies/rsi.py:105`; actual fill and risk computed separately at `studies/_bars.py:129` and `:130`.

WaveTrend fixes its target from the signal close even though it enters at the next open. RSI fixes its target from the trigger or signal close even though the fill can gap. R is then recomputed from the actual fill without recomputing the target. Consequently a selected 1.5R or 2R target does not represent that reward relative to the trade's risk; a sufficiently large gap can even put a “target” behind entry.

**Reproducers:** `WT_target_uses_actual_fill_risk`: signal close=100, stop=90, next-open fill=110, chosen multiple=1.5. Actual target=115, net with zero fees=+0.25 R; FORMULAS section 9 target=`110+1.5*20=140`. `RSI_gap_target_uses_actual_fill_risk`: trigger=100, stop=90, gap fill=110, multiple=2. Actual target=120; expected target=`110+2*20=150`.

### 4. HIGH — Close-dependent signal exits receive the already-closed price

**Locations:** `MyTradingSys/research/sim_desk/studies/_bars.py:153` and `:154`; close-dependent signals at `studies/rsi.py:109` and `studies/wavetrend.py:107`.

The adapters decide the exit using the completed indicator bar, then the engine fills at the close of the minute immediately before the signal becomes available. The implementation documents this assumption, but it grants a close-dependent decision the price that generated it. The exit timestamp also records that minute's **open**, one minute earlier than its close. Entry correctly waits until the signal bar closes; exit does not use equivalent executable timing.

**Reproducer:** `signal_exit_at_already_closed_price`. Entry=100, stop=80 (R=20), the signal becomes known at 00:02 UTC after a close of 101, next open=90. Actual net=`(1-.05-.0505)/20=+0.044975 R`, timestamp=00:01. Under the **OURS causal next-open fill** convention, net=`(-10-.05-.045)/20=-0.50475 R`, execution time=00:02. A market-on-close convention would need a rule executable before knowing that close; none is implemented.

### 5. HIGH — Entry-minute target suppression also affects market-open entries

**Location:** `MyTradingSys/research/sim_desk/studies/_bars.py:140`.

The engine disables the target throughout the fill minute for every entry. FORMULAS section 18.5 deliberately does this for a level touch whose intrabar ordering is unknown. Applied to a market entry at the minute open, however, entry precedes all subsequent prices, so a target-only hit is knowable. This documented conservative policy changes completed winners into later losers.

**Reproducer:** `market_entry_target_on_fill_bar`. Market buy=100 at open, stop=98, target=102, entry minute OHLC=(100,103,99,102), next minute reaches 98. Actual result=-1.0495 R. Under the **OURS market-open execution** convention, the first minute hits only the target, so expected net=`(2-.0005*100-.0002*102)/2=+0.9648 R`. Retain the conservative touch rule for genuinely ambiguous touch entries; it is not evidence that a market-open target was unavailable.

### 6. HIGH — Breakout entry can exit at an opening price from before entry

**Locations:** `MyTradingSys/research/sim_desk/studies/_bars.py:129`, `:135`, `:146`.

The engine applies a gap-stop rule to the entry minute even when the position did not exist at its open. For a breakout triggered later in that minute, it can select the pre-entry opening price as the stop exit. Conservative intrabar ordering does not make an earlier opening print an executable post-entry price.

**Reproducer:** `breakout_fill_bar_pre_entry_open_as_stop`. Minute OHLC=(90,105,89,104), long trigger=100, stop=95, fees=0. Actual entry=100, exit=90, net=-2 R. If adopting the documented conservative assumption that the stop was reached after entry, the stop fill should be 95, net=-1 R. If the low occurred before entry, no entry-minute stop is established. Neither ordering supports selecting the known pre-entry open of 90.

### 7. HIGH — Perpetual-futures “net” omits funding entirely

**Locations:** `MyTradingSys/research/sim_desk/studies/_bars.py:107`, `:156`, `:159`; levels equivalent `MyTradingSys/research/levels_confluence_2026-10-14/ladder.py:222` and `:224`. Instruments come from perpetual-futures archives at `sim_desk/fetch_klines.py:15`. Multi-day holding is exposed at `studies/rsi.py:113` and `studies/wavetrend.py:111`.

Neither trade engine accepts a funding schedule or charges/credits funding. Thus equal fee settings give identical long/short flat-price returns across funding times, even for positions held for days. There is no desk disclosure in the study descriptions that this cost is excluded. This is a missing economic component, not an incorrect sign calculation in an existing funding implementation.

**Reproducers:** `funding_absent_long` and `funding_absent_short`. Flat entry/exit=100, R=2, taker fee=.0005 each side, hold 16 hours. Actual=-0.05 R for both. In the explicitly assumed FORMULAS section 13 scenario, positive funding .0001 at 8h and .0003 at the 16h exit is included by `(entry,exit]`: long expected=`(-.1-.04)/2=-0.07 R`; short expected=`(-.1+.04)/2=-0.03 R`. These are synthetic rates, not observed historical rates. Funding at entry would be excluded. Actual funding boundary behavior cannot be tested because no funding input exists.

### 8. LOW — Resampling emits unfinished bars and hides minute gaps

**Locations:** `MyTradingSys/research/sim_desk/studies/_bars.py:94` through `:100`; consumers `studies/rsi.py:82` and `studies/wavetrend.py:86`.

Resampling emits every bucket, including the unfinished trailing bucket, contrary to FORMULAS section 8. It also turns an hour with 59 minutes into an ordinary hour with no missing-data marker. UTC anchoring is correct, but completeness is not enforced. A partial trailing signal will generally have no later fill data; the demonstrated defect is premature indicator input, not proof of a completed profitable trade. Internal missing minutes can affect indicator values, stops and warm-up without warning.

**Reproducers:** `partial_trailing_bucket`: 61 consecutive 1m bars resampled to 1h produce **2** bars; only **1** hour is closed at the final minute's close. `missing_minute_emits_ordinary_hour`: delete minute 30 from an otherwise full hour; output still contains one ordinary hour from 59 inputs and no gap flag. No claim is made that complete historical monthly files actually contain such gaps; source validation is absent.

### 9. LOW — Slippage is absent on both entry and exit

**Locations:** `MyTradingSys/research/sim_desk/studies/_bars.py:121`, `:129`, `:146`, `:156`; levels fill/exit and cost accounting at `MyTradingSys/research/levels_confluence_2026-10-14/ladder.py:174`, `:196`, `:222`. Desk descriptions show fees at `sim_desk/studies/rsi.py:77` and `studies/wavetrend.py:79`.

There is no configurable or stressed entry/exit execution slippage. Gap adjustment in the shared engine is not a slippage model. The older ladder runner explicitly calls this “no slippage” (`ladder_run.py:291`), so this is a modelling/disclosure limitation rather than a hidden arithmetic implementation error. The desk should identify results as fee-only and expose an execution-cost sensitivity before treating them as realistic P&L.

**Reproducer:** `slippage_absent`. Flat trade=100, R=2, fees=.0005 each side gives actual=-0.05 R. Adding the **OURS sensitivity** of one basis point of entry notional per side (section 13's two-basis-point round-trip scenario) costs another `100*.0002/2=.01 R`: expected=-0.06 R. Neither side of the simulator currently receives that charge.

### 10. LOW — Charts detach execution markers from candle positions

**Locations:** `MyTradingSys/research/sim_desk/charts.py:45`, `:63`, `:66`, `:70`.

Candles lose their actual bucket keys and are packed from x=0, while entries/exits are positioned relative to the requested 30-minute pre-entry window. When that window precedes the available day bars, or bars have gaps, the two coordinate systems differ. A valid execution marker can appear outside the entire SVG, making examples unreliable for checking fills.

**Reproducer:** `chart_entry_at_day_open`. Eleven 1m bars at UTC day start, entry at minute 0, exit at minute 10: three 5m candles have centres x=50,150,250 on a 300-wide chart. The first-bar entry circle is rendered at **x=650**, outside the viewBox, instead of x=50. Preserve bucket timestamps and use the same time origin for candles and markers.

## Checks that matched and scope limits

- **Both-side fees:** independently derived FORMULAS example long 100 -> 102, R=2, all-taker returns **+0.9495 R**. Short stop 100 -> 102 returns **-1.0505 R**. Shared stop-before-target bar returns **-1.0495 R**. These matched; no missing exit-fee defect was found.
- **Gap behavior in shared engine:** an already-open long 100, stop98, next open95 returns **-2.54875 R** after fees. Correct, unlike the levels engine.
- **Position sizing:** the levels desk uses planned full size=1 and planned average-to-stop R, not a cash portfolio. A half-filled S1 position (100 filled for .5, 98 unfilled for .5), target110 and stop97.902 produced **filled_qty=.5**, net=`(5-.01-.011)/1.098=4.5346083789 R`, as independently expected. A result above the full-plan multiple here is a consequence of the stated planned-R denominator. RSI/WaveTrend report per-unit R from actual fill. There are no equity, leverage, lot-size, margin or liquidation controls on these desk study paths; no claim is made that these normalized studies enforce an account risk budget. Levels ideas can overlap (the underlying runner explicitly describes a per-idea study at `ladder_run.py:297`). The desk is not a portfolio sizing simulator.
- **Boundaries:** entry trigger exactly at the exclusive entry-window end does not fill. The first bar opening at the hold end is excluded. The WaveTrend adapter starts entry at the signal hour's close, **03:00 UTC** in the fixture; no entry before signal close was found in this path. RSI uses the same `signal_open+tf` handoff (`studies/rsi.py:112`). Stops win when both price barriers hit a later minute. Touch-bar stop-first handling is an explicit conservative assumption; unknown OHLC ordering cannot establish a real tick path.
- **Timezone/date lock:** `2022-04-01` maps to epoch **1648771200000**; resampling uses epoch-aligned UTC arithmetic; chart captions use `timezone.utc`. DEV end 2024-07-01 is rejected. No local-time conversion or DST dependency was found in the inspected paths.
- **Fetcher:** reviewed all 47 lines. New ZIP downloads verify SHA256 before extraction. Existing CSVs are deliberately skipped without revalidation (`fetch_klines.py:33`); the offline mock counted **30 months and zero network calls** when files exist. Missing destination directories are not created. No network fetch was necessary or performed. A checksum does not validate bar cadence/completeness, which remains the limitation in finding 8.
- **Docs:** DESIGN's historical “levels only” scope has been expanded by PLUGIN and the actual study loader; execution is in the imported engines, not `desk.py`. PLUGIN calls the result R after fees. That accurately describes fee subtraction but does not supply funding, slippage, or portfolio guarantees. No real-market edge, error frequency, or historical P&L impact was estimated from these tiny fixtures.

Only `audit.py` and this report are retained in the authorized task directory. Imported modules were run with bytecode writing disabled. Existing code, tests and cards were not edited.

Result: Offline desk reproduced; 25 comparisons yielded 10 findings (7 HIGH, 3 LOW), including intrabar look-ahead, gap fills, incorrect R targets and missing funding.
