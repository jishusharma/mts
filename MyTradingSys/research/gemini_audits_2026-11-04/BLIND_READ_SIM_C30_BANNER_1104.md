# Blind Read Audit: C30 Sim Banner vs `c30_validation_verdict.json` (H1)

- **Card**: `gemini-blind-read-sim-c30-banner-1104`
- **Goal**: D11 feeder check (A-20261104-1) for the sim-demo-opus-1104 ship: verify that the C30 banner in `MyTradingSys/research/sim_desk/results/eagle-c30-wt-rsi-div.json` accurately takes `n` and mean net % from the `trade_chart` trade list when its KPIs carry no count, and that these values match the H1 validation trades in `MyTradingSys/research/eagle_eyes_picture_2026-10-28/c30_validation_verdict.json`.
- **Target Files**:
  - `MyTradingSys/research/eagle_eyes_picture_2026-10-28/c30_validation_verdict.json`
  - `MyTradingSys/research/sim_desk/results/eagle-c30-wt-rsi-div.json`
- **Date**: 2026-11-04 UTC

---

## 1. Primary Source Extraction: `c30_validation_verdict.json` (H1)

From [c30_validation_verdict.json:6-208](file:///F:/MTS/gq/gemini-blind-read-sim-c30-banner-1104/MyTradingSys/research/eagle_eyes_picture_2026-10-28/c30_validation_verdict.json#L6-L208):

- SOURCED `c30_validation_verdict.json:7`: `"n": 35`
- SOURCED `c30_validation_verdict.json:8`: `"mean": -0.06591502449152191`
- SOURCED `c30_validation_verdict.json:24-204`: array of 35 H1 trades `[date, net_pct, bars]`:
  1. `2024-07-03 12:00`: `-3.6538` % (`bars`: 60)
  2. `2024-07-30 03:30`: `0.2395` % (`bars`: 10)
  3. `2024-08-01 05:30`: `0.2925` % (`bars`: 9)
  4. `2024-08-05 03:30`: `2.3345` % (`bars`: 26)
  5. `2024-08-15 08:30`: `0.8657` % (`bars`: 7)
  6. `2024-08-19 12:00`: `0.2374` % (`bars`: 9)
  7. `2024-08-27 01:30`: `-6.6348` % (`bars`: 60)
  8. `2024-09-04 03:30`: `0.9557` % (`bars`: 24)
  9. `2024-09-30 12:00`: `-0.0225` % (`bars`: 34)
  10. `2024-10-01 22:30`: `0.9845` % (`bars`: 13)
  11. `2024-10-23 13:30`: `0.1314` % (`bars`: 20)
  12. `2024-10-31 21:30`: `-0.2748` % (`bars`: 28)
  13. `2024-11-03 16:30`: `0.7116` % (`bars`: 9)
  14. `2024-11-17 23:30`: `0.7973` % (`bars`: 6)
  15. `2024-11-24 19:00`: `1.4149` % (`bars`: 8)
  16. `2024-11-26 00:30`: `0.5918` % (`bars`: 12)
  17. `2024-12-03 15:00`: `0.1946` % (`bars`: 11)
  18. `2024-12-09 23:00`: `0.3142` % (`bars`: 20)
  19. `2024-12-29 23:30`: `0.2749` % (`bars`: 19)
  20. `2025-01-08 13:30`: `-0.4139` % (`bars`: 24)
  21. `2025-01-09 15:30`: `-0.1268` % (`bars`: 22)
  22. `2025-01-21 02:30`: `0.6366` % (`bars`: 16)
  23. `2025-01-23 06:00`: `2.5635` % (`bars`: 20)
  24. `2025-01-27 03:30`: `0.0022` % (`bars`: 23)
  25. `2025-02-02 05:30`: `-4.2254` % (`bars`: 59)
  26. `2025-02-23 18:00`: `0.5285` % (`bars`: 12)
  27. `2025-02-24 22:00`: `-5.5670` % (`bars`: 49)
  28. `2025-03-10 00:30`: `2.3755` % (`bars`: 10)
  29. `2025-03-29 18:00`: `0.4673` % (`bars`: 14)
  30. `2025-04-07 00:00`: `-0.1823` % (`bars`: 28)
  31. `2025-04-16 02:00`: `0.2578` % (`bars`: 18)
  32. `2025-04-26 15:00`: `0.3298` % (`bars`: 15)
  33. `2025-05-24 01:30`: `0.5181` % (`bars`: 18)
  34. `2025-05-31 01:30`: `0.1557` % (`bars`: 25)
  35. `2025-06-22 00:00`: `0.6186` % (`bars`: 12)

### Direct Aggregations of H1 Trades
- OURS trade count `n`: `35`
- OURS sum of trade nets: `-2.3072` %
- OURS arithmetic mean net % per trade: `-2.3072 / 35 = -0.06591999999999999` %
- OURS arithmetic mean net % rounded to 3 decimals: `-0.066` %
- SOURCED `c30_validation_verdict.json:8` stored mean: `-0.06591502449152191` % (rounded to 3 decimals: `-0.066` %)

---

## 2. Comparison with `eagle-c30-wt-rsi-div.json`

From [eagle-c30-wt-rsi-div.json:24899-24909](file:///F:/MTS/gq/gemini-blind-read-sim-c30-banner-1104/MyTradingSys/research/sim_desk/results/eagle-c30-wt-rsi-div.json#L24899-L24909):

```json
  "banner": {
   "state": "UNCLEAR",
   "tone": "",
   "verdict": "VALIDATION: H1 FAIL, H2 INCONCLUSIVE (mean +0.22 %, CI includes 0, Holm p 0.218). Not promoted; HOLDOUT unread.",
   "n": 35,
   "net_r": null,
   "try_no": null,
   "breakeven_x": null,
   "text": "UNCLEAR · verdict as written: VALIDATION: H1 FAIL, H2 INCONCLUSIVE (mean +0.22 %, CI includes 0, Holm p 0.218). Not promoted; HOLDOUT unread. · n=35 (trade list) · net -0.066 %/trade after fees · try n/a · fee break-even n/a",
   "net_pct": -0.066
  }
```

From [eagle-c30-wt-rsi-div.json:71-24894](file:///F:/MTS/gq/gemini-blind-read-sim-c30-banner-1104/MyTradingSys/research/sim_desk/results/eagle-c30-wt-rsi-div.json#L71-L24894) (`examples` -> `trade_chart`):
- `trades` count in `trade_chart`: `35`
- Sum of net % in `trade_chart` trades (rounded to 3 decimals per trade in chart): `-2.304` %
- Mean of `trade_chart` net %: `-0.06582857142857142` % (rounded to 3 decimals: `-0.066` %)
- Banner `n`: SOURCED `eagle-c30-wt-rsi-div.json:24903` = `35`
- Banner `net_pct`: SOURCED `eagle-c30-wt-rsi-div.json:24908` = `-0.066`
- Banner `text`: SOURCED `eagle-c30-wt-rsi-div.json:24907` includes `"n=35 (trade list) · net -0.066 %/trade after fees"`

---

## 3. Comparison Table

| Metric | Source (`c30_validation_verdict.json`) | Target Banner (`eagle-c30-wt-rsi-div.json`) | Match Status |
|---|---|---|---|
| Trade Count `n` | `35` (SOURCED `line 7`, OURS counted 35 trades `line 24-204`) | `35` (SOURCED `line 24903`, `"n=35 (trade list)"` `line 24907`) | MATCH |
| Mean Net % (raw) | `-0.065915...` (SOURCED `line 8`), `-0.06592...` (OURS trade sum mean) | `-0.066` (rounded representation) | MATCH |
| Mean Net % (3 dec) | `-0.066` % (OURS rounded) | `-0.066` % (SOURCED `line 24908`, `line 24907`) | MATCH |

The banner trade count `n=35` and mean net % `-0.066 %/trade` accurately reflect the 35 H1 trades in `c30_validation_verdict.json`.

---

VERDICT: MATCH

## Claude spot-check

Recomputed on 2026-11-04 with a short json parser (scratch script, not committed) from `eagle_eyes_picture_2026-10-28/c30_validation_verdict.json` (`H1`, `H2`) and `sim_desk/results/eagle-c30-wt-rsi-div.json` (`banner`, `examples` where `kind` is `trade_chart`).

| # | Number (recomputed) | Source | Verdict |
|---:|---|---|---|
| 1 | H1 trade count: 35 | verdict `H1.n` and `len(H1.trades)` | AGREE |
| 2 | H1 mean net: -0.06592 % (prints -0.066) | verdict `H1.mean` | AGREE |
| 3 | H1 trade sum: -2.3072 % | sum of `H1.trades[i][1]` | AGREE |
| 4 | trade_chart: 35 trades, sum -2.3040 %, mean -0.06583 %; dates match the verdict in order; largest per-trade gap 0.0005 (3-dp rounding) | sim json `examples[trade_chart].trades[i].net` | AGREE |
| 5 | banner `n` 35, `net_pct` -0.066; the banner text's "mean +0.22 %" is the H2 mean (0.2203), not an H1 error | sim json `banner`, verdict `H2.mean` | AGREE |

Files: `git diff --stat origin/fast-track...gemini-q/gemini-blind-read-sim-c30-banner-1104` touches only this read, its layer_lab report and its card json; no study file changed.

Spot-check: 5 of 5 AGREE.
