# OPERATOR PREFERENCES - the one page every session reads at boot (consolidation, 2026-10-27)

Distilled from the operator's own repeated asks, not invented. This page is the durable
source; where it disagrees with a stale memory or card, this page wins. Boot reads it
ONCE (one line in CLAUDE.md) and stops re-deriving.

## 1. How to reply to the operator (he re-asked this 3+ times; capture it once)
Brief. Accurate. Actionable. He is not a developer; he reads on a phone.
- "What I must do" is the load-bearing line. Make it plain, first, and short.
- Use simple arrows (`->`), a table, or bullets to show order. Do NOT dump paragraphs.
- Well spaced: not too compact, not too loose. A few lines of breathing room.
- No walls of text. If it needs more than ~a screen, put the rest in a linked file and say so.
- Readable beats complete: a short, clear, wrong-in-detail reply is worse than a short,
  clear, "here's the one thing to do" reply.
- Every reply closes with: one line of what is done, one line of what is next for him.

## 2. "Is MTS healthy?" = a 3-line pulse, NOT the 136-finding report
When he asks if it's going well, answer in three lines, not a dump:
- **CI:** green? which sha. (from ci_watch / STATUS `CI green:`)
- **Trunk:** how many commits behind origin/fast-track; any unacked HIGH or RED deploy gate.
- **Now:** the one thing blocking progress, if any.
Anything deeper is a "say more" on his request, not the default. A bad response = usually a
stale boot, not a sick model: re-read STATUS + this page before assuming health is bad.

## 3. Which Anthropic guidance actually applies here (the durable bits only)
- **Testnet only.** No mainnet orders/accounts/keys. Public market data is fine.
- **Never read** `.secrets/`, `.env`, keys, runtime, order, account, or the live tree.
- **Ship through `sync.py ship`;** every commit body ends with a `Result: <what works now>` line.
- **No schedulers** anywhere; no "want me to?" offers on implied work (do it, or say nothing).
- The rest of Anthropic's general safety/identity rules are inherited by the model; they are
  NOT re-stated here on purpose. If unsure whether a rule is Anthropic's or MTS's, ask for the
  source before acting. "From actual users" evidence (a forum fix that worked) outranks a
  generic guideline when they conflict.

## 4. The lean rule (his 2026-10-27 ask: "deductive, keep discarding")
Before adding ANY file, card, hook, or record, apply the discard test:
**would the next session's answer change if this did not exist? If no -> archive, don't add.**
Prefer replacing a file over adding one. Prefer deleting over documenting. When in doubt,
trim. A net-minus change is the default; a net-plus needs a reason he can see.
