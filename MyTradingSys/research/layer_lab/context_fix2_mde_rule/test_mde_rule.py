import math

from mde_rule import n_needed, verdict


def test_unpowered_negative_cell_is_inconclusive_not_fail():
    # Negative E with day SE .10 has realised MDE + cost = .28 + .066 > .30.
    assert verdict(mean_e=-0.02, day_se=0.10, week_se=0.11, cost_r=0.066,
                   t_day=-0.2, t_week=-0.18) == "INCONCLUSIVE"


def test_pass_requires_week_clustered_t_too():
    assert verdict(mean_e=0.40, day_se=0.05, week_se=0.13, cost_r=0.066,
                   t_day=8.0, t_week=3.0) == "INCONCLUSIVE"
    assert verdict(mean_e=0.40, day_se=0.05, week_se=0.06, cost_r=0.066,
                   t_day=8.0, t_week=3.3) == "PASS"


def test_realised_powered_nonpositive_e_can_fail():
    assert verdict(mean_e=-0.10, day_se=0.08, week_se=0.09, cost_r=0.066,
                   t_day=-4.0, t_week=-3.5) == "FAIL"


def test_n_needed_cost_sensitivities_match_hand_arithmetic():
    assert n_needed(0.30) == 685
    assert n_needed(0.375) == 393
