# 24-Hour Critical Work Audit & Ad-Hoc Verification Report (2026-10-30)

**Auditor**: Gemini 4 Argon (Low) — `JIS-NUC` (`jis-nuc/gemini-24h-critical-audit`)
**Scope**: High-level ad-hoc verification and code/test audit of the critical commits shipped in the last 24 hours (`2026-10-29T13:00Z` to `2026-10-30T13:00Z` on `fast-track` up to `0e638993b`).
**Actionable Cards Filed for Claude AI**:
1. `wave1-item2-settlement-window-and-double-count` (`SONNET` / `IMPORTANT`)
2. `spikefade-a-s1-cap-misapplied-and-replay-drift` (`SONNET` / `IMPORTANT`)
3. `cbp-run-prompt-metadata-and-analyst-levels-hit-bug` (`JIS-NB` / `IMPORTANT`)
4. `liq-accumulator-shutdown-queue-drain` (`JIS-NB` / `IMPORTANT`)

---

## Executive Summary of Critical Gaps Found

| # | Area | Commits Audited | Critical Gap / Defect Found | Assigned Card for Claude AI |
|---|---|---|---|---|
| **1** | **Wave-1 Item 2: Mainnet/Testnet Settlement PnL** | `513698432`, `c511a40dc`, `926980721` | **Solved the `-4.82e-06 BTC` "mystery" AND uncovered a live UTC-day double-counting bug**: (a) On Deribit testnet, no `08:00:00Z` settlement entry occurred on `2026-10-10` in either `_11.json` or `_13.json`, so `account_summary.session_rpl` (`+1.17e-06` in `_11.json`, `+2.56e-06` in `_13.json`) is the **36-hour cumulative cashflow since `2026-10-09T08:00:00Z`** (`sum(cashflow) = +1.18e-06` / `+2.58e-06`), NOT since `2026-10-10T08:00:00Z` (`-3.65e-06`). Adding 36h `session_rpl` to 4h `change` in `test_recorded_settlement_identity` (`test_mainnet_pnl.py:130-154`) caused the exact `-4.82e-06 BTC` discrepancy (`+1.17e-06 - (-3.65e-06) = +4.82e-06`). (b) Worse, in live `daily_loss_monitor.py:349-353`, querying `get_transaction_log` from `00:00 UTC` on a day when an `08:00 UTC` settlement fires causes `mainnet_pnl.realized_btc()` to **double-count** every trade closed between `00:00 UTC` and `08:00 UTC` (`profit_as_cashflow=True` on the trade AND swept into `settlement.change` at `08:00 UTC`). | `wave1-item2-settlement-window-and-double-count` |
| **2** | **Wave-1 Item 3 & 4: SpikeFade Detector, Cap & Replay** | `c4ad479e0`, `1dce15d9e`, `80e6ff471` | **Three-way SpikeFade regression**: (a) Commit `80e6ff471` (`SpikeFadeDetector.java:189-197`) misapplied card `spikefade-prior-day-high-proxy-cap`: instead of capping `priorHigh` (`dayHigh[LOOKBACK-1]`), it capped `A-S1` stop selection (`<= 3%`) and fell back to `A-S2` (`high + 20.0` DAX points = **`$20` stop on BTC!**), making the broken `$20` BTC stop trigger *more* frequently while leaving the card `blocked`. (b) Commit `c4ad479e0` dropped the `A-C2` (`lastClose > priorHigh`) gate in `SpikeFadeDetector.detect()`, which silently dropped `A-C2` for `SpikeFadePaths.java:13` (`A2`/`A3`) and `SpikeFadeProfile.java:13`. (c) `ItemFourReplay.java:188` still enforces `G4_A-C2_CLOSE_NOT_ABOVE_PRIOR_DAY_HIGH`, so the diagnostic replay contradicts `SpikeFadeDetector.detect()` on 129 bars of `2026-10-29`. | `spikefade-a-s1-cap-misapplied-and-replay-drift` |
| **3** | **CBP Runner & Analyst Levels / Live Aid** | `358a0e50a`, `e4b325418`, `14f601e2c`, `966f15bbc` | **Silent metadata drop & pre-publish `HIT` look-ahead**: (a) `scripts/dev/cbp_run.py:43-51,150` executes `PROMPT % {"analyst": ..., "published": ..., "title": ...}` against a `PROMPT` string containing **zero `%` format placeholders**, silently discarding `analyst`, `published`, and `title` on every LLM extraction call. Also, a single video failure raises `RuntimeError` at line 212 before `write_stamp()` at line 234, leaving `stamp.json` stale (`cbp-daily-firing-gap`). (b) `scripts/dev/analyst_levels.py:84` computes `t0` from date-only `published` (`YYYY-MM-DD` -> `00:00:00 UTC`), so `mark()` checks 1h bars from `00:00 UTC` of the publish day—hours *before* the video was recorded—falsely marking levels as `HIT`. (c) `analyst_levels.py:35-50` parses non-price `k` numbers in `40k..200k` (e.g. `"Over 100k liquidations"` -> `100000.0`) and misses `"76k-77k"` in `_RANGE_K`. | `cbp-run-prompt-metadata-and-analyst-levels-hit-bug` |
| **4** | **Live Liquidation Log Wiring & Shutdown** | `4a038ed5b` | **Dropped liquidation events on shutdown**: (a) `BinanceLiquidationAccumulator.java:219-224` calls `logWriter.interrupt()` in `shutdown()`, causing `logLoop()` (`lines 80-92`) to exit immediately on `InterruptedException` **without draining `logQueue`**, losing queued liquidation events on JVM stop/restart. (b) `Main.java:75-80` hardcodes `LIQ_LOG_SYMBOLS = List.of("BTCUSDT", "ETHUSDT")` regardless of the CLI `<symbol>` passed to `Main statemachine <symbol>`. | `liq-accumulator-shutdown-queue-drain` |
| **5** | **Backtest Cost-Constant Gate** | `2d7d4d49c`, `8daa21e51` | **Regex bypass in `test_no_own_costs.py:18`**: `ASSIGN` only matches `NAME = <digit>` at line start, missing parenthesized expressions (`FEE_RT = (5 + 5) * 1e-4`), tuple unpacking (`MAKER_FEE, TAKER_FEE = ...`), and default arguments (`fee_bps=5.0`). | Included in audit report; minor follow-up noted in Card 1/report |

