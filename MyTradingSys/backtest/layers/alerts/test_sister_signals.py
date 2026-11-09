"""Tests for sister_signals.py (card sister-signals-wired-1109). Fixture closes are OURS, shaped on SISTER_NOTE_2026-11-09
(11-08 dip to 73,510, week close 74,850). No network: providers are injected."""
import json
import time
from datetime import datetime, timezone

from MyTradingSys.backtest.layers.alerts import sister_signals as ss

UTC = timezone.utc
DAY = 86_400_000


def ms(y, m, d, h=0, mi=0):
    return int(datetime(y, m, d, h, mi, tzinfo=UTC).timestamp() * 1000)


def daily(closes, lows=None, start=ms(2026, 11, 1)):
    lows = lows or [c - 500 for c in closes]
    return [{"t": start + i * DAY, "c": float(c), "l": float(lo)} for i, (c, lo) in enumerate(zip(closes, lows))]


WEEKLY_OK = [{"t": ms(2026, 10, 26), "c": 76_100.0, "l": 71_000.0}, {"t": ms(2026, 11, 2), "c": 74_850.0, "l": 72_900.0}]
CFG = ss.load_config()


def test_config_has_source_and_ours_label():
    raw = json.loads(ss.CONFIG_PATH.read_text(encoding="utf-8"))
    assert "SISTER_NOTE_2026-11-07" in raw["source"] and "SISTER_NOTE_2026-11-09" in raw["source"]
    assert raw["label"] == "OURS"
    assert CFG["phase2_lo"] == 72_000 and CFG["phase2_hi"] == 75_000 and CFG["confirm_weekly"] == 80_500
    assert CFG["stop_weekly"] == 60_000 and CFG["stop_low"] == 57_800 and CFG["topup_lo"] == 65_000


def test_nov_7_to_9_closes_give_phase2_on():
    d = daily([75_900, 75_400, 74_400, 73_950], start=ms(2026, 11, 5))   # 11-07 74,400 and 11-08 73,950 in the zone
    assert ss.compute_state(d, WEEKLY_OK, 73_900.0, CFG) == "PHASE2_ON"


def test_one_close_in_zone_is_not_phase2():
    d = daily([75_900, 75_400, 75_300, 74_100])
    assert ss.compute_state(d, WEEKLY_OK, 74_100.0, CFG) == "WAIT"


def test_daily_close_under_72000_gives_top_up():
    d = daily([74_400, 73_950, 71_900])
    assert ss.compute_state(d, WEEKLY_OK, 71_950.0, CFG) == "TOP_UP"


def test_price_in_65_67k_gives_top_up():
    d = daily([74_400, 73_950, 72_300])
    assert ss.compute_state(d, WEEKLY_OK, 66_200.0, CFG) == "TOP_UP"


def test_weekly_close_under_60000_is_stop_and_beats_top_up():
    wk = WEEKLY_OK + [{"t": ms(2026, 11, 9), "c": 59_800.0, "l": 59_000.0}]
    assert ss.compute_state(daily([66_000, 65_500, 61_000]), wk, 60_100.0, CFG) == "STOP"


def test_new_low_under_57800_is_stop():
    d = daily([60_500, 59_900, 60_200], lows=[59_000, 57_700, 59_500])
    assert ss.compute_state(d, WEEKLY_OK, 60_200.0, CFG) == "STOP"


def test_weekly_close_over_80500_is_confirmed():
    wk = WEEKLY_OK + [{"t": ms(2026, 11, 9), "c": 80_900.0, "l": 76_000.0}]
    assert ss.compute_state(daily([80_000, 80_700, 81_000]), wk, 81_000.0, CFG) == "CONFIRMED"


# ---------- poll: flips, restart safety, fail closed, notes, Monday brief line ----------

def provider(d, w, price, prices=None):
    def fetch(source=None):
        return {"daily": d, "weekly": w, "price": price, "source": source or "perp",
                "prices": prices or {"BTC": price, "ETH": 2_090.0, "SOL": 85.7, "LINK": 10.3, "HBAR": 0.0658}}
    return fetch


