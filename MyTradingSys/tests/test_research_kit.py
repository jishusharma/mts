"""research_kit: expected numbers are hand arithmetic (shown in each test), never read from an existing implementation.

Copy comparison (2026-10-16, same inputs run through each frozen copy and the kit; copies are extracted by AST and executed in
isolation, the frozen studies are not imported, run or edited). "edge" = n = 1 or all rows on one day, where the kit returns NaN.

| copy | file:line | regular input | edge input | verdict |
|---|---|---|---|---|
| cluster_mean_se | research/gross_effect_screen_2026-10-15/screen.py:183 | = kit | SE 0.0 (t = inf), kit NaN | agrees (edge differs) |
| diff_cluster | research/gross_effect_screen_2026-10-15/screen.py:193 | = kit (OLS sandwich = same-day-aware) | not guarded for 1-row groups | agrees (edge differs) |
| cm_se | research/chart_read_g5_2026-10-16/common.py:104 | = kit | SE 0.0, kit NaN | agrees (edge differs) |
| mde=2.8*se (verdict_arm) | research/chart_read_g5_2026-10-16/common.py:218 | = kit.mde | - | agrees |
| mde_T = 2.8*se | research/gross_effect_screen_2026-10-15/screen.py:254 | = kit.mde | - | agrees |
| cluster_se | research/wlow_bounce_bbrsi60_2026-10-16/study.py:80 | = kit | n=1 NaN, one day SE 0.0, kit NaN | agrees (edge differs) |
| diff_stats | research/wlow_bounce_bbrsi60_2026-10-16/study.py:131 | SE 1.9319 vs kit 2.3431 on groups sharing days | - | DISAGREES: sqrt(se_a^2 + se_b^2) drops the same-day covariance |
| mde | research/volume_2026-10-09/vstats.py:130 | 0.4973 vs kit 0.5600 (sd 2.0, n 100) | - | DISAGREES: one-sided alpha 0.05 (z 1.645 + 0.8416 = 2.4866) vs 2.8 |
| mde_block cost_r | research/krown_malkan_g3_2026-10-16/event_counts.py:303 | cost 0.20 R vs kit 0.28 R at stop 0.5 % | - | DISAGREES: FEE_RT = 0.10 % (fee only) vs 0.14 % (fee + slippage) |
| mde_block MDE | research/krown_malkan_g3_2026-10-16/event_counts.py:303 | via backtest/power_mde.py, z 2.8016 | - | agrees within 0.06 % |
| holm | research/published_strats_2026-10-13/run_pub.py:503 | = kit | - | agrees |

Summary: 3 copies disagree on regular input (wlow diff_stats, vstats mde, krown cost_r); 4 more differ only at the edge
(screen.py:183 and :178, common.py:104, wlow study.py:80). The studies are frozen; their numbers stand with these caveats.
`backtest/power_mde.py` (win-rate MDE) is kept as is and is checked below for agreement with kit.mde.
"""
import ast
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from MyTradingSys.backtest import research_kit as K  # noqa: E402
from MyTradingSys.backtest.power_mde import power_mde  # noqa: E402

RESEARCH = ROOT / "MyTradingSys" / "research"


# ---------------------------------------------------------------- kit, hand arithmetic
def test_cluster_mean_se_hand():
    # g 1,2,3,4 on days 0,0,1,1: mean 2.5; day sums of (x - mean) = -2, +2; sqrt(4 + 4) / 4 = 0.7071068
    m, se = K.cluster_mean_se([1, 2, 3, 4], [0, 0, 1, 1])
    assert m == 2.5
    assert se == pytest.approx(math.sqrt(8) / 4, abs=1e-12)


def test_cluster_mean_se_each_row_its_own_day():
    # deviations -1.5 -0.5 0.5 1.5: squares 2.25 0.25 0.25 2.25 = 5; sqrt(5) / 4 = 0.5590170
    _, se = K.cluster_mean_se([1, 2, 3, 4], [10, 11, 12, 13])
    assert se == pytest.approx(math.sqrt(5) / 4, abs=1e-12)


def test_cluster_mean_se_undefined_cases_are_nan():
    assert math.isnan(K.cluster_mean_se([5.0], [0])[1])               # n = 1
    assert math.isnan(K.cluster_mean_se([1, 2, 3], [7, 7, 7])[1])     # one day: sandwich is exactly 0, not a real SE
    m, se = K.cluster_mean_se([], [])
    assert math.isnan(m) and math.isnan(se)


