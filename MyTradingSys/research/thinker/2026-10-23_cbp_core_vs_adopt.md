# CBP integration: old plan (A, new Extraction Core) vs better plan (A2, adopt what exists) - Thinker, 2026-10-23

Operator order: beat the previous plan by a good margin, proof for every improvement, state where it does not win.
All numbers measured this session (commands in the last column or in "Commands").

## Measured facts
| Fact | Number | Command / source |
|---|---|---|
| Fetch paths that exist | 1 in CBP (`cbp_v2/fetch_latest.ps1`, 76 lines) + 2 in `scripts/dev` (120 + 115 lines) + 4 one-off yt-dlp scripts in `research/*` folders | `git grep -l "yt-dlp\|yt_dlp"`, `wc -l` |
| Quote checkers | 2: `scripts/dev/verify_extract_quotes.py` (84 l), `research/krown_capture_2026-10-16/check_quotes.py` (37 l) | `wc -l` |
| Duplicated DATA today | 0 video ids shared between CBP inbox (67 files) and MTS transcript stores | loop over inbox ids, `ls` in `raw_transcripts_canonical/` and `research/*/transcripts/` printed nothing |
| Format mismatch | MTS verifier needs `> "quote"` + `Source GPS: <id> \| BEGIN\|MIDDLE\|END` and reads `raw_transcripts_canonical/<id>_raw.txt`; CBP writes `evidence: "<quote>"` (ONE quote per video) in `extractions.md` | `verify_extract_quotes.py:1-12`, `cbp_v2/extract_prompt.md` |
| MTS fetcher interface | takes video ids/URLs (`--analyst X --out DIR ID...`), no "latest N of a channel" | `fetch_captions_timed.py:1-8` |
| Consumer wiring | `queue/consumer.py` has no caller in scripts or MyTradingSys python (grep empty) | `git grep "queue/consumer\|queue.consumer"` |
| Actionable analysts | 6 of 10 enabled give levels (Rekt, Jason, Krown, Michael, Michaal, Qriptal); they hold 41 of 67 inbox files = 65% of 1,198,159 bytes | python over `analysts.json` and `inbox/` |
| CBP pending.json | last real content 2026-09-30 (krown, rejected); analyst_feed.json and dashboard updated 2026-10-22 | `ls` dates, earlier turn |

## Old plan (A) vs better plan (A2)
A = build a shared "Extraction Core" module in MTS, migrate CBP and research onto it (~5 cards, OURS).
A2 = no new module. Pick the existing MTS tools as the single copies and bend CBP to them:
1. ONE quote checker: `verify_extract_quotes.py` also accepts CBP's `evidence:` lines (or CBP emits the GPS form). Delete `check_quotes.py` and do NOT build the third copy D5 plans.
2. ONE fetcher: add `--channel @x --latest N` to `scripts/dev/fetch_captions_timed.py`; CBP's `fetch_latest.ps1` is deleted. Research one-offs are history: left alone.
3. ONE store: CBP writes into `raw_transcripts_canonical/` keyed by id (git-ignored, off the public repo); `cbp_v2/inbox` goes.
4. Signals profile is a prompt + schema in CBP repo calling those tools; the consumer is run by the coordinator on wake (no scheduler).

| Criterion | A (old) | A2 (new) | Proof / who wins |
|---|---|---|---|
| Live fetch paths | 3 -> 1 | 3 -> 1 | tie |
| Quote checkers | 2 -> 1 | 2 -> 1, third copy never built | tie on end state; A2 needs no new module |
| New code to write/own | new module + migration of 3 callers | 1 flag on an existing script + 1 regex/format branch in an existing verifier + delete 2 files | A2: fewer moving parts (counted from the facts above); cards ~3 vs ~5, both OURS and unmeasured |
| Duplicate data removed now | 0 | 0 | tie: nothing to dedupe yet (measured 0 shared ids) |
| Tokens per run | unchanged | unchanged | tie: neither plan touches the extraction prompt or model; saving needs the profile change below |
| Schedulers | 0 | 0 | tie |

Honest result: A2 wins on build size only; it does not win on dedupe or tokens. The margin is smaller than "good margin" and rests on two OURS card counts. I do not claim more.

## One real saving (measured, not part of A vs A2)
The signal profile only needs the 6 actionable analysts; running extraction on all 10 reads 1,198,159 bytes per full pass vs 783,080 for the 6 (-35%). Caveat: the 4 thesis-only analysts feed the consensus view, not signals; if the consensus page is wanted, keep them at a lower cadence. This is the only number here that moves tokens.

## Two strongest points against A2 (and against my own claim)
1. Format mismatch is real: the verifier requires GPS position tags and one quote per claim; CBP's schema has ONE quote per video. A2 step 1 is not a regex, it changes what CBP extracts (a quote per level), which raises tokens per video. That cost is NOT_IN_DATA until the A/B run: `python scripts/dev/verify_extract_quotes.py` on 3 CBP extractions rewritten in GPS form.
2. Nothing consumes the queue yet (`consumer.py` has no caller) and gate 5 (promotion backtest) keeps every CBP row from trading. All dedupe work is hygiene until a consumer run produces one acked row. The order of cards should be: consumer run first (proves any value), dedupe second.

## Recommendation (labelled RECOMMENDATION)
A2, in this order: (1) one acked row through the consumer, (2) quote-gate merge, (3) fetcher flag + store move, (4) actionable-6 profile. Stop after (1) if the row shows CBP gives no tradable signal: then the dedupe is not worth doing.

## DEFAULT (OURS)
Operator has not chosen A/A2/C or answered q-v1-cbp-routine. Default taken: file ONE card, step (2) (quote-gate merge), since it is common to A and A2 and removes a duplicate under either plan. Other steps wait for the operator's choice (PENDING OPERATOR).
