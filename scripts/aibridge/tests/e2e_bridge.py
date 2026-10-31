import sys; sys.dont_write_bytecode = True
"""e2e_bridge.py - end-to-end check of the DSA bridge (AIBridge): rows E0-E5 of FIX_PLAN.md section 4.

  python scripts/aibridge/tests/e2e_bridge.py [--json] [--payload DIR] [--live]          scratch mode (default)
  python scripts/aibridge/tests/e2e_bridge.py --target installed [F:/AIBridge] [--json]  installed mode

Scratch mode: tier A drives a scratch agent (own port/token/policy, copy of the payload) over HTTP; tier B runs node over the payload's
extension/loop.js. Installed mode: the same rows against the installed agent and its installed loop.js (only harmless Write-Output /
exit-code probes; token read from config.json, never printed); it writes only under <root>/run/e2e/<utc>/.
Rows: E0 install, E1 six-block reply, E2 thinking fixture, E3 exit-1 commands, E4 dropped generation, E5 live (NOT_CHECKED without a
Chrome session). Exit 0 only when no row is FAIL; any FAIL -> exit 1. Audit counts ignore dry airun calls.
"""
import argparse
import datetime
import hashlib
import html.parser
import json
import os
import re
import subprocess
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(os.environ.get("MTS_REPO_ROOT") or Path(__file__).resolve().parents[3])
FIX = Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(REPO / "MyTradingSys" / "tests"))
sys.path.insert(0, str(REPO / "scripts" / "dev"))

HARNESS = """
const L = require(process.argv[2]);
const fx = JSON.parse(process.argv[3]);
const out = {};
function need(n) { if (typeof L[n] !== 'function') throw new Error('loop.js has no ' + n + '() (pre-0.7.4 extension)'); return L[n]; }
if (fx.op === 'select') {
  const r = need('selectBlocks')(fx.descs);
  const texts = r.selected.map(i => fx.descs[i].cmd);
  out.selected = r.selected; out.ignored = r.ignored; out.status = r.status;
  out.keys = need('batchKeys')(texts); out.texts = texts;
} else if (fx.op === 'dup') {
  out.dup = need('dupOf')(fx.texts);
} else if (fx.op === 'watch') {
  const w = need('replyWatch'); let st = null; out.actions = [];
  for (const ev of fx.events) { const r = w(st, ev, ev.t * 1000); st = r.state; if (r.action !== 'none') out.actions.push([ev.t, r.action]); }
  out.status = need('quietWaitStatus')(200000, 180000);
}
console.log(JSON.stringify(out));
"""


class Desc(html.parser.HTMLParser):
    """deepseek_reply.html -> [{cmd, chain:[{tag,cls}...]}] for every <code> block."""
    def __init__(self):
        super().__init__()
        self.stack, self.out, self._code = [], [], None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "code":
            self._code = {"cmd": "", "chain": [dict(t) for t in self.stack]}
        elif tag not in ("br", "img"):
            self.stack.append({"tag": tag, "cls": a.get("class", "")})

    def handle_endtag(self, tag):
        if tag == "code" and self._code is not None:
            self.out.append(self._code)
            self._code = None
        elif self.stack and self.stack[-1]["tag"] == tag:
            self.stack.pop()

    def handle_data(self, d):
        if self._code is not None:
            self._code["cmd"] += d


class Rows:
    def __init__(self):
        self.rows = []

    def add(self, name, status, evidence):
        self.rows.append({"case": name, "verdict": status, "evidence": str(evidence)[:600]})
        print("%s %s %s" % (name, status, str(evidence)[:300]), file=sys.stderr, flush=True)


