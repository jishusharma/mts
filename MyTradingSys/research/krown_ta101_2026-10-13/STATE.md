# Krown TA 101 - state board (rewritten 2026-10-14 after batch 2; counts come from MANIFEST.csv)

Playlist: TA 101 - Everything You Need To Know (PLPEz1q0esi3gEd4DMbaGwFf3uqwAY6vTU), checked 2026-10-14 with
`yt-dlp --flat-playlist -J` (metadata only): **37 entries = 19 reachable + 18 hidden by YouTube** (no title, no captions).
The older note said "28 listed / 18 reachable / 10 to do". That was wrong: 11 ids were pending at that time, 19 are reachable.

| Stage | Count | Detail |
|---|---|---|
| Reachable | 19 | 14 TA + 1 fees video extracted, **4 still missing** |
| Phase 1 extracted | 15 | batch 1 (Aug-Oct 2026): 7 TA episodes + the fees video; batch 2 (Mar-Jun 2026): 7 TA videos |
| Quote gate | 15 of 15 PASS | re-run 2026-10-14 by this session, not taken from worker reports |
| Number gate | 15 of 15, 0 wrong | 4 benign mismatches in batch 1 (MANIFEST.csv), 0 in batch 2 |
| Phase 1 missing | 4 | hNfjyrJEytI fMRvOt26xcA LB3DRYxnA0A _JoJbu_Ug-A (captions: HTTP 429) |
| Hidden | 18 | not retrievable; NOT_IN_DATA (private, removed or members-only: unknown) |
| Phase 2/3 ledger | 120 rules | 99 READY, 6 BLOCKED, 15 REJECT; 0 dead source pointers; KROWN_CONSOLIDATED.md, KROWN_RULES.csv |
| Layer spec / pre-reg | draft v0.2 | KROWN_LAYER_SPEC.md, PRE_REG_KROWN.md |

## Batch 2 changed the picture
- It is an earlier series (Mar-Apr 2026: guide, trend, levels, moving averages, RSI, volatility) plus a tops video (Jun 2026); the
  Aug-Oct "TA Foundations" episodes re-teach much of it. Overlap raises confidence in the shared rules; the differences are conflicts C9-C14.
- **Stops and exits exist now**, though thinly: the volatility video (kcMnnQr1VFg) gives a complete compression-breakout setup with a
  structural stop (far side of the compression zone, a close beyond it) and a volatility-based exit (BBWP peak). Still no stop distance,
  no general position size.
- New rule families: volatility (BBWP), RSI zones and divergence, the four-signal top framework, the dominant-high/low trend state.

## Remaining blocker: captions for 4 videos
- 2026-10-14: a 11-id fetch from JIS-NB returned 7 transcripts and HTTP 429 for 4 (the rate limit is intermittent, not a total block;
  an earlier note of mine that "all 11 are blocked" was wrong and is corrected here). Rules (LESSONS_DIGEST s6): STOP on a bot check,
  no cookies, tokens or third-party sites, no YouTube watch pages in the in-app browser (it autoplays audio).
- Options (operator picks, decision q-krown-captions): (a) retry once a day for 3 days; (b) paste the 4 transcripts into
  `transcripts/<id>_timed.txt` (plain text is fine); (c) skip them: 14 TA videos are the corpus.
- Their titles (content unread): top-down method order, "you don't need chart patterns", building a system, beginners adding indicators.

- 2026-10-17 (card krown-ta101-extract-remaining-10): the one allowed retry from JIS-NUC returned HTTP 429 on all 4 ids (4 backoff attempts each, no file written). Stopped per rule. Still open: operator paste (b) or a later retry from another IP; extraction, gates and ledger rebuild not started.
- 2026-10-18 (card krown-ta101-extract-remaining-10): the one allowed retry returned HTTP 429 (Too Many Requests on subtitles endpoint). Stopped per rule. Still open: operator paste (b) or a later retry from another IP; extraction, gates and ledger rebuild not started.

## Next steps, in order
1. Layer v0: detectors + recall check on his dated examples (cards `krown-layer-v0-detectors`, `krown-data-daily-majors`, `krown-recall-check`),
   then one pre-registered DEV event study (card `krown-dev-event-study`). Scope now includes the volatility, RSI and top modules.
2. If the 4 transcripts arrive: one fresh Sonnet worker per video (PROTOCOL.md s3), both gates, `python tools/build_ledger.py`, add amendments to
   the batch-2 block of `tools/build_ledger.py`, reflexivity_log batch 3.
3. Other Krown sources not yet read: daily BTC event-study videos and CBP candidates (options/research/KROWN_FREE_VS_PAID.md; card
   `krown-other-sources-event-study-videos`).

## 2026-10-18 update (planner)
- EP08 (ftK2BqggabQ, order book, TA Foundations episode 8) went public 2026-10-17; it was one of the 18 hidden ids. Extracted: 22 concepts, both gates PASS (MANIFEST row 35). The other 17 hidden ids re-checked 2026-10-18: all still private (likely unreleased episodes). Read FOUNDATIONS_EP08_IMPLICATIONS.md; follow-up card krown-foundations-ep08-follow-through.