---

## Detailed Findings & Empirical Verification

### Finding 1: Wave-1 Item 2 Settlement Identity Mystery Solved + Live Pre-08:00 UTC Double-Count Bug

#### 1.1 Commits & Files Audited
- `513698432` — `MyTradingSys/execution/test_mainnet_pnl.py`, `MyTradingSys/research/critical_test_wave1_2026-10-30/ITEMS_1_2_5.md`, `MyTradingSys/research/critical_test_wave1_2026-10-30/item2_settlement_identity.py`
- `c511a40dc` — `MyTradingSys/system/tasks/settlement-capture-testnet-second-log.json`
- `926980721` — `MyTradingSys/research/critical_test_wave1_2026-10-30/REVIEW_ITEM2_GEMINI.md`
- `MyTradingSys/execution/mainnet_pnl.py` & `MyTradingSys/execution/daily_loss_monitor.py`

#### 1.2 Why `test_recorded_settlement_identity` Failed by `-4.82e-06 BTC`
In `513698432`, `test_mainnet_pnl.py:130-154` (`test_recorded_settlement_identity`) was marked `@unittest.expectedFailure` because on the 3 trades after `2026-10-10T08:00:00Z` in `txlog_capture_2026-10-10_jishu_11.json`:
- `mainnet_pnl.daily_pnl_btc(post_08, upl=0.0)` returned `-5.45e-06 BTC` (`sum(change) = -1.80e-06` + `sum(cashflow) = -3.65e-06`).
- The test expected `sum(change for post_08) + account_summary["session_rpl"] = -1.80e-06 + 1.17e-06 = -6.30e-07 BTC`, leaving an unexplained `-4.82e-06 BTC` gap, which prompted filing `settlement-capture-testnet-second-log` (`c511a40dc`).
- Meanwhile, `REVIEW_ITEM2_GEMINI.md` (`926980721`) violated the review card's `done_when` by summing over all 13 entries instead of the post-`2026-10-10T08:00:00Z` window, and falsely claimed `session_rpl` excludes commissions.

