"""Write the Eagle_Eyes 10-30/31 chart-idea tests (C21, C23-C30) as simulator result files (sim_desk/DESIGN.md "Result files").
C26 trades are recomputed from c26_arms.py (replay); the others carry the numbers recorded in BACKTEST_CANDIDATES.md.
Percent, R and timestamps only (no prices: the repo is public). Usage: python export_sim.py <repo>"""
import json, os, sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = sys.argv[1]
OUT = os.path.join(REPO, "MyTradingSys", "research", "sim_desk", "results")
sys.path.insert(0, HERE)
import c26_arms as A

FAM = "Eagle_Eyes chart ideas (operator, 10-30/31)"
SRC = "MyTradingSys/research/eagle_eyes_picture_2026-10-28/"
WIN = "2022-01-01 to 2026-10-31, split 2022-01..2024-06 vs 2024-07..now (whole history was read: a seen-period check, not a sealed test)"
FEE = {"name": "Costs", "value_plain": "0.10% per round trip (Binance taker x2, backtest/fees.py); slippage and funding not modelled", "label": "SOURCED"}


def P(name, value, label="OURS"):
    return {"name": name, "value_plain": value, "label": label}


def day(ms):
    return datetime.fromtimestamp(ms / 1000, timezone.utc).strftime("%Y-%m-%d %H:%M")


def base(id_, title, what, how, verdict, tone, why, kpis, examples, files, date="2026-10-31"):
    return {"id": id_, "kind": "backtest", "family": FAM, "title": title, "provenance": "run", "date": date, "what": what, "how": how,
            "window": WIN, "verdict": {"label": verdict, "tone": tone}, "why": why, "kpis": kpis, "examples": examples,
            "evidence": [SRC + "BACKTEST_CANDIDATES.md"], "missing": [], "source_files": [SRC + f for f in files], "commit": "see git log"}


def replay_arm(arm, label):
    tr = sorted(A.trades(1, arm) + A.trades(-1, arm), key=lambda r: r["t"])
    rows, cum, s, usd = [], [], 0.0, 1000.0
    for r in tr:
        R = r["net"] / abs(r["stop"]) if r["stop"] else 0.0
        s += R; cum.append(round(s, 3)); usd *= 1 + r["net"] / 100
        rows.append({"d": day(r["t"])[:10], "s": r["d"], "f": "held 15m level (exit: %s, %d bars)" % (r["why"], r["bars"]),
                     "l2": round(r["stop"], 3), "t1": round(r["target"], 3), "t2": round(r["target"], 3), "r": round(R, 3)})
    return tr, rows, cum, usd


def table(title, cols, rows, caption=""):
    return {"kind": "table", "title": title, "caption": caption, "cols": cols, "rows": rows}


EV = [P("Held level", "15m pivot = highest high (lowest low) of +-16 bars, pulled back >= 0.8%, retested within 0.4% without breaking, pivot <= 72h old; decision 1h after the retest"),
      P("Timeframe", "15m Binance spot BTCUSDT")]
out = []

trA, rowsA, cumA, usdA = replay_arm("A", "ride to the held level")
out.append(base("eagle-c26-ride", "C26 arm A: after a held 15m retest, ride to the level (pre-registered)",
    EV + [P("Entry", "next 15m open toward the level (long under a held high, short over a held low)"),
          P("Target", "the held level itself"), P("Stop", "0.8% against the entry; a bar touching both = stop"),
          P("Time limit", "24h"), FEE],
    "Rules fixed in C26_PRE_REG.md (commit 21fbba6b) before the run; run once with c26_arms.py.",
    "NO: loses about the fee in both periods (net -0.10% / -0.11% per trade, n 1504 / 1362).", "bad",
    ["Price does go back to a held level (C26 magnet), but the distance is short: before fees each trade makes about zero.",
     "The 0.10% taker fee turns that zero into a steady loss; win rate 55% is not enough with a 0.8% stop.",
     "Replay R = net % divided by the 0.8% stop. The ladder shows the stop (bottom line) and the target (top lines)."],
    [{"label": "Trades", "value": str(len(trA))}, {"label": "2022-01..2024-06 net/trade", "value": "-0.100%", "tone": "bad"},
     {"label": "2024-07..now net/trade", "value": "-0.112%", "tone": "bad"}, {"label": "Win rate", "value": "55%"},
     {"label": "1,000 USD at 1x, every trade (OURS)", "value": "%.0f USD" % usdA, "tone": "bad"}],
    [{"kind": "replay", "title": "Trade replay (every trade, in time order)", "caption": "Distance from the entry in %; up is in favour of the trade. No prices.",
      "trades": rowsA, "cum": cumA}],
    ["c26_arms.py", "C26_PRE_REG.md", "failed_retest_takeout.py"]))

