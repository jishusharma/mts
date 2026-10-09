"""CLI for the orphan sweep (testnet only, read-only towards the exchange). Exit 0 ok, 1 read errors, 3 orphan HALT written.
--once (default): one sweep, an orphan writes HALT at once (manual use, unchanged).
--interval N --confirm-sweeps K [--max-sweeps M]: repeated sweeps (daily task MTS-Orphan-Watchdog via
launch-orphan-sweep.vbs runs M = K, then exits; M = 0 loops forever). An account is HALTed only
when it is an orphan in K consecutive sweeps (a read error neither counts nor resets), so the gap between an entry
fill and its position_manager's first heartbeat cannot trip it. Each orphan episode is written to HALT once; the loop
keeps running after a HALT. Exit code of a repeated run: 3 if any sweep wrote HALT, else the last sweep's code. Accounts whose testnet secret file is missing are skipped (no client to read)."""
import sys
sys.dont_write_bytecode = True

from pathlib import Path
import argparse
import json
import os
import re
import time
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import orphan_watchdog
import pm_heartbeat

LABEL_RE = re.compile(r"[a-z0-9_]{1,32}")
DEFAULT_CONFIG_PATH = HERE / "auto_trader_config.json"
SECRETS_DIR = HERE / ".secrets"
HALT_PATH = HERE / "HALT"
LOG_PATH = HERE / "orphan_watchdog.jsonl"


def account_labels(config_path=None, secrets_dir=None) -> list:
    """default + the labels in auto_trader_config.json "accounts". An unreadable config falls back to every label that has
    a testnet secret file (B148: the old fixed ['fabio'] left every jishu_N account unswept)."""
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH
    try:
        with open(config_path, encoding="utf-8") as f:
            data = json.load(f)
        labels = [v for v in data.get("accounts", {}).values() if isinstance(v, str) and LABEL_RE.fullmatch(v)]
    except (OSError, KeyError, AttributeError, json.JSONDecodeError):
        sd = Path(secrets_dir) if secrets_dir is not None else SECRETS_DIR
        labels = [m.group(1) for f in sd.glob("testnet_*.secret.json")
                  if (m := re.fullmatch(r"testnet_([a-z0-9_]{1,32})\.secret\.json", f.name))] if sd.is_dir() else []
    return ["default"] + sorted(set(labels))


def has_secret(label) -> bool:
    """Existence check only (never read). The main account ("default") is always swept."""
    return label == "default" or (SECRETS_DIR / f"testnet_{label}.secret.json").exists()


def real_get_client(label):
    old_mts_account = os.environ.get("MTS_ACCOUNT")
    if label == "default":
        os.environ.pop("MTS_ACCOUNT", None)
    else:
        os.environ["MTS_ACCOUNT"] = label
    try:
        import deribit_orders
        token = deribit_orders.authenticate()
        return (deribit_orders, token)
    finally:
        if old_mts_account is None:
            os.environ.pop("MTS_ACCOUNT", None)
        else:
            os.environ["MTS_ACCOUNT"] = old_mts_account


def main(argv=None, get_client=None, hb_dir=None, halt_path=None, log_path=None, alive=None, config_path=None,
         secret_check=None, sleep=time.sleep) -> int:
    if argv is None:
        argv = sys.argv[1:]
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", default=True)
    parser.add_argument("--interval", type=float, default=0.0)
    parser.add_argument("--currency", default="BTC")
    parser.add_argument("--confirm-sweeps", type=int, default=1,
                        help="consecutive orphan sweeps before HALT (daily task uses 7)")
    parser.add_argument("--max-sweeps", type=int, default=0, help="stop after this many sweeps (0 = no limit)")
    parser.add_argument("--hb-max-age", type=float, default=pm_heartbeat.DEFAULT_MAX_AGE_S,
                        help="seconds without a heartbeat refresh before a manager counts as dead (B148, D10)")
    
    # testnet only: --mainnet is not defined, so argparse rejects it (exit 2)
    args = parser.parse_args(argv)

    if get_client is None:
        get_client = real_get_client
        secret_check = secret_check or has_secret
    confirm = max(1, args.confirm_sweeps)
    streak, reported = {}, set()
    if halt_path is None:
        halt_path = HALT_PATH
    if log_path is None:
        log_path = LOG_PATH
    if hb_dir is None:
        hb_dir = pm_heartbeat.DEFAULT_HB_DIR  # same dir position_manager writes to
    
    def run_once():
        labels = account_labels(config_path)
        if secret_check is not None:
            labels = [lab for lab in labels if secret_check(lab)]
        live = pm_heartbeat.live_accounts(hb_dir, alive=alive, max_age_s=args.hb_max_age)
        res = orphan_watchdog.run_once(get_client, labels, live, None, log_path=log_path, currency=args.currency)
        seen = {o["account"] for o in res["orphans"]}
        for lab in labels:
            if lab in seen:
                streak[lab] = streak.get(lab, 0) + 1
            elif lab not in res["errors"]:
                streak[lab] = 0
                reported.discard(lab)
        confirmed = [o for o in res["orphans"] if streak[o["account"]] >= confirm]
        new = [o for o in confirmed if o["account"] not in reported]
        if new:
            now = datetime.now(timezone.utc)
            orphan_watchdog.write_orphan_halt(halt_path, new, now)
            # B148: run_once(halt_path=None) only logs orphan_seen, so a confirmed halt left no trace in the log
            # that `mts status` reads. Record it.
            Path(log_path).parent.mkdir(parents=True, exist_ok=True)
            with open(log_path, "a", encoding="utf-8", newline=chr(10)) as lf:
                lf.write(json.dumps({"ts": now.isoformat(), "event": "orphan_halt", "orphans": new, "errors": {},
                                     "live": sorted(live)}) + chr(10))
            reported.update(o["account"] for o in new)
        if res["orphans"]:
            print(f"Orphan accounts found: {', '.join(o['account'] for o in res['orphans'])}"
                  f" (HALT: {', '.join(o['account'] for o in confirmed) or 'not yet, unconfirmed'})")
        if res["errors"]:
            print(f"Errors occurred: {len(res['errors'])}")
        return 3 if confirmed else 1 if res["errors"] else 0
    
    code = run_once()
    halted, n = code == 3, 1
    
    if args.interval > 0:
        try:
            while args.max_sweeps <= 0 or n < args.max_sweeps:     # keeps sweeping after a HALT
                sleep(args.interval)
                code = run_once()
                halted, n = halted or code == 3, n + 1
        except KeyboardInterrupt:
            pass
    
    return 3 if halted else code


if __name__ == "__main__":
    sys.exit(main())
