"""CLI for the orphan sweep (testnet only, read-only, NOT scheduled). Exit 0 ok, 1 read errors, 3 orphan HALT written."""
import sys
sys.dont_write_bytecode = True

from pathlib import Path
import argparse
import json
import os
import re
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import orphan_watchdog
import pm_heartbeat

LABEL_RE = re.compile(r"[a-z0-9_]{1,32}")
DEFAULT_CONFIG_PATH = HERE / "auto_trader_config.json"
HALT_PATH = HERE / "HALT"
LOG_PATH = HERE / "orphan_watchdog.jsonl"


def account_labels(config_path=None) -> list:
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH
    try:
        with open(config_path, encoding="utf-8") as f:
            data = json.load(f)
        labels = [v for v in data.get("accounts", {}).values() if LABEL_RE.fullmatch(v)]
    except (OSError, KeyError, json.JSONDecodeError):
        labels = ["fabio"]
    return ["default"] + sorted(set(labels))


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


def main(argv=None, get_client=None, hb_dir=None, halt_path=None, log_path=None, alive=None, config_path=None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", default=True)
    parser.add_argument("--interval", type=float, default=0.0)
    parser.add_argument("--currency", default="BTC")
    
    # testnet only: --mainnet is not defined, so argparse rejects it (exit 2)
    args = parser.parse_args(argv)

    if get_client is None:
        get_client = real_get_client
    if halt_path is None:
        halt_path = HALT_PATH
    if log_path is None:
        log_path = LOG_PATH
    if hb_dir is None:
        hb_dir = HERE / "heartbeat"
    
    def run_once():
        labels = account_labels(config_path)
        live = pm_heartbeat.live_accounts(hb_dir, alive=alive)
        res = orphan_watchdog.run_once(get_client, labels, live, halt_path, log_path=log_path, currency=args.currency)
        if res["orphans"]:
            print(f"Orphan accounts found: {', '.join(o['account'] for o in res['orphans'])}")
        if res["errors"]:
            print(f"Errors occurred: {len(res['errors'])}")
        return 3 if res["orphans"] else 1 if res["errors"] else 0
    
    code = run_once()
    
    if args.interval > 0:
        try:
            while True:
                time.sleep(args.interval)
                code = run_once()
                if code == 3:
                    break
        except KeyboardInterrupt:
            pass
    
    return code


if __name__ == "__main__":
    sys.exit(main())