trB, rowsB, cumB, usdB = replay_arm("B", "fade the swept take-out")
out.append(base("eagle-c26-fade", "C26 arm B: fade a take-out that closes back inside within 1h (pre-registered)",
    EV + [P("Signal", "the level is taken out, then a 15m close comes back inside within 4 bars"),
          P("Entry", "next 15m open, against the take-out"), P("Stop", "beyond the take-out wick + 0.05%"),
          P("Target", "1.0% in favour"), P("Time limit", "24h"), FEE],
    "Rules fixed in C26_PRE_REG.md (commit 21fbba6b) before the run; run once with c26_arms.py.",
    "NO: net -0.08% / -0.12% per trade (n 898 / 802), win rate 37% / 28%.", "bad",
    ["About 70% of take-outs do close back inside, but the move after is small (median 0.1-0.4% in 24h).",
     "The wick stop is hit before the 1% target too often; fees finish it.",
     "Replay R = net % divided by the stop distance of that trade."],
    [{"label": "Trades", "value": str(len(trB))}, {"label": "2022-01..2024-06 net/trade", "value": "-0.078%", "tone": "bad"},
     {"label": "2024-07..now net/trade", "value": "-0.117%", "tone": "bad"}, {"label": "Win rate", "value": "37% / 28%"},
     {"label": "1,000 USD at 1x, every trade (OURS)", "value": "%.0f USD" % usdB, "tone": "bad"}],
    [{"kind": "replay", "title": "Trade replay (every trade, in time order)", "caption": "Distance from the entry in %; up is in favour of the trade. No prices.",
      "trades": rowsB, "cum": cumB}],
    ["c26_arms.py", "C26_PRE_REG.md", "failed_retest_takeout.py"]))

out.append(base("eagle-c26-magnet", "C26: a held 15m high/low is taken out later (base rates)",
    EV + [P("Control", "the same pivots at age-matched times, close 0.4-1.5% from the level, no retest condition")],
    "failed_retest_takeout.py counts how often and how soon the level breaks; no trade, no fees.",
    "REAL but not a trade: taken within 24h 72% vs 59% control, both sides, both periods.", "info",
    ["Operator's 10-31 chart: the 10-28 high held twice, was taken 19h later on 10-29, closed back under, then the drop.",
     "The retest comes about 10h after the pivot; the take-out about 4-5h after the retest.",
     "Use: a chart and dashboard line ('held level, likely taken'), not an entry on its own (arms A and B both failed)."],
    [{"label": "Taken within 24h", "value": "72%", "tone": "good"}, {"label": "Control", "value": "57-61%"},
     {"label": "Pivot to retest (median)", "value": "~10h"}, {"label": "Retest to take-out (median)", "value": "~4-5h"},
     {"label": "Take-outs that close back within 1h", "value": "~70%"}],
    [table("Share taken out", ["Group", "Period", "n", "24h", "48h", "72h"],
           [["Held highs", "2022-01..2024-06", 768, "73%", "82%", "86%"], ["Held highs", "2024-07..now", 686, "71%", "80%", "85%"],
            ["Held lows", "2022-01..2024-06", 736, "72%", "81%", "86%"], ["Held lows", "2024-07..now", 677, "73%", "79%", "82%"],
            ["Control highs", "2022-01..2024-06", 1296, "60%", "73%", "78%"], ["Control highs", "2024-07..now", 1123, "57%", "69%", "76%"]])],
    ["failed_retest_takeout.py"]))

