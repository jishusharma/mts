# Task Report: gemini-yt-rumers-extract-1

- **Task ID:** `gemini-yt-rumers-extract-1`
- **Lane / Weight:** CODEX / ROUTINE [SOURCED: `MyTradingSys/system/tasks/gemini-yt-rumers-extract-1.json:18,49`]
- **Date (UTC):** 2026-11-01
- **Worker / Model:** Gemini 4 Argon (Medium)
- **Registry:** `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md` [SOURCED: `MyTradingSys/system/tasks/gemini-yt-rumers-extract-1.json:29`]

## 1. Scope & Objective

For the 5 operator-picked videos from `@the.rumers` (`6WfTIyJ-YzQ`, `EoQDQVblmMY`, `N6zlfBJsoRc`, `kozesVBKkg4`, `aTMFouI9mF4` [SOURCED: `MyTradingSys/system/tasks/gemini-yt-rumers-extract-1.json:15`]): extract each complete trading rule or setup the speaker states, as a table with video ID, timestamp, verbatim caption quote, entry, stop, target, timeframe, indicator, claimed hit-rate, or `NOT_IN_DATA`, and mark which rules are mechanical enough to backtest (`TESTABLE` shortlist). No trading verdict.

## 2. Caption Ingestion Summary

Executed timed caption fetch:
```powershell
python scripts/dev/fetch_captions_timed.py --analyst Rumers --out MyTradingSys/research/rumers_2026-11-01/transcripts 6WfTIyJ-YzQ EoQDQVblmMY N6zlfBJsoRc kozesVBKkg4 aTMFouI9mF4
python scripts/dev/fetch_captions_timed.py --analyst Rumers --langs en-orig --out MyTradingSys/research/rumers_2026-11-01/transcripts 6WfTIyJ-YzQ
```

Video ingestion status across the 5 target videos [OURS: 5 total]:
1. `6WfTIyJ-YzQ` (*"If I Could Only Trade ONE Strategy… This Would Be It"*, published `2025-12-20`, duration `1534`s, `5076` words [SOURCED: `MyTradingSys/research/rumers_2026-11-01/transcripts/6WfTIyJ-YzQ_timed.txt:1-7`]) — **Captioned** (`OK auto 5076w` via `--langs en-orig`; saved to `MyTradingSys/research/rumers_2026-11-01/transcripts/6WfTIyJ-YzQ_timed.txt` and `raw_transcripts_canonical/6WfTIyJ-YzQ_raw.txt`).
2. `EoQDQVblmMY` (*"The One \" Box Theory\" Strategy That Works Everyday ( Stupid Simple And Proven)"*, published `2025-03-27`, duration `1405`s [SOURCED: `yt_dlp` metadata via `scripts/dev/fetch_captions_timed.py:meta`]) — **UNVERIFIED** (`HTTP Error 429: Too Many Requests` on `yt_dlp` timedtext and `IpBlocked` on `youtube_transcript_api`; marked `NOT_IN_DATA` with `0` quotes [OURS] per card rule `one fetch try per video, no retry loop, 429 -> UNVERIFIED with no quotes` [SOURCED: `MyTradingSys/system/tasks/gemini-yt-rumers-extract-1.json:23`]).
3. `N6zlfBJsoRc` (*"I Always Wait For THIS Before Entering Trades  ( Unsharp Candles )"*, published `2025-02-14`, duration `1572`s [SOURCED: `yt_dlp` metadata via `scripts/dev/fetch_captions_timed.py:meta`]) — **UNVERIFIED** (`HTTP Error 429: Too Many Requests` / `IpBlocked`; marked `NOT_IN_DATA` with `0` quotes [OURS]).
4. `kozesVBKkg4` (*"2 Stupid Simple VWAP Trading Strategies"*, published `2025-04-09`, duration `1641`s [SOURCED: `yt_dlp` metadata via `scripts/dev/fetch_captions_timed.py:meta`]) — **UNVERIFIED** (`HTTP Error 429: Too Many Requests` / `IpBlocked`; marked `NOT_IN_DATA` with `0` quotes [OURS]).
5. `aTMFouI9mF4` (*"The \" ONE CANDLE \"  Scalping Strategy I Will Use For Life"*, published `2025-06-30`, duration `1263`s [SOURCED: `yt_dlp` metadata via `scripts/dev/fetch_captions_timed.py:meta`]) — **UNVERIFIED** (`HTTP Error 429: Too Many Requests` / `IpBlocked`; marked `NOT_IN_DATA` with `0` quotes [OURS]).

Totals:
- Videos targeted: `5` [SOURCED: `MyTradingSys/system/tasks/gemini-yt-rumers-extract-1.json:15`]
- Videos captioned: `1` [OURS: `6WfTIyJ-YzQ`]
- Videos UNVERIFIED (HTTP 429, no quotes): `4` [OURS: `EoQDQVblmMY`, `N6zlfBJsoRc`, `kozesVBKkg4`, `aTMFouI9mF4`]

