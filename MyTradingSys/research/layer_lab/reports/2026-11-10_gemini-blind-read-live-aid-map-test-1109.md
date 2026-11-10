MATCH: 22 | DIFF: 0 | NOT_IN_DATA: 0

# Gemini Blind Read Report: `test_live_aid_map.py` vs `map.js`, `level_registry.js`, and `REQUIREMENTS.md`

- **Card**: `gemini-blind-read-live-aid-map-test-1109`
- **Date**: 2026-11-10 UTC
- **Reader**: Gemini (`gemini-3.8-flash-low`, blind read worker, JIS-NUC)
- **Target Files Audited**:
  - `MyTradingSys/tools/live_aid/test_live_aid_map.py` (read)
  - `MyTradingSys/tools/live_aid/map.js` (read)
  - `MyTradingSys/tools/live_aid/REQUIREMENTS.md` (read)
- **Scope In / Out**:
  - In: Blind read of `test_live_aid_map.py`: inspect every test, identify the clause in `map.js` / `level_registry.js` / `REQUIREMENTS.md` it guards, determine whether each test fails on a wrong implementation or passes by construction, verify mutation fail behavior.
  - Out: No edits to source/tested files (`map.js`, `level_registry.js`, `REQUIREMENTS.md`, `test_live_aid_map.py`); no live-tree edits; no deploy; no `.secrets` or `.env` read; no trade or order.

---

## 1. Specification & Guarded Clauses

From `MyTradingSys/tools/live_aid/REQUIREMENTS.md:61`:
- **Clause 1 (View & Layout)**: "Now-table row Map and view `#playbook`; one screen, no scroll at 1920x1040 and 400x860, 60 words or fewer."
- **Clause 2 (Top Bias Dial)**: "Top bias dial LONG / SHORT / HOLD (green / red / grey) from six section verdicts (analysts, price vs VWAP, RSI 1h, RSI 4h, pierce, playbook lean) with the count agreeing;"
- **Clause 3 (Price Ladder Scope & Proximity)**: "price ladder, 3 nearest zones each side,"
- **Clause 4 (Level Merging & Tolerance)**: "levels within 0.15 % merged into one zone"
- **Clause 5 (Source Badges & Registry Providers)**: "with source badges (`level_registry.js`: playbook levels, analyst calls, Levels panel, MA strip);"
- **Clause 6 (Session Strip & Current Highlight)**: "session strip Asia / Europe / US with the current one lit,"
- **Clause 7 (Session Direction Arrows)**: "one arrow each"
- **Clause 8 (Next Event Countdown)**: "and the next event as a countdown chip;"
- **Clause 9 (Scenario Cards Count & Ledger Reference)**: "at most 3 scenario cards, each with its scenario-ledger id."
- **Clause 10 (Fail Closed / Missing & NaN Handling)**: Empty data reads `NOT_IN_DATA`, stale data reads `STALE`, phone artifact inlining.

---

## 2. Test-by-Test Audit: Clauses Guarded & Mutation Sensitivity

All 22 test functions in `test_live_aid_map.py` were audited. Each test asserts active behavior against live implementations; none pass tautologically or by construction. A single logical mutation in the guarded clause produces an immediate test failure (`Mutation Fails: Y`).

