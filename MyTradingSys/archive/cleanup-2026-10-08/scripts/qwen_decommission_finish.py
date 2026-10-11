import sys, hashlib, subprocess, shutil
sys.dont_write_bytecode = True
from pathlib import Path
ROOT = Path(r"C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed")
BACKUP = ROOT / "backup_session"
BACKUP.mkdir(exist_ok=True)

def backup(rel):
    src = ROOT / rel
    (BACKUP / Path(rel).name).write_bytes(src.read_bytes())

def edit(rel, pairs):
    p = ROOT / rel
    backup(rel)
    before = p.read_bytes()
    hb = hashlib.sha256(before).hexdigest()[:8]
    text = before.decode("utf-8")
    for name, anchor, repl in pairs:
        c = text.count(anchor)
        print("  [%s] count=%d" % (name, c))
        if c != 1:
            raise SystemExit("ABORT %s: %s c=%d" % (rel, name, c))
        text = text.replace(anchor, repl)
    p.write_bytes(text.encode("utf-8"))
    after = p.read_bytes()
    ha = hashlib.sha256(after).hexdigest()[:8]
    na = sum(1 for c in text if ord(c) > 127)
    print("  => %s: %s -> %s, %d -> %d b, nonascii=%d" % (rel, hb, ha, len(before), len(after), na))

print("=== T049 item doc ===")
edit("MyTradingSys/items/T049_nuc_worker_v2.md", [
 ("status",
  "OPEN. Phase 2 complete 2026-09-26:",
  "CLOSED 2026-10-01 (Qwen decommissioned; AIBridge on desktop replaces the run-command surface). Phase 2 complete 2026-09-26:"),
])

print("=== B082 item doc ===")
edit("MyTradingSys/items/B082_qwen_feeder_missing.md", [
 ("status",
  "Opened 2026-10-01. Status OPEN. Severity MED.",
  "Opened 2026-10-01. Status CLOSED 2026-10-01. Severity MED."),
 ("decision",
  "Operator. No action taken.",
  "2026-10-01: task deleted; Qwen decommissioned."),
])

print("=== archive underscore duplicates if identical to dash ===")
SPECS = ROOT / "MyTradingSys/research/fast_track_2026-09-27/nuc_specs"
ARCH  = SPECS / "_archive_2026-10-01"
ARCH.mkdir(exist_ok=True)
pairs = [
 ("2102-dsa-recon-fabio-lqvv5xgy_ik.md", "2102-dsa-recon-fabio-lqvv5xgy-ik.md"),
 ("2108-dsa-recon-tom-wq_oadz-pj8.md",   "2108-dsa-recon-tom-wq-oadz-pj8.md"),
 ("2113-dsa-recon-tom-zawex_trufe.md",   "2113-dsa-recon-tom-zawex-trufe.md"),
]
for old, new in pairs:
    po = SPECS / old; pn = SPECS / new
    if not po.exists():
        print("  skip (missing): %s" % old); continue
    if not pn.exists():
        print("  keep (no replacement): %s" % old); continue
    ho = hashlib.sha256(po.read_bytes()).hexdigest()
    hn = hashlib.sha256(pn.read_bytes()).hexdigest()
    if ho == hn:
        shutil.move(str(po), str(ARCH / old))
        print("  archived identical: %s" % old)
    else:
        print("  kept (differs): %s" % old)

print("DONE")