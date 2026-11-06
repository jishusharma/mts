BLOCKED: wide pivots (strength 3) fill the OURS bands with events, but every (TF, band) fails the power gate, so no return was read. Default window 3-10 unchanged.
Regime mix: 130 weeks: bull 25 (19%) | bear 0 (0%) | range 105 (81%) | n/a 0 (0%)

# RESULT: Malkan window bands, pivot strength 3, 10 symbols pooled, DEV 2022-01..2024-06, count + power gate only

PRE_REG.md frozen before the count. Pivot strength 3 (OURS), bands unchanged, cost 0.14 %, exit 10 bars, cluster = symbol x day, Holm m = 238 (222 repo-wide DEV + 16 new cells). Bars from 2024-07-01 never opened. Files: `counts.csv`, `gate_lines.csv`, `symbols.json`.
Symbols: all 10 loaded (21768-21888 1h bars each, above the 7200 floor; none no-signal). SOL, XRP, LTC have a headerless 2022-03 file, handled by the loader (the old study loader would crash on it).

| TF | Band | Label | n events | days | sd % (10-bar) | MDE + cost % | prereg_gate |
|---|---|---|---|---|---|---|---|
| 1h | S3_10 | SOURCED | 2359 | 2119 | 2.795 | 0.416 | BLOCK |
| 1h | B11_12 | OURS | 443 | 432 | 2.795 | 0.751 | BLOCK |
| 1h | C13_18 | OURS | 487 | 479 | 2.795 | 0.721 | BLOCK |
| 1h | D19_50 | OURS | 140 | 140 | 2.795 | 1.214 | BLOCK |
| 4h | S3_10 | SOURCED | 599 | 591 | 5.454 | 1.160 | BLOCK |
| 4h | B11_12 | OURS | 116 | 116 | 5.454 | 2.443 | BLOCK |
| 4h | C13_18 | OURS | 158 | 158 | 5.454 | 2.113 | BLOCK |
| 4h | D19_50 | OURS | 38 | 38 | 5.454 | 4.163 | BLOCK |

Gate rule: BLOCK when MDE + cost exceeds 0.30 % (prereg_gate.py, same function). Sides pooled in the gate (days = distinct symbol x day).

Findings:
- Detector fixed: the OURS bands went from 4 events (BTC+ETH, strength 1) to 1h 1070 and 4h 312 events on 10 symbols.
- Gate blocks everywhere, even the SOURCED 1h 3-10 band with 2119 days: the 10-bar return sd (2.8 %) and the repo-wide Holm m of 238 put the minimum detectable net at 0.42 %, above the 0.30 % plausible ceiling. More symbols cannot fix this; the lever is a lower m (fewer repo-wide DEV variants) or a lower-variance exit, not more data.
- No outcome was computed (`--pass dev` run only for passing bands: none). Not a PASS, not a FAIL.

Not read: VALIDATION, HOLDOUT, any bar from 2024-07-01.
