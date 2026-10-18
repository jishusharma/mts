"""Executor reject diagnostics (2026-10-14; plan L-mkt-1012-0945 got 10031 invalid_args_for_instrument on its
market entry and the journal kept only str(error), so the cause could not be proven).

Contract under test (diagnostics only - no change to halting, order flow, retries or return values):
  * an entry / stop / target order rejected by the exchange journals an `order_rejected` event that also carries
    error_code, error_detail (the full error dict: code, message, data), method and `request` - a WHITELISTED view of
    what deribit_orders sent (method, instrument_name, amount, type, price, label, reduce_only, post_only,
    trigger_price, trigger). Never the token, never credentials.
  * the halting behaviour around it is exactly the pre-change behaviour (pinned below as characterization tests).
  * a path with no rejection journals nothing new.

The REAL executor.execute_plan, deribit_orders._place_order and deribit_orders._call run against a fake of the
JSON-RPC boundary (do._post) - the same boundary test_deribit_orders_phase3.py fakes. HALT files and the journal are
redirected to tmp_path: this file never touches the real execution/HALT or execution/journal.
Expected request dicts are written from the Deribit private/buy|sell|edit parameter names, not from the code.
"""
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

EXEC = Path(__file__).resolve().parent.parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(EXEC))
import deribit_orders as do  # noqa: E402
import executor  # noqa: E402
import journal  # noqa: E402

TOKEN = "SECRET-TOKEN-DO-NOT-LOG"
INSTRUMENT = "BTC-PERPETUAL"
ERR_10031 = {"code": 10031, "message": "invalid_args_for_instrument",
             "data": {"param": "amount", "reason": "test-chosen detail"}}
ERR_10050 = {"code": 10050, "message": "test_ambiguous"}
OPEN_STATES = ("open", "untriggered")


class FakeDeribit:
    """JSON-RPC fake behind do._post. `fail(method, params)` returns an error dict to reject that call, else None."""

    def __init__(self):
        self.calls = []        # (method, params, token)
        self.pos = 0
        self.orders = {}
        self.n = 0
        self.mark = 80000.0
        self.fail = None
        self.after_stop = None   # called right after a stop_market order is created (to script a later fill)

    def count(self, method):
        return sum(1 for m, _, _ in self.calls if m == method)

    def labels_swept(self):
        return [p["label"] for m, p, _ in self.calls if m == "private/cancel_by_label"]

    def _new_id(self):
        self.n += 1
        return f"O{self.n}"

    def _create(self, direction, params):
        oid = self._new_id()
        typ = params["type"]
        state = "filled" if typ == "market" else ("untriggered" if typ == "stop_market" else "open")
        filled = params["amount"] if typ == "market" else 0
        self.orders[oid] = {"order_id": oid, "direction": direction, "amount": params["amount"], "order_type": typ,
                            "label": params.get("label", ""), "reduce_only": params.get("reduce_only", False),
                            "order_state": state, "filled_amount": filled, "average_price": self.mark,
                            "price": params.get("price"), "trigger_price": params.get("trigger_price")}
        if filled:
            self.pos += filled if direction == "buy" else -filled
        return dict(self.orders[oid])

    def fill(self, oid):
        o = self.orders[oid]
        o["order_state"], o["filled_amount"] = "filled", o["amount"]
        self.pos += o["amount"] if o["direction"] == "buy" else -o["amount"]

    def post(self, method, params, token=None):
        self.calls.append((method, dict(params), token))
        err = self.fail(method, params) if self.fail else None
        if err is not None:
            return {"error": dict(err)}
        if method == "public/ticker":
            return {"result": {"mark_price": self.mark}}
        if method == "private/get_position":
            return {"result": {"size": self.pos}}
        if method == "private/get_open_orders_by_instrument":
            return {"result": [dict(o) for o in self.orders.values() if o["order_state"] in OPEN_STATES]}
        if method in ("private/buy", "private/sell"):
            order = self._create(method.split("/")[1], params)
            if params["type"] == "stop_market" and self.after_stop:
                self.after_stop()
            return {"result": {"order": order, "trades": []}}
        if method == "private/get_order_state":
            return {"result": dict(self.orders[params["order_id"]])}
        if method == "private/edit":
            o = self.orders[params["order_id"]]
            for k in ("amount", "price", "trigger_price"):
                if k in params:
                    o[k] = params[k]
            return {"result": {"order": dict(o), "trades": []}}
        if method == "private/cancel":
            o = self.orders.get(params["order_id"])
            if o is None or o["order_state"] not in OPEN_STATES:
                return {"error": {"code": 11044, "message": "not_open_order"}}
            o["order_state"] = "cancelled"
            return {"result": dict(o)}
        if method == "private/cancel_by_label":
            n = 0
            for o in self.orders.values():
                if o["label"] == params["label"] and o["order_state"] in OPEN_STATES:
                    o["order_state"] = "cancelled"
                    n += 1
            return {"result": n}
        if method == "private/close_position":
            amt = abs(self.pos)
            direction = "sell" if self.pos > 0 else "buy"
            self.pos = 0
            oid = self._new_id()
            order = {"order_id": oid, "direction": direction, "amount": amt, "order_type": "market",
                     "label": "", "reduce_only": True, "order_state": "filled", "filled_amount": amt,
                     "average_price": self.mark}
            self.orders[oid] = order
            return {"result": {"order": dict(order), "trades": []}}
        raise AssertionError(f"fake exchange: unexpected method {method}")


