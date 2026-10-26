# GPT guide for CBP work (Lead, 2026-10-27)
Sources read this turn: research/cbp/CBP_STATUS_2026-10-25.md, v1_plan_2026-10-20/D5_CBP_MODULE.md, system/ROUTING.md:41-43, system/CODEX_START.md.

## What CBP is now
CBP (Crypto Bike Plan) fetches analyst videos, extracts claims with one quote each, stores rows in `cbp_store/rows.json` (CBP repo `F:/CryptoScrapper`, JIS-NB disk). MTS runs it (`scripts/dev/cbp_run.py --due|--force`) and layers read it with `cbp.query(analyst, symbol, since_days=5)`. The queue, consumer and adapter are deleted. Rows are claims, not signals; nothing trades before gate 5 (B139 backtest promotion).

## GPT's job (ROUTING.md:41-43): checker and re-deriver, never the producer
Claude extracts, so GPT is the independent second vendor. Three things only:
1. Recount: re-derive numbers from the raw rows and prices yourself; never copy a figure from the producer's file.
2. Quote check: every claim's quote must be verbatim in `raw_transcripts_canonical/<id>_raw.txt` (`scripts/dev/verify_extract_quotes.py`); report each failure with file:line.
3. Gate review: try to break gates 1-5 (schema, quote, freshness, scorecard, promotion) with a planted bad row; report what slipped through.

## GPT does NOT
- Fetch YouTube (429; all YouTube work is Gemini on the NUC, operator 2026-10-25).
- Touch the CBP repo, the live tree, `.secrets/`, orders, or schedulers. Testnet only.
- Commit rows, transcripts or store files (repo is public); results are counts and file:line only.
- Give a verdict on an analyst without 56 scored calls (D5 gate 4).

## How
Cards below, lane CODEX, `codex_run.py` one at a time. Data lives on JIS-NB, so Codex reads a pack file outside the repo (`codex_pack.py <card>`), per CODEX_START.md "Pack file bridge". Label every parameter SOURCED (quote + file:line) or OURS. GPT lane is DOWN on credits (lane_health.py, since 2026-10-25); cards wait for it only if `--crucial`, else they move to DSA/Claude.
