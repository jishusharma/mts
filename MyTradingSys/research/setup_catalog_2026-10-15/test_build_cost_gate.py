import build_cost_gate as b


def test_cost_r_hand_values():
    # hand: 2*0.0005/0.004 = 0.25 ; 2*0.0002/0.004 = 0.10
    assert abs(b.cost_r(0.004, 0.0005) - 0.25) < 1e-12
    assert abs(b.cost_r(0.004, 0.0002) - 0.10) < 1e-12


def test_gate_thresholds():
    assert b.gate(0.004) == "CLEARS" and b.gate(0.003) == "FAILS" and b.gate(None) == "NOT_STATED"


def test_row_count_matches_section0():
    ids = b.section0_ids((b.HERE / "SETUP_CATALOG.md").read_text(encoding="utf-8"))
    assert len(ids) == 22 and len(b.build()) == len(ids)
