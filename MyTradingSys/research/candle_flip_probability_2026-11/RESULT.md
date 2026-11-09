# RESULT: candle-close-colour probability per timeframe (card candle-flip-probability-study-1106)

Regime mix: score 2025-01-01..now: 96 weeks: bull 23 (24%) | bear 0 (0%) | range 73 (76%) | n/a 0 (0%)
Regime mix: fit 2024-01-01..2025-01-01: 53 weeks: bull 35 (66%) | bear 0 (0%) | range 18 (34%) | n/a 0 (0%)

**Verdict: against the pre-registered random-walk null, 16 of 41 powered (group, cell) tests count (Brier lowered out of sample AND Holm p < 0.05 at m = 12 per group, week-clustered SEs) and 15 survive the study-wide m = 48: G1 aligned/Asia/at; G1 aligned/US/at; G1 split/Asia/at; G1 split/EU/at; G1 split/US/at; G2 aligned/Asia/at; G2 aligned/Asia/inside; G2 aligned/EU/inside; G2 aligned/US/at; G2 aligned/US/inside; G2 split/Asia/inside; G2 split/EU/inside; G3 aligned/Asia/inside; G3 split/Asia/inside; G3 split/EU/inside. Against the same null recalibrated on |d| and time left (post-review baseline, fitted on 2024), 9 count and 7 survive m = 48: G1 split/Asia/at; G1 split/EU/at; G2 aligned/Asia/at; G2 aligned/US/at; G2 aligned/US/inside; G2 split/Asia/inside; G3 aligned/US/inside. The gains are tiny (table below) and the whole score window sits in the repo's burned holdout, so nothing here is a clean out-of-sample claim for a new rule.**

What changed after the Haiku review (`REVIEW.md`; `PRE_REG.md` Amendments A1-A8): SEs now cluster by UTC week (the bar-level clusters of the frozen plan are in `cells.csv` as `p_bar`); 1d and 1w rows have no HTF cell (their own colour was in it) and are excluded from the 12 cells; a cell shift needs 30 fit bars; the headline is m = 48; a recalibrated baseline, a regime split and the null's calibration are added. The first run (bar clusters, 16 counted cells) is superseded and is not a result.

Fit 2024 (bar close <= 2025-01-01), score bars opening 2025-01-01 .. 2026-11-06 UTC, one row = one evaluation minute inside a bar; n is rows, bars the distinct bars, weeks the distinct UTC weeks (the cluster). 
1m has no inside, so 1m = NOT_IN_DATA. delta = realised - null (keeps-colour rate), Holm p (12) within the table, Holm p (48) over all four tables. NOT_POWERED = fewer than 30 bars or 30 weeks (p = 1). The prior-close colour is run too (`cells.csv`), but on 24/7 spot it is the open colour to the tick, so agreement between the two is not evidence of anything.

## Size of the gain (score window, open-colour, rows of the 12 cells pooled and weighted; 1d and 1w rows are not in the cells)

| group | rows | Brier null | Brier cond (cells on null) | gain | gain % | Brier baseline (abs d x t) | baseline gain % | Brier cond on baseline | cells count (null) | cells count (baseline) |
|---|---|---|---|---|---|---|---|---|---|---|
| G1 1m-15m | 277001 | 0.15876 | 0.15866 | -0.00010 | 0.07% | 0.15873 | 0.02% | 0.15873 | 5 of 12 | 4 of 12 |
| G2 30m-4h | 204940 | 0.16355 | 0.16276 | -0.00079 | 0.48% | 0.16301 | 0.33% | 0.16270 | 7 of 12 | 4 of 12 |
| G3 6h-1d | 44523 | 0.17043 | 0.16946 | -0.00097 | 0.57% | 0.16979 | 0.38% | 0.16955 | 4 of 12 | 1 of 12 |
| G4 2d-1w | 4170 | 0.16856 | 0.16819 | -0.00037 | 0.22% | 0.16993 | -0.81% | 0.17024 | 0 of 12 | 0 of 12 |

