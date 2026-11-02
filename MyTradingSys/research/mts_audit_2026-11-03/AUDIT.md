# MTS alignment audit, 2026-11-03 (Supervisor B, operator order)

Read this turn: D7_ROADMAP.md, LAYERS.md, VERDICTS.csv, all open task cards, LAYER_REALITY_2026-10-25.md, INTEGRATION_MAP.md,
C26_REVALIDATION_2026-11-01.md, prob_dist_layer_brief, rsi_deep_buy PROB_REPORT, kurisko BLOCKED.md, pitchfork study and its Opus review, OPERATOR_DECISIONS tail.
Not read: each result behind each row (rows quote the registers). Not checked by anyone else yet: this file (card `mts-audit-1103-independent-recheck`).
Labels: MEASURED = I ran it this turn. REGISTER = quoted from the named file. OPINION = my reading, OURS.

## 1. Verdict
Not aligned. The machinery works and bad ideas die cheaply, but nothing is ready to trade and the current rules cannot produce a unified system.
- 0 setups promoted (D7_ROADMAP.md: promoted_setups.json empty; LAYER_REALITY: no layer AHEAD). Live numbers: NOT_IN_DATA (`live_mirror.py brief`: owner unconfirmed).
- VERDICTS.csv, 117 rows (MEASURED count): 54 FAIL, 40 INCONCLUSIVE, 13 UNPARSED, 8 BLOCKED, 2 PASS. Both PASS rows are funding carry, not a directional layer.
- Roadmap: says stage S0 since 10-30, with S3's first pass or fail due 11-14. S0 exit not met (MEASURED: 22 ready cards against <= 15). No signed `q-v1-bar` or `q-v1-layers` section found in OPERATOR_DECISIONS.md, so S1 looks unsigned.
- S3 run list state (REGISTER): 1 meta-label 1h FAIL; 2 Fabio C marginal PASS, now doubtful (Argon: PASSED with n 139 < 401, bh_q 0.0233 vs 0.0465); 3 LC validation not read; 4 CryptoCred 4h/1D blocked by power gate; 5 RSI deep-buy run not done; 6 Tom v2 gross-first FAIL; 7 reclaim INCONCLUSIVE.
- Commits, 7 days, on trunk (MEASURED, crude first-match subject classifier): 2,468 total: 885 bookkeeping (36 %), 384 layer research (16 %), 153 audits, 249 ops, 98 reverts or re-lands, 21 CI red fixes, 678 other.

## 2. The worst finding: a false PASS sat on the board for 15 days
The Pitchfork 4H PASS (+0.61 %, PF 1.63) is not real on this data. MEASURED: `pitchfork_recheck.py`, 2020-01..2024-06 only, VALIDATION and HOLDOUT cut at load, tests `test_pitchfork_recheck.py`.
Faults in `run_pitchfork_4h_poc_study.py`: (a) it uses the final pivot list, where a low later undercut is rewritten, so failed entries vanish: 929 setups in the record against 1,205 knowable at the time; (b) it can fill on the confirmation bar, before the pivot is known; (c) it skips the stop check on the fill bar; (d) on one 4H bar it scores target before stop.

| Modified Schiff + VA, mean net per trade | n | mean | 95 % CI | win % | PF |
|---|---|---|---|---|---|
| STUDY rules (reproduces its 39 % win rate) | 205 | +0.748 | +0.241..+1.418 | 39.0 | 1.77 |
| CAUSAL pivots, same fills | 276 | +0.336 | -0.062..+0.890 | 33.0 | 1.32 |
| EXACT: causal, next-bar order, 1m walk, stop first | 272 | -0.011 | -0.336..+0.416 | 27.9 | 0.99 |
| Random-entry placebo, same side/stop/target | 100 runs | -0.109 | p95 +0.116 | | |

Other EXACT cells: Modified Schiff unfiltered -0.228 (CI -0.380..-0.052, n 818); Standard Andrews unfiltered -0.119 (n 935); Standard + VA +0.038 (CI -0.405..+0.536, n 224). Same sign as these on 2020-21 and on DEV except Standard + VA.
Scope of this kill: this encoding only (4H, zigzag 4 / 3 %, 1.5 % stop, ML target, BTC). Limit fills at exact touch are still generous. VA lifts the mean by about 0.2 pp over unfiltered, inside noise: a filter idea, not a result. The operator's own charts (copy-paste forks) were never tested.
Why it matters more than Pitchfork: the study said "100 % complete and validated"; the Opus review of 10-28 caught the window problem (F2) but passed the scanner as causal and did not open this runner; a GPT/Gemini re-derive and a parameter audit followed; `layer_map` still says PASS with n=734 and 64.85 % win, while its own report says 279 and 39.07 %. Review checked reports against reports. Nobody re-ran the trade loop.

## 3. Review and testing: what is wrong
1. Audits count numbers, they rarely attack method. Blind reads returned 0 DIFF over 900+ numbers (commits 11-01). They prove copying is accurate, not that a result is true. The one method pass this week (Argon, 11-02) found real faults at once.
2. PASS labels can bypass the register: Pitchfork has no VERDICTS row, so no gate ever looked at it (LAYER_REALITY flagged this on 10-25; 8 days, no card).
3. Gates spend effort on form: most of the 98 reverts are lint or cost-inventory trips on research scripts. Keep the checks, but they should not cost a revert cycle per study.
4. Live and tested differ: 94 % of live exits are time exits, the live bracket was never backtested; turn_of_candle (DEAD) was 71 % of live alerts on 10-25 (LAYER_REALITY). No layer's live numbers compare with its test.
5. Rule to add (done, section 7): no PASS without a VERDICTS row, a causal replay test that plants a later-rewritten pivot, and one re-run by another model from the trade loop up.

