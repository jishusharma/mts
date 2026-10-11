# T092 REPORT - what context does a single screenshot read get? (2026-10-10, Opus, JIS-NUC)

Brief: `MyTradingSys/items/T092_screenshot_context_gap.md`. No code changed; items filed: B157-B161.
Live state: `live_mirror.py pull` returned `REFUSED: no CURRENT pointer under \\JIS-NB\MTS-Mirror\` (mirror not
installed yet, desk task 20261009-202832 pending). Everything below is from the committed record; live files are NOT_IN_DATA.

## Answer in five lines
1. Each screenshot read starts cold. The extract template has no slot for prior context, and the next read does not
   score the falsifiers the previous read wrote down (worked example below).
2. The one persisted "context state" (`runtime/session_state.json`: thesis, watch levels, invalidates) was last written
   2026-09-14 and is still printed on the Tom alert card. Nothing in the screenshot pipeline writes it.
3. The AI meets the Java engine only by hand: a session types the snapshot numbers it can see into a markdown table.
   The engine can rebuild its own state at a past instant (archive mode), but the read procedure never asks it to.
4. Indicator values on the chart are hand-typed from pixels/headers; recomputation from klines is done ad hoc per read.
5. AI read and engine verdict are never one record: shot.py stores only claim counts, not the claims.

## 1. What a read starts from today (traced on three shots)
| Shot | Context it loaded | What it skipped / re-derived by hand | Evidence |
|---|---|---|---|
| 6188a576411b 30m | fapi 30m klines + rsi_core / rsi_divergence recomputed | no snapshot, no prior read cited | `research/screenshots/2026-10-09_BTCUSDT_6188a576411b.md:11` |
| b5f554a9f68a 3m | klines 1m-1h, live tree snapshots, last_alert.json, auto_trades, alerts, live_runner.log (on JIS-NB) | context written as prose in live_reads R3, not in the extract; capture obs 6657cd911836 | `..._b5f554a9f68a.md:9,12-13`; `missed_trades/observations/2026-10-09_live_reads.md:48-78` |
| 78f967b4e253 5m | 5m fapi klines fetched 20:14Z; "last system-side read 16:30Z (live_reads.md)" | snapshot, last_alert, OI, CVD all absent on NUC (5 of 9 rows NOT_IN_DATA); R1/R3 falsifiers not checked | `..._78f967b4e253.md:9,21-25` |

Files a read never loads (no step names them): `runtime/session_state.json`, `runtime_data/observations/derived/*`
(capture store, gitignored, JIS-NB only: `observation/capture.py:9`), earlier extracts of the same symbol/day.

## 2. Is there a causal context state a new screenshot is applied to? No.
- Template sections: header, per-shot claims, across-timeframes, six layers (only if a setup), outcomes
  (`research/screenshots/TEMPLATE.md:12,22,26,29`). No "prior reads / open hypotheses / levels in play" section.
- Worked example of the loss. R1 (13:56Z) wrote "Invalidation of the read: acceptance outside 82450-83470"
  (`live_reads.md:22`); R3 (16:30Z) wrote "Acceptance under 82630 (VWAP) = next daily POC ~82488" (`live_reads.md:78`).
  At 20:13Z the 78f967b4e253 header shows C 82366.2 (`..._78f967b4e253.md:14`): below both levels. The extract does not
  say R1 was invalidated or that R3's downside path played out; it records the operator ray ~82496 as
  "whether it is the 10-09 daily POC 82488.1 is not established" (`:7`), while R2 had already matched the operator's red line ~82500 to the daily VP POC (`live_reads.md:38`) and R3 quoted
  daily POC 82488.1 from the 16:30Z snapshot (`live_reads.md:71`).
  The context existed in a committed file and was not applied.
- `session_state.json` holds exactly the fields the brief asks for (thesis, watch_levels, next_trigger, invalidates:
  `runtime/session_state.py:19-30`) but `updated_utc` is 2026-09-14T09:28:31Z (`runtime/session_state.json:3`), git last touch
  2026-09-24. Its text ("Price ~77600 never printed 76300") is the stale SSOT_THESIS of B156; cc16a73 added the age to the
  card (`tests/test_b156_thesis_line_age.py`) but no writer exists, so the card will keep carrying it.
- `capture.py` is the closest thing to a causal record: `--supersedes` for corrections (`capture.py:102,238`), stop required
  for a setup (`:111`). It only scores setups with a side (`missed.py:6,12`); a context read (levels, falsifiers, no side)
  is stored but never scored.

## 3. Where the AI layer meets the Java engine
| Interface | Produced by | How the read compares | Repeatable by another session/model? |
|---|---|---|---|
| Snapshot fields (price, VWAP, VP POC/VAL, OI, CVD, FVG, state code, regime, day type) | `MarketDataSnapshot.java` -> `runtime_data/snapshots` (`:1585-1592`) | by hand, numbers typed into a claim row (`..._b5f554a9f68a.md:19-21`) | no: depends on which snapshot file was current when the session ran |
| Historical snapshot at an instant | archive mode `MarketDataSnapshot(Path raw)` (`:40-46`), `saveHistoricalSnapshot` (`:1368-1377`), harness `SnapAt.java` | never used by a read | would be, if wired (B160) |
| Tom / Fabio alert rows, last_alert.json | live runner on JIS-NB | by hand (R3 "MTS state at 16:30Z") | no |
| Divergence detector | runner, 1h only (`..._b5f554a9f68a.md:22`) | by hand, recomputed per read | partly (module is deterministic, call is not recorded) |
| session_state thesis | AI-written, stale since 09-14 | not compared | n/a |
| Claim classes MATCH/MISMATCH/NOT_IN_DATA | the reader | shot.py counts rows by regex, keeps counts only (`scripts/dev/shot.py:406,414`) | counts yes, claims no |

## 4. What one screenshot cannot carry
| Item | Recovered from | Status |
|---|---|---|
| Indicator settings (BB 20 2, RSI 14 SMA 14) | the chart legend itself (pre-read gate VVP-002 F.1) | recovered |
| VWAP anchor | MTS anchors at NY open (`MarketDataSnapshot.java:851` `vwap_anchor_utc`); chart anchor unknown | guessed: recurring NOT_IN_DATA (`..._78f967b4e253.md:21`, `..._b5f554a9f68a.md:19`) |
| HTF levels (VP POC/VAL, daily POC, naked POCs) | snapshot if the machine has one | NOT_IN_DATA off JIS-NB |
| Session boundaries / chart clock | stated by hand per read (`screenshot_intake.md` classify `--at --tz`) | recovered, by hand |
| CVD / net delta level | rule: compare steps, not levels (`screenshot_intake.md:59`) | steps only, no CVD file off JIS-NB |
| OI series | `oi_1m.csv` on JIS-NB | NOT_IN_DATA off JIS-NB |
| Operator rays / boxes | nowhere (`screenshot_intake.md:82`, T066 blocked) | NOT_IN_DATA always |

## 5. Hypotheses from the brief
| # | Hypothesis | Verdict | Evidence | Item |
|---|---|---|---|---|
| a | no machine-readable chart-read schema | PARTLY: obs.v1 exists for setups; claim rows and context reads are markdown only | `capture.py:9,102-111`; `shot.py:406,414` | B159 |
| b | indicator values not auto-extracted | CONFIRMED; JSON extractor of Sep 2026 never used | `screenshot_intake.md:84`; `..._78f967b4e253.md:14,19-20` | B161 |
| c | no point-in-time engine replay | REFUTED for the engine (archive mode + SnapAt exist); CONFIRMED for the read procedure (never called) | `MarketDataSnapshot.java:40-46,1368` | B160 |
| d | live state machine-local | CONFIRMED today; fix designed (LIVE_MIRROR.md), not installed on JIS-NB | mirror REFUSED 2026-10-10 | desk 20261009-202832 (no new item) |
| e | AI read and engine verdict never reconciled | CONFIRMED | section 3 table | B159 + B160 |
| new | each read starts cold; prior falsifiers not scored | CONFIRMED | section 2 worked example | B157 |
| new | session_state.json is the only context store and is dead since 09-14 | CONFIRMED | `session_state.json:3` | B158 |

## 6. Ranked build order (smallest fix, owner, fail-first test, provenance)
| Rank | Item | Smallest fix | Owner | Test that fails first | Sourced rule needed? |
|---|---|---|---|---|---|
| 1 | B157 | TEMPLATE gets a "Carried context" section; `shot.py read` refuses a chart extract without a `Prior:` line (an extract path, or `Prior: none`) and lists the open falsifiers of that prior read | VIS | test_shot: extract without `Prior:` is accepted today | no: process rule, no market parameter |
| 2 | B159 | `shot.py read` stores each claim row (id, class, claim, evidence) in the manifest; falsifier/invalidation lines go to capture as `chart_read` with `level` | VIS | test_shot: manifest holds only counts today | no |
| 3 | B160 | `shot.py engine <id>`: historical snapshot at the shot's `--at` via archive mode, saved next to the extract; read rows cite it | VIS + DATA | test: no command exists; one archive-backed fixture snapshot at a fixed instant | no (engine output, not a new rule) |
| 4 | B161 | `shot.py header <id>`: recompute BB/RSI from fapi klines with the legend's own settings at `--at`, print diff vs the typed header | VIS | test: typed header with a wrong BB mid is not flagged today | settings come from the chart legend, not MTS |
| 5 | B158 | decide the fate of session_state.json: reads write it (with written-at price), or the card drops it | DESK + CORE | test: card prints a 26-day-old thesis today | decision for the operator (default: retire from card) |

## 7. Next-session prompts (one per top gap; each <= 30 lines, run with zero operator input)
### B157 (Sonnet)
```
MTS builder session. Read CLAUDE.md, STATUS.md, items/B157_screenshot_read_starts_cold.md. Worktree only.
1. sync.py start; claim "B157 carried context in screenshot reads".
2. Tests first in scripts/dev/test_shot.py: (a) a chart extract without a `Prior:` line is refused by read_extract;
   (b) `Prior: none` is accepted; (c) `Prior: <path>` to a missing file is refused; (d) the prior extract's lines starting
   `Invalidation`/`Falsify` are returned for the reader. Run them: they must fail on today's shot.py.
3. Implement in scripts/dev/shot.py read_extract; add a "## Carried context" section to research/screenshots/TEMPLATE.md
   (Prior:, open falsifiers, each scored HELD / BROKEN / UNTESTED against the new chart).
4. Update methodology/screenshot_intake.md stage 4 (one line). Gate: run_all_tests.py --quick.
5. Commit with Result line; sync.py ship; release; overwrite NEXT_SESSION.md; where clean.
Defaults: existing extracts are not backfilled; a non-chart shot needs no Prior line.
```
### B159 (Sonnet)
```
MTS builder session. Read CLAUDE.md, STATUS.md, items/B159_screenshot_claims_not_machine_readable.md. Worktree only.
1. sync.py start; claim "B159 claim rows into manifest".
2. Tests first (test_shot.py): read_extract on the 78f967b4e253 extract stores 9 claim dicts {id, class, claim, evidence};
   status_line counts are unchanged; a malformed row is refused with its line number. Must fail on today's code.
3. Implement; keep the manifest append-only (new field on the `read` event).
4. Gate --quick; ship; release; NEXT_SESSION.md; where clean.
Defaults: no capture.py change in this session (falsifier export is a follow-up noted in the item).
```
### B160 (Sonnet, Java read-only)
```
MTS builder session. Read CLAUDE.md, STATUS.md, items/B160_engine_state_at_screenshot_time.md. Worktree only.
1. sync.py start; claim "B160 engine snapshot at shot time".
2. Inventory: where the 1m archive (raw/klines) lives on this machine; if absent, post a DSA task to run it on JIS-NB and stop at the spec.
3. Tests first: a python wrapper `shot.py engine <id>` builds the SnapAt instants file from the shot's `at` (floored to the minute)
   and refuses a shot without `at`; fixture-driven, no Java in the unit test. Must fail today.
4. Implement the wrapper calling SnapAt (research harness) from a %TEMP% build; no change to src/main.
5. Gate --quick; ship; release; NEXT_SESSION.md; where clean.
Defaults: output file research/screenshots/engine/<shot id>.json; BTCUSDT only.
```
