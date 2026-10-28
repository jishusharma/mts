# SESSION 3 HANDOFF: Execution fast lane + backtest data layer
Date: 2026-09-27 · Author: Opus 5.5 (session 3, ran in parallel with session 2 / Sonnet)
Canonical path: MyTradingSys/research/core_readiness_2026-09-27/SESSION_3_HANDOFF.md

## 0. TL;DR
- **Opus review of executor.py is DONE.** This was the gate session 2 listed as "genuinely blocked." The file was rewritten, not patched (findings R1-R8 below).
- **T050 Phase 2 + Phase 3 are CLOSED on real Deribit testnet**, run from the cloud workspace with the operator's testnet key. The key has testnet equity of 100 BTC and no withdraw scope.
- **executor v2 testnet proof suite: 6/6 PASS** against the live testnet book. The account was left flat with 0 open orders after every case.
- **B077, B078, B079: FIXED and PROVEN on testnet.** These are staged as .new files, and session 3 did NOT touch BUGS.md, to avoid colliding with session 2's BUGS.md.new. Session 2 or the next session records the status.
- **Backtest data layer chosen and built:** data.binance.vision (free, official, SHA256-verified). The downloader is tested. The next step is regenerating snapshots from raw data (spec in section 4).

## 1. Staged files (operator: diff, rename .new -> real, commit)
All five files live in the repo next to their targets. **Rename all three execution files together.** executor v2 imports the v2 names (`stop_market`, `cancel_by_label`, `get_ticker`).

| Staged file | Target | What changed |
|---|---|---|
| execution/deribit_orders.py.new | deribit_orders.py | POST JSON-RPC (the secret is no longer in the URL query); token auto-refresh; `stop_market()` (B077); `cancel_by_label()` via server-side private/cancel_by_label (B078, and the old name is now an alias of the safe call); `get_position`, `close_position`, `get_ticker` |
| execution/executor.py.new | executor.py | full rewrite, invariant-driven (see section 2). Refusal guard replaced by `--go` (dry run by default) |
| execution/plan_compiler.py.new | plan_compiler.py | one line: the fixed stop's order_type is now `stop_market` (it was `limit`) |
| execution/testnet/run_testnet_suite.py.new | testnet/run_testnet_suite.py (new dir) | the 6-case proof suite (section 3) |
| backtest/fetch_binance_archive.py.new | fetch_binance_archive.py | bulk history downloader (section 4) |

## 2. executor.py review findings (fixed in v2)
Invariant: **from the first filled contract, a server-side reduce-only stop_market covers the full filled size, or the position is flattened and the run halts.**

| # | Severity | v1 behaviour | v2 |
|---|---|---|---|
| R1 | CRITICAL | stop placed only after ALL entries left `open`, so a filled ladder rung sat unprotected for up to 10 min | stop placed on the first fill; `edit` resizes it on every new fill |
| R2 = B077 | CRITICAL | stop was a reduce-only LIMIT, which fills instantly on the wrong side | `stop_market`, trigger=mark_price |
| R3 = B079 | HIGH | `caps_check.within_max_loss` computed, never enforced | enforced pre-flight; market entries estimated pre-flight and re-checked on the real fill |
| R4 | HIGH | trailing/breakeven stop found "unimplemented" only AFTER the fill, leaving a naked position | refused pre-flight, before any order |
| R5 | HIGH | poll timeout raised while the position was still live | on the deadline (min of max_entry_seconds and validity.end), unfilled entries are cancelled and the protected position is kept |
| R6 = B078 | HIGH | label cancel wiped every BTC order | exchange labels are `<plan_id>:<label>`, cancelled server-side by label |
| R7 | HIGH | no recovery if the stop failed | stop fails, so cancel entries, `close_position`, then halt (fail-closed) |
| R8 | MED | no pre-existing-state check | refuses if the instrument already has a position or open orders; refuses a re-run of the same plan_id (journal exists) |

Design ruling (the question v1 left for Opus): **REST polling is sufficient for T050.** The stop lives server-side, so polling latency only delays stop RESIZING, never stop EXISTENCE. WebSocket is deferred to T048 satellites.

Stop price rule: limit/ladder entries use the compiler's static stop (the price the cap was checked against). Market entries use the plan percent off the real average fill.

**Known gaps (not blocking testnet; they block LIVE):**
- G1 Post-entry management is absent: the stop is not shrunk when targets fill, and there is no breakeven or trailing. reduce_only prevents a reverse position, but whether Deribit clamps an oversized reduce-only stop_market at trigger time is **not yet verified on testnet**. Add a suite case: target fills, then the stop triggers.
- G2 reconciler.py is still v1. Its forced-mismatch exit test ("close by hand in UI -> detect -> halt") has not been run. Its position model ignores stop/target fills (its own comment says so).
- G3 The `order_filled` journal now also carries `average_price`. The journal holds short labels; the exchange holds prefixed labels.
- G4 Testnet price and liquidity are not mainnet, so fill-quality numbers from testnet mean nothing.

## 3. Testnet evidence (2026-09-27, ~07:10-07:20Z, mark ~84.5k)
Raw primitives: far post-only limit placed, queried, then cancel_by_label worked (open -> cancelled). B078 isolation: two labels, one cancelled, the other still open. Market 10 USD filled; stop_market untriggered with reduce_only=True, trigger=mark_price; target limit and stop coexist (reduce-only total 20 > position 10 is accepted); `edit` moved the trigger; close_position flattened.

