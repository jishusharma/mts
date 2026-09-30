# ANGLE: pre-registered competing hypotheses - why Tom-engine output does not match the traders' trades

Opus scientist, 2026-09-30, cloud sandbox (no F: data, no exchange access). Read-only on the repo except this file.
Tom is core; Fabio and every other trader stay separate layers. Nothing here proposes a filter on Tom.
Scratch (outside the repo): `opus_hyp/` in the session scratchpad: `t1_sym.py`, `t2_shape.py`, `mk_snaps.py`,
`src/datafeed/T3Harness.java`, `t3_out.txt`.
Overlap note: another Opus agent is tracing the no-longs code path in full. E-001 below is deliberately one small
falsification test, not a trace. If both reports name the same line, treat that as two independent reads, not new evidence.

## 0. Results produced here

**RESULT (2026-09-30, cloud sandbox) E-001, H-gate-book: CONFIRMED at code level.** In archive mode, every LONG
that reaches proof 5 is downgraded to WATCH. No SHORT is.
- The chain, read from code:
  - `MarketDataSnapshot.java:1169`: the archive path writes `order_book_depth.bid_ask_ratio = 0.0`.
  - `SetupCandidatesBuilder.java:819` reads it, and `:619` emits `proof.book_imbalance = 0.0`. `countSignals` skips 0.0,
    so the proof count itself is symmetric.
  - `math_object_builder.py:402` tests `_book < 0.33`, which is true for 0.0, so a LONG gets
    `"book_imbalance=0.0 ask-heavy vs LONG"`. The short-side test (`:395`) is `> 3.0`, false for 0.0.
  - `verdict.py:122` then turns SETUP_FORMING into WATCH. `tom_bt.py:104` uses `proof_dir_of(fail_closed=True)`, so the
    backtest takes this path.
- The run: `t1_sym.py` pushes mirror-image snapshots through the real `proof_dir_of(fail_closed=True)` and
  `compute_verdict`. Fixed inputs: price 100000, `daily_poc` zone at 100000, tier `trigger_ready`, net_rr 2.2 with sanity
  true, proof_count 5, finished-auction direction "", `last_3_delta` [pos,neg,pos], conditions in_va, cvd_slope flat.
  Only the direction and the book value change.

| book_imbalance | long | short |
|---|---|---|
| 0.0 (archive default; also live fetch failure) | contradiction -> WATCH "proof 5 contradicted" | aligned -> SETUP_FORMING |
| 1.0 | SETUP_FORMING | SETUP_FORMING |
| key absent (builder default 1.0) | SETUP_FORMING | SETUP_FORMING |
| 3.5 | SETUP_FORMING | contradiction -> WATCH |
| 0.2 | contradiction -> WATCH | SETUP_FORMING |

- This fits TOM_CORE_BT exactly. WATCH episodes are balanced (long 2450, short 2399; p4 484/499), because the
  contradiction only demotes SETUP_FORMING. SETUP_FORMING is 19 of 19 short.
- Consequence: the live-rule N (17 filled) and "insufficient N" measure an archive artefact, not Tom.
- **The same asymmetry exists LIVE.** `MarketDataSnapshot.java:213-214`: a failed order-book fetch keeps depth 0, so the
  ratio is 0.0 and every long top candidate is contradicted in that snapshot. The safety check fails closed for one side
  only. PROPOSAL ONLY; this file touches nothing in the live path. The owner of execution/ decides.
- This does not explain the missing edge. The watch-level longs and shorts are both about -0.07R gross.

**RESULT (2026-09-30, cloud sandbox) E-002, H-label (TWOPEAK): CONFIRMED as heuristic, not concept.**
- `t2_shape.py` ports the shape rule at `MarketDataSnapshot.java:570-586` line for line: second = largest bin below the
  max, TWOPEAK if second > 0.6*max, else D or P by the left/right volume ratio. The port runs on 200-bin synthetic profiles
  whose true shape is known.