def run(tmp_path, fetch, now_ms):
    return ss.poll(fetch, tmp_path / "sister_state.json", tmp_path / "alerts", tmp_path / "toasts.jsonl",
                   tmp_path / "notes", now_ms, cfg=CFG)


def test_first_poll_records_state_without_alert(tmp_path):
    out = run(tmp_path, provider(daily([74_400, 73_950]), WEEKLY_OK, 73_900.0), ms(2026, 11, 10, 9))
    assert out == []
    assert json.loads((tmp_path / "sister_state.json").read_text())["state"] == "PHASE2_ON"


def test_flip_fires_once_and_restart_does_not_refire(tmp_path):
    now = ms(2026, 11, 10, 9)
    run(tmp_path, provider(daily([74_400, 73_950]), WEEKLY_OK, 73_900.0), now)
    flip = provider(daily([74_400, 73_950, 71_900]), WEEKLY_OK, 71_950.0)
    assert run(tmp_path, flip, now + 15 * 60_000) == []         # first sighting: waits for confirmation
    out = run(tmp_path, flip, now + 30 * 60_000)
    assert [a["event"] for a in out] == ["SISTER"]
    assert "PHASE2_ON -> TOP_UP" in out[0]["text"]
    assert "SISTER" in (tmp_path / "toasts.jsonl").read_text()
    assert "TOP_UP" in (tmp_path / "alerts" / ss.LOG_NAME).read_text()
    assert run(tmp_path, flip, now + 45 * 60_000) == []          # same state; a new process reads the same state file


def test_polls_inside_the_fetch_interval_do_not_fetch(tmp_path):
    calls = []

    def f():
        calls.append(1)
        return provider(daily([74_400, 73_950]), WEEKLY_OK, 73_900.0)()
    now = ms(2026, 11, 10, 9)
    run(tmp_path, f, now)
    run(tmp_path, f, now + 60_000)
    assert len(calls) == 1


def test_fetch_error_fails_closed_with_one_degraded_line(tmp_path):
    now = ms(2026, 11, 10, 9)
    run(tmp_path, provider(daily([74_400, 73_950]), WEEKLY_OK, 73_900.0), now)

    def boom():
        raise OSError("dns down")
    assert run(tmp_path, boom, now + 15 * 60_000) == []
    assert run(tmp_path, boom, now + 30 * 60_000) == []
    log = (tmp_path / "alerts" / ss.LOG_NAME).read_text().splitlines()
    assert sum("DEGRADED" in x for x in log) == 1
    assert json.loads((tmp_path / "sister_state.json").read_text())["state"] == "PHASE2_ON"   # unchanged, nothing fired
    assert not (tmp_path / "toasts.jsonl").exists()


def test_flip_writes_both_draft_notes_with_live_prices(tmp_path):
    now = ms(2026, 11, 11, 9)   # a Wednesday: notes come from the flip, not the Monday slot
    run(tmp_path, provider(daily([74_400, 73_950]), WEEKLY_OK, 73_900.0), now)
    flip = provider(daily([74_400, 73_950, 71_900]), WEEKLY_OK, 71_950.0)
    run(tmp_path, flip, now + 15 * 60_000)
    run(tmp_path, flip, now + 30 * 60_000)
    notes = sorted(p.name for p in (tmp_path / "notes").iterdir())
    assert any(n.startswith("sister_") for n in notes) and any(n.startswith("aunt_") for n in notes)
    sister = next((tmp_path / "notes").glob("sister_*")).read_text(encoding="utf-8")
    aunt = next((tmp_path / "notes").glob("aunt_*")).read_text(encoding="utf-8")
    assert "TOP_UP" in sister and "Half A" in sister and "71,200" in sister    # BTC A = 1 % below 71,950, to 100
    assert "60%" in aunt and "25%" in aunt and "15%" in aunt and "Part 2 now" in aunt
    assert "हिस्सा" in aunt                                                   # Hindi part present
    assert "70,500" in aunt                                                   # BTC limit 2 % below 71,950, to 100


