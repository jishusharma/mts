MATCH 68 | DIFF 0 | NOT_IN_DATA 0

# GPT re-derive: bb_long_window_2026-11-04 RESULT_LONG.md headline numbers

Method: Sonnet re-derivation (Codex lane stalled), no study_long.py. Inputs: counts_long.csv (n, days, fills, signals) and dev_cells_long.csv (per-cell gross, net, CI; no per-trade list is committed). Fee rule: net = gross - 0.14 % round trip (the report stated cost; FORMULAS.md section 18 uses 0.0005 taker per leg = 0.10 % RT plus slip; the report uses 0.14 %, taken as given, and the identity net = gross - 0.14 is tested on every cell). Compared at the 3-decimal rounding of the report (tolerance 0.001 on % values). Raw 1m data is not on this laptop, so gross itself cannot be re-derived from prices: it is read from dev_cells_long.csv.

| # | row | source line quoted | report value | derived value | status |
|---|---|---|---|---|---|
| 1 | H1 A 15m range all-sess signal | n 9008 / 1560 days, net -0.128 [-0.155,-0.102] | (9008, -0.128, -0.155, -0.102) | (9008, np.float64(-0.128), np.float64(-0.155), np.float64(-0.102)) | MATCH |
| 2 | H1b days | n 9008 / 1560 days | (1560,) | (1560,) | MATCH |
| 3 | H1c gross | gross +0.012 % | (0.012,) | (np.float64(0.012),) | MATCH |
| 4 | H2 ungated control | control n 12066, net -0.118 [-0.141,-0.094] | (12066, -0.118, -0.141, -0.094) | (12066, np.float64(-0.118), np.float64(-0.141), np.float64(-0.094)) | MATCH |
| 5 | H2b gate effect | gate effect -0.010 % (t -1.4) | (-0.01, -1.4) | (np.float64(-0.01), np.float64(-1.4)) | MATCH |
| 6 | H3 bull | Bull (n 3058) net -0.087 [-0.137,-0.037] | (3058, -0.087, -0.137, -0.037) | (3058, np.float64(-0.087), np.float64(-0.137), np.float64(-0.037)) | MATCH |
| 7 | H4 long | long -0.105 [-0.145,-0.066] | (4498, -0.105, -0.145, -0.066) | (4498, np.float64(-0.105), np.float64(-0.145), np.float64(-0.066)) | MATCH |
| 8 | H5 short | short -0.151 [-0.185,-0.117] | (4510, -0.151, -0.185, -0.117) | (4510, np.float64(-0.151), np.float64(-0.185), np.float64(-0.117)) | MATCH |
| 9 | H5b long+short n and weighted net = both | sides pooled | (9008, np.float64(-0.128)) | (9008, np.float64(-0.128)) | MATCH |
| 10 | H6 wide | Wide -0.133 [-0.189,-0.077] | (3580, -0.133, -0.189, -0.077) | (3580, np.float64(-0.133), np.float64(-0.189), np.float64(-0.077)) | MATCH |
| 11 | H6b wide hit | wide 14 % target hits | (0.14,) | (np.float64(0.14),) | MATCH |
| 12 | H7 narrow | narrow -0.125 [-0.148,-0.102] | (5428, -0.125, -0.148, -0.102) | (5428, np.float64(-0.125), np.float64(-0.148), np.float64(-0.102)) | MATCH |
| 13 | H7b narrow hit | narrow 26 % | (0.26,) | (np.float64(0.26),) | MATCH |
| 14 | H8 1h range | 1h range n 2226 net -0.103 [-0.211,+0.005] | (2226, -0.103, -0.211, 0.005) | (2226, np.float64(-0.103), np.float64(-0.211), np.float64(0.005)) | MATCH |
| 15 | H9 4h range | 4h n 548 -0.091 [-0.486,+0.305] | (548, -0.091, -0.486, 0.305) | (548, np.float64(-0.091), np.float64(-0.486), np.float64(0.305)) | MATCH |
| 16 | H10 15m late | 15m late -0.043 [-0.108,+0.023] | (1108, -0.043, -0.108, 0.023) | (1108, np.float64(-0.043), np.float64(-0.108), np.float64(0.023)) | MATCH |
| 17 | H11 retest all | retest net -0.127 vs signal -0.128 | (9007, -0.127, -0.1528103072549753, -0.1006086021432047) | (9007, np.float64(-0.127), np.float64(-0.153), np.float64(-0.101)) | MATCH |
| 18 | H12 retest fill | 9007 of 9008 fill (99.99 %) | (9007, 9008) | (9007, 9008) | MATCH |
| 19 | H12b fill pct | 99.99 % | (99.99,) | (99.99,) | MATCH |
| 20 | T A asia signal k=None | n 2697 / 1412 d, net -0.140 [-0.182,-0.098] | (2697, -0.14, -0.182, -0.098) | (2697, np.float64(-0.14), np.float64(-0.182), np.float64(-0.098)) | MATCH |
| 21 | T A asia signal k=None days | 1412 days | (1412,) | (1412,) | MATCH |
| 22 | T A asia signal k=None Holm p | Holm p <0.001 | ('<0.001',) | (0.0,) | MATCH |
| 23 | T A london signal k=None | n 2093 / 1270 d, net -0.165 [-0.220,-0.109] | (2093, -0.165, -0.22, -0.109) | (2093, np.float64(-0.165), np.float64(-0.22), np.float64(-0.109)) | MATCH |
| 24 | T A london signal k=None days | 1270 days | (1270,) | (1270,) | MATCH |
| 25 | T A london signal k=None Holm p | Holm p <0.001 | ('<0.001',) | (0.0,) | MATCH |
| 26 | T A ny signal k=None | n 3110 / 1465 d, net -0.123 [-0.168,-0.079] | (3110, -0.123, -0.168, -0.079) | (3110, np.float64(-0.123), np.float64(-0.168), np.float64(-0.079)) | MATCH |
| 27 | T A ny signal k=None days | 1465 days | (1465,) | (1465,) | MATCH |
| 28 | T A ny signal k=None Holm p | Holm p <0.001 | ('<0.001',) | (0.0,) | MATCH |
| 29 | T A asia retest k=None | n 2696 / 1416 d, net -0.143 [-0.186,-0.101] | (2696, -0.143, -0.186, -0.101) | (2696, np.float64(-0.143), np.float64(-0.186), np.float64(-0.101)) | MATCH |
| 30 | T A asia retest k=None days | 1416 days | (1416,) | (1416,) | MATCH |
| 31 | T A asia retest k=None Holm p | Holm p <0.001 | ('<0.001',) | (0.0,) | MATCH |
| 32 | T A london retest k=None | n 2093 / 1270 d, net -0.164 [-0.218,-0.109] | (2093, -0.164, -0.218, -0.109) | (2093, np.float64(-0.164), np.float64(-0.218), np.float64(-0.109)) | MATCH |
| 33 | T A london retest k=None days | 1270 days | (1270,) | (1270,) | MATCH |
| 34 | T A london retest k=None Holm p | Holm p <0.001 | ('<0.001',) | (0.0,) | MATCH |
| 35 | T A ny retest k=None | n 3110 / 1465 d, net -0.115 [-0.160,-0.069] | (3110, -0.115, -0.16, -0.069) | (3110, np.float64(-0.115), np.float64(-0.16), np.float64(-0.069)) | MATCH |
| 36 | T A ny retest k=None days | 1465 days | (1465,) | (1465,) | MATCH |
| 37 | T A ny retest k=None Holm p | Holm p <0.001 | ('<0.001',) | (0.0,) | MATCH |
| 38 | T B asia level k=0.25 | n 486 / 374 d, net -0.045 [-0.171,+0.080] | (486, -0.045, -0.171, 0.08) | (486, np.float64(-0.045), np.float64(-0.171), np.float64(0.08)) | MATCH |
| 39 | T B asia level k=0.25 days | 374 days | (374,) | (374,) | MATCH |
| 40 | T B asia level k=0.25 Holm p | Holm p 1.00 | ('1.00',) | (1.0,) | MATCH |
| 41 | T B asia level k=0.5 | n 507 / 389 d, net -0.065 [-0.180,+0.050] | (507, -0.065, -0.18, 0.05) | (507, np.float64(-0.065), np.float64(-0.18), np.float64(0.05)) | MATCH |
| 42 | T B asia level k=0.5 days | 389 days | (389,) | (389,) | MATCH |
| 43 | T B asia level k=0.5 Holm p | Holm p 1.00 | ('1.00',) | (1.0,) | MATCH |
| 44 | T B asia level k=1.0 | n 520 / 394 d, net -0.084 [-0.193,+0.026] | (520, -0.084, -0.193, 0.026) | (520, np.float64(-0.084), np.float64(-0.193), np.float64(0.026)) | MATCH |
| 45 | T B asia level k=1.0 days | 394 days | (394,) | (394,) | MATCH |
| 46 | T B asia level k=1.0 Holm p | Holm p 1.00 | ('1.00',) | (1.0,) | MATCH |
| 47 | T B london level k=0.25 | n 390 / 316 d, net -0.208 [-0.379,-0.037] | (390, -0.208, -0.379, -0.037) | (390, np.float64(-0.208), np.float64(-0.379), np.float64(-0.037)) | MATCH |
| 48 | T B london level k=0.25 days | 316 days | (316,) | (316,) | MATCH |
| 49 | T B london level k=0.25 Holm p | Holm p 0.34 | ('0.34',) | (0.3392,) | MATCH |
| 50 | T B london level k=0.5 | n 403 / 322 d, net -0.212 [-0.374,-0.051] | (403, -0.212, -0.374, -0.051) | (403, np.float64(-0.212), np.float64(-0.374), np.float64(-0.051)) | MATCH |
| 51 | T B london level k=0.5 days | 322 days | (322,) | (322,) | MATCH |
| 52 | T B london level k=0.5 Holm p | Holm p 0.23 | ('0.23',) | (0.2256,) | MATCH |
| 53 | T B london level k=1.0 | n 413 / 330 d, net -0.238 [-0.393,-0.084] | (413, -0.238, -0.393, -0.084) | (413, np.float64(-0.238), np.float64(-0.393), np.float64(-0.084)) | MATCH |
| 54 | T B london level k=1.0 days | 330 days | (330,) | (330,) | MATCH |
| 55 | T B london level k=1.0 Holm p | Holm p 0.06 | ('0.06',) | (0.0589,) | MATCH |
| 56 | T B ny level k=0.25 | n 439 / 345 d, net -0.139 [-0.291,+0.014] | (439, -0.139, -0.291, 0.014) | (439, np.float64(-0.139), np.float64(-0.291), np.float64(0.014)) | MATCH |
| 57 | T B ny level k=0.25 days | 345 days | (345,) | (345,) | MATCH |
| 58 | T B ny level k=0.25 Holm p | Holm p 0.98 | ('0.98',) | (0.9838,) | MATCH |
| 59 | T B ny level k=0.5 | n 456 / 355 d, net -0.141 [-0.294,+0.011] | (456, -0.141, -0.294, 0.011) | (456, np.float64(-0.141), np.float64(-0.294), np.float64(0.011)) | MATCH |
| 60 | T B ny level k=0.5 days | 355 days | (355,) | (355,) | MATCH |
| 61 | T B ny level k=0.5 Holm p | Holm p 0.97 | ('0.97',) | (0.9669,) | MATCH |
| 62 | T B ny level k=1.0 | n 478 / 370 d, net -0.144 [-0.289,+0.002] | (478, -0.144, -0.289, 0.002) | (478, np.float64(-0.144), np.float64(-0.289), np.float64(0.002)) | MATCH |
| 63 | T B ny level k=1.0 days | 370 days | (370,) | (370,) | MATCH |
| 64 | T B ny level k=1.0 Holm p | Holm p 0.86 | ('0.86',) | (0.8582,) | MATCH |
| 65 | G1 net = gross - 0.14 on all cells | 1413 cells with n>0 | (0,) | (0,) | MATCH |
| 66 | G2 CI centred on net | 1413 cells | (0,) | (0,) | MATCH |
| 67 | G3 cells vs counts_long.csv keys | 1755/1755 | (1755,) | (1755,) | MATCH |
| 68 | G4 n equal in both csv |  | (0,) | (0,) | MATCH |

