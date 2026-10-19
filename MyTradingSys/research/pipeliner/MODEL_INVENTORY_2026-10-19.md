# Model inventory and capability order, 2026-10-19 (Pipeliner)

Source: repo docs (ROUTING.md, LAYER_LAB.md, LAB_RECIPES.md, GEMINI_START.md, HOW_MTS_RUNS.md, CLOUD_ACCOUNTS.md) and the model list the Claude app shows. No benchmark exists in the repo, so the order is by model generation and tier, plus how the repo routes each model. "UNVERIFIED" means no head-to-head result is recorded anywhere.

## Accounts

| Provider | Account / plan | Where it runs | Source |
|---|---|---|---|
| Anthropic (Claude) | Login A jishu.sharma@gmail.com | JIS-NUC | CLOUD_ACCOUNTS.md |
| Anthropic (Claude) | Login B jishu.awgp | JIS-NB | CLOUD_ACCOUNTS.md |
| Anthropic (Claude) | Login C jishusharma1985@gmail.com (Max) | JIS-NB and JIS-NUC | CLOUD_ACCOUNTS.md |
| OpenAI (GPT) | Codex app, plan Plus; login not recorded | JIS-NUC (`F:\MTS\mts-codex`) | HOW_MTS_RUNS.md, LAYER_LAB.md |
| Google (Gemini) | Google AI Pro, Antigravity; NUC login not recorded | JIS-NUC (`F:\MTS\mts-gemini`) | GEMINI_START.md |
| Google (Gemini) | Google AI Pro, Antigravity; laptop jishusharma1985@gmail.com (reported 10-19, not confirmed in app) | Laptop | GEMINI_START.md |
| DeepSeek | DeepSeek chat through AIBridge; account not recorded | JIS-NB and JIS-NUC bridges (DSA) | DSA_DELEGATION.md |

The Google AI Pro menu also lists Claude Opus 5.5, Claude Sonnet 5.5 and GPT-OSS 120B. Those draw on a separate pool (pool 2 in GEMINI_START.md), not on the Anthropic logins.

## Ranking (most capable first)

| # | Model | Provider / account | Repo use today | Basis for position |
|---|---|---|---|---|
| 1 | Claude Fable 5.1 (`claude-fable-5-1`) | Anthropic (run by the operator by hand; never messaged) | none by agents | Newest generation, top tier. Operator-only. |
| 2 | Claude Opus 5.5 (`claude-opus-5-5`) | Anthropic logins A/B/C; Google AI Pro menu | operator-named judgment only (WORKERS.md rule 6) | Top tier of the current generation. |
| 3 | GPT-6.1 Sol (`gpt-6.1-sol`) | Codex Plus, NUC | critical-audit and build-review, medium effort | Newest GPT generation in the repo. UNVERIFIED against Opus. |
| 4 | GPT-6 Astra (`gpt-6-astra`) | Codex Plus, NUC | independent challenge; flagged cards only (allowance hog) | Named above Luna for challenge work. Older than Sol 6.1 by name. UNVERIFIED against Sol. |
| 5 | Gemini 4 Argon (`gemini-4-argon-low|medium|high`) | Google AI Pro, NUC and laptop | hard cards (weekly-only pool) | Top Gemini tier, per GEMINI_START.md. |
| 6 | Claude Sonnet 5.5 (`claude-sonnet-5-5`) | Anthropic A/B/C | relay builders, Pipeliner, Session_Planner | Default workhorse for judgment and build. |
| 7 | GPT-6 Luna (`gpt-6-luna`) | Codex Plus, NUC | bulk run, audit and build at low or medium | Cheapest GPT in lab routing. |
| 8 | Gemini 3.8 Flash (`gemini-3.8-flash-low|medium|high`) | Google AI Pro | routine cards, first-pass review | Default Gemini for routine work. |
| 9 | Claude Haiku 5.5 (`claude-haiku-5-5`) | Anthropic A/B/C | mechanical checks only | Cheapest Claude. |
| 10 | GPT-OSS 120B | Google AI Pro menu | none | Open-weight; not in any routing table. |
| 11 | DeepSeek chat (version not recorded, UNSOURCED) | DSA bridges | run-and-report desk rows (DSA lanes) | Version unknown; treat as a worker, not a reviewer. |
| - | Gemini 2.5 Pro | none now | named in LAB_RECIPES.md only | Not in the current Google menu (ROUTING.md C5). Do not route to it. |

## What this means for DSA

- DSA is a DeepSeek worker: it runs commands and reports. It is not the reviewer for its own output.
- Review of DSA output: a Claude Sonnet 5.5 spot check (DSA_DELEGATION.md), which is the existing rule.
- Comparing Haiku with Sonnet on Pipeliner: rows 6 and 9 above are the pair to test. Judge the drain decisions, not the sweep counts.