Suite (`run_testnet_suite.py`), 6/6 PASS:
- C1 market long 100: pos 100; stop_market 100 below fill; targets 50+50
- C2 market short 100: pos -100; buy stop above fill
- C3 4-rung ladder with rung 1 marketable and a 12 s deadline: rung 1 protected immediately; rungs 2-4 cancelled; pos 10 = stop 10
- C4 pre-flight refusals: B079 limit cap, B079 market estimate, trailing stop, R8 dirty account. All refused, nothing placed.
- C5 exchange rejects the stop after a fill (forced): flattened, halted, pos 0
- C6 same plan_id re-run: refused (idempotency)

## 4. Backtest data decision (T051 v2)
**Problem:** the archived-snapshot corpus is about 2 weeks (9.2k snapshots). After D1+D4, SETUP_FORMING is about 23 signals. That is statistically useless for validating the engine layer by layer.

**Decision:** regenerate snapshots from raw exchange history, and use the archived live snapshots as the parity oracle.

**Source: data.binance.vision** (free, official, SHA256 per file, same venue/symbol as MTS signals). Verified today:

| dataset | MTS input | availability |
|---|---|---|
| klines 1m (incl. taker_buy_volume) | price path, structure, VWAP, **CVD exact at 1m** (delta = 2·taker_buy − volume) | 2020+ |
| aggTrades | exact VP / CVD | 2020+, ~0.1-0.3 GB/day zipped, opt-in |
| metrics 5m | OI, OI trend, long/short ratios | 2021+ |
| fundingRate | funding | monthly files only; current month appears after month end (use REST for it) |
| bookDepth | ±1..5 % depth bands every ~30-60 s: **proxy only** for book_imbalance | 2023+ |
| markPriceKlines 1m | stop triggers (Deribit stops trigger on mark) | 2020+ |
| Deribit get_tradingview_chart_data | fill-side prices/basis | free public API, verified reachable |

Size without aggTrades is about 2.3 MB/day, so about 850 MB for 12 months. Paid alternative: Tardis.dev (tick L2 incl. Deribit native). Only consider it if the bookDepth proxy fails the parity gate. Pricing not verified.

**Pipeline and gates (for Builder/Sonnet; do not skip gates):**
1. **L0 data:** `python MyTradingSys\backtest\fetch_binance_archive.py --start 2025-09-01 --end 2026-09-26`. Add `--datasets aggTrades` only for the parity window 2026-09-13..26 at first.
2. **L1 snapshot regeneration:** add a *file-source* adapter to Java historical mode. It reads raw CSVs strictly up to candle close t, with no live calls. This also fixes the known look-ahead / zeroed-flow bug (plan Phase D). **Gate P1:** regenerated snapshots for 2026-09-13..26 must match archived live snapshots on Tom core steps 1-8, using the existing harness (118/118 candidates, 1652/1652 fields). Any field without a raw source is emitted as null plus `"source":"unavailable"`, never zero.
3. **Gate P2 (book proxy):** compare bookDepth-proxy imbalance vs archived book_imbalance on the overlap window and report the sign agreement %. If it is below the threshold the operator sets, run every backtest twice: with the proxy, and with book signals excluded from the proof count.
4. **L2 verdict replay:** verdict.py (after C1/D1 revert and C3/D4 directional count) over the regenerated 12 months.
5. **L3 trade sim:** sim.py switched from 60 s snapshot prices to 1m klines (stop-first when both hit in one bar). Stops are evaluated on markPriceKlines. Deribit fees stay. Report basis against Deribit chart data.
6. **L4 execution sim:** feed plan_compiler outputs (ladder fixed-fixed-double-triple etc.) through the same 1m engine. A rung fills if low ≤ rung (long).
7. **Discipline:** freeze rules before running. Hold out the last 3 months untouched until the rules freeze. Report Wilson CIs (already in sim.py).

## 5. Operator steps, in order, one at a time
1. Diff and rename the 5 .new files (section 1). Commit.
2. With the testnet UI open: `python MyTradingSys\execution\testnet\run_testnet_suite.py`. Expect `6/6 PASS` (about 1-2 min, self-cleaning).
3. `python MyTradingSys\backtest\fetch_binance_archive.py --start 2025-09-01 --end 2026-09-26` (desktop or NUC).
4. Still open from session 2: A2-A4 (core_check.ps1, Maven Java replay) need your pwsh+Maven once.

## 6. Next session: task list and model
**Model: Sonnet 5** for execution (per the Opus-designs / lower-models-execute split; every task above has a gate). **NUC builder (qwen3-coder:30b):** mechanical pieces only (L3 sim port to 1m bars, L4 ladder sim, CSV loaders), each with a unit test the builder must pass. **Opus 5.5** only for: C3 Java directional-proof review, the L1 file-source adapter design review, and G1/G2 before any mainnet key.

Next session queue:
1. Record B077/B078/B079 as fixed-staged in BUGS.md / items/INDEX.md (after session 2's BUGS.md.new is resolved).
2. G1 suite case (target fill, then stop trigger) and G2 reconciler v2 plus its forced-mismatch test on testnet.
3. C1 (D1 revert) in verdict.py + start-trading-day.ps1; C2/C3 Java (needs the operator's Maven).
4. L1 file-source adapter plus gates P1/P2, then L2-L4.

## 7. Security note
The testnet key was read into the cloud workspace to run the suite, and deleted from it after the run. That departs from execution/README's "no AI reads .secrets" convention, done at the operator's fast-lane instruction. It is testnet-only, with no withdraw scope. Rotating it is optional and cheap.
