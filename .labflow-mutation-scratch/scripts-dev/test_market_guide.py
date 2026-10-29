"""pytest tests for market_guide.py (synthetic data in tmp dirs; expected numbers worked out by hand)."""
import json
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import market_guide as mg  # noqa: E402

H = 3600000
NOW = 40 * H  # 40h after epoch, aligned


def kline(open_time, ms, o, h, l, c, v=1.0):
    return {"open_time": open_time, "close_time": open_time + ms - 1, "open": o, "high": h, "low": l,
            "close": c, "volume": v}


def write_json(path, obj):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f)


def bars_from_closes(closes, ms=H):
    return [{"t": i * ms, "o": c, "h": c, "l": c, "c": c, "v": 1.0, "ct": i * ms + ms - 1}
            for i, c in enumerate(closes)]


def test_unclosed_bar_dropped(tmp_path):
    p = tmp_path / "k.json"
    # bar 2 closes at 3H-1; with now = 3H - 1 it is not yet closed (close_time >= now)
    write_json(p, [kline(0, H, 1, 2, 1, 2), kline(H, H, 2, 3, 2, 3), kline(2 * H, H, 3, 4, 3, 4)])
    got = mg.load_klines(str(p), 3 * H - 1)
    assert [b["t"] for b in got] == [0, H]
    assert [b["t"] for b in mg.load_klines(str(p), 3 * H)] == [0, H, 2 * H]


def test_4h_resample_complete_buckets_only():
    bars = []
    # hours 0..7 complete (2 buckets), hours 8..9 partial third bucket, bucket 4 (hours 16..19) missing hour 17
    for h in range(0, 10):
        bars.append({"t": h * H, "o": 10 + h, "h": 20 + h, "l": 5 + h, "c": 11 + h, "v": 2.0, "ct": h * H + H - 1})
    for h in (16, 18, 19):
        bars.append({"t": h * H, "o": 1, "h": 1, "l": 1, "c": 1, "v": 1.0, "ct": h * H + H - 1})
    out = mg.resample_4h(bars)
    assert [b["t"] for b in out] == [0, 4 * H]
    b0 = out[0]
    # hours 0..3: open of h0 = 10, close of h3 = 14, high max(20..23)=23, low min(5..8)=5, vol 8
    assert (b0["o"], b0["c"], b0["h"], b0["l"], b0["v"]) == (10, 14, 23, 5, 8.0)
    assert out[1]["o"] == 14 and out[1]["c"] == 18 and out[1]["h"] == 27 and out[1]["l"] == 9
    assert out[1]["ct"] == 7 * H + H - 1


def test_ema_cross_up_bars_ago():
    # 25 falling closes 100..76 (EMA9 < EMA21), then jump to 1000 (idx 25, EMA9=260.8 > EMA21~160), stays 3 more bars
    closes = [100 - i for i in range(25)] + [1000] * 4
    info = mg.ma_info(bars_from_closes(closes))
    assert info["cross_ema"] == ("up", 3)  # last index 28, cross at index 25


def test_ema_cross_down_bars_ago():
    # 25 rising 100..124 (EMA9 > EMA21), crash to 1 (EMA9 ~99.4 < EMA21 ~112.8) at idx 25, 3 more bars at 1
    closes = [100 + i for i in range(25)] + [1] * 4
    info = mg.ma_info(bars_from_closes(closes))
    assert info["cross_ema"] == ("down", 3)


def test_insufficient_bars_na():
    info = mg.ma_info(bars_from_closes([1.0 + i for i in range(10)]))
    names = {n: v for n, v, _ in info["rows"]}
    assert names["SMA20"] is None and names["SMA50"] is None and names["SMA200"] is None
    assert names["EMA9"] is not None and names["EMA21"] is None
    assert info["cross_ema"] is None and info["cross_sma"] is None and info["slope50"] is None
    assert mg.rsi_info(bars_from_closes([1.0, 2.0, 3.0]))["rsi"] is None


