"""Synthetic-bar tests for T10 (core + stats). No data cache. Run: python -m pytest test_t10_core.py  (or unittest)."""
import sys
import pathlib
import numpy as np

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "backtest"))
import fees  # noqa: E402
import t10_core as core  # noqa: E402
import t10_stats as st  # noqa: E402

DAY = 86400000
START = core._eday(2021, 1, 4)


def base_rows():
    """285 bars of a steady decline, a 5-bar rally (+~24%), then a rejection bar T = index 290 that fires every flag."""
    c = [200 * 0.992 ** i for i in range(285)]
    x = c[-1]
    for r in (0.04, 0.05, 0.05, 0.04, 0.04):
        x *= 1 + r
        c.append(x)
    rows, prev = [], c[0]
    for i, cl in enumerate(c):
        o = prev
        rows.append((o, max(o, cl) * 1.01, min(o, cl) * 0.99, cl))
        prev = cl
    last, pl = c[-1], rows[-1][2]
    o = last * 1.03
    cl = pl * 0.99
    rows.append((o, o * 1.01, cl * 0.99, cl))
    return rows


T = 290


def mkrun(extra=(), pull_gap_days=400, upto=None, rows=None):
    rows = list(rows if rows is not None else base_rows())
    if upto is not None:
        rows = rows[:upto]
    rows = rows + list(extra)
    arr = np.array([((START + i) * DAY,) + tuple(r) for i, r in enumerate(rows)], float)
    return core.make_runs("SYN", arr, int(arr[-1, 0] + pull_gap_days * DAY))[0]


def env(run):
    return {int(d): True for d in run.day}, {int(d): 40 for d in run.day}


def flat(n, px, r=0.001):
    return [(px, px * (1 + r), px * (1 - r), px)] * n


def trade_info(run):
    why, info = core.entry_screen(run, T)
    assert why is None, why
    return info          # e, xd, ended, entry, stop_px, target_px


# ---------------------------------------------------------------- constants and indicators
def test_fee_is_12bp_from_fees_py():
    assert core.FEE_RT == 2 * fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13
    assert abs(core.FEE_RT - 12 / 10000.0) < 1e-12


def test_wilder_atr_hand_value():
    n = 20
    h, l, c = np.full(n, 101.0), np.full(n, 99.0), np.full(n, 100.0)
    h[14], l[14] = 108.0, 92.0
    atr = core.wilder_atr(h, l, c)
    assert abs(atr[13] - 2.0) < 1e-12
    assert abs(atr[14] - (2 * 13 + 16) / 14.0) < 1e-12      # 3.0, by hand


def test_prior_min_excludes_current_bar():
    x = np.array([5, 4, 3, 2, 1, 9, 9, 9, 9, 9, 9, 0.5], float)
    pm = core.prior_min(x, 10)
    assert pm[10] == 1 and pm[11] == 1          # bar 11 (0.5) is not in its own window


def test_signal_fires_on_the_planted_bar_with_every_flag():
    run = mkrun()
    gate, alive = env(run)
    raw, ok = core.signal_mask(run, gate, alive)
    assert list(np.where(ok)[0]) == [T]
    assert run.down[T] and run.rally12[T] and run.rej[T]


def test_signal_needs_gate_alive_and_history():
    run = mkrun()
    gate, alive = env(run)
    off = {d: False for d in gate}
    assert not core.signal_mask(run, off, alive)[1].any()
    few = {d: 29 for d in alive}
    raw, ok = core.signal_mask(run, gate, few)
    assert raw.any() and not ok.any()
    short = mkrun(rows=base_rows()[-100:])           # fewer than 260 bars of history
    g2, a2 = env(short)
    assert not core.signal_mask(short, g2, a2)[0].any()


# ---------------------------------------------------------------- look-ahead
def test_signal_uses_only_bars_through_t():
    full = mkrun(extra=flat(12, 20.0))
    gate, alive = env(full)
    raw, ok = core.signal_mask(full, gate, alive)
    rs = np.random.RandomState(3)
    alt_rows = base_rows()[:T + 1] + [tuple(v * (1 + rs.normal(0, .3)) for v in (20, 21, 19, 20)) for _ in range(40)]
    alt = mkrun(rows=alt_rows)
    g2, a2 = env(alt)
    raw2, ok2 = core.signal_mask(alt, g2, a2)
    assert list(ok[:T + 1]) == list(ok2[:T + 1]) and ok[T]
    trunc = mkrun(upto=T + 1)                          # nothing after t at all
    g3, a3 = env(trunc)
    assert core.signal_mask(trunc, g3, a3)[1][T]


