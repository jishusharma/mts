"""Guard: every non-test caller of the Fabio v3 model/manage functions passes mgmt= explicitly.

Function defaults (mgmt "dist") exist only to keep spec T01-T50 valid; the v3.1 default is "event"
(manage.py docstring), so a caller that omits mgmt silently runs dist management.
"""
import ast
import pathlib

FABIO = pathlib.Path(__file__).resolve().parents[2]            # backtest/layers/fabio
ALERTS = FABIO.parent / "alerts"
CALLS = {"model_a_trade", "model_b", "model_c", "model_d_trade", "walk_trade", "simulate_trade", "simulate_trade_legs"}
# fabio_of_model.simulate_trade is the unrelated v1 function (no mgmt parameter)
SKIP = {"fabio_of_model.py"}


def _files():
    for root in (FABIO, ALERTS):
        for p in root.rglob("*.py"):
            if "tests" in p.parts or p.name.startswith(("test_", "pending_test")) or p.name in SKIP:
                continue
            yield p


def _has_mgmt_kw(node):
    return any(k.arg == "mgmt" for k in node.keywords)


def offenders(files=None):
    bad = []
    for p in (files if files is not None else _files()):
        tree = ast.parse(p.read_text(encoding="utf-8"))
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.Module)):
                continue
            body_calls = [n for n in ast.walk(fn) if isinstance(n, ast.Call)]
            for c in body_calls:
                name = c.func.id if isinstance(c.func, ast.Name) else getattr(c.func, "attr", None)
                if name not in CALLS or _has_mgmt_kw(c):
                    continue
                splat = any(k.arg is None for k in c.keywords)
                # **kw is fine only when the enclosing function builds that dict with mgmt=
                if splat and isinstance(fn, ast.FunctionDef) and any(_has_mgmt_kw(x) for x in body_calls):
                    continue
                if isinstance(fn, ast.Module) and not isinstance(fn, ast.FunctionDef):
                    continue                                    # visit calls inside their function only
                bad.append("%s:%d %s" % (p.name, c.lineno, name))
    return sorted(set(bad))


def test_every_non_test_caller_passes_mgmt():
    assert offenders() == []


def test_guard_detects_an_omitting_caller(tmp_path):
    f = tmp_path / "caller.py"
    f.write_text("def run(bars):\n    return walk_trade(bars, 0, 1, 1.0, 1.0, 0.5)\n", encoding="utf-8")
    assert offenders([f]) == ["caller.py:2 walk_trade"]
    g = tmp_path / "ok.py"
    g.write_text("def run(bars):\n    return walk_trade(bars, 0, 1, 1.0, 1.0, 0.5, mgmt='event')\n", encoding="utf-8")
    assert offenders([g]) == []
