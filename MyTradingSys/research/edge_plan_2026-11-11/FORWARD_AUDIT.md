# Forward slots audit (card forward-slots-audit-and-readout-1111, 2026-11-14)

Source: EDGE_PLAN s(b). Audit only: no logger deployed or restarted, no edge judged. All paths repo-relative.

| Slot | Logger file | Journal path (readout input) | Readout column present (Y/N) |
|---|---|---|---|
| Krown S8 (testnet) | MyTradingSys/execution/auto_trader.py (source `layer:krown:s8_break:4h`, account krown_s8) | MyTradingSys/execution/trade_ledger.jsonl (`--ledger`) | Y |
| Malkan level short (paper) | MyTradingSys/backtest/layers/rsi/malkan_level_short_live.py | runtime_data/malkan_level_short_forward.jsonl (`--malkan`) | Y |
| T06L (paper) | MyTradingSys/backtest/layers/rsi/rsi_ma_cross_live.py (long rows only) | runtime_data/t06_rsi_ma_cross_forward.jsonl (`--t06`) | Y |
| C30 (paper) | MyTradingSys/research/c30_forward_2026-11-11/c30_paper_log.py | runtime_data/c30_h2_forward.jsonl (`--c30`) | Y |

Findings
- The C30 row was already wired (ROWS in forward_readout_all.py) and already tested
  (test_c30_outcome_rows_scored_by_t_and_source, test_c30_kill_row_*), so no new test was needed; 14 tests pass
  (test_forward_readout_all.py + test_c30_paper_log.py).
- C30 logger proof: `c30_paper_log.py --once --journal <temp>` fetched public 15m bars and parsed them
  (`{"key": "c30_paper_log", "bar": 1794593700000, "appended": []}`), no signal on that bar, so no journal file was created.
- Malkan and T06 loggers exist but are not deployed (coordinator card deploy-malkan-level-short-forward-1109); journals absent, readout prints n 0.

Output of `python MyTradingSys/research/fable_run7_forward_test/forward_readout_all.py`:

| Slot | Mode | Trades | Net R | E+ | E- | State |
|---|---|---|---|---|---|---|
| Krown S8 | testnet | 0 | - | - | - | n 0, no data yet |
| Malkan | paper | 0 | - | - | - | n 0, no data yet |
| T06L | paper | 0 | - | - | - | n 0, no data yet |
| C30 | paper | 0 | - | - | - | n 0, no data yet |

T06 short (reported, not a lead): n 0, mean R -, unscored.
Net R = mean fee-net R per trade. KILL: E- >= 10 after 10 obs, or 30 trades with net R <= 0, or a journal kill row (EDGE_PLAN c).

Analyst-call slot (paper, stop at 30 trades with net R <= 0): setup n 0, net R -; level only n 0, net R -; trigger only n 0, net R -. State: RUNNING.
