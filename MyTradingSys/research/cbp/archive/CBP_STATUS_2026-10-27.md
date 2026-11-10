# CBP status 2026-10-27 (Builder, read-only audit; sources read this turn)

## 1. What exists and works
- MTS side: `scripts/dev/cbp_run.py` (single entry, `--due`/`--force`) and `MyTradingSys/cbp/{__init__.py,schema.json}` (`cbp.query(analyst, symbol, since_days=5)`), per D5 "as built" (v1_plan_2026-10-20/D5_CBP_MODULE.md:6-20). Queue/consumer/adapter removed (D5:18); B139 item now marked SUPERSEDED (items/B139_cbp_adapter.md:3).
- CBP repo F:/CryptoScrapper (branch cloud/work): first `cbp_run --force` stored 13 rows, 1 rejected (commit d184752); queue retired (7d2937b); one dashboard from `cbp_store/rows.json` (296e318); inbox deleted, transcripts in `raw_transcripts_canonical/` (d20ae76). `cbp_store/rows.json` exists.
- One quote checker: `verify_extract_quotes.py` accepts CBP `evidence:` lines; filler/stutter fix (thinker/2026-10-23_cbp_quote_problems.md:18-19). Card cbp-one-quote-checker = done.
- Actionable-6 profile (Rekt, Jason, Krown, Michael, Michaal, Qriptal) on; thesis-only analysts (Benjamin, Bob, Jala, CCU) off by default; -85% bytes in the store vs all-enabled (research/_archive/loose_2026-10/cbp_profile6_result.md:4-6). CBP commit 50e71c3.
- Fetcher has `--channel --latest N` (fetch_captions_timed.py:5-9; card done).
- Golden set + producer gates + 26 CBP tests pass (thinker/2026-10-23_cbp_ultra_verdict.md:9,17).

## 2. What was decided
- Core-vs-adopt: A2 (adopt existing tools, no new Extraction Core) wins on build size only, not on dedupe or tokens (thinker/2026-10-23_cbp_core_vs_adopt.md:35).
- Opus roadmap: CBP fetches/extracts/stores, layers call `cbp.query`; DELETE queue/acks/consumer/scheduler; KEEP quote gate, dedupe, B139 gate for trading only (thinker/2026-10-23_cbp_roadmap_opus.md:6-7,19-29).
- Operator: 5-day window, MTS runs CBP (never self-running), 2-3 runs/day by due-ness windows, no scheduler (roadmap_opus.md:64-73).
- Ultra verdict (independent, 10-23): 3 of 15 rows NOT MET = golden CI never ran (GitHub billing), leftover scheduled-task file, no analyst scorecard (ultra_verdict.md:11,13,18). Rows 5/7 cheap; gate 4 open (D5:79 PENDING). Rows are claims, not signals; nothing trades without gate 5 (D5:19).

## 3. Open cards (`python scripts/dev/tasks.py list`, 2026-10-27)
- dropped (shipped or retired): cbp-actionable-6-extraction-profile-rekt (CBP 50e71c3, research/_archive/loose_2026-10/cbp_profile6_result.md), cbp-adapter-read-raw-transcripts-canonic (adapter removed f9fcf77b4), cbp-repo-commit-krown-ack-tidy-pending-a (queue retired), cbp-one-acked-row-through-queue-consumer.
- done: mts-cbp-integration-land-one-cbp-candida, cbp-add-channel-latest-n-to-fetch-captio, cbp-one-quote-checker, gemini-ccu-dxntdn3jfTg-check.
- refined, left: cbp-routine-retire-cbp-daily-workflow-sk (parked: SKILL.md is on another host, delete by hand there; this host's ~/.claude/scheduled-tasks holds only mts-dispatcher, mts-lane-watch); cbp-quote-row-84-jason-bo88aebojf8-retry (p4, needs YouTube: Gemini on the NUC).
- ready CODEX: cbp-scorecard-recount, cbp-quote-gate-review, cbp-gates-planted-bad-row. raw: cbp-ingestion (p1, CODEX).
## 4. Blockers
- Quote problems (quote_problems.md:8-14): 5 remain in old extractions.md: 2 non-verbatim preamble digests, 2 altered/spliced Jala quotes, 1 missing transcript (Jason bO88AeBojf8, HTTP 429). Old-block problems predate the 22 Oct run.
- YouTube 429 on caption fetch (row 84, Jason bO88AeBojf8). The 2026-10-25 "all YouTube work Gemini on NUC only" note
  was a preference, not a limit (bug-youtube-gemini-only-rule-is-a-preference, 2026-10-27; ROUTING.md updated):
  `fetch_captions_timed.py` already falls back to `youtube-transcript-api` on a 429, so `cbp_run.py` can be retried
  on any machine; it is not blocked on Gemini/NUC specifically.
- Golden CI on CBP repo blocked by GitHub billing (ultra_verdict.md:11). Routine file `~/.claude/scheduled-tasks/cbp-daily-workflow/SKILL.md` still on disk (ultra_verdict.md:13; roadmap_opus.md:12).
- No scorecard, so no analyst weight is justified (D5:51).

## 5. Next 3 steps (RECOMMENDATION, OURS)
1. Housekeeping card: delete the 3 leftover routine files, close/drop the stale raw cards, mark B139 superseded by D5.
2. Build analysts/SCORECARD.md (56 scored calls per analyst, D5 gate 4) from `cbp_store` rows vs price: the only thing that says which analyst is worth a layer.
3. Fix CI on the CBP repo (billing or run golden harness locally in MTS CI), then one `cbp_run --due` via the coordinator; retry Jason row 84 through Gemini fetch.

## CCU DXntdN3jfTg
Result: NO CONTENT CHECKED. Captions blocked by YouTube: `ERROR: Unable to download video subtitles for 'en': HTTP Error 429: Too Many Requests` (NUC, Gemini job gemini-q/gemini-ccu-dxntdn3jfTg-check, `fetch_captions_timed.py --analyst CCU DXntdN3jfTg`; the timedtext endpoint itself returned 429).
- Metadata only (from yt-dlp, not from captions): channel Crypto Crew University, upload 2026-10-20, ~21m16s; title text came back garbled (a "Bitcoin's Bull Flag Breakout: Is Crypto About to Explode?" style title), unverified.
- BTC call, levels, bottom-thesis vote, entry/stop/target: UNKNOWN. No quotes exist, none invented. Extract file records the 429 and passes `verify_extract_quotes.py` (exit 0, 0 quotes); it sits on NUC branch gemini-q/gemini-ccu-dxntdn3jfTg-check (not shipped).
- Next: retry after the 429 cools (same card, new run), same retry as cbp-quote-row-84.

