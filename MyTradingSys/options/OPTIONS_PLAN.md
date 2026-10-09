# OPTIONS MODULE (BTC, Deribit) - PLAN  [session 2026-10-09, App/Opus-lane SUP + Sonnet workers]
Status: independent module. No integration with auto_trader/execution until operator approves a written integration spec.
Owner dir: MyTradingSys/options/. Nothing here imports or edits live-system files (CLAUDE.md live-tree rule).

## Scope (operator ask 2026-10-09)
1. Krown (CBP channel): separate FREE tradable content from PAID; infer paid-content ideas; find free equivalents.
2. Deribit BTC options: data collection (public, no keys), then profitability research, then hedging role for the other books.
3. Strategy research for BTC options that has worked; adopt only what our own backtest supports.

## Method note (playbook Part I, Step 1 - fixed before searching)
Question A "Is any BTC option strategy net-profitable after costs?" Settling evidence: our own backtest on Deribit
data - walk-forward / out-of-sample, >= 1 full vol cycle if data allows, fees (0.03% of underlying capped 12.5% of
premium, per leg) + bid/ask spread + settlement, delta-hedge costs where hedged; PBO/overfit check by param-grid breadth.
Question B "Does an options overlay reduce drawdown of our perp book at acceptable carry?" Evidence: replay of the
testnet/backtest perp PnL stream against priced puts/collars; report carry cost vs tail saved.
External literature = ranking of what to test only (T1/T2). Krown/practitioner = T3 ideas only.
Provenance rule: every parameter (strike delta, DTE, exit) must trace to a quote/paper or be a swept grid reported in
full; no tuning on a single path. Unsourced default = NO-SOURCE, flagged.
Data caveat: Deribit public history may not give historical order books; mark prices/IV from our own snapshots only
accumulate going forward. Backtests on historical TRADES + DVOL + index are lower-fidelity; label accordingly.

## Layout
research/  KROWN_*.md, LITERATURE_*.md, STRATEGY_*.md   collector/  deribit_opt_*.py   data/ (gitignored raw)   tests/
## Phases
P0 plan+protocol review (this) | P1 workers: Krown, literature, collector (parallel) | P2 backfill + continuous snapshot
P3 strategy backtests (own) | P4 hedge-overlay study | P5 verdict + integration spec (not integration)
