"""Capture channel + missed-trade analysis. Expected values are worked by hand in the comments."""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import capture  # noqa: E402
import missed  # noqa: E402

T0 = "2026-10-07T21:00:00Z"


def setup_rec(**kw):
    base = {"session": "desk-1", "kind": "chart_read", "text": "fade the range top", "symbol": "BTCUSDT",
            "timeframe": "15m", "ts_market": T0, "side": "short", "entry": 83550, "stop": 83800, "target": 83050}
    base.update(kw)
    return base


def write_bars(d, start, rows):
    """rows: (o, h, l, c) per minute from start."""
    d.mkdir(parents=True, exist_ok=True)
    t = datetime.fromisoformat(start.replace("Z", "+00:00"))
    lines = ["t,o,h,l,c"]
    for i, (o, h, l, c) in enumerate(rows):
        ms = int((t + timedelta(minutes=i)).timestamp() * 1000)
        lines.append(f"{ms},{o},{h},{l},{c}")
    (d / f"{t.date().isoformat()}.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---- capture ---------------------------------------------------------------

def test_naive_time_refused_and_ist_converted():
    with pytest.raises(capture.ObsError):
        capture.parse_time("2026-10-08 02:47")
    # 02:47 IST = 21:17 UTC the previous day
    assert capture.iso(capture.parse_time("2026-10-08 02:47", "+05:30")) == "2026-10-07T21:17:00Z"


def test_chart_read_must_be_labeled_chart_read(tmp_path):
    with pytest.raises(capture.ObsError, match="rule 4"):
        capture.append(setup_rec(label="system"), tmp_path)


def test_setup_without_stop_refused(tmp_path):
    with pytest.raises(capture.ObsError, match="no invalidation"):
        capture.append(setup_rec(stop=None), tmp_path)


def test_stop_on_wrong_side_refused(tmp_path):
    with pytest.raises(capture.ObsError, match="above entry"):
        capture.append(setup_rec(stop=83400), tmp_path)


def test_append_only_and_build(tmp_path):
    now = datetime(2026, 10, 7, 21, 5, tzinfo=timezone.utc)
    a = capture.append(setup_rec(), tmp_path, now=now)
    capture.append(setup_rec(text="second read"), tmp_path, now=now + timedelta(seconds=1))
    corr = capture.append({"session": "desk-1", "kind": "correction", "text": "first read was wrong",
                           "ts_market": T0, "supersedes": a["obs_id"]}, tmp_path, now=now + timedelta(seconds=2))
    f = tmp_path / "captures" / "2026-10-07.jsonl"
    assert len(f.read_text(encoding="utf-8").splitlines()) == 3
    with open(f, "a", encoding="utf-8") as h:
        h.write("not json\n")
    res = capture.build(tmp_path)
    # 3 valid, 1 superseded -> 1 setup left; the bad line is kept as a reject
    assert res == {"observations": 3, "setups": 1, "rejects": 1, "dir": str(tmp_path / "derived")}
    rows = (tmp_path / "derived" / "setups.csv").read_text(encoding="utf-8").splitlines()
    assert len(rows) == 2 and "second read" in rows[1]
    obs = [json.loads(x) for x in (tmp_path / "derived" / "observations.jsonl").read_text(encoding="utf-8").splitlines()]
    assert {o["obs_id"]: o["superseded"] for o in obs}[a["obs_id"]] is True
    assert corr["label"] == "inferred"


def test_quality_flags():
    r = capture.validate(dict(setup_rec(target=None, entry=None), schema="obs.v1", ts_logged=T0,
                              chart={"source": "binance footprint"}))
    flags = capture.quality_flags(r)
    assert "footprint_no_zones" in flags and "no_target" in flags and "entry_at_market" in flags
    assert flags[0].startswith("six_layer_missing:panel+neutral")


def test_cli_add(tmp_path, capsys):
    rc = capture.main(["--dir", str(tmp_path), "add", "--session", "s", "--kind", "chart_read", "--symbol", "BTCUSDT",
                       "--tf", "5m", "--at", "2026-10-08 02:47", "--tz", "+05:30", "--side", "long",
                       "--stop", "82700", "--text", "absorption at lows", "--falsify", "15m close < 82706"])
    assert rc == 0 and "2026-10-07T21:17:00Z" in capsys.readouterr().out
    assert capture.main(["--dir", str(tmp_path), "add", "--session", "s", "--kind", "trade_call",
                         "--at", T0, "--text", "x", "--symbol", "BTCUSDT", "--tf", "5m"]) == 2  # no side


# ---- missed ----------------------------------------------------------------

def built_setup(**kw):
    r = capture.validate(dict(setup_rec(**kw), schema="obs.v1", ts_logged=T0))
    r["quality_flags"] = capture.quality_flags(r)
    return r


def ev(minute_offset, event, side="short", **kw):
    t = datetime(2026, 10, 7, 21, 0, tzinfo=timezone.utc) + timedelta(minutes=minute_offset)
    return dict({"ts": capture.iso(t), "_ts": t, "event": event, "side": side, "source": "layer:x"}, **kw)


def test_mts_reason_priority_and_window():
    s = built_setup()  # 15m -> window +-30 min
    evs = [ev(5, "skipped_halt", brakes=["HALT_DAILY_LOSS"]), ev(10, "layer_trade_blocked", reason="T055 no edge")]
    assert missed.mts_response(s, evs)[:2] == ("blocked", "T055 no edge")
    assert missed.mts_response(s, [ev(31, "trade_attempt", outcome="entered", plan_id="S1")])[0] == "no_signal"
    assert missed.mts_response(s, [ev(30, "trade_attempt", outcome="entered", plan_id="S1")])[:2] == ("entered", "S1")
    assert missed.mts_response(s, [ev(0, "signal_rejected", side="long", reason="x")])[0] == "opposite_signal"
    assert missed.mts_response(s, [ev(-5, "skipped_halt", brakes=["HALT_DAILY_LOSS"])])[:2] == ("halt", "HALT_DAILY_LOSS")


def test_score_short_limit_target():
    # short limit 83550, stop 83800, target 83050. Bar0 below entry (no fill), bar1 trades 83550 -> fill,
    # bar2 low 83000 <= target -> win. R = (83550-83050)/(83800-83550) = 500/250 = 2.0
    bars = [(datetime(2026, 10, 7, 21, i, tzinfo=timezone.utc), *x) for i, x in
            enumerate([(83400, 83450, 83350, 83420), (83420, 83560, 83400, 83500), (83500, 83520, 83000, 83100)])]
    out = missed.score(built_setup(), bars, timedelta(hours=1))
    assert out["outcome"] == "target" and out["r_multiple"] == 2.0
    assert out["fill_ts"] == "2026-10-07T21:01:00Z" and out["exit_ts"] == "2026-10-07T21:02:00Z"
    # mfe = 83550-83000 = 550 -> 2.2R ; mae = 83560-83550 = 10 -> 0.04R
    assert out["mfe_r"] == 2.2 and out["mae_r"] == 0.04


def test_score_same_bar_counts_as_stop_and_unfilled():
    bars = [(datetime(2026, 10, 7, 21, 0, tzinfo=timezone.utc), 83550, 83900, 83000, 83500)]
    assert missed.score(built_setup(), bars, timedelta(hours=1))["outcome"] == "stop"
    far = [(datetime(2026, 10, 7, 21, 0, tzinfo=timezone.utc), 83000, 83100, 82900, 83000)]
    assert missed.score(built_setup(), far, timedelta(hours=1))["outcome"] == "not_filled"


def test_score_long_at_market_no_target():
    # long at market: entry = close of bar holding the read = 100; stop 90 -> risk 10.
    # later high 125 -> mfe 2.5R, low 95 -> mae 0.5R, no stop hit, no target -> no_target
    s = built_setup(side="long", entry=None, stop=90, target=None)
    bars = [(datetime(2026, 10, 7, 21, i, tzinfo=timezone.utc), *x) for i, x in
            enumerate([(99, 101, 98, 100), (100, 125, 95, 120)])]
    out = missed.score(s, bars, timedelta(hours=1))
    assert out == {"outcome": "no_target", "fill_ts": "2026-10-07T21:00:00Z", "exit_ts": None,
                   "r_multiple": None, "mfe_r": 2.5, "mae_r": 0.5}


def test_end_to_end_missed_report(tmp_path):
    obs, bars_dir = tmp_path / "obs", tmp_path / "bars"
    capture.append(setup_rec(), obs, now=datetime(2026, 10, 7, 21, 0, 5, tzinfo=timezone.utc))
    capture.append(setup_rec(symbol="ETHUSDT", text="eth read"), obs, now=datetime(2026, 10, 7, 21, 0, 6, tzinfo=timezone.utc))
    capture.build(obs)
    write_bars(bars_dir, T0, [(83400, 83450, 83350, 83420), (83420, 83560, 83400, 83500), (83500, 83520, 83000, 83100)])
    trades = tmp_path / "auto_trades.jsonl"
    trades.write_text(json.dumps({"ts": "2026-10-07T21:03:00Z", "event": "skipped_halt", "source": "layer:rsi",
                                  "side": "short", "brakes": ["HALT_DAILY_LOSS"]}) + "\n", encoding="utf-8")
    assert missed.main(["--dir", str(obs), "--auto-trades", str(trades), "--bars", str(bars_dir),
                        "--klines", str(tmp_path / "none.json")]) == 0
    rows = (obs / "derived" / "missed.csv").read_text(encoding="utf-8").splitlines()
    assert len(rows) == 3
    rep = (obs / "derived" / "MISSED_REPORT.md").read_text(encoding="utf-8")
    assert "| MISSED | 1 |" in rep and "| UNRESOLVED | 1 |" in rep and "| halt | 1 |" in rep


def test_5m_kline_fallback_when_1m_recorder_has_gap(tmp_path):
    # 1m files end before the read; 5m klines cover it. Short 83550/83800/83050 at 21:00.
    # 5m bar 21:00 trades 83560 (fill), bar 21:05 low 83040 <= 83050 -> target, R 2.0, source 5m
    write_bars(tmp_path / "bars", "2026-10-07T07:00:00Z", [(1, 1, 1, 1)])
    t = datetime(2026, 10, 7, 21, 0, tzinfo=timezone.utc)
    k = [{"open_time": int((t + timedelta(minutes=5 * i)).timestamp() * 1000), "open": o, "high": h, "low": l, "close": c}
         for i, (o, h, l, c) in enumerate([(83400, 83560, 83390, 83500), (83500, 83510, 83040, 83100)])]
    kp = tmp_path / "k.json"
    kp.write_text(json.dumps(k), encoding="utf-8")
    row = missed.analyse([built_setup()], [], tmp_path / "bars", timedelta(hours=1), kp)[0]
    assert (row["bar_source"], row["outcome"], row["r_multiple"], row["verdict"]) == ("5m", "target", 2.0, "MISSED")
    assert row["mts_reason"] == "no_signal"
