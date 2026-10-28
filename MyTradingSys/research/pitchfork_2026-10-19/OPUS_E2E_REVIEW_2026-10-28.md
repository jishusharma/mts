# Opus E2E review: Pitchfork layer (2026-10-28)

Card: `pitchfork-opus-e2e-audit-2026-10-28`. Reviewer: claude-opus-5-5 (login C, JIS-DESKTOP).
Verdict: **CHANGES REQUESTED** (not ACCEPT). Tests pass; two rule-level defects and two desk-vs-live
mismatches mean the desk numbers do not measure what the live layer emits.

## Tests (run this session)

| Command | Result |
|---|---|
| pytest: test_pitchfork_detector, sim_desk/test_pitchfork, test_integration_http, T06 test_cost_inventory, test_lookahead_lint | 56 passed, 0 skipped (first run: 5 setup errors only because `target/tmp` did not exist) |
| `mvn test -Dtest=PitchforkSignalLayerTest,SetupCandidatesBuilder*Test` | 53 run, 0 failures, BUILD SUCCESS |

Lookahead lint and cost inventory: pass (no FAIL hits, no uninventoried cost constants).
The card note said "85/85 pytest"; the card's own command set is 56 tests. Not a defect, just a different count.

## Findings (most severe first)

| # | Sev | Where | Finding |
|---|---|---|---|
| F1 | HIGH | `pitchfork_detector.py:528`, `PitchforkSignalLayer.java:500`, desk `EXIT['ML']` label "(trader)" | Hagopian target is `entry +/- channel_width` where `channel_width = UML - LML`. Source (RESEARCH_PITCHFORK_LAYER.md:42) defines the measured move as `W = abs(UML - ML)`, i.e. half of what the code uses. The target is 2x the sourced distance while the desk labels it "(trader)". The source's own setup table (:54-55) says "ML -/+ Channel Width", which for a symmetric fork equals the far tine, not a move from the break; the source is internally inconsistent, so the fix needs one reading chosen and labelled. |
| F2 | HIGH | `PitchforkSignalLayer.java:30-34` javadoc | Cites PHASE2_4H_POC_STUDY "+0.61% net, PF 1.63" as support. That study window is 2020-01-01..2026-09-26 (whole history, no dev/holdout split, no fee-net OOS). It is in-sample evidence and must not be read as an edge. Also it was run with Standard/Schiff/Modified on a different scanner, not this class. |
| F3 | MED | `PitchforkSignalLayer.java:501-511` | Live PF-REV bounce is emitted even when price already reached the ML after P2 (`hasReachedMl` true) and with no age cap on the triplet. Python scanner (`:497`) requires `not has_reached_ml`, no Hagopian, and `bar_i - p2_confirm_bar <= 60`. Live offers stale bounces the desk never tested. |
| F4 | MED | `studies/pitchfork.py:131-132` vs `PitchforkSignalLayer.java:381,427` | Desk profile is TPO (no volume) with bin 10 / 1 / 0.5 by price; live uses real 4h volume and 10 USD bins for every symbol. ETH VA/POC on the desk and in live differ. The desk VA/POC result does not measure the live filter. |
| F5 | LOW | `studies/pitchfork.py:131` | Bin width picked from the mean of the first 50 closes of the whole array: signals in bars 0..49 see later closes (lookahead, bin-size bucket only). The planted-leak test uses `vp_filter='ALL'` only, so VA/POC causality is untested. |
| F6 | LOW | detector `:494,498`, Java `:503,508` | Bounce side comes from `p2.is_high` but the tine is LML/UML by name. On an inverted fork (`p2_is_lower` false for a swing-low P2, steep slope) the entry tine is the line through P1, not P2. Hagopian path uses `p2_is_lower` correctly; bounce path does not. |
| F7 | LOW | detector `:527` vs Java `:497-499` | Hagopian stop parity: Python uses the bar extreme, Java the close. Source says "above/below local fail" (the failed swing extreme); both are OURS and unlabelled as such. |
| F8 | LOW | Java `:315-338` | 1m wick proof reads the last 20 1m bars with no close-time filter; Binance klines include the forming bar, so `proof_1m_wick_rejection` and `score.raw` can flip within a minute. Score-only, no order effect found. |
| F9 | LOW | Java `:532,552-553,590-595`; `TIGHT_POC 0.75%`, wick ratio 0.5, 20-bar window, RR floor 1.5, net_rr_sanity 1.4, score 95/85/75 | OURS numbers carry no OURS label. P-02 (55/75 degree switch and invalidation) is not implemented; Java is fixed Modified Schiff (fine, but say so). PF-REV stop is 1.5% (OURS) vs source "1.0 ATR below P2". |
| F10 | LOW | detector `:334-383` vs `:412-447` | ZigZag logic duplicated inline in `scan_pitchfork_signals`; Java `findPivotsZigZag` is a third copy with a different branch order (a bar that is both local high and low resolves differently). Dedup into one Python function; add a Java-vs-Python pivot parity fixture. |

Checked and OK: Modified Schiff geometry identical in Python and Java; FORMULAS 18.1 profile (tie to lower bin) matches;
Python scanner is causal (pivot at `bar_i - lookback` uses bars `<= bar_i`; profile over P0..P2 only); Java drops the
unclosed trailing 4h bar when close time is present and fails closed on malformed input; `netRR` goes through
`ExecutionMathConstants.netRR(symbol, ...)` (B070 parity); desk entry is next bar open, cache key hashes both files.

## Live wiring

`scripts/core/start-trading-day.ps1:113,445,475` passes `-Dmts.pitchfork=true` to the snapshot and state machine,
so PF-* candidates are appended to the live candidate list (`SetupCandidatesBuilder.java:271`). The card says
`live_path: false`; it is live-path. F3 therefore reaches the live candidate list today.

## Decisions (OURS)

- DECISION (OURS): stamp CHANGES-REQUESTED, not ACCEPT, on both implementation cards; leave them open.
- DECISION (OURS): no code fix in this review card: F1 needs a source reading chosen, F3 is a live-path change
  that needs its own tests. Fixes go to card `pitchfork-review-fixes-2026-10-28`.
- DECISION (OURS): flag left as is (testnet only). Not checked in this review: whether a PF-* candidate can arm an
  order in the state machine. Turning the flag off is a live-tree change, out of scope; the fix card checks it first.
