"""MTS Control Room: the operator's one page (status, road to profitability, board, decisions, suggestions).

  python scripts/dev/make_control_room.py                      # write runtime_data/control_room/mts_control_room.html
  python scripts/dev/make_control_room.py --out page.html
  python scripts/dev/make_control_room.py --data-root <live tree>   # read ledger + findings from another checkout

Read-only over the repo. Hand-kept content (road stages, road tasks, evidence, notes, change list) lives in
MyTradingSys/system/control_room.json; rows come from research/BUGS.md (via make_groups), the bigtrade FINDINGS.md
and execution/auto_trades.jsonl. Decisions and suggestions are NOT in the page: they live in the artifact's db.
Publishing and reading the db are Claude tool calls; the loop is in MyTradingSys/system/CONTROL_ROOM.md.
"""
import argparse
import collections
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
import artifacts as af  # noqa: E402
import make_groups as mg  # noqa: E402
import relay_board  # noqa: E402
import session_log  # noqa: E402
import tasks as task_cards  # noqa: E402

CFG = REPO / "MyTradingSys" / "system" / "control_room.json"
TPL = HERE / "control_room.tpl.html"
FINDINGS = "MyTradingSys/research/bigtrade_2026-10-09/FINDINGS.md"
LEDGER = "MyTradingSys/execution/auto_trades.jsonl"
STATUS = "MyTradingSys/research/STATUS.md"
OPEN = {"OPEN", "IN-FIX", "BLOCKED", "ESCALATED", "AUDITED", "REPORTED"}
FX = re.compile(r"^## (F-BT-\d+)\s+(.*?)\s+\[(\w+)\]\s+status:\s*(.*)$")


def finding_status(st):
    s = st.upper()
    if s.startswith(("FIXED", "NOT-A-DEFECT")) or "FIXED FOR BACKTESTS" in s:
        return "CLOSED"
    for k in ("ESCALATED", "AUDITED", "REPORTED"):
        if k in s:
            return k
    return "OPEN"


def load_findings(path):
    out = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        m = FX.match(line)
        if m:
            fid, title, sev, st = m.groups()
            out[fid] = {"id": fid, "sev": {"MEDIUM": "MED"}.get(sev, sev), "status": finding_status(st), "title": title,
                        "group": "EVID", "src": "bigtrade FINDINGS.md"}
    return out


def source_label(src):
    """'layer:rsi:rsi_events:5m' -> 'rsi_events 5m'; 'tom' -> 'tom'."""
    p = src.replace("layer:", "", 1).split(":") if src.startswith("layer:") else [src]
    return p[0] if len(p) == 1 else f"{p[-2]} {p[-1]}"


