# Session MTS-2026-10-01-1916Z-CLD-BLD-two-cores-int/sonnet-04: TWO CORES SWITCHABILITY (WAVE 4, spec only, no code)
Doctrine: ARCH:70-83. Checkout 9695b36, branch claude/quirky-knuth-y2u3ij. Every factual line cites file:line against the COMMITTED tracked files at that checkout (verified: `git diff --stat 9695b36 HEAD` is empty for execution/, backtest/layers/alerts/, TLB, orderflow_bars.py, timeframe/, scripts/, mts.ps1, .gitignore, CLAUDE.md, session_state.py, SUPERVISOR_LOG, FABIO_V3_SPEC, ARCH, SCAF, READY, PROMPT; the later wave commits do not touch them). "unknown" = the clone shows nothing; no rule is inferred. Not reopened: two cores, modules never gate (ARCH:7-9, :27, :43). Task source: PROMPT:114-127.
Task wins over SCAF section 5 (SCAF:41-46): the block moves from execution/auto_trader_config.json to MyTradingSys/runtime/cores_config.json (PROMPT:119), and the module keys are `rsi_obs` / `consensus` (SCAF:44 had rsi_observation / consensus_writer).

Cite keys (repo-relative):
- AT = MyTradingSys/execution/auto_trader.py; ATC = MyTradingSys/execution/auto_trader_config.json (tracked: git ls-files)
- LRC = MyTradingSys/backtest/layers/alerts/live_runner_cli.py; LRK = same dir, live_runner_core.py; TLB = MyTradingSys/backtest/layers/test_layer_boundaries.py
- ARCH / SCAF / READY = MyTradingSys/research/{ARCHITECTURE_TWO_CORES, TWO_CORES_SCAFFOLD, TWO_CORES_READINESS}_2026-10-01.md; PROMPT = MyTradingSys/research/CLOUD_PROMPT_TWO_CORES_INTEGRATION_2026-10-02.md
- SPEC = MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md; SUP = same dir, SUPERVISOR_LOG.md; RAT = scripts/dev/run_all_tests.py; TNS = scripts/dev/testnet_status.py
Other paths: execution/{position_manager,trade_ledger,orphan_watchdog_cli,test_auto_trader,test_fabio_slot}.py, execution/{TESTNET_SUBACCOUNTS,FABIO_TESTNET_SLOT}.md and mts.ps1 are under MyTradingSys/execution/ (mts.ps1 at repo root); live_layers.py, test_live_runner_cli.py under backtest/layers/alerts/; orderflow_bars.py under backtest/layers/fabio/; registry.json, tf_resample.py under backtest/layers/timeframe/; alert_rate_check.py, run_staged_tests.py under scripts/dev/; tests/ = MyTradingSys/tests/; CONSOLIDATION_REPORT_2026-10-01.md in research/; MAINTAINER_REPORT_2026-09-30.md in research/fast_track_2026-09-27/.
Cites are to the tracked .py, not to any .new (an auto_trader.py.new exists in the tree, staged by this task for TF_SECONDS 3m per SUP:241; its content was not read; AT line numbers shift when it is promoted).

## 1. Config block shape
One file, one loader. Exact JSON (flags as the ARCH defaults; shipped value of `cores.fabio` is decision D1 below):
```json
{
  "cores":   { "tom": true, "fabio": true },
  "modules": { "rsi_obs": true, "consensus": true }
}
```
Value type: JSON bool (not `{"enabled": bool}`). Why:
1. ARCH:72 defines each as one enable flag; no per-flag parameter is documented anywhere read (unknown if any are planned).
2. The existing `{"enabled": ...}` nesting exists because those blocks carry other fields (AT:52-53 size_usd/max_loss_usd/hours...; AT:55-57); the new block has none, so a wrapper (SCAF:43-44) is empty nesting.
3. PROMPT:117-118 writes the block flat (`cores {tom: on, fabio: on}`).
4. Only a real JSON `true` counts as on (section 2), so the string "false" cannot be truthy.
Cost: if a per-core parameter is added later the bool form needs a one-time migration.