- Output: a unimodal gaussian with sigma 0.8 bins gives D. Sigma 1.0, 1.2, 3, 10 and 40 bins all give TWOPEAK. So do a
  bimodal profile, a P-shaped profile and a b-shaped profile of width 10 bins.
- Only 1-bin spikes escape, and then both P- and b-shaped spikes print "P". The code has no "b" label.
- Algebra: for a gaussian the neighbouring bin exceeds 0.6*max iff sigma > 0.989 bins. The "second peak" is almost always
  the POC's neighbour, so any profile wider than about 1 bin reads TWOPEAK.
- `vp_shape` is not read by `classifyState`. So this explains "the alerts look alike" (display, `mts_math.py:166-172`,
  and the DSA reading of it). It does not explain trade selection.

**RESULT (2026-09-30, cloud sandbox) E-003, H-param gate replay: Tom's own documented trade cannot be produced.**
- The harness is `T3Harness.java`. It calls the unmodified `SetupCandidatesBuilder.build` (copied, compiled with
  jackson 2.17.2) on the synthetic snapshots from `mk_snaps.py`.
- Snapshot setup: price 100000, balance state, daily VAH (short) or VAL (long) at price, 15m swing = the stop, weekly POC
  = the target, all other levels far away.

| case | geometry | output |
|---|---|---|
| A short | Tom yRvMW6lgN1o scaled by percent: stop 0.044%, target 0.36% (8.1R) | the VAH candidate is DROPPED (the 0.1% floor resets the stop to 0.2%, the target becomes 1.8R < 2.0). The only survivor is the 15m_swing_high zone itself, with a fallback stop at 100244.09, gross 2.02, net 1.51, net_ok false = WAIT_RR |
| E long | mirror of A | mirror output (swing_low zone, gross 2.02, net 1.52, WAIT_RR) |
| B short | Tom R:R at BTC scale: stop 0.30%, target 2.43% (8.1R) | 0 candidates (the target is beyond the 3.5R window) |
| C short | control: stop 0.30%, target 0.90% (3R) | daily_vah ct_short, gross 3.0, net 2.25, net_ok true |
| D long | control mirror | daily_val ct_long, gross 3.0, net 2.25, net_ok true |

- So candidate generation is symmetric for this pair (C/D). Tom's trade is unproducible at ES scale (A) and at his R:R
  (B), by the floor and the window alone. This is one trade (n=1), so it is an existence proof, not a rate.

**RESULT (2026-09-30, cloud sandbox) R-004, code read (grep).** `SetupCandidatesBuilder.java`, `verdict.py` and the
proof-direction block of `math_object_builder.py` never read funding, open interest, basis or liquidations. The only
hit is `post_funding_vp`, which is demoted. For the CORE verdict, H-data therefore reduces to book imbalance.
Funding and OI can matter only through layers or live operator reading.

## 1. Experiment log format (pre-registration)
Proposed file: `MyTradingSys/research/EXPERIMENT_LOG.md`, one block per experiment, append-only.

Rules:
- Fields 1-9 are committed BEFORE the run, and the commit hash goes in field 10. After that they are never edited. A
  change means a new ID with `supersedes:`.
- The result block is appended. Deviations from the plan are listed, never hidden.
- Every run that looks at outcome data adds a row to `bt_runs/TRIAL_REGISTRY.csv`. Fix the dedupe key: it is run_id =
  date today (REVIEW M9), and it should be run_id + git hash + config hash.
- Numbers in the prediction come from FORMULAS.md or from stated algebra, never from the code under test.

