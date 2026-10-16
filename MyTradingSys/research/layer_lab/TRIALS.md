# Layer lab trial log

Every backtest or recall run the lab makes is one row here (LAYER_LAB.md, Backtest discipline). Append only.

| date (UTC) | card | command | data range | headline number |
|---|---|---|---|---|
| 2026-10-14 | levels-sizing-quick-probe (operator quick diagnostic) | python MyTradingSys/research/levels_sizing_2026-10-14/probe.py | DEV 2024-12-02..2025-03-31; 8 arms; validation unread | 117 paired signals; all net negative; mean -0.216 to -0.195R; full per-arm TRIAL_REGISTRY.csv in study folder |
| 2026-10-14 | lab-candle-close-dev attempt 1 | study.py | DEV 2022-01..2024-06 | Aborted before events: timestamp-unit gap check; zero actual gaps; no outcomes |
| 2026-10-14 | lab-candle-close-dev attempt 2 | study.py | same DEV | Aborted before events: pandas read-only array; fail-first regression added |
| 2026-10-14 | lab-candle-close-dev attempt 3 | study.py | same DEV | 126 arms, 105541 event rows, 0 pass; all pooled 14bp screens negative; subgroup tables exploratory |
| 2026-10-14 | lab-candle-close-dev overwrite guard | study.py | no data loaded | Refused because results exist; no additional trial outcomes |
| 2026-10-15 | lc-levels-hold | `python -c` (load_klines + levels_by_day + analyze; full command in levels_hold.md) | DEV 2024-12-01..2025-03-31; seed history 2024-11-21..2024-11-30 | KEEP 8, DROP 4; 1,072/1,279 KEEP-family L2 reached (83.8%); 917/1,072 returned to L1 |
| 2026-10-16 | lc-event-table | `python MyTradingSys/research/levels_confluence_2026-10-14/event_table.py` + 16 one-at-a-time feature contrasts | DEV 2024-12-01..2025-03-31; seed 2024-11-21..2024-11-30 | 1,278 first touches; 1,050 L2 fills (82.2%); E1 RSI-hold +1.190 MFE_R (95% day CI +0.414..+2.042), E4 outer-band +0.918 (+0.053..+1.898); 17 total trial arms |
| 2026-10-16 | q79-touchbar (lc-levels-hold re-run, look-ahead fixed) | old vs new `analyze` on identical bars (script in levels_hold.md addendum; load_klines end_ms=2024-07-01) | standard DEV 2022-04-01..2024-06-30; VALIDATION/HOLDOUT unread | 12 families x 2 arms; all 8 KEEP survive; HOLD e.g. prior_day_high 62.1->37.6%, 4h_fractal_low 56.7->44.9%, naked_poc 53.4->53.1%; vah/val/week_low also pass CI but not added; daily_open DROP |
