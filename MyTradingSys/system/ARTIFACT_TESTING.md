# Artifact testing: how every page we keep is tested

Pages here = the live aid (`tools/live_aid/live_aid.html`, opened from disk), the sim desk (`research/sim_desk`: local app
`page.html` + static `artifact/index.html`), the CBP desks (built in F:/CryptoScrapper, published by the CBP workflow) and the
registry pages (`system/artifacts/registry.json`: home, control room, layers, research map, planner, Tom and Fabio deck).
Design written 2026-10-30 (operator ask) after the analyst-levels "hit" look-ahead reached the live aid unseen: the maths had
tests, the page had none, and nothing checked the date rule. Four layers, each with one question and one place to run.

## The four layers

| Layer | Question | How | Runs |
|---|---|---|---|
| 1 Maths | Does each number on the page equal an independent computation? | Python recomputes from the same bars/rows (never from the page code); JS maths run through node (`test_live_aid.py`). A `*_BREAK=<fn>` switch breaks one function on purpose: its test must fail (fail-first proof) | ship gate + CI |
| 2 Build | Does the builder turn its inputs into the page it should, and refuse bad inputs? | Builder tests on fixtures: every input row shows, bad rows fail the build, DEV window enforced, no raw price / order / account data in the output, SOURCED/OURS label on every parameter, no size/entry/exit wording on observation-only pages | ship gate + CI |
| 3 Open it | Does the page open and stay honest when its feeds are gone? | Headless Chromium, network OFF, every page from disk: no uncaught script error, no NaN / [object Object] / bare undefined cell, the live aid reads NOT_IN_DATA (`scripts/dev/test_artifact_pages.py`) | desktop ship gate (CI skips: no browser) |
| 4 Honesty in time | Could the page know something before it happened? | Every "hit", "fired", "reached" uses an as-of instant that is after the fact that produced it (date-only publish -> next UTC day; bar close, not bar open); a test plants a touch before the instant and asserts it does not count (`test_analyst_levels.py::Hit`) | ship gate + CI, and every audit reads for it |

Rules that hold for all four: a new test fails on the pre-change code once; a page is never opened against the real exchanges
in a test (public data is allowed, determinism is not negotiable); screenshots are not goldens (they break on every font and
width change and tell nothing a text check does not). Published-page drift is its own check: `artifacts.py stale` after each
ship (warning only), `publish-record` once republished.

## Where each artifact stands (2026-10-30)

| Artifact | 1 Maths | 2 Build | 3 Open it | 4 Time | Gap, card |
|---|---|---|---|---|---|
| Live aid | `test_live_aid.py` (RSI, BB, ATR, VWAP, WaveTrend, in-trade, liquidations, funding, news, US open, analysts; `LIVE_AID_BREAK`) | `test_build_analyst_data.py` (roster complete, rejected shown, levels offline) | `test_artifact_pages.py`: opens offline, NOT_IN_DATA, no NaN | `test_analyst_levels.py::Hit` (publish-day bars never count) | Numbers on the rendered page are never checked (layer 3 only sees "no crash"): a replay mode that feeds the page `fixture_klines.json` instead of sockets, then a test reads the tiles and compares with the layer-1 maths. Card `live-aid-replay-mode-fixture-feeds` |
| Sim desk (static page) | `test_reference.py`, `test_desk.py` verdicts | `artifact/test_artifact.py` (every result file becomes a test, DEV window, relative only, bad files fail) + `test_page_top.py` | `test_artifact_pages.py` | n/a (precomputed DEV results) | none open |
| Sim desk (local app) | same | `test_integration_http.py` (endpoints, every study wired, date lock) | not opened in a browser: `page.html` is only syntax-checked in node (HANDOVER_SIMV2.md). Card `sim-desk-page-click-test` | n/a | one card |
| CBP analyst desk / consensus desk | n/a (words, not maths) | F:/CryptoScrapper `tests/test_golden.py`, `test_emit_gates.py`, `tools/test_profile.py` (extraction semantics, gates, profile) | registry copies open (`test_artifact_pages.py`); the analyst desk has no repo copy, so it is never opened or staleness-checked | `cbp_run.py` prompt carries the publish date (`test_cbp_run.py`) | Card `cbp-analyst-desk-repo-copy-and-open-check` |
| Registry pages (home, control room, layers, research map, planner, deck) | n/a | `test_make_*.py` per generator; `test_artifacts.py` (one url per page, banner, every link registered) | `test_artifact_pages.py` | n/a | hand-made DATA lines (research map, planner) have no builder test: accepted, they change by hand in the live page |

## Recipe for a new page or a new panel (what "done" means on the card)

1. Maths in a `.js`/`.py` file beside the page, not inline in the html, so layer 1 can import it; a `*_BREAK` switch for the new function.
2. Builder reads inputs from a path argument (fixtures in tests), writes with `newline='\n'`, refuses a bad row loudly.
3. The page handles every feed and data file being absent: the cell says NOT_IN_DATA or names the command that builds the file.
4. Add the page to `registry.json` (`html` set) or to `EXTRA_PAGES` in `test_artifact_pages.py`; run `python scripts/dev/test_artifact_pages.py`.
5. Any "hit / fired / reached / since" column: write the as-of rule in the file docstring and a planted look-ahead test before the feature.
6. Ship: layers 1, 2, 4 run in CI; layer 3 on the desktop gate. Republish, then `artifacts.py publish-record --slug <slug>`.

## Not done on purpose

- No screenshot goldens, no visual-diff service, no browser farm: one headless Chromium on the desktop is the whole layer 3.
- No test of the claude.ai viewer itself (CSP, pins, sharing): `artifacts.py plan` lists what a login must do; the operator clicks.
- Live aid numbers on the rendered page wait for the replay mode card; until then layer 1 is the number check.
