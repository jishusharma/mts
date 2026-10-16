"""Promotion gate: research -> pre-registered screen -> backtest gate -> testnet shadow -> testnet trading.

  python -m MyTradingSys.backtest.layers.promotion.promote check <manifest.json> [--json]
  python -m MyTradingSys.backtest.layers.promotion.promote register <manifest.json> --mode shadow|testnet
  python -m MyTradingSys.backtest.layers.promotion.promote demote <setup_id> [--to shadow]
  python -m MyTradingSys.backtest.layers.promotion.promote verify          (every registry entry re-checked; CI uses it)

Every gate fails closed: a missing or unreadable field is a REJECT with the reason. This tool never runs a backtest and
never reads VALIDATION or HOLDOUT data; it only reads the records a research session wrote down. Spec: system/PROMOTION_PIPELINE.md.

Manifest (JSON), all keys required:
  setup_id            trade-source prefix, e.g. "layer:fabio:volume_fvg:"
  layer               layer name, e.g. "fabio"
  pre_reg             {"path": repo-relative PRE_REG file, "git_sha": commit that holds it}
  screen_verdict      {"path": repo-relative file; JSON {"verdict": "PASS"} or a line "VERDICT: PASS"}
  backtest            {"report_path": repo-relative report that carries the BT-TUNED label, "label": "BT-TUNED"}
  oos                 {"fee_net": true, "net_r": x, "ci_low": a, "ci_high": b, "n_trades": n, "trades_csv": repo-relative csv, column net_r}
                      (fee-net, out of sample; net_r/CI/n are recomputed from trades_csv, seed 20261016, 2000 draws, tolerance 0.01 R / 5% n)
  trial_ledger        {"path": CSV with a "study" column, "entry_id": study id, "variants": N}
  validation_reads    [exactly one {"at": ISO date, "ref": where it was read}]
  holdout_reads       [exactly one {"at": ISO date, "ref": ...}]
  requested_mode      "shadow" or "testnet"
"""
import argparse
import csv
import datetime as dt
import json
import math
import random
import re
import subprocess
import sys
from pathlib import Path
from statistics import NormalDist

from MyTradingSys.backtest.layers.promotion import registry as reg

REPO = Path(__file__).resolve().parents[4]
CONFIG_PATH = REPO / "MyTradingSys" / "execution" / "auto_trader_config.json"
MIN_TRADES = 30        # OURS: sanity floor on the OOS sample (GO_LIVE_BAR needs 200 testnet trades later); not from a trader
SIZE_CEILING_USD = 10000   # = auto_trader.SIZE_CEILING_USD (test_promote asserts they match)
POWER_Z = 0.84         # OURS: z for 80% power in the MDE trade floor
MDE_SAFETY = 4         # OURS: safety factor on the MDE-based trade floor
BOOT_SEED = 20261016   # OURS: bootstrap seed for the OOS recompute
BOOT_DRAWS = 2000      # OURS
TOL_R = 0.01           # OURS: max |manifest - recompute| for net_r and both CI ends, in R
TOL_N = 0.05           # OURS: max relative |n_trades - rows in trades_csv|
LABEL = "BT-TUNED"
REQUIRED = ("setup_id", "layer", "pre_reg", "screen_verdict", "backtest", "oos", "trial_ledger",
            "validation_reads", "holdout_reads", "requested_mode")


def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and x == x and abs(x) != float("inf")


def holm_z(variants):
    """OURS: two-sided 5% Holm/Bonferroni critical z for `variants` trials in the ledger (z=1.96 for 1)."""
    return NormalDist().inv_cdf(1 - 0.025 / max(1, int(variants)))


def mde_floor(o, z):
    """OURS: n >= max(MIN_TRADES, 4*((z+0.84)*sd/net_r)^2), sd = se*sqrt(n), se = (ci_high-ci_low)/3.92."""
    se = (o["ci_high"] - o["ci_low"]) / 3.92
    sd = se * math.sqrt(max(o["n_trades"], 0))
    return max(MIN_TRADES, MDE_SAFETY * ((z + POWER_Z) * sd / o["net_r"]) ** 2)


