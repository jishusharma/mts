# Mainnet path, one page (Thinker, 2026-10-25)
MODEL: Sonnet, lite (open on Opus for deep design). Read-only; nothing run. Labels: SOURCED = file:line, OURS = my judgement, NOT_IN_DATA = repo does not say.
Not read: `system/handover/LEAD_RESUME_2026-10-25.md` is not on trunk yet (NOT_IN_DATA). Dev-factory state is taken from STATUS.md (generated 2026-10-23, stale by 2 days).

## Facts re-checked
- The go-live bar IS signed: accepted 2026-10-09, decision D06-gate (system/GO_LIVE_BAR.md:3). `items/T086_go_live_bar.md:12` still says "No receipt": that card is stale, fix it.
- Bar: 200+ closed testnet trades from configs that passed walk-forward fee-net, net P&L > 0, profit factor > 1.2, time exits < 5%, uptime > 95%, all held 30 days in a row (GO_LIVE_BAR.md:6-14).
- No layer has a positive fee-net result: "No layer is AHEAD" (LAYER_REALITY:3). `promoted_setups.json` ships empty (PROMOTION_PIPELINE.md:3). Confirmed.
- 94% of live exits are time exits; the 1%/2%/8-bar bracket was never backtested (LAYER_REALITY:26; T09_live_parity.md:3, observed 97%). Confirmed.
- Only PASS in the verdict table: carry_basis, n 911, +0.042%, not a layer, not live, report unread (LAYER_REALITY:29).
- Repo public until mainnet or first fee-net pass (CLAUDE.md Hard rules). Gate board: no gate moved in 24h; 229 commits in 24h, 72% "other" (STATUS.md:36-37).

## 1. Critical path (ROI order)
| # | Item | Number that moves | Cost | Done when |
|---|---|---|---|---|
| 1 | Find ONE config with a positive fee-net out-of-sample result. Cheapest leads: read the carry_basis report; do the single levels-confluence VALIDATION read (never read, LAYER_REALITY:16) | layers with positive result: 0 to 1 | OURS: 2-4 days of one worker; weekly % NOT_IN_DATA | net R > 0, 95% CI low > 0, n >= 30 (PROMOTION_PIPELINE.md:15), holdout read once |
| 2 | Make live exits equal the tested exits (card t09-f2, already claimed) | time-exit share 94% to under 5% (bar line 4) | OURS: 1-2 days builder, needs restart/reset/API-error tests (CLAUDE.md) | parity test passes; 3 days of testnet exits show under 5% time exits |
| 3 | Promote that config: shadow, then testnet with a size flag | `promoted_setups.json` entries: 0 to 1 | OURS: under 1 day | `promote.py check` and `verify` green (PROMOTION_PIPELINE.md:11-26) |
| 4 | Start the 30-day clock: 200 trades, PF > 1.2, net > 0, one bad day restarts it | clock days: 0 to 30 | 30 calendar days fixed (SOURCED GO_LIVE_BAR:14); this is the long pole, so items 1-3 decide when it starts | trade ledger shows all five numbers true for 30 days |
| 5 | Uptime above 95% over the same 30 days | uptime: 81% on 2026-10-09 (GO_LIVE_BAR:23); today NOT_IN_DATA | live host move is staged, not cut over as of 2026-10-21 (LIVE_HOST_MOVE.md:1); window date unset (:111) | supervisor log shows over 95% |
| 6 | Mainnet mechanics: close B149 (settlement and funding in daily P&L, must close before mainnet, STATUS.md:90); checks #8, #9 open (MAINNET_READINESS_CHECKLIST.md:72-73); operator makes the sub-account, key (no withdraw scope), funds at most 100 USD (:29-33); first order capped at 50 USD (:16) | open mainnet blockers: 3 to 0 | OURS: 1-2 days, mostly operator; can run inside the 30 days | checklist sections A and B all ticked; plus a separate signed real-money decision (GO_LIVE_BAR.md:26) |

