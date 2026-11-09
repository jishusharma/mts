# Level story on history (DESCRIPTIVE)

**Turn/through scores do NOT separate outcomes (fixed levelstory.js, one pass): share in the idea direction is 0.45-0.55 in every bucket vs 0.50 baseline, net of 10 bp is negative in almost every bucket, and the one standout (SHORT turn >=5: 0.67 first 90 days) reverses in the last 90 (0.39).**

Descriptive only. Thresholds are OURS and coded as in levelstory.js (one pass, no tuning). No holdout, no trade claim. BTCUSDT spot 15m, 2026-05-11 00:00 to 2026-11-09 20:45 UTC (180 days evaluated), ex = {} (no WaveTrend, OI, or forming bar, so those evidence lines and TESTING never fire). Levels: prior UTC day high/low/close, today's Asia (00-08Z) high/low after 08Z. Near = close within 0.3% of the level. A signal counts only when the state or idea for that level changes (leaving the 0.3% band resets). Share+ = share of moves in the signal direction (away from the level for REJECTED/FAILED BREAK/APPROACHING, the idea direction when an idea exists, through for ACCEPTED/BREAKING), close to close after 4 and 8 bars. Events overlap in time (several levels, same hours), so n overstates independent samples; the standard error of a share is about 0.5/sqrt(n). Net = mean bp minus 10 bp round-trip fee. void<8b = share where a 15m close went beyond voidAt before 8 bars. Halves: first 90 days vs last 90 days.

Bars near a level (level x bar pairs): 15202. Signals counted: 8753. State frequency over all level-bar pairs: {'APPROACHING': 5490, 'FAILED BREAK': 1220, 'ACCEPTED': 2166, 'REJECTED': 4645, 'BREAKING': 1681}.

## Baseline: all bars near a level
| group | n | share+ 4b | mean/med bp 4b | net of 10bp 4b | share+ 8b | mean/med bp 8b | net 8b | void<8b |
|---|---|---|---|---|---|---|---|---|
| near_resistance_bars_dir_down [all] | 7398 | 0.499 | 0.85 / -0.03 | -9.15 | 0.474 | 0.48 / -1.58 | -9.52 |  |
| near_resistance_bars_dir_down [h1_first90] | 3456 | 0.504 | 1.3 / 0.1 | -8.7 | 0.487 | 2.4 / -1.33 | -7.6 |  |
| near_resistance_bars_dir_down [h2_last90] | 3942 | 0.495 | 0.46 / -0.29 | -9.54 | 0.463 | -1.2 / -1.69 | -11.2 |  |
| near_support_bars_dir_up [all] | 7804 | 0.509 | -0.89 / 0.3 | -10.89 | 0.498 | -2.5 / -0.16 | -12.5 |  |
| near_support_bars_dir_up [h1_first90] | 3838 | 0.505 | -1.84 / 0.17 | -11.84 | 0.486 | -4.42 / -1.06 | -14.42 |  |
| near_support_bars_dir_up [h2_last90] | 3966 | 0.512 | 0.02 / 0.36 | -9.98 | 0.509 | -0.65 / 0.69 | -10.65 |  |
| all_near_bars_raw_up [all] | 15202 | 0.505 | -0.87 / 0.21 | -10.87 | 0.511 | -1.52 / 0.75 | -11.52 |  |
| all_near_bars_raw_up [h1_first90] | 7294 | 0.5 | -1.58 / 0.02 | -11.58 | 0.498 | -3.46 / -0.09 | -13.46 |  |
| all_near_bars_raw_up [h2_last90] | 7908 | 0.509 | -0.22 / 0.35 | -10.22 | 0.523 | 0.28 / 1.19 | -9.72 |  |

