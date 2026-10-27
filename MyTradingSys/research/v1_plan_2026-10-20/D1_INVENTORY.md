# D1. In-flight inventory with a disposition (measured 2026-10-20 on JIS-NB)

Disposition words: FINISH = do it in the stage named; PARK = keep the files, no work until the roadmap re-opens it;
CLOSE = drop the card, branch or row (files stay in git history). A PARK or CLOSE is a proposal; `tasks.py done`,
`tasks.py flag` and branch deletion happen only after the operator answers q-v1-freeze (DECISIONS_PROPOSED.md).

## 1. Counts (RESULT 2026-10-20)
| List | Number | Source |
|---|---|---|
| Task cards | raw 47, refined 37, ready 48, blocked 8, done 293, dropped 29 | `python scripts/dev/tasks.py status` |
| Claims | 18, of which 3 STALE (26-41 h, no commit) | `sync.py start` output |
| Desk rows (DSA / JIS-NB / JIS-NUC) | 17 pending; 7 are the DSA-NB audit rows posted 2026-10-16, never taken | `desk.py list` |
| Codex lab queue | 8 ready | `codex_run.py status` |
| Relay list | NEXT_SESSION.md, 19.7 KB, 7 hand-over blocks from 4 machines | `wc -c` |
| Control Room inbox file | 5 entries, newest 2026-10-12 | OPERATOR_INBOX.md |
| BUGS.md rows OPEN | 71 (18 of them T034-T058, opened 2026-09-19..29) | `grep OPEN` |
| Worktrees on this machine | 63; 24 local branches ahead of trunk (table in section 2) | `git worktree list`, `git rev-list` |
| `.new` files | 2 (fabio/htf_context_live.py.new and its test, 223 h old) | STATUS.md |
| Windows scheduled tasks `MTS*` on JIS-NB | 22 registered: 15 enabled (Ready/Running), 7 disabled | `Get-ScheduledTask` 2026-10-20 |
| Live sources trading on testnet | 27 `pre_pipeline_sources`, all `review_by 2026-10-23`; `promoted_setups.json` entries: 0 | execution/auto_trader_config.json, promoted_setups.json |
| Layer families / backtest rows | 13 families (LAYERS.md); 22 layers in layer_map.json; 29 TRIAL_LEDGER rows, all split DEV | LAYERS.md, TRIAL_LEDGER.csv |
| Commit mix last 24 h | 231 commits: research 19 %, claim/release 44 %, other 37 % | STATUS.md 2026-10-20 03:30 |

## 2. Branches and trees
| Item | State (RESULT) | Disposition | Reason |
|---|---|---|---|
| `claude/traffic-unjam-77aa8e` (worktree `aws-ai-services-mts-aff750`): 958c0d05 FIFO ship gate + tree-killing step limits + `traffic.py jam`; 8d3dc4d0 step limit 30 min, gate bound 90 min | `git cherry origin/fast-track`: 2 commits not on trunk; branch 0 behind trunk (merge 32c5d34d) | FINISH now (S0, first ship) | Measured cause of the 2026-10-20 jam (14 ships, 137 min slots: FLOW_2026-10-20.md on that branch). Nothing in D7 works while ships queue for hours. Review before ship: SUPER_SESSION rule 11 (gate diff) |
| `research/traffic/FLOW_2026-10-20.md` | exists only on the unjam branch | FINISH with the branch | the jam post-mortem behind the operator's "everything runs, nothing happens" |
| `claude/dazzling-nobel-e74128` (artifacts rebuild, 15 commits ahead) | its ship was running 2026-10-20 04:30 | FINISH if the ship lands; else CLOSE | pages shrink to 2 in D8; rebuilding pages that go away is waste |
| `claude/super-5h-no-cap-9a9128`, `claude/focused-bohr-5dfb28` (MTS Home one screen), `claude/context-diet-f0864c`, `claude/elated-sinoussi-5cb401` (kurisko labels), `claude/vigilant-elion-f5951f` (RSI spec I/J), `claude/infallible-shirley-9cfe03`, `claude/wizardly-dirac-2bd7fb` | 3-9 commits ahead each, touched 2026-10-20; mostly trunk merges plus 1 work commit | FINISH: one ship each in the FIFO, then retire the tree | the work is done; shipping is cheaper than losing it; afterwards `sync.py tidy --apply` |
| `claude/eloquent-shannon-345adc` (Tom fade entry paths, REVIEWED APPROVE) | 7 ahead, 2026-10-18; NEXT_SESSION says the NUC claimed the same card | PARK | Tom v2 is third in the research line (D4); ship when Tom v2 enters |
| `worktree-agent-af8beddd49095a589` (Kurisko module) | 2 ahead; superseded by dd001f2a7 on trunk (FLOW table) | CLOSE | duplicate of landed work |
| `claude/distracted-snyder-ab1792`, `claude/loving-khorana-43085b`, `cloud/2026-10-04-audit-reconcile` | 3 / 3 / 1 ahead, 2026-10-04..18, no owner session | CLOSE (keep the refs 30 days) | stale; nothing references them |
| `keep/*` branches (12) | copies the app made of the branches above | CLOSE with their `claude/*` twin | duplicates |
| `claude/thinker-role-8e2d54` worktree | 0 ahead of trunk | CLOSE (retire the tree) | nothing unshipped |
| `backup/backup/JIS-NB/*` (about 60 refs), `origin/mts-signals` | backups and the signal channel | leave | not work items |
| `.new`: `backtest/layers/fabio/htf_context_live.py.new` + test | 223 h; Fabio v2 waits on ledger repairs | CLOSE (delete the .new) | Fabio is PARKED (D4); a 9-day .new is noise in STATUS.md |

