RESULT 2026-11-09 Live Aid Map tab (card live-aid-bias-map-one-screen-1109); the screenshots use the test fixture (daily_playbook test bars), not live numbers.
1. Map = dial LONG / SHORT / HOLD (6 section verdicts, 4 of 6 style count) + ladder (3 zones each side, 0.15 % merge) + session strip + 3 scenario cards; 51 visible words (budget 60).
2. map_1920x1040.png: page height 1040 = viewport, content ends at y 494; map_400x860.png: height 860 = viewport, content ends at y 540; phone_400x860.png (phone page, 49 words) the same, no scroll either way.
3. Levels: level_registry.js feeds the ladder from playbook levels, analyst calls, Levels panel and MA strip; two sources within 0.15 % are one zone with merged badges (PDC + analyst "CO" in the test).
4. The 11-level text line and the analyst list are gone from the page; the old text cards sit behind a closed Detail line; the next event shows once as a countdown chip.
5. Tests: test_live_aid_map.py 22 tests, red on the pre-change tree (22 failed), green now; test_live_aid, test_daily_playbook, layout and replay tests still pass.
