# What the old layer backtests got wrong - register part 1 of 3 (Lead, 2026-10-26)
Source of this part: `MyTradingSys/research/BUGS.md` only. Rows were pulled by a Haiku reader (56 candidate rows), I re-opened 5 against the file (B075 :160, B103 :213, B147 :258, B151 :262, B154 :266) and all matched; the rest are copied, not individually re-opened. Status is the BUGS.md Status cell. CLOSED means the bug row was closed; it does not mean the layer was re-run, and no re-run number is recorded in these rows (NOT_IN_DATA; find with `grep -n "rerun\|re-run" MyTradingSys/research/BUGS.md`).
Not yet read for this register: DSA audit T01-T10, layer_lab reports, VERDICTS notes, fable/gap audits. Part 2 and 3 cover those. No keep/drop/park calls here.
Categories: BUG, UNVETTED_PARAM, FABRICATION, ASSUMPTION. "Could change a verdict" is NOT_IN_DATA unless the row says so.

## Backtest data and cost errors (touch every layer's numbers)
| ID | What was wrong | Cat | Status | BUGS.md |
|---|---|---|---|---|
| B075 | Historical mode zeroed trade_flow, book_imbalance, funding, OI and pulled live basis and OI into a past snapshot (look-ahead) | BUG | CLOSED | :160 |
| B081 | Four different fee sets in code for the same Deribit BTC perp | BUG | CLOSED | :172 |
| B103 | Backtest funding cost silently 0 outside the loaded funding range | BUG | CLOSED | :213 |
| B102 | Offline session models anchor NY/London at fixed UTC minutes, no DST, wrong by 1 h on about 40% of days | BUG | CLOSED | :212 |
| B044 | CVD and trade_flow built from a kline taker-buy proxy, not tick delta | ASSUMPTION | WONTFIX | :68 |
| B023 | Live and historical snapshot builders contradict on cvd_trade_flow_aligned | BUG | WONTFIX | :46 |
| B154 | No regime- or session-stratified verdict exists; every edge is one aggregate number | ASSUMPTION | OPEN | :266 |
| B187 | Price-level study blocked by a power gate it cannot pass on current data | UNVETTED_PARAM | OPEN | :302 |

## By layer
| Layer | ID | What was wrong | Cat | Status | BUGS.md |
|---|---|---|---|---|---|
| Tom | B146 | No minimum stop width: median stop 0.082%, planned gross R:R 79, fees dominate | BUG | CLOSED | :257 |
| Tom | B147 | Live-rule evidence unreliable: rerun gave 0 signals vs 19 earlier on same history; holdout read twice; Oct-7 run not on HEAD | BUG | CLOSED | :258 |
| Tom | B131, B085 | Proof-5 candidate pool skews 215 short : 105 long, baked in before any direction guard; residual cause unverified | BUG | CLOSED | :242, :196 |
| Tom | B084 | Origin of book_imbalance 0.0 in the Python proof block unverified; symptom fixed without a gate | BUG | CLOSED | :195 |
| CryptoCred | B143 | 0.1% stop buffer and 1.5R target have no source | UNVETTED_PARAM | BLOCKED | :254 |
| CryptoCred | B151 | Limit-fill backtest fills on touch and drops signals by a future event, so its PASS numbers are upper bounds | BUG | CLOSED | :262 |
| CryptoCred | B145 | filter_range_noise is off in the live layer; no evidence it is neutral | ASSUMPTION | CLOSED | :256 |
| Krown / levels | B141 | bal_4h / bal_1d null on every row: the balance rule holds in 0.4% (4H) and 0% (1D) of windows, so failed_breakout is null | UNVETTED_PARAM | OPEN | :252 |
| Fabio-style extra setups | B142, B039 | Stop is the previous 1m bar high/low with no trader source; momentum setup had no R:R gate | UNVETTED_PARAM / BUG | CLOSED | :253, :62 |
| Screener | B144 | Exhaustion proxy (volume 2.0x over 240 one-minute bars) has no source | UNVETTED_PARAM | OPEN | :255 |
| Callers | B139 | Analyst-rules adapter has no tracked item; candidates file never produced; analyst rules unbacktested | ASSUMPTION | OPEN | :250 |
| Every layer alert | B118 | auto_trader uses one fixed unsourced bracket (stop 1.0%, targets 2) for every layer alert | UNVETTED_PARAM | CLOSED | :229 |
| Every layer alert | T085 | 97% of testnet trades end on the time exit | BUG | OPEN | :187 |

## Engine-gate errors (affect which setups a core verdict allows)
B116 unsourced 0.1% min stop and 0.2% fallback stop (:227, CLOSED); B117 unsourced proof bands 3 and 5 (:228, OPEN); B135 proof-count thresholds need re-check (:246, CLOSED); B153 net_rr floor 1.25 no source (:264, CLOSED); B070 UTC-00:00 open anchor and 0.75 slippage multiplier gated a verdict (:150, CLOSED); B074 rule-order dependence in Compute-Verdict (:159, OPEN); B071 fail-open proof direction (:154, CLOSED); B136 OI feed broken, snapshot reported OI flat 0.0 with HIGH confidence (:247, CLOSED); B054 cvd_aligned proof is direction-blind (:78, WONTFIX); B042 day_type with provisional thresholds (:65, WONTFIX).

## Also found
B163 (:276, OPEN): an operator-pasted "Setup Alpha / Setup Beta" handoff asked to be implemented and backtested; it is a request, not a layer result, listed so it is not mistaken for a tested strategy.

## Reading across the rows (OURS)
- The same three defects recur: stops and targets with no source (B116, B118, B142, B143, B146), costs wrong or missing (B081, B103, B151), and tests that read one aggregate number (B154, B147's repeated holdout read).
- Whether fixing any of these changes a DEAD or FAIL label: NOT_IN_DATA for every row above.