Reading, computed from the tables (no mechanism is claimed): per timeframe the change in Brier (conditioned minus null) runs from -0.00143 to +0.00000 (worse on 2 of 19 timeframes), a gain of at most 0.9% of the null's Brier; no materiality floor was pre-registered, so these are statistical, not economic, gains. The counted cells split by band position and sign of delta: at delta < 0: 7, inside delta < 0: 1, inside delta > 0: 8. The null itself is off (table at the end): the keeps-colour rate runs above it late in long bars, so cell shifts fitted on the null partly measure that error; the baseline columns remove it, and the 'at band' cells select large |price - mean|, so they largely proxy |d|.

## G1 1m-15m (15m, 10m, 5m, 3m, 2m)

| cell | n | bars | weeks | fit bars | realised | null | delta | Brier null | Brier cond | Holm p (12) | Holm p (48) | counts |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| aligned/Asia/at | 5753 | 2994 | 97 | 1659 | 0.8321 | 0.8707 | -0.0386 | 0.12211 | 0.12066 | 0.000 | 0.000 | YES |
| aligned/Asia/inside | 54559 | 23838 | 97 | 13504 | 0.7599 | 0.7596 | 0.0003 | 0.16215 | 0.16215 | 1.000 | 1.000 | no |
| aligned/EU/at | 3906 | 2071 | 97 | 1034 | 0.8367 | 0.8674 | -0.0307 | 0.11934 | 0.11941 | 0.000 | 0.002 | no |
| aligned/EU/inside | 35959 | 15550 | 97 | 8398 | 0.7557 | 0.7632 | -0.0075 | 0.16318 | 0.16312 | 0.070 | 0.339 | no |
| aligned/US/at | 7283 | 3780 | 97 | 1815 | 0.8263 | 0.8654 | -0.0391 | 0.12429 | 0.12368 | 0.000 | 0.000 | YES |
| aligned/US/inside | 66233 | 28687 | 97 | 14666 | 0.7573 | 0.7548 | 0.0025 | 0.16320 | 0.16319 | 1.000 | 1.000 | no |
| split/Asia/at | 3671 | 2077 | 97 | 1164 | 0.8287 | 0.8701 | -0.0414 | 0.12316 | 0.12154 | 0.000 | 0.000 | YES |
| split/Asia/inside | 41147 | 17912 | 97 | 9694 | 0.7567 | 0.7599 | -0.0033 | 0.16309 | 0.16312 | 1.000 | 1.000 | no |
| split/EU/at | 2177 | 1241 | 96 | 650 | 0.8218 | 0.8686 | -0.0468 | 0.12525 | 0.12322 | 0.000 | 0.000 | YES |
| split/EU/inside | 23400 | 9989 | 97 | 5649 | 0.7616 | 0.7649 | -0.0033 | 0.16045 | 0.16044 | 1.000 | 1.000 | no |
| split/US/at | 2988 | 1636 | 97 | 1047 | 0.8286 | 0.8720 | -0.0434 | 0.12005 | 0.11867 | 0.000 | 0.000 | YES |
| split/US/inside | 29925 | 13146 | 97 | 8271 | 0.7623 | 0.7593 | 0.0029 | 0.16143 | 0.16142 | 1.000 | 1.000 | no |

Post-review baseline for the same cells (null recalibrated on |d| x t_left from 2024; delta2 = realised - baseline):

