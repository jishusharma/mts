# P1 PRE-REG: phase-tag split of frozen DEV events (RSI-DIV-MTF, Krown)

Frozen 2026-10-31 BEFORE any outcome was read. Spec: SYNTHESIS.md s4 row P1; VALIDATION.md 3b, 4b, 4d.

## 0. Input audit (done before this file; no outcome read)
| Layer | Frozen DEV per-event fee-net R list on disk? | Evidence |
|---|---|---|
| RSI-DIV-MTF | NO. `layer_lab/rsi_divergence_event_table` is a gross MFE/MAE table (643 events, no exit rule, no fees); `rsi_divergence_mtf_2026-10-09` reports 10-bar % returns on 2022-01..2026-10 incl. holdout dates, with no event list. | REPORT.md, RESULT.md, summary.json |
| Krown | NO. `krown_audit_2026-10-22` states "No DEV event study has run"; `krown_free_2026-10-31` has 6 Silver Cross events (n < 30 for any cell); `sim_desk` Krown runs are exploratory, n 3-35, no event files. | REPORT.md s1.2, DEV_CHECK.md |
Producing a list would need a new exit rule and fee model = a new study, not a split of a frozen result. Rule: no re-tune, no re-run with new params. So the real-data run is BLOCKED for both layers; this commit freezes the method and ships the tested pipeline so the run is one command once a frozen list exists.

## 1. Design (frozen)
- Unit: one event with date t (UTC day of the signal/entry) and fee-net R. Only events dated 2022-01-01..2024-06-30 (DEV); anything 2025-07+ is dropped and counted.
- Tags (fast-cycling only, from `phase_tag/tags.csv`, row t built from bars closed <= t-1): cowen_side (above/inside/below), sma200_side (above/below), wsma10_phase (4 states). Events with a blank tag are dropped from that tag's test.
- Halving-bin and drawdown-bin: reported as n and mean only, no verdict (D3).
- Placebo tag (OURS): ISO-week parity of the event date. Must come out null; a flagged placebo voids that layer's run.
- Cells: n >= 30 reported, n >= 200 decided; below 30 shown as "n too small".
- CI: block bootstrap of event-day blocks (10 calendar-day blocks, 2,000 resamples, OURS), 95% percentile.
- Family-wise test: `harness.shift_null_test`, 1,000 circular shifts of the label sequence (events in time order), 95th percentile of max |cell mean - pooled mean|, step-down. One test per (layer, tag).
- Pass for a cell (all required): n >= 200; flagged by the shift test; same sign as the pooled effect in every calendar year with >= 30... (every year present in DEV with n >= 10 in that cell; fewer qualifying years = not decidable); same sign in >= 2 of 3 tag episodes (episode = maximal run of consecutive days with one label; the 3 longest episodes of the cell) each with bootstrap 95% CI not crossing the opposite sign; placebo not flagged.
- Verdict words: PASS, FAIL, NOT_DECIDABLE (n < 200 or episodes/years too thin), BLOCKED (no frozen list).
- Trials: cells = layers x tags x states, each one row in layer_lab/TRIALS.md.
- Labels: all thresholds above are OURS except n >= 30/200, 1,000 shifts, 95th percentile, placebo requirement (SOURCED SYNTHESIS P1).
- Planted-edge test: +0.3 into a random 20% of one cell's events through this same pipeline must flag that cell and no other; no injection must flag nothing.
