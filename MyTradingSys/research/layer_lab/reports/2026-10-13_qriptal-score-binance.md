# BLOCKED: Qriptal Binance scorecard (2026-10-13)

## Verdict

BLOCKED: the claimed 22 staged transcripts are missing from the allowed worktree: `MyTradingSys/extracts/_staged_2026-09-27` does not exist, and neither does `MyTradingSys/research/qriptal_2026-10-10`. The only named source brief (`MyTradingSys/items/B162_qriptal_signal_layer.md`) describes 22 transcripts, but contains no call rows that can substitute for them. No Qriptal scorer or scorer unit test exists in the worktree. Without the posted timestamps, entries, stops, targets, and side for every call, the requested n, win rate, and net R cannot be computed or independently checked.

The 1m candles found under `F:/MTS/data/tom_raw/klines` are outside the authorized worktree. They were not read or used. This report therefore does not treat their existence as satisfying the task's input requirement.

## What was checked

- `MyTradingSys/system/tasks/qriptal-score-binance.json`: card scope, test requirement, and 22-transcript goal.
- `MyTradingSys/system/LAYERS.md:218-223`: callers layer says scoring comes before further work and lists this card.
- `MyTradingSys/items/B162_qriptal_signal_layer.md`: identifies 22 staged transcripts and the self-reported 67.1% win rate, 3.99% average win, and 0.63% average loss.
- Worktree path checks (Python): staged source directory = absent; target scorecard directory = absent; no matching Qriptal files or scorer found in `MyTradingSys`.
- External data inventory only (no file reads): `F:/MTS/data/tom_raw/klines` has 89 BTCUSDT 1m CSV filenames, outside scope/worktree.

## Findings

| Severity | Location | Finding | Evidence | Proposed fix |
|---|---|---|---|---|
| HIGH | `MyTradingSys/extracts/_staged_2026-09-27` | NOT_IN_DATA: all 22 source transcripts needed to recover calls are absent. | Python `Path.exists()` returned `False`; no Qriptal files were found under `MyTradingSys`. | Restore the staged transcripts into this worktree, then rerun this card. |
| HIGH | scorer unit test / implementation | NOT_IN_DATA: there is no current scorer or named test file to exercise. | Scoped file inventory found no Qriptal scorer or test. | Once inputs are restored, add the specified three-call test first, capture its expected red failure, then implement and run it green. |
| MED | `F:/MTS/data/tom_raw/klines` | NOT_IN_DATA for this run: candles are outside the authorized worktree. | Inventory found filenames only; no candle contents were read. | Make the required development candles available within the authorized worktree/scope before scoring. |

## Test output

Not run. The specified scorer test cannot be written as a regression test against the current code because no scorer implementation or call schema is present; the transcript inputs are also missing. Therefore there is no valid red-then-green output to report. No scorecard or inferred outcome was produced.

## Changed files

- `MyTradingSys/research/layer_lab/reports/2026-10-13_qriptal-score-binance.md` - this blocked report.

## Follow-up cards

None.