| cell | base | delta2 | Brier base | Brier cond2 | Holm p (12) | Holm p (48) | counts vs baseline |
|---|---|---|---|---|---|---|---|
| aligned/Asia/at | 0.8537 | -0.0216 | 0.12075 | 0.12031 | 0.036 | 0.173 | YES |
| aligned/Asia/inside | 0.7573 | 0.0026 | 0.16214 | 0.16213 | 0.855 | 1.000 | no |
| aligned/EU/at | 0.8496 | -0.0129 | 0.11800 | 0.11880 | 0.529 | 1.000 | no |
| aligned/EU/inside | 0.7604 | -0.0047 | 0.16345 | 0.16343 | 0.606 | 1.000 | no |
| aligned/US/at | 0.8488 | -0.0225 | 0.12331 | 0.12373 | 0.003 | 0.013 | no |
| aligned/US/inside | 0.7533 | 0.0040 | 0.16341 | 0.16340 | 0.300 | 1.000 | no |
| split/Asia/at | 0.8535 | -0.0248 | 0.12198 | 0.12147 | 0.011 | 0.043 | YES |
| split/Asia/inside | 0.7576 | -0.0010 | 0.16294 | 0.16298 | 1.000 | 1.000 | no |
| split/EU/at | 0.8516 | -0.0298 | 0.12386 | 0.12306 | 0.011 | 0.047 | YES |
| split/EU/inside | 0.7619 | -0.0003 | 0.16062 | 0.16062 | 1.000 | 1.000 | no |
| split/US/at | 0.8545 | -0.0258 | 0.11922 | 0.11905 | 0.029 | 0.128 | YES |
| split/US/inside | 0.7571 | 0.0052 | 0.16146 | 0.16145 | 0.606 | 1.000 | no |

## G2 30m-4h (4h, 3h, 2h, 1h, 30m)

| cell | n | bars | weeks | fit bars | realised | null | delta | Brier null | Brier cond | Holm p (12) | Holm p (48) | counts |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| aligned/Asia/at | 5352 | 1555 | 96 | 821 | 0.7954 | 0.8398 | -0.0444 | 0.13734 | 0.13590 | 0.000 | 0.000 | YES |
| aligned/Asia/inside | 40063 | 8868 | 97 | 4716 | 0.7532 | 0.7241 | 0.0292 | 0.16462 | 0.16365 | 0.000 | 0.000 | YES |
| aligned/EU/at | 3190 | 1025 | 97 | 536 | 0.8138 | 0.8339 | -0.0201 | 0.12813 | 0.12775 | 0.248 | 1.000 | no |
| aligned/EU/inside | 26233 | 6210 | 97 | 3308 | 0.7459 | 0.7253 | 0.0206 | 0.16673 | 0.16630 | 0.000 | 0.003 | YES |
| aligned/US/at | 8850 | 2659 | 97 | 1429 | 0.8059 | 0.8484 | -0.0425 | 0.13602 | 0.13423 | 0.000 | 0.000 | YES |
| aligned/US/inside | 44297 | 10025 | 97 | 5091 | 0.7350 | 0.7478 | -0.0128 | 0.17368 | 0.17359 | 0.000 | 0.001 | YES |
| split/Asia/at | 1255 | 433 | 89 | 186 | 0.8104 | 0.8246 | -0.0142 | 0.13152 | 0.13305 | 0.833 | 1.000 | no |
| split/Asia/inside | 31945 | 7207 | 97 | 3880 | 0.7570 | 0.7104 | 0.0466 | 0.16444 | 0.16208 | 0.000 | 0.000 | YES |
| split/EU/at | 921 | 297 | 75 | 148 | 0.8610 | 0.8568 | 0.0043 | 0.09590 | 0.10344 | 0.833 | 1.000 | no |
| split/EU/inside | 18035 | 4359 | 97 | 2505 | 0.7460 | 0.7186 | 0.0273 | 0.16637 | 0.16557 | 0.000 | 0.000 | YES |
| split/US/at | 1991 | 639 | 90 | 510 | 0.8127 | 0.8508 | -0.0381 | 0.12702 | 0.12732 | 0.022 | 0.136 | no |
| split/US/inside | 22808 | 5471 | 97 | 3266 | 0.7551 | 0.7461 | 0.0090 | 0.16429 | 0.16418 | 0.248 | 1.000 | no |

Post-review baseline for the same cells (null recalibrated on |d| x t_left from 2024; delta2 = realised - baseline):