out.append(base("eagle-c25-stochrsi", "C25: Stoch RSI cross vs plain RSI as a trigger (15m, 1h, 4h, 1d)",
    [P("Stoch RSI", "14, 14, 3, 3 (TradingView defaults); K crosses D under 20 = long, over 80 = short", "SOURCED"),
     P("Plain RSI", "RSI 14 back over 30 = long, back under 70 = short", "SOURCED"),
     P("Trend filter", "close above / below the 200-bar average"), P("Hold", "8 x 15m, 6 x 1h, 6 x 4h, 5 x 1d"),
     P("Edge", "signal mean minus holding the same side for the same time at every bar"), FEE],
    "stochrsi_vs_rsi.py on Binance spot from 2022; one signal per two holds.",
    "NO intraday: no edge on 15m, 1h or 4h in either period; one small daily lead (n 17/16).", "bad",
    ["Stoch RSI fires about 3.5x as often as plain RSI and adds no information over it.",
     "Daily trend-long +0.68% / +0.84% over 5 days is 1 of 32 cells with 16-17 trades: could be luck, needs its own pre-registration.",
     "Keep it as a chart read (stretched / not stretched), not a trigger."],
    [{"label": "15m long cross, edge", "value": "-0.02% / -0.02%", "tone": "bad"}, {"label": "4h long cross, 2024-07..now", "value": "-0.26%", "tone": "bad"},
     {"label": "1d trend-long edge (n 17/16)", "value": "+0.68% / +0.84%", "tone": "warn"}],
    [table("Edge vs base after fees", ["Chart", "Signal", "2022-01..2024-06", "2024-07..now"],
           [["15m", "Stoch cross long (n 2312/2115)", "-0.020%", "-0.020%"], ["15m", "RSI 30 long (n 648/664)", "+0.005%", "+0.027%"],
            ["1h", "Stoch cross short + trend (n 325/316)", "+0.067%", "+0.069%"], ["4h", "Stoch cross long (n 153/151)", "+0.033%", "-0.258%"],
            ["1d", "Stoch cross long + trend (n 17/16)", "+0.680%", "+0.835%"]])],
    ["stochrsi_vs_rsi.py"]))

out.append(dict(base("eagle-c27-wavetrend", "C27: WaveTrend dots (LazyBear WT_CROSS_LB) as triggers, 15m / 1h / 2h / 4h",
    [P("WaveTrend", "n1 10, n2 21, wt2 = 4-bar average of wt1; overbought / oversold lines +53 / -53", "SOURCED"),
     P("Signals", "buy dot = wt1 crosses up through wt2 (in the -53 zone, or anywhere); sell dot = the mirror"),
     P("Hold", "16 x 15m, 12 x 1h, 6 and 12 x 2h, 6 x 4h; entry at the close of the bar after the dot"),
     P("Edge", "signal mean minus holding the same side for the same time at every bar"), FEE],
    "wavetrend_dots.py on Binance spot 15m from 2022 (1h/2h/4h built from it); 2024-07+ left sealed for the WaveTrend pre-reg.",
    "NO as a trigger: no dot type beats fees on any timeframe beyond noise; zone dots (the ones on the chart) are worse than plain dots.", "bad",
    ["Agrees with the older MTS WaveTrend atlas (wavetrend_2026-10-17: 4 FAIL, 5 INCONCLUSIVE, no fees) and the 30m sequence study.",
     "Best cell: 4h any buy dot, net +0.14% over 24h, 1 SE 0.14% - one standard error, among 20 cells: luck-sized.",
     "Use it as context (stretched / turning), never alone; a 2024-07+ check needs its own pre-registration."],
    [{"label": "2h buy dot <= -53, 24h net", "value": "-0.19% (n 108)", "tone": "bad"},
     {"label": "2h sell dot >= 53, 24h net", "value": "-0.41% (n 119)", "tone": "bad"},
     {"label": "Best cell: 4h any buy dot", "value": "+0.14% net, 1 SE 0.14%", "tone": "warn"}],
    [table("After fees, 2022-01..2024-06", ["Chart / hold", "Signal", "n", "Win", "Edge vs base", "Net"],
           [["15m / 4h", "buy dot <= -53", 787, "57%", "-0.00%", "-0.09%"], ["15m / 4h", "sell dot >= 53", 825, "51%", "-0.06%", "-0.17%"],
            ["1h / 12h", "buy dot <= -53", 216, "49%", "-0.15%", "-0.21%"], ["1h / 12h", "sell dot >= 53", 214, "50%", "-0.16%", "-0.30%"],
            ["2h / 24h", "buy dot <= -53", 108, "52%", "-0.18%", "-0.19%"], ["2h / 24h", "sell dot >= 53", 119, "55%", "-0.22%", "-0.41%"],
            ["2h / 24h", "any buy dot", 815, "51%", "+0.04%", "+0.02%"], ["4h / 24h", "any buy dot", 405, "54%", "+0.15%", "+0.14%"],
            ["4h / 24h", "any sell dot", 404, "43%", "-0.16%", "-0.34%"]])],
    ["wavetrend_dots.py"]), window="2022-01-01 to 2024-06-30 only (2024-07+ sealed by wavetrend_2026-10-17/PRE_REG.md)"))

