# Sim-desk UX/display review — per-ship verification (2026-10-26)

Trunk-checked review of the 5 sim-desk UX/display commits from the stand-up brief
(`research/sim_standing_2026-10-26.md`, bfe807df8). Every claim below was re-verified
against current trunk code + its tests, not against the commit message. All 5 hold.

Trunk at review: `origin/fast-track` (HEAD `d280b584b`). Research-only: no test gate
runs on this file's ship.

| commit | claim | verdict | proof (file:line) | note |
|---|---|---|---|---|
| `80d63bacd` | `python desk.py` picks a free port, opens the browser, prints the URL; test_launcher.py covers it | **HOLDS** | desk.py:524–538 (`start_server` tries `port..port+30`, falls back to port 0); :537 `webbrowser.open(url)`; :553 `print(f'Simulator desk on {url}…')` | test_launcher.py: 8 tests (3 launcher/first-page + 5 runs-table) all pass. Free-port logic and busy-port-forward covered (test_launcher.py:32). |
| `271ef8fc6` → `e0a985ca2` | smoke-revert cycle left that failure mode fixed: smoke result file gone from the catalogue path, or the catalogue test now handles desk-* rows, and CI green for it | **HOLDS** | trunk `results/` has NO `desk-wavetrend-4fe72b9f.json`; the smoke `TRIALS.md` ledger row is absent on trunk | The failure was "an uncatalogued / collect-hostile desk-* result file breaks `test_artifact.py`". It's fixed two ways and both are in current code: (1) the smoke file + ledger row were reverted out; (2) `build_catalogue.py:164–168` (section 7) now adds a row per `desk-*.json` so a saved run is always collect-safe and catalogued. `test_artifact.py` runs 8/8 green locally. Replacement `desk-krown-634f1a37.json` is present, collect-safe, and carries a catalogue row (`_catalogue.json` result_id `desk-krown-634f1a37`). |
| `67426492d` | breakdown table (year / side / 4h-UTC-hour cells, "too few trades" under 30), every saved desk run gets a build_catalogue row | **HOLDS** | desk.py:134 `MIN_BUCKET = 30`; desk.py:137–160 `breakdown()` (year via `datetime64[Y]`, 4h bucket `(t//3.6e6)%24//4`, `few = n < MIN_BUCKET`); page.html:95–97 (`#bd`, `#chartbox`, `#ledgerbox` folds); page.html:358 `"too few trades"` label; desk.py `export_result → refresh_catalogue()`; build_catalogue.py:164–168 | test_build2.py: 5 tests pass — `test_breakdown_by_hand` (expected cells worked by hand: year 2022/2023, long/short, 00-04/04-08/20-24 UTC), `test_breakdown_marks_few_only_under_30`, `test_saved_run_is_in_the_catalogue` (a saved run's result file is in the rebuilt catalogue). |
| `119aea4ec` | MTS Home: compact page, dedupe, wire Sim Desk and CBP Analyst Desk; links resolve, no stale dedupe leftovers | **HOLDS** | registry.json adds `sim_desk` (url `…/KaPy7f5BKFsvmqin84DpyF`) + `cbp_analyst_desk` (url `…/EsvscEYpcnzjQ231AzcDZC`); test_artifacts.py:179–193 (`test_home_has_session_recipes_without_duplicates`, `test_new_pages_are_wired_into_home`); test_artifacts.py:166–177 (compact page, folded boxes, `len(html)<30000`, dup "where to answer" box gone) | `test_artifacts.py` runs 22/22 green locally. Sim Desk + CBP Analyst Desk both in MTS Home page list; session recipes have no duplicate lines; the two unlisted pages are now registered. |
| `578cf27cb` | tasks: sim-dashboard-v1 done; rebuilt sim_desk artifact and LAYERS.md; published-artifact rebuild matches the current page; LAYERS.md consistent | **HOLDS** | `system/tasks/sim-dashboard-v1.json` `state: done`, `closed: 2026-10-26T16:24:50Z`; LAYERS.md no longer lists the `sim-dashboard-v1` open card; `research/sim_desk/artifact/index.html` rebuilt | Rebuild is byte-identical to the committed `index.html` (`build_artifact.py --out` → 131 646 B, diff empty), and the krown result is present in it (krown landed before the rebuild). LAYERS.md open-cards list and the done task card agree. |

## CI / green status

| area | suite | result |
|---|---|---|
| launcher (c1) | `sim_desk/test_launcher.py` | 8 passed |
| catalogue/artifact (c2) | `sim_desk/artifact/test_artifact.py` | 8 passed |
| breakdown + catalogue-safe save (c3) | `sim_desk/test_build2.py` | 5 passed |
| MTS Home (c4) | `scripts/dev/test_artifacts.py` | 22 passed |

## Non-defects worth noting (not downgrades)

- **6 STALE published pages** flagged in `STATUS.md` 2026-10-26 (`mts_control_room`, `mts_layer_map`,
  `tom_fabio_deck`, `mts_home`, `research_map`, `session_planner`): current `make_status.get_stale_pages()`
  still reports exactly these 6 (published copies lag the repo build). This is the normal post-rebuild
  "not yet republished" state, tracked separately — it is not a defect of the 5 sim-desk UX commits and
  does not affect the verdicts above.
- **test-run environment**: `test_launcher.py` and `test_build2.py` use pytest's `tmp_path`; on this
  host the default pytest temp root is unwritable, so run with `--basetemp=<worktree>/.tmp_pytest`.
  Code is fine; this is only a local test-runner quirk, not a trunk defect.

**Summary: 5/5 HOLDS.** The sim-desk UX/display work shipped on trunk is consistent with its claims
in current code and tests.