| cell | base | delta2 | Brier base | Brier cond2 | Holm p (12) | Holm p (48) | counts vs baseline |
|---|---|---|---|---|---|---|---|
| aligned/Asia/at | 0.8355 | -0.0401 | 0.13804 | 0.13698 | 0.001 | 0.003 | YES |
| aligned/Asia/inside | 0.7429 | 0.0103 | 0.16346 | 0.16340 | 0.107 | 0.493 | no |
| aligned/EU/at | 0.8318 | -0.0180 | 0.12806 | 0.12774 | 0.640 | 1.000 | no |
| aligned/EU/inside | 0.7436 | 0.0023 | 0.16618 | 0.16621 | 1.000 | 1.000 | no |
| aligned/US/at | 0.8441 | -0.0382 | 0.13631 | 0.13485 | 0.000 | 0.000 | YES |
| aligned/US/inside | 0.7627 | -0.0277 | 0.17429 | 0.17362 | 0.000 | 0.000 | YES |
| split/Asia/at | 0.8266 | -0.0162 | 0.13144 | 0.13328 | 1.000 | 1.000 | no |
| split/Asia/inside | 0.7316 | 0.0254 | 0.16247 | 0.16182 | 0.000 | 0.000 | YES |
| split/EU/at | 0.8507 | 0.0103 | 0.09675 | 0.10342 | 1.000 | 1.000 | no |
| split/EU/inside | 0.7375 | 0.0085 | 0.16539 | 0.16542 | 0.640 | 1.000 | no |
| split/US/at | 0.8454 | -0.0328 | 0.12699 | 0.12749 | 0.107 | 0.538 | no |
| split/US/inside | 0.7615 | -0.0064 | 0.16419 | 0.16415 | 0.710 | 1.000 | no |

## G3 6h-1d (1d, 12h, 8h, 7h, 6h)

| cell | n | bars | weeks | fit bars | realised | null | delta | Brier null | Brier cond | Holm p (12) | Holm p (48) | counts |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| aligned/Asia/at | 1174 | 442 | 80 | 255 | 0.8075 | 0.8350 | -0.0275 | 0.12735 | 0.12673 | 1.000 | 1.000 | no |
| aligned/Asia/inside | 8517 | 2786 | 97 | 1435 | 0.7307 | 0.6991 | 0.0316 | 0.17509 | 0.17411 | 0.004 | 0.012 | YES |
| aligned/EU/at | 763 | 339 | 77 | 214 | 0.8519 | 0.8345 | 0.0174 | 0.10204 | 0.10201 | 1.000 | 1.000 | no |
| aligned/EU/inside | 5483 | 2259 | 97 | 1154 | 0.7210 | 0.7122 | 0.0088 | 0.17686 | 0.17680 | 1.000 | 1.000 | no |
| aligned/US/at | 1904 | 741 | 91 | 382 | 0.8225 | 0.8483 | -0.0258 | 0.12172 | 0.12106 | 0.524 | 1.000 | no |
| aligned/US/inside | 10024 | 3286 | 97 | 1651 | 0.7376 | 0.7377 | -0.0000 | 0.17233 | 0.17236 | 1.000 | 1.000 | no |
| split/Asia/at | 317 | 134 | 41 | 84 | 0.7350 | 0.7014 | 0.0336 | 0.17716 | 0.17868 | 1.000 | 1.000 | no |
| split/Asia/inside | 6769 | 2363 | 97 | 1214 | 0.7363 | 0.6802 | 0.0561 | 0.17598 | 0.17272 | 0.000 | 0.000 | YES |
| split/EU/at | 56 | 32 | 21 | 32 | 0.5893 | 0.6629 | -0.0736 | 0.22038 | 0.22394 | 1.000 | 1.000 | NOT_POWERED |
| split/EU/inside | 4012 | 1703 | 97 | 921 | 0.7268 | 0.6918 | 0.0350 | 0.17770 | 0.17658 | 0.007 | 0.023 | YES |
| split/US/at | 21 | 12 | 7 | 9 | 0.5238 | 0.7433 | -0.2194 | 0.20468 | 0.20468 | 1.000 | 1.000 | NOT_POWERED |
| split/US/inside | 5483 | 1920 | 97 | 1169 | 0.7374 | 0.7055 | 0.0319 | 0.17575 | 0.17449 | 0.017 | 0.061 | YES |

