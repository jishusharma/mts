"""Context diet: what a session loads at boot stays small (operator asked repeatedly to cut context loading).
BOOT-COST per role (mts_doctor.boot_cost_roles), the ROLES.md index size and the NEXT_SESSION.md size cap."""
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "dev"))
import mts_doctor as md  # noqa: E402

NEXT = REPO / "MyTradingSys/system/NEXT_SESSION.md"
NEXT_CAP_BYTES = 12 * 1024
PIPELINER_CAP_TOKENS = 12000


class BootCostMeasure(unittest.TestCase):
    def test_section_ref_counts_only_that_section(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "MyTradingSys/system/roles").mkdir(parents=True)
            (root / "MyTradingSys/system/BIG.md").write_text("# Big\n## One\n" + "a\n" * 100 + "## Two\n" + "b\n" * 10 + "### Sub\nc\n## Three\nd\n", encoding="utf-8")
            role = ("<!-- role: X -->\nRead first: `MyTradingSys/system/BIG.md#Two`, `MyTradingSys/system/BIG.md` (rule)\n"
                    "## Boot\n1. `MyTradingSys/system/BIG.md#Two` again; `MyTradingSys/system/BIG.md#Two` once.\n")
            (root / "MyTradingSys/system/roles/x.md").write_text(role, encoding="utf-8")
            total, refs = md.boot_cost_roles(root)["x.md"]
            sizes = dict(refs)
            self.assertEqual(len(refs), 2, refs)  # the same file#section twice counts once
            self.assertEqual(sizes["MyTradingSys/system/BIG.md#Two"], len("## Two\n" + "b\n" * 10 + "### Sub\nc\n"))
            self.assertGreater(sizes["MyTradingSys/system/BIG.md"], 200)
            self.assertEqual(total, len(role.encode()) + sum(sizes.values()))

    def test_report_has_a_boot_cost_row_per_role(self):
        with tempfile.TemporaryDirectory() as d:
            path, _ = md.run(repo=REPO, out_dir=d, process=False)
            text = path.read_text(encoding="utf-8")
        for f in (REPO / "MyTradingSys/system/roles").glob("*.md"):
            self.assertIn(f"BOOT-COST {f.stem}:", text)


class RepoBootCost(unittest.TestCase):
    def test_pipeliner_boot_under_12k_tokens(self):
        total, _ = md.boot_cost_roles(REPO)["pipeliner.md"]
        self.assertLess(total // 4, PIPELINER_CAP_TOKENS, f"Pipeliner Boot reads {total} B; name sections (`path#Heading`), not whole files")

    def test_no_role_over_the_cap(self):
        for name, (total, refs) in md.boot_cost_roles(REPO).items():
            self.assertLessEqual(total // 4, md.BOOT_CAP_TOKENS, f"{name}: {total} B, files {refs}")

    def test_roles_md_is_a_slim_index(self):
        n = len((REPO / "MyTradingSys/system/ROLES.md").read_bytes())
        self.assertLess(n // 4, 1200, f"ROLES.md is {n} B; role detail belongs in roles/<role>.md")


class NextSessionSize(unittest.TestCase):
    def test_next_session_under_12_kb(self):
        n = len(NEXT.read_bytes())
        self.assertLessEqual(n, NEXT_CAP_BYTES, f"NEXT_SESSION.md is {n} B (cap {NEXT_CAP_BYTES}): archive the oldest `## ` blocks "
                             "to MyTradingSys/system/handoff_history/<date>_next_session_trim.md and point the header there")


if __name__ == "__main__":
    unittest.main()