def test_sma50_slope_sign():
    closes = [float(i) for i in range(60)]
    assert mg.ma_info(bars_from_closes(closes))["slope50"] == "up"
    assert mg.ma_info(bars_from_closes(closes[::-1]))["slope50"] == "down"


def test_rsi_regime_side():
    up = mg.rsi_info(bars_from_closes([float(i) for i in range(1, 40)]))
    assert up["rsi"] == 100.0 and up["regime"].startswith("above") and up["level"] == 60.0
    assert up["dist"] == 40.0
    dn = mg.rsi_info(bars_from_closes([float(i) for i in range(40, 1, -1)]))
    assert dn["rsi"] == 0.0 and dn["regime"].startswith("below") and dn["level"] == 40.0
    assert dn["dist"] == -40.0


def test_malkan_levels_read_from_source():
    assert (mg.MALKAN_LO, mg.MALKAN_HI) == (40.0, 60.0)


def _alerts_file(tmp_path, rows):
    p = tmp_path / "5m.jsonl"
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    return str(p)


def test_turn_of_candle_excluded_and_24h_window(tmp_path):
    rows = [
        {"layer": "turn_of_candle", "sub": "x", "event": "toc", "tf": "5m", "t_close": NOW - 1000},
        {"layer": "rsi", "sub": "rsi_events", "event": "cross", "tf": "5m", "t_close": NOW - 1000},
        {"layer": "rsi", "sub": "rsi_events", "event": "cross", "tf": "5m", "t_close": NOW - 2 * 86400000},
    ]
    got = mg.load_alerts(_alerts_file(tmp_path, rows), NOW)
    assert len(got) == 1 and got[0]["layer"] == "rsi"
    assert mg.load_alerts(str(tmp_path / "missing.jsonl"), NOW) is None


def test_unknown_layer_untested(tmp_path):
    p = tmp_path / "verdicts.json"
    p.write_text(json.dumps({"fabio": {"tag": "NO-EDGE", "source": "x:1"}, "ma": {"tag": "UNTESTED", "source": "y:2"}}))
    v = mg.load_verdicts(str(p))
    assert mg.verdict_tag(v, "no_such_layer") == "UNTESTED"
    assert mg.verdict_tag(v, "fabio") == "NO-EDGE"
    assert mg.verdict_tag(v, "ma") == "UNTESTED"
    assert mg.load_verdicts(str(tmp_path / "missing.json")) == {}


def test_real_verdicts_every_entry_has_tag_and_source():
    v = mg.load_verdicts()
    assert v, "market_guide_verdicts.json missing or unreadable"
    for k, e in v.items():
        assert e["tag"] in ("EDGE", "NO-EDGE", "UNTESTED"), k
        assert e["source"], k


def _make_dirs(tmp_path, newest_5m_open):
    kd = tmp_path / "k"
    ad = tmp_path / "a"
    kd.mkdir()
    ad.mkdir()
    write_json(kd / "BTCUSDT_5m.json", [kline(newest_5m_open - i * 300000, 300000, 10, 11, 9, 10)
                                         for i in range(30, -1, -1)])
    write_json(kd / "BTCUSDT_15m.json", [kline(NOW - 900000 * (i + 1), 900000, 10, 11, 9, 10) for i in range(30, -1, -1)])
    write_json(kd / "BTCUSDT_1h.json", [kline(NOW - H * (i + 1), H, 10, 11, 9, 10) for i in range(30, -1, -1)])
    return str(kd), str(ad)


def test_stale_flag_and_fresh(tmp_path):
    mod = mg._load_candles()
    # fresh: newest 5m closed bar ends at NOW-1
    kd, ad = _make_dirs(tmp_path, NOW - 300000)
    fresh = mg.build(NOW, kd, ad, {}, mod)
    assert "FEED STALE" not in fresh
    assert "Context only - not trade signals. Verdict tags from backtests." in fresh
    # stale: newest 5m bar closed 11 minutes ago (> 2 bars = 10 min)
    (tmp_path / "s").mkdir()
    kd2, ad2 = _make_dirs(tmp_path / "s", NOW - 300000 - 11 * 60000)
    stale = mg.build(NOW, kd2, ad2, {}, mod)
    assert "FEED STALE: 5m" in stale
    assert "FEED STALE: 15m" not in stale


