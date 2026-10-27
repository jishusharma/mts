# SCREENSHOT INTAKE
# Purpose: every image the operator shows a session is saved once, understood once, and ends in a filed result or a stated "no action".
# Scope: all surfaces. Reading rules for charts stay in chart_read_protocol.md and visual_validation_protocol_vvp001/002.md; this file is the pipeline around them.
# Written 2026-10-09 (operator ask: "does every session know if it gets saved?"). Tool: scripts/dev/shot.py. Tests: scripts/dev/test_shot.py.

## WHY THIS EXISTS (verified 2026-10-09)
- Claude keeps a pasted image in places nobody is told about: inside the session transcript, in ~/.claude/uploads/<session>/, and in a Temp folder that is cleaned.
  When checked on 2026-10-09, two of the nine file paths cited by the first big screenshot study were already deleted, including the 10-05 5m chart the operator cross-checked.
- Transcripts do not last either: the oldest surviving transcript of this project starts 2026-09-28, although the project has run since August. The pixels inside a transcript have a limited life.
- CLAUDE.md and DSA_SESSION_PROMPT.md said nothing about screenshots, so no session knew whether an image was kept. The VVP-002 extractor (Sep 13-24) never produced a single extract.
- The one study that did it by hand (bigtrade, 25 images read, 85 observations) found 13 observations where the chart and our pipeline disagree and 13 chart elements no file holds at all:
  Java volume-profile bias of 300-690 points, an OI series that is hourly-stepped, a VWAP anchor mismatch, a frozen naked-POC list. That is what a standing process should produce every time.

