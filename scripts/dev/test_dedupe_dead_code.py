"""dedupe audit batches 3-4: dead helpers stay removed and the root handover/ folder stays gone."""
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
    # batch 4 (CODE.md rows 3, 4, 5, 9)
    "run_all_tests.py": "run_step",
    "role_loader.py": "explicit_role",
    "role_loader.py#2": "clean_prompt",
    "c_drive_guard.py": "sync_script",
    # batch 5 (fresh single-occurrence scan)
    "indicator_audit_compare.py#2": "engine_bb_live",
}


class DeadCode(unittest.TestCase):
    def test_dead_defs_removed(self):
        for fn, name in DEAD.items():
            tree = ast.parse((DEV / fn.split("#")[0]).read_text(encoding="utf-8"))
            defs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
            self.assertNotIn(name, defs, f"{fn}:{name} is dead code (CODE.md rows 6-8,10)")

    def test_root_handover_folder_gone(self):
        # INFRA.md row 14: role_loader reads MyTradingSys/system/handover only
        self.assertFalse((REPO / "handover" / "LEAD.md").exists())
        self.assertFalse((REPO / "handover" / "SUPERVISOR_C.md").exists())

    def test_batch4_one_shot_handover_files_in_history(self):
        # INFRA.md row 17: finished pilot notes are history, not per-login hand-over files
        for name in ("PILOT3_HAIKU.md", "PILOT3_RESULTS.md", "SUPER_RUN_2H.md"):
            self.assertFalse((REPO / "MyTradingSys/system/handover" / name).exists(), name)
            self.assertTrue((REPO / "MyTradingSys/system/handoff_history" / name).exists(), name)

    def test_batch5_unreferenced_dated_doc_in_history(self):
        # INFRA.md row 18: HOST_WORKTREES_2026-10-21 had zero readers (git grep -F), so it is history
        self.assertFalse((REPO / "MyTradingSys/system/HOST_WORKTREES_2026-10-21.md").exists())
        self.assertTrue((REPO / "MyTradingSys/system/handoff_history/HOST_WORKTREES_2026-10-21.md").exists())


if __name__ == "__main__":
    unittest.main()