Defaults (ARCH:73 lists Tom, Fabio, RSI observation; the consensus default comes from the task, PROMPT:117-118, not from ARCH:73):
| Flag | Default | Shipped value proposed | Note |
|---|---|---|---|
| cores.tom | on (ARCH:73) | true | = today: AT:52 `enabled: True`, and ATC:9-19 has no `enabled` key |
| cores.fabio | on (ARCH:73) | **false pending D1** | see D1 |
| modules.rsi_obs | on (ARCH:73) | true | observation only, never gates (ARCH:27) |
| modules.consensus | on (task) | true | observation only (ARCH:43) |

**OPEN DECISION D1 (supervisor; not decided here): default of cores.fabio.**
- SPEC:249-267 (section 8) requires stage 0-3 + holdout evidence and the pass criteria at SPEC:266-267, ending "Then testnet as its own layer (FTM:69) via a supervisor task" (SPEC:267). No result of that evaluation is in the tree: unknown.
- SPEC:234: TRIAL_REGISTRY.csv "does not exist yet"; `find . -name 'TRIAL_REGISTRY*'` finds none.
- The compiled core has no selected NS-grid cell: NS-grid values are registered grids, not values (SPEC:11-12, :192-231, :236-244); the IS-best cell per model is a section 8 output (SPEC:261); grep for "chosen cell / selected cell / IS-chosen" in research/ hits only T055 files and SPEC:243-244 (no Fabio v3 cell recorded). Provenance rule: no tuning of NO-SOURCE parameters (CLAUDE.md:26-27).
- Proposal: ship `cores.fabio: false`; the flip to true is a supervisor action after the section 8 result. The flag is inert until steps 3-4 land (nothing reads it before), so the shipped value matters at the step 3 promote. SCAF:26 records the same gate.

How the block maps onto existing toggles (single source of truth = cores_config.json for switching a core or module; legacy keys stay in place, unedited):
| Existing | Cite | Governs | Relation proposed | Untouched |
|---|---|---|---|---|
| "tom".enabled | AT:52; checked AT:125 | Tom signal -> trade only (not Tom alert emission) | effective = legacy AND cores.tom, applied once at boot right after the merge (AT:545-547); either off = off. cores_config can only add a veto or lift its own veto; it never overrides a legacy `false` | key, default, check site AT:125 |
| "layers".enabled | AT:55; checked AT:211 | every layer family's trades | none: not a core or module flag | all |
| "disabled_layers" | AT:64; checked AT:211 as `layer in cfg["disabled_layers"]` = exact layer-name membership, not a prefix (SCAF:45 says "prefix": wrong) | per layer-name reject | cores.fabio does not write to it (decision D4) | all |
| "accounts" | AT:67 default `{"layer:fabio:": "fabio"}`; ATC:2-8 overrides; shallow merge AT:547 | prefix -> account label; no enable semantics (AT:248-258) | step 4 adds one key; independent of the flags | AT:67 (test_fabio_slot.py:35,62 build cfg from DEFAULT_CONFIG and assert it) |
The only reader of the legacy toggles in any .py/.ps1/.java/.json is AT (grep `tom.*enabled|disabled_layers`: AT and test_auto_trader.py only). The `start` event (AT:552 logs dry_run, brakes, tom_last_alert_no) should also carry the four resolved flags and the legacy `tom.enabled`, so the operator can see why Tom is off (proposal; D5 covers AND vs overwrite).

