# Qriptal Binance scorecard - BLOCKED

**BLOCKED - no defensible all-calls score can be computed from the staged inputs.**

## What was checked

- `extracts/_staged_2026-09-27/raw/qriptal_*_raw.txt`: 22 staged raw transcripts (read-only). The set contains raw captions, not a normalized call ledger.
- `extracts/_staged_2026-09-27/extracts/qriptal/trade_log/2026-09-20_ZPFK3ZsLwoo.md`: the only structured trade-log extraction. Its tables mix past trades, forward plans, hypothetical examples, other assets, skipped calls, and cases with unstated entry/stop/target fields (see sections 1-3).
- `F:/MTS/data/tom_raw/klines`: BTCUSDT 1m CSV files span `BTCUSDT-1m-2022-01.csv` through `BTCUSDT-1m-2026-09-26.csv`; candle date coverage exists but cannot repair missing call fields or disambiguate which transcript statements are actionable calls.
- `MyTradingSys/research/qriptal_2026-10-10` is absent. No scorer implementation or scorer unit-test file exists in that target directory.
- Formula reference: `MyTradingSys/backtest/layers/FORMULAS.md`, section 17, defines Binance taker fees as 0.05% per side and net R:R. It does not specify how to classify overlapping targets/stops, unfilled limit orders, timeout, or incomplete calls for this source.

## Findings

| Severity | Evidence | Finding | Required input to unblock |
|---|---|---|---|
| HIGH | `extracts/_staged_2026-09-27/extracts/qriptal/trade_log/2026-09-20_ZPFK3ZsLwoo.md:14-23` | Even the sole structured extraction includes no-entry/no-stop/no-target calls, skipped and retrospective cases, and a recap that overlaps rows. A count or outcome cannot safely be inferred. | A reviewed ledger of eligible calls, with source video ID and transcript timestamp, market, direction, exact entry/order type, stop, target(s), and explicit taken/posted status. |
| HIGH | `extracts/_staged_2026-09-27/raw/qriptal_*_raw.txt` (22 files; command below) | The task asks to score every call. The 21 other raw transcripts have no normalized call inventory; automated keyword presence does not determine eligibility or provide complete scoring terms. | Complete human-verified extraction of all 22 transcripts, resolving recaps, duplicates, hypotheticals, multi-asset calls, ambiguity, and missing levels before scoring. |
| MED | `MyTradingSys/backtest/layers/FORMULAS.md:17` | The cited fee formula supports per-trade net R:R, but the card does not predefine resolution rules for targets/stop touched in the same 1m candle or when a call has multiple targets/partial exits. | Preregistered outcome rules in the call ledger/scorer before any score is reported. |

## Commands / results

- PowerShell inventory of `extracts/_staged_2026-09-27/raw/qriptal*`: 22 files.
- PowerShell recursive inventory of the structured Qriptal extraction folder: 1 file, `2026-09-20_ZPFK3ZsLwoo.md`.
- PowerShell inventory of `F:/MTS/data/tom_raw/klines`: first file `BTCUSDT-1m-2022-01.csv`, last file `BTCUSDT-1m-2026-09-26.csv`.
- `Get-ChildItem MyTradingSys/research/qriptal_2026-10-10`: directory not found.

## Deliverable status

No scorecard, scorer, or unit test was written: a synthetic test would not resolve the missing source-of-truth ledger, and any all-calls number would require guessed eligibility or trade parameters. The requested red-then-green test output is therefore NOT RUN (blocked before implementation). No holdout was read. No changes were made outside this report.

Changed files: `MyTradingSys/research/layer_lab/reports/2026-10-14_qriptal-score-binance.md`.

Follow-up cards created: none. The blocker is missing reviewed call data and predefined resolution rules; the existing data does not support the requested exact score.
