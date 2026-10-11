# T068 - P3: OI arm rerun of T063 when n>=30 per arm

Opened 2026-10-06 by MTS-2026-10-06-1254Z-APP-ANA-research-agenda. Status QUEUED. Source: research agenda follow-up.

## Scope

Rerun T063 "Stop-run OI flush signature" analysis once OI data sufficient:
- **Trigger:** oi_5m recorder gap-free (sufficient 30-day history per arm)
- **Earliest:** late October 2026
- **Owner:** Desktop (Jis)
- **Dependency:** T063 original study; oi_live/oi_5m_30d.csv populated

## Rationale

P1 research established passive order execution costs are negligible (+0.02 bp). T063 OI flush signature is a candidate setup trigger once OI arm has enough history (30 min bars × 30 days = robust quantile thresholds).

## Deliverable

Rerun report: mean adverse selection / stop-run effectiveness per OI arm (buy, sell, neutral).
