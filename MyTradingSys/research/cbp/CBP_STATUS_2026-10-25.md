# CBP status 2026-10-25 (Builder, read-only audit; sources read this turn)

## 1. What exists and works
- MTS side: `scripts/dev/cbp_run.py` (single entry, `--due`/`--force`) and `MyTradingSys/cbp/{__init__.py,schema.json}` (`cbp.query(analyst, symbol, since_days=5)`), per D5 "as built" (v1_plan_2026-10-20/D5_CBP_MODULE.md:6-20). Queue/consumer/adapter removed (D5:18); B139 item still says OPEN and describes the old adapter (items/B139_cbp_adapter.md:3,8): stale.
- CBP repo F:/CryptoScrapper (branch cloud/work): first `cbp_run --force` stored 13 rows, 1 rejected (commit d184752); queue retired (7d2937b); one dashboard from `cbp_store/rows.json` (296e318); inbox deleted, transcripts in `raw_transcripts_canonical/` (d20ae76). `cbp_store/rows.json` exists.
- One quote checker: `verify_extract_quotes.py` accepts CBP `evidence:` lines; filler/stutter fix (thinker/2026-10-23_cbp_quote_problems.md:18-19). Card cbp-one-quote-checker = done.
- Actionable-6 profile (Rekt, Jason, Krown, Michael, Michaal, Qriptal) on; thesis-only analysts (Benjamin, Bob, Jala, CCU) off by default; -85% bytes in the store vs all-enabled (research/cbp_profile6_result.md:4-6). CBP commit 50e71c3.
- Fetcher has `--channel --latest N` (fetch_captions_timed.py:5-9; card done).
- Golden set + producer gates + 26 CBP tests pass (thinker/2026-10-23_cbp_ultra_verdict.md:9,17).

## 2. What was decided
- Core-vs-adopt: A2 (adopt existing tools, no new Extraction Core) wins on build size only, not on dedupe or tokens (thinker/2026-10-23_cbp_core_vs_adopt.md:35).
- Opus roadmap: CBP fetches/extracts/stores, layers call `cbp.query`; DELETE queue/acks/consumer/scheduler; KEEP quote gate, dedupe, B139 gate for trading only (thinker/2026-10-23_cbp_roadmap_opus.md:6-7,19-29).
- Operator: 5-day window, MTS runs CBP (never self-running), 2-3 runs/day by due-ness windows, no scheduler (roadmap_opus.md:64-73).
- Ultra verdict (independent, 10-23): 3 of 15 rows NOT MET = golden CI never ran (GitHub billing), leftover scheduled-task file, no analyst scorecard (ultra_verdict.md:11,13,18). Rows 5/7 cheap; gate 4 open (D5:79 PENDING). Rows are claims, not signals; nothing trades without gate 5 (D5:19).

## 3. Open cards (tasks.py list, 2026-10-25)
- raw: cbp-actionable-6-extraction-profile (work shipped per profile6_result; card not closed), cbp-adapter-read-raw-transcripts (adapter removed: likely drop), cbp-quote-row-84-jason-bo88aebojf8-retry (p4), cbp-repo-commit-krown-ack-tidy (queue retired: likely drop), cbp-routine-retire-cbp-daily-workflow-skill.
- done: mts-cbp-integration, cbp-add-channel-latest-n, cbp-one-quote-checker. dropped: cbp-one-acked-row-through-queue.
- new: gemini-ccu-dxntdn3jfTg-check (ready, CODEX lane).

## 4. Blockers
- Quote problems (quote_problems.md:8-14): 5 remain in old extractions.md: 2 non-verbatim preamble digests, 2 altered/spliced Jala quotes, 1 missing transcript (Jason bO88AeBojf8, HTTP 429). Old-block problems predate the 22 Oct run.
- YouTube 429 on caption fetch (row 84). All YouTube work now Gemini on NUC only (operator 2026-10-25).
- Golden CI on CBP repo blocked by GitHub billing (ultra_verdict.md:11). Routine file `~/.claude/scheduled-tasks/cbp-daily-workflow/SKILL.md` still on disk (ultra_verdict.md:13; roadmap_opus.md:12).
- No scorecard, so no analyst weight is justified (D5:51).

## 5. Next 3 steps (RECOMMENDATION, OURS)
1. Housekeeping card: delete the 3 leftover routine files, close/drop the stale raw cards, mark B139 superseded by D5.
2. Build analysts/SCORECARD.md (56 scored calls per analyst, D5 gate 4) from `cbp_store` rows vs price: the only thing that says which analyst is worth a layer.
3. Fix CI on the CBP repo (billing or run golden harness locally in MTS CI), then one `cbp_run --due` via the coordinator; retry Jason row 84 through Gemini fetch.

## CCU DXntdN3jfTg
(pending Gemini run)
