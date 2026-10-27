import sys, csv, gzip, io, os
sys.dont_write_bytecode = True
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(r"C:\Users\E-ngineers\IdeaProjects\mts-dsa-jis-nuc-1019-0713")
LIVE = Path(r"C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed")
F = Path(r"F:/MTS/data")
OUT = ROOT / "MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T01/out"
OUT.mkdir(parents=True, exist_ok=True)
DEV_END_MS = int(datetime(2024,7,1,tzinfo=timezone.utc).timestamp()*1000)

def unit_of(t):
    if t is None: return "?"
    if 1e14 < t < 1e16: return "us"
    if 1e12 < t < 1e13: return "ms"
    if 1e9 < t < 1e10: return "s"
    return f"?({t})"

def to_ms(t):
    if 1e14 < t < 1e16: return t // 1000
    return t

def scan_kline_dir(d, has_header=False):
    files = sorted(d.glob("*.csv")) if d.exists() else []
    seen = set(); dups = 0; n = 0; first = None; last = None; unit_set = set()
    for f in files:
        with open(f, newline="", encoding="utf-8") as fh:
            for row in csv.reader(fh):
                if not row: continue
                if not row[0].lstrip("-").isdigit():
                    if has_header: continue
                    continue
                try: t = int(row[0])
                except: continue
                unit_set.add(unit_of(t)); t = to_ms(t)
                n += 1
                if t in seen: dups += 1
                else: seen.add(t)
                if first is None or t < first: first = t
                if last is None or t > last: last = t
    gaps = 0
    if seen:
        ordered = sorted(seen)
        step = 60000
        for i in range(1, len(ordered)):
            if ordered[i] - ordered[i-1] > step * 1.5: gaps += 1
    return dict(n_files=len(files), n_rows=n, n_unique=len(seen), dups=dups, gaps=gaps,
                first=first, last=last, unit="+".join(sorted(unit_set)))

