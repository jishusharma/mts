"""Item 1: run fix tests against pre-fix code. Builds trees under scratch, never touches the repo."""
import io, os, subprocess, sys, tarfile, shutil

R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
S = os.path.join(os.environ.get("TEMP", "."), "wave1_prefix_check")
PATCH = os.path.join(R, r"MyTradingSys\research\fast_track_2026-09-27\review\fix3_diff.patch")


def export(rev, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    os.makedirs(dest)
    data = subprocess.run(["git", "-C", R, "archive", rev, "MyTradingSys/execution"], capture_output=True, check=True).stdout
    tarfile.open(fileobj=io.BytesIO(data)).extractall(dest)
    return os.path.join(dest, "MyTradingSys", "execution")


def show(rev, path):
    return subprocess.run(["git", "-C", R, "show", f"{rev}:{path}"], capture_output=True, check=True).stdout


def pytest(cwd, target, k=None):
    cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", target]
    if k:
        cmd += ["-k", k]
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    lines = p.stdout.strip().splitlines()
    fails = [l for l in lines if l.startswith("FAILED") or l.startswith("ERROR")]
    return p.returncode, (lines[-1] if lines else p.stderr[-300:]), fails


which = sys.argv[1]
if which == "fix3":
    post = export("03bd84035", os.path.join(S, "post"))
    pre = export("03bd84035", os.path.join(S, "pre"))
    # reverse the FIX3 patch: patch headers name deribit_orders.py / *.new; trunk files have no .new
    txt = open(PATCH, encoding="utf-8").read()
    for f in ["executor", "position_manager", "kill_switch", "daily_loss_monitor"]:
        txt = txt.replace(f"{f}.py.new.pre_fix3", f"{f}.py").replace(f"{f}.py.new\t", f"{f}.py\t")
    txt = txt.replace("+++ deribit_orders.py.new", "+++ deribit_orders.py")
    p = subprocess.run(["patch", "-R", "-p0", "--no-backup-if-mismatch"], input=txt, cwd=pre, capture_output=True, text=True)
    print("patch rc", p.returncode, p.stdout[-600:], p.stderr[-300:])
    for d, name in [(post, "POST-FIX c4c55076c (tree 03bd84035)"), (pre, "PRE-FIX (FIX3 reversed)")]:
        for k in ["C1", "C2", "C3"]:
            rc, last, fails = pytest(d, "testnet/offline/test_fix3_offline.py", k)
            print(f"{name} {k}: rc={rc} {last}")
            for f in fails:
                print("   ", f[:160])
elif which == "b1":
    post = export("0ef6f946d", os.path.join(S, "b1post"))
    pre = export("0ef6f946d", os.path.join(S, "b1pre"))
    open(os.path.join(pre, "kill_switch.py"), "wb").write(show("0ef6f946d^", "MyTradingSys/execution/kill_switch.py"))
    for d, name in [(post, "POST-FIX 0ef6f946d"), (pre, "PRE-FIX kill_switch@0ef6f946d^")]:
        rc, last, fails = pytest(d, "test_premainnet1_offline.py")
        print(f"{name}: rc={rc} {last}")
        for f in fails:
            print("   ", f[:160])
