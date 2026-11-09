"""Daily session playbook (card daily-session-playbook-live-aid-1109). Expected numbers are written by hand from the fixture below.

Fixture: 28 days of 1h bars, 2026-10-05 (Mon) .. 2026-11-01 (Sun), plus 2026-11-02 up to 09:00Z. Every day, hour h (0..23):
open 100+h, close 101+h, high 103+h, low 99+h. On odd days of the month the Asia hour-3 high is 125 instead of 106.
So Asia (hours 0-7) is O 100 L 99 C 108 and H 110 (even day) or 125 (odd day); Europe (hours 7-12) is O 107 H 115 L 106 C 113;
US (hours 13-20) is O 113 H 123 L 112 C 121. Odd days in history: 15, even: 13.
"""
import datetime as dt
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_artifact  # noqa: E402
import daily_playbook as pb  # noqa: E402

UTC = dt.timezone.utc
HOUR = 3_600_000
JS = HERE / "playbook.js"
A = 110 / 99 - 1      # Asia range, even day
B = 125 / 99 - 1      # Asia range, odd day


def ms(y, m, d, h=0):
    return int(dt.datetime(y, m, d, h, tzinfo=UTC).timestamp() * 1000)


def make_bars(first=dt.date(2026, 10, 5), last=dt.date(2026, 11, 1), partial_until=(dt.date(2026, 11, 2), 10)):
    bars = []
    d = first
    while d <= last:
        for h in range(24):
            hi = 103 + h
            if h == 3 and d.day % 2 == 1:
                hi = 125
            bars.append((ms(d.year, d.month, d.day, h), 100.0 + h, float(hi), 99.0 + h, 101.0 + h))
        d += dt.timedelta(days=1)
    if partial_until:
        pd_, ph = partial_until
        for h in range(ph):
            bars.append((ms(pd_.year, pd_.month, pd_.day, h), 100.0 + h, 103.0 + h, 99.0 + h, 101.0 + h))
    return bars


BARS = make_bars()
DAY = dt.date(2026, 11, 2)
NOW = dt.datetime(2026, 11, 2, 10, 30, tzinfo=UTC)


def build(tmp_path, now=NOW, bars=BARS, day=DAY, ledger=None, **kw):
    led = tmp_path / "ledger.csv"
    if ledger is not None:
        led.write_text(ledger, encoding="utf-8", newline="\n")
    return pb.build(bars, day, now, ledger_path=led, **kw), led


# ---------- sessions and splits ----------

def test_session_windows_and_overlap():
    assert pb.SESSIONS == {"Asia": (0, 8), "Europe": (7, 13), "US": (13, 21)}
    assert pb.sessions_at(0) == ["Asia"] and pb.sessions_at(7.5) == ["Asia", "Europe"] and pb.sessions_at(8) == ["Europe"]
    assert pb.sessions_at(13) == ["US"] and pb.sessions_at(20.99) == ["US"] and pb.sessions_at(21) == [] and pb.sessions_at(23.5) == []


def test_fixture_bars_give_the_right_session_splits():
    st = pb.session_stats(BARS, dt.date(2026, 11, 1))          # odd day
    assert (st["Asia"]["o"], st["Asia"]["h"], st["Asia"]["l"], st["Asia"]["c"], st["Asia"]["bars"]) == (100, 125, 99, 108, 8)
    assert (st["Europe"]["o"], st["Europe"]["h"], st["Europe"]["l"], st["Europe"]["c"], st["Europe"]["bars"]) == (107, 115, 106, 113, 6)
    assert (st["US"]["o"], st["US"]["h"], st["US"]["l"], st["US"]["c"], st["US"]["bars"]) == (113, 123, 112, 121, 8)
    assert abs(st["Asia"]["range_pct"] - B) < 1e-12 and st["Asia"]["complete"] and st["US"]["complete"]
    assert pb.session_stats(BARS, dt.date(2026, 11, 2))["Asia"]["h"] == 110   # even day: no spike
    # a bar at 07:00Z belongs to Asia AND Europe, the 08:00Z bar to Europe only, 21:00Z to nobody
    odd = pb.session_stats(BARS, dt.date(2026, 10, 31))
    assert odd["Asia"]["bars"] == 8 and odd["Europe"]["bars"] == 6 and odd["US"]["bars"] == 8