@pytest.fixture
def env(tmp_path, monkeypatch):
    fake = FakeDeribit()
    monkeypatch.setattr(do, "_post", fake.post)
    monkeypatch.setattr(do, "authenticate", lambda *a, **k: TOKEN)   # never reads .secrets
    monkeypatch.setattr(do, "_ACTIVE_ENV", "test")
    monkeypatch.setattr(journal, "JOURNAL_DIR", tmp_path / "journal")
    for attr, fname in (("HALT_PATH", "HALT"), ("HALT_DAILY_LOSS_PATH", "HALT_DAILY_LOSS"),
                        ("HALT_DAILY_LOSS_PATH_MAINNET", "HALT_DAILY_LOSS_MAINNET")):
        monkeypatch.setattr(executor, attr, tmp_path / fname)
    monkeypatch.setattr(executor, "POLL_INTERVAL_SECONDS", 0)
    assert executor.HALT_PATH.parent == tmp_path        # the real execution/HALT is never in play
    return SimpleNamespace(fake=fake, halt=tmp_path / "HALT", jdir=tmp_path / "journal")


def _compiled(plan_id, entries=None, stop_price=79000.0):
    entries = entries or [{"side": "BUY", "amount": 100, "order_type": "market", "price": None, "label": "entry_1"}]
    return {"plan_id": plan_id,
            "stop_order": {"side": "SELL", "label": "stop_order", "price": stop_price},
            "caps_check": {"within_max_loss": True, "max_notional_usd": 10_000_000, "max_loss_usd": -1_000_000},
            "max_position_size": sum(e["amount"] for e in entries),
            "entry_orders": entries}


def _plan_with_target():
    return {"stop": {"type": "fixed_percent", "percent_below_entry": 1.25},
            "targets": [{"amount_percent": 100, "pnl_target_percent": 1.0}]}


def _events(plan_id, etype=None):
    ev = journal.read_events(plan_id)
    return [e for e in ev if e["event_type"] == etype] if etype else ev


def _types(plan_id):
    return [e["event_type"] for e in _events(plan_id)]


# ------------------------------------------------------------------ entry rejected (the 10031 incident)

def test_entry_10031_journals_request_and_full_error(env):
    env.fake.fail = lambda m, p: ERR_10031 if m == "private/buy" else None
    with pytest.raises(executor.ExecutionHalted) as ei:
        executor.execute_plan(_compiled("p1"))
    assert str(ei.value) == f"flattened + halted: entry entry_1 rejected: {ERR_10031}"
    (rej,) = _events("p1", "order_rejected")
    d = rej["data"]
    assert d["label"] == "entry_1"
    assert d["error"] == str(ERR_10031)                    # pre-existing key kept for old readers
    assert d["error_code"] == 10031
    assert d["error_detail"] == ERR_10031                  # code, message AND data
    assert d["method"] == "private/buy"
    assert d["request"] == {"method": "private/buy", "instrument_name": INSTRUMENT, "amount": 100,
                            "type": "market", "label": "p1:entry_1"}


def test_entry_rejection_halting_is_exactly_as_before(env):
    env.fake.fail = lambda m, p: ERR_10031 if m == "private/buy" else None
    with pytest.raises(executor.ExecutionHalted) as ei:
        executor.execute_plan(_compiled("p2"))
    assert str(ei.value).startswith("flattened + halted: entry entry_1 rejected:")
    assert _types("p2") == ["intent", "order_rejected", "mismatch_halt"]
    assert _events("p2", "mismatch_halt")[0]["data"] == {"reason": f"entry entry_1 rejected: {ERR_10031}"}
    halt_text = env.halt.read_text(encoding="utf-8")        # fail_closed still writes the HALT (tmp path)
    assert "p2: entry entry_1 rejected" in halt_text
    assert env.fake.count("private/buy") == 1               # 10031 is not retried
    assert env.fake.count("private/close_position") == 0    # nothing filled, nothing to flatten
    assert env.fake.labels_swept() == ["p2:entry_1", "p2:stop_order"]
    assert env.fake.pos == 0 and not any(o["order_state"] in OPEN_STATES for o in env.fake.orders.values())