## 3. Cards (48 ready, 8 blocked, 37 refined, 47 raw), grouped
| Group | Cards | Disposition | Reason |
|---|---|---|---|
| Live path and safety | `state-code-accumulator-backfill` (ready p2 JIS-NB), `review-statecode-backfill-gpt` (ready p1 CODEX), `snapshot-vwap-anchor-label`, `gate-quarantine-expiry-cap`, `gap-g7-stop-slippage`, `deploy-runbook-manual-world`, `move-live-host-generated-files-status-md`, `host-legacy-tasks-unregister` (p1) | FINISH: S2 (backfill, vwap, g7, quarantine); S0 (legacy tasks, deploy runbook, generated files) | gap_audit_2026-10-19 GAP-2: session CVD off by -367.4 BTC after a reconnect, state fails open; D3 adds restart safety to the bar |
| Levels Confluence (LC) | `lc-ladder-dev` (ready CODEX), `lc-validation` (refined DSA-NUC) | FINISH in S3 | layer 1 of 2 in D4 |
| CryptoCred HTF | `cryptocred-prereg-4h-1d` done dc745272; the DEV run card is not filed yet | FINISH in S3: file and run the DEV card | layer 2 of 2 in D4 |
| Tom v2 on BTC | `tom-btc-eye-read` (blocked p1: needs the operator as second reader), `tom-btc-encode`, `tom-btc-dev-backtest`, `tom-btc-validation`, `tom-btc-other-setups`, `tom-probe-prereg`, `tom-probe-runner`, `tom-short-coverage-above-vah`, `multi-tf-bias-stack`, `lab-verify-trend-healthy-in-balance` | PARK: next in line when an S3 slot frees | 7 Tom backtests, every one negative net of fees (LAYERS.md Tom rows); the chain is blocked on a human eye-read |
| RSI deep-buy (operator study 2026-10-19: SPEC + 8 raw cards) | `rsi-deep-*` | PARK until an S3 slot frees, unless the operator swaps it in for CryptoCred (q-v1-layers) | newest layer; entering during the freeze breaks the WIP limit |
| Kurisko | `kurisko-prereg-fire-counts`, `kurisko-dev-event-study`, keep/kurisko-provenance | PARK | module landed (dd001f2a7); count-only prereg froze 0 of 8 cells (NEXT_SESSION 10-18): no power yet |
| Krown | `krown-dev-event-study` (CRUCIAL), `krown-data-cme-btc-volume`, `krown-other-sources-event-study-videos`, `trendline-audit-gaps-disposition`, `b-item-krown-core-rsi-returns-100` | PARK | not built, not backtested; 4 of 19 videos blocked on captions |
| WaveTrend | `wavetrend-c1-v2`, `wavetrend-data-inference`, `wavetrend-audit-c1-disposition` | PARK | W01-W03/W09 FAIL, W04-W08 INCONCLUSIVE (STATUS_2026-10-19.md) |
| Malkan / RSI | `malkan-gfs-btc-htf-prereg`, `malkan-prereg-dwm-equities`, `malkan-w1hr-local-whisper-asr`, `rsi-cross-unmapped-and-pivot-stack` | PARK; CLOSE `rsi-cross-unmapped` | divergence: no edge on any TF (RSI-DIV-MTF); the 39 unmapped rsi:cross rejections in the mirrored auto_trades.jsonl are the guard working |
| Positioning, session, pooled trend | `positioning-c1-longwindow-count-power`, `positioning-c1-prereg-no-source`, `pooled-short-lookback-trend-tsmom-30d-sm` (reads the sealed holdout) | CLOSE | family verdicts FAIL/closed (T055 C1-C3, T087); NO-SOURCE; a holdout read is spent once |
| Fabio v2 | `fabio-layer-v2-spec`, `fabio-layer-v2-markets` (OPUS p5), `rv05-h2`, `rv05-h3`, `context-conditioned-session-flow-states`, `oi-pivot-reversal-probability-by-tf` | PARK | v3 OOS FAIL (79 trades, mean -0.10 R); ledger audit FIX-FIRST; Opus research is the costliest lane |
| Callers / analysts | `habib-plan-hit-rate-study`, `qriptal-discord-calls-2026-10-18`, `analyst-ingest-roman-x`, `review-ground-layer-youtube-strategy-and` | PARK into S4 (CBP module); CLOSE `review-ground-layer` | CBP-module work (D5); the scorecard needs 56 scored calls before any weight (analysts/SCORECARD.md section 2) |
| DSA audits of the backtest base | `dsa-audit-04..10` (ready DSA-NB; desk rows STALE 4 days), `dsa-audit-08` (blocked CODEX), `rv-dsa-q33-rerun`, `rv-dsa-test-sweep` | FINISH T06 (cost/fill realism) and T09 (live parity) in S3 on a Claude or Codex lane; PARK T04, T05, T07, T08, T10; CLOSE the rv-dsa rows | the DSA-NB lane has not taken a row in 4 days; T06/T09 decide whether S3 numbers can be trusted |
| Lab tooling | `lab-formula-spec-text`, `lab-formula-spec-recount`, `lab-planted-error-trial`, `argon-blind-read-7-frames`, `one-timeframe-map-for-the-whole-toolchai`, `tc5-lab-lane-dedupe`, `tc2-lab-runners-set-lease-env` | FINISH `lab-formula-spec-text` + `tc5-lab-lane-dedupe` in S0 (Codex, prepaid); PARK the rest | dedupe stops double runs (jam cause 2); spec text makes re-derivation possible |
| Process / docs / tooling | `tc3-budget-lines`, `tc4-desk-done-once`, `tasks-sweep-closed-cards`, `card-worker-fields`, `roles-md-index-slim`, `ai-behavior-fold-or-archive`, `pipeliner-boot-diet`, `super-session-rules-to-pointers`, `trim-builder-cwd-and-prelaunch-worktree`, `trim-claudemd-re-read-guard`, `research-top-level-declutter`, `shot-py-store-path-nuc`, `mid-turn-image-intake-gap`, `aibridge-version-not-bumped`, `java-popups` | FINISH `tasks-sweep-closed-cards` in S0; CLOSE the rest or fold into D8 | 293 done cards in the live folder slow every `tasks.py` call; the others each save minutes and cost a session |
| q17 cards | `q17-p3-one-work-list`, `q17-p4-bookkeeping-out-of-git`, `q17-p5-three-pages` (raw) | FINISH P4 in S0; P3 and P5 are replaced by D8 | P4 attacks the 44 % plumbing share; D8 goes further than P3/P5 |
| Fable / context studies | `fable-setups-pack-prep`, `context-composite-v2-dev-read`, `indicator-values-multi-model-audit` (claimed 6 h) | FINISH the claimed audit; PARK the two others | Fable runs need one operator message each (WORKERS rule 5) and are not on the S3 path |
| AWS Bedrock pilot | `aws-bedrock-extraction-pilot` | CLOSE unless the operator has 2 free hours before 2026-10-25 | serves Tom transcript extraction, and Tom v2 is parked (D9) |
| CI leftovers | `ci-919cc0f` (p0; CI green x3 per NEXT_SESSION) | CLOSE | stale |