```
### E-NNN  <short title>
1  hypothesis:   H-<family>-<n>, one sentence, causal
2  competitors:  which other H's this test separates it from, and what each of them predicts here
3  prediction:   observable + direction + threshold (e.g. "long SETUP_FORMING >= 5 when book is neutralised")
4  falsifier:    the exact observation that kills the hypothesis
5  test:         code path@commit, data path + date range, inputs/config, trial-count increment
6  runner:       cloud now | desktop F: snapshots | desktop live logs | NUC ; tier T0-T4
7  cost:         wall time + model tier + operator minutes
8  decision rule: pre-stated alpha / CI rule / count rule; what counts as INCONCLUSIVE
9  if confirmed / if falsified: the action in each case
10 registered:   date, session, commit hash of this block
--- RESULT (appended) ---
11 run:          date, environment, exact command, output file
12 observed:     raw numbers (no rounding beyond 2 dp), n, CI
13 deviations:   anything that differed from 5-8
14 verdict:      CONFIRMED | FALSIFIED | INCONCLUSIVE (+ which competitor gained)
15 decision:     action taken, owner, follow-up E-IDs
```
Honesty note on E-001..E-003: they were written in this session just before running, and they were not committed
first. They are therefore NOT valid pre-registrations. They are logged as exploratory, and the desktop tests below
(E-101 onward) are the confirmatory versions.

## 2. Hypotheses
Each entry gives the claim (C), prediction (P), falsifier (F), cheapest test (T), runner and cost (R), and what we do if
confirmed (A). "Watch set" means the 4417 filled WATCH+SETUP_FORMING episodes in TOM_CORE_BT (proof >= 3).

### H-gate: asymmetric or fail-closed gates remove one side
- **H-gate-1 (book zero -> long contradiction).**
  - C: the 0.0 book value alone causes the 19/19 short split.
  - P: every long top-candidate row with proof 5 in the F: snapshots has `proof_direction_details` containing
    "book_imbalance=0.0 ask-heavy vs LONG". When the book value is replaced by "absent" (neutral), long SETUP_FORMING
    goes from 0 to >= 5. The long share of SETUP_FORMING then lies inside the watch-set Wilson interval of the long share
    (2450/4849 = 50.5%).
  - F: some proof-5 long row lacks that detail and is still not SETUP_FORMING, or the neutralised rerun still gives
    0 longs. Either means a second long-killer exists (the flow contradiction at `verdict.py:131-135`, or
    `last_3_delta`).
  - T (E-101): stream `F:\MTS\data\tom_snapshots\*.gz` and, for each row, call `snapshot_to_row` twice: as-is, then with
    `setup_candidates[*].proof.book_imbalance` deleted. Tabulate verdict x direction x reason, and the 301 lost proof-5
    rows by reason (this also closes REVIEW H1). No new trades are simulated, so no trial row is added.
  - R: desktop F:, T0 script, about 20 min plus a 15 min Sonnet write-up.
  - A: correct the archive default in the backtest adapter only (book -> absent, not 0.0), then rerun the live-rule
    variant as a new registered trial. Hand the live fetch-failure side to the execution owner as a proposal
    (fail closed for BOTH sides, i.e. a WAIT_PROOF "book unavailable", with a restart/API-error test as the hard rules
    require).
- **H-gate-2 (live mirror).**
  - C: live snapshots with a failed book fetch silently block longs.
  - P: `runtime_data` snapshot logs contain rows with bid_ask_ratio == 0.0. In those rows every long top candidate is
    contradicted, and no short is.
  - F: no 0.0 rows in the live logs (the fetch never fails), or 0.0 rows with longs not contradicted.
  - T (E-102): parse the live snapshot/apparatus logs (real JSON, not a grep of a tail) and count ratio == 0.0 by day,
    and the long verdicts in those rows.
  - R: desktop live logs, T0, 10 min.
  - A: raise the proposal in E-101/A to the SUPERVISOR_LOG with the counts.
- **H-gate-3 (the gate stack is too deep, whatever the side).**
  - C: even after H-gate-1 is fixed, AND-stacking (net_rr window, tier, proof >= 5, no contradictions) leaves N < 100
    in 4.7 years.
  - P: the corrected live-rule N stays < 100.
  - F: N >= 100.
  - T: the same run as E-101 with the neutralised book.
  - R: included in E-101.
  - A: the protocol cannot judge the live rule on history; judge it on live testnet with a pre-set stopping rule.

