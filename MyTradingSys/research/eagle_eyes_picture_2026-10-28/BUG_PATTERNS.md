# Backtest bug patterns and the checks that run before a result is trusted (2026-10-31)

Operator: "look at the bugs that we have found so far. What are the patterns? And then do a testing around it before you even attempt the backtesting. Or keep it running in the parallel."
Source: one read-only sweep of the audits (DSA audit T01-T10, fable_audit_2026-10-18, BUGS.md, wavetrend / trendlines / pitchfork audits,
gemini_audits_2026-10-30, critical_test_wave1). About 150 defects; counts are approximate (only the T01-T10 tables were parsed exactly, 51 rows).
None flipped a verdict except the gate-logic cases (pattern 5).

| # | Pattern | ~Bugs | Example | Check | In `bt_preflight.py` |
|---|---|---|---|---|---|
| 1 | Fee / funding wrong or silently zero | 20 | own fee constants in 57/70 files; funding=None pays 0 | fee identity re-derived from prices; ban own fee constants (`test_no_own_costs.py`) | P6 |
| 2 | Spec vs code mismatch | 14 | WT C1 pivots unconfirmed; trendline anchor poisoning | clean-room twin from the pre-reg text, diff event lists | not yet (P2 covers the look-ahead half) |
| 3 | Backtest vs live parity | 10 | FVG side inverted live vs backtest | replay the same bars through both | out of scope (research only) |
| 4 | Look-ahead / time causality | 12+ | HTF bar used before close; OI pairing one bar off | lookahead_lint + prefix test: values at bar i equal on bars[:i+1] | P2 |
| 5 | Statistics / gate logic | 11 | Holm m 57 vs 75 flipped 4 verdicts; SD added to R | planted-power test; random-entry control | P8 (control) |
| 6 | Holdout / split hygiene | 12 | default run read HOLDOUT; "TRAIN" ran into validation | hard window cut in the loader | C27/C28 cut at 2024-07-01 in `wavetrend_dots.R15` |
| 7 | Data silently wrong or missing | 10 | loader accepted gaps and duplicates; OI fail-open to 0 | bars vs span, no duplicates, no all-zero column | P1 (caught C27's lost bars) |
| 8 | Fill realism | 8 | gap through stop booked at the stop; touch = fill | gap-through-stop canary | not yet (C26 has stops: next) |
| 9 | Constants from another market | 7 | DAX 20-point stop on BTC; fixed US-open hour | SOURCED/OURS label on every constant | labels in every result file |
| 10 | Inputs not pinned | 7 | changed inputs, identical reruns | input hash vs manifest | not yet |

Bugs found in this session's own studies, all caught only by looking at the output:
- C27: timestamp alignment dropped about half of the 1h/2h/4h bars (P1 now catches it).
- C28: the trend-flip exit closed counter-trend buys on bar 1, so all four exits were identical (P3 twins + P4 hold now catch it).
- C28: "sell dot in the red band during a downtrend" fired 5 times in 2.5 years (P5 rarity now flags it).

## Run 2026-10-31 on C27/C28 (`python bt_preflight.py <repo>`)
172 checks pass; 5 FAIL, all P5 rarity (rules that almost never fire: listed in the C28 card, not used for conclusions).
P2 prefix: WT and trend structure identical on 25 truncated cuts (no look-ahead). P6 fee identity exact. P7 no overlaps.
P8 random entries: the C28 lead (2h uptrend buy dot, exit X3, +0.45%) beats random entries with the same exit in 25 of 30 draws:
only a weak lead, as the card says.

Next checks to add (patterns 2, 8, 10): clean-room twin of each pre-reg, gap-through-stop canary for C26, input hash manifest.
