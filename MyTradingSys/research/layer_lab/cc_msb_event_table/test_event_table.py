import importlib.util
from pathlib import Path

MODULE = Path(__file__).with_name("event_table.py")
SPEC = importlib.util.spec_from_file_location("cc_msb_event_table", MODULE)
event_table = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(event_table)

START = 1640995200000  # 2022-01-01 UTC
HOUR = 3_600_000
N = 50
# Body = close (o == c). 16 flat bars, then highs 103 (i18) and 102 (i21, lower high, confirmed i23),
# higher low 100.5 (i20) / 100.8 (i23); first close above 102 is bar 25 (24 is 101.5).
CLOSES = [100.0] * 18 + [103.0, 101.0, 100.5, 102.0, 101.0, 100.8, 101.5, 102.5] + [102.5] * 24
CLOSES[27] = 101.5   # close back inside after the break: no second row
CLOSES[28] = 102.6   # and above 102 again: still no second row


def _bars(closes=CLOSES, start=START):
    return [{"t": start + i * HOUR, "o": c, "h": c + 0.5, "l": c - 0.5, "c": c} for i, c in enumerate(closes)]


def _atr14(bars, i):
    # independent hand formula (FORMULAS.md section 12): mean of the last 14 true ranges
    trs = [max(bars[j]["h"] - bars[j]["l"], abs(bars[j]["h"] - bars[j - 1]["c"]),
               abs(bars[j]["l"] - bars[j - 1]["c"])) for j in range(i - 13, i + 1)]
    return sum(trs) / 14


def _rows(bars):
    return event_table.build_event_table(bars)


def test_one_up_msb_row_on_break_bar_with_hand_values():
    bars = _bars()
    bars[30]["h"] = 105.0   # forward high spike
    bars[35]["l"] = 101.0   # forward low
    rows = _rows(bars)
    assert len(rows) == 1
    row = rows[0]
    assert row["direction"] == "up" and row["side"] == "long" and row["status"] == "OK"
    assert row["event_t"] == bars[25]["t"]          # first close above the lower high 102
    assert row["swing_t"] == bars[21]["t"]
    assert row["entry_t"] == bars[26]["t"] and row["entry"] == bars[26]["o"] == 102.5
    atr = _atr14(bars, 25)                           # bars closed at the entry bar open
    assert row["risk_r"] == atr
    assert row["bars_forward"] == 24
    assert abs(row["mfe_R"] - (105.0 - 102.5) / atr) < 1e-12
    assert abs(row["mae_R"] - (102.5 - 101.0) / atr) < 1e-12


def test_swing_not_used_before_confirmed_and_fires_once():
    rows = _rows(_bars())
    up = [r for r in rows if r["swing_t"] == START + 21 * HOUR]
    assert len(up) == 1                              # re-break on bars 26/28 gives no second row
    assert up[0]["event_t"] >= up[0]["swing_t"] + 3 * HOUR   # confirmed_i = i + 2, so break > i + 2


def test_bars_after_break_do_not_change_the_event():
    base = _rows(_bars())[0]
    altered = _bars()
    for k in range(26, N):
        altered[k]["o"] = altered[k]["c"] = 500.0
        altered[k]["h"], altered[k]["l"] = 501.0, 499.0
    alt = _rows(altered)[0]
    assert (alt["event_t"], alt["swing_t"], alt["direction"]) == (base["event_t"], base["swing_t"], base["direction"])


def test_gap_in_forward_window_is_not_in_data():
    bars = _bars()
    del bars[40]
    row = _rows(bars)[0]
    assert row["status"] == "NOT_IN_DATA" and row["mfe_R"] == "" and row["mae_R"] == ""


def test_short_forward_window_is_not_in_data():
    row = _rows(_bars()[:45])[0]
    assert row["status"] == "NOT_IN_DATA" and row["bars_forward"] == 0


def test_close_that_stays_inside_gives_no_row():
    closes = list(CLOSES)
    closes[25] = 101.9
    closes[26:] = [101.9] * (N - 26)
    assert _rows(_bars(closes)) == []


def test_down_msb_mirrors_to_short():
    closes = [200.0 - c for c in CLOSES]
    bars = _bars(closes)
    row = _rows(bars)[0]
    assert row["direction"] == "down" and row["side"] == "short" and row["status"] == "OK"
    assert row["event_t"] == bars[25]["t"] and row["swing_t"] == bars[21]["t"]


def test_bars_outside_dev_are_never_used():
    assert _rows(_bars(start=event_table.DEV_END_MS)) == []
