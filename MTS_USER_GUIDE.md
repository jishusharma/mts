# MTS User Guide

Last reviewed: 2026-10-06  |  Trading: Deribit **testnet** only  |  Instrument: BTC-PERPETUAL

MTS watches the BTC market, tells you when a setup is forming, and places
your trades with a stop that is always on the exchange. You decide; MTS executes.
Everything runs from one command: **`mts`**.

> Starting Claude sessions, roles, super sessions, broadcast: see `MyTradingSys/system/START_HERE.txt` (the cheat sheet, updated 2026-10-22).

---

## 1. One-time setup

You need: Windows, PowerShell 7, Python 3.10+, Java + Maven (for the market loop).

**Put the shortcuts on your Desktop**

```powershell
pwsh -File C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\scripts\setup\install-desktop.ps1
```

| Shortcut      | What it does                                          |
|---------------|-------------------------------------------------------|
| **MTS**       | Opens the MTS console. Everything below is typed here. |
| **MTS Guide** | Opens this guide.                                     |
| **MTS KILL**  | Emergency stop. Asks you to type `KILL` first.        |

**Testnet key** - create it on test.deribit.com with *read + trade* only (no
withdraw). Save it as `MyTradingSys\execution\.secrets\testnet.secret.json`:

```json
{ "client_id": "...", "client_secret": "...", "env": "test" }
```

Never paste this file into a chat or a document.

**Check it all works**

```powershell
mts test       # offline tests - must end with ALL TESTS PASSED
mts account    # shows your testnet balance - proves the key works
```

---

## 2. The daily flow

```
 mts start  ->  mts status  ->  (alert)  ->  mts plan  ->  mts check  ->  mts trade  ->  mts stop
  loop on       all green?      setup        write it     read the       place it      end of
                                forming                   orders                       day
```

---

## 3. Start the day

Double-click **MTS**, then:

```powershell
mts start      # starts the market loop and its watchdog
mts status     # wait ~1 minute, then check
```

A good `mts status` looks like this:

```
Market loop
  OK    running (loop, watchdog, data feed)
  OK    market state A>L  (bull 2 / bear 1)  updated 12s ago
  last verdict: WAIT_TRIGGER (price not at zone)   setup: ct_short @ ...
Brakes
  OK    no brakes set - trading allowed
```

Any `WARN` or `STOP` line: see section 6.

Optional, when you will trade today: `mts guard` starts the daily-loss guard
in its own window. It closes everything if the day's loss passes 500 USD.

**While you wait:** `mts watch` shows the live dashboard. Alerts pop up on
screen by themselves when a setup gets close to its entry.

---

## 4. Place a trade

### Step 1 - Build the plan

```powershell
mts plan
```

Answer the questions. Press Enter to accept the value in [brackets].

```
  Side (long/short) [long]: short
  Entry (market/limit/ladder) [market]: limit
  Limit price (USD): 90000
  Size in USD (multiples of 10) [100]: 200
  Stop distance from entry, % [2.0]: 1
  Targets, profit % (e.g. 2,5  or  30@2,70@5  or none) [2,5]: 30@2,70@5
  Max loss you accept, USD [50]: 20
  Plan valid for how many hours [2]: 1
SAVED S-lim-0928-1329
```

Targets: `2,5` splits the size equally at +2% and +5%. `30@2,70@5` takes 30%
off at +2% and 70% at +5%.

### Step 2 - Check the orders (sends nothing)

```powershell
mts check S-lim-0928-1329
```

Read three things: the **stop price**, the **target prices**, and
**worst_case_loss_usd**. If anything looks wrong, run `mts plan` again.

### Step 3 - Place it

```powershell
mts trade S-lim-0928-1329
```

It shows the orders again and asks you to type `GO`. Then:

- **Market** entry fills at once.
- **Limit / ladder** entries wait up to 10 minutes (or until the plan
  expires) for a fill. Whatever has not filled by then is cancelled.