def test_partial_session_is_flagged_and_missing_session_is_none():
    st = pb.session_stats(BARS, DAY)                           # bars to 09:00Z only
    assert st["Asia"]["complete"] is True
    assert st["Europe"]["complete"] is False and st["Europe"]["bars"] == 3 and st["Europe"]["h"] == 112   # hours 7,8,9: high 103+9
    assert st["US"] is None


# ---------- base rates ----------

def test_base_rates_from_history_only():
    r = pb.base_rates(BARS, DAY, "Asia")
    assert r["n"] == 28
    assert abs(r["range_p25"] - A) < 1e-12 and abs(r["range_p50"] - B) < 1e-12 and abs(r["range_p75"] - B) < 1e-12   # 13 even + 15 odd days
    assert abs(r["up_p50"] - (125 / 100 - 1)) < 1e-12 and abs(r["down_p50"] - (1 - 99 / 100)) < 1e-12
    assert r["up_share"] == 1.0                                # Asia closes 108 over its 100 open every day
    assert r["wd_n"] == 4 and abs(r["wd_range_p50"] - (A + B) / 2) < 1e-12   # Mondays 10-05 odd, 10-12 even, 10-19 odd, 10-26 even
    e = pb.base_rates(BARS, DAY, "Europe")
    assert e["n"] == 28 and abs(e["range_p50"] - (115 / 106 - 1)) < 1e-12


def test_base_rates_never_look_ahead():
    future = BARS + [(ms(2026, 11, 3, h), 100.0, 900.0, 1.0, 100.0) for h in range(24)]
    assert pb.base_rates(future, DAY, "Asia") == pb.base_rates(BARS, DAY, "Asia")


def test_incomplete_history_sessions_are_not_counted():
    cut = [b for b in BARS if not (b[0] == ms(2026, 10, 20, 5))]          # one Asia bar missing on 10-20
    assert pb.base_rates(cut, DAY, "Asia")["n"] == 27


# ---------- key levels and value area ----------

def test_value_area_hand_case():
    bars = [(0, 100.2, 102.9, 100.1, 102.0), (1, 101.2, 103.9, 101.1, 103.0), (2, 101.2, 101.9, 101.1, 101.5)]
    # bin 1: counts 100:1, 101:3, 102:2, 103:1 (total 7); POC bin 101; 70% = 4.9: add 102 (2 > 1 of bin 100) -> 5
    assert pb.value_area(bars, 1) == (101.0, 101.5, 103.0)
    assert pb.value_area([], 50) is None


def test_key_levels_prior_day_week_open():
    lv = pb.key_levels(BARS, DAY, NOW)
    assert (lv["PDH"], lv["PDL"], lv["PDC"]) == (126, 99, 124)            # Sun 11-01: odd-day spike 125, hour 23 high 126
    assert (lv["PWH"], lv["PWL"]) == (126, 99)                           # Mon 10-26 .. Sun 11-01
    assert lv["DAY_OPEN"] == 100 and lv["WEEK_OPEN"] == 100
    assert set(lv) >= {"VAL", "POC", "VAH"} and lv["VAL"] <= lv["POC"] <= lv["VAH"]


def test_key_levels_day_not_started_uses_last_close_as_open_and_says_so():
    later = dt.datetime(2026, 11, 2, 0, 0, tzinfo=UTC)
    lv = pb.key_levels([b for b in BARS if b[0] < ms(2026, 11, 2)], DAY, later)
    assert lv["DAY_OPEN"] is None and lv["PDH"] == 126 and lv["LAST"] == 124


# ---------- touch counts (history first touch from the session open) ----------

def test_touch_counts_hand_cases():
    # Asia open 100 every day: +5 % / -5 % never touched... hour 2 high is 105 -> UP first on all 28 days
    assert pb.touch_counts(BARS, DAY, "Asia", 0.05, 0.05) == {"n": 28, "UP": 28, "DOWN": 0, "BOTH": 0, "NEITHER": 0}
    # the hour-0 bar spans 99..103: +0.5 % and -0.5 % are in one bar -> BOTH (order inside a 1h bar is unknown)
    assert pb.touch_counts(BARS, DAY, "Asia", 0.005, 0.005)["BOTH"] == 28
    # +24 % only the odd-day spike (125) reaches; -5 % never
    assert pb.touch_counts(BARS, DAY, "Asia", 0.24, 0.05) == {"n": 28, "UP": 15, "DOWN": 0, "BOTH": 0, "NEITHER": 13}
    assert pb.touch_counts(BARS, DAY, "Asia", 5.0, 0.005)["DOWN"] == 28


