# Model economics check, 2026-10-21

Question (operator): what do the latest real sources say about the Claude models we use, how to use them
effectively and economically, and what should MTS change? Every claim below has a source; vendor numbers are
marked VENDOR, independent ones INDEPENDENT. Nothing here is our own measurement except the WORKERS.md lines quoted.

## 1. What changed since our rules were written

| Model | Released | Input / output per 1M tokens | Cache read | Source |
|---|---|---|---|---|
| Fable 5.1 | 2026-09-01 | $10 / $50 | $0.25 | anthropic.com/claude-fable-and-mythos-5-1 |
| Opus 5.5 | 2026-09-22 | $4 / $20 (Opus 5 was $5 / $25) | $0.20 | anthropic.com/claude-opus-5-5 |
| Sonnet 5.5 | 2026-09-28 | $2 / $10 | $0.10 (cut 50% on 2026-10-07) | anthropic.com/claude-sonnet-5-5, /claude-haiku-5-5 |
| Haiku 5.5 | 2026-10-07 | $0.10 / $0.50 up to 100k prompt; $0.50 / $2.50 above | $0.01 | anthropic.com/claude-haiku-5-5 |

Price ratios now: Opus = 2x Sonnet; Sonnet = 20x Haiku (inside 100k). Haiku costs 4x more past a 100k prompt.

## 2. What the sources say

1. **Haiku 5.5 is for narrow work** (VENDOR, Haiku page): built for "high-volume, cost-sensitive tasks" (summaries,
   compaction, queries, classification); "Sonnet 5.5 and Opus 5.5 remain better choices for complex agentic coding";
   pairs well "as a subagent". Terminal-Bench 4.0: Haiku 39.2%, Sonnet 70.6%. OSWorld 2.1: 72.4% vs 83.9%.
   Independent index (Artificial Analysis, via felloai.com): Opus 58, Sonnet 56, Haiku 43.
2. **Opus 5.5 is cheaper per task than it looks** (VENDOR + customer claims, Opus page): 40% cheaper than Opus 5
   at default (medium) effort; default effort beats Opus 5 at max effort on Terminal-Bench for about a fifth of
   the cost; Rogo: lowest effort beat Opus 5 high with ~60% fewer output tokens.
3. **Judge by cost per completed task, not per-token price; build your own eval suite and rerun it when models
   ship; a larger model at lower effort may beat a smaller one at higher effort; Opus plans, Sonnet executes**
   (VENDOR, Anthropic webinar "Building with the Claude 5.5 family").
4. **Claude Code cost docs** (VENDOR, code.claude.com/docs/en/costs): Sonnet for most coding, Opus for complex
   architecture/multi-step reasoning, `model: haiku` for simple subagents; clear between tasks; CLAUDE.md under
   200 lines; idle cross-session messages, goal check-ins and scheduled tasks each resend the full context
   (`crossSessionInbound: hold` stops that); agent teams use ~7x tokens; first message after the cache lifetime
   reprocesses everything; `/usage` now shows cache hit share and its likely miss cause.
5. **Long context makes answers less reliable** (INDEPENDENT, Chroma "Context Rot", 2025-07-14, 18 models):
   reliability drops as input grows, worst when the needed fact is in the middle and near-miss distractors exist.
   Older models; direction is what matters for us.
6. **Cheap-first routing works only with a check and an escalation** (INDEPENDENT, peer-reviewed/preprint):
   SWE-Router (ICML 2026, arXiv 2607.00053): the prompt alone cannot tell task difficulty; watching the cheap
   model's first 2 turns predicts escalation far better (Route-AUC 0.780 vs 0.476 for prompt-only routers), and
   the routed mix sometimes beat always-strong. Triage (arXiv 2604.07494): send a task to the cheapest tier whose
   output passes the same verification gate, re-run on the heavy tier when it fails; it pays only when the light
   tier's pass rate exceeds the cost ratio. (Exact savings not visible in what I could read.)

## 3. MTS against the evidence

| # | Our rule now | Evidence | Gap | Proposed change |
|---|---|---|---|---|
| A | Admin_Guy (rule, role, state questions) runs on **Haiku 5.5 high** (START_HERE.txt; roster) | 2.1: Haiku for narrow work, not multi-file judgment; our bug-haiku-stale-rule-answers is 2 real misses | Rule answers need reading several files and judging which is current | Admin_Guy on **Sonnet 5.5 low/medium**; Haiku stays for its lookups as a subagent. Cost: ~20x per token, but Admin_Guy turns are few |
| B | Opus is "the tight exception" because it used 2.5x tokens per ship (WORKERS.md lines 13, 39-43) | 2.2-2.3: Opus 5.5 at 2x price and lower token use; judge cost per completed task | Our 1,970k vs 802k eq figure predates Opus 5.5 / Sonnet 5.5 and ignores the price ratio | Re-measure eq per ship on the 5.5 models (turn_meter / ship log), with prices applied, before changing the rule. Try Opus 5.5 at **low** effort for design cards |
| C | WORKERS.md "eq" applies no price ratios (line 4) | 2.3 cost per completed task | We can't compare models in dollars | Add a price column per model (table in section 1) to the eq report |
| D | Rule 3a: scoped work to Haiku Agents + spot-check one claim | 2.6 Triage/SWE-Router: cheap-first needs a verification gate and an escalation | Spot-check exists; automatic escalation does not | Brief adds a done check the Agent must pass; a failed check re-runs the card on Sonnet (no second Haiku try) |
| E | Haiku briefs can grow past 100k context | 2.1 Haiku price x5 past 100k | Silent price jump | Haiku Agents: hand back at 100k context |
| F | Turn meter hands over by context size (rule 5) | 2.4 cost of long context; 2.5 context rot | None - evidence supports it | Keep |
| G | Coordinators message idle sessions often | 2.4 each idle delivery resends full context | Unmeasured cost | Measure with `/usage` attribution; consider `crossSessionInbound: hold` for idle workers |
| H | No eval suite of our own tasks per model | 2.3 build and rerun one | We pick models by doctrine | A 10-task MTS eval (rule answer, bug fix, card refine, chart read) run on each new model; results in the trial ledger |

## 4. Recommendation

Do A now (it is the open high-priority bug and the evidence points the same way). Do B, C and H together as one
measured card: re-run the eq-per-ship numbers on the 5.5 models with prices applied, then decide the Opus rule
from that number, not from the old one. D and E are small brief/rule edits.

## Sources
- https://www.anthropic.com/claude-haiku-5-5
- https://www.anthropic.com/claude-sonnet-5-5
- https://www.anthropic.com/claude-opus-5-5
- https://www.anthropic.com/claude-fable-and-mythos-5-1
- https://claude.com/resources/webinars/building-with-the-claude-5-5-family-choosing-the-right-model-and-getting-more-from-every-token
- https://code.claude.com/docs/en/costs
- https://research.trychroma.com/context-rot
- https://www.alphaxiv.org/abs/2607.00053 (SWE-Router, ICML 2026)
- https://arxiv.org/abs/2604.07494 (Triage)
- https://felloai.com/ultimate-claude-model-comparison/ (Artificial Analysis index, secondary)