class Agent:
    """HTTP view of an agent: scratch (aibridge_scratch) or installed (config.json). The token is never printed."""
    def __init__(self, scratch=None, root=None):
        self.scratch, self.root = scratch, root
        if scratch:
            self.audit = os.path.join(scratch.sdir, "audit.jsonl")
            self.cwd = scratch.work
        else:
            cfg = json.loads(Path(root, "src", "config.json").read_text(encoding="utf-8-sig"))
            self.token, self.origin = cfg.get("token"), (cfg.get("allowed_origins") or [""])[0]
            self.base = "http://%s:%s" % (cfg.get("bind", "127.0.0.1"), cfg.get("port", 7181))
            self.audit = os.path.join(root, "src", "audit.jsonl")
            self.cwd = str(root)

    def ping(self):
        if self.scratch:
            return self.scratch.http("GET", "/ping", timeout=10)[1]
        req = urllib.request.Request(self.base + "/ping", headers={"Origin": self.origin})
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode() or "{}")

    def run(self, cmd, **kw):
        if self.scratch:
            return self.scratch.run(cmd, **kw)
        body = {"cmd": cmd, "cwd": self.cwd, "token": self.token, "timeout_s": 60}
        body.update(kw)
        req = urllib.request.Request(self.base + "/run", data=json.dumps(body).encode(), method="POST",
                                     headers={"Origin": self.origin, "Content-Type": "text/plain"})
        try:
            with urllib.request.urlopen(req, timeout=240) as r:
                return r.status, json.loads(r.read().decode("utf-8") or "{}")
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode("utf-8") or "{}")

    def audit_size(self):
        return os.path.getsize(self.audit) if os.path.exists(self.audit) else 0

    def audit_since(self, off):
        if not os.path.exists(self.audit):
            return None
        with open(self.audit, "rb") as f:
            f.seek(off)
            data = f.read().decode("utf-8", "replace")
        out = []
        for ln in data.splitlines():
            try:
                out.append(json.loads(ln.split("\t", 1)[1]))
            except Exception:
                pass
        return out

    def task(self, steps):
        return self.run("inline", task="inline", task_spec=json.dumps({"steps": steps}), task_params={})


def node_run(tmp, loop_js, fx):
    h = Path(tmp) / "e2e_harness.js"
    h.write_text(HARNESS, encoding="utf-8", newline="\n")
    p = subprocess.run(["node", str(h), str(loop_js), json.dumps(fx)], capture_output=True, text=True, timeout=60)
    if p.returncode != 0:
        raise RuntimeError((p.stderr.strip().splitlines() or ["node failed"])[-1][:300])
    return json.loads(p.stdout)


def release_current(payload):
    try:
        return json.loads(Path(payload, "RELEASES.json").read_text(encoding="utf-8"))["current"]
    except Exception:
        return "?"


def case(rows, name, fn):
    try:
        st, ev = fn()
    except Exception as e:
        st, ev = "FAIL", "%s: %s" % (type(e).__name__, str(e)[:300])
    rows.add(name, st, ev)


def e0(a, payload, installed_root):
    if installed_root:
        import aibridge_verify
        res = aibridge_verify.check(str(installed_root))
        bad = [r["check"] for r in res if r["status"] == "FAIL"]
        return ("FAIL", "aibridge_verify FAIL rows: " + ", ".join(bad)) if bad else ("PASS", "aibridge_verify: %d rows, no FAIL" % len(res))
    want = re.search(r"AgentVersion = '([^']+)'", Path(payload, "src", "agent.ps1").read_text(encoding="utf-8")).group(1)
    cur = release_current(payload)
    nonce = hashlib.sha1(os.urandom(8)).hexdigest()[:10]
    st, r = a.run("Write-Output " + nonce)
    ping = str(a.ping())
    ok = want == cur and want in ping and st == 200 and nonce in str(r.get("out", "")) and r.get("exit") == 0
    return ("PASS" if ok else "FAIL"), "agent %s RELEASES.current %s ping-has-version=%s roundtrip exit=%s" % (want, cur, want in ping, r.get("exit"))