import wt_context as WC
_c28 = WC.trades("2h", 8, WC.RULES[4], 2)
_rows, _cum, _s = [], [], 0.0
for r in _c28:
    _s += r["net"]; _cum.append(round(_s, 3))
    _rows.append({"d": day(r["t"])[:10], "s": r["d"], "f": "2h uptrend buy dot (exit: %s, %d bars)" % (r["why"], r["bars"]),
                  "l2": 0, "t1": 0, "t2": 0, "r": round(r["net"], 3)})
out.append(dict(base("eagle-c28-wt-structure", "C28: WaveTrend inside market structure (sell tops in downtrends, buy dots in uptrends), 1h / 2h / 4h",
    [P("WaveTrend", "n1 10, n2 21, wt2 = 4-bar average; bands +53 / -53", "SOURCED"),
     P("Trend", "flips down when a close breaks the last swing low, up when a close breaks the last swing high; swings = +-5 bars, known 5 bars later"),
     P("Entries", "downtrend: sell dot at >= 53 or >= 0, buy dot at <= -53; uptrend: buy dot at <= -53 or <= 0; next bar's open"),
     P("Exits compared", "X1 centre cross | X2 far band | X3 first opposite dot after the far band | X4 first opposite dot; trend flip ends a with-trend trade; cap 60 bars"),
     FEE],
    "wt_context.py on Binance spot 15m built into 1h/2h/4h. Replay = the best cell (2h uptrend buy dot <= 0, exit X3); r = net % per trade (no fixed stop).",
    "NO for the downtrend shorts; one LEAD: 2h uptrend buy dot, exit at the first sell dot after WT reaches +53 (n 69, +0.45% net, both halves positive).", "warn",
    ["In a downtrend WT almost never reaches +53: 5 sell-dot-in-the-red-band trades on 1h in 2.5 years, none on 2h/4h.",
     "Downtrend shorts at sell dots above 0 lose on every timeframe and every exit (-0.15% to -0.55% per trade).",
     "The lead was chosen as best of about 40 cells on the same data (t 1.0) and beats random entries with the same exit in only 25 of 30 draws (bt_preflight.py P8): it needs a pre-registered read of 2024-07+ before anyone trusts it."],
    [{"label": "2h uptrend buy dot, exit X3", "value": "+0.45% net, n 69", "tone": "warn"},
     {"label": "2h downtrend short at sell dot >= 0", "value": "-0.15% to -0.55%", "tone": "bad"},
     {"label": "Sell dots in the red band during downtrends", "value": "5 in 2.5 years (1h)", "tone": "bad"}],
    [{"kind": "replay", "title": "2h uptrend buy dot, exit at the first sell dot after +53", "trades": _rows, "cum": _cum},
     table("Net per trade after fees, 2022-01..2024-06 (halves: to 2023-03 / from 2023-04)", ["Chart", "Rule", "Exit", "n", "Win", "Net", "Halves"],
           [["2h", "Uptrend buy dot <= 0", "X3", 69, "39%", "+0.454%", "+0.64% / +0.32%"], ["2h", "Uptrend buy dot <= 0", "X1", 85, "56%", "+0.061%", "+0.20% / -0.05%"],
            ["4h", "Uptrend buy dot <= 0", "X3", 24, "38%", "+0.734%", "+1.12% / +0.41%"], ["1h", "Uptrend buy dot <= 0", "X3", 133, "36%", "-0.005%", "+0.12% / -0.13%"],
            ["2h", "Downtrend sell dot >= 0", "X1", 83, "46%", "-0.160%", "-0.16% / -0.16%"], ["2h", "Downtrend sell dot >= 0", "X4", 100, "30%", "-0.150%", "-0.08% / -0.23%"],
            ["1h", "Downtrend sell dot >= 0", "X1", 139, "46%", "-0.259%", "-0.16% / -0.36%"], ["4h", "Downtrend buy dot <= -53", "X4", 44, "45%", "+0.549%", "+0.41% / +0.74%"],
            ["2h", "Downtrend buy dot <= -53", "X1", 66, "68%", "-0.050%", "-1.34% / +1.40%"]])],
    ["wt_context.py", "wavetrend_dots.py"]), window="2022-01-01 to 2024-06-30 only (2024-07+ sealed by wavetrend_2026-10-17/PRE_REG.md)"))

