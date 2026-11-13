"""Offline tests for recorder.py (design v1 section 7 + v2). Fakes only, no network, no exchange credentials.

Expected values are computed here by hand from the rule text (Binance kline row layout, delta = taker buy - taker sell
= 2*takerBuyBase - volume, cadence words of OPERATOR_DECISIONS.md 2026-11-12 13:05Z), never copied from recorder output.
Run: python -m pytest MyTradingSys/execution/us_open_trader/test_recorder.py
"""
import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

import pytest  # noqa: E402

import recorder  # noqa: E402

U = timezone.utc


def dt(h, m, s=0, day=13, month=11, year=2026):
    return datetime(year, month, day, h, m, s, tzinfo=U)


WINTER_OPEN = dt(14, 30)           # 2026-11-13, US on EST: 09:30 ET = 14:30Z
SUMMER_OPEN = dt(13, 30, day=15, month=7)   # EDT: 13:30Z


# ---------------------------------------------------------------- cadence
@pytest.mark.parametrize("now,expect", [
    (dt(3, 10), dt(4, 0, 5)),            # hourly before T-2h
    (dt(4, 0, 5), dt(5, 0, 5)),          # strictly after now
    (dt(10, 20), dt(11, 0, 5)),
    (dt(12, 0, 5), dt(12, 30, 5)),       # hourly slot 12:00 done; next is T-2h itself (14:30 - 2h = 12:30)
    (dt(12, 29, 59), dt(12, 30, 5)),     # one second before T-2h
    (dt(12, 30, 5), dt(12, 45, 5)),      # 15 min from T-2h
    (dt(13, 0, 0), dt(13, 0, 5)),        # before the +5 s offset of the same slot
    (dt(14, 15, 5), dt(14, 28, 5)),      # 15-min phase ends at T-2 min: next is the first 1-min slot
    (dt(14, 28, 5), dt(14, 29, 5)),
    (dt(14, 29, 5), dt(14, 30, 5)),      # the open itself
    (dt(14, 30, 5), dt(14, 31, 5)),
    (dt(14, 44, 5), dt(14, 45, 5)),      # T+15 is the last 1-min reading
    (dt(14, 45, 5), dt(15, 0, 5)),       # after: 15 min
    (dt(15, 0, 5), dt(15, 15, 5)),
    (dt(15, 7, 0), dt(15, 15, 5)),
    (dt(20, 30, 5), dt(20, 45, 5)),
    (dt(20, 45, 5), dt(21, 0, 5)),       # 21:00Z slot is the last
    (dt(21, 0, 5), None),                # stop at 21:00Z
    (dt(22, 0, 0), None),
])
def test_next_due_winter(now, expect):
    assert recorder.next_due(now, WINTER_OPEN) == expect


@pytest.mark.parametrize("now,expect", [
    (dt(9, 59, 59, 15, 7), dt(10, 0, 5, 15, 7)),
    (dt(11, 30, 5, 15, 7), dt(11, 45, 5, 15, 7)),   # T-2h = 11:30 for a 13:30 open
    (dt(13, 15, 5, 15, 7), dt(13, 28, 5, 15, 7)),
    (dt(13, 28, 5, 15, 7), dt(13, 29, 5, 15, 7)),
    (dt(13, 44, 5, 15, 7), dt(13, 45, 5, 15, 7)),
    (dt(13, 45, 5, 15, 7), dt(14, 0, 5, 15, 7)),
    (dt(20, 45, 5, 15, 7), dt(21, 0, 5, 15, 7)),
    (dt(21, 0, 5, 15, 7), None),
])
def test_next_due_summer(now, expect):
    assert recorder.next_due(now, SUMMER_OPEN) == expect


def test_next_due_custom_until():
    assert recorder.next_due(dt(15, 0, 5), WINTER_OPEN, until=dt(15, 10)) is None
    assert recorder.next_due(dt(14, 45, 5), WINTER_OPEN, until=dt(15, 10)) == dt(15, 0, 5)


def test_readings_per_session_count():
    """Walk the whole day from 12:00:00: 1-min phase has 18 readings (T-2 .. T+15 inclusive)."""
    t, n_fast, seen = dt(12, 0, 0), 0, []
    while True:
        t = recorder.next_due(t, WINTER_OPEN)
        if t is None:
            break
        seen.append(t)
    fast = [x for x in seen if dt(14, 28) <= x < dt(14, 46)]
    assert len(fast) == 18
    assert seen[-1] == dt(21, 0, 5)
    assert all(b > a for a, b in zip(seen, seen[1:]))


