"""B127 TC-TOP5-2: Fabio v3 package isolation. Spec (pending_test_fabio_v3.py T50, FABIO_V3_SPEC :5-6, :342): v3 modules import only
stdlib, orderflow_bars and their own siblings - nothing from execution, layers.alerts, Tom/core. That is the structural form of
'disable Tom, Fabio unchanged'."""
import ast
from pathlib import Path

V3 = Path(__file__).resolve().parents[1] / "backtest" / "layers" / "fabio" / "v3"
BAD = {"execution", "alerts", "core", "tom"}


def bad_imports(source):
    out = []
    for node in ast.walk(ast.parse(source)):
        mods = []
        if isinstance(node, ast.Import):
            mods = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            mods = [("." * node.level) + (node.module or "")] + [(node.module or "") + "." + a.name for a in node.names]
        for m in mods:
            if BAD & {p.lower() for p in m.replace("..", ".").split(".") if p}:
                out.append(m)
    return out


def test_detector_flags_tom_and_execution_imports():
    assert bad_imports("from MyTradingSys.execution import auto_trader") != []
    assert bad_imports("import MyTradingSys.backtest.layers.alerts.live_runner_cli") != []
    assert bad_imports("from ..core import x") != []
    assert bad_imports("import math\nfrom . import models\nfrom MyTradingSys.backtest.layers.fabio import orderflow_bars") == []


def test_v3_package_has_no_tom_execution_or_alerts_imports():
    files = sorted(V3.glob("*.py"))
    assert {p.name for p in files} >= {"engine.py", "models.py", "signals.py", "fill.py", "manage.py", "costs.py", "day_gates.py"}
    offenders = {p.name: bad_imports(p.read_text(encoding="utf-8")) for p in files}
    assert {k: v for k, v in offenders.items() if v} == {}