out.append(dict(base("eagle-c29-wt-lower-tf", "C29: red-band WaveTrend sells in a downtrend on 10m / 15m / 30m (trend from the same chart or from 2h)",
    [P("WaveTrend", "n1 10, n2 21, wt2 = 4-bar average; bands +53 / -53", "SOURCED"),
     P("Trend", "same chart: swing-break structure on the trading chart; 2h: structure of the last CLOSED 2h bar"),
     P("Rules / exits", "as C28 (sell dot >= 53 or >= 0 in a downtrend, buy dots in an uptrend; exits X1-X4; cap 60 bars)"), FEE],
    "wt_lower_tf.py on Binance spot 5m from 2022 built into 10m/15m/30m.",
    "Frequency fixed, profit not: with the 2h downtrend as context red-band sells happen often (10m n 321, 15m 187, 30m 63) but lose on 10m/15m; 30m about flat.", "bad",
    ["With the trend read on the same small chart, red-band sells stay rare (3-9 in 2.5 years): the context has to come from a higher chart.",
     "10m and 15m red-band sells lose with every exit (-0.04% to -0.21% per trade after fees).",
     "30m with the 2h downtrend: +0.18% per trade with exit X3 (n 61, both halves positive, t 0.5): too weak to call."],
    [{"label": "10m red-band sells, 2h downtrend", "value": "n 321, -0.09% to -0.17%", "tone": "bad"},
     {"label": "15m red-band sells, 2h downtrend", "value": "n 187, -0.04% to -0.21%", "tone": "bad"},
     {"label": "30m red-band sells, 2h downtrend, X3", "value": "n 61, +0.18%", "tone": "warn"}],
    [table("Downtrend red-band sells (sell dot >= 53), net per trade after fees", ["Chart", "Trend from", "Exit", "n", "Net", "Halves"],
           [["10m", "2h", "X1", 321, "-0.117%", "-0.08% / -0.16%"], ["10m", "2h", "X4", 458, "-0.094%", "-0.08% / -0.11%"],
            ["15m", "2h", "X1", 187, "-0.037%", "+0.14% / -0.25%"], ["15m", "2h", "X3", 176, "-0.209%", "-0.06% / -0.39%"],
            ["30m", "2h", "X3", 61, "+0.181%", "+0.21% / +0.16%"], ["30m", "2h", "X4", 78, "+0.068%", "+0.16% / +0.01%"],
            ["10m", "same", "X1", 9, "-0.179%", "-"], ["15m", "same", "X1", 4, "-0.532%", "-"]])],
    ["wt_lower_tf.py", "wt_context.py"]), window="2022-01-01 to 2024-06-30 only (2024-07+ sealed by wavetrend_2026-10-17/PRE_REG.md)"))