def test_ladder_second_rung_rejected_records_its_price_and_cancels_the_first(env):
    entries = [{"side": "BUY", "amount": 50, "order_type": "limit", "price": 79500.0, "label": "entry_1"},
               {"side": "BUY", "amount": 50, "order_type": "limit", "price": 79250.5, "label": "entry_2"}]
    env.fake.fail = lambda m, p: ERR_10031 if p.get("label") == "p3:entry_2" else None
    with pytest.raises(executor.ExecutionHalted):
        executor.execute_plan(_compiled("p3", entries, stop_price=78000.0))
    (rej,) = _events("p3", "order_rejected")
    assert rej["data"]["label"] == "entry_2"
    assert rej["data"]["request"] == {"method": "private/buy", "instrument_name": INSTRUMENT, "amount": 50,
                                      "type": "limit", "price": 79250.5, "label": "p3:entry_2"}
    assert env.halt.exists()
    assert env.fake.orders["O1"]["order_state"] == "cancelled"      # rung 1 cancelled by fail_closed, as before


def test_ambiguous_10050_entry_carries_request_and_still_sweeps(env):
    env.fake.fail = lambda m, p: ERR_10050 if m == "private/buy" else None
    with pytest.raises(executor.ExecutionHalted):
        executor.execute_plan(_compiled("p4"))
    (rej,) = _events("p4", "order_rejected")
    assert rej["data"]["error_code"] == 10050
    assert rej["data"]["request"] == {"method": "private/buy", "instrument_name": INSTRUMENT, "amount": 100,
                                      "type": "market", "label": "p4:entry_1"}
    assert env.fake.count("private/buy") == 1               # order-creating call: never retried
    assert "p4:entry_1" in env.fake.labels_swept()
    assert env.halt.exists()


# ------------------------------------------------------------------ stop rejected after a fill

def test_stop_rejected_after_fill_journals_request_and_still_flattens(env):
    env.fake.fail = lambda m, p: ERR_10031 if p.get("type") == "stop_market" else None
    with pytest.raises(executor.ExecutionHalted) as ei:
        executor.execute_plan(_compiled("p5"))
    assert str(ei.value).startswith("flattened + halted: R7 stop could not be placed/resized")
    (rej,) = _events("p5", "order_rejected")
    d = rej["data"]
    assert d["label"] == "stop_order"
    assert d["error_code"] == 10031 and d["error_detail"] == ERR_10031
    assert d["request"] == {"method": "private/sell", "instrument_name": INSTRUMENT, "amount": 100,
                            "type": "stop_market", "label": "p5:stop_order", "reduce_only": True,
                            "trigger_price": 79000.0, "trigger": "mark_price"}
    assert env.fake.pos == 0                                # flattened exactly as before
    assert env.fake.count("private/close_position") == 1
    assert env.halt.exists()
    assert "mismatch_halt" in _types("p5")


def test_stop_resize_rejected_journals_the_edit_request(env):
    # market rung fills at once and gets a stop for 50; the limit rung fills only after that stop exists, so the
    # second poll must RESIZE the stop (private/edit) - and that edit is what the exchange rejects.
    entries = [{"side": "BUY", "amount": 50, "order_type": "market", "price": None, "label": "entry_1"},
               {"side": "BUY", "amount": 50, "order_type": "limit", "price": 79500.0, "label": "entry_2"}]
    env.fake.after_stop = lambda: env.fake.fill("O2")
    env.fake.fail = lambda m, p: ERR_10031 if m == "private/edit" else None
    with pytest.raises(executor.ExecutionHalted) as ei:
        executor.execute_plan(_compiled("p6", entries))
    assert str(ei.value).startswith("flattened + halted: R7 stop could not be placed/resized")
    (rej,) = _events("p6", "order_rejected")
    stop_id = _events("p6", "stop_resized")[0]["data"]["order_id"]
    assert rej["data"]["label"] == "stop_order"
    assert rej["data"]["method"] == "private/edit"
    assert rej["data"]["request"] == {"method": "private/edit", "order_id": stop_id, "amount": 100,
                                      "trigger_price": 79000.0}
    assert env.fake.pos == 0 and env.halt.exists()          # flattened + halted exactly as before


# ------------------------------------------------------------------ target rejected (benign, flow continues)