## THE FLOW
| # | Stage | Who | Gate (what blocks) | Command |
|---|---|---|---|---|
| 1 | LAND | automatic (hook), or `shot.py ingest` | none: saving never waits for a session to remember | `shot.py ingest` |
| 2 | CLASSIFY | the session that sees it | a shot stays `new` and shows OVERDUE after 24 h; `--why` (the operator's meaning) is mandatory | `shot.py classify` |
| 3 | SET | automatic | charts of one symbol within 10 min form a set; a set with one timeframe is flagged SINGLE-TF | `shot.py sets` |
| 4 | READ | the session, chart sets by Sonnet or better | extract must name every shot id and carry claim rows `\| id \| class \| claim \| evidence \|` (B159: each row is stored on the manifest `read` event; a malformed row is refused with its line number) | `shot.py read --extract` |
| 5 | REPORT | the session | every MISMATCH is filed or explained in 20+ characters; NOT_IN_DATA becomes a feature hypothesis | file in BUGS.md / PLAN.md |
| 6 | CLOSE | the session | outcome must exist in the repo (`finding:B156`, `finding:card:<task id>`, `feature:FEAT-11`) or be a stated `noaction:`/`note:` | `shot.py done` |
| 7 | MEASURE | STATUS.md, every build | `SHOTS ...` line; overdue count; claims MATCH/MISMATCH/NOT_IN_DATA; items filed | `shot.py status` |

## 1 LAND - how a session knows it was saved
`.claude/settings.json` runs `shot.py hook` at SessionStart and UserPromptSubmit in every checkout that has pulled it. The hook lands any new image of that session
(transcript paste, uploads folder, Temp folder; the same bytes arriving by two routes are one shot) and prints a short notice into the session:
`[SCREENSHOT INTAKE] N image(s) ... SAVED`, with the shot ids and the operator's own words sent with the image. No notice means nothing new landed.
The hook never blocks and never errors a prompt; failures go to `<store>/hook_errors.log`.
Store: `runtime_data/screenshots/` of the main checkout (one per machine, shared by all worktrees, gitignored: screenshots can show accounts). Layout: `img/<id>.png`, `manifest.jsonl` (append-only events), `cursors.json`, `inbox/`.

| Surface | Saved? | What the session must do |
|---|---|---|
| Claude Code app, any worktree | yes, by the hook, at the next prompt | classify, read, close per the notice |
| Project-thread wake with attachment | yes, `ingest` finds ~/.claude/uploads | same |
| Plain chat (DSA) | NO. The chat holds the pixels, nothing reaches the disk | say so in the first line of the reply: "SHOT NOT SAVED (chat has no disk)". Write the read as text through AIRUN with `Shots: chat-only` in the extract. If it matters, the operator drops the file in `runtime_data/screenshots/inbox/` or pastes it in a Code session |
| Cloud session | no (different machine) | say "not saved"; the extract it commits is the record |

## 2 CLASSIFY - what the operator meant
The notice quotes the operator's words sent with the image. Those words are the meaning; copy them into `--why` rather than guessing from pixels.
| kind | Use for | Extra fields | Goes to |
|---|---|---|---|
| chart | any price chart or order-flow panel (TradingView, CoinGlass, Binance, footprint, heatmap, analyst chart) | `--symbol --tf --at [--tz] --source` | sets, read, extract |
| positions | exchange / account / PnL / transactions | none | private: read for the trade ledger, never write numbers into a tracked file |
| app | any non-trading software screen: Claude, AIBridge, terminal, error dialogs, system monitors | none | bug or process evidence: BUGS.md / LESSONS_LEARNED.md |
| other | news, a post, someone else's analysis, anything with a possible meaning | none | a T-item if it suggests research |
| noise | no meaning for the project | none | closes immediately, reason kept |
`--at` is the market time on the chart's right edge. Chart clocks differ: TradingView pages via CoinGlass are UTC; CoinGlass footprint pages (legend.coinglass.com) are IST (UTC+5:30). A naive time without `--tz` is refused.

## 3 SET - charts studied together
The operator's TradingView charts are one question seen at several timeframes. `shot.py sets` groups them. A set read must say which timeframes are present and which are missing
(chart_read_protocol layers 3-4: the same level on another panel, and on a higher timeframe). One timeframe only = the read is context, not a read.

## 4 READ - the procedure that already worked
Checklist (operator 2026-10-17): every read answers every line of `operator_chart_checklist.md` (present / absent / panel missing). A thing discussed on one chart is looked for on all charts.
Copy `MyTradingSys/research/screenshots/TEMPLATE.md`. Carried context first (B157): a chart extract needs a `Prior:` line (the previous read's extract, or `Prior: none`) or `shot.py read` refuses it; `read` prints that read's Invalidation/Falsify lines, each scored HELD / BROKEN / UNTESTED against the new chart.
Per image: pre-read gate (VVP-002 F.1), then each claim on the chart gets one row classed:
- MATCH: reproduced from files on disk (give file and numbers).
- MISMATCH: the chart shows one thing, our pipeline or raw data another.
- NOT_IN_DATA: the chart shows something no file holds (operator rays and boxes always land here until T066).
Rules learned from the first study: state the chart clock; compare CVD steps, never CVD levels (the chart anchors at its first loaded bar); mark pixel reads with their error; footprint cell numbers are not volume (meaning unknown);
no trade advice in an extract.
Engine state at the shot (B160): `shot.py engine <id>` writes `research/screenshots/engine/<id>.json` (the engine's own snapshot rebuilt at the shot's minute from the 1m archive); a claim row about VWAP, VP, CVD or state cites that file instead of whatever snapshot is current. A read that names a setup also goes to `capture.py add --kind chart_read ... --image <shot id>` (invalidation required, six layers).

### 4b PAIRED REVIEW (operator 2026-10-15: review runs side by side, different models, economical)
Evidence: on set 7f3698134541 the serial Haiku review (run after the read) caught 5 WRONG + 1 UNSUPPORTED of 22 claims (`..._REVIEW.md`), which is worth keeping. Because it ran after the read, it added wall-clock, and it anchored on the draft.
1. START TOGETHER: right after `classify` + `engine`, the reader (Sonnet) starts one Haiku subagent in the background (`run_in_background`). A spawned session cannot `start_session`, so a subagent is the route. That subagent is the BLIND reader. It gets the shot ids, image paths, `engine/<id>.json` and the 1m kline path, and never the reader's draft. It writes its own claim rows (`| id | class | claim | evidence |`) to `<set>_REVIEW.md` under `## Blind read`.
2. RECONCILE: the reader diffs both claim lists. A claim only one side made, or any number that differs by more than the pixel error, is re-checked against raw data by the reader. Then the same subagent gets a second message to verify the reader's final rows. That message carries no new context, only the final extract. It records CONFIRMED / WRONG / UNSUPPORTED under `## Verdicts`.
3. ONE SHIP: the extract and the REVIEW go in one `sync.py ship`. The verdict counts go on the commit's `Result:` line. A read counts as done only when `git cherry origin/fast-track <sha>` prints nothing. On 10-15 a read was reported "on fast-track" while its commit was local only.
4. COST RULE: when 3 sets in a row get 0 WRONG, step 1 drops to a numbers-only check. When WRONG is above 15% for 3 sets, change the reading procedure (this file), not the reviewer.

## 5-6 REPORT AND CLOSE - the feedback loop
| Claim class | Becomes | Owner group (PROJECT_MAP) |
|---|---|---|
| MISMATCH | a B-item (defect in data, engine or wiring) or an explained `noaction:` | the group that owns the field (DATA, CORE, LAYR) |
| NOT_IN_DATA | a FEAT-hypothesis in the backtest plan (formula, causal at bar close, thresholds = analysis settings) | EVID |
| MATCH | nothing; counted | none |
`shot.py done --outcome finding:<id> | feature:<id> | noaction:<why> | note:<text>`. A chart cannot be closed unread; an id that is not in the repo is refused. A finding filed as a task card (`tasks.py new ... --layer <family>`) closes with `finding:card:<id>` and shows under its layer in `system/LAYERS.md`.

## 7 MEASURE
`shot.py status` prints `SHOTS landed N: new, classified, read, done | overdue | claims | filed`; make_status.py puts it in STATUS.md, so every session reads it at boot.
Yield check: if 10 consecutive chart shots close with no finding and no feature, review the reading procedure here instead of reading more charts.
Recurring NOT_IN_DATA rows (operator drawings, net-delta series, footprint imbalance) are the standing list of what the data pipeline lacks.

## KNOWN LIMITS (open)
- The hook only exists in checkouts that contain `.claude/settings.json`. Sessions opened in the live tree (every one of the 13 pastes so far had that as its working folder) get it only after MTS-AutoDeploy updates the live tree;
  until then run `python scripts/dev/shot.py ingest` yourself (idempotent, about 1 s).
- Images sent while a turn is running (mid-turn) are not user records: the app writes them to the transcript as `attachment` / `queued_command` (blocks in `attachment.prompt`). `ingest_transcript` lands that shape since 2026-10-24 (card mid-turn-image-intake-gap); the five 4h/1h/8h/12h/1D shots of 2026-10-18 ~14:57Z predate it and are recovered by `shot.py ingest` only if their transcript still exists. They were not found in Temp or uploads.
- A set is "within 10 minutes". Charts of one question pasted in two messages hours apart (the 2026-10-02 pair: 4h+1d at 18:23Z, two 15m at 20:17Z) are two sets; read them together by hand.
- The SessionStart backlog reminder repeats at most every 6 hours, so a real backlog does not become wallpaper.
- Not yet observed on a live paste: whether the app writes the image before the UserPromptSubmit hook runs. Worst case the notice arrives with the next prompt. First real paste: confirm with `shot.py list`.
- Plain-chat (DSA) images cannot be saved from inside the chat; the inbox folder is the manual route.
- Operator drawings (rays, boxes, volume-profile anchors) are stored nowhere; T066 (read TradingView layouts) is blocked since 2026-10-05 (no connected Chrome).
- Images older than the app's retention that were never in a transcript are gone. `shot.py ingest` on 2026-10-09 recovered 22 images (13 pastes, 9 uploads).
- runtime_data/screenshot_extracts/_SCHEMA.json and screenshot_worker_prompt.md (JSON extractor, Sep 2026) are superseded by the template; left in place, never used.