def test_cluster_diff_shared_days_pairs_cancel():
    # A 1,3 and B 2,4 on days 0,1: mA 2, mB 3, diff -1. Per-day influence: day0 (-1)/2 - (-1)/2 = 0; day1 1/2 - 1/2 = 0 -> SE 0
    d, se = K.cluster_diff([1, 3], [0, 1], [2, 4], [0, 1])
    assert d == -1.0
    assert se == pytest.approx(0.0, abs=1e-12)


def test_cluster_diff_disjoint_days_adds_variances():
    # A days 0,1 and B days 2,3: day influences -0.5, +0.5 (A) and +0.5, -0.5 (B); sqrt(4 x 0.25) = 1
    d, se = K.cluster_diff([1, 3], [0, 1], [2, 4], [2, 3])
    assert d == -1.0
    assert se == pytest.approx(1.0, abs=1e-12)
    # disjoint days: independent formula agrees: se_a = se_b = sqrt(1 + 1)/2 = 0.70711; sqrt(0.5 + 0.5) = 1
    assert K.cluster_diff_independent([1, 3], [0, 1], [2, 4], [2, 3])[1] == pytest.approx(1.0, abs=1e-12)


def test_cluster_diff_shared_days_differs_from_independent():
    # same pairs as the cancelling case: truth is 0, the independent formula gives sqrt(0.5 + 0.5) = 1
    assert K.cluster_diff_independent([1, 3], [0, 1], [2, 4], [0, 1])[1] == pytest.approx(1.0, abs=1e-12)
    assert K.cluster_diff([1, 3], [0, 1], [2, 4], [0, 1])[1] < 1e-9


def test_cluster_diff_small_groups_nan():
    d, se = K.cluster_diff([1.0], [0], [2, 4], [0, 1])
    assert d == -2.0 and math.isnan(se)
    assert all(math.isnan(x) for x in K.cluster_diff([], [], [1, 2], [0, 1]))


def test_t_stat_edges():
    assert K.t_stat(1.0, 0.5) == 2.0
    assert K.t_stat(1.0, 0.0) == float("inf")
    assert K.t_stat(-1.0, 0.0) == float("-inf")
    assert math.isnan(K.t_stat(0.0, 0.0))
    assert math.isnan(K.t_stat(1.0, float("nan")))


def test_norm_p_two():
    # two-sided normal tail at 1.96 is 0.05 (table value 0.0499958); at 0 it is 1
    assert K.norm_p_two(1.96) == pytest.approx(0.05, abs=1e-4)
    assert K.norm_p_two(0.0) == 1.0
    assert K.norm_p_two(-1.96) == K.norm_p_two(1.96)


def test_mde_is_2p8_se():
    assert K.mde(0.05) == pytest.approx(0.14, abs=1e-12)          # 2.8 x 0.05
    assert K.mde(0.05, z=2.0) == pytest.approx(0.10, abs=1e-12)


def test_mde_agrees_with_power_mde_win_rate_module():
    # power_mde uses (1.96 + 0.8416) sd / sqrt(n); the kit's rounded 2.8 is within 0.06 %
    r = power_mde(0.4, 2.0, 0.2, 100)
    sd = r["mde_net_r"] * math.sqrt(100) / K.MDE_Z_EXACT
    assert K.mde(sd / math.sqrt(100)) == pytest.approx(r["mde_net_r"], rel=1e-3)
    assert K.MDE_Z_EXACT == pytest.approx(2.8016, abs=1e-4)


def test_power_check_hand():
    # n 100, sd 2.0 (%): MDE = 2.8 x 2.0 / 10 = 0.56; + cost 0.14 = 0.70
    r = K.power_check(100, 2.0, 0.8, cost=0.14)
    assert r["mde"] == pytest.approx(0.56, abs=1e-12)
    assert r["needed"] == pytest.approx(0.70, abs=1e-12)
    assert r["proceed"] is True
    r2 = K.power_check(100, 2.0, 0.5, cost=0.14)                   # 0.70 > 0.5
    assert r2["proceed"] is False


def test_require_power_refuses_and_passes():
    with pytest.raises(K.PowerRefusal):
        K.require_power(100, 2.0, 0.5, cost=0.14)
    assert K.require_power(400, 2.0, 0.5, cost=0.14)["mde"] == pytest.approx(0.28, abs=1e-12)   # 2.8 x 2 / 20; 0.28 + 0.14 = 0.42 <= 0.5


def test_power_check_bad_input():
    with pytest.raises(ValueError):
        K.power_check(0, 1.0, 1.0)
    with pytest.raises(ValueError):
        K.power_check(10, -1.0, 1.0)


