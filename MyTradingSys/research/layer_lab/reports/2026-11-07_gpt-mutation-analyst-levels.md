# Mutation Audit: `scripts/dev/analyst_levels.py` vs `scripts/dev/test_analyst_levels.py` — 20 mutants (OURS): 12 KILLED (OURS), 8 SURVIVED (OURS)

- **Task**: `gpt-mutation-tests-analyst-levels-1107` (SOURCED: `MyTradingSys/system/tasks/active/gpt-mutation-tests-analyst-levels-1107.json` / card prompt)
- **Target Module**: `scripts/dev/analyst_levels.py` (186 lines SOURCED: `scripts/dev/analyst_levels.py:1-186`)
- **Test Suite**: `scripts/dev/test_analyst_levels.py` (205 lines SOURCED: `scripts/dev/test_analyst_levels.py:1-205`; 22 baseline tests passing in 0.020s OURS via `python -m unittest scripts/dev/test_analyst_levels.py`)
- **Programme Source**: `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md` section 6 ("mutation tests on `analyst_levels.py`" SOURCED: `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md:86`)
- **Method**: 20 single-site mutations (OURS) covering comparison flips, off-by-one shifts on as-of / cutoff dates, and dropped filters were generated in an isolated temporary directory (`tempfile.TemporaryDirectory`) with `sys.path` pre-pending the temp copy before importing `analyst_levels` and running `unittest` on `test_analyst_levels`. Neither `scripts/dev/analyst_levels.py` nor `scripts/dev/test_analyst_levels.py` was modified in the repository (`git status` clean other than this report, OURS).

---

## 1. Mutant Table (20 Mutants: 12 KILLED, 8 SURVIVED — OURS)

