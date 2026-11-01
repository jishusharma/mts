"""Fabio v3 engine (FABIO_V3_SPEC.md v3.1 section 4): runs models A, B, C, D independently over one window, causally.

Public API: run(bars, config) -> {verdict, model, side, entry, stop, target, management, diagnostics}.

bars = the window's 1m order-flow bars (one session window, oldest first). The engine reports the state AS OF bar
`as_of` (config, default the last bar): bars after it are never read (spec section 2 causality). verdict is a section-4
state name: IDLE | IMPULSE | PROBE | ARMED | SIGNAL | IN_TRADE | DONE. The first model in config["models"] order that
"fires" (ARMED, SIGNAL, IN_TRADE or DONE after a trade) is reported; otherwise the most advanced non-firing state.

Imports: stdlib + v3 siblings only (spec header). Nothing from execution/ or layers/alerts/.
"""
from .day_gates import ENTRY_CUTOFF, WINDOW_BARS, day_gate_open
from .models import (model_a_trade, model_b, model_c, model_d_trade, scan_model_a, scan_model_b, scan_model_c,
                     scan_model_d)
from .signals import B_PROF, K_BAL, effort_arrays, failed_auction, volume_tier

DMAX = 0.01          # P30 NS-fixed: Dmax 1.0% (spec section 4 Common)
IB_LEN = 30          # P38 FABIO: model C IB = first 30 minutes (spec section 4 model C)
M_PUSH = 15          # P07 NS-fixed: S4 window 15 for models A, B, D (spec 7.1 P07); model C takes config["m_c"] {5, 15}
MODELS = ("A", "B", "C", "D")   # spec section 4: "Section 4 defines models A, B, C, D"

# Spec 7.1 NS-grid values have NO default (prompt: "Grid params are REQUIRED config, no defaults").
REQUIRED = ("N",          # P01 NS-grid {60, 120, 240}
            "p",          # P03 NS-grid {0.05, 0.10}
            "z_hi",       # P04 NS-grid {2.0, 2.5, 3.0}
            "m_c",        # P07 NS-grid {5, 15} (model C)
            "f",          # P31 NS-grid {0.3%, 0.5%}
            "g",          # P40 NS-grid {off, 0.8}
            "entry_mode",  # spec section 4 Common: "rest" | "confirm" (grid)
            "mgmt")       # spec 5.2: "event" | "dist" (grid; main grid "event", spec section 11)
FIRING = ("ARMED", "SIGNAL", "IN_TRADE", "DONE")
RANK = {"IDLE": 0, "IMPULSE": 1, "PROBE": 1, "ARMED": 2, "SIGNAL": 3, "IN_TRADE": 4, "DONE": 5}


def _check(config):
    missing = [k for k in REQUIRED if k not in config]
    if missing:
        raise ValueError("missing required config (NS-grid, no defaults): %s" % ", ".join(missing))
    if config["entry_mode"] not in ("rest", "confirm"):
        raise ValueError("entry_mode must be 'rest' or 'confirm', got %r" % (config["entry_mode"],))
    if config["mgmt"] not in ("dist", "event"):
        raise ValueError("mgmt must be 'dist' or 'event', got %r" % (config["mgmt"],))
    if config["mgmt"] == "dist" and "be_k" not in config:
        raise ValueError("missing required config (P21 NS-grid, no default): be_k")   # spec 7.1 P21 {1.0, 2.0}
    for mdl in config.get("models", MODELS):
        if mdl not in MODELS:
            raise ValueError("unknown model %r" % (mdl,))


def _make_gate(bars, o, config):
    """Day gate for models A, C, D (spec section 6 / P40): G(i) from the running window range; fail closed."""
    g = config["g"]
    if g is None or g == "off":
        return None                                                       # g off: always open (spec section 6)
    hi, lo, hh, ll = [], [], None, None
    for b in bars[o:]:
        hh = b["h"] if hh is None else max(hh, b["h"])
        ll = b["l"] if ll is None else min(ll, b["l"])
        hi.append(hh)
        lo.append(ll)
    pr = config.get("prior_ranges")                 # unknown: spec silent on the container; callable(elapsed) -> list

    def gate(b):
        el = b - o
        if el < 0 or el >= len(hi):
            return False                                                  # fail closed
        prior = pr(el) if callable(pr) else (pr or [])
        return day_gate_open(el, hi[el] - lo[el], prior, g)
    return gate


def _tier(bars, o, i, config):
    """S4 tier (spec section 3): config["tier"] if given, else volume_tier(session volume so far, prior_vols)."""
    if "tier" in config:
        return config["tier"]
    pv = config.get("prior_vols")
    if pv is None:
        return "99"                                  # spec S4: fewer than 10 prior days -> "99"
    today = sum(b["buy_vol"] + b["sell_vol"] for b in bars[o:i + 1])
    return volume_tier(today, pv)        # unknown: tier is fixed at as_of for the whole replay (scanners take one tier)


