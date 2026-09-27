# Step 6 (Multi-Account) — Deliberately Not Built Yet

**Why:** Step 6's own exit criterion is "two plans running simultaneously in two subaccounts, isolated." That can't be validated — or even meaningfully designed against — until Steps 1–5 have run at least once against a real testnet order book. Writing an account-registry abstraction now would be designing against assumptions (does `cancel_all_by_label` actually scope per-account cleanly? does a resting stop survive a disconnect the way the docs imply?) that are currently unverified guesses, not facts. That's the same failure mode this project just filed as B071 in miniature: building on top of an unconfirmed belief.

**What exists today that Step 6 will build on:**
- `deribit_orders.py` functions already take no account-scoping assumption baked in — each call uses whatever `token` (from `authenticate()`) is passed in. A multi-account registry is mechanically "one secret file + one token per subaccount," which the current functions already support without modification.
- `journal.py` keys everything by `plan_id`, not by account — multiple accounts' plans already won't collide in the journal as long as `plan_id` stays unique across accounts (worth an explicit naming convention, e.g. `<account>_<date>_<seq>`, when Step 6 starts).

**What Step 6 actually needs to answer (deferred to Opus, after testnet proves Steps 1–5):**
1. Account registry format — one secret file per subaccount under `.secrets/`? A single JSON mapping account name → credentials?
2. Per-account caps — same `trade_plan_schema.json` caps fields, or an account-level ceiling that trade-plan caps must stay under?
3. What "test what cancel-on-disconnect does to a resting stop first" (from the original handoff) actually showed — this is an empirical finding Step 1's testnet run needs to produce, not something to design around in the abstract.

**Recommendation:** Leave Step 6 as this note until Step 1 has a completed testnet run in hand. Don't let its absence block anything — Steps 1–5 are single-account by design and don't need Step 6 to be useful.