Post-review baseline for the same cells (null recalibrated on |d| x t_left from 2024; delta2 = realised - baseline):

| cell | base | delta2 | Brier base | Brier cond2 | Holm p (12) | Holm p (48) | counts vs baseline |
|---|---|---|---|---|---|---|---|
| aligned/Asia/at | 0.8357 | -0.0282 | 0.12940 | 0.12870 | 1.000 | 1.000 | no |
| aligned/Asia/inside | 0.7233 | 0.0074 | 0.17432 | 0.17438 | 1.000 | 1.000 | no |
| aligned/EU/at | 0.8434 | 0.0085 | 0.10333 | 0.10350 | 1.000 | 1.000 | no |
| aligned/EU/inside | 0.7407 | -0.0197 | 0.17653 | 0.17615 | 0.191 | 0.667 | no |
| aligned/US/at | 0.8495 | -0.0270 | 0.12331 | 0.12258 | 0.493 | 1.000 | no |
| aligned/US/inside | 0.7589 | -0.0213 | 0.17266 | 0.17225 | 0.013 | 0.047 | YES |
| split/Asia/at | 0.7312 | 0.0038 | 0.17680 | 0.17957 | 1.000 | 1.000 | no |
| split/Asia/inside | 0.7083 | 0.0280 | 0.17319 | 0.17249 | 0.092 | 0.317 | no |
| split/EU/at | 0.7185 | -0.1292 | 0.22144 | 0.21588 | 1.000 | 1.000 | NOT_POWERED |
| split/EU/inside | 0.7250 | 0.0018 | 0.17612 | 0.17634 | 1.000 | 1.000 | no |
| split/US/at | 0.7559 | -0.2321 | 0.22332 | 0.22332 | 1.000 | 1.000 | NOT_POWERED |
| split/US/inside | 0.7328 | 0.0045 | 0.17485 | 0.17486 | 1.000 | 1.000 | no |

## G4 2d-1w (1w, 5d, 3d, 2d)

| cell | n | bars | weeks | fit bars | realised | null | delta | Brier null | Brier cond | Holm p (12) | Holm p (48) | counts |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| aligned/Asia/at | 81 | 63 | 26 | 34 | 0.8272 | 0.8284 | -0.0012 | 0.13055 | 0.13667 | 1.000 | 1.000 | NOT_POWERED |
| aligned/Asia/inside | 719 | 530 | 95 | 242 | 0.7441 | 0.7121 | 0.0320 | 0.17472 | 0.17341 | 0.904 | 1.000 | no |
| aligned/EU/at | 40 | 40 | 19 | 24 | 0.8250 | 0.8072 | 0.0178 | 0.14103 | 0.14103 | 1.000 | 1.000 | NOT_POWERED |
| aligned/EU/inside | 376 | 376 | 93 | 169 | 0.7287 | 0.7093 | 0.0195 | 0.17615 | 0.17879 | 1.000 | 1.000 | no |
| aligned/US/at | 160 | 96 | 33 | 46 | 0.8375 | 0.8382 | -0.0007 | 0.11938 | 0.11978 | 1.000 | 1.000 | no |
| aligned/US/inside | 1262 | 605 | 96 | 276 | 0.7702 | 0.7460 | 0.0242 | 0.16214 | 0.16160 | 1.000 | 1.000 | no |
| split/Asia/at | 56 | 47 | 23 | 23 | 0.8214 | 0.7926 | 0.0289 | 0.11281 | 0.11281 | 1.000 | 1.000 | NOT_POWERED |
| split/Asia/inside | 534 | 434 | 95 | 190 | 0.7079 | 0.7014 | 0.0064 | 0.18053 | 0.18082 | 1.000 | 1.000 | no |
| split/EU/at | 21 | 21 | 13 | 10 | 0.7143 | 0.7866 | -0.0723 | 0.16943 | 0.16943 | 1.000 | 1.000 | NOT_POWERED |
| split/EU/inside | 258 | 258 | 88 | 115 | 0.6628 | 0.6630 | -0.0002 | 0.19975 | 0.19981 | 1.000 | 1.000 | no |
| split/US/at | 55 | 46 | 21 | 26 | 0.7636 | 0.7510 | 0.0126 | 0.11572 | 0.11572 | 1.000 | 1.000 | NOT_POWERED |
| split/US/inside | 608 | 423 | 93 | 218 | 0.7484 | 0.6958 | 0.0526 | 0.17587 | 0.17315 | 0.108 | 0.270 | no |