def _manage(mdl, st, bars, o, i, cfg, ctx):
    """Simulate management for a model whose order filled (spec 5.2). Returns a trade dict or None (unknown cases)."""
    kw = dict(end_idx=i, mgmt=cfg["mgmt"], be_k=cfg.get("be_k", 1.0), slip_bps=cfg.get("slip_bps", 0.0),
              s8_kw=ctx["s8_kw"], ctrl=ctx["ctrl"], absorbed=ctx["absb"], last_entry_idx=o + ENTRY_CUTOFF - 1)
    f, mode = cfg["f"], cfg["entry_mode"]
    if mdl == "A":
        if mode != "rest":
            return None      # unknown: scan_model_a IN_TRADE (confirm) returns price = entry, not the LVN touch level
        r = model_a_trade(bars, st["armed_idx"], st["s"], st["O"], st["price"], f, DMAX, entry_mode="rest", **kw)
    elif mdl == "C":
        r = model_c(bars, o, IB_LEN, cfg["m_c"], f, DMAX, entry_mode=mode, tier=ctx["tier"], gate_open=ctx["gate"] or True,
                    **kw)
    elif mdl == "D":
        fa = failed_auction(bars, st["armed_idx"], cfg["N"], ctx["k_bal"], cfg["p"], M_PUSH, ctx["absb"], ctx["tier"],
                            ctx["bin_size"])
        if fa is None:
            return None
        r = model_d_trade(bars, st["armed_idx"], fa["s"], fa["edge"], fa["lvl"], f, DMAX, entry_mode=mode, **kw)
    elif mdl == "B":         # scan_model_b IN_TRADE returns the probe bar + balance: replay model_b on them (spec 4 / 5.2)
        r = model_b(bars, st["probe_idx"], st["bal"], f=f, dmax=DMAX, entry_mode=mode,
                    target_mode=cfg.get("target_mode", "edge"), **kw)
    else:
        return None
    return r["trades"][0] if r["trades"] else None


def _is_open(t, i, o):
    """A trade that 'exits' window_end on the as-of bar before the window ends is still open (spec 5.2 exits)."""
    return t["reason"] == "window_end" and t["exit_idx"] == i and i < o + WINDOW_BARS - 1


def _scan(mdl, bars, o, i, cfg, ctx):
    N, p, f, mode = cfg["N"], cfg["p"], cfg["f"], cfg["entry_mode"]
    kb, bs, tier, gate = ctx["k_bal"], ctx["bin_size"], ctx["tier"], ctx["gate"]
    if mdl == "A":
        return scan_model_a(bars, o, i, N, kb, p, M_PUSH, tier, bs, f, DMAX, mode, ctx["ctrl"], ctx["absb"], gate=gate)
    if mdl == "B":                                                        # spec section 4: model B has no day gate
        return scan_model_b(bars, o, i, N, kb, mode, f, DMAX, ctx["absb"], target_mode=cfg.get("target_mode", "edge"),
                            bin_size=bs)
    if mdl == "C":
        return scan_model_c(bars, o, i, IB_LEN, cfg["m_c"], tier, mode, f, DMAX, gate=gate)
    return scan_model_d(bars, o, i, N, kb, p, M_PUSH, tier, bs, mode, f, DMAX, ctx["absb"], gate=gate)


def _entry_of(st, trade):
    if trade is not None:
        return trade["entry"]
    if st["state"] == "SIGNAL":
        return st.get("entry_ref")        # spec section 4: taker at the next open; c[i] is the reference only
    return st.get("price")


def run(bars, config):
    """Run models A, B, C, D over `bars` as of bar config.get("as_of", len(bars)-1) and report the first that fires."""
    _check(config)
    o = config.get("open_idx", 0)                                      # unknown: window start inside bars (default 0)
    i = config.get("as_of", len(bars) - 1)
    if not bars or not 0 <= o <= i < len(bars):
        raise ValueError("as_of / open_idx outside bars")
    kb, bs = config.get("k_bal", K_BAL), config.get("bin_size", B_PROF)   # P02 NS-fixed k_bal 0.8; P41 SIM bin 50
    ctrl, absb = effort_arrays(bars, i, z_hi=config["z_hi"])             # spec section 3 S3, L 60
    tier = _tier(bars, o, i, config)
    ctx = {"k_bal": kb, "bin_size": bs, "ctrl": ctrl, "absb": absb, "tier": tier, "gate": _make_gate(bars, o, config),
           "s8_kw": {"k_bal": kb, "tier": tier, "bin_size": bs, "z_hi": config["z_hi"], "p": config["p"]}}
    diag, fired, best = {}, None, None
    for mdl in config.get("models", MODELS):
        st = _scan(mdl, bars, o, i, config, ctx)
        trade = None
        if st["state"] == "IN_TRADE":
            trade = _manage(mdl, st, bars, o, i, config, ctx)
            if trade is not None and not _is_open(trade, i, o):
                st = dict(st, state="DONE")                            # section 4 state DONE: trade finished
        diag[mdl] = {"state": st["state"], "setup": st, "trade": trade}
        if st["state"] in FIRING and fired is None:
            fired = (mdl, st, trade)
        if best is None or RANK[st["state"]] > RANK[best[1]["state"]]:
            best = (mdl, st, trade)
    mdl, st, trade = fired or best
    mgmt = None
    if trade is not None:
        mgmt = {"mgmt": trade["mgmt"], "moves": trade["moves"], "exit": trade["exit"], "exit_idx": trade["exit_idx"],
                "reason": trade["reason"], "net_r": trade["net_r"], "stop_now": trade["stop"]}
    # unknown: spec silent on the verdict when no model fires and none is mid-state; IDLE with model None is used
    return {"verdict": st["state"], "model": mdl if st["state"] != "IDLE" else None, "side": st.get("s") or None,
            "entry": _entry_of(st, trade), "stop": (trade["stop0"] if trade else st.get("stop")),
            "target": (trade["target"] if trade else st.get("target")), "management": mgmt, "diagnostics": diag}
