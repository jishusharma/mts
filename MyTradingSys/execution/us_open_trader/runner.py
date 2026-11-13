"""runner.py - live watcher for the us_open_trader (DESIGN v1 section 6 as replaced by V2-8; V2-2 slippage guard;
V2-4 one bar shape). TESTNET ONLY (Deribit test) or paper. There is no mainnet flag.

The runner contains NO trading rule of its own: entries, exits, stops, targets and arming come from engine.step /
fill / reject / force_exit. The runner only moves information between the closed 1m klines of the ref feed, the engine
and the exchange (through cotrade.place_order / ensure_stop / close_trade, which carry the real safety checks).

Per poll: HALT files -> ref price + basis (deribit mark - ref price, re-measured with its time) -> closed 1m klines
(score.fetch_klines / closed_bars, the same source and parser as score.py) -> engine.step on each new closed bar ->
act on events -> exchange position check -> pending stop move / pending close -> flat time.

Fail closed (each sets `halted_reason`: NO new entries for the day; an open position stays under its server stop,
is still managed and is still closed at flat time): HALT file, stale ref price / klines (> 30 s), corrupt or missing
state on a mid-session restart, exchange position without state, any cotrade `ok: False`, liquidation check failed.
Never widens a stop (cotrade.ensure_stop never loosens). Never touches an order directly: the only exchange writes are
the three cotrade calls, so only orders labelled `cotrade` are ever affected.

Every parameter is SOURCED (<file>) or OURS.
"""
import argparse
import json
import math
import os
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import engine  # noqa: E402
import score  # noqa: E402

BAR_MS = score.BAR_MS                  # 1m klines (SOURCED us_open_trader/score.py BAR_MS)
STALE_MS = 30000                       # price / basis / klines older than this are stale (SOURCED DESIGN v1 section 6, V2-8)
SLIPPAGE_FRAC = 0.25                   # refuse the entry when ref is more than 0.25*stop_dist beyond the trigger (SOURCED V2-2)
LIQ_STOP_MULT = 2.0                    # stop must sit >= 2*stop_dist inside the liquidation price (SOURCED V2-8)
TICK = 0.5                             # BTC-PERPETUAL price tick (SOURCED execution/cotrade.py TICK)
BE_MIN_TICKS = 2                       # a moved stop must be >= 2 ticks on the protective side of the mark (SOURCED V2-8)
MAX_FINAL_CLOSE_TRIES = 3              # close_trade attempts after flat time, then give up (server stop stays) (OURS)
MID_SESSION_AFTER_MS = BAR_MS          # state missing/corrupt once the first armed bar has closed = mid-session (OURS)
INSTRUMENT = "BTC-PERPETUAL"           # SOURCED execution/cotrade.py INSTRUMENT
STATE_VERSION = 1                      # OURS


# ------------------------------------------------------------------ small helpers

def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def _tick(p):
    return round(p / TICK) * TICK


def _find_order(state, oid):
    for o in state["plan"]["orders"]:
        if o["id"] == oid:
            return o
    raise KeyError(oid)


