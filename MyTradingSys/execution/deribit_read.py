import sys
sys.dont_write_bytecode = True
"""
MyTradingSys/execution/deribit_read.py  (T050 phase 2)

Authenticated, READ-ONLY, TESTNET-ONLY. Places nothing, cancels nothing.
BASE is a hard-coded testnet constant; pointing this at mainnet requires
editing the file. (A runtime check on a constant was removed 2026-09-26
after review - it could never fail, so it gave false assurance.)
Known nit: public/auth sends client_secret as a GET query parameter over
TLS; the script never logs the URL.
Refuses to continue if the key's granted scope includes wallet:read_write
(withdraw-capable) - trade keys for MTS must not be able to move funds.

Needs MyTradingSys/execution/.secrets/testnet.secret.json (gitignored):
  {"client_id": "...", "client_secret": "...", "env": "test"}
The operator creates that file. No AI session reads it.

Never prints the secret or the access token.
Syntax-checked only on 2026-09-26; first real run is the operator's.

Run: python MyTradingSys/execution/deribit_read.py [--currency BTC|USDC] [--account <label>]
"""
import json, argparse, urllib.request, urllib.error, urllib.parse, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SECRET = ROOT / "MyTradingSys" / "execution" / ".secrets" / "testnet.secret.json"
BASE = "https://test.deribit.com/api/v2"  # testnet only in phase 2 - do not parameterise
INSTRUMENT = {"BTC": "BTC-PERPETUAL", "USDC": "BTC_USDC-PERPETUAL"}
ACCOUNT_RE = re.compile(r"[a-z0-9_]{1,32}")


def call(method, params, token=None):
    url = "%s/%s?%s" % (BASE, method, urllib.parse.urlencode(params))
    headers = {"User-Agent": "MTS-T050-phase2/1.0"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            body = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode("utf-8"))
        except Exception:
            raise RuntimeError("%s: HTTP %s" % (method, e.code))
    if "error" in body:
        raise RuntimeError("%s: %s" % (method, body["error"]))
    return body["result"]


def resolve_secret(account=None) -> Path:
    if account is None or account == "":
        return SECRET
    if not ACCOUNT_RE.fullmatch(account):
        raise ValueError("bad account label %r" % account)
    return SECRET.parent / ("testnet_%s.secret.json" % account)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--currency", choices=["BTC", "USDC"], default="BTC")
    ap.add_argument("--account", default=None, help="named TESTNET sub-account label (.secrets/testnet_<label>.secret.json)")
    a = ap.parse_args(argv)
    try:
        path = resolve_secret(a.account)
    except ValueError as e:
        print("REFUSED: %s" % e)
        return 2
    if not path.exists():
        print("MISSING: %s - create it first (see MyTradingSys/execution/README.md)" % path); return 2
    cfg = json.load(open(path, encoding="utf-8"))
    if cfg.get("env") != "test":
        print('REFUSED: secret file env must be "test"'); return 2

    auth = call("public/auth", {"grant_type": "client_credentials",
                                "client_id": cfg["client_id"], "client_secret": cfg["client_secret"]})
    token, scope = auth["access_token"], auth.get("scope", "")
    print("AUTH OK. granted scope:", scope)
    if "wallet:read_write" in scope:
        print("REFUSED: key can withdraw (wallet:read_write). Recreate it with wallet none/read."); return 3

    cur = a.currency
    s = call("private/get_account_summary", {"currency": cur}, token)
    print("ACCOUNT %s: equity=%s balance=%s available_funds=%s margin_balance=%s initial_margin=%s maintenance_margin=%s" % (
        cur, s.get("equity"), s.get("balance"), s.get("available_funds"), s.get("margin_balance"),
        s.get("initial_margin"), s.get("maintenance_margin")))
    pos = call("private/get_positions", {"currency": cur, "kind": "future"}, token)
    print("POSITIONS:", len(pos))
    for p in pos:
        print("  %s size=%s dir=%s avg=%s mark=%s upnl=%s" % (p.get("instrument_name"), p.get("size"), p.get("direction"),
              p.get("average_price"), p.get("mark_price"), p.get("floating_profit_loss")))
    oo = call("private/get_open_orders_by_instrument", {"instrument_name": INSTRUMENT[cur]}, token)
    print("OPEN ORDERS on %s: %d" % (INSTRUMENT[cur], len(oo)))
    for o in oo:
        print("  %s %s %s amount=%s price=%s trigger=%s label=%s" % (o.get("order_id"), o.get("direction"), o.get("order_type"),
              o.get("amount"), o.get("price"), o.get("trigger_price"), o.get("label")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