### H-data: inputs missing in history
- C: book imbalance, funding, OI and basis are absent from the archive, and their absence (not the rules) keeps history
  unlike live.
- P: given R-004, only book imbalance enters the core verdict. Removing it from LIVE snapshots changes
  SETUP_FORMING <-> WATCH in a material share of live rows (> 20%) and flips direction balance.
- F: neutralising book in live snapshots changes < 5% of live verdicts. History then lacks nothing the core uses, and
  H-data is dead for Tom core.
- T (E-103): take the live snapshots (they have a real book). Recompute verdicts three ways: as-is, with
  `book_imbalance` deleted, and with it set to 0.0. The third reproduces the archive and should re-create the
  all-short bias.
- R: desktop live logs, T0, 20 min.
- A: if material, buy or archive order-book history (a recorder job on the NUC). If not, stop citing "missing proofs" as
  the reason for low N. Funding and OI stay a layer question, not a core one.

### H-param: thresholds exclude the traders' geometry
- C: the 0.1% floor / 0.2% fallback stop, the [2.0, 3.5]R nearest-target window, net = 0.75*gross >= 2, and proof >= 5
  remove exactly the trades the traders take.
- P: when every Tom walkthrough trade that has stated stop and target is replayed as a synthetic snapshot through the
  builder, >= 70% produce no candidate with net_ok true. On F: data, the fallback stop share of watch-set trades is
  >= 50%.
- F: most replayed trades survive with the trader's own stop and target. Or the fallback share is < 20%, in which case
  the 0.200% median stop is a coincidence.
- T:
  - E-104 (cloud now): extend T3Harness to all Tom trades with ticks in extracts/fresh and TOM_VERBATIM_INDEX (for
    example TOM-094: 10 ticks / 70 ticks). Scale each two ways, by percent and by ATR ratio. Expected numbers come from
    the trader's stated ticks, not from our code.
  - E-105 (desktop F:): add `stop_src` (swing | fallback | floor_reset) to the row and count it.
- R: E-104 is cloud, Sonnet, about 1.5 h. E-105 is desktop, T0, 15 min.
- A: do NOT loosen the thresholds on the backtest (that is a trial). Pre-register a Tom-geometry variant: stop at the
  in-range max-volume level, target at the prior-week POC with no 3.5R cap, and a stop-width-dependent fee instead of the
  flat 25%. Run it once, as a new trial.

### H-unit: the edge lives in whole trades or days (management), not in entry rules
- C: entries are near-random. The traders' P&L comes from payoff shape: a rare large winner, stop to zero then adds
  (Fabio), and letting a trade run (Tom). Our fixed [2, 3.5]R exit and the no-BE/no-trail rule cut that off.
- P: on the watch-set entries, MFE in R has a fat right tail. The share of trades that reach >= 8R before -1R
  (within 24 h) beats the fair random-limit null's share by >= 3 percentage points. For reference, a driftless walk
  with no time cap reaches +aR before -1R with probability 1/(1+a), which is 11% at a = 8; the 24 h cap makes the null
  share lower, so the comparison is against the measured null only. Payoff variants (uncapped target at the next HTF
  level, BE at +1R) raise mean gross R versus the fixed exit by > 0.05R.
- F: the MFE distribution matches the random-limit null (KS p > 0.2). All exit variants stay within +/-0.03R of each
  other and of the null. Management cannot create what entries lack, and H-unit is falsified.
- T (E-106): on the F: 1m archive, recompute MFE/MAE for each watch-set entry up to 24 h. Evaluate 4 pre-declared exit
  policies (fixed 3R, next-HTF-level, BE at 1R, trail by 15m swing) against the REVIEW H2 fair null: a random limit at
  the same side and distance, same fill/ran rules.