| Mutant | Line (`analyst_levels.py`) | Change (`original` -> `mutant`) | Category | Status (OURS) | Killing Test(s) in `test_analyst_levels.py` (OURS) |
|---|---|---|---|---|---|
| M01 | `analyst_levels.py:56` | `text = _NOT_PRICE.sub(" ", text)` -> `text = text` | Drop filter (`_NOT_PRICE` count filter: `"100k liquidations"` SOURCED: `analyst_levels.py:56`) | **KILLED** | `test_counts_are_not_prices` (`test_analyst_levels.py:36`) |
| M02 | `analyst_levels.py:57` | `text = _YEAR.sub(" ", text)` -> `text = text` | Drop filter (`_YEAR` date-cue filter: `"in 2026"`, `"by 2030"` SOURCED: `analyst_levels.py:36-37,57`) | **KILLED** | `test_bare_eth_price_in_year_range_kept` (`test_analyst_levels.py:93`), `test_eth_formats_and_band` (`test_analyst_levels.py:66`) |
| M03 | `analyst_levels.py:64` | `if lo <= v <= hi and v not in seen:` -> `if lo < v <= hi and v not in seen:` | Flip comparison (`<=` -> `<` on lower band edge `40_000` SOURCED: `analyst_levels.py:28,64`) | **KILLED** | `test_band_edges_inclusive` (`test_analyst_levels.py:162`) |
| M04 | `analyst_levels.py:64` | `if lo <= v <= hi and v not in seen:` -> `if lo <= v < hi and v not in seen:` | Flip comparison (`<=` -> `<` on upper band edge `200_000` SOURCED: `analyst_levels.py:28,64`) | **KILLED** | `test_band_edges_inclusive` (`test_analyst_levels.py:162`) |
| M05 | `analyst_levels.py:73` | `if symbol not in [cbp._norm_symbol(s) for s in r.get("symbols") or []]:` -> `if False:` | Drop filter (row symbol filter in `ladder()` SOURCED: `analyst_levels.py:73-74`) | **SURVIVED** | — (see Section 2, Survivor M05) |
| M06 | `analyst_levels.py:77-79` | `if (v, r.get("video_id")) in seen:` / `seen.add((v, r.get("video_id")))` -> `if v in seen:` / `seen.add(v)` | Drop filter scope (dedupe by `v` globally instead of per `video_id` SOURCED: `analyst_levels.py:77-79`) | **KILLED** | `test_same_level_two_videos_both_kept` (`test_analyst_levels.py:168`) |
| M07 | `analyst_levels.py:82` | `return sorted(lv, key=lambda x: -x["level"])` -> `return sorted(lv, key=lambda x: x["level"])` | Flip comparison/order (sort ascending instead of descending SOURCED: `analyst_levels.py:82`) | **KILLED** | `test_ladder_btc_only_sorted_one_per_video` (`test_analyst_levels.py:44`), `test_ladder_eth_levels` (`test_analyst_levels.py:53`) |
| M08 | `analyst_levels.py:86` | `cutoff = (now - timedelta(days=days)).date().isoformat()` -> `cutoff = (now - timedelta(days=days - 1)).date().isoformat()` | Off-by-one on as-of date window (`days` -> `days - 1` in `recent_rows()` SOURCED: `analyst_levels.py:86`) | **SURVIVED** | — (see Section 2, Survivor M08) |
| M09 | `analyst_levels.py:87` | `and (r.get("published") or "") >= cutoff]` -> `and (r.get("published") or "") > cutoff]` | Flip comparison (`>=` -> `>` on as-of cutoff date in `recent_rows()` SOURCED: `analyst_levels.py:87`) | **SURVIVED** | — (see Section 2, Survivor M09) |
| M10 | `analyst_levels.py:87` | `if not cbp.validate_row(r) and (r.get("published") or "") >= cutoff]` -> `if not cbp.validate_row(r)]` | Drop filter (drop `published >= cutoff` date filter in `recent_rows()` SOURCED: `analyst_levels.py:87`) | **SURVIVED** | — (see Section 2, Survivor M10) |
| M11 | `analyst_levels.py:100` | `if len(page) < 1000:` -> `if len(page) <= 1000:` | Flip comparison (`< 1000` -> `<= 1000` klines pagination cap SOURCED: `analyst_levels.py:92,100`) | **KILLED** | `test_klines_paginate_past_1000_cap` (`test_analyst_levels.py:98`) |
| M12 | `analyst_levels.py:108` | `+ timedelta(days=1)` -> `+ timedelta(days=0)` | Off-by-one on as-of date in `hit_from()` (00:00 UTC of publish day instead of day after SOURCED: `analyst_levels.py:11-12,108`) | **KILLED** | `test_publish_day_bars_never_count` (`test_analyst_levels.py:124`) |
| M13 | `analyst_levels.py:108` | `+ timedelta(days=1)` -> `+ timedelta(days=2)` | Off-by-one on as-of date in `hit_from()` (`+2 days` instead of `+1 day` SOURCED: `analyst_levels.py:108`) | **KILLED** | `test_publish_day_bars_never_count` (`test_analyst_levels.py:124`), `test_hit_touch_on_bar_extreme_counts` (`test_analyst_levels.py:173`) |
| M14 | `analyst_levels.py:117` | `seg = [b for b in bars if b[0] >= t0]` -> `seg = [b for b in bars if b[0] > t0]` | Flip comparison (`>= t0` -> `> t0` on first post-publish bar timestamp in `mark()` SOURCED: `analyst_levels.py:117`) | **KILLED** | `test_hit_touch_on_bar_extreme_counts` (`test_analyst_levels.py:173`) |
| M15 | `analyst_levels.py:118` | `min(b[2] for b in seg) <= x["level"] <= max(b[1] for b in seg)` -> `min(b[2] for b in seg) < x["level"] <= max(b[1] for b in seg)` | Flip comparison (`<=` -> `<` on bar low touch in `mark()` SOURCED: `analyst_levels.py:118`) | **KILLED** | `test_hit_touch_on_bar_extreme_counts` (`test_analyst_levels.py:173`) |
| M16 | `analyst_levels.py:118` | `min(b[2] for b in seg) <= x["level"] <= max(b[1] for b in seg)` -> `min(b[2] for b in seg) <= x["level"] < max(b[1] for b in seg)` | Flip comparison (`<=` -> `<` on bar high touch in `mark()` SOURCED: `analyst_levels.py:118`) | **KILLED** | `test_hit_touch_on_bar_extreme_counts` (`test_analyst_levels.py:173`) |
| M17 | `analyst_levels.py:120` | `cbp.parse_expiry(x["expires_at"]) <= now` -> `cbp.parse_expiry(x["expires_at"]) > now` | Flip comparison (`<= now` -> `> now` on `expired` flag in `mark()` SOURCED: `analyst_levels.py:120`) | **SURVIVED** | — (see Section 2, Survivor M17) |
| M18 | `analyst_levels.py:130` | `if not placed and x["level"] < price:` -> `if not placed and x["level"] > price:` | Flip comparison (`< price` -> `> price` for `---- now <price> ----` placement in `render()` SOURCED: `analyst_levels.py:130-131`) | **SURVIVED** | — (see Section 2, Survivor M18) |
| M19 | `analyst_levels.py:149` | `if cbp.parse_expiry(x["expires_at"]) > now]` -> `]` (filter removed) | Drop filter (unexpired filter in `hook_block()` SOURCED: `analyst_levels.py:146,149`) | **SURVIVED** | — (see Section 2, Survivor M19) |
| M20 | `analyst_levels.py:156` | `lv = [x for x in lv if abs(x["dist_pct"]) <= band_pct]` -> `lv = lv` | Drop filter (`band_pct` distance filter in `hook_block()` SOURCED: `analyst_levels.py:145-146,156`) | **SURVIVED** | — (see Section 2, Survivor M20) |