- The moment anything fills, a stop order is placed on the exchange.
- A new window, **MTS manage &lt;plan&gt;**, opens. **Leave it open.** It keeps
  the stop the same size as your position as targets fill, and closes out
  when the trade is done.

### Step 4 - While the trade is open

```powershell
mts account    # position, open orders, balance
mts status     # shows which plan is being managed
```

The trade ends by itself when the stop or the last target fills. The manager
window then prints `status: closed`.

### Plan rules (MTS refuses anything outside these)

| Rule                    | Limit                                          |
|-------------------------|------------------------------------------------|
| Size                    | multiples of 10 USD; total at most 10,000 USD  |
| Max loss per plan       | at most 500 USD                                |
| Stop                    | fixed % from entry (no trailing, no breakeven) |
| Plans at once           | one - a trade refuses if a position or order is already open |
| Validity                | a plan can only be traded inside its time window |

### Repeat trades in one line

```powershell
python MyTradingSys\execution\new_plan.py --side long --entry market --size 100 --stop 2 --targets 2,5 --max-loss 50 --hours 2 --yes
```

### Auto-trading (testnet)

```powershell
mts auto       # starts the auto-trader in its own window
mts autolog    # what it did: trades, skips, rejected signals
mts ledger     # closed auto-trades per source: n, win rate, mean net, sum net
```

The auto-trader places trades by itself, through the same plan -> check ->
trade path as above:

- **Tom setups** (`SETUP_FORMING` / `SETUP_CONFIRMED`, net R:R at least 2):
  a limit order at the zone, using the alert's own stop and target. Size 200 USD, max loss 25 USD.
- **Indicator layers** (RSI, Fabio, and any new layer the alert runner emits
  with a side): a market order, stop 1%, target 2%. Size 100 USD, max loss 10 USD.
- One trade at a time. Signals that arrive while a trade is open are logged
  as `skipped_busy`, so every layer still gets counted.
- The brakes in section 5 apply: `mts pause` stops new auto-trades at once.

---

## 5. The three brakes

| Brake          | Command     | What happens                                          |
|----------------|-------------|-------------------------------------------------------|
| Pause          | `mts pause` | No new trades. Open trades keep their stops.          |
| Kill           | `mts kill`  | Cancels every order, closes every position, then pauses. |
| Kill (mainnet) | `mts kill-mainnet` | Same, on the LIVE mainnet account. |
| Daily loss     | `mts guard` | If the day's loss passes 500 USD: closes everything, pauses for the day. |

MTS also pauses itself if something goes wrong during a trade. In every case:

1. `mts account` - see what is actually open.
2. `mts resume` - type `RESUME` to allow trading again.

---

## 6. When something goes wrong

| You see                                   | Do this                                          |
|-------------------------------------------|--------------------------------------------------|
| A trade looks wrong and you want out now  | `mts kill` (or the **MTS KILL** shortcut)        |
| `HALTED: ...` after a trade or in the manager | MTS closed out and paused. `mts account`, then `mts resume` |
| `Trading is paused`                       | A brake is set. `mts status` says which. `mts account`, then `mts resume` |
| You closed the manager window by accident | `mts manage <plan>` - your stop stayed on the exchange |
| `outside validity window`                 | The plan expired. `mts plan` for a new one.      |
| `position or open orders already exist`   | Something is still open. `mts account`.          |
| `not running` or `STALE` in status        | `mts stop`, then `mts start`                     |
| `HALT_DAILY_LOSS is set`                  | Daily loss limit hit. Stop for the day.          |
| Anything else                             | `mts pause`, then read the message calmly.       |

---

## 7. End the day

```powershell
mts stop       # stops the market loop
```

Open trades are not affected: their stops live on the exchange. Keep any
**MTS manage** window open until its trade is closed.

---

## 8. All commands

