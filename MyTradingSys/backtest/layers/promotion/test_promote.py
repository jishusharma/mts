"""Tests for promote.py gates (check/register/demote/verify). Each gate has a mutant that must REJECT; the good manifest
must PASS. Uses a throwaway git repo with dated commits (PRE_REG committed 2026-01-01, screen verdict 2026-02-01).
Also the CI hook: every entry of the shipped registry must pass `check` (shipped registry is empty)."""
import copy
import csv
import datetime as dt
import json
import os
import random
import subprocess
import tempfile
import unittest
from pathlib import Path

from MyTradingSys.backtest.layers.promotion import promote as pm
from MyTradingSys.backtest.layers.promotion import registry as reg

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


class Base(unittest.TestCase):
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
            "r/ledger40.csv": "study,variant,date,window,verdict\n" + "".join("S40,v%d,d,w,v\n" % i for i in range(40))})
        rng = random.Random(7)
        raw = [rng.gauss(0, 1) for _ in range(250)]
        mu = sum(raw) / 250
        sd = (sum((x - mu) ** 2 for x in raw) / 249) ** 0.5
        self.trades = [round(0.12 + 0.2417 * (x - mu) / sd, 6) for x in raw]       # mean 0.12 +- rounding, n=250
        (self.repo / "r" / "oos_trades.csv").write_text("net_r\n" + "".join("%r\n" % x for x in self.trades), encoding="utf-8", newline="\n")
        self.cfg = self.repo / "cfg.json"
        self.cfg.write_text(json.dumps({"trade_blocklist": [], "trade_blocklist_parked": {"layer:session:": "x"},
                                        "size_overrides": {SID: {"size_usd": 50, "max_loss_usd": 2}}}), encoding="utf-8")
        self.regp = self.repo / "promoted.json"
        self.regp.write_text('{"version": 1, "entries": []}', encoding="utf-8")
        self.m = {"setup_id": SID, "layer": "newlayer",
                  "pre_reg": {"path": "r/PRE_REG.md", "git_sha": self.pre_sha},
                  "screen_verdict": {"path": "r/screen.json"},
                  "backtest": {"report_path": "r/bt.md", "label": "BT-TUNED"},
                  "oos": {"fee_net": True, "net_r": 0.12, "ci_low": 0.09, "ci_high": 0.15, "n_trades": 250, "trades_csv": "r/oos_trades.csv"},
                  "trial_ledger": {"path": "r/ledger.csv", "entry_id": "S1", "variants": 3},
                  "validation_reads": [{"at": "2026-02-10", "ref": "r/val_read.md"}],
                  "holdout_reads": [{"at": "2026-02-11", "ref": "h1"}],
                  "requested_mode": "shadow"}

    def tearDown(self):
        self.tmp.cleanup()

    def chk(self, m=None):
        return pm.check(self.m if m is None else m, repo=self.repo, config_path=self.cfg)

    def mut(self, fn):
        m = copy.deepcopy(self.m)
        fn(m)
        return self.chk(m)

    def rejected(self, fn, needle):
        r = self.mut(fn)
        self.assertEqual(r["result"], "REJECT", r)
        self.assertTrue(any(needle in x for x in r["reasons"]), r["reasons"])