---

## 2. Surviving Mutants & Suggested Tests

All 8 surviving mutants (`M05`, `M08`, `M09`, `M10`, `M17`, `M18`, `M19`, `M20` — OURS) expose specific coverage gaps in `scripts/dev/test_analyst_levels.py`. Below is the root cause and a concrete test to kill each survivor.

### Survivor 1: `M05` — Row symbol filter dropped in `ladder()` (`analyst_levels.py:73`)
- **Why it survived**: In `test_ladder_btc_only_sorted_one_per_video` (`test_analyst_levels.py:44-49`) and `test_btc_unchanged_and_ignores_alt_rows` (`test_analyst_levels.py:60-64`), the non-BTC rows have pointers `"SOL 180"` and `"ETH support at 2,350"`, and the BTC row in `test_ladder_eth_levels` (`test_analyst_levels.py:53-58`) has pointer `"BTC support 75k"`. Because `parse_levels(p, symbol)` (`analyst_levels.py:64`) already rejects numbers outside `SYMBOL_BANDS[symbol]` (`BTC: (40_000, 200_000)`, `ETH: (1_000, 10_000)` SOURCED: `analyst_levels.py:28`), `180` and `2350` are rejected by the BTC price band and `75000` is rejected by the ETH price band even when the row symbol filter at `analyst_levels.py:73` is completely removed. However, if a non-BTC row mentions a number inside `40,000..200,000` (e.g., `"SOL 50,000 target"` or a cross-asset pointer on an altcoin row), dropping `analyst_levels.py:73` leaks that level into the BTC ladder.
- **Suggested test** (OURS):
```python
def test_ladder_symbol_filter_rejects_alt_row_with_in_band_number(self):
    rows = [row("Habib", ["SOL 50,000 wallets active, target 180"], symbols=("SOL",), vid="s1"),
            row("Krown", ["alt index at 45,000"], symbols=("ETH",), vid="e1"),
            row("Michael", ["BTC support at 75k"], symbols=("BTC",), vid="b1")]
    self.assertEqual([x["level"] for x in al.ladder(rows, symbol="BTC")], [75000.0])
```

### Survivors 2, 3, 4: `M08`, `M09`, `M10` — Cutoff date window and comparison in `recent_rows()` (`analyst_levels.py:86-87`)
- **Why they survived**: Every test that calls `recent_rows()` (`test_cli_symbol_flag` at `test_analyst_levels.py:72`, `test_chart_paste_shows_analyst_levels` at `test_analyst_levels.py:136`, and `test_main_offline_makes_no_network_call` at `test_analyst_levels.py:189`) constructs rows using the default `row(..., days_ago=1)` (`test_analyst_levels.py:17`). With `--days 10` (`analyst_levels.py:166`) or `days=7` (`analyst_levels.py:145`), a 1-day-old row always satisfies `published >= cutoff` even if `days` is off by one (`M08`), `>=` is flipped to `>` (`M09`), or the filter is removed (`M10`). No test includes a row exactly on the `days` boundary (`days_ago=10`) or older than `days` (`days_ago=11`).
- **Suggested test** (OURS, kills `M08`, `M09`, and `M10` simultaneously):
```python
def test_recent_rows_cutoff_boundary_inclusive_and_drops_older(self):
    now = datetime(2026, 10, 30, 12, 0, tzinfo=timezone.utc)
    r_in = dict(row("Michael", ["75k"]), video_id="v_in", published="2026-10-20")   # exactly 10 days ago (cutoff)
    r_out = dict(row("Krown", ["80k"]), video_id="v_out", published="2026-10-19")   # 11 days ago (outside)
    with tempfile.TemporaryDirectory() as d:
        store = os.path.join(d, "rows.json")
        with open(store, "w", encoding="utf-8", newline="\n") as f:
            json.dump({"schema": 1, "rows": [r_in, r_out], "rejected": []}, f)
        got = al.recent_rows(days=10, now=now, store=store)
    self.assertEqual([r["video_id"] for r in got], ["v_in"])
```