Post-review baseline for the same cells (null recalibrated on |d| x t_left from 2024; delta2 = realised - baseline):

| cell | base | delta2 | Brier base | Brier cond2 | Holm p (12) | Holm p (48) | counts vs baseline |
|---|---|---|---|---|---|---|---|
| aligned/Asia/at | 0.8310 | -0.0038 | 0.12787 | 0.13323 | 1.000 | 1.000 | NOT_POWERED |
| aligned/Asia/inside | 0.7303 | 0.0138 | 0.17638 | 0.17624 | 1.000 | 1.000 | no |
| aligned/EU/at | 0.8088 | 0.0162 | 0.13535 | 0.13535 | 1.000 | 1.000 | NOT_POWERED |
| aligned/EU/inside | 0.7104 | 0.0183 | 0.17839 | 0.18180 | 1.000 | 1.000 | no |
| aligned/US/at | 0.8408 | -0.0033 | 0.11971 | 0.12033 | 1.000 | 1.000 | no |
| aligned/US/inside | 0.7583 | 0.0119 | 0.16289 | 0.16284 | 1.000 | 1.000 | no |
| split/Asia/at | 0.8083 | 0.0132 | 0.11547 | 0.11547 | 1.000 | 1.000 | NOT_POWERED |
| split/Asia/inside | 0.7224 | -0.0146 | 0.18402 | 0.18448 | 1.000 | 1.000 | no |
| split/EU/at | 0.7848 | -0.0706 | 0.16858 | 0.16858 | 1.000 | 1.000 | NOT_POWERED |
| split/EU/inside | 0.6677 | -0.0049 | 0.20468 | 0.20507 | 1.000 | 1.000 | no |
| split/US/at | 0.7564 | 0.0072 | 0.12510 | 0.12510 | 1.000 | 1.000 | NOT_POWERED |
| split/US/inside | 0.7125 | 0.0358 | 0.17479 | 0.17364 | 0.913 | 1.000 | no |

## Brier per timeframe (score window, all family rows incl. 1d/1w; cond = the group's fitted cell shifts, base = recalibrated null)

