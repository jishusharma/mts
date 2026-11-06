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


# ---------------------------------------------------------------- order flow state (card live-orderflow-state-line)
# (minute of 2026-10-14 UTC, o, h, l, c, volume, taker_buy_volume), fapi BTCUSDT 1m 14:30..15:08Z
OF_1M = [
    (870, 82016.90, 82040.30, 81980.60, 82009.50, 231.995, 134.840),
    (871, 82009.50, 82022.10, 81950.50, 81985.60, 132.023, 84.352),
    (872, 81985.50, 82005.60, 81946.10, 82000.40, 76.467, 40.936),
    (873, 82000.30, 82009.00, 81940.00, 81969.00, 127.607, 66.030),
    (874, 81969.00, 82034.70, 81920.40, 82034.60, 118.173, 71.041),
    (875, 82034.70, 82060.40, 81955.30, 81962.20, 182.815, 119.513),
    (876, 81962.10, 81980.10, 81893.60, 81893.60, 156.293, 89.863),
    (877, 81893.60, 81990.00, 81864.40, 81880.00, 242.012, 102.857),
    (878, 81880.00, 81923.20, 81858.00, 81879.30, 178.201, 107.854),
    (879, 81879.30, 81887.40, 81807.00, 81830.00, 423.383, 85.891),
    (880, 81830.00, 81915.80, 81820.20, 81897.10, 209.404, 150.669),
    (881, 81897.10, 81916.90, 81841.40, 81858.20, 183.991, 112.424),
    (882, 81858.20, 81905.10, 81850.00, 81869.00, 171.605, 100.230),
    (883, 81869.00, 81885.40, 81807.60, 81813.50, 260.965, 130.660),
    (884, 81813.60, 81871.70, 81808.00, 81808.00, 191.218, 88.224),
    (885, 81808.00, 81838.20, 81755.20, 81834.70, 461.806, 212.178),
    (886, 81834.70, 81893.50, 81789.80, 81893.40, 334.261, 204.336),
    (887, 81893.40, 81938.80, 81861.00, 81906.70, 249.203, 169.852),
    (888, 81906.80, 81912.20, 81864.20, 81880.10, 131.476, 85.278),
    (889, 81880.10, 81884.00, 81729.10, 81746.70, 269.426, 100.778),
    (890, 81746.80, 81746.80, 81713.20, 81721.60, 243.754, 115.136),
    (891, 81721.50, 81792.40, 81713.60, 81792.30, 239.074, 189.122),
    (892, 81792.40, 81812.80, 81730.30, 81737.70, 190.068, 107.653),
    (893, 81737.80, 81737.80, 81701.00, 81704.30, 176.856, 76.726),
    (894, 81704.30, 81720.00, 81651.40, 81690.20, 514.517, 174.923),
    (895, 81690.20, 81793.40, 81679.30, 81788.40, 386.489, 276.618),
    (896, 81788.40, 81804.40, 81740.00, 81783.50, 368.323, 211.017),
    (897, 81783.50, 81818.00, 81783.40, 81817.70, 152.638, 115.990),
    (898, 81817.70, 81850.00, 81783.40, 81841.20, 183.257, 106.515),
    (899, 81841.20, 81935.90, 81834.90, 81926.40, 373.267, 271.894),
    (900, 81926.30, 81946.90, 81854.70, 81854.70, 410.553, 254.843),
    (901, 81854.70, 81861.90, 81760.00, 81760.10, 119.174, 47.308),
    (902, 81760.10, 81784.60, 81744.90, 81760.30, 200.305, 130.811),
    (903, 81760.30, 81778.80, 81745.00, 81767.00, 150.156, 89.864),
    (904, 81767.10, 81852.80, 81767.00, 81814.10, 182.510, 129.237),
    (905, 81814.10, 81836.00, 81791.90, 81826.20, 199.063, 112.597),
    (906, 81826.10, 81826.20, 81795.20, 81804.30, 51.893, 34.675),
    (907, 81804.20, 81813.20, 81706.10, 81706.10, 79.675, 35.098),
    (908, 81706.20, 81712.80, 81622.00, 81622.60, 313.355, 98.394),
]
# (minute, sumOpenInterest BTC), fapi openInterestHist 5m
OF_OI = [(810, 92543.425), (815, 92186.684), (820, 92133.843), (825, 92182.994), (830, 92199.995), (835, 92162.684), (840, 92267.187), (845, 92621.94), (850, 92634.852), (855, 92406.094), (860, 92585.261), (865, 92705.254), (870, 92859.464), (875, 92937.941), (880, 93012.029), (885, 93121.087), (890, 93163.699), (895, 93303.831), (900, 93541.348), (905, 93546.335)]
DAY0_1014 = 1791936000000  # 2026-10-14 00:00Z


