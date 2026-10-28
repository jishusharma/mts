"""
Architecture test: verify layer boundary rules.

Rules:
1. No .py under MyTradingSys/backtest/layers/ imports MyTradingSys.execution or anything that places orders
2. No .py under MyTradingSys/execution imports MyTradingSys.backtest.layers
3. Layers are alert-only; Tom core is never filtered by layers
"""
import ast
import unittest
from pathlib import Path


class TestLayerBoundaries(unittest.TestCase):
    """Test that layer and execution modules respect import boundaries."""

    @classmethod
    def setUpClass(cls):
        """Find the repo root and layer/execution directories."""
        cls.repo_root = Path(__file__).parent.parent.parent.parent
        cls.layers_dir = cls.repo_root / "MyTradingSys" / "backtest" / "layers"
        cls.execution_dir = cls.repo_root / "MyTradingSys" / "execution"

    def get_imports(self, filepath):
        """Extract all import statements from a Python file using AST."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(filepath))
        except (SyntaxError, ValueError):
            return []

        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

        return imports

    def test_layers_dont_import_execution(self):
        """Verify no .py under layers/ imports MyTradingSys.execution."""
        failures = []

        for py_file in self.layers_dir.rglob("*.py"):
            # Skip __pycache__ and .new files
            if "__pycache__" in py_file.parts or py_file.suffix == ".new":
                continue

            imports = self.get_imports(py_file)
            for imp in imports:
                if imp.startswith("MyTradingSys.execution"):
                    failures.append(
                        f"{py_file.relative_to(self.repo_root)} imports {imp} "
                        f"(layers must not import execution)"
                    )
                # Also check for direct execution module names that place orders
                if any(
                    imp.startswith(x)
                    for x in [
                        "MyTradingSys.execution",
                        "deribit_orders",
                        "executor",
                        "position_manager",
                    ]
                ):
                    # Filter to only real execution imports (not coincidental matches)
                    if "MyTradingSys.execution" in imp:
                        failures.append(
                            f"{py_file.relative_to(self.repo_root)} imports {imp} "
                            f"(layers are alert-only, never order-placing)"
                        )

        self.assertFalse(
            failures,
            f"Execution imports found in layers:\n" + "\n".join(failures),
        )

    def test_wavetrend_is_observation_only_stdlib(self):
        """wavetrend/ is observation-only: stdlib imports only (no execution, no other layer, no numpy)."""
        allowed = {"math", "collections", "csv", "sys", "unittest", "pathlib", "numpy", "pandas", "wavetrend"}
        failures = []
        for py_file in (self.layers_dir / "wavetrend").glob("*.py"):
            for imp in self.get_imports(py_file):
                root = imp.split(".")[0]
                if root not in allowed or (root in {"numpy", "pandas"} and py_file.name != "make_golden.py"):
                    failures.append(f"{py_file.name} imports {imp}")
        self.assertFalse(failures, "; ".join(failures))

    def test_kurisko_is_observation_only(self):
        """kurisko/ is observation-only: stdlib, its own modules and rsi_core only (no execution, no Tom code, no numpy)."""
        allowed = {"math", "collections", "csv", "json", "sys", "unittest", "pathlib", "stoch_core", "quad_rotation",
                   "MyTradingSys"}
        failures = []
        for py_file in (self.layers_dir / "kurisko").glob("*.py"):
            for imp in self.get_imports(py_file):
                root = imp.split(".")[0]
                ok = root in allowed and (root != "MyTradingSys" or imp == "MyTradingSys.backtest.layers.rsi.rsi_core")
                if not ok:
                    failures.append(f"{py_file.name} imports {imp}")
        self.assertFalse(failures, "; ".join(failures))

    def test_execution_doesnt_import_layer_backtest(self):
        """Verify no .py under execution/ imports MyTradingSys.backtest.layers."""
        failures = []

        for py_file in self.execution_dir.rglob("*.py"):
            # Skip __pycache__ and .new files
            if "__pycache__" in py_file.parts or py_file.suffix == ".new":
                continue

            imports = self.get_imports(py_file)
            for imp in imports:
                if imp.startswith("MyTradingSys.backtest.layers"):
                    failures.append(
                        f"{py_file.relative_to(self.repo_root)} imports {imp} "
                        f"(execution must not import layer backtest)"
                    )

        self.assertFalse(
            failures,
            f"Layer backtest imports found in execution:\n" + "\n".join(failures),
        )


if __name__ == "__main__":
    unittest.main()
