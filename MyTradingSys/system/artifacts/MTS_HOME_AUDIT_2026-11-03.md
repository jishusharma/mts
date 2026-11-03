# MTS Home audit 2026-11-03 (read-only; Auditor)

Framing: MTS Home (`MyTradingSys/system/artifacts/mts_home.html`, built 2026-11-02 11:03 UTC, data blob at line 125) is a launcher,
not a layer page. It has 0 layer cards. Layers live in the page it links, "MTS Layers" (`layers_board.html`, last commit 3dbbb40bc
2026-11-02; `make_home.py` line 142 flags it "behind repo"). So "every layer brought forward" means: rebuild and republish MTS Layers,
plus add one compact layer strip to Home. Generator: `scripts/dev/make_home.py` (350 lines).

## Structure (mts_home.html lines 91-169)
| # | Section | Shows | Date/commit quoted |
|---|---|---|---|
| 1 | header (L91) | title + Built stamp | DATA.generated 2026-11-02 11:03 UTC |
| 2 | Waiting for you (L95) | 4 items from OPERATOR_DECISIONS.md + task cards | 2026-10-21, 11-01, 11-02, 10-24 |
| 3 | Road to profitability (L99) | stages S0..S5 from D7_ROADMAP.md | "Now: S0", S0 expect "now to 2026-10-27" |
| 4 | Pages (L104) | 6 tiles from registry.json | pub 10-31 x4, 11-01, 10-31 |
| 5 | Start a session (L109) | 7 recipes + super-session prompt fold | SUPER_SESSION.md |
| 6 | A link fails (L113) | share instructions | static |
| 7 | Old copies to delete (L119) | 14 retired URLs | registry.json |
| 8 | footer (L122) | how registry feeds the page | static |

## A) STALE (5)
| # | Home says | Truth now | File:line |
|---|---|---|---|
| A1 | Sim Desk tile pub 2026-11-01 | registry last_published 2026-11-03 (commits 06624e11d, 5f6c86009: per-trade candle chart, replay) | `MyTradingSys/system/artifacts/registry.json` page sim_desk |
| A2 | Waiting: "27 grandfathered sources review_by 2026-10-23" | 11 days overdue; take the recommended default (extend 14 days), record, drop from strip | `MyTradingSys/system/OPERATOR_DECISIONS.md:1261` |
| A3 | Waiting: 11-01 "start DSA", 11-02 "Console credit" | standing instructions already given ("may be used without asking"), not open questions; they inflate the count | `OPERATOR_DECISIONS.md:1620`, `:1623` |
| A4 | Road: S0 expect "to 2026-10-27", S1 "10-27..10-29", Now S0 | today 11-03; windows past, no stage marked signed, dates or Now line are wrong | `MyTradingSys/research/v1_plan_2026-10-20/D7_ROADMAP.md:13-14` |
| A5 | MTS Layers tile (pub 2026-10-31) | layer_map.json changed 2026-11-03; board built 11-02; STATUS lists mts_layer_map, mts_home, research_map, tom_fabio_deck STALE (STATUS itself generated 10-30, rerun it) | `MyTradingSys/research/STATUS.md:8-14` |

## B) DUPLICATES (3)
| # | Duplicate | Keep |
|---|---|---|
| B1 | Tiles "Tom and Fabio: what they taught" and "Tom and Fabio Setup Review": same subject, both manual, both pub 10-31 | Keep Setup Review as the tile; add the deck as a second link in it (registry rows tom_fabio_deck + tom_fabio_setup_review) |
| B2 | "Old copies to delete" (L119) lists pages registry already marks `retire` (mts_control_room, session_planner, btc_live_aid, CBP desks) while the strip and Road restate Control Room content | Keep the strip (cap 3); reduce Old copies to a one-line count |
| B3 | Recipe "Spend spare budget" and the Super-session prompt fold (L112) are one action twice | Keep the fold, drop the recipe row |

