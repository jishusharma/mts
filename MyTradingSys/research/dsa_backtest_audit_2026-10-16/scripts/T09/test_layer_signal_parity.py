"""T09: the 30-day DEV replay through the LIVE layer code (poll_once, fake fetch_fn, network patched to raise) agrees with the
backtest-side signal code per layer, with no network. Layers whose live adapter calls the same detector with the same parameters must
match exactly; the layers listed in KNOWN_DIVERGENT differ today and are pinned here (findings T09-F1..F5 in T09_live_parity.md): when a
fix lands, move the layer out of KNOWN_DIVERGENT and the exact-match check takes over.
Reads scripts/T09/out/parity_result.json (made by parity_core.py, ~25 min); runs the replay only when that file is missing."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

EXACT = ["cryptocred|sr_flip|1h", "cryptocred|sr_flip|15m", "cryptocred|failed_msb|1h", "cryptocred|failed_msb|15m",
         "fabio|cvd_absorption|1h", "fabio|cvd_absorption|15m", "session|session_momentum|15m", "turn_of_candle|turn_of_candle|1m"]
KNOWN_DIVERGENT = ["fabio|volume_fvg|15m", "fabio|volume_fvg|1h", "fabio|escalation|15m", "fabio|escalation|1h",
                   "positioning|funding_cvd_fade|1h", "rsi|rsi_events|5m", "rsi|rsi_events|15m", "rsi|rsi_events|1h",
                   "cryptocred|fib_pullback|15m", "cryptocred|fib_pullback|1h"]


def test_replay_signals_match_backtest():
    import parity_core as pc          # does not exist before T09 (fails on pre-change code)
    res = pc.load_or_run()
    assert res["network_attempts"] == 0, "a network path was reached during the replay"
    assert len(res["days"]) == 30 and res["n_errors"] == 0
    per = res["per_key"]
    for k in EXACT:
        b = per[k]["backtest"]
        assert per[k]["live_alerts"] > 0, k
        assert (b["side_diff"], b["live_only"], b["bt_only"], b["off_by_one"]) == (0, 0, 0, 0), (k, b)
        assert b["same"] == b["n"], (k, b)
    for k in KNOWN_DIVERGENT:
        b = per[k]["backtest"]
        assert b["side_diff"] + b["live_only"] + b["bt_only"] + b["off_by_one"] > 0, "now matches: remove %s from KNOWN_DIVERGENT" % k
    # volume_fvg: the live side is the mirror of the backtest 'bounce' reading (T09-F1)
    for k in ("fabio|volume_fvg|15m", "fabio|volume_fvg|1h"):
        assert per[k]["backtest"]["same"] == 0 and per[k]["backtest"]["side_diff"] > 0