def test_default_day_rolls_to_tomorrow_after_the_us_session():
    assert pb.default_day(dt.datetime(2026, 11, 8, 22, 32, tzinfo=UTC)) == dt.date(2026, 11, 9)
    assert pb.default_day(dt.datetime(2026, 11, 9, 5, 0, tzinfo=UTC)) == dt.date(2026, 11, 9)
    assert pb.default_day(dt.datetime(2026, 11, 9, 20, 59, tzinfo=UTC)) == dt.date(2026, 11, 9)


# ---------- scenarios, ledger rows ----------

def test_build_skips_finished_sessions_and_gives_two_or_three_scenarios_each(tmp_path):
    data, led = build(tmp_path)
    assert data["day"] == "2026-11-02" and data["built_utc"] == "2026-11-02T10:30:00Z"
    names = [s["name"] for s in data["sessions"]]
    assert names == ["Asia", "Europe", "US"]
    by = {s["name"]: s for s in data["sessions"]}
    assert by["Asia"]["status"] == "done" and by["Asia"]["scenarios"] == []
    assert by["Europe"]["status"] == "live" and by["US"]["status"] == "next"
    for n in ("Europe", "US"):
        sc = by[n]["scenarios"]
        assert 2 <= len(sc) <= 3, (n, sc)
        for s in sc:
            assert s["down"] < s["ref"] < s["up"]
            c = s["counts"]
            assert c["UP"] + c["DOWN"] + c["BOTH"] + c["NEITHER"] == c["n"] == 28
            assert s["likely"] in ("UP", "DOWN", "NONE") and s["invalid"] and s["idea"] and s["id"].startswith("S")


def test_typical_swing_scenario_hand_numbers(tmp_path):
    data, led = build(tmp_path)
    eu = next(s for s in data["sessions"] if s["name"] == "Europe")
    ts = next(s for s in eu["scenarios"] if s["kind"] == "swing")
    assert ts["ref"] == 107.0                                   # Europe opened 07:00Z at 107, session already running
    assert ts["up"] == pytest.approx(107 * (115 / 107), abs=0.06) and ts["down"] == pytest.approx(106.0, abs=0.06)
    # from every Europe open the hour-7 bar (106..110) touches 106 first, 115 never: DOWN 28. The mirror (up 0.93 %, down 7.5 %) is UP 28:
    # the nearer level wins both ways, so the excess is 0 and there is no lean (without the mirror the ledger would score "nearer first")
    assert ts["counts"] == {"n": 28, "UP": 0, "DOWN": 28, "BOTH": 0, "NEITHER": 0} and ts["mirror"]["UP"] == 28 and ts["likely"] == "NONE"
    assert "closes the map" in ts["invalid"]


def test_lean_needs_an_excess_over_the_mirror():
    # symmetric 2 % map from the Asia open: hour 0 reaches 103 on every day, 98 never -> real excess UP, mirror agrees
    likely, c, m = pb.lean(BARS, DAY, "Asia", 0.02, 0.02)
    assert likely == "UP" and c["UP"] == 28 and m["UP"] == 28
    # lopsided map: the near level wins both ways -> NONE
    assert pb.lean(BARS, DAY, "Europe", 115 / 107 - 1, 1 - 106 / 107)[0] == "NONE"
    assert pb._lean({"n": 19, "UP": 19, "DOWN": 0}, {"n": 19, "UP": 19, "DOWN": 0}) == "NONE"      # below MIN_N
    assert pb._lean({"n": 100, "UP": 10, "DOWN": 40}, {"n": 100, "UP": 40, "DOWN": 10}) == "NONE"  # pure nearness
    assert pb._lean({"n": 100, "UP": 10, "DOWN": 60}, {"n": 100, "UP": 20, "DOWN": 30}) == "DOWN"  # (-50 - 10) / 2 = -30


def test_unstarted_session_uses_the_last_closed_bar_as_reference(tmp_path):
    data, _ = build(tmp_path)
    us = next(s for s in data["sessions"] if s["name"] == "US")
    assert all(s["ref"] == 110.0 for s in us["scenarios"])    # last closed bar is 09:00Z, close 101+9


