"""Lane-like load for Defender / service CPU checks: N workers churn small files and spawn git, python and node.

  python scripts/operator/cpu_stress.py [seconds=40] [workers=8]

Samples every 5 s while the load runs and prints one table: total CPU, MsMpEng, PcaSvc host, top 5 processes.
Writes only under F:\\MTS\\scratch\\cpu_audit (falls back to the temp dir). Reads the repo only through `git status`.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

SECONDS = int(sys.argv[1]) if len(sys.argv) > 1 else 40
WORKERS = int(sys.argv[2]) if len(sys.argv) > 2 else 8
ROOT = r"F:\MTS\scratch\cpu_audit" if os.path.isdir(r"F:\MTS\scratch") else tempfile.gettempdir()
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def churn(i, end):
    d = os.path.join(ROOT, f"stress_{i}")
    os.makedirs(d, exist_ok=True)
    n = 0
    while time.time() < end:
        for k in range(60):                      # pytest-like: many small .py/.pyc files written and read
            p = os.path.join(d, f"t{k}.py")
            with open(p, "w", newline="\n") as f:
                f.write("x = %d\n" % (n * k))
            with open(p) as f:
                f.read()
        subprocess.run(["git", "-C", REPO, "status", "--short", "-uno"], capture_output=True)
        subprocess.run([sys.executable, "-c", "import json,os,sys;print(len(os.listdir('.')))"], capture_output=True, cwd=d)
        n += 1
    shutil.rmtree(d, ignore_errors=True)
    return n


def sample():
    ps = ("$a=Get-Process|%{[pscustomobject]@{I=$_.Id;N=$_.Name;C=$_.CPU}};Start-Sleep 4;"
          "$t=(Get-Counter '\\Processor(_Total)\\% Processor Time').CounterSamples.CookedValue;"
          "$r=Get-Process|%{$p=$_;$x=$a|?{$_.I -eq $p.Id};if($x -and $x.C -ne $null -and $p.CPU -ne $null){"
          "[pscustomobject]@{N=$p.Name;D=($p.CPU-$x.C)/4}}}|Group N|%{[pscustomobject]@{N=$_.Name;D=($_.Group|measure D -sum).Sum}}|sort D -desc|select -first 6;"
          "$m=(Get-Counter '\\Process(MsMpEng)\\% Processor Time').CounterSamples.CookedValue/100;"
          "'{0:N0}|{1:N2}|{2}' -f $t,$m,(($r|%{'{0}={1:N2}' -f $_.N,$_.D}) -join ' ')")
    out = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True).stdout.strip()
    return out


end = time.time() + SECONDS
print("t(s)  total%  MsMpEng(core)  top processes (core-seconds/s)")
t0 = time.time()
with ThreadPoolExecutor(WORKERS + 1) as ex:
    futs = [ex.submit(churn, i, end) for i in range(WORKERS)]
    while time.time() < end - 4:
        print("%4d  %s" % (time.time() - t0, sample().replace("|", "  ")), flush=True)
    done = sum(f.result() for f in futs)
print("rounds completed (throughput, higher is better):", done)