class Gates(Base):
    def test_good_manifest_passes(self):
        r = self.chk()
        self.assertEqual((r["result"], r["reasons"]), ("PASS", []))

    def test_holm_adjusted_ci_for_many_variants(self):
        def f(m):
            m["trial_ledger"].update(path="r/ledger40.csv", entry_id="S40", variants=40)
            m["oos"].update(ci_low=0.02, ci_high=0.22)
        self.rejected(f, "Holm")

    def test_validation_read_ref_must_be_a_logged_file(self):
        self.rejected(lambda m: m["validation_reads"][0].update(ref="no/such/log.md"), "validation_reads ref")
        self.rejected(lambda m: m["validation_reads"][0].update(ref="  "), "validation_reads")

    def test_trade_floor_is_mde_based(self):
        self.rejected(lambda m: m["oos"].update(ci_low=0.02, ci_high=0.22, n_trades=31), "MDE")

    def test_recompute_matches_manifest_numbers(self):
        n, mean, lo, hi = pm.recompute_oos(self.repo / "r" / "oos_trades.csv")
        self.assertEqual(n, 250)
        self.assertAlmostEqual(mean, sum(self.trades) / 250, places=9)
        self.assertLess(lo, mean)
        self.assertGreater(hi, mean)
        self.assertEqual(pm.recompute_oos(self.repo / "r" / "oos_trades.csv"), (n, mean, lo, hi))    # seeded: deterministic

    def test_typed_net_r_far_from_trades_csv_rejects(self):
        # manifest says 0.5 R (CI around it) but the csv mean is 0.12
        self.rejected(lambda m: m["oos"].update(net_r=0.5, ci_low=0.45, ci_high=0.55), "recompute")

    def test_missing_trades_csv_rejects(self):
        def f(m):
            del m["oos"]["trades_csv"]
        self.rejected(f, "trades_csv")
        self.rejected(lambda m: m["oos"].update(trades_csv="r/none.csv"), "trades_csv")

    def test_trades_count_must_match_within_five_percent(self):
        self.rejected(lambda m: m["oos"].update(n_trades=300), "recompute")

    def test_matching_trades_csv_passes_and_legacy_is_check_only_flag(self):
        self.assertEqual(self.chk()["result"], "PASS")
        m = copy.deepcopy(self.m)
        del m["oos"]["trades_csv"]
        self.assertEqual(pm.check(m, repo=self.repo, config_path=self.cfg, legacy=True)["result"], "PASS")
        self.assertEqual(pm.check(m, repo=self.repo, config_path=self.cfg)["result"], "REJECT")

    def test_unreadable_manifest_rejects(self):
        r = pm.check(self.repo / "nope.json", repo=self.repo, config_path=self.cfg)
        self.assertEqual(r["result"], "REJECT")

    def test_missing_field_rejects(self):
        for k in pm.REQUIRED:
            m = copy.deepcopy(self.m)
            del m[k]
            self.assertEqual(self.chk(m)["result"], "REJECT", k)

    def test_pre_reg_missing_file(self):
        self.rejected(lambda m: m["pre_reg"].update(path="r/none.md"), "PRE_REG file")

    def test_pre_reg_must_predate_screen(self):
        # PRE_REG committed AFTER the screen verdict
        late = commit(self.repo, "2026-03-01T10:00:00+00:00", "late", {"r/PRE_REG.md": "rewritten\n"})
        self.rejected(lambda m: m["pre_reg"].update(git_sha=late), "does not predate")

    def test_pre_reg_bad_sha(self):
        self.rejected(lambda m: m["pre_reg"].update(git_sha="deadbeef"), "git_sha")

    def test_screen_verdict_must_pass(self):
        (self.repo / "r" / "screen.json").write_text(json.dumps({"verdict": "FAIL"}), encoding="utf-8")
        r = self.chk()
        self.assertEqual(r["result"], "REJECT")
        self.assertTrue(any("need PASS" in x for x in r["reasons"]))

    def test_screen_verdict_text_form_and_garbage(self):
        (self.repo / "r" / "screen.json").write_text("blah\nVERDICT: PASS\n", encoding="utf-8")
        self.assertEqual(self.chk()["result"], "PASS")
        (self.repo / "r" / "screen.json").write_text("passed I think", encoding="utf-8")
        self.assertEqual(self.chk()["result"], "REJECT")

    def test_screen_verdict_uncommitted_has_no_date(self):
        (self.repo / "r" / "new_screen.json").write_text(json.dumps({"verdict": "PASS"}), encoding="utf-8")
        self.rejected(lambda m: m["screen_verdict"].update(path="r/new_screen.json"), "not committed")

    def test_backtest_label_required(self):
        (self.repo / "r" / "bt.md").write_text("# report without label\n", encoding="utf-8")
        r = self.chk()
        self.assertTrue(any("BT-TUNED" in x for x in r["reasons"]))

    def test_oos_net_r_must_be_positive(self):
        self.rejected(lambda m: m["oos"].update(net_r=-0.01, ci_low=-0.2, ci_high=0.1), "not above 0")

    def test_ci_low_must_be_positive(self):
        self.rejected(lambda m: m["oos"].update(ci_low=0.0), "CI low")

    def test_oos_must_be_fee_net(self):
        self.rejected(lambda m: m["oos"].update(fee_net=False), "fee_net")

    def test_oos_inconsistent_ci(self):
        self.rejected(lambda m: m["oos"].update(ci_high=0.05), "outside its own CI")

    def test_oos_nan_and_strings_reject(self):
        self.rejected(lambda m: m["oos"].update(net_r=float("nan")), "numeric")
        self.rejected(lambda m: m["oos"].update(n_trades="250"), "numeric")

    def test_oos_trade_floor(self):
        self.rejected(lambda m: m["oos"].update(n_trades=5), "floor")

    def test_trial_ledger_variant_count_must_match(self):
        self.rejected(lambda m: m["trial_ledger"].update(variants=2), "lists 3 variants")

    def test_trial_ledger_entry_must_exist(self):
        self.rejected(lambda m: m["trial_ledger"].update(entry_id="S9"), "no rows")

    def test_trial_ledger_missing_file(self):
        self.rejected(lambda m: m["trial_ledger"].update(path="r/none.csv"), "trial ledger")

    def test_validation_exactly_one_read(self):
        self.rejected(lambda m: m.update(validation_reads=[]), "missing fields")
        self.rejected(lambda m: m["validation_reads"].append({"at": "2026-03-01", "ref": "v2"}), "exactly one")

    def test_holdout_exactly_one_read(self):
        self.rejected(lambda m: m["holdout_reads"].append({"at": "2026-03-01", "ref": "h2"}), "exactly one")
        self.rejected(lambda m: m.update(holdout_reads=[{"at": "", "ref": "x"}]), "non-empty")

    def test_parked_layer_rejects(self):
        def f(m):
            m["setup_id"], m["layer"] = "layer:session:session_momentum:", "session"
        self.rejected(f, "trade_blocklist_parked")

    def test_blocklisted_layer_rejects_and_unreadable_config_rejects(self):
        self.cfg.write_text(json.dumps({"trade_blocklist": [SID], "trade_blocklist_parked": {}}), encoding="utf-8")
        self.assertTrue(any("trade_blocklist lists" in x for x in self.chk()["reasons"]))
        self.cfg.write_text("{broken", encoding="utf-8")
        self.assertTrue(any("unreadable" in x for x in self.chk()["reasons"]))

    def test_bad_mode_rejects(self):
        self.rejected(lambda m: m.update(requested_mode="live"), "requested_mode")

    def test_report_path_cannot_escape_repo(self):
        self.rejected(lambda m: m["backtest"].update(report_path="../outside.md"), "backtest report")