def test_open_for_is_dst_aware():
    assert recorder.open_for(date(2026, 11, 13)) == dt(14, 30)
    assert recorder.open_for(date(2026, 10, 30)) == dt(13, 30, day=30, month=10)   # DST ends Sun 2026-11-01
    assert recorder.open_for(date(2026, 11, 2)) == dt(14, 30, day=2)
    assert recorder.open_for(date(2026, 3, 9)) == dt(13, 30, day=9, month=3)       # DST starts Sun 2026-03-08


# ---------------------------------------------------------------- indicators
def test_rsi_all_up_is_100_and_known_value():
    assert recorder.rsi([float(i) for i in range(1, 30)]) == 100.0
    # 15 closes alternating +2 / -1 : first 14 changes -> 7 gains of 2, 7 losses of 1 -> RS = 2 -> RSI = 100-100/3
    closes = [100.0]
    for i in range(14):
        closes.append(closes[-1] + (2 if i % 2 == 0 else -1))
    assert recorder.rsi(closes) == pytest.approx(100 - 100 / 3)


def test_bb_known_values():
    closes = [10.0] * 10 + [12.0] * 10        # mean 11, population sd 1
    b = recorder.bb(closes)
    assert b == {"mid": 11.0, "up": 13.0, "lo": 9.0, "width_pct": round(4 / 11 * 100, 3)}


# ---------------------------------------------------------------- fakes
def kline(t_ms, c, h, l, vol, taker_buy):
    return [t_ms, str(c), str(h), str(l), str(c), str(vol), t_ms + 59999, "0", 1, str(taker_buy), "0", "0"]


# minute opens ending just before the reading at 14:31:05 -> closed bars open 14:28, 14:29, 14:30; forming bar 14:31
def ms(h, m, day=13):
    return int(dt(h, m, day=day).timestamp() * 1000)


SPOT = [
    kline(ms(14, 28), 69000, 69010, 68990, 10.0, 7.0),   # delta = 14-10 = +4
    kline(ms(14, 29), 69020, 69100, 69005, 4.0, 1.0),    # delta = 2-4 = -2
    kline(ms(14, 30), 69050, 69200, 69015, 6.0, 5.0),    # delta = 10-6 = +4
    kline(ms(14, 31), 69060, 69070, 69050, 1.0, 1.0),    # forming: must be ignored
]


def good_fetch(spot=None, raise_hosts=()):
    spot = SPOT if spot is None else spot

    def f(url, timeout=5):
        for h in raise_hosts:
            if h in url:
                raise TimeoutError("fake dead " + h)
        if "data-api.binance.vision" in url:
            return spot
        if "bybit.com/v5/market/tickers" in url:
            return {"result": {"list": [{"lastPrice": "69050", "markPrice": "69049", "openInterest": "50000",
                                         "openInterestValue": "3452500000", "fundingRate": "0.0001", "volume24h": "9000"}]}}
        if "account-ratio" in url:
            return {"result": {"list": [{"buyRatio": "0.55", "sellRatio": "0.45"}]}}
        if "bybit.com/v5/market/kline" in url:
            # newest first, first row is the forming bar; 30 closed bars closing 1..30 plus the forming one
            rows = [[str(1000 + i), "0", "0", "0", str(float(c)), "0", "0"] for i, c in enumerate(range(1, 32))]
            return {"result": {"list": list(reversed(rows))}}
        if "okx.com" in url and "open-interest" in url:
            return {"data": [{"oiCcy": "12345.5"}]}
        if "okx.com" in url and "funding-rate" in url:
            return {"data": [{"fundingRate": "0.00005"}]}
        if "deribit.com" in url:
            return {"result": [{"mark_price": 69040.5, "open_interest": 1.5e9, "funding_8h": 0.0002, "volume_usd": 2e9}]}
        if "fapi.binance.com" in url:
            if "premiumIndex" in url:
                return {"markPrice": "69045", "lastFundingRate": "0.0001"}
            return {"openInterest": "80000"}
        raise AssertionError("unexpected url " + url)

    return f


def fresh_state():
    return recorder.new_state()


def make_reading(fetch, now=dt(14, 31, 5), state=None, levels=(), notes=()):
    st = state if state is not None else fresh_state()
    return recorder.reading(now, st, fetch, list(levels), list(notes), local=False), st


