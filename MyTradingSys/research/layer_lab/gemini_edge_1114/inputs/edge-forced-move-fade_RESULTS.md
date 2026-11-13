# edge-forced-move-fade-1113 (local, not shipped) worktree C:\Users\E-ngineers\IdeaProjects\mts-jis-nb-edge-forced-move-fade-1113
PRE_REG + H4 addendum committed before outcomes. Folder MyTradingSys/research/edge_forced_move_fade_2026-11-13 (results.csv, results_h4.csv).
15m impulse (range>=k ATR, vol>=3x med20, new 16-bar extreme), 10 Bybit perps, OI 15min, fee 2x taker + funding, day-cluster CI, placebo.

## H1 fade FORCED (OI fell) / H2 follow NEW (OI rose): FAIL, 0 of 32 cells pass (BH 10%)
VALIDATION (2024-07..2025-06) fee-net mean per trade, all cells within -0.22%..+0.09%:
- H1 k2 x0.3: n 1426 (330 days): T2 -0.16, T4 -0.15, T8 -0.09 (CI -0.21..+0.05), bracket -0.11 (CI -0.16..-0.06); placebo -0.10
- H1 k3 x0.6 T8: n 436 +0.03 (CI -0.31..+0.46); all others negative
- H2 k3 x0.6 T8: n 500 +0.09 (CI -0.26..+0.55) vs placebo -0.07; event-minus-placebo CI -0.21..+0.16
RECENT: H1 every cell negative with CI wholly below zero in most (k2 x0.3 T4 -0.10, CI -0.16..-0.03); H2 about -0.05..+0.03.
KEY: OI class does not separate. Fade ALL impulses VALIDATION T4 -0.15 (n 3051); fade class B (OI rose) -0.14; fade class A (forced) -0.15. Fading costs fees and loses either way. Follow ALL -0.09, follow A -0.09, follow B -0.04: marginally less bad, never positive.
Note: most impulses are already past the 50% retrace at the close of the bar after (13.4k skipped of ~15k class A BTC+alts for the target cells): the give-back happens within 2 bars, before an entry is possible.

## H4 OI build then unwind, 30m and 1h (addendum, pre-registered before outcomes): FAIL, 0 of 96 cells pass
H4a (fade the built side at unwind start), VALIDATION: every cell negative, -0.14%..-0.41% (1h N12 y2 12h: n 2208, 363 days, -0.41, CI -0.64..-0.19; placebo -0.14). RECENT -0.03..-0.17.
H4b (follow trend while OI builds): VALIDATION -0.13..+0.12 (best 1h N6 y2 12h n 2259: +0.12, CI -0.10..+0.33, placebo -0.04, diff CI lower -0.06); RECENT -0.11..+0.01. No cell clears the CI or BH.
Descriptive control (not pre-registered, not a pass): same unwind bar but FOLLOW the built side (H4a_rev) 1h N12 12h: VALIDATION +0.19/+0.21 (CI -0.01..+0.39 / -0.00..+0.43, n 2875/2208), DEV -0.02/+0.01, RECENT -0.11/-0.09. Positive in one year only.
H3 (CVD) dropped: Bybit trade files 30-260 MB per coin-day, too heavy for 500+ days on an overloaded machine.
Commits local only (no ship). Last sha 64cc5e736.
