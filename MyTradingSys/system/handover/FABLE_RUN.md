# Fable run R6: DECIDING PRE-REG (start text)

Operator start line, typed into a new Code session on Fable 5.1, effort high:

    Run FABLE_RUN.md

The session finds this file (`MyTradingSys/system/handover/FABLE_RUN.md`) and follows it. Design and reasons: `MyTradingSys/research/fable_run_design_2026-10-28/DESIGN.md`. Card: `fable-run6-powered-prereg`.

---

You are the MTS Fable session R6. Boot per CLAUDE.md steps 1-2 (`python scripts/dev/sync.py start fable-run6-powered-prereg`, STATUS.md). Usage guard: `get_usage` first and last into `MyTradingSys/research/fable_runs_2026-10-28/USAGE.md` (add an `## R6` section, UTC, all meters). Stop and ship when the weekly Fable meter rises 4 points, the 5 h window reaches 85 %, you pass 45 tool turns, or context reaches 60 %.

Hard limits: no bar at or after 2024-07-01 00:00Z (VALIDATION/HOLDOUT sealed); no outcome column (forward return, PnL, R) is read anywhere; no backtest run; no live tree, no mainnet, never read `.secrets/` or `.env`. Public Binance 4h/1d klines for BTC/ETH/SOL may be fetched (1w is resampled from 1d). No questions to the operator: take the conservative default and log `DECISION (OURS)`.

QUESTION: R1 (`research/fable_runs_2026-10-28/R1_EDGE_OR_STOP.md`) left one path to a BTC fee-net edge: a 4h-and-up rule with enough events. Which family (Krown S5/S8 4h, Malkan RSI 40/60 1d/1w, pitchfork 1d) can be powered, and what is the frozen test that decides it? Do not re-argue R1's verdicts.

READ (the inputs list in DESIGN.md, section "Inputs"): R1 sections 2-4; FORMULAS.md fees + `backtest/power_mde.py`; `backtest/PRE_REG_TEMPLATE.md`; `research/layer_lab/TRIALS.md`; `research/pit_levels_2026-10-16/PRE_REG_V2.md`; BUGS.md B187; `research/context_factors_2026-10-16/COUNTS_DEV_EXT.md`; `research/sim_desk/studies/{krown,rsi,_bars}.py`; `research/malkan_extract_2026-10-15/PRE_REG_MALKAN_GFS_BTC.md`; `research/pitchfork_2026-10-19/PHASE1_EVENT_STUDY.md`; card `krown-dev-event-study`; `research/design_cards_2026-10-26/FABLE_FEE_STOP_RULE.md`.

DO:
1. Write `research/fable_run6_powered_prereg/counts_only.py`: event timestamps only. Windows: DEV 2022-01-01..2024-06-30 (D3), DEV_EXT 2020-01-01..2021-12-31. It drops every bar >= 2024-07-01 at load (before any computation) and asserts none remain, and asserts no outcome column is loaded. 1w bars are resampled from 1d. Write `COUNTS.csv` (family, timeframe, symbol, window, events, mean 14/stop_i in R, n_needed, powered). DEV_EXT missing on disk = NOT_IN_DATA, never estimated as data.
2. One m per family: `python scripts/dev/verdicts.py check "<family words>"` (paste output; exit 1 = a FAIL or one_run pre-reg already covers it: family not powerable here), m = `verdicts.py count --split DEV` + your new cells. Derive both the n_needed z and the DEV pass t from that same m (Holm, as in PRE_REG_V2.md:36). n_needed from R1 section 3 (sd 1.37 R, plausible 0.30 R, cost = mean(14/stop_i) in R); pool symbols with one cluster per UTC day. Then `python scripts/dev/prereg_gate.py --n <days> --sd <sd> --sd-source <file:line> --cost <R> --m auto --new-cells <N>`: exit 1 = NOT POWERED, never freeze. Label each number SOURCED (file:line) or OURS.
3. Write `research/fable_run6_powered_prereg/PRE_REG.md` (max 3 pages): counts table + gate outputs; then EITHER the frozen pre-reg for the best family whose gate exits 0 (all 12 template items, <= 9 cells, stop >= 4x round-trip fee, DEV pass t >= the Holm z for its m, one VALIDATION read pass t >= 2.0 same sign) OR a STOP verdict for the BTC trading-edge program.
4. Cards (`tasks.py twins` first; the three `krown-dev-event-study*` cards are likely twins of E2, then `tasks.py new` + `fill`, then `tasks.py check`; revert any other card it rewrites): E2 DEV run (SONNET), the VALIDATION read (blocked: operator told in one line), carry executability memo (SONNET). On STOP: one card per R1 STOP-list row to pause it.
5. Ship: `python scripts/dev/sync.py ship --release fable-run6-powered-prereg`; commit body `Result: <family POWERED n_available/n_needed | STOP>`; verify with `python scripts/dev/sync.py where` that nothing is left unshipped; `tasks.py done fable-run6-powered-prereg`.

Reply (6 lines max): bold result line (POWERED family or STOP), counts row that decides it, cards filed, usage delta.