def test_entry_is_next_bar_open_and_target_frozen_at_signal():
    e_open = 23.5
    run = mkrun(extra=[(e_open, 23.6, 23.4, 23.5)] + flat(12, 23.5))
    row, why = core.make_trade(run, T)
    assert row["entry_px"] == e_open and row["entry_day"] == row["signal_day"] + 1
    target = float(run.low10[T])
    assert row["target_px"] == target
    # rewriting the bars after the signal never moves the frozen target
    run2 = mkrun(extra=[(e_open, 23.6, 23.4, 23.5)] + flat(12, 30.0))
    row2, _ = core.make_trade(run2, T)
    assert row2["target_px"] == target


# ---------------------------------------------------------------- simulator
def test_stop_wins_ties_when_one_bar_touches_stop_and_target():
    run0 = mkrun(extra=[(23.5, 23.6, 23.4, 23.5)])
    e, xd, ended, entry, stop_px, target_px = trade_info(run0)
    bar = (23.5, stop_px * 1.01, target_px * 0.99, 23.0)          # high >= stop AND low <= target
    run = mkrun(extra=[bar] + flat(12, 23.0))
    row, _ = core.make_trade(run, T)
    assert row["exit_reason"] == "STOP" and row["exit_px"] == stop_px and row["hold_days"] == 1
    assert row["gross"] < 0


def test_target_fill_price_and_R_arithmetic_by_hand():
    run0 = mkrun(extra=[(23.5, 23.6, 23.4, 23.5)])
    e, xd, ended, entry, stop_px, target_px = trade_info(run0)
    bar2 = (23.0, 23.1, target_px * 0.98, target_px * 1.0)           # bar after entry touches the target, not the stop
    run = mkrun(extra=[(23.5, 23.6, 23.4, 23.5), bar2] + flat(12, 20.0))
    row, _ = core.make_trade(run, T)
    stop_pct = stop_px / entry - 1
    gross = (entry - target_px) / entry
    assert row["exit_reason"] == "TARGET" and row["exit_px"] == target_px and row["hold_days"] == 2
    assert abs(row["gross"] - gross) < 1e-12
    assert abs(row["net"] - (gross - 0.0012)) < 1e-12                   # 12 bp, hand number
    assert abs(row["net_R"] - (gross - 0.0012) / stop_pct) < 1e-12
    assert abs(row["fee_R"] - 0.0012 / stop_pct) < 1e-12
    assert abs(row["gross_R"] - row["net_R"] - row["fee_R"]) < 1e-12
    assert stop_pct >= core.STOP_FLOOR - 1e-12


def test_stop_floor_five_percent_and_formula():
    run0 = mkrun(extra=[(23.5, 23.6, 23.4, 23.5)])
    e, xd, ended, entry, stop_px, target_px = trade_info(run0)
    formula = float(run0.hh5[T] + 0.5 * run0.atr[T])
    assert stop_px == max(formula, entry * 1.05)
    assert stop_px >= entry * 1.05 - 1e-9


def test_gap_open_above_stop_fills_at_open():
    run0 = mkrun(extra=[(23.5, 23.6, 23.4, 23.5)])
    e, xd, ended, entry, stop_px, target_px = trade_info(run0)
    gap = (stop_px * 1.03, stop_px * 1.04, stop_px * 1.02, stop_px * 1.03)
    run = mkrun(extra=[(23.5, 23.6, 23.4, 23.5), gap] + flat(12, 23.0))
    row, _ = core.make_trade(run, T)
    assert row["exit_reason"] == "STOP-GAP" and row["exit_px"] == stop_px * 1.03 and row["net_R"] < -1.0


def test_time_exit_after_ten_bars_at_close():
    run = mkrun(extra=[(23.5, 23.6, 23.4, 23.5)] + [(23.5, 23.6, 23.4, 23.5)] * 11)
    row, _ = core.make_trade(run, T)
    assert row["exit_reason"] == "TIME" and row["hold_days"] == 10 and row["exit_px"] == 23.5
    assert row["exit_day"] == row["entry_day"] + 9


def test_ended_coin_exits_at_last_close_and_live_coin_skips_incomplete_window():
    tail = [(23.5, 23.6, 23.4, 23.5)] * 4
    ended = mkrun(extra=tail, pull_gap_days=400)
    row, why = core.make_trade(ended, T)
    assert row["exit_reason"] == "ENDED" and row["exit_day"] == int(ended.day[-1])
    live = mkrun(extra=tail, pull_gap_days=1)
    row2, why2 = core.make_trade(live, T)
    assert row2 is None and why2 == "INCOMPLETE-WINDOW"


def test_target_not_below_entry_is_skipped():
    run = mkrun(extra=[(15.0, 15.1, 14.9, 15.0)] + flat(12, 15.0))     # opens under the frozen target
    row, why = core.make_trade(run, T)
    assert row is None and why == "TARGET-NOT-BELOW-ENTRY"