| Command              | What it does                                              |
|----------------------|-----------------------------------------------------------|
| `mts start`          | Start the market loop and its watchdog                    |
| `mts stop`           | Stop the market loop cleanly                              |
| `mts status`         | One screen: loop, market state, last alert, brakes        |
| `mts watch`          | Live dashboard (Ctrl+C to leave)                          |
| `mts plan`           | Build a trade plan by answering questions                 |
| `mts plans`          | List saved plans, with time left and whether traded       |
| `mts check <plan>`   | Show the exact orders a plan would place (sends nothing)  |
| `mts trade <plan>`   | Place a plan on testnet, then open its manager window     |
| `mts manage <plan>`  | Re-open the manager window for a live plan                |
| `mts account`        | Testnet balance, positions, open orders (read-only)       |
| `mts pause`          | Block all new trades                                      |
| `mts resume`         | Remove the brakes after you have checked the account      |
| `mts kill`           | Emergency: cancel all, close all, pause                   |
| `mts kill-mainnet`   | Emergency on MAINNET: cancel all, close all, pause        |
| `mts guard`          | Start the daily-loss guard in its own window              |
| `mts orphans`        | Check every testnet account for a position no manager owns (may set HALT) |
| `mts auto`           | Start the testnet auto-trader in its own window           |
| `mts runner`         | Start the alert runner (indicator layers) in its own window (only the runner; mts guard starts it too, with the loss monitor and orderflow) |
| `mts market`         | Market guide: MA / RSI / candle state per timeframe + recent layer alerts, each tagged with its backtest verdict (EDGE / NO-EDGE / UNTESTED). Context only, never a trade signal. Also writes `MyTradingSys/runtime/market_guide.md` |
| `mts autolog`        | Last 20 auto-trader decisions                             |
| `mts ledger`         | Closed auto-trades per source: n, win rate, net P/L       |
| `mts missed [hours]` | Missed-trade analysis: chart-observed setups vs what MTS did, scored on 1m bars (read-only) |
| `mts soak`           | Testnet soak report from the execution journal (read-only) |
| `mts wiring`         | Check that every code file is run by something or declared in system/wiring_registry.json |
| `mts desk`           | List open desktop tasks that other sessions posted (post/take/done: scripts/dev/desk.py)  |
| `mts go [slug]`      | Launch the next queued build task in claude (empty queue prints IDLE). Slug = lowercase kebab, names the session MTS-<UTC>-CLI-BLD-<slug>. `-Dry` prints only; run from inside a Claude Code session it always prints only |
| `mts test`           | Run the offline tests (no exchange)                       |
| `mts guide`          | Open this guide                                           |
| `mts help`           | List every command                                        |

Outside the MTS window, run `.\mts.ps1 <command>` from the project folder.

---

## 9. Where things are

| What                     | Where (inside the project folder)          |
|--------------------------|--------------------------------------------|
| Your plans               | `MyTradingSys\execution\plans\`            |
| Trade history, per plan  | `MyTradingSys\execution\journal\`          |
| Brake files              | `MyTradingSys\execution\HALT`, `HALT_DAILY_LOSS` |
| Past brakes              | `MyTradingSys\execution\halt_history\`     |
| Market loop log          | `runtime_data\apparatus_log.txt`           |
| Last alert               | `runtime_data\last_alert.json`             |

---

## 10. Known limits

- Trading is testnet only. The only mainnet command is `mts kill-mainnet` (emergency close).
- One plan at a time on BTC-PERPETUAL.
- The daily-loss guard's profit-and-loss reading is still being verified on
  testnet. Treat it as a backstop, not your only protection.
- Alerts are signals. The decision to trade is always yours.

---

## Keeping this guide current

- Any change to an `mts` command or to a flow above updates this guide in the
  same commit, and moves the *Last reviewed* date.
- `mts test` fails if a command in `mts.ps1` is missing from section 8, or a
  path in section 9 does not exist.