## 4. Desk rows, claims, scheduled tasks, routines
| Item | State | Disposition | Reason |
|---|---|---|---|
| 7 DSA-NB audit rows (2026-10-16) | STALE 93.6 h (FLOW), never taken | re-post T06 + T09 as Claude cards; CLOSE the other 5 rows | see the cards row above |
| JIS-NUC rows: send pages to repo, stop the NUC inbox poller, AIBridge 0.7.1 install | pending 1-3 days | FINISH "stop the poller" in S0 (a poller is a routine); CLOSE the other two | pages shrink (D8); the AIBridge lane is retired unless its queue drains (D8) |
| JIS-NB rows: java-popups parent, republish 3 stale pages | pending | PARK java-popups; CLOSE republish | D8 keeps 2 pages, republished from one login |
| DSA rows: krown CME volume, T02/T03 blocked-data reruns, 2 indicator-audit blind packets | pending | PARK | all serve parked layers or a parked audit |
| Claims STALE: `backfill-t087-session-level-split-and-ve` (done on trunk per NEXT_SESSION), `encode-v1-only-kill-scope-for-weekly-low`, `funding-carry-with-real-spot-basis-margi` | 35-41 h, no commit | release all three (`sync.py release`) | PARALLEL.md: ask the owner or release; the owners' hand-overs say nothing was started |
| Windows tasks on JIS-NB: enabled `MTS testnet canary`, `MTS testnet status`, `MTS-Alert-Rate-Check`, `MTS-Audit-Digest`, `MTS-Audit-Rotation`, `MTS-CDriveCare`, `MTS-Declutter-Backups`, `MTS-Feed-Watchdog`, `MTS-Live-Health`, `MTS-Make-Status`, `MTS-OI-Recorder`, `MTS-Orphan-Watchdog`, `MTS-Retention`, `MTS-Wrapper`, `MTS_Monitor_4h`; disabled: AutoDeploy, Backup, DailyHygiene, DispatchGate, LiveMirror, Scheduler-Tick, Supervisor | against SCHEDULING_POLICY.md (none allowed); card `host-legacy-tasks-unregister` p1 ready | operator decision q-v1-keepers: unregister all 22, or keep an explicit keeper list (Feed-Watchdog, Live-Health, OI-Recorder, Wrapper, canary) and unregister 17 | the GO-LIVE BAR needs 95 % uptime; a stack with no reviver and no coordinator running cannot hold it (D3 item M4) |
| CBP routine `cbp-daily-workflow` (Claude scheduled task, Haiku, 3x/day; CryptoScrapper/cbp_v2/PIPELINE.md 2026-10-15) | a routine, against SCHEDULING_POLICY.md; NEXT_SESSION says the check is owed | operator decision q-v1-cbp-routine: keep it as the one named exception, or the coordinator runs the CBP pipeline on wake | D5 makes CBP an MTS module; its schedule obeys the MTS policy either way |
| Gap audit 2026-10-19 (Gemini, T0-ONLY review) | 8 gaps | GAP-1/2/3 are in D3 and S2; GAP-4/6/7/8 are the unjam branch and D8; GAP-5 (10 zombie cards, 6 gemini-q branches: no `gemini-q/*` ref exists on origin today) gets a one-time reconcile in S0 | the audit is unreviewed; take the proofs that quote file:line, not its token estimates |
| BUGS.md 71 OPEN rows | 18 are from 2026-09 with no receipt in 3 weeks | S0 rule: every OPEN row gets a stage tag (S2/S3/S4/S5) or CLOSE, one Pipeliner pass; default CLOSE for rows older than 21 days with no receipt | a registry nobody reads only grows |
| OPERATOR_INBOX.md 5 entries (2026-10-11/12) | not re-read here | the Pipeliner closes them in the same pass | outside this session's budget |

## 5. Untouched by this inventory
The live tree, `auto_trader_config.json` (the 2026-10-23 review is its own decision, D4 section 4), keys, `.secrets`, the holdout data, every backup branch.
