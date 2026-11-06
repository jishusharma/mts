# Blind read: scripts/dev/analyst_levels.py (2026-11-06)

Read from analyst_levels.py and test_analyst_levels.py only; the earlier gpt audit/mutation reports were not read. Parse claims checked by running parse_levels on ad-hoc strings.

## Hit timing / no-hit-before-video rule
Correct as documented: hit_from (L96-98) = 00:00 UTC of the day after the date-only publish date; mark (L104-106) keeps bars with t >= that; high/low columns are right (spot_1h returns (t, high, low, close), mark uses b[1]=high, b[2]=low, b[3]=close). No off-by-one found; the test pins both the edge and the boundary (L87-95, L136-141).
Caveats: (a) same-day touches after the video are missed by design; (b) if `published` is a local date west of UTC, bars from the next UTC midnight can still precede the video (hours of lookahead); source timezone not checked; (c) a touch after expires_at still counts HIT (expired is a separate flag).

## Defects
1. L32-33 _NOT_PRICE tail-matches inside a comma number: "75,000 BTC" is read as "75," + "000 BTC", the token is removed, and the level is lost. Verified: parse_levels("support at 75,000 BTC") = [] and ("target 80k BTC") = [] (the count-word list includes BTC/ETH, so a price followed by the ticker is dropped). False negatives on real levels.
2. L35, L55 _YEAR strips any bare 2020-2039 for ETH, whose band is 1,000-10,000 (L28): "ETH 2030 support" gives []. A plausible ETH level is treated as a year (comma forms like 2,030 are kept).
3. L90-93 spot_1h limit=1000 hourly bars (~41.6 days) with startTime=since: for --days over about 41 the series stops short of now, so `price = bars[-1][3]` is stale and recent touches are missed. Default 10 and hook 7 are safe. Also an empty kline list gives IndexError at L102 in main (hook_block swallows it, main crashes).
4. L74 dedupe key (level, video_id): rows lacking video_id collapse all of their levels together across rows (r.get returns None/""). Rows normally have video_id, so low risk.
5. L29 LO, HI are unused after SYMBOL_BANDS; L55 has a misplaced comment ("100k liquidations" note sits on the _YEAR line). Docstring L11 still says prices 40k..200k (BTC only).

Not defects: expires_at is mandatory and validated by cbp.validate_row (cbp/__init__.py L94), so the empty-expiry branch at L108 cannot be hit from valid rows; the `now` line placement (L118) and "one level per video" (L74-77) match the docstring.

FOUND: 5 defects (#1, #2, #3 behavioural; #4, #5 minor), 3 caveats. DIFF vs docstring claims: 2 (ETH band vs "prices 40k..200k" wording; count filter dropping ticker-suffixed prices).
