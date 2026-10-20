# D3. Review of GO_LIVE_BAR.md (D06-gate, accepted 2026-10-09)

Proposal only. The bar file is not edited; the operator answers q-v1-bar (DECISIONS_PROPOSED.md).

## The bar as written
200 closed testnet trades from configs that passed walk-forward (OOS net R > 0, 95 % CI > 0, fees included, holdout read
once); net P&L > 0; profit factor > 1.2; time-outs < 5 % of closes; stack uptime > 95 %; all of it held for 30 consecutive
days; one failing day restarts the clock. Measured from `runtime_data/trade_ledger.jsonl` and the supervisor log.

## Where we stand against it (RESULT, from files on disk)
| Bar item | Today | Source |
|---|---|---|
| Walk-forward-passed configs | 0 (`promoted_setups.json` entries: 0; every LAYERS.md backtest row negative or no edge) | LAYERS.md, execution/promoted_setups.json |
| 200 closed trades from such configs | 0 by definition; the 27 sources trading now are grandfathered, review_by 2026-10-23 | auto_trader_config.json |
| Time-outs < 5 % | 97 % time-exit (T085) on the grandfathered flow | GO_LIVE_BAR.md status 2026-10-09 |
| Uptime > 95 % | 81 % over 120 h on 2026-10-09; no newer number readable off the desktop (mirror STALE 2026-10-19, flags HALT, HALT_DAILY_LOSS) | GO_LIVE_BAR.md, runtime_data/_mirror brief |
| 30 consecutive days | clock has never started | same |

So the blocker is research (no passed config), not engineering. The bar itself is mostly right.

## Keep (still right)
- Fee-net OOS with CI > 0 as the only entry ticket. This is what separates a system from a story.
- Holdout read once. Non-negotiable; the pooled-trend card that reads it is why D1 closes that card.
- 30 days of live testnet behaviour. Backtests do not show reconnects, partial fills or API errors.
- Uptime as a bar item. A trading stack that is down misses stops as well as entries.

## Missing (propose to add)
- M1 Restart safety: after any restart or reconnect, every accumulator either backfills or marks itself INVALID and the
  trader fails closed. Evidence of the gap: `StateCodeEmitter.java:177-189, 454-479` (session CVD -367.4 BTC, VWAP missing
  26.8 % of volume, gap_audit_2026-10-19 GAP-2). A bar that counts trades taken on a wrong CVD counts the wrong thing.
- M2 Settlement blindness: L6/B149 (daily_loss_monitor.py:510 reads one subaccount). Mainnet needs the loss cap to see
  every account it protects. Bar item: daily-loss cap verified against the exchange ledger once per day, tested.
- M3 Stop parity: the stop on the exchange equals the stop in the ledger, including after a bracket amend (gap-g7, q-gap-b).
  Bar item: 0 parity violations in the 30-day window.
- M4 Uptime defined on the mainnet host and measured by a heartbeat file, not by a reviver that is itself a scheduled task.
  Today 15 Windows tasks keep the stack alive against SCHEDULING_POLICY.md; the bar cannot be read if they go (q-v1-keepers).
- M5 Per-config minimum: at least 30 closed trades per promoted config inside the 200, so one config cannot carry the bar.
- M6 Kill-switch drill: one deliberate HALT and one deliberate restart during the 30 days, with the expected state after each
  written before the drill (EXPECT) and compared (RESULT).
- M7 Mainnet first step written now, not later: tiny fixed size, an experiment stop (for example 20 trades or -5 R), and
  `trade_blocklist` as the only way back. It belongs beside the bar so the bar is read as "what unlocks the next decision".

## Excessive or fragile (propose to change)
- "One failing day restarts the clock" makes a single exchange outage or a Windows update erase 29 good days. Proposal: a
  rolling 30-day window in which at most 1 day fails uptime, and the P&L and PF items are read over the whole window.
- "Time-outs < 5 %" is a symptom, not a bar item. Exits are a layer property, fixed in each layer's pre-registration (T085
  is a Tom-flow number). Proposal: keep it as a per-layer promotion condition (time-exit share declared in pre-reg, measured on
  DEV), drop it from the live bar.
- "200 closed trades in 30 days" with 1-2 layers: EXPECT per LC pre-reg counts (levels_hold.md) a 4h/1d layer gives a handful
  of trades per week. Two layers may not reach 200 in 30 days. Proposal: 200 trades or 60 days, whichever comes first, with
  the per-config minimum M5 still binding. If the operator keeps 200 in 30 days, the plan must admit a third layer or an
  intraday one, which D4 argues against for v1.
- PF > 1.2 is fine; net P&L > 0 is then redundant but harmless. Keep both for readability.

## What changes if the operator says yes
GO_LIVE_BAR.md gets a "v1 revision 2026-10-xx" block with M1-M7 and the two changes above; D2 acceptance points at it; the
S2 cards in D7 are exactly M1-M4; S5 is the 30/60-day window.