# ---------------------------------------------------------------- reading
def test_reading_keys_and_numbers():
    rec, st = make_reading(good_fetch(), levels=[69000, 69150, 70000])
    for k in ("ts_utc", "kind", "src", "binance_spot", "bybit", "bybit_1m", "bybit_15m", "okx", "deribit", "levels_touched", "gaps"):
        assert k in rec
    assert rec["ts_utc"] == "2026-11-13T14:31:05Z" and rec["kind"] == "reading"
    s = rec["binance_spot"]
    # first reading of the day counts the newest closed bar only (stop-gap behaviour): the 14:30 bar
    assert s["price"] == 69050.0 and s["bars"] == 1
    assert s["hi_since_last"] == 69200.0 and s["lo_since_last"] == 69015.0
    assert s["vol_btc_since_last"] == 6.0
    assert s["net_delta_btc_since_last"] == 4.0          # 2*5 - 6
    assert s["cvd_btc_since_start"] == 4.0
    assert rec["levels_touched"] == [69150]             # in [69015,69200]; 69000 and 70000 are not
    assert rec["bybit"]["long_share"] == 0.55 and rec["bybit"]["oi_btc"] == 50000.0 and rec["bybit"]["funding"] == 0.0001
    assert rec["okx"] == {"oi_btc": 12345.5, "funding": 0.00005}
    assert rec["deribit"]["mark"] == 69040.5
    # closed closes are 1..30: RSI of a straight rise is 100, bb mid = mean of last 20 = 20.5
    assert rec["bybit_1m"]["rsi14"] == 100.0 and rec["bybit_1m"]["bb20"]["mid"] == 20.5 and rec["bybit_1m"]["close"] == 30.0
    # stated gaps present in every record
    g = " | ".join(rec["gaps"])
    assert "liquidations" in g and "coinglass" in g and rec["binance_perp"]["mark"] == 69045.0


def test_second_reading_counts_only_new_bars_cvd_accumulates():
    f = good_fetch()
    rec1, st = make_reading(f)
    more = SPOT[:3] + [kline(ms(14, 31), 69060, 69300, 69040, 3.0, 3.0),     # delta +3
                       kline(ms(14, 32), 69070, 69080, 69060, 1.0, 0.0)]     # forming
    rec2 = recorder.reading(dt(14, 32, 5), st, good_fetch(spot=more), [], [], local=False)
    s = rec2["binance_spot"]
    assert s["bars"] == 1 and s["net_delta_btc_since_last"] == 3.0
    assert s["cvd_btc_since_start"] == 7.0 and s["hi_since_last"] == 69300.0


def test_venue_raising_is_a_gap_others_intact():
    rec, _ = make_reading(good_fetch(raise_hosts=("okx.com", "fapi.binance.com", "bybit.com/v5/market/tickers")))
    assert "error" in rec["okx"] and "error" in rec["bybit"]
    assert rec["deribit"]["mark"] == 69040.5
    assert rec["binance_spot"]["price"] == 69050.0
    assert rec["bybit_1m"]["close"] == 30.0
    txt = " | ".join(rec["gaps"])
    assert "okx" in txt and "bybit" in txt and "binance_perp" in txt
    json.dumps(rec, allow_nan=False)


def test_ratio_failure_keeps_bybit_ticker_with_null_shares():
    rec, _ = make_reading(good_fetch(raise_hosts=("account-ratio",)))
    assert rec["bybit"]["last"] == 69050.0
    assert rec["bybit"]["long_share"] is None and rec["bybit"]["short_share"] is None
    assert any("bybit_ratio" in g for g in rec["gaps"])
    json.dumps(rec, allow_nan=False)


def test_spot_dead_gives_error_no_cvd_change_and_no_touched():
    rec, st = make_reading(good_fetch(raise_hosts=("data-api.binance.vision",)), levels=[69000])
    assert "error" in rec["binance_spot"] and rec["levels_touched"] == []
    assert st["cvd"] == 0.0


def test_empty_bybit_ratio_list_is_none_not_nan():
    f0 = good_fetch()

    def f(url, timeout=5):
        if "account-ratio" in url:
            return {"result": {"list": []}}
        return f0(url, timeout)
    rec, _ = make_reading(f)
    assert rec["bybit"]["long_share"] is None
    s = json.dumps(rec, allow_nan=False)
    assert "NaN" not in s


def test_nan_and_inf_are_sanitised():
    assert recorder.clean({"a": float("nan"), "b": [float("inf"), 1.5], "c": {"d": float("-inf")}}) == {"a": None, "b": [None, 1.5], "c": {"d": None}}


def test_slow_venue_cannot_delay_past_deadline():
    import time as _t
    f0 = good_fetch()

    def f(url, timeout=5):
        if "deribit.com" in url:
            _t.sleep(1.0)
        return f0(url, timeout)
    t0 = _t.time()
    rec = recorder.reading(dt(14, 31, 5), fresh_state(), f, [], [], local=False, deadline_s=0.2)
    assert _t.time() - t0 < 0.9
    assert "error" in rec["deribit"] and "timeout" in rec["deribit"]["error"]
    assert rec["binance_spot"]["price"] == 69050.0