def _of_bars():
    return [{"t": DAY0_1014 + m * 60000, "o": o, "h": h, "l": l, "c": c, "v": v, "tbv": tb,
             "ct": DAY0_1014 + m * 60000 + 59999} for m, o, h, l, c, v, tb in OF_1M]


def _of_oi():
    return [(DAY0_1014 + m * 60000, x) for m, x in OF_OI]


def test_orderflow_1m_state_at_1508z_matches_result_md():
    # RESULT.md section 1: price lower low 81622.0 at 15:08Z while CVD made a higher low, OI rising.
    # Halves 14:39-14:53 / 14:54-15:08: low 81701.0 -> 81622.0 (LL); CVD min -3838.8 -> -3630.0 (HL, by hand from tbv);
    # OI 14:05 92621.94 -> 15:05 93546.335 = +0.998%.
    s = mg.order_flow_state(_of_bars(), 15, _of_oi())
    assert (s["price"], s["level"], s["cvd"], s["oi"]) == ("LL", 81622.0, "HL", "up")
    assert abs(s["oi_pct"] - 0.998) < 0.001
    assert s["state"].startswith("bullish CVD divergence")
    lines = mg.order_flow_state_lines(_of_bars(), [], [], _of_oi())
    assert lines[0].startswith("1m @15:09Z: price LL 81622.0 | Binance CVD HL | OI 60m +1.00%")
    assert all("no tested edge" in x for x in lines)
    assert lines[1].startswith("5m: n/a") and lines[2].startswith("15m: n/a")


def test_orderflow_unclosed_bar_dropped_and_resample():
    raw = [[i * 60000, "1", "2", "0.5", "1.5", "10", i * 60000 + 59999, "0", 0, "6", "0", "0"] for i in range(10)]
    bars = mg.fapi_kline_bars(raw, 9 * 60000 + 59999)  # bar 9 not closed yet
    assert len(bars) == 9 and bars[0]["tbv"] == 6.0
    five = mg.resample(bars, 300000)  # only minutes 0..4 complete
    assert len(five) == 1 and five[0]["v"] == 50.0 and five[0]["tbv"] == 30.0


def test_vwap_00z_hlc3():
    # day 1: bars at 00:00 (hlc3 10, v 1) and 00:01 (hlc3 20, v 3); previous-day bar ignored -> (10+60)/4 = 17.5
    d = 86400000
    bars = [{"t": d - 60000, "h": 99, "l": 99, "c": 99, "v": 5, "ct": d - 1},
            {"t": d, "h": 12, "l": 8, "c": 10, "v": 1, "ct": d + 59999},
            {"t": d + 60000, "h": 21, "l": 19, "c": 20, "v": 3, "ct": d + 119999}]
    assert mg.vwap_00z(bars, d + 120000) == 17.5


def test_build_prints_orderflow_section_and_vwap_note(tmp_path):
    kd, ad = tmp_path / "k", tmp_path / "a"
    kd.mkdir()
    ad.mkdir()
    now = DAY0_1014 + (15 * 60 + 9) * 60000
    text = mg.build(now, str(kd), str(ad), {}, mg._load_candles(), orderflow=(_of_bars(), _of_oi()))
    assert "## Order flow, 1m/5m/15m (descriptive only, no tested edge" in text
    assert "- 1m @15:09Z: price LL 81622.0" in text
    assert "our 00:00Z VWAP" in text and "chart-relative" in text