def test_holm_hand():
    # p .01 .04 .03, m 3. Sorted .01 .03 .04: 3 x .01 = .03; 2 x .03 = .06; 1 x .04 = .04 -> running max .06
    assert list(K.holm([0.01, 0.04, 0.03])) == pytest.approx([0.03, 0.06, 0.06], abs=1e-12)


def test_holm_caps_at_one_and_larger_family():
    assert list(K.holm([0.5, 0.6])) == pytest.approx([1.0, 1.0], abs=1e-12)          # 2 x .5 = 1.0; 1 x .6 -> max stays 1
    # 10 variants run, only 2 reported: .001 x 10 = .01; .01 x 9 = .09
    assert list(K.holm([0.001, 0.01], m=10)) == pytest.approx([0.01, 0.09], abs=1e-12)
    with pytest.raises(ValueError):
        K.holm([0.1, 0.2, 0.3], m=2)


def test_holm_reject():
    assert list(K.holm_reject([0.01, 0.04, 0.03], alpha=0.05)) == [True, False, False]   # adjusted .03 .06 .06


def test_cost_in_r():
    assert K.TAKER_RT_PCT == 0.14 and K.MAKER_IN_RT_PCT == 0.09
    assert K.taker_cost_r(0.5) == pytest.approx(0.28, abs=1e-12)       # 0.14 / 0.5
    assert K.maker_in_cost_r(0.5) == pytest.approx(0.18, abs=1e-12)    # 0.09 / 0.5
    assert K.taker_cost_r(0.35) == pytest.approx(0.4, abs=1e-12)       # 0.14 / 0.35
    assert K.cost_in_r(0.10, 0.25) == pytest.approx(0.4, abs=1e-12)
    with pytest.raises(ValueError):
        K.cost_in_r(0.14, 0.0)