def _atomic_write(path, obj):
    """Temp file in the same directory, then os.replace: a crash leaves the old file or the new one, never half."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            json.dump(obj, f, sort_keys=True)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, str(path))
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


# ------------------------------------------------------------------ exchanges (the only code that talks outward)

class PaperExchange:
    """Simulated exchange for mode=paper: zero client calls. Fills at the next bar's open (or the trigger when
    asked), a fake position, a simulated server stop that closes it. Prices are ref-feed prices (basis 0)."""
    live = False
    checks_liq = False

    def __init__(self):
        self.pos = None         # {"side","amount","stop"}
        self.ref = None
        self.last_exit = None

    def snapshot(self):
        return {"pos": self.pos, "last_exit": self.last_exit}

    def restore(self, snap):
        if snap:
            self.pos, self.last_exit = snap.get("pos"), snap.get("last_exit")

    def mark(self):
        if self.ref is None:
            raise RuntimeError("no ref price yet")
        return self.ref

    def place(self, said, side, amount, stop, fill_price=None):
        self.pos = {"side": side, "amount": amount, "stop": stop}
        self.last_exit = None
        return {"ok": True, "fill_price": fill_price}

    def position(self):
        if self.pos is None:
            return {"size": 0, "avg": None, "liq": None}
        return {"size": self.pos["amount"] if self.pos["side"] == "buy" else -self.pos["amount"],
                "avg": None, "liq": None}

    def ensure_stop(self, px):
        if self.pos is not None and px is not None:
            long_ = self.pos["side"] == "buy"
            self.pos["stop"] = max(self.pos["stop"], px) if long_ else min(self.pos["stop"], px)   # never loosen
        return {"ok": True}

    def close(self, reason):
        if self.pos is not None and self.last_exit is None:
            self.last_exit = self.ref
        self.pos = None
        return {"ok": True}

    def on_bar(self, bar):
        """The simulated server stop: a touched stop closes the fake position at the stop price."""
        p = self.pos
        if p is None:
            return
        hit = bar["l"] <= p["stop"] if p["side"] == "buy" else bar["h"] >= p["stop"]
        if hit:
            self.last_exit = p["stop"]
            self.pos = None

    def exit_price(self, since_ms, side):
        return self.last_exit

    def settle_entering(self, intent):
        return ("reject", "paper_restart")


class DeribitExchange:
    """Testnet exchange. Writes go ONLY through cotrade (place_order / ensure_stop / close_trade); the client is used
    for reads (mark, position, order state, user trades). The injected `cot` is the cotrade module (or a fake)."""
    live = True
    checks_liq = True

    def __init__(self, cot, client, account=None, journal_dir=None, halt_path=None, env=None, secret_exists=None):
        self.cot, self.client, self.account = cot, client, account
        self.journal_dir, self.halt_path, self.env, self.secret_exists = journal_dir, halt_path, env, secret_exists
        self._token = None

    def _kw(self):
        kw = {"client": self.client, "account": self.account, "journal_dir": self.journal_dir,
              "halt_path": self.halt_path, "env": self.env}
        return {k: v for k, v in kw.items() if v is not None or k == "account"}

    def _read(self, fn):
        """A private read with one re-authentication on error."""
        for attempt in (0, 1):
            try:
                if self._token is None:
                    self._token = self.client.authenticate(self.account)
                return fn(self._token)
            except Exception:  # noqa: BLE001
                self._token = None
                if attempt:
                    raise

    def mark(self):
        t = self.client.get_ticker(INSTRUMENT)
        m = t.get("mark_price") if isinstance(t, dict) else None
        if not _num(m) or m <= 0:
            raise RuntimeError("mark price unreadable: %r" % (t,))
        return float(m)

    def position(self):
        p = self._read(lambda tok: self.client.get_position(tok, INSTRUMENT))
        size = p.get("size", 0) if isinstance(p, dict) else None
        if not _num(size):
            raise RuntimeError("position unreadable: %r" % (p,))
        return {"size": size, "avg": p.get("average_price"), "liq": p.get("estimated_liquidation_price")}

    def place(self, said, side, amount, stop, fill_price=None):
        try:
            r = self.cot.place_order(said, side, "market", None, amount, stop, **self._kw())
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "reasons": ["place_order raised %r" % (e,)]}
        if not isinstance(r, dict) or not r.get("ok"):
            return {"ok": False, "reasons": (r or {}).get("reasons") if isinstance(r, dict) else [repr(r)]}
        px = None
        oid = r.get("order_id")
        try:
            st = self._read(lambda tok: self.client.get_order_state(tok, oid))
            px = st.get("average_price") if isinstance(st, dict) else None
        except Exception:  # noqa: BLE001
            px = None
        if not (_num(px) and px > 0):
            try:
                px = self.position().get("avg")
            except Exception:  # noqa: BLE001
                px = None
        return {"ok": True, "fill_price": float(px) if _num(px) and px > 0 else None, "order_id": oid}

    def ensure_stop(self, px):
        try:
            return self.cot.ensure_stop(stop_px=px, **self._kw())
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "reasons": ["ensure_stop raised %r" % (e,)]}

    def close(self, reason):
        kw = self._kw()
        if self.secret_exists is not None:
            kw["secret_exists"] = self.secret_exists
        try:
            return self.cot.close_trade(reason=reason, **kw)
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "reasons": ["close_trade raised %r" % (e,)]}

    def on_bar(self, bar):
        pass

    def exit_price(self, since_ms, side):
        """Volume-weighted price of the reduce-side user trades since the entry; None when there is no such trade."""
        try:
            now = int(time.time() * 1000)
            trades = self._read(lambda tok: self.client.get_user_trades_by_instrument_and_time(
                tok, INSTRUMENT, int(since_ms), now))
        except Exception:  # noqa: BLE001
            return None
        opp = "sell" if side == "buy" else "buy"
        qty = val = 0.0
        for t in trades or []:
            reduce_side = t.get("reduce_only") if "reduce_only" in t else t.get("direction") == opp
            if reduce_side and _num(t.get("price")) and _num(t.get("amount")) and t["amount"] > 0:
                qty += t["amount"]
                val += t["amount"] * t["price"]
        return val / qty if qty > 0 else None

    def settle_entering(self, intent):
        """Restart with a write-ahead `entering` intent: decide from the exchange position and the cotrade journal.
        Returns ("fill", exchange_price) | ("reject", reason) | ("mismatch", reason)."""
        try:
            pos = self.position()
        except Exception as e:  # noqa: BLE001
            return ("unreadable", "position unreadable: %r" % (e,))
        if pos["size"] == 0:
            return ("reject", "restart_no_position")
        try:
            jdir = self.journal_dir if self.journal_dir is not None else self.cot.journal_dir()
            recs = self.cot._records(Path(jdir))
        except Exception as e:  # noqa: BLE001
            return ("mismatch", "journal unreadable: %r" % (e,))
        lo = intent.get("wall_ms", 0) - 60000   # OURS: journal clock vs runner clock tolerance
        placed = []
        for r in recs:
            if (r.get("action") or {}).get("kind") == "place" and (r.get("result") or {}).get("state") == "placed":
                try:
                    ts = datetime.fromisoformat(r["ts_utc"]).timestamp() * 1000
                except Exception:  # noqa: BLE001
                    continue
                if ts >= lo:
                    placed.append(r)
        if not placed:
            return ("mismatch", "position on the exchange but no placed record for this intent")
        px = pos.get("avg")
        if not (_num(px) and px > 0):
            return ("mismatch", "position average price unreadable")
        return ("fill", float(px))


# ------------------------------------------------------------------ runner

class Runner:
    def __init__(self, plan, mode, ex, said, poll_secs, clock, sleep, price_fn, kline_fn, state_dir, halt_paths,
                 paper_fill, max_polls, log):
        self.plan, self.mode, self.ex, self.said = plan, mode, ex, said
        self.poll_secs, self.clock, self.sleep = poll_secs, clock, sleep
        self.price_fn, self.kline_fn = price_fn, kline_fn
        self.state_path = Path(state_dir) / ("state_%s.json" % plan["day"])
        self.halt_paths = [Path(p) for p in halt_paths]
        self.paper_fill, self.max_polls, self.log = paper_fill, max_polls, log
        self.paper = mode == "paper"
        self.symbol = score._symbol(plan)
        self.events = []
        self.st = None       # engine state
        self.rn = None       # runner state
        self.cur_t = None    # exit time stamp used inside bar processing
        self.polls = 0

    # ---- time
    def now_ms(self):
        return int(round(self.clock() * 1000))

    # ---- state file
    def save(self):
        if self.paper:
            self.rn["paper"] = self.ex.snapshot()
        _atomic_write(self.state_path, {"version": STATE_VERSION, "mode": self.mode, "engine": self.st,
                                        "runner": self.rn})

    def _fresh_rn(self):
        return {"last_bar_t": None, "halted_reason": None, "basis": None, "basis_t": None, "last_price": None,
                "last_price_ts": None, "last_price_ok_ms": None, "last_kline_ok_ms": None, "pending_stop": None,
                "pending_close": None, "paper_pending": None, "final_tries": 0, "final_close": None,
                "intent": None, "paper": None, "basis_at_fill": None}

    def load_or_new(self, now_ms):
        """Returns None, or a refusal string."""
        if self.state_path.exists():
            try:
                d = json.loads(self.state_path.read_text(encoding="utf-8"))
                if not (isinstance(d, dict) and isinstance(d.get("engine"), dict) and isinstance(d.get("runner"), dict)
                        and d["engine"].get("plan", {}).get("day") == self.plan["day"]):
                    raise ValueError("unexpected shape")
                if d.get("mode") != self.mode:
                    return "state file is mode %r, this run is %r: refused" % (d.get("mode"), self.mode)
                self.st, self.rn = d["engine"], {**self._fresh_rn(), **d["runner"]}
                if self.paper:
                    self.ex.restore(self.rn.get("paper"))
                return None
            except ValueError as e:   # JSON errors are ValueError too
                aside = self.state_path.with_name(self.state_path.name + ".corrupt")
                os.replace(str(self.state_path), str(aside))
                self._fresh(now_ms)
                self.halt("state_corrupt: %s (moved to %s)" % (e, aside.name))
                return None
        self._fresh(now_ms)
        if now_ms >= self.st["arm_ms"] + MID_SESSION_AFTER_MS:
            self.halt("state_missing: no state file on a mid-session start")
        return None

    def _fresh(self, now_ms):
        self.st = engine.new_state(self.plan, live=True, mode=self.mode)
        self.rn = self._fresh_rn()

    def halt(self, reason):
        if self.rn["halted_reason"] is None:
            self.rn["halted_reason"] = reason
            self.log("HALTED (no new entries today): %s" % reason)

    # ---- engine plumbing
    def _emit(self, events):
        self.events.extend(events)

    def _in_position(self):
        return self.st["position"] is not None

    # ---- measurement
    def _measure(self, now_ms):
        rn = self.rn
        if rn["last_price_ok_ms"] is None:
            rn["last_price_ok_ms"] = rn["last_kline_ok_ms"] = now_ms   # grace: stale counts from the first poll
        try:
            r = self.price_fn()
            price, ts = (r if isinstance(r, tuple) else (r, now_ms / 1000.0))
            if not (_num(price) and price > 0 and _num(ts)) or now_ms - ts * 1000 > STALE_MS:
                raise ValueError("unusable or stale reading %r" % (r,))
            rn["last_price"], rn["last_price_ts"], rn["last_price_ok_ms"] = float(price), ts * 1000, now_ms
        except Exception as e:  # noqa: BLE001
            self.log("price read failed: %r" % (e,))
            return
        if self.paper:
            self.ex.ref = rn["last_price"]
        try:
            rn["basis"], rn["basis_t"] = (self.ex.mark() - rn["last_price"]), now_ms   # paper: 0
        except Exception as e:  # noqa: BLE001 - keep the old basis with its old time
            self.log("mark read failed: %r" % (e,))

    def _basis_fresh(self, now_ms):
        return self.rn["basis"] is not None and now_ms - self.rn["basis_t"] <= STALE_MS

    def _check_stale(self, now_ms):
        if now_ms < self.st["arm_ms"]:
            return
        rn = self.rn
        if now_ms - rn["last_price_ok_ms"] > STALE_MS:
            self.halt("stale_price: no fresh ref price for %ds" % ((now_ms - rn["last_price_ok_ms"]) // 1000))
        if now_ms - rn["last_kline_ok_ms"] > STALE_MS:
            self.halt("stale_price: no klines for %ds" % ((now_ms - rn["last_kline_ok_ms"]) // 1000))

    def _check_halt_files(self):
        for p in self.halt_paths:
            if p.exists():
                self.halt("halt_file: %s present" % p.name)
                return

    # ---- klines
    def _new_bars(self, now_ms):
        rn = self.rn
        start = self.st["arm_ms"] if rn["last_bar_t"] is None else max(self.st["arm_ms"], rn["last_bar_t"] + BAR_MS)
        if now_ms < self.st["arm_ms"] or start > now_ms:
            return []
        try:
            bars = self.kline_fn(self.symbol, start, now_ms)
        except Exception as e:  # noqa: BLE001
            self.log("kline fetch failed: %r" % (e,))
            return []
        rn["last_kline_ok_ms"] = now_ms
        last = rn["last_bar_t"] if rn["last_bar_t"] is not None else -1
        return [b for b in sorted(score.closed_bars(bars, now_ms), key=lambda b: b["t"]) if b["t"] > last]

    # ---- bar processing
    def process_bar(self, bar, now_ms):
        st, rn = self.st, self.rn
        self.cur_t = bar["t"] if self.paper else now_ms
        if self.paper:
            pend = rn["paper_pending"]
            if pend and bar["t"] > pend["t"] and st["entering"] is not None:
                self._paper_fill_pending(pend, bar)
            if bar["t"] < st["flat_ms"]:   # the flat bar is a time exit at its open: no stop simulation there (engine rule)
                self.ex.on_bar(bar)
        _, events = engine.step(st, bar)
        rn["last_bar_t"] = bar["t"]
        self._emit(events)
        for ev in events:   # decisions are written before any exchange call (restart-safe)
            if ev["type"] == "move_stop":
                rn["pending_stop"] = ev["price"]
            elif ev["type"] == "exit" and ev["reason"] == "target":
                rn["pending_close"] = {"reason": "target", "engine_exit": False}
        self.save()
        for ev in events:
            if ev["type"] == "enter":
                self._enter(ev, now_ms)
        self._act_pending(now_ms)
        if self.paper:
            self._check_position(now_ms)
            self._act_pending(now_ms)
        self.save()

    # ---- entry
    def _reject(self, oid, t, reason):
        _, ev = engine.reject(self.st, oid, t, reason)
        self._emit(ev)
        self.rn["intent"] = None
        self.rn["paper_pending"] = None
        self.save()

    def _enter(self, ev, now_ms):
        st, rn = self.st, self.rn
        oid, t = ev["order_id"], ev["t"]
        o = _find_order(st, oid)
        if rn["halted_reason"]:
            return self._reject(oid, t, "halted: %s" % rn["halted_reason"])
        if rn["last_price"] is None or now_ms - rn["last_price_ok_ms"] > STALE_MS:
            return self._reject(oid, t, "stale_price")
        if not self._basis_fresh(now_ms):
            return self._reject(oid, t, "basis_stale")
        px = rn["last_price"]
        beyond = (px - o["trigger"]) if engine._goes_up(o) else (o["trigger"] - px)
        if beyond > SLIPPAGE_FRAC * o["stop_dist"]:
            return self._reject(oid, t, "slippage_guard: ref %s is %.1f beyond trigger %s" % (px, beyond, o["trigger"]))
        sign = 1 if o["side"] == "buy" else -1
        amount = o.get("amount_usd") or st["plan"]["amount_usd"]
        rn["intent"] = {"order_id": oid, "t": t, "side": o["side"], "amount": amount, "wall_ms": now_ms}
        if self.paper:
            if self.paper_fill == "trigger":
                self._paper_open(o, t, float(o["trigger"]), amount)
            else:
                rn["paper_pending"] = {"order_id": oid, "t": t}
                self.save()
            return
        try:
            mark = self.ex.mark()
        except Exception as e:  # noqa: BLE001
            return self._reject(oid, t, "mark_unreadable: %r" % (e,))
        stop = _tick(mark - sign * o["stop_dist"])
        self.save()   # write-ahead: engine `entering` + intent are on disk before the order goes out
        r = self.ex.place(self.said, o["side"], amount, stop)
        if not r.get("ok"):
            self.halt("cotrade: place refused/failed: %s" % (r.get("reasons"),))
            try:
                if self.ex.position()["size"] != 0:   # something filled before the failure: take it off
                    rn["pending_close"] = {"reason": "place_failed", "engine_exit": False}
                    self._act_pending(now_ms)
            except Exception as e:  # noqa: BLE001
                self.halt("cotrade: position unreadable after failed place: %r" % (e,))
            return self._reject(oid, t, "cotrade_refused")
        fp = r.get("fill_price")
        if not (_num(fp) and fp > 0):
            self.halt("cotrade: fill price unreadable")
            rn["pending_close"] = {"reason": "fill_unreadable", "engine_exit": False}
            self._act_pending(now_ms)
            return self._reject(oid, t, "fill_unreadable")
        self._after_fill(o, t, fp - rn["basis"], stop, now_ms)

    def _paper_open(self, o, t, fill, amount):
        sign = 1 if o["side"] == "buy" else -1
        self.ex.place(self.said, o["side"], amount, fill - sign * o["stop_dist"], fill_price=fill)
        self._after_fill(o, t, fill, None, self.now_ms())

    def _paper_fill_pending(self, pend, bar):
        o = _find_order(self.st, pend["order_id"])
        amount = self.rn["intent"]["amount"] if self.rn["intent"] else self.st["plan"]["amount_usd"]
        self.rn["paper_pending"] = None
        self._paper_open(o, bar["t"], float(bar["o"]), amount)

    def _after_fill(self, o, t, ref_fill, ex_stop, now_ms):
        st, rn = self.st, self.rn
        _, ev = engine.fill(st, o["id"], t, ref_fill)
        self._emit(ev)
        rn["intent"] = None
        rn["basis_at_fill"] = rn["basis"]
        self.save()
        if self.ex.checks_liq and ex_stop is not None:
            self._liq_check(o, ex_stop, now_ms)
        elif self.ex.checks_liq:   # adopted at restart: the exchange stop is whatever cotrade holds; judge by the engine stop
            self._liq_check(o, st["position"]["stop"] + rn["basis"], now_ms)

    def _liq_check(self, o, ex_stop, now_ms):
        need = LIQ_STOP_MULT * o["stop_dist"]
        try:
            pos = self.ex.position()
            liq = pos.get("liq")
            if pos["size"] != 0:
                ok = _num(liq) and ((ex_stop - liq) if o["side"] == "buy" else (liq - ex_stop)) >= need
            else:
                ok = True
        except Exception:  # noqa: BLE001
            ok = False
        if not ok:
            self.halt("liquidation_check: stop %s not >= %s inside liquidation" % (ex_stop, need))
            self.rn["pending_close"] = {"reason": "liq_check", "engine_exit": True}
            self._act_pending(now_ms)

    # ---- stop moves
    def _apply_pending_stop(self, now_ms):
        rn = self.rn
        if rn["pending_stop"] is None or not self._in_position():
            rn["pending_stop"] = None if not self._in_position() else rn["pending_stop"]
            return
        if not self._basis_fresh(now_ms):
            return   # never act on an old basis: the move waits (the initial stop keeps protecting)
        pos = self.st["position"]
        new = rn["pending_stop"] + rn["basis"]
        try:
            mark = self.ex.mark()
        except Exception:  # noqa: BLE001
            return
        gap = BE_MIN_TICKS * TICK
        protective = (new <= mark - gap) if pos["side"] == "buy" else (new >= mark + gap)
        rn["pending_stop"] = None
        if not protective:   # the stop would be rejected: leave the trade at once instead
            rn["pending_close"] = {"reason": "be_close", "engine_exit": True}
            self.save()
            return
        r = self.ex.ensure_stop(_tick(new) if not self.paper else new)
        if not r.get("ok"):
            self.halt("cotrade: ensure_stop failed: %s" % (r.get("reasons"),))
        self.save()

    # ---- closing
    def _act_pending(self, now_ms):
        rn = self.rn
        self._apply_pending_stop(now_ms)
        pc = rn["pending_close"]
        if pc is None:
            return
        r = self.ex.close(pc["reason"])
        if not r.get("ok"):
            self.halt("cotrade: close_trade failed: %s" % (r.get("reasons"),))
            self.save()
            return   # retried on the next poll
        rn["pending_close"] = None
        if pc["engine_exit"] and self._in_position():
            self._engine_exit(pc["reason"], now_ms)
        self.save()

    def _engine_exit(self, reason, now_ms):
        st, rn = self.st, self.rn
        pos = st["position"]
        t = self.cur_t if self.cur_t is not None else now_ms
        px = self.ex.exit_price(pos["entry_t"], pos["side"])
        basis = rn["basis"] if (rn["basis"] is not None and self._basis_fresh(now_ms)) else rn.get("basis_at_fill")
        known = _num(px) and (basis is not None or self.paper)
        ref = (px - (basis or 0.0)) if known else pos["stop"]   # placeholder only; the row is blanked below
        _, ev = engine.force_exit(st, t, ref, reason)
        self._emit(ev)
        if not known:   # never invented: no matching exchange trade -> the row says so
            row = st["trades"][-1]
            row.update({"exit": None, "r_gross": None, "r_net": None, "exit_price_known": False})

    def _check_position(self, now_ms):
        st, rn = self.st, self.rn
        if rn["pending_close"] is not None or st["entering"] is not None or rn["paper_pending"]:
            return
        try:
            size = self.ex.position()["size"]
        except Exception as e:  # noqa: BLE001
            self.log("position read failed: %r" % (e,))
            return
        if self._in_position():
            if size == 0:   # the server stop filled: clean up leftovers, then book the exit
                moved = st["position"]["moved"]
                rn["pending_close"] = {"reason": "be_stop" if moved else "stop", "engine_exit": True}
        elif size != 0:
            self.halt("position_without_state: exchange holds %s but the engine has no position" % size)

    # ---- restart: settle a write-ahead intent
    def _settle_entering(self, now_ms):
        st, rn = self.st, self.rn
        ent = st["entering"]
        if ent is None or self.paper or not self._basis_fresh(now_ms):
            return
        intent = rn["intent"] or {"order_id": ent["order_id"], "t": ent["t"], "wall_ms": 0}
        verdict, val = self.ex.settle_entering(intent)
        o = _find_order(st, ent["order_id"])
        if verdict == "fill":
            self._after_fill(o, ent["t"], val - rn["basis"], None, now_ms)
            r = self.ex.ensure_stop(None)    # keep / verify the stop of the adopted position (never loosens)
            if not r.get("ok"):
                self.halt("cotrade: ensure_stop failed: %s" % (r.get("reasons"),))
        else:
            if verdict != "reject":
                self.halt("%s: %s" % ("position_without_state" if verdict == "mismatch" else "cotrade", val))
            self._reject(ent["order_id"], ent["t"], "restart: %s" % val)

    # ---- one poll
    def poll(self):
        now_ms = self.now_ms()
        st, rn = self.st, self.rn
        self._check_halt_files()
        self._measure(now_ms)
        self._settle_entering(now_ms)
        bars = [] if st["done"] else self._new_bars(now_ms)
        self._check_stale(now_ms)
        for b in bars:
            self.process_bar(b, now_ms)
        self.cur_t = None
        if not self.paper:
            self._check_position(now_ms)
        if st["done"] and rn["pending_close"] is None and rn["final_close"] is None:
            rn["pending_close"] = {"reason": "flat_time", "engine_exit": False}   # unconditional, whatever the engine thinks
        self._act_pending(now_ms)
        if st["done"] and rn["pending_close"] is not None:
            rn["final_tries"] += 1
        self.save()

    def finished(self):
        st, rn = self.st, self.rn
        if not st["done"]:
            return False
        if rn["pending_close"] is None:
            rn["final_close"] = "ok"
            return True
        if rn["final_tries"] >= MAX_FINAL_CLOSE_TRIES:
            rn["final_close"] = "failed"   # the position (if any) stays under its server stop; the operator is told
            return True
        return False

    def loop(self):
        while True:
            self.poll()
            self.polls += 1
            if self.finished():
                self.save()
                return "finished"
            if self.max_polls is not None and self.polls >= self.max_polls:
                self.save()
                return "max_polls"
            self.sleep(self.poll_secs)


# ------------------------------------------------------------------ public entry points

def _default_halt_paths():
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import executor
    return [executor.HALT_PATH, executor.HALT_DAILY_LOSS_PATH]


def _default_price_fn(symbol):
    def fn():   # public spot ticker; the reading is stamped with the time we got it
        last = None
        for host in score.HOSTS:
            try:
                d = score.http_fetch("https://%s/api/v3/ticker/price?symbol=%s" % (host, symbol))
                return float(d["price"]), time.time()
            except Exception as e:  # noqa: BLE001
                last = e
        raise RuntimeError("all price hosts failed: %r" % (last,))
    return fn


def run(plan_path, mode="paper", poll_secs=5, clock=None, sleep=None, price_fn=None, kline_fn=None, client=None,
        cot=None, said=None, account=None, journal_dir=None, halt_path=None, env=None, state_dir=None,
        halt_paths=None, paper_fill="next_open", max_polls=None, secret_exists=None, log=None):
    """Watch the session described by plan_path until flat time. Returns a result dict (never raises on a refusal)."""
    if mode not in ("paper", "testnet"):
        raise ValueError("mode must be paper or testnet, got %r" % (mode,))
    log = log or (lambda m: print(m, file=sys.stderr))
    plan = json.loads(Path(plan_path).read_text(encoding="utf-8"))
    engine.new_state(plan, live=True, mode=mode)   # validates the plan (ValueError on a malformed one)
    if mode == "testnet":
        if not (said and said.strip()):
            return {"ok": False, "reasons": ["testnet mode needs --said (the operator's words): refused"]}
        if cot is None:
            sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
            import cotrade as cot  # noqa: F811
        if client is None:
            import deribit_orders as client  # noqa: F811
        if env is None:
            env = client.active_env() if hasattr(client, "active_env") else "test"
        if env != "test":
            return {"ok": False, "reasons": ["REFUSED: us_open_trader runs on the Deribit test environment only"]}
        ex = DeribitExchange(cot, client, account, journal_dir, halt_path, env, secret_exists)
    else:
        ex = PaperExchange()
    clock = clock or time.time
    sleep = sleep or time.sleep
    price_fn = price_fn or _default_price_fn(score._symbol(plan))
    kline_fn = kline_fn or (lambda sym, a, b: score.fetch_klines(sym, a, b))
    r = Runner(plan, mode, ex, said, poll_secs, clock, sleep, price_fn, kline_fn,
               state_dir or score.default_out_dir(), halt_paths if halt_paths is not None else _default_halt_paths(),
               paper_fill, max_polls, log)
    refusal = r.load_or_new(r.now_ms())
    if refusal:
        return {"ok": False, "reasons": [refusal]}
    how = r.loop()
    st, rn = r.st, r.rn
    return {"ok": True, "how": how, "trades": st["trades"], "events": r.events, "halted_reason": rn["halted_reason"],
            "final_close": rn["final_close"], "polls": r.polls,
            "state": {"engine": st, "runner": rn, "mode": mode}}


def build_parser():
    ap = argparse.ArgumentParser(description="us_open_trader live watcher: paper (no exchange calls) or Deribit "
                                             "testnet. Testnet only.")
    ap.add_argument("plan", help="plan.json")
    ap.add_argument("--mode", choices=["paper", "testnet"], default="paper")
    ap.add_argument("--said", help="the operator's exact words (required in testnet mode)")
    ap.add_argument("--poll", type=float, default=5, help="seconds between polls")
    return ap


def main(argv=None):
    a = build_parser().parse_args(argv)
    if a.mode == "testnet" and not (a.said and a.said.strip()):
        print("refused: testnet mode needs --said \"<the operator's words>\"", file=sys.stderr)
        return 2
    kw = {}
    if a.mode == "testnet":
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        import cotrade
        import deribit_orders as do
        do.select_environment(False)   # forces testnet, same as cotrade.main; there is no way to choose otherwise
        secret_exists = lambda acct: do.secret_path_for("test", acct).exists()  # noqa: E731
        kw = dict(cot=cotrade, client=do, account=cotrade.pick_account(secret_exists), secret_exists=secret_exists)
    res = run(a.plan, mode=a.mode, poll_secs=a.poll, said=a.said, **kw)
    if not res["ok"]:
        print("refused: %s" % "; ".join(res["reasons"]), file=sys.stderr)
        return 2
    print(json.dumps({k: res[k] for k in ("how", "trades", "halted_reason", "final_close", "polls")}, indent=2,
                     default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
