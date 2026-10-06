"""B076: SETUP_CONFIRMED is unreachable BY DESIGN until T052 supplies a Tom-cited trigger.

Spec: compiled_engine.md sec 8 [SYSTEM] notes (D6a thresholds 3/5, D6b "no code path emits it").
These tests pin that spec so a SETUP_CONFIRMED emitter cannot appear without a sourced trigger (provenance rule).
"""
import itertools
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "MyTradingSys" / "backtest"))
sys.path.insert(0, str(ROOT / "MyTradingSys" / "runtime"))

import verdict  # noqa: E402

PS1 = ROOT / "scripts" / "core" / "start-trading-day.ps1"
ENGINE_DOC = ROOT / "MyTradingSys" / "runtime" / "compiled_engine.md"
EMITTABLE = {"NO_TRADE", "WAIT_RR", "WAIT_FAR", "WAIT_TRIGGER", "WAIT_PROOF", "WATCH", "SETUP_FORMING"}


def _snap(proof, tier, direction, cvd, pv):
    return {
        "current_price": 100.0,
        "conditions": {"price_vs_va": pv, "cvd_slope": cvd},
        "setup_candidates": [{"rank": 1, "direction": direction,
                              "math": {"net_rr": 3.0, "tier": tier},
                              "score": {"proof_count": proof}}],
    }


def test_python_verdict_never_emits_setup_confirmed():
    seen = set()
    grid = itertools.product(range(0, 9), ("core", "conditional", "ignore"), ("long", "short"),
                             ("rising", "falling", "flat"), ("inside", "below_val", "above_vah"),
                             ("aligned", "contradiction", "error"))
    for proof, tier, d, cvd, pv, pd in grid:
        seen.add(verdict.compute_verdict(_snap(proof, tier, d, cvd, pv), pd=pd, floor=1.25)["verdict"])
    assert "SETUP_CONFIRMED" not in seen
    assert seen <= EMITTABLE
    assert "SETUP_FORMING" in seen  # the ladder still reaches its documented top


def test_proof_thresholds_are_3_and_5():
    ok = lambda p: verdict.compute_verdict(_snap(p, "core", "long", "flat", "inside"), floor=1.25)["verdict"]
    assert [ok(p) for p in (2, 3, 4, 5)] == ["WAIT_PROOF", "WATCH", "WATCH", "SETUP_FORMING"]


def _compute_verdict_body():
    src = PS1.read_text(encoding="utf-8")
    start = src.index("function Compute-Verdict")
    end = src.index("\nfunction ", start + 1) if "\nfunction " in src[start + 1:] else len(src)
    return src[start:end]


def test_powershell_compute_verdict_assigns_no_setup_confirmed():
    body = _compute_verdict_body()
    assigned = set(re.findall(r'(?:\$v\s*=|verdict\s*=)\s*"([A-Z_]+)"', body))
    assert assigned, "no verdict assignments parsed; function layout changed"
    assert "SETUP_CONFIRMED" not in assigned
    assert assigned <= EMITTABLE
    assert re.search(r"\$proof -lt 3", body) and re.search(r"\$proof -lt 5", body)


def test_engine_doc_records_unreachable_status_and_thresholds():
    txt = ENGINE_DOC.read_text(encoding="utf-8")
    assert "SETUP CONFIRMED is structurally unreachable" in txt
    assert "proof_count < 3 → WAIT_PROOF; 3–4 → WATCH; ≥ 5 → SETUP_FORMING" in txt
    assert "T052" in txt
