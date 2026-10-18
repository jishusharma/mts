"""Tests for screen.py (pure numpy fixtures, no market data). Run: python test_screen.py"""
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import screen as S  # noqa: E402  (fails before screen.py exists)

DAY = 1440


def make_fixture(ndays, side=-1, fade_days=None, f_days=None, early_jump_day=None, seed=7):
    """Every day: flat 100 until bar 200, jump J (grows with the day) at bar 200, flat, then a fade at bar 262.
    side=-1: up-jump (SHORT fade); side=+1: down-jump (LONG fade). F days: sellers (SHORT) / buyers (LONG) aggressive."""
    rng = np.random.default_rng(seed)
    n = ndays * DAY
    o = np.full(n, 100.0)
    h = o.copy()
    l = o.copy()
    c = o.copy()
    v = np.full(n, 10.0)
    tbv = np.full(n, 5.0)
    fades = np.zeros(ndays)
    fflag = np.zeros(ndays, bool)
    for k in range(ndays):
        b = k * DAY
        J = 0.01 * (1 + 0.01 * k)
        f_on = (k % 4 != 3) if f_days is None else bool(f_days[k])
        fade = (0.006 + 0.001 * rng.standard_normal()) if f_on else 0.0
        if fade_days is not None and not fade_days:
            fade = 0.0
        jb = 200 if early_jump_day != k else 30
        p1 = 100 * (1 - side * J)           # side=-1 -> 100*(1+J)
        p2 = p1 * (1 + side * fade)         # fade back toward 100
        # bars jb: the jump; jb+1..jb+61 flat at p1; then p2
        o[b + jb], c[b + jb] = 100.0, p1
        h[b + jb] = max(100.0, p1)
        l[b + jb] = min(100.0, p1)
        sl = slice(b + jb + 1, b + jb + 62)
        o[sl] = h[sl] = l[sl] = c[sl] = p1
        sl = slice(b + jb + 62, b + DAY)
        o[sl] = h[sl] = l[sl] = c[sl] = p2
        fades[k] = fade
        fflag[k] = f_on
        # delta sign: SHORT F => negative delta (tbv < v/2); LONG F => positive
        agg = (8 if side == 1 else 2) if f_on else (2 if side == 1 else 8)
        tbv[b:b + DAY] = agg
    return dict(O=o, H=h, L=l, C=c, V=v, TBV=tbv, QV=v * c), fades, fflag


def test_delta():
    d = S.delta(np.array([10.0, 10.0]), np.array([8.0, 2.0]))
    assert np.allclose(d, [6.0, -6.0]), d       # 2*tbv - v ; buyer-taker volume is the buy side


def test_cluster_se():
    g = np.array([1.0, 3.0, 5.0])
    day = np.array([0, 0, 1])
    m, se = S.cluster_mean_se(g, day)
    assert abs(m - 3.0) < 1e-12
    assert abs(se - np.sqrt(8 / 9)) < 1e-12, se   # S_day = -2, +2 ; Var = 8/9


def test_cooldown():
    cands = [(100, -1), (130, -1), (161, -1), (170, 1), (200, -1)]
    out = S.apply_cooldown(cands, 60)
    # 130 is blocked by 100; 161 is 61 after 100 -> kept; 200 blocked by 161; LONG 170 independent
    assert out == [(100, -1), (161, -1), (170, 1)], out


def test_loader_refuses_validation():
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "BTCUSDT-1m-2024-07.csv"
        cut = S.CUTOFF_MS
        p.write_text("open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,x,y\n"
                     f"{cut},1,1,1,1,1,0,1,1,1,1,0\n", encoding="utf-8")
        try:
            S.load_dev([p])
        except ValueError:
            return
        raise AssertionError("loader accepted a bar >= 2024-07-01")


def run(ndays, **kw):
    A, fades, fflag = make_fixture(ndays, **kw)
    led = S.build_ledger(A, ndays)
    cells = S.compute_cells(A, led, ndays)
    res = S.evaluate(cells, A, ndays)
    return A, fades, fflag, led, cells, res


