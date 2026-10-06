# MTS-2026-10-03-1329Z-CLI-BLD-tf3-fabio-v3-live
Surface: CLI (App could not be confirmed to reach repo/child processes from this launch; fallback per SURFACE_POLICY). Model: Sonnet 5.5.

## T0
- BUILD_PIPELINE.md:44 row 1.5 TF3; TOM_FABIO_REVIEW_2026-10-03.md:50 E6 (cause not established).
- v3/signals.py:277-284 volume_tier: <10 prior days -> "99" (never silence). engine.py:75-80 _tier: no prior_vols -> "99"; live_runner_cli make_fabio_v3_layer passes none.
- live_runner_cli.py fabio_v3_flow_window: needs ny_open_utc(day); returns None -> silent. ny_open_utc(2026-10-03) is None (Saturday), 2026-10-02 = 13:30Z.
- Live CSV 2026-10-03: 698 rows 03:01-14:38Z, no gaps, thr_days 26. Offline archive ends 2026-09-28.
## T1-T3
- of_backfill.py + test_of_backfill.py; ran 09-29..10-02: 4 x 1440 rows thr_days 30. Gate step added. 4 tests pass; mutation (ownership guard removed) fails 1.
- Check: fabio_v3_flow_window on 10-02 15:00Z -> 91 bars; engine.run returns IN_TRADE verdict.
## T5 deviations
- 10-03 00:00-03:01Z not backfilled (live writer owns the day; prepending would break its cvd_day). Backfilled CSVs left untracked (runtime data, 2.9 MB), not committed.
- Whether v3 emits alerts on Monday is unverified until 2026-10-05 13:30Z.
