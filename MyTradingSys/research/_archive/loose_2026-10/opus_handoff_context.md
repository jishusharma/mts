# Handoff to Opus 5.5: Step 2 Design + System Clarifications

**Date:** 2026-09-27 00:45 IST  
**From:** Haiku 4.5 (Research & Prep)  
**To:** Opus 5.5 (Design & Decision-Making)  
**Session:** claude-sonnet-5-2026-09-26 → ongoing

---

## Context Summary

**Goal:** Build MTS's exchange API execution layer (Deribit, BTC perpetuals) with testnet validation before mainnet gate.

**Current State:**
- T048 (satellite framework) freeze lifted; T050 (Deribit execution) opened as first slice
- T049 (NUC worker v2) live and restart-proven
- B071 (fail-open proof-direction bug) filed; blocks mainnet
- T051 (backtest) parked by operator; resumes after execution layer proves
- Phase 5 (rule tagging) awaiting four-step proof application

**Model Guidance (from original handoff):**
- Haiku: docs, ledger, scripts
- Sonnet: steps 1, 3–6 (Deribit session, compiler, executor, reconciliation, multi-account)
- Opus: steps 2, 7, 8 (trade-plan spec design, satellites/clusters design, mainnet gate review)

---

## Your Job Now: Step 2 (Trade-Plan Spec Design)

### Requirements
A **trade-plan JSON file format** that captures:
- **Account** (which Deribit subaccount to use)
- **Instrument** (BTC-PERPETUAL)
- **Side** (LONG / SHORT)
- **Validity Window** (start, end timestamps; or duration)
- **Entry Strategy:**
  - Market order (single market buy/sell)
  - Single limit (one limit order at fixed price)
  - Laddered range (N rungs across a price range)
- **Size Definition:**
  - Base unit (e.g., 10 BTC contracts)
  - Multiplier list per rung (e.g., [1, 1, 2, 3] for 4-rung ladder)
- **Stop Rule** (TBD by you: fixed %-below, trailing, or custom)
- **Profit Targets** (e.g., ["50% at +2%", "50% at +5%"])
- **Caps & Limits:**
  - Max notional per trade
  - Max loss (halt if realized loss exceeds)
  - Max concurrent orders
- **Operator Approval** (auto-exec within caps, or manual approval gate?)

### Deliverables
1. **JSON Schema** (`execution/trade_plan_schema.json`)
   - All fields, data types, constraints, examples
2. **Validator** (`execution/trade_plan_validator.py`)
   - Rejects plans that would exceed caps
   - Validates entry strategy syntax
   - Checks timestamp logic
3. **Examples:**
   - 5 valid plans (varying entry types, stops, targets)
   - 3 invalid plans (cap violations, malformed, etc.)
4. **Exit Criteria:**
   - All 5 valid plans pass validation
   - All 3 invalid plans are rejected (with reason)

### Design Decisions (You Decide)

These **must** be decided before schema is final:

| Question | Impact | Example Options |
|----------|--------|------------------|
| **Max Notional?** | Cap field in schema | $10K, $50K, $100K per trade? |
| **Max Loss?** | Hard halt trigger | -$500, -$1K, -5% of equity? |
| **Stop Rule?** | Stop field format | Fixed % below entry? Trailing? Breakeven after N fills? |
| **Targets Format?** | Target array schema | `["50% at +2%", "30% at +5%", "20% TP"]`? Or JSON object? |
| **Concurrent Order Limit?** | Cap field | Max 10? 20? (for ladder + stop) |
| **Operator Approval?** | Executor behavior | Auto-exec all caps-compliant plans? Or require manual YES for each? |
| **Time Zones?** | Validity window | ISO-8601 UTC? Operator's local IST? |

**Recommendation:** Start conservative (e.g., $10K max notional, -$500 max loss, 10 concurrent orders max). Can loosen after phase 4 (reconciliation) proves stable.

---

## Deribit API Context (Haiku's Research)

See `deribit_api_research.md` (attached). Key points:

- **Authentication:** OAuth2 client_credentials via `/public/auth`; token refresh on error 13009
- **Order Placement:** WebSocket `private/buy` / `private/sell` preferred (lower latency)
- **Order States:** open → (partial fills tracked) → filled/rejected/cancelled
- **Partial Fills:** Must query order by ID to get cumulative `filled_amount`
- **Errors:** 10002 (funds) = STOP, 10028 (rate limit) = RETRY, 13009 (token) = REFRESH
- **Reconciliation:** Query `/private/get_account_summary` + `/private/get_position` + `/private/get_open_orders`

---

## Dependency Chain (Visual)

