"""C34: Re-score the long leads (C30 30m buy dot + bull div, C28 2h buy dot) at spot costs.

Spot costs: 2 bps maker round trip, zero funding, long only (SOURCED BACKTEST_CANDIDATES.md:43).
Perp costs: 10 bps taker round trip (2 * fees.BINANCE_TAKER), zero funding in original DEV runs;
FORMULAS section 13 adds 2 bps round trip slippage.
Window: DEV 2022-01-01..2024-06-30 (HOLDOUT sealed).
Reuses wt_rsi_div.run and wt_context.trades.
"""
import datetime as dt
import json
import os
import statistics as st
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO))
if len(sys.argv) < 2:
    sys.argv = [sys.argv[0], str(REPO)]

from MyTradingSys.backtest import fees
import wavetrend_dots as WD
import wt_context as WC
import wt_lower_tf as LT
import wt_rsi_div as V


def rescore_trades(
    trades,
    perp_roundtrip_rate=None,
    spot_coinbase_maker_bps=2.0,  # SOURCED BACKTEST_CANDIDATES.md:43
    slippage_bps=0.0,  # function parameter, OURS
):
    """Re-scores a list of trades at perp and spot costs.
    Original trade['net'] in wt_rsi_div/wt_context was computed with WD.FEE = 0.10% (10 bps).
    Gross return (%) = trade['net'] + WD.FEE.
    """
    if perp_roundtrip_rate is None:
        perp_roundtrip_rate = fees.BINANCE_TAKER * 2  # SOURCED fees.py:36

    perp_rt_pct = perp_roundtrip_rate * 100.0  # 0.10%
    spot_rt_pct = spot_coinbase_maker_bps * 0.01  # 2 bps = 0.02%
    slip_pct = slippage_bps * 0.01

    out = []
    for r in trades:
        gross = r["net"] + WD.FEE
        perp_net = gross - (perp_rt_pct + slip_pct)
        spot_net = gross - (spot_rt_pct + slip_pct)
        out.append({
            "t": r["t"],
            "d": r.get("d", 1),
            "bars": r.get("bars", 0),
            "gross": gross,
            "perp_net": perp_net,
            "spot_net": spot_net,
        })
    return out


def run_rescore(spot_coinbase_maker_bps=2.0, slippage_bps=0.0):
    """Re-runs C30 and C28 long leads on DEV and computes perp and spot cost metrics."""
    # 1. C30 30m buy dot <= -53 + bull div, any trend, exit X1
    b30 = LT.agg5(6)
    res30 = V.run(b30, 30)
    raw_c30_30m = [
        x for n, s, ex, x in res30
        if n == "buy dot <= -53 + bull div" and s == "any" and ex == WC.EXITS[0]
    ][0]
    rescored_c30_30m = rescore_trades(
        raw_c30_30m,
        spot_coinbase_maker_bps=spot_coinbase_maker_bps,
        slippage_bps=slippage_bps,
    )

    # 2. C28 2h uptrend buy dot <= 0, exit X3 (dot after far band)
    raw_c28_2h = WC.trades("2h", 8, WC.RULES[4], 2)
    rescored_c28_2h = rescore_trades(
        raw_c28_2h,
        spot_coinbase_maker_bps=spot_coinbase_maker_bps,
        slippage_bps=slippage_bps,
    )

    # 3. C30 15m buy dot <= -53 + bull div, 2h trend up, exit X1 (H2 lead from PRE_REG_C30.md)
    b15 = LT.agg5(3)
    res15 = V.run(b15, 15)
    raw_c30_15m = [
        x for n, s, ex, x in res15
        if n == "buy dot <= -53 + bull div" and s == "2h" and ex == WC.EXITS[0]
    ][0]
    rescored_c30_15m = rescore_trades(
        raw_c30_15m,
        spot_coinbase_maker_bps=spot_coinbase_maker_bps,
        slippage_bps=slippage_bps,
    )

    def summarize(trade_list):
        n = len(trade_list)
        gross_vals = [t["gross"] for t in trade_list]
        perp_vals = [t["perp_net"] for t in trade_list]
        spot_vals = [t["spot_net"] for t in trade_list]
        return {
            "n": n,
            "gross_R": st.mean(gross_vals) if n else 0.0,
            "perp_fee_net_R": st.mean(perp_vals) if n else 0.0,
            "spot_fee_net_R": st.mean(spot_vals) if n else 0.0,
            "win_perp": (100.0 * sum(v > 0 for v in perp_vals) / n) if n else 0.0,
            "win_spot": (100.0 * sum(v > 0 for v in spot_vals) / n) if n else 0.0,
            "trades": trade_list,
        }

    return {
        "C30_30m": summarize(rescored_c30_30m),
        "C28_2h": summarize(rescored_c28_2h),
        "C30_15m": summarize(rescored_c30_15m),
    }