## C) MISSING (9)
| # | Missing | Truth lives in |
|---|---|---|
| C1 | All 14 layer families have no card: tom, fabio, guidance, rsi, cryptocred, positioning, session_timing, volume_candles_ma, live_engine, callers, krown, wavetrend, pitchfork, pizzino | `MyTradingSys/system/LAYERS.md:10,42,72,83,105,120,136,156,187,205,217,236,248,269` |
| C2 | Per-family one-line verdict (Tom core STOP; Fabio v3 OOS FAIL; TOM-VP-RETURN 57.2% vs 70% not reproduced, 10-31) | LAYERS.md "Status:" and newest Backtests line per family (e.g. L11-20, L43-47) |
| C3 | Layer reviews: rsi/cc/pitchfork/engine, positioning/volume/callers, tom/guidance, tom_fabio_review 10-31, layer_review 10-26 | `MyTradingSys/research/layer_lab/reports/layer_review_*.md` (3), `MyTradingSys/research/tom_fabio_review_2026-10-31/`, `MyTradingSys/research/layer_review_2026-10-26/` |
| C4 | Eagle_Eyes since 10-29: candidates c21 BB pierce, c23 daily shorts, c24 OI-after-flush, c25 stochrsi, c26 ride/magnet/fade, c30 WT+RSI divergence validation; session map and US plan 10-30 | `MyTradingSys/research/eagle_eyes_picture_2026-10-28/` (BACKTEST_CANDIDATES.md, C30_VALIDATION.md, SESSION_MAP_2026-10-30.md, US_SESSION_PLAN_2026-10-30.md) |
| C5 | Sim results not linked from Home: 338 files in results/, catalogue 4903 lines (eagle-c21..c30, dir-pitchfork, dir-tom_correlation_trick, dir-jala_layer, dir-cowen_q4, dir-testnet_cotrade) | `MyTradingSys/research/sim_desk/results/_catalogue.json` |
| C6 | Newer layer work: jala_layer, liquidation_layer, pizzino_layer, flow_layers_concepts | `MyTradingSys/research/jala_layer_2026-10-31/`, `liquidation_layer_2026-10-28/`, `pizzino_layer_2026-10-27/`, `flow_layers_concepts_2026-10-28/`; jala and liquidation are not in the family list at LAYERS.md:8 |
| C7 | Sim Desk requirements 11-02 | `MyTradingSys/research/sim_desk/REQUIREMENTS_2026-11-02.md` |
| C8 | BTC Live Aid: README says live set, registry says `retire`, Home shows nothing | `MyTradingSys/system/artifacts/README.md:59` vs `registry.json` btc_live_aid |
| C9 | Health line (CI green, GO-PRIVATE trigger B carry_basis 10-18) | `MyTradingSys/research/STATUS.md:4-5` |

## D) USELESS (4)
| # | Item | Why cut |
|---|---|---|
| D1 | "A link fails, or you use another login" fold (L113) | static prose, no number or decision; one sentence in footer |
| D2 | Pages sub-line "Blue edge: you write there..." (L105) | explains one tile (research_map); move into that tile |
| D3 | Old copies to delete, 14 URL rows (L119) | operator housekeeping, no decision value on the front page; keep a count |
| D4 | Footer "For Claude sessions" (L122) | written for sessions, not the operator; belongs in artifacts/README.md |

## E) Rebuild recipe
1. Edit `scripts/dev/make_home.py`: add `layers()` reading `MyTradingSys/system/layer_index.json` + `layer_map.json` (newest backtest per family); add a Layers section to the template (L91-122) before Pages; add `eagle()` (newest rows of BACKTEST_CANDIDATES.md) and `simdesk()` (counts from `_catalogue.json`).
2. In `build()` (L126): drop standing-decision items from `waiting()` (L80), cap strip at 3; delete D1-D4 and B1-B3 from the template.
3. Fix dates/Now line in `MyTradingSys/research/v1_plan_2026-10-20/D7_ROADMAP.md:14`.
4. Rebuild the board first: `python scripts/dev/make_layers_board.py` then `python scripts/dev/make_layers_md.py`.
5. `python scripts/dev/make_home.py` then `python scripts/dev/test_artifacts.py`.
6. `python scripts/dev/sync.py ship`; Artifact-publish Home and MTS Layers over their registry urls (owner jishusharma1985), update last_published in registry.json.

Noticed: STATUS.md (generated 2026-10-30 18:51) is 4 days old; still says CI green 52ec65dd8 and lists 6 stale pages.
Noticed: `layer_map.html` and `layers_board.html` both exist in artifacts/; registry points only at layers_board.html, so layer_map.html looks orphaned.
Noticed: `cr_moved.html` sits in artifacts/ but has no registry row.
Noticed: item A2 (review_by 2026-10-23) has been open 11 days with a recommended default nobody applied.
