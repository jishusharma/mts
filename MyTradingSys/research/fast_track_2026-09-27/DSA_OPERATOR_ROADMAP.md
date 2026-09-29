# DSA + Jishu roadmap - road to a Deribit MAINNET smoke test (written 2026-09-29 ~04:40 IST, supervisor)

Who does what: **DSA** = the operator's chat model in Chrome (not Claude; can also become a queue worker - DSA_BROWSER_WORKER_PLAN.md). **Jishu** = operator, hands on keys,
exchange UI, and the laptop. **Code mode** (desktop supervisor + workers) builds and tests; it never touches mainnet,
keys or .secrets/. Mainnet orders are only ever placed by Jishu typing the confirmation string himself.

Goal: ONE tiny mainnet round trip (<= 50 USD notional, BTC-PERPETUAL, stop + target attached, then flat) that proves
the real path end to end. Not a strategy test. Do the tracks in order; each has a DONE check.

## Track A - Laptop as second worker (Jishu, 30 min, any time)
A1. Install Ollama on the laptop; `ollama pull qwen3-coder:30b` if RAM >= 32 GB, else `qwen2.5-coder:14b`.
A2. Copy `scripts/worker/nuc-worker.ps1` + `setup-nuc.ps1` to the laptop; point it at the same NUC-QUEUE share
    (`Dumps/workers/NUC-QUEUE`), host label `LAPTOP`. It claims tasks by name like the NUC, so both drain one queue.
A3. DONE when `python scripts/worker/queue_tool.py status` shows a second WORKER line with host LAPTOP.
    If the laptop sleeps, the task goes stale and the NUC re-claims it - no harm. Tell code mode the model name.

## Track B - DSA reads + rules consolidation (DSA with Jishu pasting; ~1 h)
B1. Consolidate the 35 new FAB-/T- rules (extracts committed 2d8b1b0, f19d8e2, 93a8940, ad36fef) into the master lists;
    map Topic `exit` -> management/target. Output: one file per author; Jishu saves it, code mode runs the quote gate.
B2. Ruling needed (Jishu decides, DSA drafts options): Tom-vs-Fabio override (who wins when they disagree) and
    T058 decisions (history fetch depth; hedge timing). DONE when written into SUPERVISOR_LOG.md.

## Track C - Mainnet account setup (Jishu at Deribit UI, DSA guides step by step; ~45 min)
Do NOT paste any key into chat, DSA or code mode. DSA only explains screens.
C1. Create a Deribit **subaccount** named `MTS-SMOKE` (never the main account). Enable 2FA on the main account.
C2. Transfer <= 100 USD equivalent (BTC or USDC) to the subaccount. Nothing else lives there.
C3. Create an API key ON THE SUBACCOUNT: scopes trade:read_write + account:read + wallet:read ONLY
    (NO wallet:read_write - the code refuses keys that can withdraw). IP whitelist = desktop public IP.
C4. Jishu writes `.secrets/mainnet.secret.json` himself: `{"env": "mainnet", "client_id": "...", "client_secret": "..."}`.
    The code refuses a secret whose env does not match (both directions).
C5. DONE when Jishu runs the offline refusal test and read-only check that code mode will list in
    `MyTradingSys/execution/MAINNET_READINESS_CHECKLIST.md` (being built now) - all green.

## Track D - Go / no-go (Jishu, with the checklist; 10 min)
All must be true: checklist machine items green; testnet chain 6/6 + 4/4 + 4/4 on the same commit; daily-loss guard
(L6 part 2) built; kill switch command tested on testnet; testnet auto-trader has >= 20 real (non-smoke) fills with
no HALT/unprotected-position events; Jishu at the desk for the whole trade.

## Track E - Smoke trade (Jishu types, code mode watches read-only)
E1. `mts plan` a 20-50 USD limit with stop + target -> `mts check` -> `mts guard` -> mainnet run command from the
    checklist; type the confirmation string at the prompt.
E2. Watch: stop and target live on the exchange within seconds of fill. If not -> kill switch command at once.
E3. Close (target, stop or manual), confirm flat + no open orders, export the fills. DONE = journal row + screenshot.
Abort criteria: any error on placement, stop missing > 10 s, slippage > 0.2 %, any unexpected order -> kill switch.

## What code mode is doing meanwhile (no operator needed)
Update 22:30 IST: CITATION FLAGS (operator): C3 source = arXiv 2607.09426 Kim & Hansen (order imbalance at quarter-hour opens -> 4-12 h returns) - being verified + C3 backtest running; T055a cites the wrong paper (Kim & Hansen, T1->T2); T055b misquotes the 44-concept ICT/SMC study. Correction notes go on top of both files. Laptop doctrine: WORKSTATION_MODES.md. Notes to the supervisor: SUPERVISOR_INBOX.md.
Update 12:47 IST: mainnet PnL tx-type allow-list + orphan watchdog committed (924d7a0, d115b0d; watchdog not yet scheduled). Testnet trade open 5 h in profit; layer trades have no time exit, so data comes slowly - decide Q1 (per-layer bracket/time exit) and Q2 (sub-accounts).
Update 09:47 IST: mainnet-ready build + stop-out fix committed 2b8b19a (testnet 14/14). Auto-trading resumed; fills are slow because one account = one trade at a time - answer Q2 (testnet sub-accounts) to multiply data. Audit 910 waits for your OVERRIDE (touches PROJECT_VISION).
Update 06:50 IST: DSA browser worker built (194ee7c; you calibrate it - DSA_BROWSER_WORKER_PLAN steps 3-7). C3 promoted; T055 C1/C2 no edge (3672305). Found + fixing a real bug: a stopped-out trade was reported as 'unexplained flat' and halted - must be fixed before mainnet. Fabio 108-111 Qwen extractions held -> good first jobs for the DSA lane.
S5 mainnet flag (4 gates + 50 USD mainnet cap), L6 part 2 PnL source, guard re-audit, readiness checklist; testnet
auto-trading gathering data 24/7; hourly Haiku gate on NUC builds; Fabio holds + formula audit repacked to the queue.
Open questions from NEXT_SESSION_PLAN s9 (layer brackets, testnet sub-account per layer family, keep no-edge layers,
500 USD testnet cap) still use the defaults until Jishu answers.
New questions (2026-09-29): (1) Mainnet kill switch currently needs the typed confirmation too - supervisor recommends
allowing it with flag + mainnet secret only (it can only reduce risk); Deribit UI is the fallback. (2) Confirm the
transaction-log types excluded from daily PnL (deposit, withdrawal, transfer*) against the Deribit docs (DSA can check).
(3) Build still open: G-d account-wide sweep if a position_manager dies (supervision design).
