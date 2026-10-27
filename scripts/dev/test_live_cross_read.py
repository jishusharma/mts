"""live_cross_read: since-open baseline (prior-bar-close fix), rolling correlation, legend check, fixture I/O."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import live_cross_read as lcr  # noqa: E402

T0 = 1700000000  # any 5m-aligned-enough anchor; tests only use relative offsets


def test_since_open_uses_prior_bar_close():
    # Binance klines are stamped by OPEN time: bar keyed `open_ts` covers [open_ts, open_ts+300) and its
    # close is the open_ts+300 price. The since-open "price at open" must be the close of the PRIOR bar
    # (keyed open_ts-300), which closes exactly at open_ts.
    open_ts = T0
    series = {
        open_ts - 600: 100.50,
        open_ts - 300: 100.35,   # closes AT open_ts: the correct baseline
        open_ts: 99.98,          # closes at open_ts+300 (13:35 price): the old, wrong baseline
        open_ts + 300: 100.00,   # last bar
    }
    baseline, last, pct = lcr.since_open(series, open_ts)
    assert baseline == 100.35 and last == 100.00
    assert round(pct, 2) == -0.35  # correct: last/prior_close - 1
    old_wrong_pct = (last / series[open_ts] - 1) * 100
    assert round(old_wrong_pct, 2) == 0.02  # what the pre-fix baseline (bar AT open_ts) would have given


def test_since_open_no_bar_before_open_is_none():
    series = {T0 + 300: 100.0, T0 + 600: 101.0}
    baseline, last, pct = lcr.since_open(series, T0)
    assert baseline is None and pct is None and last == 101.0


def test_at_or_before():
    series = {T0: 1.0, T0 + 300: 2.0, T0 + 600: 3.0}
    assert lcr.at_or_before(series, T0 + 599) == 2.0
    assert lcr.at_or_before(series, T0 - 1) is None


def test_corr_perfect_and_too_few_points():
    assert round(lcr.corr([1, 2, 3, 4, 5], [2, 4, 6, 8, 10]), 6) == 1.0
    assert lcr.corr([1, 2, 3], [1, 2, 3]) != lcr.corr([1, 2, 3], [1, 2, 3])  # nan != nan, n < 5


def test_rolling_r_window_sizes_and_perfect_corr():
    n = 40
    a = {T0 + i * 300: 100 + i for i in range(n)}
    b = {T0 + i * 300: 200 + 2 * i for i in range(n)}  # perfectly correlated returns
    out = lcr.rolling_r(a, b, windows=((12, "last 1h"), (36, "last 3h"), (999, "all")))
    by_label = {label: (r, k) for label, r, k in out}
    assert round(by_label["last 1h"][0], 6) == 1.0 and by_label["last 1h"][1] == 12
    assert by_label["all"][1] == n - 1  # n-1 returns from n bars


def test_rolling_r_skips_non_consecutive_gaps():
    a = {T0: 100.0, T0 + 300: 101.0, T0 + 900: 103.0}  # gap: T0+600 missing, 300s step broken
    b = {T0: 50.0, T0 + 300: 51.0, T0 + 900: 52.0}
    out = lcr.rolling_r(a, b, windows=((10, "w"),))
    assert out[0][2] == 1  # only the one 300s-spaced pair (T0 -> T0+300) counts


def test_legend_check_bb20():
    closes_row = lambda c: [0, 0, 0, 0, c, 0]
    klines = [closes_row(100.0)] * 19 + [closes_row(140.0)]  # 19 at 100, 1 at 140 -> mean 102
    mid, up, lo = lcr.legend_check(klines, bb_window=20)
    assert round(mid, 2) == 102.0
    assert up > mid > lo


def test_default_open_ts_is_1330z():
    import datetime as dt
    now = dt.datetime(2026, 10, 27, 15, 0, tzinfo=dt.timezone.utc)
    ts = lcr.default_open_ts(now)
    got = dt.datetime.fromtimestamp(ts, dt.timezone.utc)
    assert (got.hour, got.minute) == (13, 30) and got.date() == now.date()


def test_report_lines_cover_since_open_and_correlation():
    btc = {T0 - 300: 99.0, T0: 100.0, T0 + 300: 101.0}
    others = {"ES=F": {T0 - 300: 10.0, T0: 10.1, T0 + 300: 10.2}}
    lines = lcr.report(btc, others, T0)
    text = "\n".join(lines)
    assert "SINCE OPEN" in text and "BTC" in text and "ES=F" in text
    assert "ROLLING 5m-return correlation" in text


def test_fixture_round_trip_offline(tmp_path):
    fixture = {
        "btc_5m": {str(T0 - 300): 100.35, str(T0): 99.98, str(T0 + 300): 100.0},
        "others_5m": {"ES=F": {str(T0 - 300): 10.0, str(T0): 10.0, str(T0 + 300): 10.0}},
        "open_ts": T0,
        "btc_1m": [[0, 0, 0, 0, 100.0, 0]] * 20,
    }
    p = tmp_path / "fixture.json"
    p.write_text(json.dumps(fixture), encoding="utf-8")
    btc_5m, others_5m, open_ts, btc_1m = lcr.load_fixture(p)
    assert open_ts == T0 and btc_5m[T0 - 300] == 100.35 and others_5m["ES=F"][T0] == 10.0
    assert lcr.main(["--fixture", str(p), "--legend"]) == 0  # runs end-to-end offline, no network


def test_main_fixture_without_legend_still_zero(tmp_path, capsys):
    fixture = {"btc_5m": {str(T0 - 300): 100.0, str(T0): 100.0}, "others_5m": {}, "open_ts": T0}
    p = tmp_path / "f2.json"
    p.write_text(json.dumps(fixture), encoding="utf-8")
    assert lcr.main(["--fixture", str(p)]) == 0
    out = capsys.readouterr().out
    assert "SINCE OPEN" in out
