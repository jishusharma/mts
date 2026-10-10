# B171 - imbalance indicator: implement, backtest, run on testnet (end to end)

Status: OPEN. Severity: HIGH (operator). Opened 2026-10-10.
Source: Control Room inbox oclzxu4fqt9d6b0rx1gr (requirement, 14:02Z), plus two pasted X-sweep answers gfu6dxifgkhsr3xaqxgn (marked Grok) and 5mdfbjfq4ctldfgnnuhk (marked Gemini); verbatim in MyTradingSys/system/OPERATOR_INBOX.md.

## Operator's words
> Get the profitable imbalance indicator in our Armory now now - implement -back test -  run on test net! End to end - high priority

## What the repo already shows (read 2026-10-10, do not re-derive)
- No profitable imbalance indicator exists in the Armory yet. T093 (4-12 h turn-of-candle imbalance on klines 2022-2026): NO REPLICATION, gross +0.5 bp vs 10 bp round-trip taker fee, sign flips by year. P4 quarter-hour imbalance (corrected 2026-10-08): NO REPLICATION. research/imbalance_2026-10-10/RESEARCH.md plus the Grok addenda: public X evidence of fee-surviving pure OBI/OFI on BTCUSDT perps is absent.
- The two pasted answers say the same: nothing found for maker/post-only/rebate; the only quantified claim (@polyquantai, Polymarket, no fees stated) is unverified, and @VelvetSoul's controlled test collapses to noise. Tier: T4 social claims, not usable as a source for parameters.
- The fee wall is the binding constraint, so any candidate must be pre-registered and carry its cost model.

## Plan (end to end, in order; none of it may skip a gate)
1. Pre-register candidates (PRE_REG_*.md, declared trial count) from sourced material only: operator-supplied trader quotes / transcripts. Unsourced parameters are NO-SOURCE and stay OPERATOR-EXPERIMENT grid cells, never tuned.
2. Backtest on hist+dev, holdout read once, fee-inclusive, maker-fill variant modelled only with the real queue assumption stated. Data limit: kline taker-buy proxy only; true book imbalance/aggTrades are not on disk, so a book-OBI test needs a capture first (check the live orderflow_1m `fp` files for what exists).
3. Only a candidate that passes the pre-registered criterion becomes a layer (separate layer, never a Tom filter), staged as .new under layers/.
4. Testnet run (Deribit test) of a passing layer is a supervisor/desk step: builders do not restart live processes, touch HALT or open trades.
If nothing passes, the honest result is NO-INFO recorded here, not a tuned indicator.

## Progress
2026-10-10: filed by Control Room pickup. Not started.
2026-10-10 ~17:00Z (relay Q3): step 1 NO-INFO. grep of all 113 raw_transcripts_canonical files for "imbalance" (72 hits): used only as auction-market balance/imbalance (value area, single prints, breakouts) and once as a colour-coded footprint buy/sell imbalance (oPyUif2Zrtk, "104 sales, 147 purchases ... large buying imbalance") with no ratio, window or threshold. No quote defines a testable rule, so no PRE_REG_imbalance.md. Control Room decision D24-imbalance-quote filed (default: park B171). No code, no backtest.