## 3. Extracted Rules & Testable Shortlist (`RUMERS_EXTRACT_1.md`)

Primary deliverable: `MyTradingSys/research/rumers_2026-11-01/RUMERS_EXTRACT_1.md`.
- Summary table rows: `13` [OURS: `MyTradingSys/research/rumers_2026-11-01/RUMERS_EXTRACT_1.md:19-33`] (`9` verbatim quoted rule rows from `6WfTIyJ-YzQ` + `4` explicit `NOT_IN_DATA` rows for the `4` HTTP 429 UNVERIFIED videos).
- Testable shortlist entries: `4` mechanical variations (`T1`..`T4`) of the "Pattern Scalp" strategy [OURS: `MyTradingSys/research/rumers_2026-11-01/RUMERS_EXTRACT_1.md:84-91`]:
  1. **`T1 (RUMERS-PS-ORB-ENGULF)`**: First `15`-minute candle of session closes [SOURCED: `6WfTIyJ-YzQ_timed.txt:103-119`] with high-to-low range `>= 20%` (`0.20`) of Daily ATR (default settings) [SOURCED: `6WfTIyJ-YzQ_timed.txt:211-247`]; drop to `5`-minute chart [SOURCED: `6WfTIyJ-YzQ_timed.txt:344-348`] and enter in the opposite direction when a "Power of Tower" (engulfing / `30%` to `50%` or `30%` to `40%` retracement candle [SOURCED: `6WfTIyJ-YzQ_timed.txt:328-337`]) is broken by the next `5`-minute bar [SOURCED: `6WfTIyJ-YzQ_timed.txt:358-367`, `466-477`]; stop loss below low of day (long) or above high of candles / high of day (short) [SOURCED: `6WfTIyJ-YzQ_timed.txt:368-369`, `481-482`]; target `50%` (midpoint) to `100%` of the `15`-minute range [SOURCED: `6WfTIyJ-YzQ_timed.txt:370-377`, `482-489`]; claimed hit-rate: `NOT_IN_DATA`.
  2. **`T2 (RUMERS-PS-ORB-HAMMER)`**: Same `15`-minute opening range `>= 20%` Daily ATR filter; on `5`-minute chart, enter when a following candle breaks the high of a bullish hammer ("John Wick") or breaks below a bearish inverted hammer [SOURCED: `6WfTIyJ-YzQ_timed.txt:282-286`, `315-326`, `647-650`]; stop beyond session extreme; target `50%` to `100%` of the `15`-minute range.
  3. **`T3 (RUMERS-PS-EXTENDED-OPEN)`**: When the opening manipulation drive extends `15` to `40` minutes past the first `15`-minute bar without printing a `5`-minute John Wick or Power of Tower, take the first `5`-minute `30%` to `50%` retracement / signal candle post-`15`m with stop above high of day / below low of day and target at the `50%` midpoint of the range [SOURCED: `6WfTIyJ-YzQ_timed.txt:566-601`, `660-663`].
  4. **`T4 (RUMERS-PS-INTRADAY-SPIKE)`**: Apply the same `>= 20%` Daily ATR filter to any intraday `15`-minute spike bar, entering on the subsequent `5`-minute John Wick or Power of Tower reversal with stop beyond high/low of day and target at the `50%` midpoint of the `15`-minute spike bar [SOURCED: `6WfTIyJ-YzQ_timed.txt:602-655`].

## 4. Verification Gate

Pre-change failure check (before creating `RUMERS_EXTRACT_1.md`):
```powershell
python scripts/dev/verify_extract_quotes.py MyTradingSys/research/rumers_2026-11-01/RUMERS_EXTRACT_1.md
```
Result: `FileNotFoundError` (exit code `1` [OURS]).

Post-change verification gate:
```powershell
python scripts/dev/verify_extract_quotes.py MyTradingSys/research/rumers_2026-11-01/RUMERS_EXTRACT_1.md
```
Result: `PASS: 0 problem(s)` across all `9` verbatim quote blocks (`RUMERS_EXTRACT_1.md:44,48,52,56,60,64,68,72,76`), exit code `0` [SOURCED: `verify_extract_quotes.py` output].

Noticed: `scripts/dev/fetch_captions_timed.py` defaults to `--langs en` (line 215), which requests the `&tlang=en` auto-translated track on `yt_dlp` when a video's native auto-caption track is keyed as `en-orig` (unlike `scripts/dev/fetch_captions.py:52` which checks `for key in (lang, lang + "-orig")`); passing `--langs en-orig` fetched `6WfTIyJ-YzQ` immediately (`5076w`), while the remaining 4 videos hit the host-level YouTube HTTP 429 / `IpBlocked` limit already tracked on the desk queue (`20261101-060221-cbp-youtube-block-on-nuc-root-cause-and-`).