| tf | colour | rows | bars | Brier null | Brier cond | cond - null | Brier base | base - null |
|---|---|---|---|---|---|---|---|---|
| 15m | open | 56567 | 9469 | 0.15447 | 0.15429 | -0.00018 | 0.15458 | +0.00011 |
| 10m | open | 55904 | 9423 | 0.15877 | 0.15877 | -0.00000 | 0.15890 | +0.00013 |
| 5m | open | 55630 | 14148 | 0.15928 | 0.15926 | -0.00002 | 0.15921 | -0.00006 |
| 3m | open | 55136 | 28113 | 0.16136 | 0.16121 | -0.00015 | 0.16130 | -0.00006 |
| 2m | open | 53764 | 53764 | 0.16007 | 0.15990 | -0.00017 | 0.15978 | -0.00029 |
| 4h | open | 20915 | 4048 | 0.17053 | 0.16952 | -0.00100 | 0.17022 | -0.00031 |
| 3h | open | 28331 | 4723 | 0.16972 | 0.16866 | -0.00106 | 0.16891 | -0.00081 |
| 2h | open | 42497 | 7422 | 0.16734 | 0.16646 | -0.00088 | 0.16645 | -0.00088 |
| 1h | open | 56722 | 9459 | 0.16221 | 0.16127 | -0.00094 | 0.16180 | -0.00041 |
| 30m | open | 56475 | 9428 | 0.15636 | 0.15600 | -0.00036 | 0.15600 | -0.00035 |
| 1d | open | 4044 | 674 | 0.17091 | 0.17091 | +0.00000 | 0.17124 | +0.00033 |
| 12h | open | 7420 | 1349 | 0.16232 | 0.16089 | -0.00143 | 0.16113 | -0.00119 |
| 8h | open | 10795 | 2024 | 0.17867 | 0.17808 | -0.00059 | 0.17857 | -0.00010 |
| 7h | open | 12144 | 2313 | 0.16760 | 0.16660 | -0.00100 | 0.16707 | -0.00053 |
| 6h | open | 14164 | 2698 | 0.17083 | 0.16983 | -0.00100 | 0.16997 | -0.00086 |
| 1w | open | 570 | 95 | 0.14774 | 0.14774 | +0.00000 | 0.15135 | +0.00361 |
| 5d | open | 804 | 134 | 0.16524 | 0.16495 | -0.00029 | 0.16633 | +0.00109 |
| 3d | open | 1344 | 224 | 0.16930 | 0.16851 | -0.00078 | 0.17109 | +0.00180 |
| 2d | open | 2022 | 337 | 0.16939 | 0.16926 | -0.00013 | 0.17060 | +0.00120 |
| 15m | pc | 56567 | 9469 | 0.15459 | 0.15441 | -0.00017 | 0.15469 | +0.00010 |
| 10m | pc | 55904 | 9423 | 0.15868 | 0.15869 | +0.00001 | 0.15881 | +0.00012 |
| 5m | pc | 55630 | 14148 | 0.15934 | 0.15931 | -0.00002 | 0.15928 | -0.00006 |
| 3m | pc | 55136 | 28113 | 0.16126 | 0.16111 | -0.00015 | 0.16118 | -0.00008 |
| 2m | pc | 53764 | 53764 | 0.16006 | 0.15990 | -0.00016 | 0.15978 | -0.00028 |
| 4h | pc | 20915 | 4048 | 0.17053 | 0.16953 | -0.00099 | 0.17021 | -0.00031 |
| 3h | pc | 28331 | 4723 | 0.16972 | 0.16867 | -0.00105 | 0.16891 | -0.00081 |
| 2h | pc | 42497 | 7422 | 0.16734 | 0.16646 | -0.00088 | 0.16644 | -0.00089 |
| 1h | pc | 56722 | 9459 | 0.16221 | 0.16128 | -0.00093 | 0.16181 | -0.00040 |
| 30m | pc | 56475 | 9428 | 0.15636 | 0.15600 | -0.00036 | 0.15601 | -0.00035 |
| 1d | pc | 4044 | 674 | 0.17091 | 0.17091 | +0.00000 | 0.17124 | +0.00033 |
| 12h | pc | 7420 | 1349 | 0.16232 | 0.16089 | -0.00143 | 0.16113 | -0.00119 |
| 8h | pc | 10795 | 2024 | 0.17867 | 0.17809 | -0.00059 | 0.17856 | -0.00011 |
| 7h | pc | 12144 | 2313 | 0.16760 | 0.16659 | -0.00100 | 0.16707 | -0.00053 |
| 6h | pc | 14164 | 2698 | 0.17083 | 0.16983 | -0.00100 | 0.16997 | -0.00087 |
| 1w | pc | 570 | 95 | 0.14774 | 0.14774 | +0.00000 | 0.15135 | +0.00361 |
| 5d | pc | 804 | 134 | 0.16524 | 0.16494 | -0.00029 | 0.16633 | +0.00109 |
| 3d | pc | 1344 | 224 | 0.16929 | 0.16851 | -0.00078 | 0.17109 | +0.00180 |
| 2d | pc | 2022 | 337 | 0.16939 | 0.16926 | -0.00013 | 0.17060 | +0.00120 |

## Score-window delta by weekly regime (open-colour, all rows of the group; weeks = distinct UTC weeks; fit was 66% bull, score is 76% range)