out.append(dict(base("eagle-c30-wt-rsi-div", "C30: WaveTrend dots plus RSI divergence (sell tops with bearish, buy bottoms with bullish), 10m to 4h",
    [P("RSI", "14, Wilder", "SOURCED"), P("WaveTrend", "n1 10, n2 21, wt2 = 4-bar average; bands +53 / -53", "SOURCED"),
     P("Divergence", "newest high (low) in the last 8 bars beyond the extreme of bars 9-40 back while RSI is lower (higher); first RSI peak >= 60 (trough <= 40)"),
     P("Trend", "any / same chart / last closed 2h bar"), P("Exits", "X1-X4 as C28; cap 60 bars"), FEE],
    "wt_rsi_div.py: 5m data built into 10m/15m/30m, 15m data into 1h/2h/4h. About 250 cells: treat every number as in-sample.",
    "Bottoms YES-ish, tops NO: buy dot <= -53 with bullish RSI divergence is positive on 15m and 30m in both halves; shorts with bearish divergence lose almost everywhere (3 of 65 cells positive).", "warn",
    ["30m buy dot <= -53 + bullish divergence, exit at the centre line: n 88, win 80%, +0.35% net, both halves positive; it beats the same buy dots without divergence (95th percentile +0.22%) and random bars (+0.13%).",
     "15m same rule with the 2h trend up, centre-line exit: n 44, win 75%, +0.26%, t 2.8.",
     "Selected from about 250 cells on one period: needs a pre-registered read of 2024-07+ before anyone trusts it."],
    [{"label": "30m buy dot <= -53 + bull div, X1", "value": "+0.35% net, n 88, win 80%", "tone": "good"},
     {"label": "Shorts with bearish divergence", "value": "3 of 65 cells positive", "tone": "bad"},
     {"label": "Long cells positive", "value": "30 of 62", "tone": "warn"}],
    [table("Net per trade after fees (n >= 30), 2022-01..2024-06", ["Chart", "Signal", "Trend", "Exit", "n", "Win", "Net", "Halves"],
           [["30m", "buy dot <= -53 + bull div", "any", "X1", 88, "80%", "+0.346%", "+0.41% / +0.25%"],
            ["30m", "buy dot <= -53 + bull div", "any", "X2", 87, "61%", "+0.322%", "+0.33% / +0.32%"],
            ["15m", "buy dot <= -53 + bull div", "2h up", "X1", 44, "75%", "+0.261%", "+0.30% / +0.22%"],
            ["15m", "buy dot <= -53 + bull div", "2h up", "X2", 42, "60%", "+0.355%", "+0.42% / +0.29%"],
            ["4h", "buy dot <= 0 + bull div", "any", "X4", 35, "46%", "+0.904%", "+0.80% / +1.10%"],
            ["2h", "buy dot <= -53 + bull div", "any", "X4", 30, "50%", "+0.609%", "+0.36% / +0.98%"],
            ["10m", "sell dot >= 53 + bear div", "any", "X1", 249, "-", "-0.137%", "-"],
            ["15m", "sell dot >= 53 + bear div", "any", "X1", 168, "-", "-0.240%", "-"],
            ["30m", "sell dot >= 53 + bear div", "any", "X1", 83, "-", "-0.461%", "-"]])],
    ["wt_rsi_div.py", "wt_lower_tf.py", "wt_context.py"]), window="2022-01-01 to 2024-06-30 only (2024-07+ sealed by wavetrend_2026-10-17/PRE_REG.md)"))

out.append(base("eagle-c21-bb-pierce", "C21: first close under the lower Bollinger band in a falling band, short to the mid",
    [P("Pierce", "first close below BB(20,2) lower band, mid falling, no pierce in the prior 10 bars"),
     P("Breakdown context", "the close is a new 14-day low"), P("Exit", "first close back above the BB mid (or RSI under 30 then back over its SMA 14)"),
     P("Timeframes", "15m, 30m, 4h"), FEE],
    "bb_lower_pierce_breakdown.py, Binance spot 15m from 2022 (30m and 4h built from it).",
    "LEAD only: 30m breakdown pierces positive in both periods (+0.16% / +0.62%) but n 38/35 among many cells.", "warn",
    ["15m breakdown pierces fall about 0.9% further (median) but the mid exit gives it back: -0.06% / -0.20%.",
     "Pierces that are not a new 2-week low lose on 15m and 30m.",
     "Needs one pre-registered 30m test before it counts."],
    [{"label": "30m breakdown, mid exit", "value": "+0.16% / +0.62%", "tone": "warn"}, {"label": "15m breakdown, mid exit", "value": "-0.06% / -0.20%", "tone": "bad"},
     {"label": "4h breakdown", "value": "-1.5% / -1.7%", "tone": "bad"}],
    [table("Mid-exit net per trade", ["Chart", "Context", "n", "2022-01..2024-06", "2024-07..now"],
           [["15m", "breakdown", "57/54", "-0.06%", "-0.20%"], ["30m", "breakdown", "38/35", "+0.16%", "+0.62%"], ["4h", "breakdown", "16/14", "-1.5%", "-1.7%"]])],
    ["bb_lower_pierce_breakdown.py"], date="2026-10-31"))