def test_every_scenario_is_a_ledger_row_with_a_score_time(tmp_path):
    sl = pb.sl
    data, led = build(tmp_path)
    rows = sl.load(led)
    sc = [s for x in data["sessions"] for s in x["scenarios"]]
    assert len(rows) == len(sc) and {r["id"] for r in rows} == {s["id"] for s in sc}
    by_id = {r["id"]: r for r in rows}
    for x in data["sessions"]:
        for s in x["scenarios"]:
            r = by_id[s["id"]]
            end = {"Europe": "2026-11-02T13:00Z", "US": "2026-11-02T21:00Z"}[x["name"]]
            given = {"Europe": "2026-11-02T10:30Z", "US": "2026-11-02T13:00Z"}[x["name"]]   # a session that has not opened is scored from its open
            assert r["end_utc"] == end and r["given_utc"] == given                        # score time = session end
            assert r["text"].startswith("[PB 2026-11-02 %s %s]" % (x["name"], s["n"]))
            assert float(r["up"]) == s["up"] and float(r["down"]) == s["down"] and r["likely"] == s["likely"]
            assert "OURS" in r["text"] and "daily_playbook.py" in r["text"]


def test_rebuild_is_idempotent_and_keeps_ids(tmp_path):
    d1, led = build(tmp_path)
    n1 = len(pb.sl.load(led))
    d2 = pb.build(BARS, DAY, NOW + dt.timedelta(minutes=40), ledger_path=led)
    assert len(pb.sl.load(led)) == n1
    assert [s["id"] for x in d1["sessions"] for s in x["scenarios"]] == [s["id"] for x in d2["sessions"] for s in x["scenarios"]]


def test_old_ledger_rows_stay_untouched(tmp_path):
    old = ("id,given_utc,end_utc,likely,up,down,text,outcome,touched_utc,score,rates\n"
           "S001,2026-11-04T09:00Z,2026-11-05T09:00Z,DOWN,78850.0,77615.0,old,,,,\n")
    data, led = build(tmp_path, ledger=old)
    rows = pb.sl.load(led)
    assert rows[0]["id"] == "S001" and rows[0]["text"] == "old" and rows[1]["id"] == "S002"
    assert min(s["id"] for x in data["sessions"] for s in x["scenarios"]) == "S002"


def test_thin_history_never_leans(tmp_path):
    short = make_bars(first=dt.date(2026, 10, 20))             # 13 days of history < MIN_N
    data, _ = build(tmp_path, bars=short)
    assert pb.MIN_N == 20
    for x in data["sessions"]:
        for s in x["scenarios"]:
            assert s["likely"] == "NONE"
        assert all(s["kind"] != "swing" for s in x["scenarios"])   # no base rate to size a swing from


def test_yesterday_rows_show_hit_miss_and_open(tmp_path):
    hdr = "id,given_utc,end_utc,likely,up,down,text,outcome,touched_utc,score,rates\n"
    led = (hdr
           + "S001,2026-11-01T00:00Z,2026-11-01T08:00Z,UP,110.0,99.0,[PB 2026-11-01 Asia 1] near,UP,2026-11-01T03:00Z,HIT,\n"
           + "S002,2026-11-01T07:00Z,2026-11-01T13:00Z,DOWN,115.0,106.0,[PB 2026-11-01 Europe 1] near,UP,2026-11-01T09:00Z,MISS,\n"
           + "S003,2026-11-01T13:00Z,2026-11-01T21:00Z,NONE,123.0,112.0,[PB 2026-11-01 US 1] near,BOTH,2026-11-01T14:00Z,NA,\n"
           + "S004,2026-11-01T13:00Z,2026-11-01T21:00Z,UP,123.0,112.0,[PB 2026-11-01 US 2] swing,,,,\n"
           + "S005,2026-10-31T13:00Z,2026-10-31T21:00Z,UP,123.0,112.0,[PB 2026-10-31 US 1] older,UP,2026-10-31T14:00Z,HIT,\n")
    data, _ = build(tmp_path, ledger=led)
    y = {r["id"]: r for r in data["yesterday"]["rows"]}
    assert set(y) == {"S001", "S002", "S003", "S004"}                       # the 10-31 row is two days old
    assert [y[i]["grade"] for i in ("S001", "S002", "S003", "S004")] == ["HIT", "MISS", "NA", "UNSCORED"]
    assert y["S001"]["session"] == "Asia" and y["S002"]["session"] == "Europe"
    assert data["yesterday"]["hit"] == 1 and data["yesterday"]["miss"] == 1 and data["yesterday"]["na"] == 1 and data["yesterday"]["open"] == 1
    assert data["yesterday"]["day"] == "2026-11-01"


# ---------- levels, analysts, events on the page data ----------

