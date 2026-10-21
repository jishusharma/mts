# Plugging a layer into the simulator desk

One layer = one file in `studies/`. The desk finds it at start. No edit to `desk.py` and no edit to the page.
`studies/levels.py` is the working example. `test_plugin.py` shows how small a file can be: it uses a 30-line dummy study.

## What the layer file must provide

| Name | What it is |
|---|---|
| `ID`, `TITLE` | A short id (used in the trial ledger) and a plain title for the page. |
| `params()` | The settings boxes. Each box has a plain label. A box is a list of choices, a number with min/max, or a date. |
| `normalize(p)` | Fills in defaults and checks the typed values. Bad input gives a plain error such as "please type a number". It must keep `start`/`end` inside the development window. |
| `label(q)`, `describe(q)` | A short ledger label, and one plain sentence saying what this setting does. |
| `run(q, progress)` | Runs the backtest and returns one row per trade idea. The rows hold `day`, `touch_t`, `net` (R after fees), `gross`, `fees` and `filled` (did it actually trade). They also hold `all_days` and `refs`, where `refs` is a handle used to redraw one trade. |
| `chart_trade(ref, q)` (optional) | The 1m bars of that day, side, level, entries (time and price), stop, target, exits (time, price and reason) and net R. Without this function the desk shows no charts. |
| `PRIOR_TAG`, `build_cache()` (optional) | The ledger tag of earlier tries made outside the desk, and a one-off data cache build (`desk.py --build`). |

## What the desk does for every layer

- **Date lock:** only the development window (2022-04-01 to 2024-06-30) can be run. The validation and held-back data are never offered.
- **Verdict:** counts filled trades only, and states the 95 % range of the average:
  - PASSED when the whole range is above zero.
  - FAILED when even the top of the range is below +0.10 R and the sample was big enough to see +0.10 R.
  - Otherwise NOT ENOUGH DATA.
- **Trial ledger:** each new setting writes one row to `layer_lab/TRIALS.md` before the result shows. A repeat writes nothing. The page shows how many tries were made.
- **Charts:** the 3 winners and 3 losers closest to the typical winner and loser, with date and time in UTC.
- **Questions panel:** the open decisions are shown on the page, and answers are saved to `cache/answers.jsonl`, which is local and never committed. New questions go in `questions.json`.

## Which layers fit (survey 2026-10-21, read-only)

"Fits now" means a layer already returns timestamped trades. **No layer does that today**, so every layer below needs a small adapter or does not fit yet.

| Layer | Verdict | Why |
|---|---|---|
| Levels study | **Fits (plugged in)** | `studies/levels.py`. |
| Tom (BTC) | **Small adapter** | `backtest/tom_bt.py` runs on cached rows and 1m bars, with no Java needed. Its trades carry bar numbers, not times, so it needs a time wrapper and a settings list. The current Tom rules are on STOP while v2 is written (LAYERS.md), so wrap v2 only. |
| CryptoCred | **Small adapter** | `layers/cryptocred/cc_bt_adapter.py` already turns signals into trades. Its tested setups failed. |
| RSI | **Small adapter** | `layers/rsi/run_rsi_backtest.py` turns events into trades with a fixed stop and target. |
| Session levels / momentum, funding fade, big-trade fires | **Small adapter, low value** | All closed with no edge, or their held-back data is still unread. |
| Fabio (order flow, v3) | **Does not fit yet** | The order-flow bars start 2024-12-02, which is after the development window ends, and the raw trades needed to rebuild them are not on disk. Fabio is also being redefined. |
| Tom DAX | **Does not fit** | It trades a different market, and no DAX data has been bought. |
| Detectors and studies (wavetrend, pitchfork, krown, volume, candle patterns, guidance matrix, callers) | **Does not fit** | They flag events but are not trading rules, so there are no trades to simulate. |
| Live engine | **Does not fit** | It is execution, not a backtest. |

Which layer goes first is a question on the desk page. Nothing is ported until it is answered.