## By state (state-change events)
| group | n | share+ 4b | mean/med bp 4b | net of 10bp 4b | share+ 8b | mean/med bp 8b | net 8b | void<8b |
|---|---|---|---|---|---|---|---|---|
| ACCEPTED [all] | 1469 | 0.482 | -0.34 / -0.92 | -10.34 | 0.491 | 0.18 / -0.78 | -9.82 | 0.944 |
| ACCEPTED [h1_first90] | 726 | 0.5 | 0.47 / -0.04 | -9.53 | 0.494 | 0.74 / -0.41 | -9.26 | 0.951 |
| ACCEPTED [h2_last90] | 743 | 0.464 | -1.13 / -1.3 | -11.13 | 0.487 | -0.38 / -0.93 | -10.38 | 0.937 |
| APPROACHING [all] | 2121 | 0.51 | -0.29 / 0.3 | -10.29 | 0.496 | -0.95 / -0.25 | -10.95 |  |
| APPROACHING [h1_first90] | 1037 | 0.5 | -1.68 / 0.0 | -11.68 | 0.499 | -1.35 / -0.06 | -11.35 |  |
| APPROACHING [h2_last90] | 1084 | 0.518 | 1.04 / 0.38 | -8.96 | 0.494 | -0.56 / -0.34 | -10.56 |  |
| BREAKING [all] | 1626 | 0.473 | -1.06 / -1.61 | -11.06 | 0.494 | 0.4 / -0.58 | -9.6 |  |
| BREAKING [h1_first90] | 851 | 0.471 | -0.35 / -1.88 | -10.35 | 0.485 | 0.79 / -0.94 | -9.21 |  |
| BREAKING [h2_last90] | 775 | 0.474 | -1.84 / -1.56 | -11.84 | 0.505 | -0.02 / 0.15 | -10.02 |  |
| FAILED BREAK [all] | 782 | 0.497 | -0.04 / -0.33 | -10.04 | 0.455 | -0.67 / -3.46 | -10.67 | 0.503 |
| FAILED BREAK [h1_first90] | 413 | 0.508 | 0.04 / 0.21 | -9.96 | 0.45 | -2.59 / -4.27 | -12.59 | 0.516 |
| FAILED BREAK [h2_last90] | 369 | 0.484 | -0.14 / -1.2 | -10.14 | 0.459 | 1.48 / -2.79 | -8.52 | 0.489 |
| REJECTED [all] | 1886 | 0.497 | -0.48 / -0.36 | -10.48 | 0.487 | -1.4 / -1.27 | -11.4 | 0.568 |
| REJECTED [h1_first90] | 923 | 0.506 | -0.91 / 0.06 | -10.91 | 0.491 | -0.39 / -1.01 | -10.39 | 0.557 |
| REJECTED [h2_last90] | 963 | 0.488 | -0.07 / -0.78 | -10.07 | 0.483 | -2.38 / -1.49 | -12.38 | 0.578 |