def e1(a, tmp, loop_js):
    fx = json.loads((FIX / "six_blocks.json").read_text(encoding="utf-8"))
    nonce = hashlib.sha1(os.urandom(8)).hexdigest()[:8]
    cmds = [c.replace("{N}", nonce) for c in fx["commands"]]
    descs = [{"cmd": c, "chain": fx["chain"]} for c in cmds]
    b = node_run(tmp, loop_js, {"op": "select", "descs": descs})
    if b["selected"] != list(range(6)) or len(set(b["keys"])) != 6:
        return "FAIL", "selectBlocks gave %s, %d distinct keys (want 0..5, 6)" % (b["selected"], len(set(b["keys"])))
    off = a.audit_size()
    outs = []
    for c in cmds:
        st, r = a.run(c)
        outs.append((st, r.get("exit"), str(r.get("out", ""))))
    if not all(s == 200 and e == 0 and ("E1-%s-%d" % (nonce, i + 1)) in o for i, (s, e, o) in enumerate(outs)):
        return "FAIL", "agent answers: " + str([(s, e) for s, e, _ in outs])
    ev = a.audit_since(off)
    if ev is None:
        return "FAIL", "audit.jsonl not found at " + a.audit
    counts = [sum(1 for x in ev if ("E1-%s-%d" % (nonce, i + 1)) in str(x.get("cmd", "")) and not x.get("dry")) for i in range(6)]
    return ("PASS" if counts == [1] * 6 else "FAIL"), "tier B 6 selected, 6 keys; tier A audit non-dry runs per nonce %s" % counts


def e2(tmp, loop_js):
    p = Desc()
    p.feed((FIX / "deepseek_reply.html").read_text(encoding="utf-8"))
    descs = [{"cmd": d["cmd"], "chain": d["chain"]} for d in p.out]
    b = node_run(tmp, loop_js, {"op": "select", "descs": descs})
    texts = b["texts"]
    if len(p.out) != 6 and len(p.out) != 4:
        return "FAIL", "fixture parse gave %d blocks" % len(p.out)
    thinking = [i for i, d in enumerate(p.out) if any("think" in c["cls"] for c in d["chain"])]
    if thinking != b["ignored"] or not texts or any(i in thinking for i in b["selected"]) or len(thinking) != 2:
        return "FAIL", "selected=%s ignored=%s (want exactly the 2 thinking-panel drafts ignored)" % (b["selected"], b["ignored"])
    d = node_run(tmp, loop_js, {"op": "dup", "texts": ["x", "y", "x"]})["dup"]
    if d != [0, 0, 1]:
        return "FAIL", "dupOf(x,y,x)=%s want [0,0,1]" % d
    return "PASS", "2 thinking drafts ignored, %d answer blocks selected; duplicate in answer -> block 1" % len(texts)


def e3(a):
    nonce = hashlib.sha1(os.urandom(6)).hexdigest()[:6]
    cwd = a.cwd
    plans = [
        ("a native exit 1 then EXIT_CODE line", [{"name": "s", "cmd": "python -c \"import sys; sys.exit(1)\"; Write-Output 'EXIT_CODE=1'", "cwd": cwd}]),
        ("b native exit 1 after output", [{"name": "s", "cmd": "python -c \"import sys; print('x'); sys.exit(1)\"", "cwd": cwd}]),
        ("c no summary, expect missing", [{"name": "s", "cmd": "Write-Output 'step 1/3'; Write-Output 'step 2/3'", "cwd": cwd, "expect": "ALL TESTS PASSED"}]),
    ]
    bad = []
    for name, steps in plans:
        st, r = a.task(steps)
        out = str(r.get("out", ""))
        if not (st == 200 and r.get("exit") not in (0, None) and "TASK RESULT: FAIL" in out):
            bad.append("%s: http=%s exit=%s fail-line=%s" % (name, st, r.get("exit"), "TASK RESULT: FAIL" in out))
    st, r = a.task([{"name": "s", "cmd": "Write-Output ok-" + nonce, "cwd": cwd}])
    if not (st == 200 and r.get("exit") == 0 and "TASK RESULT: PASS" in str(r.get("out", ""))):
        bad.append("control Write-Output: http=%s exit=%s" % (st, r.get("exit")))
    st, r = a.run("This-Is-A-Fake-Command")
    if not (st == 200 and r.get("exit") == 0):
        bad.append("fake command (documented exit 0): http=%s exit=%s" % (st, r.get("exit")))
    return ("FAIL", "; ".join(bad)) if bad else ("PASS", "3 failing plans -> exit!=0 + TASK RESULT: FAIL; control PASS; fake command exit 0 (documented)")