### Survivor 5: `M17` — Expiry comparison flipped in `mark()` (`analyst_levels.py:120`)
- **Why it survived**: Every test calling `al.mark()` (`test_publish_day_bars_never_count` at `test_analyst_levels.py:129` and `test_hit_touch_on_bar_extreme_counts` at `test_analyst_levels.py:176`) passes `expires_at=""`, and `test_render_hit_vs_open_tag` (`test_analyst_levels.py:181`) also passes `expires_at=""` without setting `expired`. Neither `x["expired"]` in `mark()` (`analyst_levels.py:120`) nor the `" exp"` suffix in `render()` (`analyst_levels.py:136-137`) is ever asserted.
- **Suggested test** (OURS):
```python
def test_mark_and_render_expired_boundary(self):
    now = datetime(2026, 10, 31, 12, 0, tzinfo=timezone.utc)
    t = int(datetime(2026, 10, 30, tzinfo=timezone.utc).timestamp())
    bars = [(t, 80_000.0, 79_000.0, 79_500.0)]
    lv = [
        dict(analyst="A", published="2026-10-29", bias="BULL", video_id="v1", said="s", level=80_000.0, expires_at="2026-10-31T12:00:00Z"),
        dict(analyst="B", published="2026-10-29", bias="BULL", video_id="v2", said="s", level=75_000.0, expires_at="2026-10-31T12:00:01Z"),
    ]
    al.mark(lv, bars, now)
    self.assertEqual([x["expired"] for x in lv], [True, False])
    out = al.render(lv, price=79_500.0)
    self.assertIn("HIT  exp", out)
```

### Survivor 6: `M18` — Spot marker placement comparison flipped in `render()` (`analyst_levels.py:130`)
- **Why it survived**: `test_render_hit_vs_open_tag` (`test_analyst_levels.py:180-187`) passes only a single level (`75000.0`) below `price=79000.0` and only asserts `assertIn("-5.00% HIT ", hit)`. Whether `---- now 79,000 ----` is placed before the first level `< price` (`analyst_levels.py:130`) or appended at the bottom (`analyst_levels.py:140-141`), `"-5.00% HIT "` is still present in the string. No test checks line ordering of `---- now <price> ----` between levels above and below spot.
- **Suggested test** (OURS):
```python
def test_render_places_spot_divider_between_higher_and_lower_levels(self):
    base = dict(analyst="Michael", published="2026-10-29", bias="BEARISH", video_id="v1", said="s", expires_at="", hit=False)
    lv = [dict(base, level=82_000.0, dist_pct=2.5), dict(base, level=78_000.0, dist_pct=-2.5)]
    lines = al.render(lv, price=80_000.0).splitlines()
    idx_82 = next(i for i, ln in enumerate(lines) if "82,000" in ln)
    idx_now = next(i for i, ln in enumerate(lines) if "---- now 80,000 ----" in ln)
    idx_78 = next(i for i, ln in enumerate(lines) if "78,000" in ln)
    self.assertTrue(idx_82 < idx_now < idx_78)
```

### Survivors 7 & 8: `M19` & `M20` — Unexpired filter (`analyst_levels.py:149`) and `band_pct` distance filter (`analyst_levels.py:156`) dropped in `hook_block()`
- **Why they survived**: `test_chart_paste_shows_analyst_levels` (`test_analyst_levels.py:136-146`) mocks `spot_1h` to raise `OSError("offline")` (so line 156 `abs(x["dist_pct"]) <= band_pct` is never reached) and only provides a single unexpired row (`expires_at = now + 5 days` from `row()`, `test_analyst_levels.py:21`). Thus neither the expiry filter at `analyst_levels.py:149` nor the `band_pct` filter at `analyst_levels.py:156` is ever exercised with a row that should be excluded.
- **Suggested test** (OURS, kills both `M19` and `M20`):
```python
def test_hook_block_filters_expired_and_outside_band_pct(self):
    now = datetime.now(timezone.utc)
    r_near = row("Michael", ["support 78k, far 60k"], days_ago=1, vid="v_live")
    r_exp = dict(row("Krown", ["support 79k"], days_ago=2, vid="v_exp"),
                 expires_at=(now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ"))
    t = int(now.timestamp()) - 3600
    bars = [(t, 80_500.0, 79_500.0, 80_000.0)]  # spot = 80,000 -> 78k is -2.5% (in 6% band), 60k is -25.0% (out)
    with mock.patch.object(al, "recent_rows", return_value=[r_near, r_exp]), \
            mock.patch.object(al, "spot_1h", return_value=bars):
        out = al.hook_block(days=7, band_pct=6.0)
    self.assertIn("78,000", out)
    self.assertNotIn("60,000", out)  # kills M20 (band_pct filter)
    self.assertNotIn("79,000", out)  # kills M19 (expiry filter)
```

---

## 3. Verification Commands & Repo Cleanliness

- **Baseline test command**: `python -m unittest scripts/dev/test_analyst_levels.py` -> `Ran 22 tests in 0.020s OK` (OURS).
- **Repo diff check**: `git status --short` shows only `?? MyTradingSys/research/layer_lab/reports/2026-11-07_gpt-mutation-analyst-levels.md` (`scripts/dev/analyst_levels.py` and `scripts/dev/test_analyst_levels.py` untouched, 0 lines changed — OURS).
