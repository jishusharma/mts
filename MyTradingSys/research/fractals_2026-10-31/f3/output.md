# F3 output (DEV 2022-01-01..2025-06-30; 1190 non-overlapping queries; split at 2023-11-13 07:00:00)

| variant | forecasts (A/B) | trades n | hit | net %/trade | R/trade | week-boot 95% CI | control | control mean [2.5,97.5] | p | Holm p | meanA | meanB |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| UNFILT | 1190 (595/595) | 368 | 0.473 | -0.2160 | -0.092 | [-0.5054, 0.0797] | RW | -0.0935 [-0.3345, 0.1656] | 0.8007 | 1.0000 | -0.5071 (n 182) | 0.0689 (n 186) |
| UNFILT | 1190 (595/595) | 368 | 0.473 | -0.2160 | -0.092 | [-0.5054, 0.0797] | SHUF | -0.0846 [-0.3066, 0.1743] | 0.8439 | 1.0000 | -0.5071 (n 182) | 0.0689 (n 186) |
| PHASE | 1100 (535/565) | 359 | 0.474 | -0.2766 | -0.135 | [-0.5660, 0.0323] | RW | -0.0948 [-0.3522, 0.2142] | 0.9003 | 1.0000 | -0.3598 (n 167) | -0.2043 (n 192) |
| PHASE | 1100 (535/565) | 359 | 0.474 | -0.2766 | -0.135 | [-0.5660, 0.0323] | SHUF | -0.0886 [-0.3634, 0.2005] | 0.9169 | 1.0000 | -0.3598 (n 167) | -0.2043 (n 192) |

UNFILT: verdict INCONCLUSIVE; sd of net %/trade 2.735; trades needed to see 0.10 % at 80 % power: 5873

PHASE: verdict INCONCLUSIVE; sd of net %/trade 2.623; trades needed to see 0.10 % at 80 % power: 5401

PHASE minus UNFILT pooled net %/trade: -0.0606, week-boot 95% CI [-0.3711, 0.2341] (descriptive, no verdict)