def e4(tmp, loop_js):
    fx = json.loads((FIX / "dropped_generation.json").read_text(encoding="utf-8"))
    r = node_run(tmp, loop_js, {"op": "watch", "events": fx["events"]})
    acts = r["actions"]
    notice = [t for t, k in acts if k == "notice"]
    stop = [t for t, k in acts if k == "stop"]
    if not notice or notice[0] > fx["notice_by_s"] or not stop or stop[0] <= notice[0]:
        return "FAIL", "actions %s (want notice <= %d s then stop)" % (acts, fx["notice_by_s"])
    if not r.get("status"):
        return "FAIL", "pump-deadline status empty (silence)"
    return "PASS", "notice at %ss, stop at %ss; pump status: %s" % (notice[0], stop[0], r["status"][:60])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default="F:/AIBridge")
    ap.add_argument("--target", choices=["scratch", "installed"], default="scratch")
    ap.add_argument("--payload", default=str(REPO / "scripts" / "aibridge"))
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--out", default="")
    ns = ap.parse_args()
    installed = ns.target == "installed"
    root = Path(ns.root) if installed else None
    payload = Path(ns.payload)
    utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rows = Rows()
    scratch = None
    if installed:
        tmp = root / "run" / "e2e" / utc
        loop_js = root / "extension" / "loop.js"
    else:
        tmp = Path(ns.out) / utc if ns.out else Path(tempfile.mkdtemp(prefix="e2e_bridge_"))
        loop_js = payload / "extension" / "loop.js"
    tmp.mkdir(parents=True, exist_ok=True)
    version = "?"
    try:
        if installed:
            a = Agent(root=root)
        else:
            import aibridge_scratch
            aibridge_scratch.PAYLOAD = payload
            scratch = aibridge_scratch.Scratch()
            a = Agent(scratch=scratch)
        try:
            pv = a.ping()
            version = str(pv.get("version") or pv.get("agent") or "?")
        except Exception:
            version = release_current(payload)
        case(rows, "E0", lambda: e0(a, payload, root))
        case(rows, "E1", lambda: e1(a, tmp, loop_js))
        case(rows, "E2", lambda: e2(tmp, loop_js))
        case(rows, "E3", lambda: e3(a))
        case(rows, "E4", lambda: e4(tmp, loop_js))
        rows.add("E5", "NOT_CHECKED", "live DeepSeek chat needs a Chrome-capable session (card dsabr-c7); --live only records the request" if ns.live
                 else "live DeepSeek chat not requested (use --live from a Chrome-capable session)")
    except Exception as e:
        rows.add("E0", "FAIL", "agent start/connect failed: %s" % str(e)[:300])
    finally:
        if scratch:
            scratch.close()
    done = {r["case"] for r in rows.rows}
    for n in ("E0", "E1", "E2", "E3", "E4", "E5"):
        if n not in done:
            rows.add(n, "FAIL", "not run (earlier error)")
    fails = [r["case"] for r in rows.rows if r["verdict"] == "FAIL"]
    rep = {"bridge_version": version, "target": ns.target, "payload": str(payload), "utc": utc, "ok": not fails, "cases": rows.rows}
    try:
        (tmp / "report.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
    except Exception:
        pass
    if ns.json:
        print(json.dumps(rep, indent=1))
    else:
        print("bridge %s: %s" % (version, "ALL PASS" if not fails else "FAIL " + ",".join(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