out.append(base("eagle-c23-daily-shorts", "C23: daily shorts from RSI lower highs and Bollinger-mid rejections",
    [P("A: divergence", "bearish RSI divergence at a high, swings 3-40 days apart (repo rule)", "SOURCED"),
     P("A_major", "5/5-day close pivots within 60 days, close >= 98% of the prior high, RSI >= 3 lower"),
     P("B: mid rejection", "high reaches the BB mid, close below it, mid lower than 5 days ago; filters RSI < 60, lower band touched, RSI under its SMA"),
     P("Exits", "10-day and 20-day hold; band exit (lower band target, close above the signal high stop)"), FEE],
    "daily_div_mid_reject.py, Binance spot daily 2017-08..2026-10; in-sample to 2022-12, out-of-sample from 2023-01.",
    "NO: no variant beats simply being short every day in both periods.", "bad",
    ["Daily samples are small (13-54 per period): only a ~5% per trade edge could be seen.",
     "Mid rejection beat the base by 3.3% in-sample but only 0.1% out-of-sample.",
     "His 2026 examples did work (10-20 +3.4% in 5 days), which is why it looks tradable on the chart."],
    [{"label": "Base short, 10 days", "value": "-1.76% / -1.54%"}, {"label": "A divergence, 10 days", "value": "-3.2% / -1.7%", "tone": "bad"},
     {"label": "B mid rejection, 10 days", "value": "+1.55% / -1.42%", "tone": "bad"}],
    [table("10-day short return per signal", ["Signal", "n", "to 2022-12", "from 2023-01"],
           [["Base (every day)", "-", "-1.76%", "-1.54%"], ["A divergence", "25/27", "-3.2%", "-1.7%"], ["A_major", "16/13", "-1.6%", "-1.6%"],
            ["B mid rejection", "54/49", "+1.55%", "-1.42%"], ["B + lower band", "28/35", "+3.8%", "-1.9%"]])],
    ["daily_div_mid_reject.py"]))

out.append(base("eagle-c24-oi-after-flush", "C24: after a long flush, does the open-interest path call the next move?",
    [P("Flush", "5m bar with price -0.25% or worse and Bybit OI -0.2% or worse"), P("Chop", "price moves under 0.8% over the next 40 min"),
     P("Groups", "OI over those 40 min: rebuilds >= +0.2%, flat, keeps falling <= -0.2%"), P("Data", "Bybit linear BTCUSDT 5m, 120 days")],
    "oi_after_flush.py; next 1h and 4h move vs every-30-min base. No trade, no fees.",
    "NO direction: all groups near a coin flip (4h up 53/56/55% vs 52% base).", "info",
    ["Still-falling OI makes a >1% move in 4h more likely (14% vs 6%), but not which way.",
     "OI tells who is trapped when a level breaks, not where price goes; this feeds the dashboard 'What the money is doing' tile."],
    [{"label": "n (rebuild / flat / falling)", "value": "18 / 9 / 22"}, {"label": "4h up", "value": "53 / 56 / 55% vs 52%"},
     {"label": "4h move > 1% down, OI falling", "value": "14% vs 6%", "tone": "warn"}],
    [{"kind": "none", "title": "Examples", "caption": "no example trades exported: event study, no trade rule"}],
    ["oi_after_flush.py"], date="2026-10-31"))
for r in out:
    r["window"] = WIN if r["id"] not in ("eagle-c23-daily-shorts", "eagle-c24-oi-after-flush") else (
        "2017-08-17 to 2026-10-29, split at 2023-01-01 (whole history read)" if r["id"] == "eagle-c23-daily-shorts" else "2026-07-02 to 2026-10-30 (Bybit 5m)")
    with open(os.path.join(OUT, r["id"] + ".json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(r, f, separators=(",", ":"))
    print("wrote", r["id"], "replay trades %d" % len(r["examples"][0].get("trades", [])) if r["examples"][0]["kind"] == "replay" else "")