| group | regime | n | weeks | delta vs null | se | delta vs baseline | se |
|---|---|---|---|---|---|---|---|
| G1 1m-15m | bull | 68708 | 24 | -0.0042 | 0.0025 | -0.0000 | 0.0026 |
| G1 1m-15m | range | 208293 | 73 | -0.0045 | 0.0011 | -0.0011 | 0.0011 |
| G2 30m-4h | bull | 50714 | 24 | 0.0066 | 0.0037 | -0.0091 | 0.0036 |
| G2 30m-4h | range | 154226 | 73 | 0.0145 | 0.0019 | -0.0010 | 0.0019 |
| G3 6h-1d | bull | 11949 | 24 | 0.0233 | 0.0059 | -0.0009 | 0.0060 |
| G3 6h-1d | range | 36618 | 73 | 0.0202 | 0.0041 | -0.0040 | 0.0041 |
| G4 2d-1w | bull | 1176 | 24 | -0.0137 | 0.0232 | -0.0258 | 0.0234 |
| G4 2d-1w | range | 3564 | 73 | 0.0380 | 0.0109 | 0.0251 | 0.0110 |

## The null's own calibration by time left (score window, open-colour, all rows of the group; week-clustered se)

| group | t_left | n | weeks | realised | null | delta | se |
|---|---|---|---|---|---|---|---|
| G1 1m-15m | 0.0-0.2 | 32969 | 97 | 0.8856 | 0.8790 | 0.0065 | 0.0019 |
| G1 1m-15m | 0.2-0.4 | 79703 | 97 | 0.8140 | 0.8128 | 0.0012 | 0.0015 |
| G1 1m-15m | 0.4-0.6 | 86494 | 97 | 0.7554 | 0.7633 | -0.0079 | 0.0015 |
| G1 1m-15m | 0.6-0.8 | 59508 | 97 | 0.6905 | 0.7027 | -0.0122 | 0.0019 |
| G1 1m-15m | 0.8-1.0 | 18327 | 97 | 0.6240 | 0.6304 | -0.0064 | 0.0035 |
| G2 30m-4h | 0.0-0.2 | 33722 | 97 | 0.8899 | 0.8625 | 0.0274 | 0.0017 |
| G2 30m-4h | 0.2-0.4 | 33721 | 97 | 0.8289 | 0.8051 | 0.0238 | 0.0020 |
| G2 30m-4h | 0.4-0.6 | 68115 | 97 | 0.7526 | 0.7404 | 0.0122 | 0.0020 |
| G2 30m-4h | 0.6-0.8 | 34377 | 97 | 0.6829 | 0.6794 | 0.0035 | 0.0026 |
| G2 30m-4h | 0.8-1.0 | 35005 | 97 | 0.6249 | 0.6281 | -0.0032 | 0.0029 |
| G3 6h-1d | 0.0-0.2 | 6747 | 97 | 0.8783 | 0.8437 | 0.0347 | 0.0040 |
| G3 6h-1d | 0.2-0.4 | 7421 | 97 | 0.8210 | 0.7896 | 0.0315 | 0.0040 |
| G3 6h-1d | 0.4-0.6 | 16861 | 97 | 0.7434 | 0.7231 | 0.0204 | 0.0044 |
| G3 6h-1d | 0.6-0.8 | 8769 | 97 | 0.6783 | 0.6627 | 0.0156 | 0.0052 |
| G3 6h-1d | 0.8-1.0 | 8769 | 97 | 0.6200 | 0.6122 | 0.0079 | 0.0058 |
| G4 2d-1w | 0.0-0.2 | 790 | 97 | 0.8722 | 0.8505 | 0.0216 | 0.0132 |
| G4 2d-1w | 0.2-0.4 | 790 | 97 | 0.8203 | 0.7907 | 0.0296 | 0.0128 |
| G4 2d-1w | 0.4-0.6 | 1580 | 97 | 0.7614 | 0.7291 | 0.0323 | 0.0128 |
| G4 2d-1w | 0.6-0.8 | 790 | 97 | 0.6810 | 0.6542 | 0.0268 | 0.0174 |
| G4 2d-1w | 0.8-1.0 | 790 | 97 | 0.6127 | 0.6040 | 0.0086 | 0.0179 |