## 4. Layers today (REGISTER unless marked)
| Layer | Ready to trade? | Evidence | Next, or why stop |
|---|---|---|---|
| Pitchfork | No | MEASURED above; live flag on but needs 15 4H bars, gets 3, never fires | Test the operator's forks; causal rule in the desk first |
| Four-oscillator scalp (Kurisko) | Untested | Sources say 4 stochastics, not RSIs. 1m/5m blocked on taker fee, no outcome read. 15m, 1h, maker entry never tried | New pre-reg (card); it needs a maker fill model or it is dead on fees |
| Malkan RSI 40/60 | No | Only 1h support looks stable; live trades events never tested | Context input |
| RSI deep-buy | No | Tables exist; 25.8 % of cells drift out of range on VALIDATION | Context tables by phase (unparked) |
| Krown | No | Recall 3 of 12; no DEV study | Run the 3 refined DEV cards |
| WaveTrend | No | Trigger no; OB at H1 leans holds | C1 v2, then filter only |
| Tom | No | Old encoding, VP return, gross-first near-band all fail on BTC | Only his other setups if a new reason appears |
| Fabio | No | v3 OOS -0.10 R; Model C PASS doubtful | Recheck card first |
| Levels confluence | No | DEV negative, VALIDATION unread | Read once to close it |
| CryptoCred | No | Fails 15m-1h; 4h/1D power-blocked | Low |
| Pizzino | Untested | Indicators built | pz-4 DEV backtest |
| C26 regime fade | Candidate | DOWN highs 60 % back to L1, n 30, seen data | The clearest live idea: Phase 3 forward test |
| Carry | Passes, not directional | +0.042 %, n 911 | Separate decision: real money question |
| Rumers, Jala, Michael, Habib, callers | No | Extraction or first counts | Keep going, per operator |

## 5. Archive (no more runs unless a card writes a new reason; nothing deleted)
| Direction | Proof | Scope |
|---|---|---|
| DAX chain | Abandoned, not disproven: SMOKE only, no FDAX bought (q11) | Open DAX-dependent cards dropped; F:/MTS/data/dax_* kept |
| RSI divergence as a trigger | 31 of 32 net negative; 1m t -73; C30 shorts lose 62 of 65 | Trigger only |
| CVD divergence as a trigger | 0 of 12 arms, rerun same | 1m/5m trigger |
| OI as next direction | 4 studies, coin flip | Direction only; size or context open |
| Ladders and martingale for expectancy | 3 negative runs; no edge created | Structure as an edge claim |
| Tom VP pivot and old BTC encoding | Holdout -0.32 R; no anchor beats placebo | These encodings |
| Q33 cross guidance, funding/CVD fade, session momentum, turn of candle, candle-close pooled | Registered FAIL or no edge | As encoded; note all used generic exits (INTEGRATION_MAP s3) |
| Chronos-Bolt forecast, fractal analogs F3/F4 | FAIL or no edge on DEV | These models |

## 6. Probability layer and how to unify (OPINION, to be proven)
State today: wanted since September, code in `backtest/prob_table.py`, zero evidence runs, no owner. Pieces exist unjoined: BB state map (ran 10-30), RSI tables, Eagle base rates, Q10 on 30 events. Its card stayed "blocked on data" although the map ran.
Why combining is stuck: a layer may join only after it passes alone as a trade (PROJECT_VISION:262). Context layers cannot pass as a stand-alone trade, and nothing has, so the rule deadlocks. Proposed:
1. Common shape: every layer publishes `state_at(ts, tf)` with causal tests. It stops being a trade rule of its own.
2. One table: state to forward distribution (P up/down, MFE and MAE quantiles, by horizon), against a matched baseline, per regime and timeframe. Probability is the common currency.
3. Decision is EV after fees from that distribution, never a raw probability (53.2 % hit rate lost 10 bp on candle-close). A trigger only times the entry.
4. New test for a context layer: does it shift the distribution, same sign on 2020-21 and DEV, then one VALIDATION read? No P&L needed alone. Trades still need fee-net OOS.
5. Refresh rule: 25.8 % drift against 5 % chance says static tables fail; condition on phase and rolling recalculation.
6. Simplify: roles CONTEXT, REGIME, LOCATION, TRIGGER, RISK, one layer per role (LAYER_CONFLUENCE_DESIGN). Layers reading one object count once.
Proof that would make or kill this: pooled log-loss and EV against baseline on 2020-21 fitted on DEV. If adding states does not beat the baseline there, unification by probability is wrong and we say so.

## 7. Applied this turn
- Pitchfork rows relabelled in layer_map and layer_index; VERDICTS row added; result cards corrected.
- D7: confluence removed from the freeze for DEV research; a PASS rule added. Live gates unchanged.
- Blockers lifted: S0 park on pitchfork-fixes-desk-python, rsi-deep-context-tables, pz-5 stays gated; false data block on bb-state-regime-tf-map; layer-state-snapshot-causal entry gate removed. DAX cards tom-probe-prereg, tom-probe-runner dropped.
- New raw cards: mts-audit-1103-independent-recheck, prob-layer-common-table, kurisko-quad-15m-1h-maker-prereg, pitchfork-operator-forks-causal, research-pass-needs-rerun-gate, research-lint-warn-not-revert.
Kept on purpose: testnet only, fee-net, frozen pre-reg before outcomes, one VALIDATION read, sealed HOLDOUT, look-ahead checks.
