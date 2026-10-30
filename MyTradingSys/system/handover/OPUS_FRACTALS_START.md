# Opus start brief: fractals on BTC, deep research (operator 2026-10-31, login A)

You are an Opus session on login A. Operator order: investigate the kind of fractals studied on BTC and see if we can use them to trade. Deep research.
Card (bookkeeping, may still be raw): `opus-fractals-btc-deep-research-1031` (`tasks.py brief opus-fractals-btc-deep-research-1031`). Boot per CLAUDE.md; `sync.py start fractals-opus-1031`; work in the worktree it prints.

## What to produce (all under MyTradingSys/research/fractals_2026-10-31/)
1. REPORT.md, literature part: which fractal ideas are studied on BTC (Williams 5-bar fractals; fractal dimension and Hurst exponent; multi-timeframe self-similarity and Elliott-type counts; Mandelbrot multifractal volatility; shape matching like our drop_bounce fractal.py), and the published evidence on returns after fees. Every claim has a link and a date. SOURCED vs OURS labelled. Table: idea, source, fee-net?, out-of-sample?, what it claims. No invented numbers.
2. PRE_REG.md: one or two candidate rules built only from fractal structure that fit our levels and coil layers (a fractal confirms only after its right-hand bars close). Frozen and committed before the first run; trial ledger; family-wise correction.
3. Run on DEV only (2022-04-01..2024-06-30, BTC 1m, F:/MTS/data/tom_raw/klines), fee-net with MyTradingSys/backtest/fees.py. Also a shuffle null and a one-bar shift look-ahead check. VALIDATION and holdout stay untouched.
4. Verdict in plain words: tradeable / only a context filter for an existing layer / not tradeable, with n trades, fee-net R, and what would change the answer. An honest negative is a valid result.

## Rules
Prior art: research/drop_bounce_2026-10-29/fractal.py (descriptive shape search, no fees). Repo is PUBLIC: no account/order data. Live tree, engine and layer code are out of scope. Ship with `sync.py ship --release <slug>`, commit body has `Result:`. End your report with a `Noticed:` line. Reply format: bold result line first, tables, plain words.