def test_luna_ftt_hole_blocks_spanning_trade():
    run = mkrun(extra=[(23.5, 23.6, 23.4, 23.5)] * 12)
    run.name = "LUNA"
    # shift the run's days so the window sits inside the LUNA hole
    run.day = run.day - run.day[T] + core._eday(2022, 5, 20)
    row, why = core.make_trade(run, T)
    assert row is None and why == "HOLE"
    run.name = "XYZ"
    row, why = core.make_trade(run, T)
    assert row is not None


def test_cooldown_blocks_second_signal_inside_ten_bars(monkeypatch):
    run = mkrun()
    m = np.zeros(run.n, bool)
    m[[100, 105, 110, 120]] = True
    monkeypatch.setattr(core, "signal_mask", lambda *a, **k: (m, m))
    acc, c = core.scan_signals(run, {}, {})
    assert acc == [100, 110, 120] and c["cooldown_blocked"] == 1      # 105 blocked, 110 is exactly 10 later


# ---------------------------------------------------------------- funding, split, weeks, helpers
def test_funding_short_receives_positive_rate_and_nan_when_not_covered():
    ts = [(START + 300) * DAY + k * 8 * 3600000 for k in range(-2, 12)]
    f = core.Funding(ts, [0.001] * 14)
    entry, end = (START + 300) * DAY, (START + 301) * DAY
    assert abs(f.income_short(entry, end) - 0.003) < 1e-12            # 3 prints after entry, short earns +0.1% each
    fneg = core.Funding(ts, [-0.002] * 14)
    assert abs(fneg.income_short(entry, end) + 0.006) < 1e-12         # negative funding: the short pays
    assert f.income_short(entry - 30 * DAY, end) != f.income_short(entry - 30 * DAY, end)     # NaN: not covered
    assert f.income_short(entry, end + 90 * DAY) != f.income_short(entry, end + 90 * DAY)


def test_iso_entry_week_sunday_belongs_to_the_week_of_the_prior_monday():
    mon, sun, nxt = core._eday(2023, 10, 16), core._eday(2023, 10, 22), core._eday(2023, 10, 23)
    assert core.iso_week_of_day(mon) == core.iso_week_of_day(sun) != core.iso_week_of_day(nxt)
    assert core.split_of_day(core._eday(2023, 12, 31)) == "DEV" and core.split_of_day(core._eday(2024, 1, 1)) == "VAL"


def test_smooth_cycle_needs_ten_consecutive_days():
    raw = [(i, "BULL") for i in range(5)] + [(5 + i, "BEAR") for i in range(9)] + [(14, "BULL")]
    sm = core.smooth_cycle(raw)
    assert all(sm[i] == "BULL" for i in range(15))                    # 9 BEAR days then a break: never adopted
    raw2 = [(i, "BULL") for i in range(5)] + [(5 + i, "BEAR") for i in range(12)]
    sm2 = core.smooth_cycle(raw2)
    assert sm2[13] == "BULL" and sm2[14] == "BEAR"                    # 10th consecutive BEAR day is index 14


def test_episodes_chain_within_14_days():
    ids = core.episodes([100, 110, 124, 140, 300, 301])
    assert ids[0] == ids[1] == ids[2] and ids[3] != ids[2] and ids[4] != ids[3] and ids[4] == ids[5]