## REJECTED and FAILED BREAK by turn bucket
| group | n | share+ 4b | mean/med bp 4b | net of 10bp 4b | share+ 8b | mean/med bp 8b | net 8b | void<8b |
|---|---|---|---|---|---|---|---|---|
| REJECTED turn <3 [all] | 1099 | 0.485 | 0.18 / -0.93 | -9.82 | 0.467 | -3.0 / -2.39 | -13.0 |  |
| REJECTED turn <3 [h1_first90] | 548 | 0.511 | -0.51 / 0.07 | -10.51 | 0.471 | -1.29 / -2.21 | -11.29 |  |
| REJECTED turn <3 [h2_last90] | 551 | 0.459 | 0.87 / -1.84 | -9.13 | 0.463 | -4.71 / -2.92 | -14.71 |  |
| REJECTED turn 3 [all] | 453 | 0.519 | 0.51 / 0.84 | -9.49 | 0.523 | 4.08 / 1.99 | -5.92 | 0.581 |
| REJECTED turn 3 [h1_first90] | 224 | 0.496 | 0.05 / -0.84 | -9.95 | 0.527 | 5.09 / 1.75 | -4.91 | 0.58 |
| REJECTED turn 3 [h2_last90] | 229 | 0.541 | 0.97 / 1.69 | -9.03 | 0.52 | 3.08 / 2.3 | -6.92 | 0.581 |
| REJECTED turn 4 [all] | 267 | 0.498 | -2.95 / -0.01 | -12.95 | 0.513 | -1.56 / 1.32 | -11.56 | 0.584 |
| REJECTED turn 4 [h1_first90] | 118 | 0.475 | -3.94 / -1.64 | -13.94 | 0.483 | -5.71 / -1.15 | -15.71 | 0.576 |
| REJECTED turn 4 [h2_last90] | 149 | 0.517 | -2.17 / 0.35 | -12.17 | 0.537 | 1.73 / 2.46 | -8.27 | 0.591 |
| REJECTED turn >=5 [all] | 67 | 0.537 | -8.2 / 2.35 | -18.2 | 0.463 | -11.66 / -5.77 | -21.66 | 0.418 |
| REJECTED turn >=5 [h1_first90] | 33 | 0.606 | -3.14 / 2.35 | -13.14 | 0.606 | -3.61 / 7.71 | -13.61 | 0.333 |
| REJECTED turn >=5 [h2_last90] | 34 | 0.471 | -13.12 / -1.91 | -23.12 | 0.324 | -19.47 / -14.56 | -29.47 | 0.5 |
| FAILED BREAK turn <3 [all] | 0 | | | | | | | |
| FAILED BREAK turn <3 [h1_first90] | 0 | | | | | | | |
| FAILED BREAK turn <3 [h2_last90] | 0 | | | | | | | |
| FAILED BREAK turn 3 [all] | 303 | 0.52 | -0.06 / 1.55 | -10.06 | 0.45 | -0.7 / -4.76 | -10.7 | 0.517 |
| FAILED BREAK turn 3 [h1_first90] | 159 | 0.484 | -0.32 / -1.9 | -10.32 | 0.409 | -4.41 / -6.34 | -14.41 | 0.547 |
| FAILED BREAK turn 3 [h2_last90] | 144 | 0.559 | 0.23 / 2.05 | -9.77 | 0.497 | 3.42 / -1.09 | -6.58 | 0.483 |
| FAILED BREAK turn 4 [all] | 286 | 0.49 | 0.68 / -1.69 | -9.32 | 0.423 | -2.86 / -5.73 | -12.86 | 0.542 |
| FAILED BREAK turn 4 [h1_first90] | 146 | 0.514 | 1.37 / 0.3 | -8.63 | 0.425 | -4.1 / -5.49 | -14.1 | 0.548 |
| FAILED BREAK turn 4 [h2_last90] | 140 | 0.464 | -0.03 / -4.19 | -10.03 | 0.421 | -1.56 / -5.86 | -11.56 | 0.536 |
| FAILED BREAK turn >=5 [all] | 193 | 0.472 | -1.1 / -0.96 | -11.1 | 0.508 | 2.61 / 2.36 | -7.39 | 0.425 |
| FAILED BREAK turn >=5 [h1_first90] | 108 | 0.537 | -1.23 / 0.97 | -11.23 | 0.546 | 2.11 / 5.19 | -7.89 | 0.426 |
| FAILED BREAK turn >=5 [h2_last90] | 85 | 0.388 | -0.93 / -5.98 | -10.93 | 0.459 | 3.23 / -1.3 | -6.77 | 0.424 |