def test_ledger_flags_and_prices():
    ndays = 40
    A, fades, fflag, led, cells, res = run(ndays, early_jump_day=25)
    days = led["day"]
    assert led["j"].tolist() == [200] * len(days), set(led["j"])       # only the planted bar
    assert 25 not in set(days), "L1: a jump at bar 30 (<60 bars into the session) must not trade"
    assert set(days) == set(range(15, ndays)) - {25}, sorted(set(days))   # L4 needs >= 15 reference days
    assert set(led["side"]) == {-1}
    for i, k in enumerate(days):
        assert led["F"][i] == fflag[k]
        assert led["D5"][i] == (-30.0 if fflag[k] else 30.0), led["D5"][i]
    # p_in = open[t+1+d], p_out = open[t+1+d+h]; G for d=1,h=60
    G = cells["G"][(1, 60)]
    for i, k in enumerate(days):
        assert abs(G[i] - fades[k] * 100) < 1e-9, (G[i], fades[k])


def test_planted_fade_pass_flow():
    res = run(330)[-1]
    assert res["verdict"] == "PASS_FLOW", res
    assert res["T"]["n"] >= 200


def test_planted_mirror_long_pass_flow():
    A, fades, fflag, led, cells, res = run(330, side=1)
    assert set(led["side"]) == {1}
    assert res["verdict"] == "PASS_FLOW", res


def test_flat_fixture_fails():
    res = run(330, fade_days=False)[-1]
    assert res["verdict"] == "FAIL", res


def test_small_n_inconclusive():
    res = run(60)[-1]
    assert res["verdict"] == "INCONCLUSIVE", res


def test_manifest_matches_pass():
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        f1 = tdp / "file1.csv"
        f2 = tdp / "file2.csv"
        f1.write_bytes(b"hello world")
        f2.write_bytes(b"test data 123")
        man = tdp / "DATA_MANIFEST.csv"
        rows1 = S.check_manifest([f1, f2], path=man)
        assert man.exists()
        assert len(rows1) == 2
        # Second call with existing matching manifest passes without error
        rows2 = S.check_manifest([f1, f2], path=man)
        assert rows1 == rows2


def test_manifest_refuses_changed_input():
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        f1 = tdp / "file1.csv"
        f1.write_bytes(b"original content")
        man = tdp / "DATA_MANIFEST.csv"
        S.check_manifest([f1], path=man)
        frozen_bytes = man.read_bytes()

        # Modify file by one byte
        f1.write_bytes(b"original content!")
        try:
            S.check_manifest([f1], path=man)
        except SystemExit as exc:
            assert "file1.csv" in str(exc)
        else:
            raise AssertionError("check_manifest did not raise SystemExit on changed content")
        assert man.read_bytes() == frozen_bytes, "Manifest was modified on refusal"


def test_manifest_refuses_file_set_change():
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        f1 = tdp / "file1.csv"
        f2 = tdp / "file2.csv"
        f1.write_bytes(b"content1")
        f2.write_bytes(b"content2")
        man = tdp / "DATA_MANIFEST.csv"
        S.check_manifest([f1], path=man)
        frozen_bytes = man.read_bytes()

        # Extra file
        try:
            S.check_manifest([f1, f2], path=man)
        except SystemExit as exc:
            assert "file2.csv" in str(exc) or "file" in str(exc).lower()
        else:
            raise AssertionError("check_manifest did not raise SystemExit on extra file")
        assert man.read_bytes() == frozen_bytes

        # Missing file
        man2 = tdp / "DATA_MANIFEST_2.csv"
        S.check_manifest([f1, f2], path=man2)
        frozen_bytes2 = man2.read_bytes()
        try:
            S.check_manifest([f1], path=man2)
        except SystemExit as exc:
            assert "file2.csv" in str(exc) or "file" in str(exc).lower()
        else:
            raise AssertionError("check_manifest did not raise SystemExit on missing file")
        assert man2.read_bytes() == frozen_bytes2


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        t()
        print("ok", t.__name__)
    print(f"{len(tests)} tests passed")


if __name__ == "__main__":
    main()