def test_atomic_write_no_tmp(tmp_path):
    out = tmp_path / "sub" / "market_guide.md"
    mg.write_atomic(str(out), "hello\n")
    mg.write_atomic(str(out), "again\n")
    assert out.read_text(encoding="utf-8") == "again\n"
    assert os.listdir(out.parent) == ["market_guide.md"]


def test_candle_info_last_three_bars():
    mod = mg._load_candles()
    # 8 flat-ish bars then a doji (body 0 <= 0.1*range) as the last bar -> doji at 0 bars ago
    bars = [{"t": i, "o": 10, "h": 12, "l": 8, "c": 11, "v": 1} for i in range(8)]
    bars.append({"t": 8, "o": 10, "h": 12, "l": 8, "c": 10, "v": 1})
    found = dict(mg.candle_info(bars, mod))
    assert found.get("doji") == 0


def test_volume_info_synthetic_slot_history():
    # Synthetic slot history with stride=6 (4h bars, 6 bars/day)
    # Slot 0 in cycles 0..4 have volumes: 100, 150, 120, 180, 140 (OURS: synthetic volumes)
    # Sorted: [100.0, 120.0, 140.0, 150.0, 180.0] -> median is 140.0 (OURS: hand-computed median)
    # Current bar (cycle 5, slot 0): volume = 280.0 (OURS: synthetic volume)
    # Hand-computed ratio: 280.0 / 140.0 = 2.0 (OURS: 280 / 140 = 2.0 exactly)
    # SOURCED: MyTradingSys/research/volume_2026-10-09/vfeat.py:13 (STRIDE={"4h": 6})
    # SOURCED: MyTradingSys/research/volume_2026-10-09/vfeat.py:14 (KBASE={"4h": 20})
    slot0_vols = [100.0, 150.0, 120.0, 180.0, 140.0, 280.0]  # 5 prior + current
    bars = []
    # 5 full cycles of 6 bars each (indices 0..29), then cycle 5 bar 0 (index 30)
    for c_idx in range(5):
        for s_idx in range(6):
            v = slot0_vols[c_idx] if s_idx == 0 else 50.0
            bars.append({"t": (c_idx * 6 + s_idx) * 14400000, "o": 10, "h": 11, "l": 9, "c": 10, "v": v})
    # current bar: cycle 5, slot 0
    bars.append({"t": 30 * 14400000, "o": 10, "h": 11, "l": 9, "c": 10, "v": slot0_vols[5]})

    info = mg.volume_info(bars)
    assert info["n"] == 5  # OURS: 5 prior same-slot bars
    assert info["baseline"] == 140.0  # OURS: hand-computed median
    assert info["relative_volume"] == 2.0  # OURS: hand-computed ratio 280.0 / 140.0 = 2.0
    assert info["label"] == "descriptive only"


def test_market_guide_build_prints_volume_line(tmp_path):
    mod = mg._load_candles()
    kd, ad = _make_dirs(tmp_path, NOW - 300000)
    verdicts = {"volume": {"tag": "NO-EDGE", "source": "test"}}
    text = mg.build(NOW, kd, ad, verdicts, mod)
    assert "## Volume [NO-EDGE]" in text
    assert "time-adjusted relative volume:" in text
    assert "slot baseline n=" in text
    assert "effort vs result, match OI scope" in text
    assert "descriptive only" in text



def test_falsifier_status_available_in_market_guide():
    # score-context-reads-automatically-carrie scope_in includes market_guide.py
    assert hasattr(mg, "falsifier_status")
    # SOURCED line: "Falsify: acceptance under 82630" (test_shot.py:211)
    # Level broken by close (OURS fixture)
    res = mg.falsifier_status("Falsify: acceptance under 82630", [{"o": 82700, "h": 82750, "l": 82500, "c": 82550}])
    assert res == "BROKEN"
