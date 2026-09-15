# CRYPTO ADAPTATIONS
# Date: 2026-08-06
# Purpose: Single file for all crypto-specific additions.
#   → Every adaptation tagged: "Tom rule" OR "Crypto hack"
#   → Every crypto hack has validation status
#   → Tom rules always take priority over crypto hacks

---

## PRINCIPLE

Tom trades DAX futures. We trade crypto perps. Some things transfer directly. Some need adaptation. Some are entirely new.

This file exists so we never confuse "what Tom said" with "what we added."

---

## TOM RULES (Directly Transferable)

These require zero adaptation. They work identically in crypto.

| # | Rule | Source | Crypto Notes |
|---|------|--------|--------------|
| 1 | Volume Profile (VAH, VAL, VPOC) | All VP videos | [OK] Identical. CoinGlass shows VP. |
| 2 | VWAP models | 43JaKHRvxHk, VumVuGnCcFM | [OK] Identical. CoinGlass shows VWAP. |
| 3 | CVD / Delta | y67l86cSqb8 | [OK] Identical. CoinGlass shows CVD. |
| 4 | Weekly profiles mandatory | Ld1dhjGdTCA, 9eHZMVXilgc | [OK] Identical. Use weekly VP. |
| 5 | IDEA + PROOF two-step | NkQeOVDTAec | [OK] Identical. |
| 6 | Entry on pullback after proof | NkQeOVDTAec, BVpYGKz9PBU | [OK] Identical. |
| 7 | Target = next structural level | All VP videos | [OK] Identical. |
| 8 | Counter-trade zone = prior day VAH/VAL/VPOC | BVpYGKz9PBU | [OK] Identical. Use prior day VP. |
| 9 | Structural invalidation stops | BVpYGKz9PBU, kXhIAug0Gh8 | [OK] Identical. |
| 10 | Fixed monetary risk | zQTbdEweG3c, BVpYGKz9PBU | [OK] Identical. Use USD instead of €. |
| 11 | 200-300 trades for key figures | BVpYGKz9PBU | [OK] Identical. |
| 12 | News filter mandatory | Ld1dhjGdTCA | [OK] Identical. Check crypto news. |
| 13 | Per-strategy journaling mandatory | Ld1dhjGdTCA | [OK] Identical. |

---

## CRYPTO HACKS (Our Additions — Flagged)

These are NOT from Tom. They are crypto-specific additions. Each has a validation status.

| # | Hack | Status | Evidence | Notes |
|---|------|--------|----------|-------|
| 1 | **Aggregated CVD** (Binance+Bybit+OKX) | [WARN] UNVALIDATED | Tom said "aggregated CVD" but we don't know if he meant these 3 exchanges | Better than single-exchange but threshold untested |
| 2 | **Funding rate** as context | [WARN] UNVALIDATED | Tom NEVER mentions funding | May indicate directional bias. No backtest. |
| 3 | **Liquidation clusters** as squeeze risk | [WARN] UNVALIDATED | Tom NEVER mentions liquidations | Intuitive but unproven. Threshold ($100M) arbitrary. |
| 4 | **OI delta** for confirmation | [WARN] UNVALIDATED | Tom NEVER mentions OI | Our addition from crypto trader community. |
| 5 | **UTC 00:00 as "daily open"** | [WARN] UNVALIDATED | DAX has 08:00 CET open. Crypto is 24/7. | Our convention. No validation. |
| 6 | **Funding reset times** (00:00/08:00/16:00 UTC) | [WARN] UNVALIDATED | Tom never mentions funding resets | Our convention from crypto market structure. |
| 7 | **Perpetual swaps** vs futures | [OK] VALIDATED | Standard crypto instrument | Functionally identical to futures for our purposes. |
| 8 | **CoinGlass as primary source** | [OK] VALIDATED | Aggregates multiple exchanges | Better than single exchange for crypto. |
| 9 | **Slippage buffer** (Net R:R = theoretical × 0.75) | [WARN] UNVALIDATED | Added after 5-LLM research | Conservative estimate. No live data. |
| 10 | **Correlation-adjusted risk** (ρ>0.7 = shared exposure) | [WARN] UNVALIDATED | Added after 5-LLM research | Mathematically sound but untested live. |

---

## REJECTED CRYPTO HACKS

These were considered and rejected.

| # | Hack | Why Rejected | Date |
|---|------|-------------|------|
| 1 | Funding rate boost in scoring | 52-55% accuracy = barely above random. Removed. | 2026-08-04 |
| 2 | 70/30 Value Area coverage claim | Misattributed. Removed. | 2026-08-04 |
| 3 | FVG as core setup | Zero empirical backing. S03 deprecated. | 2026-08-04 |
| 4 | ORB as standalone setup | Unsupported by Tom. Merged then discarded. | 2026-08-04 |

---

## VALIDATION ROADMAP

| Priority | Hack | How to Validate | Target Date |
|----------|------|-----------------|-------------|
| 1 | Liquidation cluster threshold | Backtest: does $100M cluster at support = squeeze? | After S02 live |
| 2 | Funding rate context | Track funding at zone vs outcome for 50+ trades | After S02 live |
| 3 | OI delta confirmation | Track OI change at entry vs outcome for 50+ trades | After S02 live |
| 4 | Aggregated CVD thresholds | Compare single-exchange vs aggregated CVD accuracy | After S02 live |
| 5 | UTC 00:00 open | Compare UTC 00:00 vs exchange-specific daily VP accuracy | After S02 live |

---

## RULE: TOM ALWAYS WINS

If a Tom rule and a crypto hack conflict:
- **Tom rule wins. Always.**
- Crypto hack is noted as "overridden by Tom rule [X]"
- No exceptions.

Example:
- Crypto hack says: "Elevated funding at support = don't long"
- Tom rule says: "Zone + proof = entry"
- Result: Enter per Tom rule. Note funding as context only.