def test_default_fetch_passes_5s_timeout(monkeypatch):
    seen = {}

    class R:
        def read(self):
            return b"[1]"

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def fake_urlopen(req, timeout=None):
        seen["t"] = timeout
        return R()
    monkeypatch.setattr(recorder.urllib.request, "urlopen", fake_urlopen)
    assert recorder.http_get("http://x") == [1]
    assert seen["t"] == 5 and recorder.CALL_TIMEOUT_S == 5


# ---------------------------------------------------------------- restart / CVD
def write_lines(path, lines):
    path.write_text("".join(lines), encoding="utf-8", newline="\n")


def test_restart_resumes_cvd_from_last_line(tmp_path):
    p = tmp_path / "readings_2026-11-13.jsonl"
    last = {"ts_utc": "2026-11-13T14:31:05Z", "binance_spot": {"cvd_btc_since_start": 123.5, "last_bar_t": ms(14, 30)}}
    write_lines(p, [json.dumps({"ts_utc": "x"}) + "\n", json.dumps(last) + "\n"])
    st = recorder.load_state(p)
    assert st["cvd"] == 123.5 and st["last_t"] == ms(14, 30) and st["flags"] == []
    # next reading adds only bars newer than 14:30 : the 14:31 bar (+3)
    more = SPOT[:3] + [kline(ms(14, 31), 69060, 69300, 69040, 3.0, 3.0), kline(ms(14, 32), 1, 1, 1, 1.0, 0.0)]
    rec = recorder.reading(dt(14, 32, 5), st, good_fetch(spot=more), [], [], local=False)
    assert rec["binance_spot"]["cvd_btc_since_start"] == 126.5 and rec["binance_spot"]["bars"] == 1


def test_restart_from_stopgap_line_without_last_bar_t(tmp_path):
    """The stop-gap record_now.py lines have no last_bar_t: bars closed before ts_utc must not be counted twice."""
    p = tmp_path / "r.jsonl"
    write_lines(p, [json.dumps({"ts_utc": "2026-11-13T14:30:05Z", "binance_spot": {"cvd_btc_since_start": 10.0}}) + "\n"])
    st = recorder.load_state(p)
    assert st["cvd"] == 10.0 and st["last_t"] == ms(14, 29)      # newest bar closed at 14:30:05 opened 14:29
    rec = recorder.reading(dt(14, 31, 5), st, good_fetch(), [], [], local=False)
    # bars after 14:29: the 14:30 bar only (+4)
    assert rec["binance_spot"]["cvd_btc_since_start"] == 14.0


def test_corrupt_last_line_resets_cvd_with_flag_no_crash(tmp_path):
    p = tmp_path / "r.jsonl"
    good = json.dumps({"ts_utc": "2026-11-13T14:30:05Z", "binance_spot": {"cvd_btc_since_start": 99.0, "last_bar_t": ms(14, 29)}})
    p.write_text(good + "\n" + '{"ts_utc": "2026-11-13T14:31:05Z", "binance_sp', encoding="utf-8")
    st = recorder.load_state(p)
    assert st["cvd"] == 0.0 and st["last_t"] == 0 and any("corrupt" in f for f in st["flags"])
    rec = recorder.reading(dt(14, 32, 5), st, good_fetch(), [], [], local=False)
    assert rec["binance_spot"]["cvd_btc_since_start"] == 4.0
    assert any("corrupt" in f for f in rec["flags"])
    rec2 = recorder.reading(dt(14, 33, 5), st, good_fetch(), [], [], local=False)
    assert not rec2.get("flags")


def test_missing_or_empty_file_is_fresh_no_flag(tmp_path):
    assert recorder.load_state(tmp_path / "none.jsonl")["flags"] == []
    e = tmp_path / "e.jsonl"
    e.write_text("", encoding="utf-8")
    assert recorder.load_state(e)["cvd"] == 0.0 and recorder.load_state(e)["flags"] == []


def test_state_skips_last_lines_without_cvd(tmp_path):
    p = tmp_path / "r.jsonl"
    a = {"ts_utc": "2026-11-13T14:30:05Z", "binance_spot": {"cvd_btc_since_start": 5.5, "last_bar_t": ms(14, 29)}}
    b = {"ts_utc": "2026-11-13T14:31:05Z", "binance_spot": {"error": "boom"}}
    write_lines(p, [json.dumps(a) + "\n", json.dumps(b) + "\n"])
    st = recorder.load_state(p)
    assert st["cvd"] == 5.5 and st["last_t"] == ms(14, 29)


