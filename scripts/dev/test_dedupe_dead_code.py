"""dedupe audit batch 3: dead helpers stay removed and the root handover/ folder stays gone."""
import ast
import unittest
from pathlib import Path

DEV = Path(__file__).resolve().parent
REPO = DEV.parents[1]
DEAD = {
    "host_health.py": "ensure_policy",
    "indicator_audit_compare.py": "live_route_check",
    "role_line.py": "is_role",
    "make_layers_md.py": "family_ids",
}


class DeadCode(unittest.TestCase):
    def test_dead_defs_removed(self):
        for fn, name in DEAD.items():
            tree = ast.parse((DEV / fn).read_text(encoding="utf-8"))
            defs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
            self.assertNotIn(name, defs, f"{fn}:{name} is dead code (CODE.md rows 6-8,10)")

    def test_root_handover_folder_gone(self):
        # INFRA.md row 14: role_loader reads MyTradingSys/system/handover only
        self.assertFalse((REPO / "handover" / "LEAD.md").exists())
        self.assertFalse((REPO / "handover" / "SUPERVISOR_C.md").exists())


if __name__ == "__main__":
    unittest.main()
