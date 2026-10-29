"""Wave 1 item 2: check mainnet_pnl.realized_btc against the Deribit equity identity on a RECORDED testnet log.

Independent of the code: Deribit's account summary obeys equity = balance + session_rpl + session_upl (checked on the
recorded summary below), and every balance move is a transaction-log `change`. So P/L over a window that starts right
after an 08:00 UTC settlement (session_rpl and session_upl reset to 0 there, flat position) is
    sum(change of entries in window) + session_rpl_now + session_upl_now.
Assumption (labelled): the 2026-10-10 08:00 settlement ran and reset session_rpl; the capture holds no settlement entry
for it although a position was open 07:15-09:15. Run: python item2_settlement_identity.py
"""
import json, os, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "execution"))
import mainnet_pnl  # noqa: E402

cap = json.load(open(os.path.join(HERE, "..", "loose_code", "txlog_capture_2026-10-10_jishu_11.json")))
s = cap["account_summary"]
print("identity check: balance + session_rpl + session_upl =", round(s["balance"] + s["session_rpl"] + s["session_upl"], 8),
      "vs equity", s["equity"])
win = [e for e in cap["entries"] if e["ts_utc"] >= "2026-10-10T08:00:00Z"]
expected = sum(e["change"] for e in win) + s["session_rpl"] + s["session_upl"]
code = mainnet_pnl.daily_pnl_btc(win, s)
print(f"window entries={len(win)} expected(identity)={expected:.2e} BTC code={code:.2e} BTC diff={code - expected:.2e} BTC")