Honest read (OURS): items 4-6 are built or scheduled. The whole path waits on item 1. Everything the factory has shipped so far is plumbing; none of it has produced the edge.

## 2. Biggest unknowns and the cheapest test
1. Is there any edge after fees? Kurisko fee is 2.1-2.3 R on 1m (LAYER_REALITY:12). Test: read the carry_basis report and do the one levels-confluence validation read. Cost: hours, not days.
2. Does the generic bracket hide an edge that a sourced exit would show? Test: replay the two best DEV candidates with their own exits (replay harness exists, T09_live_parity.md:5). Cost: OURS 1 day.
3. Does carry_basis (a carry trade, not a chart layer) fit the system at all? Needs real spot-basis margin (claim funding-carry-with-real-spot-basis-margi is 164h old, stale). Test: ask the claim owner for a status line; NOT_IN_DATA otherwise.
4. Are testnet fills and fees like mainnet? NOT_IN_DATA. Test: the 50 USD first-order step (checklist :16) is the only real answer; run it only after the bar.
5. Is today's uptime above 95%? NOT_IN_DATA. Test: read supervisor_log over the last 7 days (one command).
6. Does the settlement/funding P&L logic match the exchange (B149)? Test: `execution/capture_txlog_settlement.py` on a captured testnet log (STATUS.md:90).

## 3. Stop or delete (does not move the path)
OPERATOR DECISION 2026-10-25: NO to every layer, lab-fixture and blind-mark item below. Nothing is demoted, parked or deleted; no layer is dropped until he has looked at it in the simulator. Layers are reviewed by card `layer-review-after-simulator` (starts after the backtest simulator ships; output: one integration map of how layers combine and the confluence rule that decides which trades fire). Releasing stale claims and the commit-churn cleanup stay allowed (dev hygiene).
Original proposal (not adopted), all reversible, none touch the live tree:
- Stop all work on DEAD layers (8 of them, LAYER_REALITY:3): RSI divergence, funding/CVD fade, cross-guidance/volume/candle patterns/ma_daily/bigtrade, session_momentum, turn_of_candle (71% of live alerts, DEAD, LAYER_REALITY:20), Tom's old BTC encoding (holdout -0.32 R, n=254, :7).
- Stop the Codex lab fixtures for provisional-dead layers: t02-f3-fixtures-wlow-session-levels, t02-f3-fixtures-fabio-v3-grid (STATUS.md:79-81; layers listed DEAD at LAYER_REALITY:21).
- Park Tom/Fabio/Malkan/Krown G3 blind-mark work until item 1 returns (no gate moved in 24h, STATUS.md:36). Keep Krown only if the DEV study is cheap.
- Rituals: release stale claims (about 20 older than 40h in the sync.py start output); close the 35 overdue screenshot intakes (STATUS.md:60); stop commit churn: 72% "other" is over the 30% cap (STATUS.md:37). Cost of keeping: budget, no number moves.
- Do not delete: GO_LIVE_BAR, promotion pipeline, kill switch, the 13 offline mainnet checks (MAINNET_READINESS_CHECKLIST.md:8-22): they are the real asset.
- Repo stays public until item 1 passes; then go private (CLAUDE.md rule). No-undo once code is copied, so keep the existing rule, no earlier flip.

## 4. First 3 actions, next 7 days
1. Sim-desk worker (Sonnet, one card): read the carry_basis report and run the one levels-confluence validation read; report positive/negative in 5 lines. Owner: DSA/sim desk lane. Done: two verdict rows in VERDICTS.csv.
2. Builder holding t09-f2 (JIS-NB claim, 8h old at boot): finish live exits equal tested exits with restart/reset/API-error tests; ship through `sync.py ship`. Done: time exits under 5% in a 3-day testnet sample.
3. Operator, 5 minutes: say yes/no to the section 3 stop list. Lead then files the demote and claim-release cards and fixes the stale T086 card (it says "no receipt", the bar is signed).