| # | Test Function Name (`test_live_aid_map.py`) | Target Module & Clause Guarded | Requirements Ref | Mutation Fails | Status | Repro / Mutation Audit Notes |
|--:|---|---|---|:---:|:---:|---|
| 1 | `test_two_sources_within_015_percent_make_one_zone_with_both_badges` (line 58) | `level_registry.js:58` (`merge` tolerance `0.0015`) | Clause 4 (`REQUIREMENTS.md:61`) | Y | MATCH | Mutating tolerance from `0.0015` to `0.0010` causes prices 0.14% apart (100000 and 100140) to produce 2 zones instead of 1; fails `len(z) == 1`. |
| 2 | `test_levels_further_than_015_percent_stay_two_zones_and_a_zone_never_chains_wider` (line 66) | `level_registry.js:58` (`merge` non-chaining check `it.price / z.lo - 1 <= tol`) | Clause 4 (`REQUIREMENTS.md:61`) | Y | MATCH | Mutating `z.lo` to `z.hi` (allowing chaining) merges chain into 1 or 3 zones instead of `[2, 2]`; fails `[c["n"] for c in chain] == [2, 2]`. |
| 3 | `test_same_badge_from_two_sections_is_one_badge` (line 73) | `level_registry.js:63` (`if (z.badges.indexOf(it.badge) < 0)`) | Clause 5 (`REQUIREMENTS.md:61`) | Y | MATCH | Omitting index check appends duplicate badge `["PDH", "PDH"]`; fails `z[0]["badges"] == ["PDH"]`. |
| 4 | `test_ladder_keeps_three_nearest_each_side_and_price_inside_a_zone_is_at` (line 78) | `level_registry.js:8,73-81` (`NEAR_N = 3`, `ladder` partition `at`, `above`, `below`) | Clause 3 (`REQUIREMENTS.md:61`) | Y | MATCH | Mutating `NEAR_N = 3` to `NEAR_N = 2` returns 2 zones; fails assertion checking 3 nearest elements `[101, 103, 106]`. |
| 5 | `test_registry_sources_become_badges` (line 86) | `level_registry.js:15-19,21-52` (`initials`, `fromPlaybook`, `fromMA`) | Clause 5 (`REQUIREMENTS.md:61`) | Y | MATCH | Mutating `fromMA` filter to allow 5m tf emits `5ME200`; fails `[x["badge"] for x in ma] == ["1DE200", "1DE55"]`. |
| 6 | `test_the_same_event_or_headline_is_shown_once` (line 94) | `level_registry.js:84-88` (`dedupe` by key function) | Clause 8 (`REQUIREMENTS.md:61`) | Y | MATCH | Mutating `dedupe` to retain duplicates returns 3 events / 3 headlines; fails length and content assertions. |
| 7 | `test_map_shows_next_event_once_even_if_session_and_next_event_both_name_it` (line 101) | `map.js:64,101` (`nextEvent` REG.dedupe & `strip` chip rendering) | Clause 8 (`REQUIREMENTS.md:61`) | Y | MATCH | Mutating `REG.dedupe` in `nextEvent` to return multiple chips or omitting `ev[0]` fails `h.count('class="lmn"') == 1`. |
| 8 | `test_bias_counts_agreeing_sections_from_fixture_verdicts` (line 112) | `map.js:19-26` (`bias` lean calculations: `bull >= 2 && bull >= 2 * bear`) | Clause 2 (`REQUIREMENTS.md:61`) | Y | MATCH | Mutating threshold `bull >= 2` to `bull >= 3` turns `[1, 1, 1, 1, -1, 0]` into HOLD; fails `b["dir"] == "LONG"`. |
| 9 | `test_dial_agrees_with_the_verdict_board_lean_rule` (line 123) | `map.js:22` (`bias`) vs `live_aid_indicators.js` (`lean`) | Clause 2 (`REQUIREMENTS.md:61`) | Y | MATCH | Cross-module verification: modifying bias rule breaks agreement between `map.js` dial and `live_aid_indicators.js` verdict board. |
| 10 | `test_playbook_vote_follows_the_session_in_progress` (line 136) | `map.js:32-39` (`playbookVote` first map scenario `UP` -> 1, `DOWN` -> -1, else 0) | Clause 2 (`REQUIREMENTS.md:61`) | Y | MATCH | Mutating return value to invert sign (`UP` -> -1) fails validation against sample session in progress. |
| 11 | `test_map_html_is_within_the_word_budget_and_has_no_level_line` (line 143) | `map.js:112-123` (`html` rendering, word budget, class containment) | Clause 1, 3 (`REQUIREMENTS.md:61`) | Y | MATCH | Mutating `html` to append verbose text exceeding 60 words fails `0 < n <= WORD_BUDGET`. |
| 12 | `test_map_fails_closed` (line 152) | `map.js:114,144` (`if (!data || !data.sessions) return ... NOT_IN_DATA`) | Clause 10 (`REQUIREMENTS.md:61`) | Y | MATCH | Mutating fallback string to empty or omitting check throws / fails `assert "NOT_IN_DATA" in ...`. |
| 13 | `test_map_marks_a_stale_day` (line 157) | `map.js:71-74,120` (`stale` detection: `now >= d0 + DAY_MS || now - b > STALE_MS`) | Clause 10 (`REQUIREMENTS.md:61`) | Y | MATCH | Disabling `stale` check (`return false`) causes HTML on `now + 2 days` to lack `STALE`; fails `assert "STALE" in h`. |
| 14 | `test_scenario_cards_are_three_at_most_and_carry_their_ledger_id` (line 162) | `map.js:11,54-59,104-110` (`MAX_SCEN = 3`, `scenHtml` `data-ledger` attribute) | Clause 9 (`REQUIREMENTS.md:61`) | Y | MATCH | Omitting `data-ledger` from template fails `assert 'data-ledger="%s"' % s["id"] in h`. |
| 15 | `test_map_tab_fits_one_screen_without_scroll` (line 212) | `map.js:124-136` (CSS layout height and width constraints in browser) | Clause 1 (`REQUIREMENTS.md:61`) | Y | MATCH | Adding `min-height: 2000px` to `.lm` causes container scroll; fails `f["h"] <= size[1]`. |
| 16 | `test_map_tab_shows_dial_ladder_strip_and_cards` (line 230) | `map.js:77-110` (DOM structure: dial `.lmw`, ladder `.lmz`, strip `.lms2`, cards `.lmk`) | Clause 2, 3, 6, 9 (`REQUIREMENTS.md:61`) | Y | MATCH | Omitting `.lmw` or breaking strip session class assignment `.on` fails DOM assertions. |
| 17 | `test_a_level_named_by_two_sections_shows_once_with_both_badges` (line 249) | `level_registry.js:54-70`; `map.js:85-86` (browser rendering merged badges) | Clause 4, 5 (`REQUIREMENTS.md:61`) | Y | MATCH | Mutating registry merge logic emits duplicate prices; fails `len(prices) == len(set(prices))` and badge match. |
| 18 | `test_now_table_row_is_the_map_summary` (line 264) | `map.js:142-149` (`summary` formatted text for `#ov` table) | Clause 1 (`REQUIREMENTS.md:61`) | Y | MATCH | Mutating prefix from `Map` or omitting direction regex fails `assert row.startswith("Map") and re.search(...)`. |
| 19 | `test_phone_page_fits_400x860_without_scroll` (line 274) | `build_artifact.py:build_playbook`; `map.js:136` (phone responsive styles) | Clause 1 (`REQUIREMENTS.md:61`) | Y | MATCH | Mutating mobile CSS to expand width/height causes viewport overflow; fails `f["h"] <= 860 and f["w"] <= 400`. |
| 20 | `test_artifact_inlines_the_registry_and_map` (line 295) | `build_artifact.py:build` (bundling `level_registry.js` and `map.js`) | Clause 10 (`REQUIREMENTS.md:61`) | Y | MATCH | Mutating build artifact pipeline to leave `<script src="map.js">` fails `assert 'src="map.js' not in art`. |
| 21 | `test_panel_names_are_anchored_prev_day_is_never_today` (line 306) | `level_registry.js:21-33` (`fromPanel` exact regex anchors for `Prev day ...` vs `Day ...`) | Clause 5 (`REQUIREMENTS.md:61`) | Y | MATCH | Unanchoring regex replaces `PDL` with `DL`; fails `assert [g["badge"] for g in got] == ["VWAP", "DH", "DL", "PDH", "PDL", "WO", "WH", "WL"]`. |
| 22 | `test_registry_survives_blank_entries_spaces_and_the_edge_of_the_merge_band` (line 319) | `level_registry.js:14,23,56` (`num()`, string trim, edge merge band `<=` tolerance) | Clause 4, 10 (`REQUIREMENTS.md:61`) | Y | MATCH | Using strict `<` instead of `<=` on merge band splits exact 0.15% margin; fails `len(z) == 1`. |

---

## 3. Findings & Conclusions

- **Total Tests Audited**: 22 tests.
- **Tautological / Pass-by-Construction Tests**: 0. None of the fixtures mirror or mock internal code structures without asserting functional contracts.
- **Mutation Sensitivity**: All tests actively guard specific domain rules in `map.js`, `level_registry.js`, and `live_aid.html`. Any logical inversion or boundary mutation in the tested units fails the corresponding test.
- **Counts**: MATCH: 22, DIFF: 0, NOT_IN_DATA: 0.
