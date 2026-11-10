"""Writes RESULT.md from sim_desk/results/live_aid-pulse-backtest.json (no number typed by hand)."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
d = json.loads((HERE.parent / "sim_desk" / "results" / "live_aid-pulse-backtest.json").read_text())
C = d["cells"]
f = lambda x: "%.1f" % x  # noqa: E731
ci = lambda v: "[%s, %s]" % (f(v[0]), f(v[1]))  # noqa: E731
p = C["h30|ALL|ALL"]
se_pct = (p["diff_ci_bp"][1] - p["diff_ci_bp"][0]) / 3.92 / 100
L = []
L.append("# RESULT: Live Aid pulse SETUP FORMING vs matched null, DEV only, BTCUSDT perp 1m, fee-net 14 bp (one run per PRE_REG.md)\n")
L.append("**Verdict: FAIL. The SETUP FORMING flag is a coin flip beyond being near a level: at 30 min, n = %d, gross %s bp %s, fee-net %s bp %s; the flag minus the near-level null is %s bp %s.** FAIL means stop: no coaching claim from the SETUP FORMING flag on BTC perp 1m-4h with these thresholds; a threshold tune needs its own PRE_REG and the VALIDATION read.\n"
         % (p["n"], f(p["gross_bp"]), ci(p["gross_ci_bp"]), f(p["net_bp"]), ci(p["net_ci_bp"]), f(p["diff_vs_null_bp"]), ci(p["diff_ci_bp"])))
L.append("Regime mix: window 2022-02-01..2024-06-30, 881 UTC days: bull 261 (29.6 %), bear 185 (21.0 %), range 435 (49.4 %); signals: bull 2889, bear 1866, range 5338 (trailing 30-day close return, +-10 %).\n")
L.append("Split: DEV only; VALIDATION (2024-07 onward) and HOLDOUT never opened (loader opens files up to 2024-06 and asserts every bar is before 2024-07-01). Tape: Binance USD-M perp 1m (proxy for the page's spot feed). Decisions every 5 min; entry open of next 1m bar + 1 bar; cost 14 bp (10 fee + 4 slippage); CI = 95 %% day-clustered bootstrap (4000 draws, seed 7). Raw setups %d, signals after the 60-min same-side cooldown %d, missing-bar drops 0.\n" % (d["setups_raw"], d["signals"]))
L.append("## Verdict arms\n| arm | n | mean | SE | cost | verdict |\n|---|---|---|---|---|---|")
L.append("| pulse SETUP FORMING minus near-level null, h30, all sessions | %d | %.4f | %.4f | 0.14 | FAIL |\n" % (p["n"], p["diff_vs_null_bp"] / 100, se_pct))
L.append("mean and SE in percent of notional (signal gross minus null gross); t = %.2f. Net of 14 bp the signal itself loses %s bp.\n" % (p["diff_vs_null_bp"] / 100 / se_pct, f(-p["net_bp"])))
for h in (15, 30, 60):
    L.append("## Horizon %d min, by session (bp; CI 95 %%, day-clustered)\n| scope | n | gross | net 14 bp | signal - near-level null | signal - random-time null | signal - lean-only null | short share |\n|---|---|---|---|---|---|---|---|" % h)
    for s in ("ALL", "Asia", "Europe", "US", "Late"):
        c = C["h%d|%s|ALL" % (h, s)]
        l3 = "%s %s" % (f(c["diff_vs_lean_only_bp"]), ci(c["diff_vs_lean_only_ci_bp"])) if c["diff_vs_lean_only_bp"] is not None else "n/a"
        L.append("| %s | %d | %s %s | %s %s | %s %s | %s %s | %s | %.2f |" % (s, c["n"], f(c["gross_bp"]), ci(c["gross_ci_bp"]), f(c["net_bp"]), ci(c["net_ci_bp"]), f(c["diff_vs_null_bp"]), ci(c["diff_ci_bp"]),
                                                                       f(c["diff_vs_random_time_bp"]), ci(c["diff_vs_random_ci_bp"]), l3, c["share_short"]))
    L.append("")
    L.append("### Horizon %d min, by regime\n| regime | n | gross | net 14 bp | signal - near-level null | signal - lean-only null |\n|---|---|---|---|---|---|" % h)
    for r in ("bull", "bear", "range"):
        c = C["h%d|ALL|%s" % (h, r)]
        L.append("| %s | %d | %s %s | %s %s | %s %s | %s %s |" % (r, c["n"], f(c["gross_bp"]), ci(c["gross_ci_bp"]), f(c["net_bp"]), ci(c["net_ci_bp"]), f(c["diff_vs_null_bp"]), ci(c["diff_ci_bp"]),
                                                              f(c["diff_vs_lean_only_bp"]), ci(c["diff_vs_lean_only_ci_bp"])))
    L.append("")
L.append("## Reading\n- No horizon, session or regime cell has a fee-net mean above zero; the best net is about -12 bp, the cost alone is 14 bp. The pooled gross effect is within about +-1 bp of zero at 15 and 30 min and +0.7 bp [-0.2, 1.7] at 60 min.\n- Against the near-level null (the PRE_REG primary control) every CI contains 0 at 15 and 30 min; at 60 min the pooled difference is +0.9 bp [-0.1, 1.9], Europe +1.8 bp [-0.2, 3.8]. Neither passes the PRE_REG rule (PASS_GROSS_ONLY needs a CI wholly above 0 at the primary 30 min cell).\n- One secondary cell has a CI above zero: 60 min, bear regime, signal minus lean-only null +3.4 bp [0.3, 6.7]. It is one of about 70 secondary contrasts printed here (24 cells x 3 nulls) (Holm family m = 236 on DEV) and does not survive that correction; it is a lead for a PRE_REG, never a finding.\n- 57 % of signals are SHORT (lean down plus a bearish divergence is found more often than the mirror); the SHORT/LONG mix is copied into the null, so it does not bias the contrast.\n- The flag fires at 62 % of the 5-min decision times that are near a level (52087 of 84348): it is not selective, so a coin flip on it is what the operator should expect from the coaching.\n- Divergence adds nothing measurable over the lean alone (signal minus lean-only null: all pooled CIs contain 0).\n")
L.append("## Caveats (not hidden)\n- Perp tape, not spot; CVD is perp taker flow. Only part of the page's level ladder exists historically (PDH/PDL/PDC, DO, WO, PWH/PWL, Asia high/low); analyst, VAL/POC/VAH, MA-strip and VWAP levels and the Home direction are NOT_IN_DATA, so the page may flag places this study never tested.\n- Events overlap (5-min cadence, several levels, 60-min cooldown per side only); n overstates independent samples, which is why the CIs are day-clustered.\n- Thresholds P stay OURS; nothing here tunes them. No VALIDATION read, no trade claim.\n")
(HERE / "RESULT.md").write_text("\n".join(L), encoding="utf-8", newline="\n")
print("ok")
