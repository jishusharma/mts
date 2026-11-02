# Console API jobs for login C (JIS-NB holds the key)

Standing order: OPERATOR_DECISIONS.md 2026-11-02. Keep about 10 USD unspent. Credit expires 2026-11-17 UTC.

1. Put the key into the process env only, as the standing order says. Never print or commit it.
2. Dry-run, then submit each file by dropping `--dry-run`:

       python scripts/dev/api_batch.py submit MyTradingSys/research/api_jobs_2026-11-02/bridge_review_opus.jsonl --max-usd 2 --model claude-opus-5-5 --max-tokens 32000 --dry-run
       python scripts/dev/api_batch.py submit MyTradingSys/research/api_jobs_2026-11-02/ready_cards_haiku.jsonl --max-usd 2 --model claude-haiku-5-5 --max-tokens 1024 --dry-run

   Dry-runs on JIS-NUC: 1.01 and 0.13 USD worst case.
3. `status <id>`, then `fetch <id> --out MyTradingSys/research/api_jobs_2026-11-02/<name>_results.jsonl`.
4. `sync.py ship` the results and broadcast the sha to B. B reads them and sends the bridge findings to the bridge owner.

If nobody on login C can run this, reply to B with who can.
