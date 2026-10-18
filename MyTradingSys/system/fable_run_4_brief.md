# Fable run 4 brief: Tom/Fabio setups from naked BTC charts, six angles, one at a time

Self-contained brief. The operator starts one Fable 5.1 session per angle, by hand, in the order below. Each session reads the pack, writes up to 3 setups for its angle, ships them, and stops.

Fable only **proposes** rules here. Nothing Fable writes is evidence: every setup is coded, counted and scored by Sonnet on data Fable never saw, through the normal gate.

Run order (operator 2026-10-19):
1. Run 2 (re-gate) first.
2. Run 3 (end-to-end backtest review), when written.
3. This run 4.

The pack card below can be built now.

## The hindsight problem, and how this design handles it
| Leak | Guard |
|---|---|
| Fable sees the chart and the future at once | Fable sees only the **LOOK window**, DEV 2022-01-01 .. 2023-06-30. The **BLIND window**, DEV 2023-07-01 .. 2024-06-30, is not in the pack. Sonnet scores setups there mechanically. VALIDATION (2024-07-01 .. 2025-06-30) is read once, only for setups that survive BLIND, under a normal PRE_REG. HOLDOUT is untouched. |
| Fable remembers BTC history from training (2023-2025 included) | This cannot be removed. Rules must be mechanical and computable, so memory cannot steer a trade. The final arbiter is promotion plus forward testnet paper trading, never a backtest alone. Each setup must say what it would need to be true going forward. |
| Many angles x many setups = best-of-N | At most 3 setups per angle and at most 15 overall. Every setup is a trial-ledger row before scoring (`verdicts.py count --ledger`, Holm m auto). |
| Probabilities fitted after the fact | Each setup states p(win), average win R, average loss R and expected net R after 14 bp **before** any count. BLIND scores against the stated band, not against "positive". |
| Image-read levels are imprecise | Levels come from the pack's computed tables (FORMULAS 18.1 POC/VAH/VAL). The charts are for context only. A rule may reference only pack columns. |

## Step 0 (Sonnet, card fable-setups-pack-prep): build the pack, before any Fable session
Build `MyTradingSys/research/fable_setups_2026-10-19/pack/` from public Binance USD-M BTCUSDT klines (LOOK window only; assert max bar open < 2023-07-01):
1. `ohlcv_{1w,1d,12h,4h}.csv`: open time UTC, OHLC, volume, taker buy volume (the only order-flow proxy; say so in README).
2. `levels_daily.csv`, `levels_weekly.csv`: for each prior day and prior week:
   - POC, VAH and VAL per FORMULAS 18.1 (70 % value area, same bin rule);
   - high, low, open and close;
   - Asia, London and NY session high and low per the session_levels layer.
3. Naked charts as PNG, candles plus volume only, no indicators, one line per prior-week POC/VAH/VAL:
   - 1W: the whole window, 1 chart;
   - 1D: one per quarter, 6 charts;
   - 12h: one per quarter, 6 charts;
   - 4h: one per month, 18 charts.
   That is 31 images. Keep each under 150 KB, 5 MB in total; it is public market data.
4. `RULES_DIGEST.md`, at most 250 lines: Tom and Fabio rules only as SOURCED quotes with file:line. Take them from:
   - `research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md`;
   - `research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md`;
   - `research/TOM_VERBATIM_INDEX.md`;
   - `research/fast_track_2026-09-27/FABIO_RULEBOOK.md` and `FABIO_TRADE_MODEL.md`.

   Add a list of what already failed, from `system/LAYERS.md` Tom/Fabio entries:
   - TOM-CORE: net -0.30 R;
   - VP anchors: no edge over placebo;
   - Fabio v3: OOS -0.10 R.
5. `README.md`: column meanings, window dates, cost 14 bp round trip (FORMULAS 13), and a statement that nothing after 2023-06-30 is in the pack.

Test: a check script asserts that no file in the pack holds a timestamp >= 2023-07-01. It must fail on a planted row.