def load_ledger(path, now):
    """Per-source totals, per-day net, span, and halt skips in the last 7 days. Missing file -> empty."""
    led = collections.defaultdict(lambda: {"n": 0, "w": 0, "net": 0.0, "time": 0})
    day = collections.defaultdict(float)
    src, first, last, halts = {}, None, None, 0
    week_ago = (now - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            ts = r.get("ts")
            if ts:
                first = first or ts
                last = ts
            if r.get("plan_id") and r.get("source"):
                src[r["plan_id"]] = r["source"]
            if r.get("event") == "skipped_halt" and (ts or "") >= week_ago:
                halts += 1
            if r.get("event") == "ledger_row" and r.get("net_pnl_usd") is not None:
                a = led[source_label(src.get(r.get("plan_id"), "unknown"))]
                a["n"] += 1
                a["w"] += r["net_pnl_usd"] > 0
                a["net"] += r["net_pnl_usd"]
                a["time"] += r.get("exit_reason") == "time_exit"
                day[ts[:10]] += r["net_pnl_usd"]
    rows = sorted(({"src": k, **v, "net": round(v["net"], 2)} for k, v in led.items()), key=lambda x: (-x["n"], x["src"]))
    days = [{"d": k, "net": round(v, 2)} for k, v in sorted(day.items())]
    return rows, days, [first, last], halts


def health(cfg, last, halts, status_text, now):
    h = []
    if last:
        age = (now - datetime.strptime(last, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)).total_seconds() / 3600
        s = "ok" if age < 2 else "warn" if age < 12 else "bad"
        h.append({"k": "Testnet stack", "v": "Running" if s == "ok" else f"Quiet {age:.0f} h", "s": s,
                  "d": f"last ledger event {last}"})
    else:
        h.append({"k": "Testnet stack", "v": "No ledger", "s": "warn", "d": "auto_trades.jsonl not found in this checkout"})
    h.append({"k": "Daily-loss halt", "v": f"{halts} skips / 7 d", "s": "ok" if halts == 0 else "warn",
              "d": "signals skipped by HALT_DAILY_LOSS in the last 7 days"})
    m = re.search(r"SHOTS landed (\d+): new (\d+), classified (\d+), read (\d+), done (\d+) \| overdue\(>24h\) (\d+)", status_text)
    if m:
        landed, new, cls, rd, done, overdue = map(int, m.groups())
        open_ = new + cls + rd
        h.append({"k": "Screenshots", "v": f"{open_} open", "s": "ok" if open_ == 0 else "bad" if overdue else "warn",
                  "d": f"{overdue} overdue past 24 h, {done} closed of {landed}"})
    return h + cfg.get("health_notes", [])


SEV_RANK = {"HIGH": 3, "MED": 2, "MEDIUM": 2, "LOW": 1}


def layer_board(cfg, items):
    """One row per layer in active work (control_room.json `layers`); a parked layer is left out.
    open_rows / worst come from the registry rows the layer names, never from the config."""
    out = []
    for x in cfg.get("layers", []):
        if x.get("stage") == "parked":
            continue
        opened = [items[r] for r in x.get("rows", []) if r in items and items[r]["status"] in OPEN]
        worst = max((o["sev"] for o in opened), key=lambda v: SEV_RANK.get(v, 0), default="")
        out.append({**x, "open_rows": len(opened), "open_ids": [o["id"] for o in opened], "worst": worst})
    return out


def page_index():
    """One row per kept page with its single live link (registry.json); a page with no url yet is left out."""
    out = []
    for pg in af.load()["pages"]:
        own = pg.get("single_owner") or next((a for a, u in pg["urls"].items() if u), "")
        url = pg["urls"].get(own, "")
        if url and pg["status"] == "canonical":
            out.append({"title": pg["title"], "url": url, "refresh": pg["refresh"], "owner": own,
                        "pub": str(pg["last_published"].get(own, ""))[:10]})
    return out


def build(cfg, data_root, now=None):
    now = now or datetime.now(timezone.utc)
    # registry = this checkout's rows (origin, freshest status) plus rows only the data checkout has (filed there, not yet shipped)
    gcfg = mg.load_cfg()
    rows = mg.load_rows()
    other = data_root / "MyTradingSys/research/BUGS.md"
    if other.exists() and other.resolve() != mg.BUGS.resolve():
        own, bugs = {r["id"] for r in rows}, mg.BUGS
        try:
            mg.BUGS = other
            rows += [r for r in mg.load_rows() if r["id"] not in own]
        finally:
            mg.BUGS = bugs
    items = {}
    for r in rows:
        g, _ = mg.classify(r, gcfg)
        items[r["id"]] = {"id": r["id"], "sev": r["sev"], "status": r["status"], "title": r["title"], "group": g, "src": "BUGS.md"}
    items.update(load_findings(data_root / FINDINGS))
    # a finding fixed on trunk before its FINDINGS.md owner ships the status line: the config closes it (id -> receipt text)
    for fid, why in cfg.get("finding_closed", {}).items():
        if fid in items:
            items[fid] = {**items[fid], "status": "CLOSED", "title": items[fid]["title"], "src": "FINDINGS.md + closed in control_room.json: " + why[:80]}
    for k, (sev, st, t) in cfg.get("x_tasks", {}).items():
        items[k] = {"id": k, "sev": sev, "status": st, "title": t, "group": "ROAD", "src": "road task (no registry row yet)"}
    stage_of = {i: s["id"] for s in cfg["road"] for i in s["items"]}
    missing = sorted(i for i in stage_of if i not in items)
    board = []
    for it in items.values():
        if it["status"] in OPEN or it["id"] in stage_of:
            board.append({**it, "stage": stage_of.get(it["id"], "PLAT"), "open": it["status"] in OPEN})
    ledger, days, span, halts = load_ledger(data_root / LEDGER, now)
    st = data_root / STATUS
    backlog = task_cards.summary(REPO)
    return {"generated": now.strftime("%Y-%m-%d %H:%M UTC"), "verdict": cfg.get("verdict", ""), "road": cfg["road"],
            "board": board, "layers": layer_board(cfg, items), "missing": missing, "ledger": ledger, "days": days, "ledger_span": span,
            "backlog": backlog, "relay": relay_board.board(REPO, backlog["rows"], now),
            "sessions": session_log.view(REPO, 48, now),
            "pages": page_index(), "evidence": cfg.get("evidence", []), "changelog": cfg.get("changelog", [])[-6:][::-1],
            "health": health(cfg, span[1], halts, st.read_text(encoding="utf-8") if st.exists() else "", now),
            "groups": {g["code"]: g["name"] for g in gcfg["groups"]},
            # every row, closed too: an Inbox item shows the live status of the row it was filed as (its resolution)
            "reg": {k: {"status": v["status"], "title": v["title"][:160]} for k, v in items.items()}}


def render(data, tpl_text):
    blob = json.dumps(data, ensure_ascii=True).replace("</", "<\\/")
    if "/*__DATA__*/null" not in tpl_text:
        raise SystemExit("template has no /*__DATA__*/null slot")
    return af.put_banner(tpl_text.replace("/*__DATA__*/null", blob), af.load(), "mts_control_room", strict=False)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=str(REPO / "runtime_data" / "control_room" / "mts_control_room.html"))
    ap.add_argument("--data-root", default=str(REPO), help="checkout to read the ledger, findings and STATUS.md from")
    a = ap.parse_args(argv)
    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    data = build(cfg, Path(a.data_root))
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(data, TPL.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
    n_open = sum(b["open"] for b in data["board"])
    print(f"wrote {out} | board {len(data['board'])} items, {n_open} open | ledger {sum(x['n'] for x in data['ledger'])} trades"
          f" | publish to {cfg.get('artifact_url')}")
    if data["missing"]:
        print("WARN road ids with no row/finding/x_task (dropped from the page): " + ", ".join(data["missing"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
