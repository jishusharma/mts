0 BUG, 5 RISK (332 commits in 24h on origin/fast-track under MyTradingSys/research: 135 merges, 143 non-Python data/docs, 54 Python-touching commits reviewed)

| sha | file:line | finding | severity | one-line fix |
|---|---|---|---|---|
| `74158f885` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `94ce17ca5` | — | Non-Python only (data/docs). | CLEAN | — |
| `741ed1840` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `c0632d2f1` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `18b972a4c` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `39e1bbf75` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `8f8d1793f` | `MyTradingSys/research/layer_lab/gemini_1114b/testgap-lease/test_lease.py` | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `e7be38cb1` | — | Non-Python only (data/docs). | CLEAN | — |
| `eb0569f0b` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `ee5fe2939` | — | Non-Python only (data/docs). | CLEAN | — |
| `3afd2219d` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `c19f40904` | — | Non-Python only (data/docs). | CLEAN | — |
| `410d2c123` | — | Non-Python only (data/docs). | CLEAN | — |
| `914238b12` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `2a573795b` | — | Non-Python only (data/docs). | CLEAN | — |
| `a45196385` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `7299cdfe5` | — | Non-Python only (data/docs). | CLEAN | — |
| `40c90065c` | `MyTradingSys/research/buyzone_test1_ladder_2026-11-14/fetch_spot.py` (+3 `.py`) | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `c9dde32f7` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `7a23a226f` | — | Non-Python only (data/docs). | CLEAN | — |
| `d8218bc75` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `9402b8e75` | — | Non-Python only (data/docs). | CLEAN | — |
| `47d29eefc` | — | Non-Python only (data/docs). | CLEAN | — |
| `0cbbb8f70` | — | Non-Python only (data/docs). | CLEAN | — |
| `9c20dfd61` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `742d2acaf` | — | Non-Python only (data/docs). | CLEAN | — |
| `7db62ce4d` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `05adda114` | — | Non-Python only (data/docs). | CLEAN | — |
| `27efe64f8` | — | Non-Python only (data/docs). | CLEAN | — |
| `7a5d5d8a9` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `4b6cec251` | — | Non-Python only (data/docs). | CLEAN | — |
| `f7cd3f0af` | — | Non-Python only (data/docs). | CLEAN | — |
| `6f919ea67` | — | Non-Python only (data/docs). | CLEAN | — |
| `864f58c77` | — | Non-Python only (data/docs). | CLEAN | — |
| `8dc663939` | — | Non-Python only (data/docs). | CLEAN | — |
| `ae47fa07b` | — | Non-Python only (data/docs). | CLEAN | — |
| `c1a3c1ac3` | `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/run_1113.py` | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `e050e4509` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `fd6e6b086` | `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/run_1113.py:243-246` | `btc_regime()` iterates `load('BTC', '1h')` without checking for `None` when `BTC_60.json` is absent, raising `TypeError`. | RISK | Guard `bars = load('BTC', '1h') or []` before iterating. |
| `d19713fb9` | `MyTradingSys/research/malkan_divergence_r03_r04_2026-11-13/fetch.py` | Revert of `405d08d41` (`malkan_divergence_r03_r04_2026-11-13/fetch.py`). | CLEAN | — |
| `856d0f204` | `MyTradingSys/research/malkan_divergence_r03_r04_2026-11-13/mal_div_lib.py` | Revert of `b9d39f5e0` (`malkan_divergence_r03_r04_2026-11-13` study). | CLEAN | — |
| `56888a045` | — | Non-Python only (data/docs). | CLEAN | — |
| `dc80419ec` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `f45ffc7e2` | — | Non-Python only (data/docs). | CLEAN | — |
| `4d663f137` | `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/test_run_1113.py` | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `94d3cf36c` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `56bc6562c` | `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/run_1113.py` | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `5b21ebe34` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `087817015` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `3d5d9f31e` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `dc72f3552` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `6fd99b40d` | — | Non-Python only (data/docs). | CLEAN | — |
| `65f254ffd` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `de15069f8` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `cc1d39415` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `dcd758573` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `4055928ea` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `e62ae14ef` | — | Non-Python only (data/docs). | CLEAN | — |
| `e1ac6fa26` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `2770d3d44` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `3e4981cd0` | `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/run_1113.py` | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `e52f8db06` | — | Non-Python only (data/docs). | CLEAN | — |
| `22a0504e4` | `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/run_1113.py` (+1 `.py`) | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `c490f42d6` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `4d24c420f` | — | Non-Python only (data/docs). | CLEAN | — |
| `02252cc11` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `62da40eba` | — | Non-Python only (data/docs). | CLEAN | — |
| `199ef429d` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `1fe5d7ec2` | — | Non-Python only (data/docs). | CLEAN | — |
| `f03ee959b` | — | Non-Python only (data/docs). | CLEAN | — |
| `13ca79f37` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `f5a53f90c` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `0e7026e3e` | — | Non-Python only (data/docs). | CLEAN | — |
| `36e1114e3` | — | Non-Python only (data/docs). | CLEAN | — |
| `8badc7d43` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `41196b0da` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `7fd4cf199` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `b8994c51d` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `f6e253383` | — | Non-Python only (data/docs). | CLEAN | — |
| `8916b1c95` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `d91eac636` | — | Non-Python only (data/docs). | CLEAN | — |
| `6071ca3f0` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `b5f7decb6` | — | Non-Python only (data/docs). | CLEAN | — |
| `48fba98ce` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `b20969721` | — | Non-Python only (data/docs). | CLEAN | — |
| `53f48ea5d` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `e929c71ec` | — | Non-Python only (data/docs). | CLEAN | — |
| `bc0d87ca8` | — | Non-Python only (data/docs). | CLEAN | — |
| `09c4d57af` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `c99c6e99f` | — | Non-Python only (data/docs). | CLEAN | — |
| `06a042e63` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `df8d12506` | — | Non-Python only (data/docs). | CLEAN | — |
| `beb966c7c` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `7a30bfbb7` | — | Non-Python only (data/docs). | CLEAN | — |
| `40d254610` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `6633e01f5` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `fe9af0a03` | — | Non-Python only (data/docs). | CLEAN | — |
| `c49c51776` | — | Non-Python only (data/docs). | CLEAN | — |
| `4f2a9d1b2` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `2984fffa0` | — | Non-Python only (data/docs). | CLEAN | — |
| `71bb56402` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `2c0e961db` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `735186644` | — | Non-Python only (data/docs). | CLEAN | — |
| `3c43fc9f6` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `00abfd8ec` | — | Non-Python only (data/docs). | CLEAN | — |
| `419c3d1c2` | `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/fetch_klines.py` | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `01d71f0cc` | `MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/fetch_klines.py` | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `b069e1857` | `MyTradingSys/research/edge4_malkan_r03_r04_2026-11-13/fetch_klines.py` (+1 `.py`) | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `6139883cd` | `MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/test_fetch_klines.py` | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `641182c35` | — | Non-Python only (data/docs). | CLEAN | — |
| `f0a6e57f8` | — | Non-Python only (data/docs). | CLEAN | — |
| `77d64acac` | — | Non-Python only (data/docs). | CLEAN | — |
| `68943edf3` | — | Non-Python only (data/docs). | CLEAN | — |
| `1ce216d8c` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `5fec8d062` | — | Non-Python only (data/docs). | CLEAN | — |
| `bec3bd4d3` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `66793e2a1` | `MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/run_1113.py` | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `19881058d` | — | Non-Python only (data/docs). | CLEAN | — |
| `c08e4c70f` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `254f72f8b` | `MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/run_1113.py:239-241` | `regime_share()` slices `load('BTC', 'D')[:-1]` without checking for `None` when `BTC_D.json` is absent, raising `TypeError`. | RISK | Guard `dk = load('BTC', 'D')` and return empty/NaN shares if `None`. |
| `ac94e4057` | — | Non-Python only (data/docs). | CLEAN | — |
| `e4c4ddbdd` | `MyTradingSys/research/edge4_rsi_4h_le12_2026-11-13/fetch_klines.py` (+1 `.py`) | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `437f15bc8` | — | Non-Python only (data/docs). | CLEAN | — |
| `981557364` | `MyTradingSys/research/rsi_confirm_layers_2026-11-13/make_report.py` (+2 `.py`) | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `835c38a57` | — | Non-Python only (data/docs). | CLEAN | — |
| `8e14fa6c4` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `d5eca1fb2` | — | Non-Python only (data/docs). | CLEAN | — |
| `bbaccb847` | — | Non-Python only (data/docs). | CLEAN | — |
| `90fc9ce87` | — | Non-Python only (data/docs). | CLEAN | — |
| `50b888fdf` | — | Non-Python only (data/docs). | CLEAN | — |
| `917495226` | — | Non-Python only (data/docs). | CLEAN | — |
| `b9d39f5e0` | `MyTradingSys/research/malkan_divergence_r03_r04_2026-11-13/mal_div_lib.py` (+2 `.py`) | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `6b47f3588` | — | Non-Python only (data/docs). | CLEAN | — |
| `680c35aff` | `MyTradingSys/research/rsi_htf_extreme_2026-11-13/htf_lib.py` (+2 `.py`) | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `f677e2b68` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `e796cd614` | — | Non-Python only (data/docs). | CLEAN | — |
| `3d511e24f` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `db6579ee6` | — | Non-Python only (data/docs). | CLEAN | — |
| `76093493a` | — | Non-Python only (data/docs). | CLEAN | — |
| `405d08d41` | `MyTradingSys/research/malkan_divergence_r03_r04_2026-11-13/fetch.py` | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `2475f37c4` | `MyTradingSys/research/rsi_confirm_layers_2026-11-13/fetch.py` (+1 `.py`) | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `54f315dd4` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `b9f9519f2` | — | Non-Python only (data/docs). | CLEAN | — |
| `811abde0a` | `MyTradingSys/research/rsi_htf_extreme_2026-11-13/fetch.py` (+1 `.py`) | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `1c4013770` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `3c60aa209` | — | Non-Python only (data/docs). | CLEAN | — |
| `0d69fda9a` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `1aa842bc9` | `MyTradingSys/research/fable_run7_forward_test/readout.py:130-131` | `analyse()` collects `brakes` (`skipped_halt`, `skipped_auto_pause`) across all `auto_rows` without filtering to the readout week `w0 <= k + BAR_MS < w1`, unlike `skipped_busy` and `skipped_floor` at lines 132-134. | RISK | Filter `brakes` to `w0 <= k + BAR_MS < w1` (or separate cumulative vs weekly brake counts). |
| `73b207b42` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `7b894a6a2` | — | Non-Python only (data/docs). | CLEAN | — |
| `b54623259` | — | Non-Python only (data/docs). | CLEAN | — |
| `307a39949` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `56c1a8bae` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `02d144104` | — | Non-Python only (data/docs). | CLEAN | — |
| `28adc9219` | — | Non-Python only (data/docs). | CLEAN | — |
| `46ff5b26b` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `e24a9c65a` | `MyTradingSys/research/edge_oi_flush_2026-11-13/fetch.py` | Revert of `a7f353353` (`edge_oi_flush_2026-11-13`). | CLEAN | — |
| `f06e58be9` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `fde3b1b20` | — | Non-Python only (data/docs). | CLEAN | — |
| `787cd69fd` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `ca422bccd` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `58c83f601` | — | Non-Python only (data/docs). | CLEAN | — |
| `b3e800d32` | — | Non-Python only (data/docs). | CLEAN | — |
| `2db525fb7` | `MyTradingSys/research/extreme_confirm_template_2026-11/core.py` | Revert of `715fe70a5` (`extreme_confirm_template_2026-11`). | CLEAN | — |
| `484016d96` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `0f24b2aea` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `758d81d0c` | — | Non-Python only (data/docs). | CLEAN | — |
| `137ecaf12` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `26d4d8c8f` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `3f2245cf8` | — | Non-Python only (data/docs). | CLEAN | — |
| `657b708e1` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `65523c9dd` | — | Non-Python only (data/docs). | CLEAN | — |
| `a3f91d55b` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `7d3c31c7d` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `518923d43` | — | Non-Python only (data/docs). | CLEAN | — |
| `eeaf09753` | — | Non-Python only (data/docs). | CLEAN | — |
| `607d7a3e2` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `88451985d` | — | Non-Python only (data/docs). | CLEAN | — |
| `cef0bc220` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `353c1914e` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `82d13a24a` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `62b0872a7` | — | Non-Python only (data/docs). | CLEAN | — |
| `097c265fb` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `b3064e1e2` | — | Non-Python only (data/docs). | CLEAN | — |
| `86dab640e` | — | Non-Python only (data/docs). | CLEAN | — |
| `2abb814b9` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `da5aab36e` | — | Non-Python only (data/docs). | CLEAN | — |
| `81c172a57` | `MyTradingSys/research/rsi_extreme_confirm_2026-11-13/engine.py` (+3 `.py`) | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `4cf93c850` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `614eaf710` | `MyTradingSys/research/rsi_extreme_confirm_2026-11-13/engine.py` (+3 `.py`) | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `3864218a8` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `32a26d519` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `839cef80f` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `b94212c25` | — | Non-Python only (data/docs). | CLEAN | — |
| `acb47415c` | — | Non-Python only (data/docs). | CLEAN | — |
| `c5645e041` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `1417bbb8a` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `2fc56523d` | — | Non-Python only (data/docs). | CLEAN | — |
| `535541038` | — | Non-Python only (data/docs). | CLEAN | — |
| `958505a2c` | — | Non-Python only (data/docs). | CLEAN | — |
| `8fa6d2537` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `e9c281380` | — | Non-Python only (data/docs). | CLEAN | — |
| `056bbf8e2` | — | Non-Python only (data/docs). | CLEAN | — |
| `bec5b8b3b` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `c529b925b` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `c2ce168b5` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `f2eb7e4b5` | — | Non-Python only (data/docs). | CLEAN | — |
| `078791693` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `1ffeabd0a` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `2346901c5` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `6fad9803e` | — | Non-Python only (data/docs). | CLEAN | — |
| `bfe54d5d1` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `7c7d31701` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `514377411` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `c0c9f440a` | — | Non-Python only (data/docs). | CLEAN | — |
| `9b9065ffa` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `12c0ef080` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `89f0e0051` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `c526af923` | — | Non-Python only (data/docs). | CLEAN | — |
| `a57954bb8` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `ddac4ffb7` | `MyTradingSys/research/rsi_range_census_2026-11-13/census_lib.py` (+3 `.py`) | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `f31e28ff0` | — | Non-Python only (data/docs). | CLEAN | — |
| `0c3bedc39` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `715fe70a5` | `MyTradingSys/research/extreme_confirm_template_2026-11/core.py` (+2 `.py`) | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `65f2d312c` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `cf596930a` | `MyTradingSys/research/rsi_extreme_confirm_2026-11-13/engine.py` (+2 `.py`) | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `2c9d12f0f` | `MyTradingSys/research/adx_1d_through25_2026-11-13/run_1113.py` | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `33a91b27c` | `MyTradingSys/research/adx_1d_through25_2026-11-13/run_1113.py:313` | `study()` evaluates `d['adx'][last] > 30 and d['adx'][last] > d['adx'][last - 1]` without guarding for `None` when a symbol has fewer than `2 * N` (28) daily bars, which would raise `TypeError`. | RISK | Check `d['adx'][last] is not None and d['adx'][last - 1] is not None` before comparing. |
| `70d5cc2e1` | `MyTradingSys/research/adx_1d_through25_2026-11-13/fetch_klines.py` | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `ec64e8c92` | `MyTradingSys/research/extreme_confirm_template_2026-11/fetch.py` | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `4bf9f6198` | `MyTradingSys/research/rsi_extreme_confirm_2026-11-13/fetch_bybit.py` | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `6ae9215a8` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `f9b81d91e` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `e57dcffa9` | `MyTradingSys/research/rsi_range_census_2026-11-13/fetch.py` | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `a7f353353` | `MyTradingSys/research/edge_oi_flush_2026-11-13/fetch.py` (+3 `.py`) | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `6c7e1df39` | — | Non-Python only (data/docs). | CLEAN | — |
| `377ff3a28` | — | Non-Python only (data/docs). | CLEAN | — |
| `19078a5cf` | `MyTradingSys/research/live_aid_flags_full_2026-11-13/run.py` | Revert of `4728a9b57` (`live_aid_flags_full_2026-11-13`). | CLEAN | — |
| `edcee25c7` | — | Non-Python only (data/docs). | CLEAN | — |
| `c895377dc` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `ebe60a4d4` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `45ad3a6a4` | `MyTradingSys/research/adx_di_2026-11/measure_1113.py:169,218` | `fade_table()` divides `len(low) / len(valid)` without guarding `len(valid) == 0`, and `run()` compares `dip[j] > dim[j]` and formats `adx[j]` without guarding `None` on short series (`< 28` bars). | RISK | Guard `len(valid) == 0` in `fade_table()` and check `None` before comparing/formatting `CUR`. |
| `09a709e1e` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `ce0e27be5` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `65586b240` | `MyTradingSys/research/adx_di_2026-11/measure_1113.py` | Revert of `adx_di_2026-11/measure_1113.py` (re-landed in `45ad3a6a4`). | CLEAN | — |
| `69ce15dca` | `MyTradingSys/research/sim_desk/build_catalogue.py` | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `91b97c4ea` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `025912e4a` | `MyTradingSys/research/adx_di_2026-11/measure_1113.py` | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `11f6367a1` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `54d649bc0` | — | Non-Python only (data/docs). | CLEAN | — |
| `67709d73a` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `140c0c613` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `33c6250c6` | `MyTradingSys/research/news_effects_2026-11/check_catalogue.py` | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `77d32e208` | — | Non-Python only (data/docs). | CLEAN | — |
| `24d19b5d3` | — | Non-Python only (data/docs). | CLEAN | — |
| `930350edc` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `4728a9b57` | `MyTradingSys/research/live_aid_flags_full_2026-11-13/run.py` (+1 `.py`) | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `fe3436571` | — | Non-Python only (data/docs). | CLEAN | — |
| `5f892abc1` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `274677a92` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `77efbd207` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `0be17fc4a` | `MyTradingSys/research/live_aid_liq_meaning_2026-11-13/liq_meaning.py` | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `61c8f76e6` | — | Non-Python only (data/docs). | CLEAN | — |
| `83bee59a6` | — | Non-Python only (data/docs). | CLEAN | — |
| `251a4be39` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `f57b22e9a` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `73c47df5b` | `MyTradingSys/research/adx_di_2026-11/measure_1113.py` | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `e41c9ab72` | `MyTradingSys/research/adx_di_2026-11/measure_1113.py` (+1 `.py`) | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `828ab5cb3` | — | Non-Python only (data/docs). | CLEAN | — |
| `405f6d5ba` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `58a607992` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `329ee21c8` | — | Non-Python only (data/docs). | CLEAN | — |
| `9dae31ac7` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `b456f1387` | — | Non-Python only (data/docs). | CLEAN | — |
| `5d88bfdff` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `f4a001da4` | `MyTradingSys/research/us_open_trader_2026-11-13/record_now.py` | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `9e694f0fd` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `33aa0b892` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `42511b99d` | — | Non-Python only (data/docs). | CLEAN | — |
| `26c16d526` | — | Non-Python only (data/docs). | CLEAN | — |
| `66e4c1bb3` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `035fdc977` | — | Non-Python only (data/docs). | CLEAN | — |
| `2f0c7dd0a` | — | Non-Python only (data/docs). | CLEAN | — |
| `2bffd911c` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `630c918e7` | — | Non-Python only (data/docs). | CLEAN | — |
| `3b01320f3` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `66b4a85e3` | — | Non-Python only (data/docs). | CLEAN | — |
| `2f10c8703` | — | Non-Python only (data/docs). | CLEAN | — |
| `b5dda085e` | — | Non-Python only (data/docs). | CLEAN | — |
| `98ca71600` | — | Non-Python only (data/docs). | CLEAN | — |
| `6b22ac394` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `da303567d` | — | Non-Python only (data/docs). | CLEAN | — |
| `4a55779f6` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `035dac5e7` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `039fd3755` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `860e24dc3` | `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py` (+1 `.py`) | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `d05d04a65` | — | Non-Python only (data/docs). | CLEAN | — |
| `6748c0713` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `98d25b491` | `MyTradingSys/research/live_aid_review_2026-11-11/fetch.py` | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `f11f0e6af` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `e06a3bead` | — | Non-Python only (data/docs). | CLEAN | — |
| `7d3f5fb29` | — | Non-Python only (data/docs). | CLEAN | — |
| `4fe2164d0` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `492334e52` | — | Non-Python only (data/docs). | CLEAN | — |
| `2b905e11c` | — | Non-Python only (data/docs). | CLEAN | — |
| `122aa5f9a` | — | Non-Python only (data/docs). | CLEAN | — |
| `cdc521b38` | — | Non-Python only (data/docs). | CLEAN | — |
| `fa2532cfe` | — | Non-Python only (data/docs). | CLEAN | — |
| `9f06fe1fa` | — | Non-Python only (data/docs). | CLEAN | — |
| `6712a68e4` | — | Non-Python only (data/docs). | CLEAN | — |
| `35dbaff68` | `MyTradingSys/research/nk_stocktalk_1113/review/harness.py` | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `77677a839` | `MyTradingSys/research/nk_stocktalk_1113/review/harness.py` | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `7b3a4e71e` | `MyTradingSys/research/nk_stocktalk_1113/review/harness.py` | Reviewed `.py` diff; no bugs, lookahead, DEV/VAL leaks, or fee/tz errors found. | CLEAN | — |
| `4b9975385` | — | Non-Python only (data/docs). | CLEAN | — |
| `d98bccbff` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `3b779d3af` | — | Non-Python only (data/docs). | CLEAN | — |
| `469523d9a` | — | Non-Python only (data/docs). | CLEAN | — |
| `e2f11afdd` | — | Merge commit (non-code / branch merge). | CLEAN | — |
| `52c23e0ff` | — | Non-Python only (data/docs). | CLEAN | — |
| `3d6951c12` | — | Non-Python only (data/docs). | CLEAN | — |
| `d3e495a25` | — | Non-Python only (data/docs). | CLEAN | — |
| `6db0886dd` | — | Non-Python only (data/docs). | CLEAN | — |
| `ddba1b138` | — | Non-Python only (data/docs). | CLEAN | — |
| `e99ae983f` | — | Non-Python only (data/docs). | CLEAN | — |
| `ec170f8ba` | — | Non-Python only (data/docs). | CLEAN | — |
| `455c976f7` | — | Non-Python only (data/docs). | CLEAN | — |
| `5d726f9ac` | — | Non-Python only (data/docs). | CLEAN | — |
| `dc7349913` | — | Non-Python only (data/docs). | CLEAN | — |
| `c40cd6df3` | — | Non-Python only (data/docs). | CLEAN | — |
| `a9fdf1bdb` | — | Non-Python only (data/docs). | CLEAN | — |
| `dea6efaf5` | — | Non-Python only (data/docs). | CLEAN | — |
| `ee6d6cb1f` | — | Non-Python only (data/docs). | CLEAN | — |
