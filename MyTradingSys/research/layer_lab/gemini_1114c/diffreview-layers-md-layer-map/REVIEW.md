VERDICT: 1 BUG, 8 RISK (60 commits reviewed on origin/fast-track, 2026-11-13..2026-11-14)

Scope: `git log --since='24 hours ago' --format='%h %s' origin/fast-track -- MyTradingSys/system/LAYERS.md MyTradingSys/system/layer_map.json` (OURS count: 60 commits).
Checks on `origin/fast-track` (`90b3c95af`): `make_layers_md.py --check` passes (`LAYERS: pointers ok`) and `LAYERS.md` matches `make_layers_md.render()`, `test_make_layer_map.py` passes (3 passed), and all 50 parsed `report` paths exist; however `json.loads(..., object_pairs_hook=...)` detects 14 duplicate keys in `MyTradingSys/system/layer_map.json:771-806`.

| sha | file:line | finding | severity | one-line fix |
|---|---|---|---|---|
| `9ccec48ec` | `MyTradingSys/system/layer_map.json:771-806` | Fused JSON object: `"id": "MALKAN-R03-R04-DIVERGENCE-20261113"` (`MyTradingSys/system/layer_map.json:772`) and `"id": "RSI-CONFIRM-LAYERS-20261113"` (`MyTradingSys/system/layer_map.json:788`) lack `}, {` after line 787, so `json.loads()` silently drops `MALKAN-R03-R04-DIVERGENCE-20261113` (still broken on `origin/fast-track`) | BUG | Insert `"read": "summary"` and `}, {` between `MyTradingSys/system/layer_map.json:787` and `788` and regenerate `LAYERS.md` |
| `5c00da0ee` | `MyTradingSys/system/LAYERS.md:1` | CLEAN: ship: regenerated LAYERS.md | CLEAN | - |
| `e050e4509` | `MyTradingSys/system/LAYERS.md:14` | Historical merge placed `MALKAN-R03-R04-RSI-DIV-20261114` under Tom instead of RSI in `LAYERS.md` (fixed in `5c00da0ee`) | RISK | Regenerate `LAYERS.md` with `make_layers_md.py` after every merge |
| `fd6e6b086` | `MyTradingSys/system/layer_map.json:3` | `asof: 2026-11-13` left stale when adding `date: 2026-11-14` row `MALKAN-R03-R04-RSI-DIV-20261114` (`MyTradingSys/system/layer_map.json:1741`), contrary to `_doc` (`MyTradingSys/system/layer_map.json:2`) | RISK | Update `asof` at `MyTradingSys/system/layer_map.json:3` to `2026-11-14` |
| `56888a045` | `MyTradingSys/system/LAYERS.md:1` | CLEAN: Revert 'Malkan R03/R04 divergence study: gate fixes (test row, look-ahead allowlist, co... | CLEAN | - |
| `65f254ffd` | `MyTradingSys/system/layer_map.json:771-806` | Merge introduced the fused `MALKAN-R03-R04-DIVERGENCE-20261113` + `RSI-CONFIRM-LAYERS-20261113` JSON object (reverted in `56888a045`, re-introduced in `9ccec48ec`) | RISK | Separate the two objects with `}, {` when resolving `layer_map.json` merge conflicts |
| `813600251` | `MyTradingSys/system/layer_map.json:1` | CLEAN: route tag | CLEAN | - |
| `0e7026e3e` | `MyTradingSys/system/layer_map.json:1` | CLEAN: RSI confirm layers study: gate fixes (context lines, test row, look-ahead allowlist, co... | CLEAN | - |
| `7fd4cf199` | `MyTradingSys/system/LAYERS.md:1` | CLEAN: Merge origin/fast-track into malkan study branch | CLEAN | - |
| `f6e253383` | `MyTradingSys/system/LAYERS.md:1` | CLEAN: Malkan R03/R04 divergence study: gate fixes (test row, look-ahead allowlist, costs.csv,... | CLEAN | - |
| `7a30bfbb7` | `MyTradingSys/system/layer_map.json:820` | `"effects": "none confirmed: 4h<=12 and 8h<=15 VALIDATION leads are UNDERPOWERED (n 16-21) and flat in DEV"` overstates DEV flatness for `4h<=12` (`MyTradingSys/research/rsi_htf_extreme_2026-11-13/RESULT.md:61` notes `DEV 4h<=12 d<30 is also positive (+0.65R at 2R, n 8)`) | RISK | Clarify at `MyTradingSys/system/layer_map.json:820` that `8h<=15` is flat in DEV while `4h<=12` is positive (`n=8..13`) |
| `f9466ee47` | `MyTradingSys/system/LAYERS.md:1` | CLEAN: Raw card: Live Aid published copy lacks Home (build_artifact does not inline home_one.js) | CLEAN | - |
| `254f72f8b` | `MyTradingSys/system/layer_map.json:1` | CLEAN: edge4 RSI 4h/8h/12h <=12 + daily<30 + confirm candle: UNDERPOWERED | CLEAN | - |
| `0b5e71980` | `MyTradingSys/system/layer_map.json:1` | CLEAN: Ship gate runs the CI-only checks (3pc, 3x, 4e, layer_map trials, extra_tests.tsv rows)... | CLEAN | - |
| `6bb1a71cf` | `MyTradingSys/system/LAYERS.md:1` | CLEAN: ship: regenerated LAYERS.md | CLEAN | - |
| `e24a9c65a` | `MyTradingSys/system/layer_map.json:1` | CLEAN: Revert edge-oi-flush ship (trunk CI red: PRE_REG Context lint, Step 3pc) | CLEAN | - |
| `aebbfa5b7` | `MyTradingSys/system/layer_map.json:1` | CLEAN: Restore OI-FLUSH row (merge had fused it into another row) after extreme-confirm-templa... | CLEAN | - |
| `2db525fb7` | `MyTradingSys/system/layer_map.json:768` | Historical revert of `edge-extreme-confirm-template` accidentally deleted `BIGCANDLE-STORY-1H-20261105` from `layer_map.json` and `LAYERS.md` (restored in later merge) | RISK | Verify revert diffs do not drop unrelated `layer_map.json` rows |
| `2aa91f3f5` | `MyTradingSys/system/LAYERS.md:1` | CLEAN: ship: regenerated LAYERS.md | CLEAN | - |
| `137ecaf12` | `MyTradingSys/system/layer_map.json:1661` | Historical merge fused `EXTREME-CONFIRM-1H-20261113` into `OI-FLUSH-XCOIN-20261113` and dropped `trials: 10` to `null` (fixed in `aebbfa5b7`, later reverted in `e24a9c65a`) | RISK | Run duplicate-key JSON check after `layer_map.json` conflict resolution |
| `ee39c2238` | `MyTradingSys/system/LAYERS.md:1` | CLEAN: Merge-fix: layer_map row trials null, read summary for extreme-confirm-template | CLEAN | - |
| `a3f91d55b` | `MyTradingSys/system/layer_map.json:1157` | Historical merge changed `BIGTRADE-EXIT` `trials` from `54` to `null` and `RSI-EXTREME-CONFIRM-1H-20261113` `trials` from `384` to `null` (fixed for `BIGTRADE-EXIT` in `ee39c2238`) | RISK | Preserve existing `trials` values on unrelated rows during merges |
| `607d7a3e2` | `MyTradingSys/system/LAYERS.md:1` | CLEAN: Merge remote-tracking branch 'origin/fast-track' into JIS-NB/edge-rsi-extreme-confirm-1113 | CLEAN | - |
| `38b41953e` | `MyTradingSys/system/LAYERS.md:1` | CLEAN: Merge remote-tracking branch 'origin/fast-track' into claude/reverent-dhawan-c12b16 | CLEAN | - |
| `fec007b2f` | `MyTradingSys/system/layer_map.json:1` | CLEAN: Re-land edge-rsi-extreme-confirm: trials null in layer_map (minBTL test pins 15 recorde... | CLEAN | - |
| `81c172a57` | `MyTradingSys/system/layer_map.json:1` | CLEAN: Revert 'Revert edge-rsi-extreme-confirm ship (trunk CI red: minBTL TRIALS row missing)' | CLEAN | - |
| `982774002` | `MyTradingSys/system/layer_map.json:1` | CLEAN: Revert cf596930a (RSI extreme confirm; breaks test_make_layer_map on trunk) | CLEAN | - |
| `614eaf710` | `MyTradingSys/system/layer_map.json:1` | CLEAN: Revert edge-rsi-extreme-confirm ship (trunk CI red: minBTL TRIALS row missing) | CLEAN | - |
| `3864218a8` | `MyTradingSys/system/LAYERS.md:1` | CLEAN: Merge origin/fast-track into edge-oi-flush-1113 | CLEAN | - |
| `536513109` | `MyTradingSys/system/LAYERS.md:1` | CLEAN: Merge remote-tracking branch 'origin/fast-track' into claude/reverent-dhawan-c12b16 | CLEAN | - |
| `2dba44025` | `MyTradingSys/system/LAYERS.md:114` | Historical commit duplicated `BIGCANDLE-STORY-1H-20261105` in `LAYERS.md` because `layer_map.json` had two copies during intermediate merges (later resolved) | RISK | Ensure `layer_map.json` has unique `id` entries before regenerating `LAYERS.md` |
| `bec5b8b3b` | `MyTradingSys/system/LAYERS.md:1` | CLEAN: Merge origin/fast-track into edge-extreme-confirm-template-1113 | CLEAN | - |
| `7c7d31701` | `MyTradingSys/system/LAYERS.md:1` | CLEAN: Merge origin/fast-track into edge-rsi-extreme-confirm-1113 | CLEAN | - |
| `12c0ef080` | `MyTradingSys/system/LAYERS.md:1` | CLEAN: Merge remote-tracking branch 'origin/fast-track' into JIS-NB/adx-1d-through25-1113-b | CLEAN | - |
| `f31e28ff0` | `MyTradingSys/system/LAYERS.md:1` | CLEAN: Krown S8 RESULT: INCONCLUSIVE does not imply stop (line 23 reworded) | CLEAN | - |
| `715fe70a5` | `MyTradingSys/system/layer_map.json:1` | CLEAN: Extreme-reading + confirm-candle template, 1h, 10 coins: FAIL 0/54 | CLEAN | - |
| `cf596930a` | `MyTradingSys/system/layer_map.json:1` | CLEAN: RSI extreme + confirming candle, 10 coins: FAIL (0/384 cells) | CLEAN | - |
| `33a91b27c` | `MyTradingSys/system/layer_map.json:1` | CLEAN: adx 1d through 25: Rule A FAIL, Rule B UNDERPOWERED; run script, tests, layer-map row | CLEAN | - |
| `f9b81d91e` | `MyTradingSys/system/LAYERS.md:1` | CLEAN: Merge origin/fast-track into edge-oi-flush-1113 | CLEAN | - |
| `a7f353353` | `MyTradingSys/system/layer_map.json:1` | CLEAN: Liquidation-flush reversal, 10 perps: FAIL | CLEAN | - |
| `79fe7e9d2` | `MyTradingSys/system/LAYERS.md:1` | CLEAN: Live Aid Home: flag markers on a bottom rail, chart key, WaveTrend how-to, divergence l... | CLEAN | - |
| `19078a5cf` | `MyTradingSys/system/layer_map.json:1` | CLEAN: Revert live_aid_flags_full ship (fe3436571, 4728a9b57, 24d19b5d3, 77d32e208, ca74fa41d)... | CLEAN | - |
| `d5289b2d2` | `MyTradingSys/system/LAYERS.md:1` | CLEAN: Malkan 12/18 divergence window labelled OURS (label only) | CLEAN | - |
| `ebe60a4d4` | `MyTradingSys/system/LAYERS.md:1` | CLEAN: Merge remote-tracking branch 'origin/fast-track' into JIS-NB/live-aid-flags-full-1113 | CLEAN | - |
| `c38d43ef0` | `MyTradingSys/system/LAYERS.md:1` | CLEAN: Result: raw cards refined (15 ready, 2 dropped, 5 waiting on dep/stamp) Next: END: refi... | CLEAN | - |
| `91b97c4ea` | `MyTradingSys/system/LAYERS.md:1` | CLEAN: Merge remote-tracking branch 'origin/fast-track' into JIS-NB/live-aid-flags-full-1113 | CLEAN | - |
| `140c0c613` | `MyTradingSys/system/LAYERS.md:1` | CLEAN: Merge origin/fast-track (keep both decision entries, keep liq-burst card line) | CLEAN | - |
| `24d19b5d3` | `MyTradingSys/system/LAYERS.md:1` | CLEAN: Live Aid idea-flag groups full-history test: 0 of 30 cells pass, layer_map row | CLEAN | - |
| `0be17fc4a` | `MyTradingSys/system/LAYERS.md:1` | CLEAN: ship: 16 file(s) | CLEAN | - |
| `20b1f52f9` | `MyTradingSys/system/LAYERS.md:1` | CLEAN: Plan prints a RUN line per due routine (routines_due.py): hygiene, learner, scenario sc... | CLEAN | - |
| `3d63e9f46` | `MyTradingSys/system/LAYERS.md:1` | CLEAN: ship: 8 file(s) | CLEAN | - |
| `a9252f832` | `MyTradingSys/system/LAYERS.md:1` | CLEAN: Merge remote-tracking branch 'origin/fast-track' into JIS-NB/stale-cards-refresh-b-1113-2 | CLEAN | - |
| `093681362` | `MyTradingSys/system/LAYERS.md:1` | CLEAN: Result: batch B stale cards handled: 3 closed (board core, board rates, malkan fwd), 5 ... | CLEAN | - |
| `7b41994dd` | `MyTradingSys/system/LAYERS.md:1` | CLEAN: Merge remote-tracking branch 'origin/fast-track' into JIS-NB/layers-md-cryptocred-4h-fa... | CLEAN | - |
| `225b34e69` | `MyTradingSys/system/layer_map.json:1` | CLEAN: Add CryptoCred 4h 10-symbol FAIL row to layer map | CLEAN | - |
| `98ca71600` | `MyTradingSys/system/LAYERS.md:1` | CLEAN: ship: 4 file(s) | CLEAN | - |
| `035dac5e7` | `MyTradingSys/system/LAYERS.md:1` | CLEAN: Merge remote-tracking branch 'origin/fast-track' into claude/reverent-dhawan-c12b16 | CLEAN | - |
| `d05d04a65` | `MyTradingSys/system/LAYERS.md:1` | CLEAN: callers-peer-ledger-provenance-1113: mark unverified analyst ledger rows SAMPLE | CLEAN | - |
| `98d25b491` | `MyTradingSys/system/LAYERS.md:1` | CLEAN: ship: 10 file(s) | CLEAN | - |
| `9c165f83c` | `MyTradingSys/system/LAYERS.md:1` | CLEAN: Refine 9 cards: 2 ready, 7 closed as done on trunk | CLEAN | - |
