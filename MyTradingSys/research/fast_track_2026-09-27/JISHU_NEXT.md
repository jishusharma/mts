# Jishu - next actions (2026-09-29, minimal). Top to bottom; each line has a DONE check.

## 1. Testnet subaccounts jishu_1..4 (15 min) - 5 parallel trade slots instead of 1
- Fund each, create a no-withdraw API key on each, write 4 secret files yourself, restart the auto-trader.
  Exact steps + routing table: `MyTradingSys/execution/TESTNET_SUBACCOUNTS.md`.
- DONE: `auto_trades.jsonl` shows layer trade_attempts while another trade is open.

## 2. DSA paste jobs (~1-2 h, any time)
- `Dumps/workers/DSA_PACK_2026-09-29/`  (Fabio 0Ky, 0jM + 2 Tom transcripts)
- `Dumps/workers/DSA_PACK_2026-09-29b/` (Fabio held extractions 108-111)
- Paste each file into DSA, save the reply at the path in that pack's README, then tell code mode (it runs the quote gate).
- DONE: all 8 replies saved.

## 3. Decisions - type one line each into SUPERVISOR_LOG.md (5 min). Defaults apply if you skip.
| Question | Recommended default |
|---|---|
| Tom vs Fabio disagree - who wins? | Tom wins; Fabio disagreement is logged only (Fabio is a separate layer) |
| T058 history fetch depth / hedge timing | 2022-01 onward (matches 1m data) / hedge only after entry fill |
| Mainnet kill switch without typed confirmation? | YES (it can only reduce risk) |
| Transaction types excluded from daily PnL | deposit, withdrawal, transfer* (DSA verifies vs Deribit docs) |
| Q2 testnet sub-account per layer family | YES - start with Fabio (item 1), add RSI next |
| Audit 910 (touches PROJECT_VISION) | OVERRIDE granted, read-only audit |

## 4. Mainnet path (later, only after >= 20 clean testnet fills)
- Track A: laptop as 2nd Qwen worker (optional, 30 min).
- Track C: Deribit subaccount MTS-SMOKE, <= 100 USD, key without withdraw, write `.secrets/mainnet.secret.json` yourself.
- Track D: go/no-go with `MyTradingSys/execution/MAINNET_READINESS_CHECKLIST.md`.
Details: `DSA_OPERATOR_ROADMAP.md`.