def test_monday_0700_writes_notes_once(tmp_path):
    mon = ms(2026, 11, 16, 7, 5)
    f = provider(daily([74_400, 73_950]), WEEKLY_OK, 73_900.0)
    run(tmp_path, f, mon - 3_600_000)               # Monday 06:05, before the slot: first poll, no notes
    assert not (tmp_path / "notes").exists()
    run(tmp_path, f, mon)
    n1 = len(list((tmp_path / "notes").iterdir()))
    run(tmp_path, f, mon + 15 * 60_000)
    assert n1 == 2 and len(list((tmp_path / "notes").iterdir())) == 2


def test_notes_dir_failure_does_not_raise(tmp_path):
    bad = tmp_path / "file_not_dir"
    bad.write_text("x")
    now = ms(2026, 11, 11, 9)
    ss.poll(provider(daily([74_400, 73_950]), WEEKLY_OK, 73_900.0), tmp_path / "s.json", tmp_path / "a", None, bad, now, cfg=CFG)
    f = provider(daily([74_400, 73_950, 71_900]), WEEKLY_OK, 71_950.0)
    ss.poll(f, tmp_path / "s.json", tmp_path / "a", None, bad, now + 15 * 60_000, cfg=CFG)
    out = ss.poll(f, tmp_path / "s.json", tmp_path / "a", None, bad, now + 30 * 60_000, cfg=CFG)
    assert [a["event"] for a in out] == ["SISTER"]


def test_sister_line_in_monday_eu_brief_only(tmp_path):
    from MyTradingSys.backtest.layers.alerts import live_level_touch as lt
    st = tmp_path / "sister_state.json"
    st.write_text(json.dumps({"state": "PHASE2_ON"}))
    assert ss.brief_line(st, ms(2026, 11, 16, 7, 1)) == "SISTER: PHASE2_ON"
    assert ss.brief_line(st, ms(2026, 11, 17, 7, 1)) is None          # Tuesday
    assert ss.brief_line(st, ms(2026, 11, 16, 13, 31)) is None        # Monday US slot
    lv = [{"key": "a", "level": 73_500.0, "who": "X"}]
    txt = lt.brief_text("EU", 73_900.0, lv, [], None, [], ms(2026, 11, 16, 7, 1), sister="SISTER: PHASE2_ON")
    assert txt.endswith("| SISTER: PHASE2_ON")
    assert "SISTER" not in lt.brief_text("EU", 73_900.0, lv, [], None, [], ms(2026, 11, 16, 7, 1))


# ---------- review defects (card sister-signals-fix-review-defects-1109) ----------

A = provider(daily([74_400, 73_950]), WEEKLY_OK, 73_900.0)             # PHASE2_ON
B = provider(daily([74_400, 73_950, 71_900]), WEEKLY_OK, 71_950.0)     # TOP_UP
T15 = 15 * 60_000


def test_stale_wick_older_than_two_days_is_not_stop():
    d = daily([66_000] * 12, lows=[57_000] + [65_000] * 11)             # a 12-day-old wick under 57,800
    assert ss.compute_state(d, WEEKLY_OK, 70_000.0, CFG) != "STOP"
    d2 = daily([66_000] * 12, lows=[65_000] * 10 + [57_000, 65_000])    # inside the last 2 closed days
    assert ss.compute_state(d2, WEEKLY_OK, 70_000.0, CFG) == "STOP"


def test_oscillation_never_emits_and_two_in_a_row_emit_once(tmp_path):
    now = ms(2026, 11, 11, 9)
    run(tmp_path, A, now)
    outs = [run(tmp_path, f, now + (i + 1) * T15) for i, f in enumerate([B, A, B, A])]
    assert outs == [[], [], [], []]
    assert not (tmp_path / "toasts.jsonl").exists()
    assert run(tmp_path, B, now + 5 * T15) == []
    assert [a["to"] for a in run(tmp_path, B, now + 6 * T15)] == ["TOP_UP"]


