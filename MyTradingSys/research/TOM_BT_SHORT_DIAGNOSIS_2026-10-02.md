# Tom core backtest: why all 19 SETUP_FORMING signals are short (diagnosis, 2026-10-02)

Session MTS-2026-10-02-1422Z-CLI-BLD-tom-diag. Read-only except `backtest/tom_bt_diag.py` and this report.
All numbers below come from `python MyTradingSys/backtest/tom_bt_diag.py` (script outputs saved beside the row cache).

## 1. Method used: A (replay with reason logged)

The row cache is complete (57 of 57 months, 120,892 rows; `tom_bt_run.py:31-32` skips months that already have a file, so it was not rebuilt).
`tom_bt_diag.py` filters the cache to the 320 rows with proof >= 5 (all are proof 5, none 6), re-reads only those snapshots from
`F:\MTS\data\tom_snapshots`, replays the exact two-pass path of `tom_bt.py:101-105`, and records `compute_verdict`'s `reason` (`verdict.py:138`).
Stage attribution comes from extra calls on a condition-stripped copy, so no verdict logic is duplicated. Runtime 2.2 s.

Two runs, because `math_object_builder.py` changed after the cache was built (cache files dated 2026-09-30 02:42 local; FROZEN.md:3 says the run used git HEAD 27dceb6 with an uncommitted tree):

| Run | math_object_builder.py | Replay vs cache | Output |
|---|---|---|---|
| PRE | 2d1f24d (HEAD minus 13295c8) | 0 mismatches of 320, 301 losses, 19 SETUP_FORMING | `F:\MTS\data\tom_bt\allshorts.diag.prefix.stdout.txt` / `.prefix.jsonl` |
| HEAD | d84fb83 (includes 13295c8) | 9 mismatches (all longs), 292 losses, 28 SETUP_FORMING | `F:\MTS\data\tom_bt\allshorts.diag.stdout.txt` / `allshorts.diag.jsonl` |

PRE reproduces the cache and the review's 320 / 19 / 301 exactly, so PRE is the measurement of what the cached backtest saw. The PRE run injects the 2d1f24d version of
the module (`git show 2d1f24d:MyTradingSys/runtime/math_object_builder.py`) through a scratch wrapper; the repo was not edited.

## 2. The 301 losses by reason and direction (PRE = what the cache saw)

| Verdict reason (verdict.py line) | Short | Long | Total |
|---|---:|---:|---:|
| `net_rr X < 2.0` (110-111) | 146 | 68 | 214 |
| `flow contradiction` (133-137) | 45 | 19 | 64 |
| `proof 5 contradicted` (122-123) | 3 | 9 | 12 |
| `broken below_val + CVD falling vs LONG` (129-130) | 0 | 9 | 9 |
| `broken above_vah + CVD rising vs SHORT` (131-132) | 2 | 0 | 2 |
| **Losses** | **196** | **105** | **301** |
| SETUP_FORMING survivors | 19 | **0** | 19 |
| Proof-5 rows | 215 | 105 | 320 |

HEAD, same table: losses 196 short / 96 long = 292; the only change is `proof 5 contradicted` long 9 -> 0. Survivors 19 short + **9 long** = 28.

## 3. Cross-tab: the four gates at verdict.py:122-137

The review (H1) said the 301 lost rows go to 122-137. That is wrong for most of them: 214 of 301 (71%) are removed earlier, at `verdict.py:110-111` (`net_rr_sanity` false), before any of those gates.

| Gate | PRE long | PRE short | HEAD long | HEAD short |
|---|---:|---:|---:|---:|
| 122-123 proof direction = contradiction | 9 | 3 | 0 | 3 |
| 124-125 proof direction = error (fail-closed) | 0 | 0 | 0 | 0 |
| 129-132 broken value-area + CVD | 9 | 2 | 9 | 2 |
| 133-137 flow contradiction | 19 | 45 | 19 | 45 |
| Upstream, not one of the four: 110-111 net_rr | 68 | 146 | 68 | 146 |

Gate 122-123 undercounts the damage because later gates overwrite its reason. The proof-direction detail measured directly (PRE, 320 rows, `build_math_object(...)["proof_direction_details"]`):

| Direction | Contradiction details (PRE) | Rows |
|---|---|---:|
| long | `book_imbalance ask-heavy vs LONG` only | 84 |
| long | `book_imbalance ask-heavy` + `last_3_delta=neg,neg,neg` | 21 |
| short | none | 178 |
| short | `last_3_delta=pos,pos,pos vs SHORT` | 37 |

**All 105 proof-5 longs were marked "contradiction" by the book-imbalance check; no short was** (0 of 215). After the 13295c8 guard, 84 longs are aligned and 21 still contradict through `last_3_delta` (HEAD run, same table).

Both net_rr and flow gates are direction-neutral in this data: net_rr passes 69/215 shorts (32%) and 37/105 longs (35%); every net_rr loss has `tier=trigger_ready`, `net_rr_sanity=False`, net_rr between 1.5 and 2.0 (script table "net_rr_sanity x tier x direction").
The flow gate hits shorts with `cvd_slope=rising` (45, all `price_vs_va=in_va`) and longs with `falling` (19), mirroring `verdict.py:134-137`.

## 4. Source check

