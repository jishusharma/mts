from stop_strata import summarize_stop_geometry, stratified_e, stop_comparability


def test_stop_shares_and_median_p90_are_hand_computable():
    c = [
        {"side": "long", "f3_stop_tf": "D", "stop_pct": 1.0},
        {"side": "long", "f3_stop_tf": "12h", "stop_pct": 3.0},
        {"side": "short", "f3_stop_tf": "D", "stop_pct": 2.0},
    ]
    pool = [
        {"side": "long", "f3_stop_tf": "D", "stop_pct": 2.0},
        {"side": "long", "f3_stop_tf": "D", "stop_pct": 4.0},
        {"side": "short", "f3_stop_tf": "8h", "stop_pct": 1.0},
    ]
    result = summarize_stop_geometry(c, pool)
    assert result["C"]["long"]["shares"] == {"D": 0.5, "12h": 0.5}
    assert result["C"]["long"]["median_stop_pct"] == 2.0
    assert result["C"]["long"]["p90_stop_pct"] == 2.8
    assert result["control_pool"]["short"]["shares"] == {"8h": 1.0}
    assert result["control_pool"]["short"]["median_stop_pct"] == 1.0


def test_stratified_e_uses_only_strata_with_kmin_controls():
    events = [
        {"side": "long", "f3_stop_tf": "D", "net_R": 2.0},
        {"side": "long", "f3_stop_tf": "D", "net_R": 4.0},
        {"side": "long", "f3_stop_tf": "8h", "net_R": 10.0},
    ]
    controls = [
        {"side": "long", "f3_stop_tf": "D", "net_R": 1.0},
        {"side": "long", "f3_stop_tf": "D", "net_R": 3.0},
        {"side": "long", "f3_stop_tf": "8h", "net_R": 0.0},
    ]
    rows = stratified_e(events, controls, kmin=2)
    assert rows == [
        {"side": "long", "f3_stop_tf": "8h", "n_events": 1,
         "n_controls": 1, "mean_event_net_R": 10.0,
         "mean_control_net_R": None, "E": None, "eligible": False},
        {"side": "long", "f3_stop_tf": "D", "n_events": 2,
         "n_controls": 2, "mean_event_net_R": 3.0,
         "mean_control_net_R": 2.0, "E": 1.0, "eligible": True},
    ]


def test_relative_median_gap_over_25_percent_flags_noncomparable_r_units():
    c = [{"side": "long", "f3_stop_tf": "D", "stop_pct": 2.0}]
    pool = [{"side": "long", "f3_stop_tf": "D", "stop_pct": 2.6}]
    result = stop_comparability(summarize_stop_geometry(c, pool), threshold=0.25)
    assert abs(result["long"]["relative_median_gap"] - 0.30) < 1e-12
    assert result["long"]["r_units_not_comparable"] is True