**Ad-Hoc Empirical Proof**:
Inspecting all 13 entries of `txlog_capture_2026-10-10_jishu_11.json` and all 6 entries of `txlog_capture_2026-10-10_jishu_13.json`:
```text
Entry 11: 2026-10-09T08:00:00Z settlement  change=-1.59e-06  cashflow=-1.59e-06
Entry 10: 2026-10-09T09:31:18Z trade       change=-6.1e-07   cashflow=-4.0e-08   pac=True
Entry  8: 2026-10-09T19:45:11Z trade       change=-6.1e-07   cashflow=+4.70e-06  pac=True
Entry  6: 2026-10-10T02:31:22Z trade       change=-6.1e-07   cashflow=-8.2e-07   pac=True
Entry  4: 2026-10-10T06:15:42Z trade       change=-6.1e-07   cashflow=+9.9e-07   pac=True
Entry  2: 2026-10-10T09:15:29Z trade       change=-6.0e-07   cashflow=-3.05e-06  pac=True
Entry  0: 2026-10-10T12:15:58Z trade       change=-6.0e-07   cashflow=-6.0e-07   pac=True
```
1. Notice there is **no `settlement` entry at `2026-10-10T08:00:00Z`** in either `_11.json` or `_13.json`!
2. Because Deribit testnet did not emit an `08:00:00Z` settlement reset on `2026-10-10`, `account_summary["session_rpl"]` at `2026-10-10T12:20:32Z` had been accumulating since the last settlement at **`2026-10-09T08:00:00Z`** (36 hours):
   - In `_11.json`: $\sum_{\text{ts} > \text{2026-10-09 08:00Z}} \text{cashflow} = -4\text{e-}8 + 4.70\text{e-}6 - 8.2\text{e-}7 + 9.9\text{e-}7 - 3.05\text{e-}6 - 6.0\text{e-}7 = \mathbf{+1.18\times 10^{-6}\text{ BTC}}$ (matches `session_rpl = +1.17e-06 BTC` within per-fill rounding!).
   - In `_13.json`: $\sum_{\text{ts} > \text{2026-10-09 08:00Z}} \text{cashflow} = +6.28\text{e-}6 - 3.70\text{e-}6 = \mathbf{+2.58\times 10^{-6}\text{ BTC}}$ (matches `session_rpl = +2.56e-06 BTC`!).
3. The net cashflow between `2026-10-09T08:00:00Z` and `2026-10-10T08:00:00Z` in `_11.json` is $-4\text{e-}8 + 4.70\text{e-}6 - 8.2\text{e-}7 + 9.9\text{e-}7 = \mathbf{+4.83\times 10^{-6}\text{ BTC}}$.
4. That `+4.83e-06 BTC` (prior 24h cashflow still sitting inside `session_rpl`) is the **exact `-4.82e-06 BTC` difference** between `code = -5.45e-06` and `expected = -6.30e-07` in `test_recorded_settlement_identity`!