- Dominant gate overall: `net_rr_sanity` (`verdict.py:110`), read from `top.math.net_rr_sanity`, set in Java at `SetupCandidatesBuilder.java:191` (`c.netRrSanity = c.netRR >= 2.0`) and emitted at `:257`. Not archive-specific; symmetric by direction.
- Dominant gate among 122-137: flow contradiction, reads `conditions.cvd_slope` (`verdict.py:128, 134-137`). That field is `cvdNode.get("slope")` at `MarketDataSnapshot.java:1111`, in the same conditions block as the archive placeholder at `:1130`. `l1_patch_mds.py:48-62` (derived `net_delta_*` and `cvd_trade_flow_aligned`) does not touch `cvd_slope`; the verdict gates never read `cvd_trade_flow_aligned`. So the L1 patch is not on this path.
- The bug path: archive snapshots emit `cond.put("book_imbalance", 0.0)` (`MarketDataSnapshot.java:1130`; live ratio defaults to 0.0 at `:214`) and every one of the 320 proof-5 rows has `proof.book_imbalance == 0.0`. Java treats 0.0 as "no data" (`SetupCandidatesBuilder.java:581`, `if (bookImbalance != 0.0)`). The Python proof-direction check did not.
- Fail-closed `proof_dir_of` default (`verdict.py:56-62`): produced 0 `proof_dir error` rows in 320 (table above). Not a cause.

## 5. Verdict

**Bug, already fixed in the working tree but not in the cached data.** In `math_object_builder.py` the LONG contradiction test treated `book_imbalance == 0.0` (the archive "no order book" placeholder) as ask-heavy (`_book < 0.33`), contradicting every long, while the SHORT mirror (`_book > 3.0`, now `math_object_builder.py:405`) is never triggered by 0.0. The asymmetry removed longs from SETUP_FORMING only. The guard `_book != 0.0` landed in 13295c8 (2026-10-02 14:28 +0530, titled "WIP partial, unverified"), after the cache was built (2026-09-30). The cached rows are therefore stale, and `TOM_CORE_BT.md` ("19 SETUP_FORMING", `TOM_CORE_BT.md:34,55`, short only) reflects the buggy code. Current code gives 28 (19 short, 9 long).
**Not explained by the bug:** the proof-5 population itself is 215 short : 105 long (67% short; ~6 sigma from 50/50), while proof 3 is 19,668 L : 19,828 S and proof 4 is 5,231 L : 5,536 S (cache). The verdict gates do not cause that skew. Cause not isolated: UNVERIFIED (see section 7).
Confidence: high (about 95%) that the book_imbalance asymmetry is the reason zero longs survived, because the replay reproduces the cache with 0 mismatches and the detail strings are measured. Medium-low on whether the remaining 19 : 9 split is "real" market structure or another asymmetry in proof construction.

## 6. Fix (not applied by this session)

The code fix already exists (HEAD, `MyTradingSys/runtime/math_object_builder.py:414`):
`            if isinstance(_book, (int, float)) and not isinstance(_book, bool) and _book != 0.0 and _book < 0.33:`
Pre-fix line (`2d1f24d:MyTradingSys/runtime/math_object_builder.py:412`):
`            if isinstance(_book, (int, float)) and not isinstance(_book, bool) and _book < 0.33:`
Remaining actions, for the supervisor/operator (this session may not do them): (a) regenerate the row cache, because `tom_bt_run.py:31-32` returns early for existing files, so move or archive `F:\MTS\data\tom_bt\*.rows.jsonl` first and re-run `rows`; (b) re-run `report` and mark `TOM_CORE_BT.md` headline N and "all short" as superseded; (c) gate 13295c8 properly (it is committed as WIP/unverified).
Related, not changed: the Python thresholds (`< 0.33`, `> 3.0`) differ from Java's proof thresholds (`> 1.5` long, `< 0.67` short, `SetupCandidatesBuilder.java:584`); provenance of the Python numbers is UNVERIFIED.

## 7. Unknowns (UNVERIFIED)

- UNVERIFIED: why proof 5 is 2:1 short while proof 3-4 are balanced. Not tested; would need the proof-component breakdown over all 120,892 rows, not only the 320.
- UNVERIFIED: whether the same 0.0 book_imbalance asymmetry affects lower-proof rows (WATCH variants in `TOM_CORE_BT.md`). The contradiction only caps SETUP_FORMING/WATCH (`verdict.py:122-125`), so WATCH-based sensitivity tables may carry it too; not measured.
- UNVERIFIED: that `MarketDataSnapshot.java:1111` sits inside the historical (archive) method and not the live one (the same line text also exists at `:293`); inferred from the neighbouring `:1130` archive placeholder.
- UNVERIFIED: how Java computes proof `cvd_aligned` (true in 320 of 320 rows) versus `conditions.cvd_trade_flow_aligned` (false in 36 of 320). Not read.
- UNVERIFIED: the "operator-approved 2026-09-30" claim in the 13295c8 code comment (SUPERVISOR_INBOX 22:30Z item 1); inbox not read.
- The 9 recovered longs and their outcomes were not simulated; this report makes no claim about edge.
- Stage columns in the jsonl (`stage0`, `stage1`) use the condition-stripped copy; they attribute loss stage, not an independent verdict.
