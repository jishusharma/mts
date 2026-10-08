# MISSED TRADES - roadmap (pick up cold from here)

Goal (operator, 2026-10-07): find the trades MTS did not take, using chart evidence from live sessions.
Live sessions observe only; their reads go through a capture channel; data work turns them into a dataset;
a comparison says, per chart-seen setup, whether MTS caught it, missed it, or was right to skip it, and why.

## What exists (v1, 2026-10-08)
| Piece | File | Does |
|---|---|---|
| Capture rules | methodology/observation_capture_protocol.md | what a live session logs, when, and how |
| Capture + normalize | observation/capture.py (`add`, `build`) | append-only obs.v1 lines; build -> derived/observations.jsonl, setups.csv, rejects.json |
| Miss analysis | observation/missed.py | setups vs auto_trades.jsonl (same side, +-2 bars of the read's TF, min 10 min), scored on 1m bars (5m klines fallback) -> missed.csv, MISSED_REPORT.md |
| Tests | observation/tests/test_observation.py | 13 tests, hand-worked numbers; in run_all_tests pytest step |

Store: `runtime_data/observations/` on JIS-NB (gitignored, data is not code). `captures/` is append-only input,
`derived/` is rebuilt every run and safe to delete.

Run, from any checkout:
```
python MyTradingSys/observation/capture.py --dir <store> build
python MyTradingSys/observation/missed.py --dir <store> --auto-trades <live>/MyTradingSys/execution/auto_trades.jsonl --bars <live>/MyTradingSys/runtime/orderflow_live --klines <live>/MyTradingSys/market_data/klines/BTCUSDT_5m.json
```
In the live tree the defaults already point at these paths once the supervisor deploys this code.

## Verdicts and reasons
CAUGHT = MTS entered the same side in the window. Otherwise the setup is scored on bars: target first = MISSED,
stop first = AVOIDED, anything else (no target, not filled, no bars, open at horizon) = UNRESOLVED.
mts_reason is the strongest same-side MTS event in the window: entered > attempt > blocked (layer blocklist) >
rejected (signal_rejected, e.g. Tom WAIT_TRIGGER, stale) > halt > busy > auto_pause; else opposite_signal, no_signal,
or not_covered (symbol MTS does not trade). "no_signal" is the system being blind; the others are the system seeing
it and choosing or being forced not to trade.

## Decisions taken as defaults (flag if wrong)
- Observation store is gitignored on JIS-NB, not committed. Cloud sessions need an exported snapshot (step 4).
- Window and horizon (2 bars / 10 min min, 24 h) are analysis settings, not trading parameters; they are printed
  in every report. Stop and target in one bar counts as the stop.
- Setups with no target are never called MISSED; they report MFE/MAE in R only, so no profit threshold is invented
  (provenance rule).
- Only BTC symbols are matched against MTS; anything else is not_covered.

## Next steps, in order
1. Adoption: brief the live desk sessions to log per observation_capture_protocol.md (the coordinator relays it).
   Until the supervisor deploys this code, they run capture.py from this worktree with `--dir` pointing at the
   live store. Done when a day of live work produces captures.
2. `mts obs` verb in scripts/mts.ps1 wrapping add/build/missed (update the user guide; check_guide.py gates it).
3. Backfill: parse READ entries of runtime/live_session_journal.md and session_log.json decisions into captures
   (kind note/chart_read, label kept, session = the MTS- id in the file). Low trust: no stops on most of them.
4. Snapshot export: `capture.py export` copies derived/ to research/missed_trades/snapshots/<date>/ in a worktree
   so cloud sessions can analyse it.
5. Recorder gap: orderflow_live 2026-10-07.csv stops at 07:41Z although the feed process was reported up; until
   fixed, scoring falls back to 5m klines (last ~41 h only). Older gaps leave setups UNRESOLVED.
6. Layer attribution: for MISSED rows, which layer (if any) would have fired with its gate relaxed; this is where
   misses turn into research items (one item per repeated reason, never a parameter tweak without a source).
7. Weekly digest: MISSED_REPORT counts by reason over time into research/audits/AUDIT_DIGEST.md.

## Do not
- Never feed captures into the gate, auto_trader or any verdict. Chart reads stay labeled "chart read".
- Never write captures from a session into the live tree's tracked files; the store path is gitignored for that.