# ---------------------------------------------------------------- statistics
def _rows(vals, weeks, coins=None, split="VAL", year=2024, cycle="BEAR"):
    out = []
    for i, (v, w) in enumerate(zip(vals, weeks)):
        out.append(dict(coin=(coins[i] if coins else "C%d" % (i % 12)), run=0, t=i, split=split, iso_week="%d-W%02d" % (year, w),
                        entry_day=core._eday(year, 1, 1) + 7 * w + (i % 3), hold_days=5, exit_reason="TIME",
                        gross_R=v + 0.02, fee_R=0.02, net_R=v, fund_R=0.0, total_R=v, net=v * 0.07, gross=v * 0.07 + 0.0012,
                        fund_rule="REAL", cycle=cycle, episode=w // 3, stop_pct=0.07, tgt_pct=0.08))
    return out


def test_planted_edge_is_detected_and_no_edge_reads_about_zero():
    rs = np.random.RandomState(1114)
    weeks = [1 + (i % 40) for i in range(120)]
    edge = _rows(rs.normal(0.6, 1.0, 120), weeks)
    b = st.week_block_bootstrap(edge)
    assert b["ci_low"] > 0 and b["mean"] > 0.3
    null = _rows(rs.normal(0.0, 1.0, 120), weeks)
    b0 = st.week_block_bootstrap(null)
    assert abs(b0["mean"]) < 0.3 and b0["ci_low"] < 0 < b0["ci_high"]


def test_bootstrap_is_seeded_and_block_two_uses_adjacent_weeks():
    r = _rows([1, -1, 1, -1, 1, -1, 1, -1], [1, 2, 3, 4, 5, 6, 7, 8])
    a, b = st.week_block_bootstrap(r), st.week_block_bootstrap(r)
    assert a == b
    s = np.array([1.0, -1, 1, -1]); n = np.ones(4)
    m = st._ratio_boot(s, n, 2, 500, 1)
    assert set(np.round(np.unique(m), 6)) <= {-1.0, 0.0, 1.0}         # adjacent pair sums are -1+1 pairs or equal pairs


def test_placebo_planted_beats_draws_and_no_edge_does_not():
    rs = np.random.RandomState(7)
    cands = [list(rs.normal(0, 0.3, 30)) for _ in range(40)]
    p = st.placebo_draws([1.0] * 40, cands)
    assert p["real_mean"] > p["p975"] and p["excess"] > 0.8
    same = st.placebo_draws([float(rs.normal(0, 0.3)) for _ in range(40)], cands)
    assert abs(same["excess"]) < 0.25 and same["rank_pct"] < 99.5


def test_ex_best_and_top_coin_and_loyo():
    rows = _rows([5.0, -0.1, -0.1, -0.1, -0.1, -0.1], [1, 2, 3, 4, 5, 6], coins=["A", "B", "C", "D", "E", "F"])
    assert st.ex_best_weeks(rows, 1)["mean"] < 0 < st.describe(rows)["mean"]
    tc = st.top_coin_removal(rows, 3)
    assert tc[0]["removed"] == ["A"] and tc[0]["mean"] < 0
    lo = st.leave_one_year_out(rows)
    assert "2024" in lo


def _planted(edge):
    rs = np.random.RandomState(5)
    wk_val = [1 + (i % 30) for i in range(90)]
    yrs = [2024 + (i % 3) for i in range(90)]
    val = []
    for i in range(90):
        r = _rows([rs.normal(0.5 if edge else 0.0, 0.5)], [wk_val[i]], year=yrs[i], coins=["V%d" % (i % 15)])[0]
        r["iso_week"] = "%d-W%02d" % (yrs[i], wk_val[i]); r["entry_day"] = core._eday(yrs[i], 1, 1) + 7 * wk_val[i]; r["t"] = i
        val.append(r)
    dev = _rows(rs.normal(0.5 if edge else 0.0, 0.5, 40), [1 + (i % 30) for i in range(40)], split="DEV", year=2022)
    trades = val + dev
    cand = {id(r): list(rs.normal(0, 0.3, 20)) for r in trades}
    return trades, cand


def test_run_stats_planted_edge_passes_and_no_edge_does_not():
    trades, cand = _planted(True)
    S = st.run_stats(trades, cand, cand, {"DEV": 0.0001, "VAL": 0.0001}, nboot=500, ndraw=300)
    assert S["verdict"] == "PASS", (S["verdict"], S["verdict_detail"], S["bars"])
    trades, cand = _planted(False)
    S0 = st.run_stats(trades, cand, cand, {"DEV": 0.0001, "VAL": 0.0001}, nboot=500, ndraw=300)
    assert S0["verdict"] != "PASS"


def test_underpowered_is_not_fail():
    rows = _rows([0.5] * 10, list(range(1, 11)))
    S = st.run_stats(rows, {}, {}, {"DEV": 0.0, "VAL": 0.0}, nboot=200, ndraw=100)
    assert S["verdict"] == "UNDERPOWERED"


def test_sign_flip_and_carry_only_labels():
    trades, cand = _planted(True)
    for r in trades:
        if r["split"] == "VAL":
            r["cycle"] = "BULL" if r["t"] % 2 else "BEAR"
            if r["cycle"] == "BEAR":
                r["net_R"] = r["total_R"] = -0.2
    S = st.run_stats(trades, cand, cand, {"DEV": 0.0, "VAL": 0.0}, nboot=300, ndraw=200)
    assert S["sign_flip"] or S["verdict"] != "PASS"
    trades, cand = _planted(True)
    for r in trades:
        if r["split"] == "VAL":
            r["net_R"], r["fund_R"], r["total_R"] = -0.1, 0.4, 0.3
    S2 = st.run_stats(trades, cand, cand, {"DEV": 0.0, "VAL": 0.0}, nboot=300, ndraw=200)
    assert S2["carry_only"] and S2["verdict"] == "CARRY-ONLY"