def test_levels_list_is_sorted_with_names(tmp_path):
    data, _ = build(tmp_path)
    ks = {x["k"] for x in data["levels"]}
    assert {"PDH", "PDL", "PDC", "PWH", "PWL", "DAY_OPEN", "VAL", "POC", "VAH"} <= ks
    ps = [x["price"] for x in data["levels"]]
    assert ps == sorted(ps, reverse=True) and all(x["name"] for x in data["levels"])


def test_analyst_calls_filtered_to_near_price_and_not_expired(tmp_path):
    calls = [{"level": 112.0, "analyst": "A1", "published": "2026-11-01", "bias": "BULLISH", "said": "reclaim 112", "expires_at": "2026-11-05T00:00:00Z"},
             {"level": 500.0, "analyst": "A2", "published": "2026-11-01", "bias": "NEUTRAL", "said": "far", "expires_at": "2026-11-05T00:00:00Z"},
             {"level": 108.0, "analyst": "A3", "published": "2026-10-20", "bias": "BEARISH", "said": "old", "expires_at": "2026-11-01T00:00:00Z"}]
    data, _ = build(tmp_path, analysts=calls)
    assert [c["analyst"] for c in data["analysts"]] == ["A1"] and data["analysts"][0]["level"] == 112.0
    none, _ = build(tmp_path, analysts=None)
    assert none["analysts"] == [] and "NOT_IN_DATA" in none["analysts_note"]


def test_events_land_in_the_session_that_contains_them(tmp_path):
    sched = [{"id": "cpi-2026-11-02", "cls": "CPI", "t0": ms(2026, 11, 2, 13) + 30 * 60_000, "stale": False},
             {"id": "x-asia", "cls": "FOMC", "t0": ms(2026, 11, 2, 7) + 30 * 60_000, "stale": False},
             {"id": "tomorrow", "cls": "PPI", "t0": ms(2026, 11, 3, 13), "stale": False}]
    data, _ = build(tmp_path, schedule=sched)
    by = {s["name"]: s for s in data["sessions"]}
    assert [e["id"] for e in by["US"]["events"]] == ["cpi-2026-11-02"] and by["US"]["events"][0]["hhmm"] == "13:30"
    assert [e["id"] for e in by["Asia"]["events"]] == ["x-asia"] and [e["id"] for e in by["Europe"]["events"]] == ["x-asia"]   # 07:30Z is inside both
    assert data["next_event"]["id"] == "tomorrow"


def test_notes_carry_base_rates_and_percentile(tmp_path):
    data, _ = build(tmp_path)
    asia = data["sessions"][0]
    assert asia["base"]["n"] == 28 and asia["today"]["h"] == 110
    # Asia range today (110/99-1) is the lowest value in history: rank 13/28 (the even days equal it)
    assert asia["today"]["pctile"] == pytest.approx(13 / 28)
    assert any("base rate" in n.lower() for n in asia["notes"])
    assert any("OURS" in n for n in data["notes"])


# ---------- reuse and files ----------

def test_reuses_monday_clocks_instead_of_copying():
    src = (HERE / "daily_playbook.py").read_text(encoding="utf-8")
    assert "def pct(" not in src and "def hourly(" not in src and "def klines(" not in src
    assert pb.mc.__file__.replace("\\", "/").endswith("monday_open_2026-11-09/monday_clocks.py")
    assert pb.mc.pct([4, 1, 3, 2], 0.5) == 2.5 and pb.pct is pb.mc.pct


def test_render_writes_playbook_data_js_that_round_trips(tmp_path):
    data, _ = build(tmp_path)
    s = pb.render(data)
    assert s.startswith("// generated by daily_playbook.py") and "window.PLAYBOOK_DATA = " in s
    back = json.loads(s.split("window.PLAYBOOK_DATA = ", 1)[1].rstrip().rstrip(";"))
    assert back["day"] == "2026-11-02" and len(back["sessions"]) == 3


def test_main_offline_with_cached_bars_writes_the_file_and_ledger(tmp_path):
    cache = tmp_path / "bars.json"
    cache.write_text(json.dumps(BARS), encoding="utf-8", newline="\n")
    out, led = tmp_path / "playbook_data.js", tmp_path / "ledger.csv"
    rc = pb.main(["--day", "2026-11-02", "--now", "2026-11-02T10:30Z", "--offline", "--bars", str(cache), "--out", str(out), "--ledger", str(led), "--no-analysts"])
    assert rc == 0 and out.exists() and len(pb.sl.load(led)) >= 4
    assert "PLAYBOOK_DATA" in out.read_text(encoding="utf-8")