```
Step 2: Trade-Plan Spec (Opus)
    ↓ (schema + validator)
Step 3: Plan Compiler (Sonnet) — convert plan to order list
    ↓ (compiled order list)
Step 4: Executor (Sonnet build, Opus review) — send orders, track fills
    ↓ (order states + fills)
Step 5: Reconciliation (Sonnet) — compare MTS belief to Deribit actual
    ↓ (reconciled state)
Step 6: Multi-Account (Sonnet) — scale to 2+ subaccounts
    ↓ (tested multi-account)
Step 7: Satellites (Opus design, Sonnet build) — linked positions, governance
    ↓ (satellite framework)
Step 8: Mainnet Gate (Opus review) — final safety check before go-live

Step 1: Session Client (Sonnet, spawn now) — parallel; done independently
    ↓ (persistent WebSocket + order wraps)
    → Ready for steps 3–6 to use
```

**Blocker Alert:** B071 (fail-open proof-direction bug) must be fixed before mainnet gate. Currently execution can send good plans but receive bad signals.

---

## What Happens After Step 2

1. **You (Opus) deliver:** Schema JSON, validator Python, 8 example files
2. **I (Haiku) test:** Run validator on examples, confirm 5 pass + 3 fail
3. **Sonnet builder:** Uses schema to build Step 3 (plan → order list) + Step 4 (executor)
4. **You (Opus) review:** Step 4 code before it touches testnet
5. **Operator (Jishu):** Creates testnet account, generates API key, runs deribit_client.py + deribit_read.py
6. **Sonnet or Haiku:** Step 1 (session client) runs; places test orders on testnet
7. **Sonnet:** Step 3 (compiler) validated with hand-calc examples
8. **Sonnet:** Step 4 (executor) runs on testnet; places ladder, tracks fills
9. **Sonnet:** Step 5 (reconciliation) tested with forced mismatch
10. **Sonnet:** Step 6 (multi-account) scales to 2 subaccounts
11. **You (Opus):** Step 7 design (satellites)
12. **You (Opus):** Step 8 mainnet review (B071 fixed, governance numbers set, testnet passed)
13. **Operator:** Go-live on mainnet with minimum position

---

## Clarification Questions for You (Opus)

Before you design, confirm:

1. **Conservative defaults OK?** (Max notional = $10K, max loss = -$500, concurrent = 10 max)
   - Or do you want different starting numbers?

2. **Stop rule preference?**
   - Fixed % below entry? (e.g., "entry - 2%")
   - Trailing stop? (e.g., "max price seen - 1%")
   - Breakeven after N fills? (e.g., "at break-even if ≥2 fills")
   - Custom JSON format? (e.g., `{"type": "fixed_percent", "percent": 2}`)

3. **Operator approval model?**
   - Auto-execute all plans that pass validation?
   - Or require operator to click "EXECUTE" on each plan?
   - This affects Step 4 (executor) behavior

4. **Target format preference?**
   - Simple string list: `["50% at +2%", "50% at +5%"]`
   - JSON object: `[{"amount_percent": 50, "pnl_percent": 2}, ...]`
   - Something else?

5. **Validity window format?**
   - ISO-8601 timestamps? (e.g., "2026-09-27T10:00:00Z")
   - Operator's IST timezone?
   - Relative (duration from now)? (e.g., "valid_for_seconds": 3600)

6. **Should the schema include MTS signal metadata?**
   - E.g., which rule/condition triggered this plan?
   - Or keep trade-plan decoupled from signal source?

---

## Files You'll Need

- `deribit_api_research.md` — All API details, error codes, partial fill handling
- Reference: Operator will provide (testnet setup):
  - Deribit testnet account
  - API key pair (trade permission only)
  - Placeholder max notional number (your starting default)

---

## Timeline

- **Now:** Opus designs schema + validator + examples
- **Today (in parallel):** Sonnet builds Step 1 (session client) + Haiku tests step 2 validator
- **Today/Tomorrow:** Operator does testnet setup (deribit_client.py test)
- **Next:** Step 3 (compiler) design + Step 4 (executor) build
- **Target:** All steps 1–6 testnet-proven within 2–3 sessions

---

## Session State Handoff

**What's Done:**
✅ T051 + B071 filed (items/INDEX.md.new staged)
✅ Deribit API research compiled
✅ Edge cases + error handling documented

**What's Ready for You:**
✅ deribit_api_research.md (all technical details)
✅ Clarification questions above (your decisions to make)
✅ Dependency chain (sequencing is clear)

**What's Waiting:**
⏳ Your schema design (step 2)
⏳ Operator's testnet setup + API key
⏳ Sonnet builder for step 1 + steps 3–4 after your schema

---

**You're ready to start. What questions do you have on the trade-plan design?**