#### 1.3 Live Double-Counting Bug in `mainnet_pnl.py` + `daily_loss_monitor.py`
Look at how `daily_loss_monitor.py:349-353` calls `mainnet_pnl.daily_pnl_btc`:
- `daily_loss_monitor.py` fetches `get_transaction_log` starting at **`00:00 UTC`** (`_day_start_ms(state["date"])`).
- On Deribit futures (`BTC-PERPETUAL`), every closing trade log entry has `profit_as_cashflow: True` permanently recorded on the log entry (`cashflow = realized_pnl`, `change = fee`).
- When an `08:00 UTC` settlement **does** occur on that UTC day, Deribit writes a `type == "settlement"` entry whose `change` sweeps the session's `cashflow` into the cash balance.
- `mainnet_pnl.realized_btc(entries)` (`MyTradingSys/execution/mainnet_pnl.py:42-61`) sums `change` on all `settlement` entries **AND** sums `change + cashflow` on all `trade` entries with `profit_as_cashflow=True`!
- Consequently, any trade closed between `00:00 UTC` and `08:00 UTC` on a day that also contains an `08:00 UTC` `settlement` entry has its `cashflow` counted **twice**: once in the trade's `cashflow` and a second time inside the `08:00 UTC` `settlement.change` (plus the `08:00 UTC` `settlement.change` also sweeps `08:00–24:00 UTC` PnL from the *previous* UTC day into today's UTC PnL!).
- **Fix required**: For a window `[t_start, t_end]`, realized PnL over the trades in that window is simply $\sum_{\text{trades}} (\text{change} + \text{cashflow}) + \sum_{\text{delivery}} \text{change}$ plus funding (Wait: on Deribit, funding is included in `settlement.change` / `settlement.total_interest_pl`, whereas trade PnL is already in `trade.cashflow`!). Including `settlement.change` in `realized_btc()` sweeps prior-day `[08:00, 24:00)` trade PnL into the current UTC day and double-counts `[00:00, 08:00)` trade PnL.

---

### Finding 2: SpikeFade `80e6ff471` Misapplied Cap (`$20` BTC Stop Fallback) & `c4ad479e0` Replay/Paths Drift

#### 2.1 Commits & Files Audited
- `80e6ff471` — `src/main/java/datafeed/SpikeFadeDetector.java`, `src/test/java/datafeed/SpikeFadeCriticalWave1Test.java`, `MyTradingSys/system/tasks/spikefade-prior-day-high-proxy-cap.json`
- `c4ad479e0` — `src/main/java/datafeed/SpikeFadeDetector.java`, `src/main/java/datafeed/SpikeFadePaths.java`, `src/main/java/datafeed/SpikeFadeProfile.java`
- `1dce15d9e` — `MyTradingSys/research/critical_test_wave1_2026-10-30/ItemFourReplay.java`, `ITEM4_REPLAY_2026-10-29.md`

#### 2.2 `80e6ff471` Capped `A-S1` Instead of `priorHigh`, Triggering the Broken `$20` `A-S2` Stop on BTC
- Card `spikefade-prior-day-high-proxy-cap.json` (`lines 14, 53-57`) was filed because `priorHigh = dayHigh[LOOKBACK - 1]` (the proxy prior-day high used for `A-C2`) had no distance cap, and specified: *"SpikeFadeCriticalWave1Test: proxy day-high beyond the cap returns null, within cap fires."*
- Instead, commit `80e6ff471` modified `SpikeFadeDetector.java:189-197` to cap **A-S1 stop-loss selection**:
  ```java
  if (d > high && (d - high) / high * 100.0 <= A_S1_MAX_DISTANCE_PCT && d < nearestAbove) {
      nearestAbove = d;
  }
  ```
- When `nearestAbove` is beyond `3%` (`A_S1_MAX_DISTANCE_PCT = 3.0`), `detect()` does **not** return `null`; instead, at `lines 195-197`, it falls back to `A-S2`:
  ```java
  boolean useAS1 = Double.isFinite(nearestAbove);
  double stop = useAS1 ? nearestAbove : high + A_S2_BUFFER_PTS;
  ```
  where `A_S2_BUFFER_PTS = 20.0` (20 DAX index points = **`$20` on a `$70,000` BTC price**, i.e., `0.03%` above the bar high—flagged in `ITEM3_SPIKEFADE_CLASSIFYSTATE.md:17` Finding A5 as a critical DAX-to-BTC unscaled bug!).