## Turn / thru buckets across states
| group | n | share+ 4b | mean/med bp 4b | net of 10bp 4b | share+ 8b | mean/med bp 8b | net 8b | void<8b |
|---|---|---|---|---|---|---|---|---|
| turn <3 (REJECTED+FAILED BREAK) [all] | 1099 | 0.485 | 0.18 / -0.93 | -9.82 | 0.467 | -3.0 / -2.39 | -13.0 |  |
| turn <3 (REJECTED+FAILED BREAK) [h1_first90] | 548 | 0.511 | -0.51 / 0.07 | -10.51 | 0.471 | -1.29 / -2.21 | -11.29 |  |
| turn <3 (REJECTED+FAILED BREAK) [h2_last90] | 551 | 0.459 | 0.87 / -1.84 | -9.13 | 0.463 | -4.71 / -2.92 | -14.71 |  |
| thru <3 (any state) [all] | 5986 | 0.497 | -0.4 / -0.13 | -10.4 | 0.488 | -0.84 / -0.96 | -10.84 | 0.536 |
| thru <3 (any state) [h1_first90] | 2993 | 0.502 | -0.7 / 0.01 | -10.7 | 0.489 | -0.79 / -0.84 | -10.79 | 0.536 |
| thru <3 (any state) [h2_last90] | 2993 | 0.493 | -0.11 / -0.34 | -10.11 | 0.487 | -0.9 / -1.05 | -10.9 | 0.536 |
| turn 3 (REJECTED+FAILED BREAK) [all] | 756 | 0.519 | 0.28 / 1.02 | -9.72 | 0.494 | 2.17 / -0.65 | -7.83 | 0.555 |
| turn 3 (REJECTED+FAILED BREAK) [h1_first90] | 383 | 0.491 | -0.11 / -1.12 | -10.11 | 0.478 | 1.15 / -1.57 | -8.85 | 0.567 |
| turn 3 (REJECTED+FAILED BREAK) [h2_last90] | 373 | 0.548 | 0.68 / 1.87 | -9.32 | 0.511 | 3.21 / 1.46 | -6.79 | 0.543 |
| thru 3 (any state) [all] | 706 | 0.452 | -2.65 / -3.32 | -12.65 | 0.471 | -0.89 / -2.74 | -10.89 | 0.956 |
| thru 3 (any state) [h1_first90] | 358 | 0.425 | -1.91 / -5.32 | -11.91 | 0.461 | 0.47 / -5.09 | -9.53 | 0.976 |
| thru 3 (any state) [h2_last90] | 348 | 0.481 | -3.42 / -1.72 | -13.42 | 0.481 | -2.29 / -1.12 | -12.29 | 0.939 |
| turn 4 (REJECTED+FAILED BREAK) [all] | 553 | 0.494 | -1.07 / -0.48 | -11.07 | 0.467 | -2.23 / -3.46 | -12.23 | 0.562 |
| turn 4 (REJECTED+FAILED BREAK) [h1_first90] | 264 | 0.496 | -1.01 / -0.25 | -11.01 | 0.451 | -4.82 / -3.87 | -14.82 | 0.561 |
| turn 4 (REJECTED+FAILED BREAK) [h2_last90] | 289 | 0.491 | -1.13 / -1.07 | -11.13 | 0.481 | 0.13 / -1.96 | -9.87 | 0.564 |
| thru 4 (any state) [all] | 915 | 0.498 | 0.71 / -0.18 | -9.29 | 0.499 | 1.51 / -0.3 | -8.49 | 0.943 |
| thru 4 (any state) [h1_first90] | 459 | 0.527 | 1.51 / 1.19 | -8.49 | 0.501 | 2.4 / 0.23 | -7.6 | 0.947 |
| thru 4 (any state) [h2_last90] | 456 | 0.469 | -0.1 / -1.09 | -10.1 | 0.497 | 0.61 / -0.48 | -9.39 | 0.939 |
| turn >=5 (REJECTED+FAILED BREAK) [all] | 260 | 0.488 | -2.93 / -0.55 | -12.93 | 0.496 | -1.07 / -0.5 | -11.07 | 0.423 |
| turn >=5 (REJECTED+FAILED BREAK) [h1_first90] | 141 | 0.553 | -1.68 / 2.0 | -11.68 | 0.56 | 0.77 / 6.54 | -9.23 | 0.404 |
| turn >=5 (REJECTED+FAILED BREAK) [h2_last90] | 119 | 0.412 | -4.41 / -5.74 | -14.41 | 0.42 | -3.26 / -2.73 | -13.26 | 0.445 |
| thru >=5 (any state) [all] | 277 | 0.466 | -0.51 / -1.42 | -10.51 | 0.502 | 0.11 / 0.26 | -9.89 | 0.937 |
| thru >=5 (any state) [h1_first90] | 140 | 0.45 | -3.21 / -2.2 | -13.21 | 0.486 | -3.72 / -1.21 | -13.72 | 0.948 |
| thru >=5 (any state) [h2_last90] | 137 | 0.482 | 2.26 / -0.64 | -7.74 | 0.518 | 4.01 / 1.34 | -5.99 | 0.926 |