## 2. Where it lands
- Config: MyTradingSys/runtime/cores_config.json (new). runtime/ already holds tracked config/state JSON next to a Python module (session_state.json + session_state.py: runtime/session_state.py:14-16). .gitignore has no entry for it (it ignores runtime/alerts/*.jsonl and live_alert_state.json only, .gitignore:89-90), so it is tracked like ATC; a live flip therefore dirties the tree (policy: unknown, item 13).
- Loader: MyTradingSys/runtime/cores_config.py (new), one function `load_cores_config(path=None) -> dict`: returns the four bools plus a `problems` list; stdlib only (json, pathlib); never raises; no cache (re-reads every call); default path `Path(__file__).resolve().parent / "cores_config.json"` (precedent runtime/session_state.py:14-15). Proposal; names are not fixed by any doc.
- Import direction (TLB): layers/ must not import MyTradingSys.execution (TLB:54, :60-74) and execution/ must not import MyTradingSys.backtest.layers (TLB:92). A loader under layers/ breaks AT; one under execution/ breaks LRC (LRC:5-6 also says no execution imports). runtime/ is named by neither rule, and no .py imports it as the package `MyTradingSys.runtime` today (grep; runtime modules are imported by bare name after a sys.path insert, tests/test_math_object_builder.py:6, :9). Allowed edges: LRC -> runtime/cores_config.py; AT -> runtime/cores_config.py; the loader imports neither tree. Because the two trees cannot import each other, the Fabio core's output must reach AT by file hand-off, as Tom (AT:45) and the layers (AT:46) already do.
- Import mechanics: no `__init__.py` anywhere on the path (ls MyTradingSys, runtime, execution, backtest, backtest/layers) so namespace imports work: LRC already uses package-style imports (LRC:17-20). AT has no `MyTradingSys.*` import: it resolves siblings by `sys.path.insert(HERE)` inside functions (AT:303-305, :368-370), its tests do the same (test_auto_trader.py:9-10), and the RAT Step 1 (execution tests) gate copies only execution/*.py|json into a temp dir (scripts/dev/run_staged_tests.py:25-29, called at RAT:77-88). A top-level `import MyTradingSys.runtime...` in AT would break that gate. Proposal: AT imports the loader lazily inside main() (same lazy pattern), ImportError = fail closed; tests inject a path.

Behaviour (fail closed; CLAUDE.md:34-35 "safety checks fail closed" applies to live-path changes; a core flag decides whether new entries open):
| Condition | Result | Reason |
|---|---|---|
| file missing | all four flags false, problem logged | cannot prove any flag on. The file ships with the loader, so missing = abnormal. Cost: Tom stops opening trades at the next auto_trader restart (D6) |
| invalid JSON / not an object | all four false | same; both existing readers fail OPEN to defaults (AT:84-88 `load_json`, runtime/session_state.py:47-58), and AT's defaults have Tom on (AT:52), so the new loader does not reuse them |
| "cores" or "modules" not an object | that block's flags false | other block unaffected |
| known key missing | that flag false | defaults live in the shipped file, not in code |
| known key not a JSON bool (string "false", 0/1, null, `{"enabled":..}`) | that flag false; other flags unaffected | Python truthiness: "false" is truthy; check `is True`. Per-flag so a bad Fabio value cannot change Tom (ARCH:74) |
| unknown key (any level) | ignored, listed in `problems`; changes no flag | cannot enable anything; a typo is visible in the log |
| any exception inside the loader | caught; all false | LRC main catches only KeyboardInterrupt (LRC:288-294), AT main likewise (AT:561): a raise would end the process |
Atomic writes by whoever edits it: temp file in the same directory then `os.replace` (precedents AT:91-94 `save_json`; runtime/session_state.py:35-45), `newline='\n'` (CLAUDE.md:24; AT:93), backup `.pre_<tag>` first (CLAUDE.md:22; ignored by .gitignore:77). Contrast LRC:108-116 `save_state` (opens the real path 'w', not atomic), so a reader can see a partial file; hence fail-closed on invalid JSON.

## 3. Read cadence
| Process | Reads cores_config | Where | Effect of a flip |
|---|---|---|---|
| auto_trader | boot only | `main()` after the config merge, before `state = load_json(...)`: between AT:547 and AT:548 | next restart |
| live_runner_cli | every tick | top of `loop_body`, before `poll_once` (LRC:259-261); `--once` goes through the same body (LRC:284-286) | next tick (`--poll-seconds` default 60, LRC:251) |
Verified boot-only for AT: the `--config` path is read at AT:543 (default ATC) and `cfg` is built once at AT:545-547 and the same object is passed to every `cycle` (AT:556); `cycle` and its callees only read `cfg` (AT:124, :173, :204, :211, :250); `load_json` is called at AT:507 (Tom alert), :546 (config), :548 (state), :550 (Tom alert) and nowhere else. Operator docs say the same: restart needed (SUP:183; FABIO_TESTNET_SLOT.md:13).
What AT re-reads per poll (not config): Tom alert file (AT:507), layer alert files by byte offset (AT:510 via :179-200), brake files (AT:511 via :240-241), AUTO_PAUSE (AT:518), account secret-file existence (AT:252 via :521), exchange position only when a manager exits (AT:333).
LRC placement notes:
- The registry is built once (LRC:256) and the loop reuses it (LRC:261). LRK stays pure and "never ... filters signals" (LRK:4-8), so flag logic lives in LRC, not LRK.
- To switch legacy registry entries per tick: filter the dict handed to `poll_once` (LRC:202, :218) rather than dropping alerts after the run: LRK marks events emitted and advances state before LRC sees them (LRK:144-148, :154-155), so a post-filter would swallow events silently. On re-enable LRK allows only `lag + 1` bars of backlog (LRK:129-132). Proposal; supervisor chooses.
- A registry entry cannot carry the Fabio core: LRK:116 calls `entry["fn"](bars)` with kline-mapped bars only (LRC:23-53). How the peer is invoked is step 3's design (unknown, item 7); the flag read at LRC:260 applies to whatever call site step 3 adds.

## 4. Migration order (exactly four steps)
Gate common to every step: `python scripts/dev/run_all_tests.py --quick` (CLAUDE.md:13-14; RAT:72) and CLAUDE.md:16 (new tests must fail on the pre-change code once; for a new module, fail-first on a deliberately broken copy, as READY:59 does). Promote protocol: back up to `.pre_<tag>`, rename, re-gate, commit (CLAUDE.md:22). Builders stage `.new`, never edit in place, never stop/restart, never touch HALT/AUTO_PAUSE or open trades (CLAUDE.md:31-33); every brief touching execution/ or layers/alerts/ repeats that. Gap: RAT:62-67 collects only committed layer tests and run_staged_tests.py copies flat dirs (:25-29), so `.new` files under backtest/layers/ are not covered by `--quick` until promoted (item 11).

### Step 1. Core modules land
- Changes: the staged pieces become promotable; nothing reads cores_config yet.
- Files, all "staged by this task", contents not read here. Present at spec time (`find . -name '*.new'`): backtest/layers/fabio/v3/{signals,fill,manage,costs,day_gates}.py.new (Wave 2 in flight: models, engine, `__init__` .py.new and files under fabio/tests/ not present yet, PROMPT:69-77, :82-84); backtest/layers/consensus/writer.py.new (+ test_writer.py.new); backtest/layers/rsi/observation.py.new (+ test_observation.py.new); runtime/math_object_builder.py.new (book_imbalance fix, READY:8, :55) with tests/test_book_imbalance_nodata.py.new, tests/test_proof_direction.py.new, research/core_readiness_2026-09-27/harness/proof_direction_cases.py.new; TF maps: execution/auto_trader.py.new + test_auto_trader.py.new (SUP:241), scripts/dev/alert_rate_check.py.new + test_alert_rate_check.py.new (READY:19). Which of these exist at promote time must be re-listed then.
- Owner: builders stage; supervisor promotes the live-path ones (math_object_builder: Tom engine, live-safety, READY:8; auto_trader.py.new: execution/ claim SUP:241). Others are not on CLAUDE.md:31-32's live-process list.
- Gate: common gate; the book_imbalance test must fail on current code (READY:55).
- Acceptance (ARCH:78-83): none end-to-end (no flag, no wiring yet). Module-level checks only as far as each staged test file provides: unknown.

### Step 2. Config + loader
- Changes: add runtime/cores_config.json and runtime/cores_config.py (section 2). No live process imports either yet.
- Files: both new; test proposal tests/test_cores_config.py (RAT:126 collects MyTradingSys/tests; runtime-module import style test_math_object_builder.py:6, :9). Ship the JSON in the same promote as the loader, before any process restart that reads it (missing file = all off, section 2).
- Owner: builder stages `.new`; supervisor promotes (new files; no restart needed, no execution/ or layers/alerts/ claim needed).
- Gate: common gate; loader tests = one per row of the section 2 table, plus: re-read picks up a rewritten file; a bad Fabio value leaves Tom true; never raises. TLB runs in RAT Step 5b (RAT:160-165) and must stay green: no new import edge exists yet.
- Acceptance: none of ARCH:78-83 yet; the loader-level precondition of ARCH:78-79 is "one flag's invalid value never changes another flag".

### Step 3. live_runner wires the Fabio core as a peer (supervisor-owned live path)
- Changes in LRC (staged `.new`): read the loader at LRC:260; apply flags per section 3; call the Fabio core as a peer; gate the RSI observation and consensus hooks on `modules.*` (the runner is the only per-tick reader; Tom-side consensus hook unknown, item 9). Alert transport for the core: unknown (item 2).
- BLOCKER, order-flow bars: LRC:23-53 maps klines to `t,o,h,l,c,v,tbv` only and fetches spot klines (LRC:84); SPEC:24-28 needs `buy_vol, sell_vol, delta, b99_*, b999_*, thr_days, fp` per 1m bar, built offline from USD-M aggTrades (orderflow_bars.py:2-4, thresholds from prior-30-day sidecars :19-23). No live source of those columns exists in code: unknown (item 5). Also unverified: Deribit tick and basis (SPEC:33).
- Files: LRC.new; tests test_live_runner_*.py (tolerant of added registry keys: test_live_runner_cli.py:70-73); import only `MyTradingSys.runtime.cores_config` (TLB:54 rule, LRC:5-6).
- Owner: supervisor (CLAUDE.md:28; PROMPT:147 "supervisor-owned; live path"). SUP:241 claims only auto_trader.py.new and test_auto_trader.py.new; a layers/alerts/ claim in SUP is required before any LRC.new (none found: grep claim/owner in SUP shows only :241 as an OWNERSHIP claim). Supervisor restarts the runner after promote (CLAUDE.md:31-33; runner has no mts.ps1 verb: READY:9; SUP:207 shows a manual restart).
- Gate: common gate (RAT Step 5b covers committed live_runner tests and TLB, RAT:160-165) + CLAUDE.md:34-35 tests: restart/reset state (state reload LRC:96-105 across a flag flip), API errors (per-TF fetch failure isolated, test_live_runner_cli.py:112), non-trade balance moves (applicability to an alert-only runner, LRC:5-6: unknown).
- Acceptance: ARCH:78-79 runner half (flip cores.fabio between ticks; legacy-layer alerts and Tom outputs for fixed inputs identical; flip cores.tom; Fabio output identical); ARCH:80 (fire N alerts, count N consensus rows) once the writer is wired; ARCH:82-83 (six TF keys) needs TF coverage (item 10).

### Step 4. auto_trader routes source `fabio-core` to the fabio testnet account
- Changes in AT (staged `.new`): (a) lazy loader call in `main()` between AT:547 and AT:548, AND-ed into `cfg["tom"]["enabled"]` (section 1) and kept as the Fabio gate; (b) a new signal builder next to AT:507-510 that yields `{"source": "fabio-core", ...}`, because source strings are built in code only: "tom" at AT:150, `layer:<layer>:<sub>:<tf>` at AT:208. A config line alone creates no source (PROMPT:148-149 describes it as a config line: conflict, section 7); (c) log the resolved flags in `start` (AT:552).
- Exact accounts entry (ATC `accounts` block, ATC:2-8; shallow-merged on DEFAULT_CONFIG at AT:547, so the five existing prefixes stay):
```json
"accounts": { "...existing five unchanged...": "...", "fabio-core": "<label>" }
```
  `<label>` is decision D3. Matching is `source.startswith(prefix)`, first match in dict order, and it returns even when the secret file is missing (AT:250-258; TNS:105-110 route() mirrors it). The existing "layer:fabio:" (ATC:4; AT:67) does NOT match "fabio-core" (startswith), and its colon also stops it catching "layer:fabio-core:..."; so a new prefix is needed. The key is not under "layer:", so its position relative to the "layer:" catch-all (ATC:7) does not matter; if instead the core travelled the layer path (source `layer:fabio-core:<sub>:<tf>`, AT:208) its key would have to precede "layer:". A bare key "fabio" would also match any later source starting "fabio".
- Other maps that read the same prefixes (CLAUDE.md:30 says grep every family map): TNS:95-102 `family_of` makes "fabio-core" its own family; TNS:197-202 `expected_keys` adds only `layer:` prefixes, so a fabio-core row gets no zero-trade flag unless extended; orphan_watchdog_cli.py:24-33 and trade_ledger.py:255-262 take every `accounts` VALUE as a label (label regex `[a-z0-9_]{1,32}`, orphan_watchdog_cli.py:18).
- Files: AT.new, test_auto_trader.py.new (same `.new` as the TF_SECONDS one: one staged copy per file), test_fabio_slot.py (routing tests; run at RAT:85), ATC (edit via `.new` + `.pre_<tag>`, SUP:181-183 precedent).
- Owner: supervisor (execution/ claim: SUP:241 must be extended beyond TF_SECONDS 3m, CLAUDE.md:28). Builder stages only; supervisor promotes and restarts auto_trader after the commit is gated (CLAUDE.md:31-33). Whoever sets AUTO_PAUSE logs owner + expected end (CLAUDE.md:29).
- Gate: common gate (RAT Step 1, the execution tests, runs test_auto_trader and test_fabio_slot, RAT:85) + CLAUDE.md:34-35 tests: restart/reset state (boot read; open fabio-core plan adopted after restart, `recover_slots` AT:463-493, tests test_auto_trader.py:326-361), API errors (`settle_slot` paths AT:326-362, tests :250-294), prefix routing, per-account busy and missing-secret fallback modelled on test_fabio_slot.py:60-63, :65-75, :77-88. Pre-flight before enabling cores.fabio: `account_for("fabio-core", cfg)` must return the label (existence check only, AT:252): otherwise the signal falls to the default slot shared with Tom (AT:521-522; test_fabio_slot.py:77-88).
- Acceptance: ARCH:78-79 in both directions (cores.tom false: `tom_signal` None at AT:125 and Fabio signal identical for a fixed input; cores.fabio false: no fabio-core signal and `tom_signal` output identical); ARCH:81 ledger scan: `source` of core-originated rows is only the Tom value or the Fabio-core value (trade_ledger.py:129 copies `attempt["source"]`, written at AT:513, :528), scoped to core rows (item 8).

## 5. Backout
Flip the flag in cores_config.json (atomic write, `.pre_<tag>` backup), then restart where the cadence requires:
| Flip | Process | Restart? | Cite / note |
|---|---|---|---|
| cores.fabio -> false | live_runner_cli | no (per tick, once step 3 lands) | LRC:259-261, :288-291 |
| cores.fabio -> false | auto_trader | yes, to load its boot-only copy | AT:545-547, :556. Until restart (once step 4 lands) it still accepts fabio-core signals already on disk; the runner stops producing new ones within one poll |
| cores.tom -> false | auto_trader | yes | AT:125 reads the boot copy. Tom alert emission is unaffected: the flag has no reader in the emitter path (grep over .py/.ps1/.java/.json); last_alert.json is written under $LogDir by scripts/core/start-trading-day.ps1:766-767 (whether $LogDir is runtime_data: unknown, SCAF:7) and read at AT:45, mts.ps1:134 |
| modules.* -> false | live_runner_cli | no | per tick. If any module/consensus hook lives in auto_trader the cadence there is boot-only: owner of the Tom-side hook unknown (item 9) |
| any, before steps 3-4 | none | n/a | nothing reads the file yet |
Restart is supervisor-only (CLAUDE.md:31-33). auto_trader: `python -m MyTradingSys.execution.auto_trader` (mts.ps1:243-248; SUP:183 describes stop + restart). Runner restart has no mts.ps1 verb (READY:9). Backout of a promoted code file: restore `.pre_<tag>`, then restart (CLAUDE.md:22; SUP:183).
Open trade of the disabled core: flipping a flag does not close it. From code:
1. Flags gate only new signals (AT:125, :211). Open slots are settled first in every cycle for all sources (AT:501-505; `settle_slot` AT:326-362).
2. position_manager.py has no config, `enabled` or `source` reference (grep: only a docstring mention at :70); executor.py, new_plan.py, plan_compiler.py do not use "source". The manager keeps its stop invariant (position_manager.py:9-10), and the server-side stop protects the position even if the process is not running (position_manager.py:43-44); time exit comes from the plan's `max_hold_minutes` (position_manager.py:217-225, :280-321).
3. A restart rebuilds slots from auto_trades.jsonl alone (no config input): AT:442-460, :463-493; live manager adopted (AT:486-488), dead manager respawned or closed per the exchange check (AT:326-358), ledger row written (AT:361, :365-376).
4. No "flatten on disable" path exists in the code read. Manual tool in docs: `kill_switch.py --confirm KILL --account <label>` (TESTNET_SUBACCOUNTS.md:23; FABIO_TESTNET_SLOT.md:26). Whether the operator wants disable to also flatten: unknown (item 12).

## 6. Open items / unknowns (numbered; [D] = decision for the supervisor, [U] = unknown; D1..D6 are the labels used in sections 1-5, they are not item numbers)
1. [D1] cores.fabio shipped default: section 1; SPEC:234, :249-267, :261.
2. [D2/U] Source value and transport. Value: "fabio-core" (PROMPT:122-123, :148), "fabio" (ARCH:47; PROMPT:151) or a layer-path source `layer:fabio-core:...` (AT:208). Transport of the core's alerts to AT (file, path, schema): no doc fixes it. Hazard: AT reads every `*.jsonl` in MyTradingSys/runtime/alerts (AT:184, :46; LRC:249) and trades any alert with a `side` field (AT:171-172; live_layers.py:8), with the fixed 1% bracket and the `layers` toggles (AT:211, :230-232), not the core's own stop/target. A Fabio-core, RSI-observation or consensus file must not be written into that directory unless that is intended. Consensus path also differs between docs: SCAF:30 runtime/consensus vs PROMPT:100 Dumps/consensus (neither is inside runtime/alerts).
3. [D3] Account label for the fabio-core source: "fabio" (AT:67; FABIO_TESTNET_SLOT.md:5), "jishu_3" (ATC:4; CONSOLIDATION_REPORT_2026-10-01.md:32; MAINTAINER_REPORT_2026-09-30.md:32-33), or a new label (needs an operator-written secret file, AT:244-245; existence unknown, `.secrets/` not opened). ATC:4 and ATC:6 already put "layer:fabio:" and "layer:rsi:" on jishu_3, and busy is per account (AT:522-525), so a shared label ties Fabio-core entries to other layers' open trades. TESTNET_SUBACCOUNTS.md:9 (jishu_1) is stale (MAINTAINER_REPORT_2026-09-30.md:32).
4. [D4] cores.fabio vs the legacy layer:fabio:* detectors (cvd_absorption 1h/15m LRC:159-172; escalation/volume_fvg 1h LRC:176-177, 15m LRC:187-188). ARCH:55 says Fabio moves from loose layer alerts into a core; ARCH:67 says add, do not modify; SPEC:273-274 says do not reuse the three detectors (kline proxies). Options: (a) cores.fabio governs only the new core, legacy detectors stay under `layers.enabled` / `disabled_layers` (AT:211); (b) cores.fabio=off also drops layer "fabio" (exact-name list entry). Unknown which is intended. Under (a), "disable Fabio" leaves layer:fabio:* trades running.
5. [U] Order-flow bar feed for the core: LRC:23-53, :84 vs SPEC:24-28, orderflow_bars.py:2-4, :19-23. No live producer in code; the 30-day threshold sidecars are offline artefacts (orderflow_bars.py:22).
6. [U] Registry contract cannot carry order-flow bars (LRK:104, :116).
7. [U] How the peer is invoked inside LRC.loop_body, and where its flag check sits: step 3 design, not in any doc.
8. [U] ARCH:81 "every trade row carries source: tom or fabio" vs existing trades with `layer:*` sources (AT:208; trade_ledger.py:129); ARCH:48 examples (layer:rsi:40_60, layer:rsi:ma_60) match no registered sub (LRC:140, :180-181) and AT:208 always builds four segments incl. tf. The test must be scoped to core rows, or the wording changed: supervisor.
9. [U] snapshot_id owner: no code defines it (grep: only ARCH:34, :42, SCAF:31-32 mention it). Consensus writer owner/hook, Tom-side hook and therefore the cadence of modules.consensus: unknown (SCAF:32).
10. [U] RSI block TF coverage (1m,3m,15m,1h,4h,1d, ARCH:39): runner fetches `--tfs` default 1h,15m,5m,1m (LRC:247), so 3m, 4h, 1d are not fetched; AT:48 TF_SECONDS lacks 3m (a layer alert on an unknown tf is rejected "no t_close/tf", AT:217-219); alert_rate_check.py:23 TF_MIN lacks 3m and 1d; the timeframe registry has 3m, 4h, 1d (timeframe/registry.json:9, :16, :20) and `resample` builds them from 1m bars (tf_resample.py:82). PROMPT:105 lists seven RSI keys (adds 5m) vs six in ARCH:39, :82-83: the "all six TF keys" test needs one definition.
11. [U] Gating `.new` under backtest/layers/: RAT:62-67 (committed tests only) and run_staged_tests.py:25-29 (flat copy). How staged layer code is run before promotion: unknown.
12. [U] Policy for an open trade when its core is switched off (flatten vs let it run): section 5 shows only the code behaviour.
13. [U] Tracked-file churn: a flag flip changes a tracked file on the tree that runs the live system; commit/ignore policy unknown (precedent: ATC tracked, edited live with `.pre_*` backups, SUP:181-183).
14. [D5] AND vs overwrite for "tom".enabled + cores.tom (section 1 proposes AND).
15. [D6] Missing or invalid file = all off (section 2 proposes). Cost: a bad edit stops Tom at the next restart; supervisor confirms.
16. [U] Independence gaps beyond the flags: (a) default slot shared with Tom when a named account's secret file is missing (AT:521-522; AT:254-256 logs once; test_fabio_slot.py:77-88); (b) HALT / HALT_DAILY_LOSS / AUTO_PAUSE are global (AT:511-519); (c) `cycle` has no try/except around the signal builders (AT:507, :510) and `main` catches only KeyboardInterrupt (AT:561), so an exception in a new fabio-core builder would stop Tom trading too; (d) one `place()` blocks the loop (AT:268-287, 900 s default timeout AT:261).
17. [U] Re-enable replay: Tom `tom_signal` returns at AT:125 before marking an alert seen (AT:130) and rejects stale alerts after `max_age_seconds` (AT:52, :141-142); the runner allows `lag + 1` bars (LRK:129-132). How a disabled core appears in the per-poll line (counts every registered key, LRC:227-238) is unknown.
18. [U] Tom "its alerts stop" (ARCH:74): the only Tom switch is on the trading side (AT:125); whether the flag must also stop Tom alert emission is unknown.
19. [U] Pre-existing, outside this spec: `load_json` fails open (AT:84-88) and DEFAULT_CONFIG sizes (AT:52 size_usd 200; AT:55 100) differ from the live file (ATC:10, :21 = 10), so an unreadable ATC silently reverts to default sizes. Observed only; not changed here.
20. [U] ARCH:87-89 OPEN (runner path) is resolved at this checkout: the runner is MyTradingSys/backtest/layers/alerts/live_runner_cli.py (READY:9).
21. [U] Other ARCH modules (probability distribution, tick-delta T040, session frame, ARCH:24-26) have no key in the task's block; the loader ignores unknown keys by design, so adding one later is a loader + file change.

## 7. Conflicts: task / scaffold / docs vs code
| Item | Says | Code or doc shows |
|---|---|---|
| Block location | SCAF:42: execution/auto_trader_config.json | task wins: runtime/cores_config.json (PROMPT:119) |
| Module keys | SCAF:44: rsi_observation, consensus_writer | task: rsi_obs, consensus (PROMPT:117-118) |
| Value type | SCAF:43-44: `{"enabled": bool}` | proposed plain bool (section 1) |
| disabled_layers | SCAF:45: "prefix 'fabio'" | exact layer-name membership (AT:211) |
| SCAF cites | auto_trader.py:53-70; :55,59,66 | DEFAULT_CONFIG AT:50-68; toggles AT:52, :55, :64; TF_SECONDS AT:48 (PROMPT:36 says :47) |
| Routing | PROMPT:148-149: a config line routes source:fabio-core | needs a code path producing that source (AT:150, :208); config adds only the prefix |
| Source value | PROMPT:122 "fabio-core"; ARCH:47, PROMPT:151 "fabio" | unresolved (item 2) |
| Fabio account | AT:67, FABIO_TESTNET_SLOT.md:5 "fabio"; TESTNET_SUBACCOUNTS.md:9 jishu_1 | ATC:4 jishu_3 (live routing) |
| ARCH default list | ARCH:73 omits consensus | consensus default is from the task |
| RSI TF keys | ARCH:39, :82-83 six | PROMPT:105 seven |
| Fabio evidence | ARCH:73 default on | SPEC:249-267 needs a registered backtest first (D1); SPEC:267 says "as its own layer", ARCH says "core" |

# END