- Thus `80e6ff471` actually **increased** the frequency of the broken `$20` BTC stop fallback whenever prior session highs are `>3%` away, while leaving `spikefade-prior-day-high-proxy-cap.json` in `blocked` status!

#### 2.3 `c4ad479e0` Dropped `A-C2` Gate in `SpikeFadeDetector`, Breaking `ItemFourReplay.java` and Silently Altering `SpikeFadePaths` / `SpikeFadeProfile`
- Commit `c4ad479e0` removed `if (!(lastClose > priorHigh)) return null;` from `SpikeFadeDetector.java:185`, turning `c2_above_prior_day` into a passive boolean field on `Signal`.
- However:
  1. `SpikeFadePaths.java:13` (`// Path A2 and A3 entry evaluation on top of a Path A1 spike bar (A-C1, A-C2 already true)`) and `SpikeFadeProfile.java:13` both call `SpikeFadeDetector.detect(...)` as their base gate—so removing `A-C2` from `SpikeFadeDetector.detect()` silently removed the `A-C2` gate from `A2`, `A3`, and `SpikeFadeProfile` as well.
  2. `MyTradingSys/research/critical_test_wave1_2026-10-30/ItemFourReplay.java:188` still has:
     ```java
     if (!(b.c[last] > priorHigh)) return "G4_A-C2_CLOSE_NOT_ABOVE_PRIOR_DAY_HIGH";
     ```
     So `ItemFourReplay.gate()` reports `G4_A-C2_CLOSE_NOT_ABOVE_PRIOR_DAY_HIGH` as a blocking gate on 129 bars of `2026-10-29` where `SpikeFadeDetector.detect()` no longer blocks on `G4`!

---

### Finding 3: `cbp_run.py` Silently Drops Analyst/Date/Title Metadata & `analyst_levels.py` Pre-Publish `HIT` Look-Ahead

#### 3.1 Commits & Files Audited
- `358a0e50a`, `e4b325418` — `scripts/dev/cbp_run.py`, `scripts/dev/cbp_schedule.py`
- `14f601e2c`, `966f15bbc` — `scripts/dev/analyst_levels.py`, `MyTradingSys/tools/live_aid/build_analyst_data.py`, `MyTradingSys/tools/live_aid/live_aid_indicators.js`

#### 3.2 `cbp_run.py:150` String Interpolation No-Op (`PROMPT % dict` Drops All Metadata)
In `scripts/dev/cbp_run.py:43-51`:
```python
PROMPT = (
    "Extract structured market pointers from this crypto analyst transcript. "
    "Respond with ONE JSON object ONLY, no prose or fences, matching: "
    '{"bias":"BULL|BEAR|NEUTRAL|MIXED","symbols":["BTC",...],'
    '"pointers":["<=25 words, verbatim from the transcript",...]}. '
    "bias is the analyst's directional lean for BTC over the next 1-5 days. "
    "pointers MUST be 1 to 6 verbatim quotes (<=25 words each) stating a "
    "concrete level, trigger, or invalidation; never paraphrase.\n\nTRANSCRIPT:\n"
)
```
And at `scripts/dev/cbp_run.py:150`:
```python
prompt = PROMPT % {"analyst": analyst, "published": published, "title": title.replace('"', "'")}
```
Because `PROMPT` contains **no `%(analyst)s`, `%(published)s`, or `%(title)s` placeholders**, Python evaluates `PROMPT % {...}` to `PROMPT` unchanged!
- Verified empirically: `'Chart Champions' in (cbp_run.PROMPT % {'analyst': 'Chart Champions', 'published': '2026-10-30', 'title': 'BTC Urgent'}) == False`.
- Furthermore, in `cbp_run.py:199-212`, if even 1 video out of a batch fails `llm_extract`, `run_once()` raises `RuntimeError` at line 212 **before** `main()` calls `write_stamp(stamp_path)` at line 234. This leaves `stamp.json` un-updated whenever a single video times out, directly explaining the stale `stamp.json` behavior tracked in `cbp-daily-firing-gap`.

