"""
Static, offline checks on the testnet suite SOURCES (no network, no secrets,
nothing imported that authenticates). Added after FIX3 verification found two
defects the offline gate could not see, because no offline test executed these
files:
  D1 run_testnet_suite.py plan(): a comment swallowed "account"/"instrument"/
     "side", so every plan failed validation on testnet.
  D2 run_testnet_suite_g1g2.py G1c: an order amount (25) that was not a
     multiple of the BTC-PERPETUAL contract size (10).

Checks:
  - every suite file parses;
  - the real plan() builder (extracted from run_testnet_suite.py by AST, not
    imported - importing the helpers would authenticate) builds, for every
    plan("...") / S.plan("...") call in every suite, a plan that passes the
    validator's structure check and executor.PLAN_ID_RE (M6);
  - the default plan compiles;
  - every literal amount passed to do.buy/do.sell/do.stop_market, and every
    literal "amount" journaled, is a multiple of CONTRACT_SIZE.

Run from the repo root:
  python MyTradingSys/execution/testnet/test_suite_static.py
"""
import sys
sys.dont_write_bytecode = True

import ast
import unittest
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import executor  # noqa: E402 - imports deribit_orders but never authenticates at import
import trade_plan_validator as tpv  # noqa: E402
from plan_compiler import compile_plan  # noqa: E402

SUITES = ["run_testnet_suite.py", "run_testnet_suite_g1g2.py", "run_testnet_suite_ft2.py"]
CONTRACT_SIZE = 10  # BTC-PERPETUAL: amounts must be a multiple of 10 USD


def _tree(name):
    return ast.parse((HERE / name).read_text(encoding="utf-8"), filename=name)


def _plan_builder():
    """The real plan() from run_testnet_suite.py, compiled on its own."""
    tree = _tree("run_testnet_suite.py")
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "plan")
    ns = {"datetime": datetime, "timezone": timezone, "timedelta": timedelta, "uuid": uuid,
          "I": "BTC-PERPETUAL"}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), "run_testnet_suite.py:plan", "exec"), ns)
    return ns["plan"]


def _plan_calls():
    """(suite, lineno, args, literal kwargs) for every plan(...) / S.plan(...) call.
    Non-literal kwargs (e.g. entry prices computed from a live mark) are dropped:
    the builder's defaults stand in, which is enough to exercise its dict shape."""
    out = []
    for suite in SUITES:
        for node in ast.walk(_tree(suite)):
            if not isinstance(node, ast.Call):
                continue
            f = node.func
            name = f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else None
            if name != "plan" or not node.args or not isinstance(node.args[0], ast.Constant):
                continue
            kw = {}
            for k in node.keywords:
                try:
                    kw[k.arg] = ast.literal_eval(k.value)
                except ValueError:
                    pass
            out.append((suite, node.lineno, node.args[0].value, kw))
    return out


class SuiteSources(unittest.TestCase):
    def test_suites_parse(self):
        for s in SUITES:
            _tree(s)

    def test_plan_builder_output_is_valid_for_every_call(self):
        build = _plan_builder()
        calls = _plan_calls()
        self.assertGreaterEqual(len(calls), 15, "expected every suite's plan() calls to be found")
        for suite, line, pid, kw in calls:
            p = build(pid, **kw)
            where = f"{suite}:{line} plan({pid!r})"
            tpv._validate_structure(p)  # raises ValidationError on a missing/bad field (D1)
            self.assertRegex(p["plan_id"], executor.PLAN_ID_RE, where)
            self.assertEqual(p["base_unit"] % CONTRACT_SIZE, 0, where)

    def test_default_plan_compiles(self):
        c = compile_plan(_plan_builder()("static_default"))
        self.assertTrue(c["entry_orders"])
        self.assertIsNotNone(c["stop_order"])

    def test_order_amounts_are_contract_multiples(self):
        n = 0
        for suite in SUITES:
            for node in ast.walk(_tree(suite)):
                if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                    continue
                if node.func.attr in ("buy", "sell") and len(node.args) >= 3:
                    amt = node.args[2]
                elif node.func.attr == "stop_market" and len(node.args) >= 4:
                    amt = node.args[3]
                else:
                    continue
                if isinstance(amt, ast.Constant) and isinstance(amt.value, (int, float)):
                    n += 1
                    self.assertEqual(amt.value % CONTRACT_SIZE, 0,
                                     f"{suite}:{node.lineno} {node.func.attr} amount {amt.value}")
        self.assertGreater(n, 0)

    def test_journaled_amounts_are_contract_multiples(self):
        for suite in SUITES:
            for node in ast.walk(_tree(suite)):
                if isinstance(node, ast.Dict):
                    for k, v in zip(node.keys, node.values):
                        if (isinstance(k, ast.Constant) and k.value == "amount"
                                and isinstance(v, ast.Constant) and isinstance(v.value, (int, float))):
                            self.assertEqual(v.value % CONTRACT_SIZE, 0, f"{suite}:{v.lineno} amount {v.value}")


if __name__ == "__main__":
    unittest.main()