## The six angles (one Fable session each, in this order)
| # | Angle | What Fable looks for | Must not |
|---|---|---|---|
| 1 | **Tom value edges** | Reactions at prior day/week VAH, VAL and POC: rejection back into value vs acceptance outside value; which HTF context (1W/1D trend, 12h range) separates them | Re-propose TOM-CORE or a plain VP-anchor touch (both failed); say what is different |
| 2 | **Fabio flow proxy** | Fabio's own model with taker-buy share as the CVD proxy: absorption at a level (high volume, small range), imbalance continuation out of value | Claim tick-level flow; every rule must compute from 4h/12h bars + taker volume |
| 3 | **Top-down context filter** | No entries: a regime map (1W/1D trend, 12h range/expansion) that says when angles 1-2 are allowed or banned. Output 1-3 filters, each a computable condition | Add entry rules |
| 4 | **Confluence** | Setups only where a Tom level and a Fabio flow condition meet (angle 1 x angle 2 outputs), plus angle 3's filter | Exceed 3 setups; reuse an angle 1-2 setup unchanged |
| 5 | **Loser anatomy** | In the LOOK window, find where the obvious Tom/Fabio plays lost (stop runs through VAL, fake acceptance). Output 1-3 **veto** conditions that remove losers | Tune a veto to a single episode; each needs at least 10 eyeballed instances, listed by date |
| 6 | **Devil's advocate** | Read the files from angles 1-5. For each setup: the hindsight trap, the placebo it must beat (random level at the same distance, or the same rule with direction flipped), and its expected trade count. Rank everything; keep at most 8 for BLIND | Add new setups |

Sessions 2-6 read the earlier angles' files first. That is the "one by one" chaining.

## Per-setup template (angles 1, 2 and 4 write setups; 3 and 5 write filters or vetoes with the same fields where relevant)
Each setup gets its own section in `research/fable_setups_2026-10-19/ANGLE_<n>.md`:
- `id` (A<n>-S<k>), direction, timeframes used.
- Context condition, trigger, entry, stop, target, time stop: each a formula over pack columns only.
- Every parameter labelled SOURCED (quote + file:line from RULES_DIGEST) or OURS (with the reason).
- **Predefined numbers**, written before any count:
  - p(win) band, e.g. 0.40-0.50;
  - average win R and average loss R;
  - expected net R after cost = p*W - (1-p)*L - mean(14 bp / stop);
  - minimum trades to judge.
- Evidence from the LOOK window: 3-6 dated examples, including at least 1 loser.
- What must stay true in the future for it to keep working (e.g. "fees stay <= 14 bp"; "BTC keeps weekly value acceptance behaviour").
- Hindsight trap: what in the chart made this look good that a rule cannot know in real time.

## Rules for every Fable session
- Read only `pack/`, `RULES_DIGEST.md`, earlier `ANGLE_*.md` files and this brief.
- No internet, no data fetch, no scripts on data outside the pack.
- Do not use remembered BTC prices after 2023-06-30. If you notice yourself doing so, say so in the file.
- Do not edit code, PRE_REGs, VERDICTS.csv or the ledger.
- Stop when one of these happens:
  - the angle's file is complete (at most 3 items);
  - the Fable weekly meter has risen 3 points;
  - 30 tool turns.

  Run 4 as a whole is capped at 12 points; skip angle 4 if the cap is near.
- Ship with `python scripts/dev/sync.py ship`, with a Result line like `angle <n>: <k> setups, predefined net R <range>`.

## Operator does by hand (per angle)
1. Check that card fable-setups-pack-prep is done, and that the pack is on fast-track.
2. Open a new Code session in a worktree of the latest fast-track and pick Fable 5.1.
3. First message (change N):
   `Read MyTradingSys/system/fable_run_4_brief.md and do angle N only, exactly as written. No questions; use defaults. Pack files and earlier ANGLE files only.`
4. Note the Fable weekly meter before and after, and put both numbers in that session's last message.

## After angle 6 (Sonnet, card fable-setups-score)
1. Code the angle 6 shortlist, at most 8 setups, as functions over the same columns built for the BLIND window.
2. Add one trial-ledger row per setup before counting.
3. Run a count-only `prereg_gate.py` check with sd in R from each setup's own two-point bound.
4. Score on BLIND DEV against each stated p(win) band and net R, with angle 6's placebo.
5. Write a normal PRE_REG for each survivor for one VALIDATION read.
6. Post to DSA: `desk.py post "Fable run 4 scored" --target DSA`.