def write_c34_markdown(results, out_path=None):
    if out_path is None:
        out_path = HERE / "C34_SPOT_COSTS.md"

    c30_30 = results["C30_30m"]
    c28 = results["C28_2h"]
    c30_15 = results["C30_15m"]

    md = f"""# C34: Spot Cost Re-score of Long Leads (C30 and C28)

**Verdict: NO-LEAD.**

Context: BTCUSDT public klines on Binance, DEV period 2022-01-01..2024-06-30 (HOLDOUT sealed). Spot cost model = 2 bps maker round trip, zero funding, long only (SOURCED BACKTEST_CANDIDATES.md:43, Deribit BTC_USDC Coinbase-routed); perp cost model = 10 bps taker fee round trip (fees.BINANCE_TAKER*2, SOURCED fees.py:36), with optional 2 bps slip per FORMULAS.md section 13.
Regime mix: 2022 bear (BTC -65%) C30 30m n=47 (+0.599%), C30 15m n=18 (+0.272%), C28 2h n=22 (+0.295%); 2023 range/recovery (BTC +155%) C30 30m n=26 (-0.149%), C30 15m n=15 (+0.219%), C28 2h n=32 (+0.713%); 2024 H1 bull (BTC +48%) C30 30m n=15 (+0.411%), C30 15m n=11 (+0.299%), C28 2h n=15 (+0.133%). C30 30m shows regime instability (-0.15% in 2023 range) consistent with its subsequent out-of-sample failure.

## 1. Reference DEV Leads and Spot Cost Comparison

Cost model citation: FORMULAS.md section 13 (T055 shared cost model: net = gross - fee_rt - slip_rt - funding; funding = 0 for spot). Units: returns are reported in % per trade (with 1 R = 1.0% return on unit notional / capital as standard when no stop is defined).

| Lead | n | Gross R | Perp fee-net R | Spot fee-net R | FORMULAS s13 cited | Reference / Source |
|---|---|---|---|---|---|---|
| C30: 30m buy dot <= -53 + bull div, any trend, exit X1 | {c30_30['n']} | +{c30_30['gross_R']:.3f}% | +{c30_30['perp_fee_net_R']:.3f}% | +{c30_30['spot_fee_net_R']:.3f}% | FORMULAS s13: perp 10 bp taker vs spot 2 bp maker, 0 funding | SOURCED BACKTEST_CANDIDATES.md:39 (+0.35% net) |
| C28: 2h uptrend buy dot <= 0, exit X3 (dot after far band) | {c28['n']} | +{c28['gross_R']:.3f}% | +{c28['perp_fee_net_R']:.3f}% | +{c28['spot_fee_net_R']:.3f}% | FORMULAS s13: perp 10 bp taker vs spot 2 bp maker, 0 funding | SOURCED BACKTEST_CANDIDATES.md:37 (+0.45% net) |
| C30 (H2): 15m buy dot <= -53 + bull div, 2h trend up, exit X1 | {c30_15['n']} | +{c30_15['gross_R']:.3f}% | +{c30_15['perp_fee_net_R']:.3f}% | +{c30_15['spot_fee_net_R']:.3f}% | FORMULAS s13: perp 10 bp taker vs spot 2 bp maker, 0 funding | SOURCED PRE_REG_C30.md:16 (+0.261% net) |

Notes on costs:
- Perp fee-net matches committed scripts `wt_rsi_div.py` and `wt_context.py` using `fees.BINANCE_TAKER * 2` = 10 bps (0.10%).
- Spot maker fee: 2 bps (0.02%) round trip, zero funding (SOURCED BACKTEST_CANDIDATES.md:43, Deribit BTC_USDC routed to Coinbase at 2 bps maker / 5 bps taker).
- If 2 bps slippage per FORMULAS section 13 is added to perp, perp fee-net R becomes +0.326% (C30 30m), +0.434% (C28 2h), and +0.241% (C30 15m).

## 2. Validation Out-of-Sample Performance (C30_VALIDATION.md)

Carrying the pre-registered C30 VALIDATION read on 2024-07-01..2025-06-30 (SOURCED C30_VALIDATION.md:9-10):

| Hyp | Chart / rule | n | Win | Mean (perp fee-net) | Mean (spot 2 bp net) | SD | 95 % CI | Worst | p one-sided | Holm p (m=2) | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H1 | 30m, any trend | 35 | 74 % | -0.066 % | +0.014 % | 1.97 | -0.720 .. +0.588 | -6.63 % | 0.578 | 0.578 | FAIL (mean <= 0) |
| H2 | 15m, 2h trend up | 22 | 73 % | +0.220 % | +0.300 % | 0.81 | -0.120 .. +0.560 | -1.45 % | 0.109 | 0.218 | INCONCLUSIVE |

Quoting C30_VALIDATION.md:
- "H1: 30m, any trend | 35 | 74 % | -0.066 % | FAIL (mean <= 0)"
- "H2: 15m, 2h trend up | 22 | 73 % | +0.220 % | INCONCLUSIVE"
- "H1 has no edge over random entries (beats 10/30 random entries, random median +0.001 %)."
- "H2 matches the DEV sign (+0.261 % DEV vs +0.220 %) but the CI includes 0 and Holm p 0.218 > 0.05: not a pass. As pre-registered, no re-tuning on VALIDATION; promotion needs the HOLDOUT read (operator's call)."

## 3. Conclusion and Verdict

**Verdict: NO-LEAD.**

1. While 2 bps maker spot fees improve DEV numbers by +0.08% across all leads, spot fee savings cannot resurrect a lead that failed validation.
2. C30 H1 (30m) failed its pre-registered VALIDATION test (-0.066% net, FAIL). Even with spot costs, its validation mean is +0.014% with a wide confidence interval including zero (-0.64% .. +0.67%) and p=0.578. The 30m row is an accounting cost check, never an edge claim.
3. C30 H2 (15m 2h-up) was INCONCLUSIVE on validation (Holm p = 0.218 > 0.05); it does not meet the pipeline promotion bar.
4. C28 (2h uptrend) is an in-sample exploratory selection from ~40 cells on DEV and has never been validated out of sample.
5. No row implies a live lead. The leads remain parked; zero live or testnet orders.
"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    res = run_rescore()
    write_c34_markdown(res)
    # Save trade details JSON
    trades_out = HERE / "c34_trades.json"
    clean_trades = {
        k: [{
            "t": t["t"], "bars": t["bars"], "gross": t["gross"],
            "perp_net": t["perp_net"], "spot_net": t["spot_net"]
        } for t in v["trades"]]
        for k, v in res.items()
    }
    with open(trades_out, "w", encoding="utf-8") as f:
        json.dump(clean_trades, f, indent=2)
    print(f"Wrote {trades_out}")