class Register(Base):
    def write_manifest(self, m=None):
        p = self.repo / "m" / "manifest.json"
        p.parent.mkdir(exist_ok=True)
        p.write_text(json.dumps(m or self.m), encoding="utf-8")
        return p

    def reg(self, mode="shadow", m=None):
        return pm.register(self.write_manifest(m), mode, repo=self.repo, registry_path=self.regp, config_path=self.cfg)

    def entries(self):
        return reg.load_registry(self.regp)[0]

    def test_register_shadow_writes_entry(self):
        ok, msg, _ = self.reg()
        self.assertTrue(ok, msg)
        e = self.entries()
        self.assertEqual([(x["setup_id"], x["mode"]) for x in e], [(SID, "shadow")])
        self.assertEqual(e[0]["commit"], git(self.repo, "rev-parse", "HEAD"))

    def test_register_rejected_manifest_writes_nothing(self):
        m = copy.deepcopy(self.m)
        m["oos"]["ci_low"] = -0.1
        ok, msg, _ = self.reg(m=m)
        self.assertFalse(ok)
        self.assertEqual(self.entries(), [])

    def test_register_twice_refused(self):
        self.reg()
        self.assertFalse(self.reg()[0])

    def test_testnet_needs_shadow_first(self):
        m = dict(self.m, requested_mode="testnet")
        ok, msg, _ = self.reg("testnet", m)
        self.assertFalse(ok)
        self.assertIn("shadow entry", msg)

    def test_testnet_needs_sized_flag_default_stays_shadow(self):
        self.reg()
        self.cfg.write_text(json.dumps({"trade_blocklist": [], "trade_blocklist_parked": {}, "size_overrides": {}}), encoding="utf-8")
        ok, msg, _ = self.reg("testnet", dict(self.m, requested_mode="testnet"))
        self.assertFalse(ok)
        self.assertIn("stays shadow", msg)
        self.assertEqual(self.entries()[0]["mode"], "shadow")

    def test_testnet_with_flag_after_shadow(self):
        self.reg()
        ok, msg, _ = self.reg("testnet", dict(self.m, requested_mode="testnet"))
        self.assertTrue(ok, msg)
        self.assertEqual([x["mode"] for x in self.entries()], ["testnet"])

    def test_mode_must_match_manifest(self):
        ok, msg, _ = self.reg("testnet")          # manifest asks for shadow
        self.assertFalse(ok)

    def test_unreadable_registry_refuses_write(self):
        self.regp.write_text("{bad", encoding="utf-8")
        ok, msg, _ = self.reg()
        self.assertFalse(ok)

    def test_demote(self):
        self.reg()
        self.reg("testnet", dict(self.m, requested_mode="testnet"))
        self.assertTrue(pm.demote(SID, "shadow", self.regp)[0])
        self.assertEqual(self.entries()[0]["mode"], "shadow")
        self.assertTrue(pm.demote(SID, "off", self.regp, self.cfg)[0])
        self.assertEqual(self.entries(), [])
        self.assertFalse(pm.demote(SID, "off", self.regp, self.cfg)[0])

    def test_demote_off_blocks_in_the_list_auto_trader_enforces(self):
        """H2: off must not return a sized, rule-mapped setup to trading."""
        import importlib.util
        import sys
        self.reg()
        self.reg("testnet", dict(self.m, requested_mode="testnet"))
        self.assertTrue(pm.demote(SID, "off", self.regp, self.cfg, now=dt.datetime(2026, 10, 16, tzinfo=dt.timezone.utc))[0])
        cfg = json.loads(self.cfg.read_text(encoding="utf-8"))
        self.assertIn(SID, cfg["trade_blocklist"])
        self.assertIn("demoted off 2026-10-16", cfg["trade_blocklist_reasons"][SID])
        spec = importlib.util.spec_from_file_location("_at", pm.REPO / "MyTradingSys" / "execution" / "auto_trader.py")
        sys.path.insert(0, str(pm.REPO / "MyTradingSys" / "execution"))
        try:
            at = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(at)
        finally:
            sys.path.pop(0)
        self.assertTrue(at.trade_block_reason(SID + "15m", cfg))

    def test_demote_off_grandfathered_source_without_entry_blocks(self):
        gf = "layer:fabio:volume_fvg:"
        self.assertTrue(pm.demote(gf, "off", self.regp, self.cfg)[0])
        self.assertIn(gf, json.loads(self.cfg.read_text(encoding="utf-8"))["trade_blocklist"])
        self.assertFalse(pm.demote(gf, "off", self.regp, self.cfg)[0])     # already blocked, nothing to do
        self.assertFalse(pm.demote(gf, "shadow", self.regp, self.cfg)[0])

    def test_demote_off_refuses_when_config_unwritable_registry_untouched(self):
        self.reg()
        self.cfg.write_text("{broken", encoding="utf-8")
        ok, msg = pm.demote(SID, "off", self.regp, self.cfg)
        self.assertFalse(ok)
        self.assertEqual([x["setup_id"] for x in self.entries()], [SID])
        self.cfg.write_text(json.dumps({"trade_blocklist": "oops"}), encoding="utf-8")
        self.assertFalse(pm.demote(SID, "off", self.regp, self.cfg)[0])
        self.assertEqual([x["setup_id"] for x in self.entries()], [SID])

    def test_verify_flags_sized_prefix_without_registry_grandfather_or_block(self):
        self.assertTrue(any(SID in x for x in pm.verify(self.repo, self.regp, self.cfg)))     # sized, nothing covers it
        c = json.loads(self.cfg.read_text(encoding="utf-8"))
        c["pre_pipeline_sources"] = {SID: {"reason": "r", "review_by": "2026-10-23"}}
        self.cfg.write_text(json.dumps(c), encoding="utf-8")
        self.assertEqual(pm.verify(self.repo, self.regp, self.cfg), [])                        # grandfathered
        c["pre_pipeline_sources"] = {}
        c["trade_blocklist"] = [SID]
        self.cfg.write_text(json.dumps(c), encoding="utf-8")
        self.assertEqual(pm.verify(self.repo, self.regp, self.cfg), [])                        # blocked
        self.cfg.write_text("{bad", encoding="utf-8")
        self.assertTrue(pm.verify(self.repo, self.regp, self.cfg))                             # fail closed

    def test_pre_reg_edited_after_registration_rejects(self):
        """M4: the PRE_REG blob at git_sha must equal HEAD's."""
        self.assertEqual(self.chk()["result"], "PASS")
        commit(self.repo, "2026-01-15T10:00:00+00:00", "quiet edit", {"r/PRE_REG.md": "pre-registration, edited\n"})
        r = self.chk()
        self.assertEqual(r["result"], "REJECT")
        self.assertTrue(any("edited after registration" in x for x in r["reasons"]), r["reasons"])

    def test_has_testnet_flag_validates_like_auto_trader(self):
        """L7: one validator; a size auto_trader would raise on (not a 10 multiple, over ceiling, no max_loss) is no flag."""
        for bad in ({"size_usd": 55, "max_loss_usd": 2}, {"size_usd": 50}, {"size_usd": 20000, "max_loss_usd": 2},
                    {"size_usd": 50, "max_loss_usd": -1}, {"size_usd": True, "max_loss_usd": 2}):
            self.cfg.write_text(json.dumps({"size_overrides": {SID: bad}}), encoding="utf-8")
            self.assertFalse(pm.has_testnet_flag(SID, self.cfg), bad)
        self.cfg.write_text(json.dumps({"size_overrides": {SID: {"size_usd": 50, "max_loss_usd": 2}}}), encoding="utf-8")
        self.assertTrue(pm.has_testnet_flag(SID, self.cfg))

    def test_size_ceiling_matches_auto_trader(self):
        import re
        src = (pm.REPO / "MyTradingSys" / "execution" / "auto_trader.py").read_text(encoding="utf-8")
        self.assertEqual(int(re.search(r"^SIZE_CEILING_USD = (\d+)", src, re.M).group(1)), pm.SIZE_CEILING_USD)

    def test_verify_green_then_red_when_evidence_breaks(self):
        self.reg()
        self.assertEqual(pm.verify(self.repo, self.regp, self.cfg), [])
        (self.repo / "r" / "screen.json").write_text(json.dumps({"verdict": "FAIL"}), encoding="utf-8")
        self.assertTrue(pm.verify(self.repo, self.regp, self.cfg))

    def test_verify_grandfathers_registered_entry_without_trades_csv(self):
        self.reg()
        mp = self.repo / "m" / "manifest.json"
        m = json.loads(mp.read_text(encoding="utf-8"))
        del m["oos"]["trades_csv"]
        mp.write_text(json.dumps(m), encoding="utf-8")
        self.assertEqual(pm.verify(self.repo, self.regp, self.cfg), [])          # legacy entry: no csv, still green
        m["oos"]["trades_csv"] = "r/oos_trades.csv"
        m["oos"].update(net_r=0.5, ci_low=0.45, ci_high=0.55)
        mp.write_text(json.dumps(m), encoding="utf-8")
        self.assertTrue(pm.verify(self.repo, self.regp, self.cfg))               # with a csv it is recomputed: red

    def test_verify_red_on_hand_inserted_entry(self):
        e = {"setup_id": SID, "mode": "shadow", "manifest": "m/none.json", "promoted_at": "2026-10-15T00:00:00Z", "commit": "x"}
        self.regp.write_text(json.dumps({"version": 1, "entries": [e]}), encoding="utf-8")
        self.assertTrue(pm.verify(self.repo, self.regp, self.cfg))

    def test_verify_red_on_malformed_registry(self):
        self.regp.write_text("nope", encoding="utf-8")
        self.assertTrue(pm.verify(self.repo, self.regp, self.cfg))


class ShippedRegistry(unittest.TestCase):
    def test_every_shipped_entry_passes_check(self):
        """CI hook: a bad registry entry makes the gate red, so MTS-AutoDeploy refuses to deploy it."""
        self.assertEqual(pm.verify(), [])


if __name__ == "__main__":
    unittest.main()
