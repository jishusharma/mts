# sim-v2 hand-over (Builder, rewritten 2026-10-25 after the Fable items)

Worktree `.claude/worktrees/mts-device-cleanup-5bfbdf`, branch `claude/heuristic-goldstine-7da61f`, trunk `origin/fast-track`.
Rules: testnet only; DEV only (2022-04-01..2024-06-30); public repo (percent and R only, no raw prices); `newline='\n'`; ship only via `python scripts/dev/sync.py ship --release sim-v2` (`--again` inside 10 min of a ship); commit body has `Result:`; co-author `Claude Sonnet 5.5`; do NOT publish the static page; no quiz, badges, scoreboard, play animation, optimizer. Overnight stop rule: get_usage each turn, stop at weekly >= 44% or 02:30Z.

## Done and shipped (git cherry empty at 20:54Z)
Batch 1: levels bug fixed (255 filled of 772, 517 never filled), result schema, `export_results.py`, catalogue (151 rows), static builder.
Overnight order a-e:
- (a) `0fc67ac06` reference tests (`test_reference.py`)
- (b) `de7acbac6` CONDITIONS panel (`conditions.py`; post-filter on the cached run; one TRIALS row per condition)
- (c) `0337601f0` run time shown (levels uncached 5.5-6.7 s, cached 0.0 s)
- (d) `533eab730` scrubbable equity curve in R and $1,000, run A vs B
- (e) `3ecd38c21` each Run writes `results/desk-<study>-<hash>.json` (`curve` example kind)
Fable items (REVIEW_FABLE_2026-10-25.md section 4):
- `bba212e80` numbers strip (win rate, PF, max DD, gross/fee/net)
- `1282d9c21` slippage box, default 0.02 % OURS (levels -0.189 R, was -0.119; frozen tests pin slip_pct=0)
- `b99094841` drawdown shaded on the curve
- `2f2954f6e` clickable trade list -> `/api/trade` candle chart
- `afd937964` Monte Carlo band (1000 fixed-seed reshuffles) + luck line sd*sqrt(2 ln N)/sqrt(n)

## Next (small first)
1. Confirm the slippage default and the deflated-Sharpe luck form once the Gemini files land (`research/gemini_burn_2026-10-25/`). Slippage stays 0.02 % OURS until then.
2. Fable cards still open: breakdown table by family/condition with n; declutter page (Questions panel off, `mockup/` deleted, SIM_DESIGN_RESEARCH.md sections 2-5 cut); entry/exit reason columns in the trade list (run results do not carry them yet).
3. Click-test `page.html` in a browser (only syntax-checked in node so far).
4. Layer-B condition uses default settings of the other study; add typed settings if wanted.

## Open problems
- Conditions are a post-filter: exact for levels, a subset (not a re-run) for rsi/wavetrend (one position at a time). Documented in DESIGN.md.
- Slippage is an extra taker rate on market/stop legs, so the fee share includes it.
- Ship gate is flaky under load (`test_lease.py` 240 s limit); retry.
- T07 audit prose says 8 of 10 reproduce, its csv says 9; page follows the csv.
- Bash tool strips backslashes: use Write/Edit or `chr()`.
