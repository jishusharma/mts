# API credit spend list (about 16 USD, expires 2026-11-17)

Haiku jobs, read-only, sum of caps 14 USD. NOT launched: launching spends the operator's credit and needs his go-ahead. DECISION (OURS): model is claude-haiku-5-5 because api_job.py MODEL_NAMES has no claude-haiku-4-5 (argparse rejects it). DECISION (OURS): commands omit --card: with --card the launcher ignores the prompt file, review ids have no task card, and the real cards' briefs are refused by the secret-path check; card id column is the slug and source card.

| # | card id | prompt file | cap USD | command |
|---|---|---|---|---|
| 1 | gpt-rederive-fabio-cvd-1108 | MyTradingSys/system/api_prompts/gpt-rederive-fabio-cvd.md | 3 | `python scripts/dev/api_job.py launch gpt-rederive-fabio-cvd-1108 --prompt-file MyTradingSys/system/api_prompts/gpt-rederive-fabio-cvd.md --model claude-haiku-5-5 --max-usd 3` |
| 2 | gpt-rederive-pre-us-failed-break-10sym-1108 | MyTradingSys/system/api_prompts/gpt-rederive-pre-us-failed-break.md | 3 | `python scripts/dev/api_job.py launch gpt-rederive-pre-us-failed-break-10sym-1108 --prompt-file MyTradingSys/system/api_prompts/gpt-rederive-pre-us-failed-break.md --model claude-haiku-5-5 --max-usd 3` |
| 3 | gpt-rederive-v-recovery-low-sweep-1108 | MyTradingSys/system/api_prompts/gpt-rederive-v-recovery-low-sweep.md | 3 | `python scripts/dev/api_job.py launch gpt-rederive-v-recovery-low-sweep-1108 --prompt-file MyTradingSys/system/api_prompts/gpt-rederive-v-recovery-low-sweep.md --model claude-haiku-5-5 --max-usd 3` |
| 4 | review-net-rr-floor-1111 | MyTradingSys/system/api_prompts/review-net-rr-floor.md | 2.5 | `python scripts/dev/api_job.py launch review-net-rr-floor-1111 --prompt-file MyTradingSys/system/api_prompts/review-net-rr-floor.md --model claude-haiku-5-5 --max-usd 2.5` |
| 5 | review-feed-watchdog-1111 | MyTradingSys/system/api_prompts/review-feed-watchdog.md | 2.5 | `python scripts/dev/api_job.py launch review-feed-watchdog-1111 --prompt-file MyTradingSys/system/api_prompts/review-feed-watchdog.md --model claude-haiku-5-5 --max-usd 2.5` |