@pytest.mark.parametrize("err,swept", [(ERR_10031, False), (ERR_10050, True)])
def test_target_rejected_journals_request_and_flow_continues(env, err, swept):
    env.fake.fail = lambda m, p: err if (p.get("type") == "limit" and p.get("reduce_only")) else None
    res = executor.execute_plan(_compiled("p7"), _plan_with_target())
    assert res["status"] == "entry_filled_stop_placed" and res["target_order_ids"] == []
    (rej,) = _events("p7", "order_rejected")
    d = rej["data"]
    assert d["label"] == "target_1"
    assert d["error_code"] == err["code"]
    assert d["request"] == {"method": "private/sell", "instrument_name": INSTRUMENT, "amount": 100,
                            "type": "limit", "price": 80800.0, "label": "p7:target_1", "reduce_only": True}
    assert not env.halt.exists()                            # a missing target is not a safety issue: no halt
    assert "mismatch_halt" not in _types("p7")
    assert env.fake.pos == 100                              # position kept, still protected by its stop
    assert ("p7:target_1" in env.fake.labels_swept()) is swept
    stops = [o for o in env.fake.orders.values() if o["order_type"] == "stop_market"]
    assert len(stops) == 1 and stops[0]["order_state"] == "untriggered"


# ------------------------------------------------------------------ nothing new on the happy path

def test_happy_path_journals_no_rejection_diagnostics(env):
    res = executor.execute_plan(_compiled("p8"), _plan_with_target())
    assert res["status"] == "entry_filled_stop_placed" and len(res["target_order_ids"]) == 1
    assert _types("p8") == ["intent", "order_placed", "order_filled", "order_placed", "stop_resized",
                            "order_placed"]
    for e in _events("p8"):
        assert not ({"request", "error_code", "error_detail", "method"} & set(e["data"])), e
    assert not env.halt.exists()


# ------------------------------------------------------------------ secrets / robustness / restart state

def test_journal_never_contains_the_token_or_credentials(env):
    env.fake.fail = lambda m, p: ERR_10031 if m == "private/buy" else None
    with pytest.raises(executor.ExecutionHalted):
        executor.execute_plan(_compiled("p9"))
    assert any(t == TOKEN for _, _, t in env.fake.calls)    # the token really was sent on the wire...
    text = (env.jdir / "p9.jsonl").read_text(encoding="utf-8")
    for needle in (TOKEN, "Bearer", "client_secret", "client_id", "access_token"):
        assert needle not in text                           # ...and never reaches the journal


def test_request_view_is_a_whitelist():
    view = do._request_view("private/buy", {"instrument_name": INSTRUMENT, "amount": 10, "type": "limit",
                                            "price": 1.0, "label": "l", "reduce_only": True, "post_only": True,
                                            "trigger_price": 2.0, "trigger": "mark_price",
                                            "access_token": "x", "client_secret": "y", "refresh_token": "z",
                                            "something_new": 1})
    assert view == {"method": "private/buy", "instrument_name": INSTRUMENT, "amount": 10, "type": "limit",
                    "price": 1.0, "label": "l", "reduce_only": True, "post_only": True, "trigger_price": 2.0,
                    "trigger": "mark_price"}


def test_order_calls_attach_request_reads_do_not(env):
    env.fake.fail = lambda m, p: ERR_10031
    with pytest.raises(do.DeribitError) as ei:
        do.buy(TOKEN, INSTRUMENT, 100, "limit", price=79500.0, label="l:e", post_only=True)
    assert ei.value.request == {"method": "private/buy", "instrument_name": INSTRUMENT, "amount": 100,
                                "type": "limit", "price": 79500.0, "label": "l:e", "post_only": True}
    assert ei.value.error == ERR_10031 and ei.value.code == 10031
    with pytest.raises(do.DeribitError) as ei:
        do.get_position(TOKEN, INSTRUMENT)
    assert ei.value.request is None                         # a read carries no order request
    assert do.DeribitError("private/buy", {"code": 1}).request is None


def test_rejection_detail_never_raises():
    e = do.DeribitError("private/buy", {"code": 1, "message": object()})      # not JSON-serialisable
    d = executor._rejection_detail(e)
    assert d["error_code"] == 1 and isinstance(d["error_detail"], dict)
    json.dumps(d)
    d2 = executor._rejection_detail(Exception("no .error / .request at all"))
    assert isinstance(d2, dict)
    json.dumps(d2)
    assert executor._rejection_detail(do.DeribitError("m", None))["error_detail"] == {"message": "None"}


def test_rejected_plan_id_is_not_retriable_after_a_restart(env):
    env.fake.fail = lambda m, p: ERR_10031 if m == "private/buy" else None
    with pytest.raises(executor.ExecutionHalted):
        executor.execute_plan(_compiled("p10"))
    env.halt.unlink()                                       # operator cleared the HALT; the journal remains
    env.fake.fail = None
    before = len(env.fake.calls)
    with pytest.raises(executor.ExecutionHalted, match="already has a journal"):
        executor.execute_plan(_compiled("p10"))
    assert len(env.fake.calls) == before                    # refused before any exchange call