#### 3.3 `analyst_levels.py:84` Marks Levels `HIT` Using 1h Bars From *Before* the Video Was Published
In `scripts/dev/analyst_levels.py:84-93`:
```python
t0 = datetime.fromisoformat(x["published"]).replace(tzinfo=timezone.utc).timestamp()
hit = None
for ts, h, l in bars:
    if ts >= t0 and l <= x["level"] <= h:
        hit = datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d %H:%MZ")
        break
```
- `x["published"]` is a date-only string (`"YYYY-MM-DD"`, e.g. `"2026-10-29"`), so `t0` is `00:00:00 UTC` on the publish date.
- If BTC traded at `$78,000` at `02:00 UTC` on `2026-10-29`, and the analyst recorded a video at `18:00 UTC` on `2026-10-29` saying *"watch for a bounce if we revisit 78k"*, `mark()` checks all 1h bars from `00:00 UTC` and falsely marks the `$78,000` level as **`HIT` at `2026-10-29 02:00Z`**—16 hours before the video existed!
- Additionally, `analyst_levels.parse_levels()` (`lines 25-50`):
  - Parses any `40k..200k` number in a pointer as a BTC price level, even when it refers to liquidations/contracts/subscribers (verified empirically: `parse_levels("Over 100k liquidations and 76k-77k resistance")` -> `[100000.0, 76000.0, 77000.0]`).

---

### Finding 4: `BinanceLiquidationAccumulator.shutdown()` Drops Queued Liquidation Events on Interrupt

#### 4.1 Commit & Files Audited
- `4a038ed5b` — `src/main/java/datafeed/Main.java`, `src/main/java/datafeed/BinanceLiquidationAccumulator.java`, `src/test/java/datafeed/LiquidationLogWiringTest.java`

#### 4.2 Root Cause in `BinanceLiquidationAccumulator.java:80-92, 219-224`
In `BinanceLiquidationAccumulator.java:219-224`:
```java
public void shutdown() {
    running = false;
    scheduler.shutdownNow();
    if (wsClient != null) wsClient.close();
    if (logWriter != null) logWriter.interrupt();
}
```
And in `logLoop()` (`lines 80-92`):
```java
private void logLoop() {
    try (BufferedWriter w = Files.newBufferedWriter(logFile, StandardCharsets.UTF_8,
            StandardOpenOption.CREATE, StandardOpenOption.APPEND)) {
        while (running || !logQueue.isEmpty()) {
            String line = logQueue.poll(1, TimeUnit.SECONDS);
            if (line == null) continue;
            w.write(line);
            w.newLine();
            w.flush();
        }
    } catch (InterruptedException ignored) {
        Thread.currentThread().interrupt();
    } catch (IOException e) { ... }
}
```
Although the `while` condition says `while (running || !logQueue.isEmpty())`, calling `logWriter.interrupt()` in `shutdown()` causes `logQueue.poll(1, TimeUnit.SECONDS)` (or even an active interrupt flag check) to immediately throw `InterruptedException`, jumping out of the `try` block and **abandoning all remaining lines in `logQueue`**!
- Furthermore, `Main.java:75-80` starts `LIQ_LOG_SYMBOLS = List.of("BTCUSDT", "ETHUSDT")` unconditionally inside `Main statemachine <symbol>`, ignoring the CLI symbols and risking multi-process file append contention if more than one `statemachine` process runs on the same checkout.
