# Mutation-kill audit: scripts/dev/analyst_levels.py vs test_analyst_levels.py

Method: 11 scratch mutations applied in place, 9 original tests run, file restored (analyst_levels.py git diff empty).
Expected values in new tests are hand-derived from the module docstring (band 40k..200k inclusive, one level per video, hit = traded through, --offline = no network).

| # | Mutation | Original 9 tests | After (14 tests) |
|---|---|---|---|
| M1 | publish-day bar counted (+0 days) | KILLED | KILLED |
| M2a | LO edge exclusive (40,000 dropped) | SURVIVED | KILLED test_band_edges_inclusive |
| M2b | HI edge exclusive (200,000 dropped) | SURVIVED | KILLED test_band_edges_inclusive |
| M2c | LO moved to 30k | SURVIVED | KILLED test_band_edges_inclusive |
| M3 | sort ascending | KILLED | KILLED |
| M4 | --offline ignored (network call made) | SURVIVED | KILLED test_main_offline_makes_no_network_call |
| M5 | HIT/open flag swapped in render | SURVIVED | KILLED test_render_hit_vs_open_tag |
| M6a | ladder drops every level (dedupe always-on) | KILLED | KILLED |
| M6b | ladder dedupes same level across videos | SURVIVED | KILLED test_same_level_two_videos_both_kept |
| M6c | parse_levels dedupe removed | KILLED | KILLED |
| M7 | hit bar-extreme touch exclusive (< instead of <=) | SURVIVED | KILLED test_hit_touch_on_bar_extreme_counts |

Result: 11 mutations, 7 survived the original suite, 0 survive the new suite (5 new tests). Not covered (out of the 6 asked): hook_block band filter, `expired` flag, `--days` cutoff.
