# Which videos are worth a caption download: the selection method (2026-10-15)

Why: YouTube rate-limits anonymous caption fetches (HTTP 429), so every fetch has a cost. Download only the videos most likely to
state rules (entry, stop, target, zones, named setups) in the trader's own words. Metadata only, anonymous (no cookies, no tokens, no
third-party caption sites, no watch pages in a browser). Tier of the result: a ranking from titles and descriptions, T3. It says which
transcript to read first, not what the trader teaches.

**Every weight below is OURS** (judgement, not the trader's), set before looking at any transcript. The named setups in the NAMED row
come from the operator's own list (RSI 40/60, 5-star, 7-star); the numbers attached to them are still OURS.

## Pipeline (all scripts in this folder, rerunnable)
1. `fetch_meta.py playlists`: the channel's 46 playlists and their members (1,210 memberships). One request per 5 s.
2. Channel listing (`yt-dlp --flat-playlist --dump-json`): 876 videos with id, title, duration, views (`data/malkan_flat.jsonl`). No dates in flat mode.
3. `score.py prelim`: a flat-only score over all 876 picks the top 60 (cut score 4.7) + the anchors + the 5 blocked ids = 61 candidates.
4. `fetch_meta.py detail <ids>`: full metadata for the 61 (description, upload date, chapters, tags), one request per 5 s, no 429 seen (`data/detail/`).
5. `score.py final`: full score, `RANKED_MALKAN.csv`. `krown_rank.py`: `RANKED_KROWN.csv`. `apply_selection.py`: card and inventory.
6. `sensitivity.py`: weights perturbed at random, 300 draws, to see whether the validation ranks survive (`data/sensitivity.txt`).

## Signals and weights (all OURS)
| Signal | Weight | Reading |
|---|---:|---|
| NAMED setup in the title: 5-star / 7-star (also Hindi स्टार, "five/seven star"), RSI 40/60 | +5 each family | the operator's named rules |
| CORE family in the title: GFS / Grandfather-Father-Son; divergence / PRD / NRD (डायवर्ज); range shift / loud move / monster move / 3X3 | +3 each family | the trader's method families |
| core total | capped at 8 | |
| GENERIC rule words in the title: setup (सेटअप), strategy (रणनीति, स्ट्रेटेजी), rules (नियम), entry (एंट्री), stop, target (टार्गेट), exit | +1 each family, cap 3 | names a rule, not a topic |
| the title says RSI | +1 | |
| description and chapter titles carry the same terms | x0.5 | |
| Hindi or Hinglish title (Devanagari, or ka/ki/kaise/nahi/se...) | +1 | Hindi is thin in our corpus and the operator asked for it; a tie-break only |
| title starts "N." inside the 3X3 Swing Trading series | +3 | the trader's own numbered course (series membership) |
| member of RSI Mastery Series | +3 | the trader's own strategy playlist |
| member of Downtrend Trading Secrets / Find The Bottom | +1.5 each | |
| member of Tuesday Technical Talk / Binge Series Top Down | +1 each | |
| member of a testimonial / success-story / mindset / interview playlist and no CORE term | -3 | not teaching |
| another pool video's description points to this id (`youtu.be/<id>`) | +1 per video, cap 2 | cross reference |
| age-adjusted views: log10((views / channel median 8,800) / (age / 2.89 y)^0.5) x 1.5, floor 0, cap 3 | 0..3 | popularity with half the age effect removed (2.89 y = median age of the pool) |
| teaching length 7-60 min | +1 (60+ min: +0.5) | |
| 3 or more chapters | +0.5 | structured lesson |
| weekly market update / market view | -4 | a rule is not the point |
| scanner / screener / stocks to watch / index target / sector call | -3 | stock tips and tools |
| options-only title (no RSI) | -2 | out of scope for the BTC layer |
| HARD EXCLUDE (include=N whatever the score) | | under 240 s (shorts); live, Q&A, testimonial, journey, motivation, mindset, daily update |

Hindi titles: the English translation is machine-made by me and kept beside the original in the CSV (`english_title`; the dictionary is in
`score.py`, `TRANSLATE`). The language column is a **title guess** (a Hinglish title is not proof of Hindi speech; Tuesday Technical Talk
titles are English but the talk is often Hindi); confirm at caption time that the `hi` track exists.

## Selection rule
1. Rank everything in the pool by score. 2. Among videos with no caption on disk, take the best one of each operator-named family
(5-star, 7-star, RSI 40/60 + GFS, divergence, range shift) so the ten are not five copies of the same topic (coverage guarantee).
3. Fill to 10 by rank. 4. Add any of the 5 blocked ids whose score is at or above the lowest selected score. Result: **12 selected**
(10 + kVIvcn7T44o and WBByyLBp8-c); of the 5 blocked ids, 4 rank in; FHEoMmD6xKM (candle patterns) does not and is NOT SELECTED.
Videos already on disk (6) are ranked but never re-fetched.

## Validation (the two known setup videos must land in the top 10)
Pool: 61 videos. Anchors: `W1HrDl70Lhk` (5-star RSI, Hindi speech, English title) and `A-CQiV_UFB4` (8. RSI Reverse Divergence, Hindi speech).
| Version | A-CQiV_UFB4 | W1HrDl70Lhk | Change |
|---|---:|---:|---|
| v1 equal weights on the core families, series +2 | **11** (11.72, a tie with rank 12) | 3 | first run: A-CQiV missed the top 10 |
| v2 | 10 | 3 | added scanner / screener to the stock-tip penalty (the old rank 7 was a stock scanner video, not a rule) |
| v3 (final) | **6** (12.72) | **2** (16.00) | (a) named setups (5/7-star, 40/60) +5 vs +3 for method families, because v2 selected no 5-star or 7-star video although the operator named them; (b) series +2 -> +3; (c) removed the word "reversal" from the divergence family (it gave candlestick videos +3); (d) the coverage guarantee |

Honest limits of this check: (b) was set with the anchors in view, so rank 6 is **not** an out-of-sample proof; there are only two anchors.
`sensitivity.py` (each of 15 weights multiplied by a random factor in +-30%, 300 draws): A-CQiV in the top 10 in 95% of draws (median 6, worst 18),
W1HrDl70Lhk in 100% (median 2, worst 8). At +-50%: 80% and 96%. So the placement is stable to moderate re-weighting, not to arbitrary weights.

Corrections to the brief, found by the metadata:
- `A-CQiV_UFB4` is "8. RSI Reverse Divergence" (3X3 series); the seven-star setup in the extracts is in `Wvq1TZh8aF0` (MAL-19, "RSI Divergence Explained Simply",
  42 min). Its title does not say 7-star, so a metadata method cannot see it: it ranks **20** (3% of draws in the top 10). A known miss.
- `W1HrDl70Lhk` is not on the Malkansview channel: it is Trader Insights' explainer (2021-10-02) of Malkan's 5-star RSI. Its description links the original,
  `f6SrqRt7Epc` (Malkan's own upload), which is **private** (yt-dlp: Private video) and not in the 876-video listing. Logged; nothing to fetch.
- The actual 5-star and 7-star videos on the channel: `v8pCR_bA0_0` (RSI - 5 Star Set Up #1, 2019, 569k views, rank 14, selected), `kL7_ybtI_Fc` (5 star, Hindi
  title, rank 22), `U12jz3LQhy0` ((7 STAR) Perfect Reversal, rank 24, selected), `c8HJV1sqNHg`, `XFO49JlODxI`, `quoII9t08Qc`, `bzbQ4_7eoZs`. Already on disk: `2HcJ3NeZmEQ` (5-star sell).

## Known weaknesses
- Titles and descriptions only. A video whose title is vague but whose content is the rules (like Wvq1TZh8aF0) is under-ranked; ones with a rule-sounding
  title and loose content are over-ranked. After the first transcripts land, compare the setups found per selected video with the score and refit (log the refit).
- 815 videos were scored on the flat listing only (title, views, duration, playlists) and none reached the detail cut; a rule-bearing video with a bland title and
  no playlist is invisible to this method.
- Views reward age-independent popularity only partly; the age exponent 0.5 is a guess.
- Playlist coverage is the channel's own playlists; videos outside any playlist get no membership signal.

## Krown (order only, nothing cut)
`RANKED_KROWN.csv` orders the pending ids of the operator's TA 101 playlist plus the four options-list priority ids with the same text signals, plus +2 for TA 101 membership.
Order: hNfjyrJEytI (4-step TA sequence, 1202 s), fMRvOt26xcA (chart patterns, 1774 s), LB3DRYxnA0A (255 s), _JoJbu_Ug-A (314 s), then the two Cointelegraph interviews
(EQy4HouRMMk, -9rAJNUpMsk; interviews -3), then the two Shorts UHY740h3e-Y (41 s) and SOaAP9vBgM4 (54 s): the options-list "priority 1 and 2" ids are Shorts, so their captions are cheap
and short. The 18 hidden playlist entries (H20-H37 in MANIFEST.csv) have no metadata and cannot be ranked. The Krown card's "10" is stale: it lists 4 pending TA ids.

## Rerun
```
python MyTradingSys/research/video_priority_2026-10-15/score.py final   # RANKED_MALKAN.csv from data/
python MyTradingSys/research/video_priority_2026-10-15/krown_rank.py
```
New videos or a changed weight: edit `score.py`, rerun, and log the change in the table above.