## Ideas (idea-change events) by turn bucket
| group | n | share+ 4b | mean/med bp 4b | net of 10bp 4b | share+ 8b | mean/med bp 8b | net 8b | void<8b |
|---|---|---|---|---|---|---|---|---|
| SHORT turn 3 [all] | 557 | 0.492 | 1.7 / -0.84 | -8.3 | 0.474 | 2.98 / -2.16 | -7.02 | 0.637 |
| SHORT turn 3 [h1_first90] | 298 | 0.47 | 1.8 / -2.06 | -8.2 | 0.456 | 3.14 / -2.95 | -6.86 | 0.641 |
| SHORT turn 3 [h2_last90] | 259 | 0.517 | 1.59 / 0.61 | -8.41 | 0.494 | 2.78 / -0.59 | -7.22 | 0.633 |
| SHORT turn 4 [all] | 324 | 0.497 | -0.19 / -0.36 | -10.19 | 0.457 | -0.27 / -3.14 | -10.27 | 0.568 |
| SHORT turn 4 [h1_first90] | 153 | 0.523 | 1.64 / 0.45 | -8.36 | 0.438 | -0.37 / -3.52 | -10.37 | 0.569 |
| SHORT turn 4 [h2_last90] | 171 | 0.474 | -1.82 / -1.47 | -11.82 | 0.474 | -0.17 / -2.57 | -10.17 | 0.567 |
| SHORT turn >=5 [all] | 140 | 0.536 | 0.8 / 2.05 | -9.2 | 0.521 | 7.45 / 3.9 | -2.55 | 0.407 |
| SHORT turn >=5 [h1_first90] | 73 | 0.671 | 7.67 / 6.33 | -2.33 | 0.616 | 17.33 / 12.31 | 7.33 | 0.356 |
| SHORT turn >=5 [h2_last90] | 67 | 0.388 | -6.69 / -5.74 | -16.69 | 0.418 | -3.32 / -3.95 | -13.32 | 0.463 |
| SHORT any [all] | 1379 | 0.51 | 1.2 / 0.34 | -8.8 | 0.483 | 2.71 / -1.22 | -7.29 | 0.671 |
| SHORT any [h1_first90] | 708 | 0.514 | 2.59 / 0.46 | -7.41 | 0.484 | 4.36 / -1.44 | -5.64 | 0.669 |
| SHORT any [h2_last90] | 671 | 0.506 | -0.28 / 0.18 | -10.28 | 0.481 | 0.96 / -1.21 | -9.04 | 0.672 |
| LONG turn 3 [all] | 588 | 0.501 | -2.26 / 0.06 | -12.26 | 0.472 | -2.55 / -1.76 | -12.55 | 0.635 |
| LONG turn 3 [h1_first90] | 295 | 0.492 | -2.95 / -0.98 | -12.95 | 0.464 | -3.01 / -1.57 | -13.01 | 0.641 |
| LONG turn 3 [h2_last90] | 293 | 0.51 | -1.56 / 0.23 | -11.56 | 0.479 | -2.1 / -2.07 | -12.1 | 0.63 |
| LONG turn 4 [all] | 342 | 0.482 | -1.02 / -1.39 | -11.02 | 0.491 | -2.51 / -0.96 | -12.51 | 0.585 |
| LONG turn 4 [h1_first90] | 178 | 0.478 | -2.11 / -1.19 | -12.11 | 0.5 | -4.33 / 0.17 | -14.33 | 0.573 |
| LONG turn 4 [h2_last90] | 164 | 0.488 | 0.16 / -1.68 | -9.84 | 0.482 | -0.53 / -2.41 | -10.53 | 0.598 |
| LONG turn >=5 [all] | 144 | 0.451 | -9.22 / -2.07 | -19.22 | 0.472 | -10.81 / -1.35 | -20.81 | 0.444 |
| LONG turn >=5 [h1_first90] | 81 | 0.432 | -15.28 / -4.09 | -25.28 | 0.481 | -18.26 / -1.18 | -28.26 | 0.457 |
| LONG turn >=5 [h2_last90] | 63 | 0.476 | -1.42 / -1.87 | -11.42 | 0.46 | -1.24 / -1.64 | -11.24 | 0.429 |
| LONG any [all] | 1473 | 0.48 | -3.26 / -1.28 | -13.26 | 0.48 | -3.23 / -1.13 | -13.23 | 0.685 |
| LONG any [h1_first90] | 741 | 0.474 | -5.35 / -1.57 | -15.35 | 0.466 | -6.29 / -2.02 | -16.29 | 0.675 |
| LONG any [h2_last90] | 732 | 0.486 | -1.15 / -0.67 | -11.15 | 0.495 | -0.13 / -0.47 | -10.13 | 0.696 |
| ANY idea [all] | 2852 | 0.494 | -1.11 / -0.46 | -11.11 | 0.481 | -0.36 / -1.18 | -10.36 | 0.678 |
| ANY idea [h1_first90] | 1449 | 0.493 | -1.47 / -0.62 | -11.47 | 0.475 | -1.08 / -1.92 | -11.08 | 0.672 |
| ANY idea [h2_last90] | 1403 | 0.495 | -0.73 / -0.34 | -10.73 | 0.488 | 0.39 / -0.96 | -9.61 | 0.684 |
