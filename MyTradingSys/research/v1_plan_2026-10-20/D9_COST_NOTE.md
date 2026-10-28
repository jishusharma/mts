# D9. Cost note: which subscriptions and credits serve the roadmap

Rule from the handoff: measure before spending; expiring credits are not by themselves a reason to use them. Plan tiers of
logins A and B are UNVERIFIED on disk (CLOUD_ACCOUNTS.md lists the logins, not the plans); C is Max.

| Resource | Serves | Keep / drop | Reason |
|---|---|---|---|
| Claude Max, login C (jishusharma1985, NB + NUC) | coordinator and S2/S3/S5 workers | keep | the roadmap runs on Claude Code; D7 needs at most 3 workers + 1 coordinator |
| Claude logins A and B | second and third worker when C is in reset | keep one as overflow; the operator picks which (B is the least used on the traffic inventory) | "any account on any machine" needs two logins, not three; the fourth account the operator plans can replace the dropped one |
| Codex Plus (5-h window + weekly cap, LAYER_LAB.md line 75) | S3 lab runs, cross-vendor review of gate diffs (rule 11) | keep while the lab queue is <= 8 and T06/T09 run there | prepaid; a second vendor reading the backtest base is worth more than a third Claude login |
| Google AI Pro (Gemini; GEMINI_START.md) | blind image reads, the gap audit | drop candidate at renewal | its one distinct use (image blind-read) is not on the v1 path; its audit was T0-only and unreviewed |
| DeepSeek via AIBridge | DSA rows | retire unless the queue drains in S0 | rows 93 h stale; the AIBridge install row itself is pending |
| Cloud credits 100 USD (expire 2026-11-05 13:29 IST, holder UNSOURCED) | S1 independent reviews of the spec and the schema; S4 golden-set runs | use only for those; what is unused expires | expiring is not a reason; reviews are |
| AWS Bedrock credits (expire 2026-10-25) | Tom transcript extraction pilot | let expire unless the operator has 2 free hours before 10-25 | Tom v2 is third in line; a pilot nobody consumes is spend |

Net: two Claude logins, Codex, and the operator. Three paid vendors become two. The measure that justifies any addition is
a stage with a bottleneck on the weekly read (D7), not a credit balance.