- R: desktop F:, Sonnet script plus a T0 run, about 3 h. This adds 4 trial rows.
- A: move evaluation to trade and day units, and write the management rules as Tom-core exit logic (plan rule change,
  operator decision). If falsified, the traders' edge (if any) is in selection the engine does not see. Go to H-extract
  and H-label.

### H-extract: the extractions distorted the rules
- C: rule rows lost order, conditioning and sign (the FAB-jasv3L-d8ZE-R5 inversion; DSA 999 ticked with no output). The
  engine implements a different system from the one in the videos.
- P: a blind second extraction (different model, trade-reconstruction template from MISSING_PIECES section 3.2) of
  5 Tom videos disagrees with the conditions/ master on >= 20% of rules that touch stop, target, entry or order type.
  At least 1 more sign inversion appears.
- F: agreement >= 90% on those fields and no inversion. The rules are faithful and the gap is elsewhere
  (H-param or H-port).
- T (E-107): pick 5 Tom videos that already have extracts. Haiku re-extracts blind to the master. Run
  `verify_extract_quotes.py` on each. A Sonnet diff counts disagreements per field. Tests come from Haiku or Sonnet, per
  the routing rules.
- R: cloud now, T2/T3, about 2 h.
- A: freeze rule-row use for builders. Every rule needs a trade reconstruction plus a gate replay (E-104) before it can
  reach code.

### H-port: ES/NQ/DAX methods do not transfer to BTC at these horizons and costs
- C: even a faithful port fails. The traders' stops are about 0.04% (ES ticks). At Deribit fees a BTC stop that tight
  costs >= 1R, and BTC's 5m noise at that width is higher relative to structure.
- P: in trader units, stop/ATR(5m) for Tom's ES trades (from the stated ticks and an ES ATR) is well below the BTC stop
  that keeps fees <= 0.1R, i.e. about 0.5% (algebra: 5 bps taker / 0.1R). Once scaled to the same stop/ATR on BTC, mean
  gross R on Tom-geometry entries is <= 0 against the fair null.
- F: Tom-geometry entries scaled by ATR show gross > +0.1R with a CI above 0 against the fair null. The method ports,
  and the loss is in parameters or labels.
- T (E-108): runs after E-104 and E-106. Scale by ATR, not by percent. ES ATR comes from a cited public source or
  operator data. BTC ATR comes from F:.
- R: desktop F:, Sonnet, about 2 h. ES data is not in the repo, which is an open dependency.
- A: stop porting tick geometry. Keep Tom's LOCATION logic (VA plus single prints, the last volume step) and re-derive
  width and target on BTC volatility as a registered, BTC-native variant.

### H-label: our labels (TWOPEAK, setup types, state) are heuristics, not the trader's concepts
- C: `vp_shape`, `classifyState` and `determineSetupType` encode screener heuristics. The trader's B, P and D profiles,
  inside day, weekly balance and "smart S/R" are never computed. The engine therefore conditions on different states.
- P: the F: snapshots show TWOPEAK >= 90% for daily and weekly profiles (E-002 predicts this). Hand-labelled Tom states
  (operator or Sonnet reading the chart, blind to our labels) agree with `classifyState` at kappa < 0.4.
- F: TWOPEAK < 60% on real data (E-002 does not transfer to real profiles), or kappa >= 0.6.
- T:
  - E-109a (desktop F:, T0, 10 min): count `conditions.vp_shape` and `weekly_vp.shape` over the 120892 rows.
  - E-109b (desktop, Sonnet plus operator, about 2 h): 50 random snapshot times, labelled blind with Tom's vocabulary.
- A: rebuild the shape labels from Tom's definitions (a top-heavy B, which is still "NOT YET COMPUTED" at
  compiled_engine.md:332, and P/b/D by the POC position within the range) as a spec with FORMULAS.md tests, before any
  alert text uses them.