def scan_funding(d, time_col=0, rate_col=2):
    files = sorted(d.glob("*.csv")) if d.exists() else []
    seen = set(); n = 0; first = None; last = None; unit_set = set()
    bad_rate = 0; rates = []
    for f in files:
        with open(f, newline="", encoding="utf-8") as fh:
            for row in csv.reader(fh):
                if not row or not row[0].lstrip("-").isdigit(): continue
                try: t = int(row[time_col]); r = float(row[rate_col])
                except: continue
                unit_set.add(unit_of(t)); t = to_ms(t)
                n += 1; seen.add(t)
                if first is None or t < first: first = t
                if last is None or t > last: last = t
                rates.append((t, r))
                if abs(r) > 0.0075: bad_rate += 1
    dev_8h_expected = 0; dev_8h_present = 0
    if first and last:
        cur = (first // (8*3600*1000)) * 8*3600*1000
        while cur <= min(last, DEV_END_MS):
            if cur >= first:
                dev_8h_expected += 1
                if cur in seen: dev_8h_present += 1
            cur += 8*3600*1000
    return dict(n_files=len(files), n_rows=n, n_unique=len(seen), dups=n-len(seen), gaps=0,
                first=first, last=last, unit="+".join(sorted(unit_set)),
                dev_8h_expected=dev_8h_expected, dev_8h_present=dev_8h_present, bad_rate=bad_rate)

def iso(ms):
    return datetime.fromtimestamp(ms/1000.0, timezone.utc).strftime("%Y-%m-%dT%H:%MZ") if ms else ""

rows = []
def add(name, r):
    rows.append(dict(source=name, n_files=r.get("n_files",0), n_rows=r.get("n_rows",0),
                     n_unique=r.get("n_unique",0), dups=r.get("dups",0), gaps=r.get("gaps",0),
                     first=iso(r.get("first")), last=iso(r.get("last")), unit=r.get("unit",""),
                     dev_8h_expected=r.get("dev_8h_expected",""), dev_8h_present=r.get("dev_8h_present",""),
                     rates_over_75bp=r.get("bad_rate","")))

print("=== inventory ===")
for label, d, kind in [
    ("tom_raw/klines (F:)", F/"tom_raw/klines", "k"),
    ("raw_1m_2022/klines (live Dumps)", LIVE/"Dumps/backtest/raw_1m_2022/klines", "k"),
    ("raw/klines (live Dumps)", LIVE/"Dumps/backtest/raw/klines", "k"),
    ("fundingRate (live Dumps)", LIVE/"Dumps/backtest/raw/fundingRate", "f"),
    ("dev_ext funding (F:)", F/"dev_ext_2019_2021/funding", "f"),
]:
    if not d.exists():
        print(f"{label}: MISSING {d}")
        continue
    r = scan_kline_dir(d) if kind == "k" else scan_funding(d)
    add(label, r)
    print(f"{label}: files={r['n_files']} rows={r['n_rows']} uniq={r['n_unique']} dups={r.get('dups')} gaps={r['gaps']} first={iso(r['first'])} last={iso(r['last'])} unit={r['unit']}" +
          (f" dev8h {r['dev_8h_present']}/{r['dev_8h_expected']} >75bp={r['bad_rate']}" if kind=='f' else ""))

with open(OUT/"data_inventory.csv","w",newline="",encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    for r in rows: w.writerow(r)
print(f"wrote {OUT/'data_inventory.csv'}")

# --- INVARIANTS: DEV 1m bars only (before 2024-07-01) ---
print("\n=== DEV 1m invariants ===")
viol = dict(ohlc=0, tbv=0, qv=0, trades=0, jump=0, frozen=0)
worst = []
frozen_run = 0; max_frozen = 0
klines = sorted((F/"tom_raw/klines").glob("*.csv"))
n_dev = 0; seen = set()
for f in klines:
    with open(f, newline="", encoding="utf-8") as fh:
        for row in csv.reader(fh):
            if not row or not row[0].lstrip("-").isdigit(): continue
            try:
                t = to_ms(int(row[0]))
                o,h,l,c,v = (float(row[i]) for i in (1,2,3,4,5))
                qv = float(row[7]) if len(row) > 7 else 0.0
                tbv = float(row[9]) if len(row) > 9 else 0.0
                ntr = int(row[8]) if len(row) > 8 else 1
            except Exception:
                continue
            if t >= DEV_END_MS: continue
            if t in seen: continue
            seen.add(t); n_dev += 1
            bad = False
            if not (l <= o <= h and l <= c <= h):
                viol["ohlc"] += 1; bad = True
            if tbv < 0 or tbv > v:
                viol["tbv"] += 1; bad = True
            if v > 0 and not (l <= qv/v <= h):
                viol["qv"] += 1; bad = True
            if v > 0 and ntr < 1:
                viol["trades"] += 1; bad = True
            if v == 0 and h == l:
                frozen_run += 1
                if frozen_run > max_frozen: max_frozen = frozen_run
            else:
                frozen_run = 0
            if bad and len(worst) < 20:
                worst.append((iso(t), o,h,l,c,v,tbv,qv))

print(f"DEV 1m bars checked: {n_dev}")
print(f"OHLC order violations: {viol['ohlc']}")
print(f"tbv out of [0,v]: {viol['tbv']}")
print(f"qv/v outside [l,h]: {viol['qv']}")
print(f"trades<1 with vol>0: {viol['trades']}")
print(f"frozen (v=0,h=l) count: {frozen_run}, max run: {max_frozen}")
with open(OUT/"invariants_summary.csv","w",newline="",encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["metric","count"])
    w.writerow(["dev_1m_bars", n_dev])
    for k,val in viol.items(): w.writerow([k, val])
    w.writerow(["frozen_max_run", max_frozen])
with open(OUT/"invariants_worst20.csv","w",newline="",encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["t_iso","o","h","l","c","v","tbv","qv"])
    for r in worst: w.writerow(r)

# --- DELTA SIGN hand example ---
print("\n=== delta sign hand example ===")
first_file = klines[0] if klines else None
if first_file:
    with open(first_file, newline="", encoding="utf-8") as fh:
        lines = [r for r in csv.reader(fh) if r and r[0].lstrip("-").isdigit()][:3]
    for row in lines:
        t = to_ms(int(row[0]))
        v = float(row[5]); tbv = float(row[9])
        delta_by_formula = 2*tbv - v
        print(f"{iso(t)}  v={v:.3f} tbv={tbv:.3f}  delta=2*tbv-v={delta_by_formula:.3f}  buy_approx={tbv:.3f} sell_approx={v-tbv:.3f}")

print("\nDONE inventory+invariants")