def test_confirm_count_survives_a_restart(tmp_path):
    now = ms(2026, 11, 11, 9)
    run(tmp_path, A, now)
    run(tmp_path, B, now + T15)
    st = json.loads((tmp_path / "sister_state.json").read_text())
    assert st["state"] == "PHASE2_ON" and st["pending"] == "TOP_UP" and st["pending_n"] == 1
    assert len(run(tmp_path, B, now + 2 * T15)) == 1                   # a fresh poll() call reads it from disk


def test_write_failure_saves_state_first_and_never_refires(tmp_path, monkeypatch):
    now = ms(2026, 11, 11, 9)
    run(tmp_path, A, now)
    run(tmp_path, B, now + T15)

    def boom(*a, **k):
        raise OSError("disk full")
    monkeypatch.setattr(ss, "append_alerts_jsonl", boom)
    out = run(tmp_path, B, now + 2 * T15)                              # must not raise
    assert out and json.loads((tmp_path / "sister_state.json").read_text())["state"] == "TOP_UP"
    monkeypatch.undo()
    assert run(tmp_path, B, now + 3 * T15) == []                       # no re-fire


def test_corrupt_state_logs_one_unknown_and_rebaselines(tmp_path):
    now = ms(2026, 11, 11, 9)
    (tmp_path / "sister_state.json").write_text("{not json", encoding="utf-8")
    assert run(tmp_path, A, now) == []                                 # no flip: re-baseline
    log = (tmp_path / "alerts" / ss.LOG_NAME).read_text().splitlines()
    assert sum("UNKNOWN" in x for x in log) == 1
    assert "UNKNOWN" in (tmp_path / "toasts.jsonl").read_text()
    assert json.loads((tmp_path / "sister_state.json").read_text())["state"] == "PHASE2_ON"
    run(tmp_path, A, now + T15)
    assert sum("UNKNOWN" in x for x in (tmp_path / "alerts" / ss.LOG_NAME).read_text().splitlines()) == 1


def test_missing_state_file_is_a_quiet_first_poll(tmp_path):            # reset: deleted file is not corruption
    run(tmp_path, A, ms(2026, 11, 11, 9))
    assert not (tmp_path / "alerts" / ss.LOG_NAME).exists()


def test_source_is_pinned_and_a_switch_fails_closed(tmp_path):
    now = ms(2026, 11, 11, 9)
    run(tmp_path, A, now)
    assert json.loads((tmp_path / "sister_state.json").read_text())["source"] == "perp"
    seen = []

    def spot_only(source=None):
        seen.append(source)
        return {**A(), "source": "spot"}
    assert run(tmp_path, spot_only, now + T15) == []
    assert seen == ["perp"]                                            # the pin was asked for
    st = json.loads((tmp_path / "sister_state.json").read_text())
    assert st["state"] == "PHASE2_ON" and st["degraded"] is True and st["source"] == "perp"


def test_slow_fetch_does_not_block_the_poll(tmp_path):
    def slow(source=None):
        time.sleep(1.0)
        return B()
    bg = ss.BackgroundFetch(slow)
    now = ms(2026, 11, 11, 9)
    t0 = time.time()
    assert run(tmp_path, bg, now) == []
    assert time.time() - t0 < 0.5
    time.sleep(1.3)
    assert run(tmp_path, bg, now + 60_000) == []                       # harvested the cached result: first poll baselines
    assert json.loads((tmp_path / "sister_state.json").read_text())["state"] == "TOP_UP"


def test_background_fetch_error_is_degraded_not_raised(tmp_path):
    def boom(source=None):
        raise OSError("dns down")
    bg = ss.BackgroundFetch(boom)
    now = ms(2026, 11, 11, 9)
    run(tmp_path, bg, now)
    time.sleep(0.3)
    assert run(tmp_path, bg, now + 60_000) == []
    assert "DEGRADED" in (tmp_path / "alerts" / ss.LOG_NAME).read_text()
