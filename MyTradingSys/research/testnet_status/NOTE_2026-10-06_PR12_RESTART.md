# NOTE: PR #12 Auto-trader Restart (2026-10-06 ~15:41:23Z)

**Validity of preceding results:**

Results recorded before **2026-10-06T15:41:23Z** in the testnet logs (auto_trades.jsonl, trade_ledger.jsonl) were generated using pre-PR-#12 code:
- Old stop floor algorithm (replaced in PR #12)
- Old target window (replaced in PR #12)
- book_imbalance = 0.0 bug instead of null (fixed in PR #12 / B084)
- Pre-B131 proof counts in Tom core

Auto-trader was restarted at ~15:41:23Z on 2026-10-06 with PR #12 fixes (stop floor removed, book_imbalance null, MSB/proof fixes, Deribit fees).

**OI-derived fields tainted:** OI ticks from 2026-09-24 until B136 restart are flat and unreliable.

Backtests T055 C1/C2 and Tom core should be rerun with current code to verify edge stability.