def recompute_oos(path):
    """(n, mean, ci_low, ci_high) from a trades csv with a net_r column: percentile bootstrap (95%) of the mean, seeded.
    Raises ValueError on an empty file, a missing column or a non-finite value (callers REJECT)."""
    with open(path, newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        if not rd.fieldnames or "net_r" not in rd.fieldnames:
            raise ValueError("no net_r column")
        xs = []
        for row in rd:
            x = float(row["net_r"])
            if not _num(x):
                raise ValueError("non-finite net_r")
            xs.append(x)
    if not xs:
        raise ValueError("no trades")
    n = len(xs)
    rng = random.Random(BOOT_SEED)
    means = sorted(sum(rng.choices(xs, k=n)) / n for _ in range(BOOT_DRAWS))
    return n, sum(xs) / n, means[int(0.025 * BOOT_DRAWS)], means[int(0.975 * BOOT_DRAWS) - 1]


def _git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    return r.returncode, r.stdout.strip()


def _first_commit_date(repo, rel):
    """Author-independent committer date (UTC) of the commit that first added `rel`, or None if untracked."""
    rc, out = _git(repo, "log", "--diff-filter=A", "--format=%cI", "--follow", "--", rel)
    if rc != 0 or not out:
        return None
    return min(dt.datetime.fromisoformat(x).astimezone(dt.timezone.utc) for x in out.splitlines())


def _sha_date(repo, sha):
    rc, out = _git(repo, "show", "-s", "--format=%cI", sha + "^{commit}")
    return dt.datetime.fromisoformat(out).astimezone(dt.timezone.utc) if rc == 0 and out else None


def _is_str(x):
    return isinstance(x, str) and x.strip() != ""


def _rel_file(repo, rel):
    """Existing file inside the repo for a repo-relative path, else None (no escaping the repo)."""
    if not _is_str(rel):
        return None
    p = (Path(repo) / rel).resolve()
    try:
        p.relative_to(Path(repo).resolve())
    except ValueError:
        return None
    return p if p.is_file() else None


def _blocked(setup_id, layer, cfg_path):
    """Reasons the setup/layer sits on the trade blocklist or its parked list (either direction of prefix)."""
    try:
        cfg = json.loads(Path(cfg_path).read_text(encoding="utf-8"))
        lists = {"trade_blocklist": cfg.get("trade_blocklist", []), "trade_blocklist_parked": cfg.get("trade_blocklist_parked", {})}
    except (OSError, ValueError, AttributeError) as e:
        return ["auto_trader_config unreadable (%r): cannot prove the layer is not blocked" % (e,)]
    bad = []
    for name, lst in lists.items():
        if not isinstance(lst, (list, dict)):
            return ["%s malformed: cannot prove the layer is not blocked" % name]
        for prefix in lst:
            if not isinstance(prefix, str) or not prefix:
                return ["%s malformed entry: cannot prove the layer is not blocked" % name]
            if setup_id.startswith(prefix) or prefix.startswith(setup_id):
                bad.append("%s lists %s" % (name, prefix))
    return bad


def check(manifest, repo=REPO, config_path=None, legacy=False):
    """legacy=True (verify() only, for entries already registered) skips the trades_csv recompute when the csv is absent.
    -> {"result": "PASS"|"REJECT", "reasons": [...], "setup_id": ..., "mode": ...}. `manifest` is a dict or a path."""
    repo = Path(repo)
    reasons = []
    m = manifest
    if not isinstance(m, dict):
        try:
            m = json.loads(Path(manifest).read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError) as e:
            return {"result": "REJECT", "reasons": ["manifest unreadable: %r" % (e,)], "setup_id": None, "mode": None}
    if not isinstance(m, dict):
        return {"result": "REJECT", "reasons": ["manifest is not an object"], "setup_id": None, "mode": None}
    missing = [k for k in REQUIRED if k not in m or m[k] in (None, "", [], {})]
    if missing:
        reasons.append("missing fields: " + ", ".join(missing))
    sid = m.get("setup_id") if _is_str(m.get("setup_id")) else None
    if sid is None and "setup_id" not in missing:
        reasons.append("setup_id not a non-empty string")
    layer = m.get("layer") if _is_str(m.get("layer")) else None
    mode = m.get("requested_mode")
    if "requested_mode" not in missing and mode not in reg.MODES:
        reasons.append("requested_mode %r not in %s" % (mode, reg.MODES))
    if sid and layer and not sid.startswith("layer:%s:" % layer):
        reasons.append("setup_id %s does not start with layer:%s:" % (sid, layer))

    def sub(key):
        v = m.get(key)
        return v if isinstance(v, dict) else None

    # G1 + G2: PRE_REG exists, predates the screen verdict, and the screen verdict is PASS
    pre, scr = sub("pre_reg"), sub("screen_verdict")
    if "pre_reg" not in missing and "screen_verdict" not in missing:
        pre_date = scr_date = None
        if not pre or not _rel_file(repo, pre.get("path")):
            reasons.append("PRE_REG file missing or unreadable")
        elif not _is_str(pre.get("git_sha")):
            reasons.append("pre_reg.git_sha missing")
        else:
            rc, _ = _git(repo, "cat-file", "-e", "%s:%s" % (pre["git_sha"], pre["path"]))
            pre_date = _sha_date(repo, pre["git_sha"])
            if rc != 0 or pre_date is None:
                reasons.append("pre_reg.git_sha does not hold the PRE_REG file")
                pre_date = None
            else:
                rc1, b1 = _git(repo, "rev-parse", "%s:%s" % (pre["git_sha"], pre["path"]))
                rc2, b2 = _git(repo, "rev-parse", "HEAD:%s" % pre["path"])
                if rc1 != 0 or rc2 != 0 or not b1 or b1 != b2:
                    reasons.append("PRE_REG edited after registration (blob at git_sha differs from HEAD, or HEAD lacks it)")
        sfile = _rel_file(repo, scr.get("path")) if scr else None
        if not sfile:
            reasons.append("screen verdict file missing or unreadable")
        else:
            txt = sfile.read_text(encoding="utf-8", errors="replace")
            verdict = None
            try:
                j = json.loads(txt)
                verdict = j.get("verdict") if isinstance(j, dict) else None
            except ValueError:
                mm = re.search(r"^\s*VERDICT:\s*([A-Za-z_]+)\s*$", txt, re.M)
                verdict = mm.group(1) if mm else None
            if verdict != "PASS":
                reasons.append("screen verdict is %r, need PASS" % (verdict,))
            scr_date = _first_commit_date(repo, scr["path"])
            if scr_date is None:
                reasons.append("screen verdict file is not committed (no date to compare with PRE_REG)")
        if pre_date and scr_date and not pre_date < scr_date:
            reasons.append("PRE_REG (%s) does not predate the screen verdict (%s)" % (pre_date.isoformat(), scr_date.isoformat()))

    # G3: backtest report carries the BT-TUNED label
    bt = sub("backtest")
    if "backtest" not in missing:
        bfile = _rel_file(repo, bt.get("report_path")) if bt else None
        if not bfile:
            reasons.append("backtest report missing or unreadable")
        elif bt.get("label") != LABEL or LABEL not in bfile.read_text(encoding="utf-8", errors="replace"):
            reasons.append("backtest report lacks the %s label" % LABEL)

    # G4: fee-net OOS net R > 0 and CI low > 0 (GO_LIVE_BAR line 1)
    o = sub("oos")
    if "oos" not in missing:
        if not o or o.get("fee_net") is not True:
            reasons.append("oos.fee_net is not true (results must be net of fees)")
        elif not all(_num(o.get(k)) for k in ("net_r", "ci_low", "ci_high", "n_trades")):
            reasons.append("oos needs numeric net_r, ci_low, ci_high, n_trades")
        else:
            tc = o.get("trades_csv")
            if tc is None and legacy:
                pass
            else:
                cfile = _rel_file(repo, tc)
                if not cfile:
                    reasons.append("oos.trades_csv missing or unreadable (the OOS number is recomputed from it)")
                else:
                    try:
                        n2, mean2, lo2, hi2 = recompute_oos(cfile)
                    except (OSError, ValueError, csv.Error) as e:
                        reasons.append("oos.trades_csv unusable: %r" % (e,))
                    else:
                        if abs(o["net_r"] - mean2) > TOL_R or abs(o["ci_low"] - lo2) > TOL_R or abs(o["ci_high"] - hi2) > TOL_R:
                            reasons.append("manifest oos differs from the recompute by more than %.2f R: manifest net_r %s CI [%s, %s], "
                                           "trades_csv net_r %.4f CI [%.4f, %.4f]" % (TOL_R, o["net_r"], o["ci_low"], o["ci_high"], mean2, lo2, hi2))
                        if abs(o["n_trades"] - n2) > TOL_N * n2:
                            reasons.append("manifest oos n_trades %s differs from the recompute (%d rows) by more than %d%%" % (o["n_trades"], n2, round(TOL_N * 100)))
            if not o["net_r"] > 0:
                reasons.append("fee-net OOS net R %s is not above 0" % o["net_r"])
            if not o["ci_low"] > 0:
                reasons.append("95%% CI low %s is not above 0" % o["ci_low"])
            if not o["ci_low"] <= o["net_r"] <= o["ci_high"]:
                reasons.append("net_r outside its own CI (ci_low <= net_r <= ci_high)")
            elif o["net_r"] > 0:
                tlv = sub("trial_ledger")
                var = tlv.get("variants") if tlv else None
                if isinstance(var, int) and not isinstance(var, bool) and var >= 1:
                    z = holm_z(var)
                    se = (o["ci_high"] - o["ci_low"]) / 3.92
                    if o["net_r"] - z * se <= 0:
                        reasons.append("Holm-adjusted CI low %.4f (z=%.3f for %d variants) is not above 0" % (o["net_r"] - z * se, z, var))
                    floor = mde_floor(o, z)
                    if o["n_trades"] < floor:
                        reasons.append("n_trades %s below the MDE-based floor of %d (z=%.3f)" % (o["n_trades"], math.ceil(floor), z))
            if int(o["n_trades"]) != o["n_trades"] or o["n_trades"] < MIN_TRADES:
                reasons.append("n_trades %s below the floor of %d" % (o["n_trades"], MIN_TRADES))

    # G5: trial ledger entry exists and its variant count matches the manifest
    tl = sub("trial_ledger")
    if "trial_ledger" not in missing:
        lfile = _rel_file(repo, tl.get("path")) if tl else None
        if not lfile or not _is_str(tl.get("entry_id")) or not isinstance(tl.get("variants"), int) or isinstance(tl.get("variants"), bool) or tl["variants"] < 1:
            reasons.append("trial ledger path, entry_id or variants (int >= 1) missing/unreadable")
        else:
            try:
                with open(lfile, newline="", encoding="utf-8") as f:
                    rows = [r for r in csv.DictReader(f) if (r.get("study") or "").strip() == tl["entry_id"]]
            except (OSError, ValueError, csv.Error) as e:
                rows = None
                reasons.append("trial ledger unreadable: %r" % (e,))
            if rows is not None:
                if not rows:
                    reasons.append("trial ledger has no rows for study %s" % tl["entry_id"])
                elif len(rows) != tl["variants"]:
                    reasons.append("trial ledger lists %d variants for %s, manifest says %d" % (len(rows), tl["entry_id"], tl["variants"]))

    # G6: VALIDATION and holdout each read exactly once
    for key in ("validation_reads", "holdout_reads"):
        if key in missing:
            continue
        recs = m.get(key)
        if not isinstance(recs, list) or len(recs) != 1:
            reasons.append("%s must hold exactly one read record (found %s)" % (key, len(recs) if isinstance(recs, list) else "non-list"))
        elif not (isinstance(recs[0], dict) and _is_str(recs[0].get("at")) and _is_str(recs[0].get("ref"))):
            reasons.append("%s record needs non-empty at and ref" % key)
        elif key == "validation_reads" and not _rel_file(repo, recs[0]["ref"]):
            reasons.append("validation_reads ref %r is not an existing repo file (the logged VALIDATION read)" % recs[0]["ref"])

    # G7: layer not on the trade blocklist or parked list
    if sid:
        reasons += _blocked(sid, layer or "", config_path or CONFIG_PATH)

    return {"result": "REJECT" if reasons else "PASS", "reasons": reasons, "setup_id": sid, "mode": mode if mode in reg.MODES else None}


def _write_registry(path, entries):
    Path(path).write_text(json.dumps({"version": 1, "entries": entries}, indent=1) + "\n", encoding="utf-8", newline="\n")


def has_testnet_flag(setup_id, config_path=None):
    """A sized testnet-trading flag exists: a size_overrides prefix (longer than the bare 'layer:') that covers setup_id."""
    try:
        cfg = json.loads(Path(config_path or CONFIG_PATH).read_text(encoding="utf-8"))
        table = cfg.get("size_overrides", {})
        for k, v in table.items():
            if isinstance(k, str) and len(k) > len("layer:") and setup_id.startswith(k):
                try:
                    reg.size_entry(v, SIZE_CEILING_USD)      # same validation as auto_trader.size_override (L7)
                    return True
                except ValueError:
                    pass
    except (OSError, ValueError, AttributeError):
        pass
    return False


def register(manifest_path, mode, repo=REPO, registry_path=None, config_path=None, now=None):
    """Write a registry entry only if check() is PASS. -> (ok, message, result)."""
    res = check(manifest_path, repo=repo, config_path=config_path)
    if res["result"] != "PASS":
        return False, "REJECT: " + "; ".join(res["reasons"]), res
    if mode not in reg.MODES:
        return False, "mode must be shadow or testnet", res
    if res["mode"] != mode:
        return False, "manifest requested_mode %s differs from --mode %s" % (res["mode"], mode), res
    rp = Path(registry_path or reg.DEFAULT_PATH)
    entries, err = reg.load_registry(rp)
    if err:
        return False, "registry unreadable, refusing to write: " + err, res
    sid = res["setup_id"]
    existing = next((e for e in entries if e["setup_id"] == sid), None)
    if mode == "shadow":
        if existing:
            return False, "%s already registered as %s" % (sid, existing["mode"]), res
    else:
        if not existing or existing["mode"] != "shadow":
            return False, "testnet needs an existing shadow entry for %s" % sid, res
        if not has_testnet_flag(sid, config_path):
            return False, "no sized testnet-trading flag (size_overrides) covers %s: stays shadow (default)" % sid, res
    rc, sha = _git(repo, "rev-parse", "HEAD")
    entry = {"setup_id": sid, "mode": mode, "manifest": str(Path(manifest_path).as_posix()),
             "promoted_at": (now or dt.datetime.now(dt.timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ"),
             "commit": sha if rc == 0 and sha else "unknown"}
    entries = [e for e in entries if e["setup_id"] != sid] + [entry]
    _write_registry(rp, entries)
    return True, "registered %s as %s" % (sid, mode), res


def _block_setup(setup_id, config_path, now):
    """Add setup_id to the trade_blocklist that auto_trader ENFORCES (trade_block_reason; trade_blocklist_parked is only
    documentation) with a reason. -> (ok, message). Refuses, writing nothing, when the config cannot be read or is malformed."""
    cp = Path(config_path)
    try:
        raw = cp.read_text(encoding="utf-8")
        cfg = json.loads(raw)
    except (OSError, ValueError) as e:
        return False, "auto_trader_config unreadable (%r): refusing to demote off (cannot block the setup)" % (e,)
    if not isinstance(cfg, dict):
        return False, "auto_trader_config is not an object: refusing to demote off"
    bl, reasons = cfg.get("trade_blocklist", []), cfg.get("trade_blocklist_reasons", {})
    if not isinstance(bl, list) or not isinstance(reasons, dict) or not all(isinstance(p, str) and p for p in bl):
        return False, "trade_blocklist / trade_blocklist_reasons malformed: refusing to demote off"
    if setup_id not in bl:
        bl.append(setup_id)
    reasons[setup_id] = "demoted off %s (promote.py demote --to off)" % (now or dt.datetime.now(dt.timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
    cfg["trade_blocklist"], cfg["trade_blocklist_reasons"] = bl, reasons
    indent = 1 if raw.startswith('{\n "') else 2
    try:
        cp.write_text(json.dumps(cfg, indent=indent, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    except OSError as e:
        return False, "auto_trader_config not writable (%r): refusing to demote off" % (e,)
    return True, "blocked"


def _blocked_exact(setup_id, config_path):
    try:
        bl = json.loads(Path(config_path).read_text(encoding="utf-8")).get("trade_blocklist", [])
        return [p for p in bl if p == setup_id] if isinstance(bl, list) else []
    except (OSError, ValueError, AttributeError):
        return []


def _cover(a, b):
    return a.startswith(b) or b.startswith(a)


def demote(setup_id, to="shadow", registry_path=None, config_path=None, now=None):
    """testnet -> shadow (default), or --to off. 'off' is never a return to trading: the entry is removed AND setup_id is
    written to auto_trader_config trade_blocklist (the list auto_trader enforces) with a reason, so a grandfathered or
    sized source stays blocked. A setup with no registry entry can also be blocked with --to off (grandfathered source)."""
    if to not in ("shadow", "off"):
        return False, "--to must be shadow or off"
    rp = Path(registry_path or reg.DEFAULT_PATH)
    entries, err = reg.load_registry(rp)
    if err:
        return False, "registry unreadable: " + err
    hit = next((e for e in entries if e["setup_id"] == setup_id), None)
    cp = config_path or CONFIG_PATH
    if not hit:
        if to == "off" and not _blocked_exact(setup_id, cp):
            ok, msg = _block_setup(setup_id, cp, now)
            return (True, "%s not in registry; -> off (blocked)" % setup_id) if ok else (False, msg)
        return False, "%s not in registry" % setup_id
    rest = [e for e in entries if e["setup_id"] != setup_id]
    if to == "shadow":
        rest.append(dict(hit, mode="shadow"))
    else:
        ok, msg = _block_setup(setup_id, cp, now)       # block first: a failed config write leaves the registry untouched
        if not ok:
            return False, msg
    _write_registry(rp, rest)
    return True, "%s -> %s" % (setup_id, to)


def verify(repo=REPO, registry_path=None, config_path=None):
    """Re-check every registry entry. -> list of problem strings (empty = green). A malformed registry is a problem."""
    entries, err = reg.load_registry(registry_path)
    if err:
        return [err]
    problems = []
    for e in entries:
        r = check(Path(repo) / e["manifest"], repo=repo, config_path=config_path, legacy=True)    # legacy: entries without trades_csv stay green
        if r["result"] != "PASS":
            problems.append("%s: %s" % (e["setup_id"], "; ".join(r["reasons"])))
        elif r["setup_id"] != e["setup_id"]:
            problems.append("%s: manifest setup_id is %s" % (e["setup_id"], r["setup_id"]))
        elif e["mode"] == "testnet" and not has_testnet_flag(e["setup_id"], config_path):
            problems.append("%s: mode testnet but no sized testnet flag" % e["setup_id"])
    # H2: every sized prefix needs a registry entry, a grandfather entry or a block entry (else a hand edit left a sized,
    # rule-mapped setup that default-deny cannot account for)
    try:
        cfg = json.loads(Path(config_path or CONFIG_PATH).read_text(encoding="utf-8"))
        table = cfg.get("size_overrides", {})
        gf = cfg.get("pre_pipeline_sources", {})
        bl = cfg.get("trade_blocklist", [])
        if not isinstance(table, dict) or not isinstance(gf, dict) or not isinstance(bl, list):
            raise ValueError("size_overrides/pre_pipeline_sources/trade_blocklist malformed")
    except (OSError, ValueError, AttributeError) as e:
        problems.append("auto_trader_config unreadable or malformed (%r): cannot check sized prefixes" % (e,))
        return problems
    known = [e["setup_id"] for e in entries] + [g for g in gf if isinstance(g, str)] + [b for b in bl if isinstance(b, str)]
    for k in table:
        if isinstance(k, str) and len(k) > len("layer:") and not any(_cover(k, x) for x in known):
            problems.append("size_overrides %s has no registry entry, no pre_pipeline_sources entry and no trade_blocklist entry" % k)
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser(prog="promote")
    sp = ap.add_subparsers(dest="cmd", required=True)
    c = sp.add_parser("check"); c.add_argument("manifest"); c.add_argument("--json", action="store_true")
    r = sp.add_parser("register"); r.add_argument("manifest"); r.add_argument("--mode", required=True, choices=reg.MODES)
    d = sp.add_parser("demote"); d.add_argument("setup_id"); d.add_argument("--to", default="shadow", choices=("shadow", "off"))
    sp.add_parser("verify")
    a = ap.parse_args(argv)
    if a.cmd == "check":
        res = check(a.manifest)
        print(json.dumps(res, indent=1) if a.json else "%s %s\n%s" % (res["result"], res["setup_id"], "\n".join("  - " + x for x in res["reasons"])))
        return 0 if res["result"] == "PASS" else 1
    if a.cmd == "register":
        ok, msg, _ = register(a.manifest, a.mode)
        print(msg)
        return 0 if ok else 1
    if a.cmd == "demote":
        ok, msg = demote(a.setup_id, a.to)
        print(msg)
        return 0 if ok else 1
    probs = verify()
    print("\n".join(probs) if probs else "registry OK")
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main())
