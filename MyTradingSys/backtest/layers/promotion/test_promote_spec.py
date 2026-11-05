"""Spec-derived tests for promote.py gates G1-G6, auditing fail-closed branches and boundary comparisons.
Each test specifically targets a mutant that survived test_promote.py.
"""
import copy
import json
import math
import os
import random
import subprocess
import tempfile
import unittest
from pathlib import Path

from MyTradingSys.backtest.layers.promotion import promote as pm

SID = "layer:newlayer:setup:"


def git(repo, *a, date=None):
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    if date:
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = date
    r = subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


def commit(repo, date, msg, files):
    for rel, text in files.items():
        p = Path(repo) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8", newline="\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-m", msg, date=date)
    return git(repo, "rev-parse", "HEAD")


class SpecGatesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        git(self.repo, "init", "-q")
        self.pre_sha = commit(self.repo, "2026-01-01T10:00:00+00:00", "prereg", {"r/PRE_REG.md": "pre-registration\n"})
        commit(self.repo, "2026-02-01T10:00:00+00:00", "screen", {
            "r/screen.json": json.dumps({"verdict": "PASS"}),
            "r/bt.md": "# report\nLabel: BT-TUNED\n",
            "r/ledger.csv": "study,variant,date,window,verdict\nS1,a,d,w,v\nS1,b,d,w,v\nS1,c,d,w,v\nS2,z,d,w,v\n",
            "r/val_read.md": "VALIDATION read log\n",
        })
        rng = random.Random(7)
        raw = [rng.gauss(0, 1) for _ in range(250)]
        mu = sum(raw) / 250
        sd = (sum((x - mu) ** 2 for x in raw) / 249) ** 0.5
        self.trades = [round(0.12 + 0.2417 * (x - mu) / sd, 6) for x in raw]
        (self.repo / "r" / "oos_trades.csv").write_text("net_r\n" + "".join("%r\n" % x for x in self.trades), encoding="utf-8", newline="\n")
        self.cfg = self.repo / "cfg.json"
        self.cfg.write_text(json.dumps({"trade_blocklist": [], "trade_blocklist_parked": {},
                                        "size_overrides": {SID: {"size_usd": 50, "max_loss_usd": 2}}}), encoding="utf-8")
        self.m = {
            "setup_id": SID,
            "layer": "newlayer",
            "pre_reg": {"path": "r/PRE_REG.md", "git_sha": self.pre_sha, "plausible_net_r": 0.12},
            "screen_verdict": {"path": "r/screen.json"},
            "backtest": {"report_path": "r/bt.md", "label": "BT-TUNED"},
            "oos": {"fee_net": True, "net_r": 0.12, "ci_low": 0.09, "ci_high": 0.15, "n_trades": 250, "trades_csv": "r/oos_trades.csv"},
            "trial_ledger": {"path": "r/ledger.csv", "entry_id": "S1", "variants": 3},
            "validation_reads": [{"at": "2026-02-10", "ref": "r/val_read.md"}],
            "holdout_reads": [{"at": "2026-02-11", "ref": "h1"}],
            "requested_mode": "shadow"
        }

    def tearDown(self):
        self.tmp.cleanup()

    def chk(self, m=None):
        return pm.check(self.m if m is None else m, repo=self.repo, config_path=self.cfg)

    def rejected(self, fn, needle):
        m = copy.deepcopy(self.m)
        fn(m)
        r = self.chk(m)
        self.assertEqual(r["result"], "REJECT", r)
        self.assertTrue(any(needle in x for x in r["reasons"]), (needle, r["reasons"]))

    # Gate G1: M05_G1_DATE_EQ
    def test_pre_reg_commit_date_equal_to_screen_verdict_rejects(self):
        """G1: PRE_REG must strictly predate the screen verdict. Equal commit timestamps must REJECT."""
        same_date = "2026-02-01T10:00:00+00:00"
        same_sha = commit(self.repo, same_date, "same_date_prereg", {"r/PRE_REG_SAME.md": "prereg same\n"})
        def f(m):
            m["pre_reg"].update(path="r/PRE_REG_SAME.md", git_sha=same_sha)
        self.rejected(f, "does not predate")

    # Gate G2: M07_G2_SCR_FILE
    def test_screen_verdict_file_missing_rejects(self):
        """G2: missing screen verdict file fails closed with an explicit REJECT reason."""
        self.rejected(lambda m: m["screen_verdict"].update(path="r/missing_screen.json"), "screen verdict file missing or unreadable")

    # Gate G3: M11_G3_LABEL_ATTR
    def test_backtest_manifest_label_mismatch_rejects(self):
        """G3: manifest backtest label must equal BT-TUNED even if the file text contains BT-TUNED."""
        self.rejected(lambda m: m["backtest"].update(label="BT-EXPLORATORY"), "backtest report lacks the BT-TUNED label")

    # Gate G4: M16_G4_CSV_COL
    def test_trades_csv_missing_net_r_column_rejects(self):
        """G4: trades_csv missing the net_r column must REJECT."""
        p = self.repo / "r" / "bad_col.csv"
        p.write_text("pnl\n0.12\n0.05\n", encoding="utf-8", newline="\n")
        self.rejected(lambda m: m["oos"].update(trades_csv="r/bad_col.csv"), "no net_r column")

    # Gate G4: M17_G4_CSV_NAN
    def test_trades_csv_nan_in_net_r_rejects(self):
        """G4: trades_csv containing NaN in net_r column must REJECT."""
        p = self.repo / "r" / "nan_trades.csv"
        p.write_text("net_r\n0.12\nnan\n0.15\n", encoding="utf-8", newline="\n")
        self.rejected(lambda m: m["oos"].update(trades_csv="r/nan_trades.csv"), "non-finite net_r")

    # Gate G4: M18_G4_CSV_EMPTY
    def test_trades_csv_empty_trades_rejects(self):
        """G4: trades_csv with header only (0 trades) must REJECT."""
        p = self.repo / "r" / "empty_trades.csv"
        p.write_text("net_r\n", encoding="utf-8", newline="\n")
        self.rejected(lambda m: m["oos"].update(trades_csv="r/empty_trades.csv"), "no trades")

    # Gate G4: M20_G4_TOL_CI_LOW
    def test_oos_ci_low_recompute_tolerance_isolated_rejects(self):
        """G4: manifest ci_low differing from trades_csv recompute by > 0.01 R must REJECT even if net_r and ci_high match."""
        # Recomputed ci_low is ~0.09. Set manifest ci_low to 0.07 (> 0.01 R diff)
        self.rejected(lambda m: m["oos"].update(ci_low=0.07), "differs from the recompute by more than 0.01 R")

    # Gate G4: M21_G4_TOL_CI_HIGH
    def test_oos_ci_high_recompute_tolerance_isolated_rejects(self):
        """G4: manifest ci_high differing from trades_csv recompute by > 0.01 R must REJECT even if net_r and ci_low match."""
        # Recomputed ci_high is ~0.15. Set manifest ci_high to 0.17 (> 0.01 R diff)
        self.rejected(lambda m: m["oos"].update(ci_high=0.17), "differs from the recompute by more than 0.01 R")

    # Gate G4: M23_G4_NET_R_POS
    def test_oos_net_r_zero_rejects(self):
        """G4: fee-net OOS net_r == 0.0 is not strictly positive and must REJECT."""
        self.rejected(lambda m: m["oos"].update(net_r=0.0, ci_low=-0.05, ci_high=0.05), "fee-net OOS net R 0.0 is not above 0")

    # Gate G4: M25_G4_CI_CONSISTENT_LO
    def test_oos_ci_low_greater_than_net_r_rejects(self):
        """G4: ci_low > net_r violates ci_low <= net_r <= ci_high and must REJECT."""
        self.rejected(lambda m: m["oos"].update(ci_low=0.14, net_r=0.12, ci_high=0.16), "outside its own CI")

    # Gate G4: M29_G4_INT_TRADES
    def test_oos_float_n_trades_rejects(self):
        """G4: non-integer n_trades (e.g. 250.5) must REJECT."""
        self.rejected(lambda m: m["oos"].update(n_trades=250.5), "floor")

    # Gate G4: M30_G4_MIN_TRADES
    def test_oos_min_trades_floor_isolated_rejects(self):
        """G4: n_trades < MIN_TRADES (30) must REJECT even when MDE floor calculation is bypassed."""
        def f(m):
            # Omit trial_ledger variants to bypass MDE floor calculation, leaving MIN_TRADES floor active
            del m["trial_ledger"]
            m["oos"].update(n_trades=29)
        r = self.chk(copy.deepcopy(self.m))
        m = copy.deepcopy(self.m)
        f(m)
        res = self.chk(m)
        self.assertEqual(res["result"], "REJECT")
        self.assertTrue(any("below the floor of 30" in x for x in res["reasons"]), res["reasons"])

    # Gate G5: M32_G5_TL_VAR_BOOL
    def test_trial_ledger_variants_bool_rejects(self):
        """G5: trial_ledger variants cannot be a boolean (e.g. True)."""
        self.rejected(lambda m: m["trial_ledger"].update(variants=True), "trial ledger path, entry_id or variants (int >= 1) missing/unreadable")

    # Gate G5: M33_G5_TL_VAR_MIN1
    def test_trial_ledger_variants_zero_rejects(self):
        """G5: trial_ledger variants must be >= 1 (0 must REJECT)."""
        self.rejected(lambda m: m["trial_ledger"].update(variants=0), "trial ledger path, entry_id or variants (int >= 1) missing/unreadable")

    # Gate G5: M36_G5_TL_VAR_MISMATCH_LT
    def test_trial_ledger_manifest_variants_greater_than_ledger_rows_rejects(self):
        """G5: manifest variants > ledger rows (e.g. manifest says 4, ledger has 3) must REJECT."""
        self.rejected(lambda m: m["trial_ledger"].update(variants=4), "lists 3 variants for S1, manifest says 4")

    # Gate G6: M38_G6_REC_NONLIST
    def test_validation_reads_non_list_rejects(self):
        """G6: validation_reads must be a list (a 1-element dict must REJECT, not crash with KeyError)."""
        self.rejected(lambda m: m.update(validation_reads={"single": {"at": "2026-02-10", "ref": "r/val_read.md"}}), "must hold exactly one read record (found non-list)")


if __name__ == "__main__":
    unittest.main()