# ---------- JS: now-session highlight, grades, stale ----------

def _js(fn, *args):
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    runner = "const P=require(process.argv[1]);let j='';process.stdin.on('data',d=>j+=d).on('end',()=>{j=JSON.parse(j);console.log(JSON.stringify(P[j.fn].apply(null,j.a)))})"
    out = subprocess.run([node, "-e", runner, str(JS)], input=json.dumps({"fn": fn, "a": list(args)}), capture_output=True,
                         text=True, encoding="utf-8", timeout=30, env=os.environ.copy())
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


@pytest.fixture(scope="module")
def sample(tmp_path_factory):
    d = tmp_path_factory.mktemp("pb")
    data, _ = build(d)
    return json.loads(json.dumps(data))


def test_js_now_sessions():
    assert _js("nowSessions", ms(2026, 11, 2, 3)) == ["Asia"]
    assert _js("nowSessions", ms(2026, 11, 2, 7) + 1800000) == ["Asia", "Europe"]
    assert _js("nowSessions", ms(2026, 11, 2, 15)) == ["US"]
    assert _js("nowSessions", ms(2026, 11, 2, 22)) == []


def test_js_cards_highlight_the_now_session(sample):
    h = _js("html", sample, ms(2026, 11, 2, 10) + 1800000)
    assert h.count('class="pbc now"') == 1 and h.count('class="pbc') == 3
    assert 'data-s="Europe"' in h.split('class="pbc now"', 1)[1][:40]
    assert "Asia" in h and "US" in h and "invalid" in h.lower()
    assert "S0" in h or "S1" in h                                            # ledger ids are on the page
    assert "OURS" in h


def test_js_grades_and_yesterday_block(sample):
    sample = json.loads(json.dumps(sample))
    sample["yesterday"] = {"day": "2026-11-01", "hit": 1, "miss": 1, "na": 0, "open": 0, "rows": [
        {"id": "S001", "session": "Asia", "name": "near", "likely": "UP", "grade": "HIT", "up": 110, "down": 99, "touched": "2026-11-01T03:00Z"},
        {"id": "S002", "session": "Europe", "name": "swing", "likely": "DOWN", "grade": "MISS", "up": 115, "down": 106, "touched": "2026-11-01T09:00Z"}]}
    h = _js("html", sample, ms(2026, 11, 2, 10))
    assert "Yesterday" in h and "HIT" in h and "MISS" in h and "S001" in h and "S002" in h
    assert _js("gradeClass", "HIT") == "up" and _js("gradeClass", "MISS") == "down" and _js("gradeClass", "NA") == "dim"


def test_js_missing_and_stale_data_fail_closed(sample):
    assert "NOT_IN_DATA" in _js("html", None, ms(2026, 11, 2, 10))
    assert "STALE" in _js("html", sample, ms(2026, 11, 4, 10))                 # built for 11-02, now 11-04
    assert "STALE" not in _js("html", sample, ms(2026, 11, 2, 11))
    assert "NOT_IN_DATA" in _js("summary", None, ms(2026, 11, 2, 10))


def test_js_summary_names_the_now_session(sample):
    s = _js("summary", sample, ms(2026, 11, 2, 10) + 1800000)
    assert s.startswith("Europe") and "maps" in s


# ---------- page and artifact ----------

def test_page_has_playbook_view_and_artifact_inlines_it():
    page = (HERE / "live_aid.html").read_text(encoding="utf-8")
    assert 'id="p-playbook"' in page and "playbook: ['p-playbook'" in page and "row('playbook'" in page
    assert page.count('<script src="playbook.js"></script>') == 1 and page.count('<script src="playbook_data.js"></script>') == 1
    art = build_artifact.build()
    assert 'src="playbook' not in art and "root.PLAYBOOK = api" in art and "PLAYBOOK_DATA" in art


def test_phone_artifact_page(sample):
    data_js = pb.render(sample)
    page = build_artifact.build_playbook(data_js)
    assert '<meta name="viewport"' in page and "max-width" in page and "@media" in page
    assert "PLAYBOOK.html(" in page and "root.PLAYBOOK = api" in page and "window.PLAYBOOK_DATA = " in page
    assert "src=" not in page                                                  # everything inlined
    assert "NOT_IN_DATA" in build_artifact.build_playbook(None)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