- Note: `determineSetupType` is also asymmetric in the long direction. There is `tc_long` and no `tc_short`. VAH shorts
  are nulled in trend_healthy, VAL longs are not (`SetupCandidatesBuilder.java:439-465`). This is a label/spec issue, not
  a bias against longs.

### H-null (baseline comparator, needed to interpret all of the above)
- C: there is no exploitable edge at these horizons on BTC after costs, whatever the rules.
- P: every registered variant (E-101 corrected, E-104/106 geometry, E-108 ported) has net CI <= 0 and gross within the
  fair null.
- F: any pre-registered variant with OOS net CI lower bound > 0 and n >= 100 after the trial-count correction (DSR with
  N_trials from the fixed registry).
- T: the fair null of E-106, run with every variant.
- A: Tom stays core, as a location/context engine for discretionary live trading. Automation claims stay unproven.

## 3. Discrimination matrix (what each key observation does)
| observation | supports | weakens |
|---|---|---|
| long SETUP_FORMING > 0 after neutralising book (E-101) | H-gate-1 | H-param as the cause of "all short" |
| corrected N still < 100 | H-gate-3 | "history lacks proofs" as the whole story |
| book-neutral live verdicts differ < 5% (E-103) | H-param, H-label | H-data |
| walkthrough trades rejected by floor/window (E-104) | H-param, H-extract (thresholds not from Tom) | H-null as the only reason |
| fat MFE tail vs fair null (E-106) | H-unit | H-null, H-port |
| MFE = null, exits equal | H-null or H-label (wrong locations) | H-unit |
| blind re-extraction disagrees (E-107) | H-extract | H-param (if the params came from the distorted rules) |
| ATR-scaled geometry gross > 0 (E-108) | H-param | H-port |
| TWOPEAK >= 90% on real rows (E-109a) | H-label | none (confirms E-002) |

## 4. Ranking by information gain / cost
| rank | test | runner | cost | why first |
|---|---|---|---|---|
| 1 | E-101 book-neutral rerun of F: snapshots | desktop F:, T0 | 20 min | decides the all-short result and the real live-rule N; also closes REVIEW H1 (loss by reason). The E-001 mechanism is already shown |
| 2 | E-102 live logs, count ratio == 0.0 | desktop live logs, T0 | 10 min | a live safety asymmetry; tells the execution owner whether it has fired |
| 3 | E-105 + E-109a counts (stop_src share, vp_shape distribution) | desktop F:, T0 | 25 min | two cheap counts that confirm or kill H-param (fallback stop) and H-label (TWOPEAK) on real data |
| 4 | E-104 gate replay of every Tom walkthrough | cloud now, Sonnet | 1.5 h | runs today with no data; turns E-003 (n=1) into a rate; feeds E-108 |
| 5 | E-106 MFE tail + exit policies vs fair null | desktop F:, Sonnet + T0 | 3 h, +4 trials | the only test that separates H-unit from H-null; costs trials, so run it after 1-4 |
| 6 | E-103 live book ablation | desktop live logs, T0 | 20 min | settles H-data for core; ranks below 1-5 because R-004 already narrows it to one field |
| 7 | E-107 blind re-extraction | cloud, Haiku + Sonnet | 2 h | H-extract; medium information, independent of the data |
| 8 | E-108 ATR-scaled port | desktop F:, Sonnet | 2 h + ES ATR source | depends on E-104 and E-106 |
| 9 | E-109b blind state labelling | desktop, operator | 2 h operator | the most expensive in human time |

Stopping rules:
- If E-101 gives corrected N >= 100 with longs, re-run the live rule as ONE registered trial before any geometry
  variant.
- If E-106 falsifies H-unit and E-104 shows the trades are unproducible, the next spend is H-label/H-extract, not
  parameter search.
- Every variant spends trials. DSR uses the corrected registry count.