# ---------------------------------------------------------------- levels
def test_levels_from_plan_json(tmp_path):
    plan = {"day": "2026-11-13", "orders": [
        {"id": "A", "trigger": 69620, "level": "Europe high 69,571"},
        {"id": "C", "trigger": 69980, "level": "analyst cluster 70,000"},
        {"id": "D", "trigger": 68120, "level": "200-week area 68,000-68,100"}], "levels": [67568]}
    p = tmp_path / "plan.json"
    p.write_text(json.dumps(plan), encoding="utf-8")
    lv, note = recorder.load_levels(p)
    assert lv == [67568, 68000, 68100, 68120, 69571, 69620, 69980, 70000] and note is None


def test_no_plan_json_gives_empty_list_and_note(tmp_path):
    lv, note = recorder.load_levels(tmp_path / "missing.json")
    assert lv == [] and "no plan" in note
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    lv, note = recorder.load_levels(bad)
    assert lv == [] and note
    rec = recorder.reading(dt(14, 31, 5), fresh_state(), good_fetch(), lv, [note], local=False)
    assert rec["levels_touched"] == [] and rec["notes"] == [note]


# ---------------------------------------------------------------- end to end main
def test_main_once_writes_one_strict_json_line(tmp_path, monkeypatch):
    monkeypatch.setenv("US_OPEN_TRADER_DIR", str(tmp_path))
    now = dt(14, 31, 5)
    rc = recorder.main(["--once", "--plan", str(tmp_path / "none.json"), "--no-local"], fetch=good_fetch(), clock=lambda: now, sleep=lambda s: None)
    assert rc == 0
    files = list(tmp_path.glob("readings_2026-11-13.jsonl"))
    assert len(files) == 1
    lines = files[0].read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    rec = json.loads(lines[0], parse_constant=lambda c: (_ for _ in ()).throw(ValueError(c)))
    assert rec["binance_spot"]["cvd_btc_since_start"] == 4.0


def test_main_loop_sleeps_to_next_due_and_stops_at_until(tmp_path, monkeypatch):
    monkeypatch.setenv("US_OPEN_TRADER_DIR", str(tmp_path))
    clock_t = [dt(20, 44, 0)]
    sleeps = []

    def sleep(s):
        sleeps.append(s)
        clock_t[0] += timedelta(seconds=s)
    rc = recorder.main(["--plan", str(tmp_path / "none.json"), "--no-local"], fetch=good_fetch(), clock=lambda: clock_t[0], sleep=sleep)
    assert rc == 0
    lines = (tmp_path / "readings_2026-11-13.jsonl").read_text(encoding="utf-8").splitlines()
    stamps = [json.loads(x)["ts_utc"] for x in lines]
    assert stamps == ["2026-11-13T20:44:00Z", "2026-11-13T20:45:05Z", "2026-11-13T21:00:05Z"]
    assert sleeps == [65.0, 900.0]


def test_main_restart_same_day_resumes_cvd(tmp_path, monkeypatch):
    monkeypatch.setenv("US_OPEN_TRADER_DIR", str(tmp_path))
    args = ["--once", "--plan", str(tmp_path / "none.json"), "--no-local"]
    recorder.main(args, fetch=good_fetch(), clock=lambda: dt(14, 31, 5), sleep=lambda s: None)
    more = SPOT[:3] + [kline(ms(14, 31), 69060, 69300, 69040, 3.0, 3.0), kline(ms(14, 32), 1, 1, 1, 1.0, 0.0)]
    recorder.main(args, fetch=good_fetch(spot=more), clock=lambda: dt(14, 32, 5), sleep=lambda s: None)
    lines = (tmp_path / "readings_2026-11-13.jsonl").read_text(encoding="utf-8").splitlines()
    assert json.loads(lines[1])["binance_spot"]["cvd_btc_since_start"] == 7.0


def test_local_sources_missing_are_recorded_not_fatal(tmp_path):
    """footprint / liquidations come from local files only; absent -> {"error"} entry, never a made-up number."""
    rec = recorder.reading(dt(14, 31, 5), fresh_state(), good_fetch(), [], [], local=True,
                           footprint_fn=lambda price, now_ms: (_ for _ in ()).throw(RuntimeError("no bars")),
                           liq_fn=lambda now_ms: {"BYBIT": {"long15": 1}})
    assert "error" in rec["footprint"]
    assert rec["liquidations"] == {"BYBIT": {"long15": 1}}
    json.dumps(rec, allow_nan=False)