# ---------------------------------------------------------------- frozen copies vs kit
def _grab(rel, name, ns):
    """Execute one top-level function of a frozen study in an isolated namespace. Returns (function, line number)."""
    tree = ast.parse((RESEARCH / rel).read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            exec(compile(ast.Module([node], []), rel, "exec"), ns)
            return ns[name], node.lineno
    raise AssertionError(f"{name} not found in {rel}")


def _base():
    return dict(np=np, math=math, defaultdict=defaultdict)


SCREEN = "gross_effect_screen_2026-10-15/screen.py"
G5 = "chart_read_g5_2026-10-16/common.py"
WLOW = "wlow_bounce_bbrsi60_2026-10-16/study.py"
KROWN = "krown_malkan_g3_2026-10-16/event_counts.py"
VSTATS = "volume_2026-10-09/vstats.py"
PUB = "published_strats_2026-10-13/run_pub.py"

G = np.array([1, 2, 3, 4, 7.5, -1, 2, 5.])
D = np.array([0, 0, 1, 1, 2, 2, 0, 1])
F = np.array([1, 0, 1, 0, 1, 0, 1, 0.])


def test_docstring_line_numbers_are_true():
    for rel, name, line in ((SCREEN, "cluster_mean_se", 183), (SCREEN, "diff_cluster", 193), (G5, "cm_se", 104),
                            (WLOW, "cluster_se", 80), (WLOW, "diff_stats", 131), (VSTATS, "mde", 130),
                            (KROWN, "mde_block", 303), (PUB, "holm", 503)):
        _, got = _grab(rel, name, _base() | {"mean": lambda x: sum(x) / len(x)})
        assert got == line, (rel, name, got)


def test_copy_screen_cluster_mean_se_agrees_regular_differs_edge():
    f, _ = _grab(SCREEN, "cluster_mean_se", _base())
    m, se = f(G, D)
    km, kse = K.cluster_mean_se(G, D)
    assert (m, se) == pytest.approx((km, kse), abs=1e-12)
    assert f(np.array([5.0]), np.array([0]))[1] == 0.0 and math.isnan(K.cluster_mean_se([5.0], [0])[1])   # edge: copy 0.0, kit NaN


def test_copy_screen_diff_cluster_agrees_with_kit_same_day_aware():
    f, _ = _grab(SCREEN, "diff_cluster", _base())
    d, se = f(G, F, D)
    kd, kse = K.cluster_diff(G[F == 1], D[F == 1], G[F == 0], D[F == 0])
    assert (d, se) == pytest.approx((kd, kse), abs=1e-9)


def test_copy_g5_cm_se_agrees_regular_differs_edge():
    f, _ = _grab(G5, "cm_se", _base())
    assert f(list(G), list(D)) == pytest.approx(K.cluster_mean_se(G, D), abs=1e-12)
    assert f([1, 2, 3], [4, 4, 4])[1] == 0.0 and math.isnan(K.cluster_mean_se([1, 2, 3], [4, 4, 4])[1])


def test_copy_wlow_cluster_se_agrees_regular_differs_edge():
    ns = _base() | {"mean": lambda x: sum(x) / len(x)}
    f, _ = _grab(WLOW, "cluster_se", ns)
    assert f(list(G), list(D)) == pytest.approx(K.cluster_mean_se(G, D)[1], abs=1e-12)
    assert math.isnan(f([5.0], [0]))                                  # n = 1: agrees with the kit
    assert f([1, 2, 3], [4, 4, 4]) == 0.0                              # one day: copy 0.0, kit NaN
    assert math.isnan(K.cluster_mean_se([1, 2, 3], [4, 4, 4])[1])


def test_copy_wlow_diff_stats_DISAGREES_on_shared_days():
    ns = _base() | {"mean": lambda x: sum(x) / len(x)}
    for name in ("cluster_se", "group_stats"):
        _grab(WLOW, name, ns)
    f, _ = _grab(WLOW, "diff_stats", ns)
    ga, da, gb, db = [1, 3, 7.5, 2], [0, 1, 2, 0], [2, 4, -1, 5], [0, 1, 2, 1]
    r = f((ga, da), (gb, db))
    d, se = K.cluster_diff(ga, da, gb, db)
    assert r["diff"] == pytest.approx(d, abs=1e-12)                    # same difference
    assert r["se"] == pytest.approx(1.9319, abs=1e-4)                  # copy: independent groups, covariance dropped
    assert se == pytest.approx(2.3431, abs=1e-4)                       # kit: shared days counted
    assert r["se"] == pytest.approx(K.cluster_diff_independent(ga, da, gb, db)[1], abs=1e-12)
    assert abs(r["se"] - se) > 0.4                                     # recorded disagreement
    assert r["mde"] == pytest.approx(2.8 * r["se"], abs=1e-12)


def test_copy_vstats_mde_DISAGREES_one_sided():
    f, _ = _grab(VSTATS, "mde", _base())
    assert f(2.0, 100) == pytest.approx((1.645 + 0.8416) * 2.0 / 10, abs=1e-12)    # 0.49732
    assert K.mde(2.0 / 10) == pytest.approx(0.56, abs=1e-12)                         # 2.8 x 0.2
    assert f(2.0, 100) < K.mde(2.0 / 10) - 0.05                                      # recorded disagreement (one-sided z)


def test_copy_krown_cost_r_DISAGREES_fee_only():
    ns = _base() | {"power_mde": power_mde, "FEE_RT": 2 * 0.0005, "RR": 2.0, "TARGET_NET_R": 0.10}
    _grab(KROWN, "median", ns)
    f, _ = _grab(KROWN, "mde_block", ns)
    r = f([{"risk_pct": 0.005}] * 100)
    assert r["cost_r"] == pytest.approx(0.20, abs=1e-12)               # 0.10 % / 0.5 %
    assert K.taker_cost_r(0.5) == pytest.approx(0.28, abs=1e-12)       # 0.14 % / 0.5 %
    # the MDE itself is power_mde's two-point formula: p0 = (1 + .2) / 3 = 0.4, mean net 0, sd per hand below
    win, loss = 2.0 - 0.2, -1.0 - 0.2
    sd = math.sqrt(0.4 * win ** 2 + 0.6 * loss ** 2)                   # mean is 0 at p0
    assert r["p0"] == pytest.approx(0.4, abs=1e-12)
    assert r["mde_net_r"] == pytest.approx(K.MDE_Z_EXACT * sd / 10, abs=1e-9)
    assert r["mde_net_r"] == pytest.approx(K.mde(sd / 10), rel=1e-3)   # agrees with the kit within 0.06 %


def test_copy_run_pub_holm_agrees():
    f, _ = _grab(PUB, "holm", _base())
    p = [0.01, 0.04, 0.03, 0.2, 0.5]
    assert list(f(p)) == pytest.approx(list(K.holm(p)), abs=1e-12)
    assert list(f([0.01, 0.04, 0.03])) == pytest.approx([0.03, 0.06, 0.06], abs=1e-12)


def test_copy_mde_constants_in_screens_equal_kit():
    # screen.py:254 and common.py:218 hardcode 2.8 * se
    for rel in (SCREEN, G5):
        assert "2.8 * " in (RESEARCH / rel).read_text(encoding="utf-8")
    assert K.MDE_Z == 2.8
