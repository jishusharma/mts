"""lookahead_lint: pattern unit tests on synthetic snippets, plus the repo gate (no NEW unreviewed FAIL hit).

The gate part is what makes `run_all_tests.py --quick` fail when a research or backtest script adds a look-ahead signature that is not
in scripts/dev/lookahead_allowlist.tsv. To clear it: fix the code, or review the hit and add a row with the real reason
(`python scripts/dev/lookahead_lint.py --new` lists them; `--update-baseline` writes them as "pre-existing, unreviewed").
"""
import functools
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "dev"))

import lookahead_lint as L  # noqa: E402


def hits(src, rel="MyTradingSys/research/x/s.py"):
    return [(h.line, h.pattern, h.severity) for h in L.scan_source(textwrap.dedent(src), rel)]


# ---------------------------------------------------------------- rolling(center=True)
def test_rolling_center_true_is_fail():
    assert hits("y = df.c.rolling(5, center=True).mean()\n") == [(1, "rolling-center", "FAIL")]


def test_rolling_center_false_or_default_is_clean():
    assert hits("y = df.c.rolling(5).mean()\nz = df.c.rolling(5, center=False).mean()\n") == []


# ---------------------------------------------------------------- shift(-k)
def test_shift_negative_is_fail_outside_fwd_names():
    assert hits("df['x'] = df.c.shift(-3)\n") == [(1, "shift-negative", "FAIL")]
    assert hits("y = df.c.shift(periods=-1)\n") == [(1, "shift-negative", "FAIL")]
    assert hits("y = np.roll(a, -2)\n") == [(1, "shift-negative", "FAIL")]
    assert hits("k = 4\ny = df.c.shift(-k)\n") == [(2, "shift-negative", "FAIL")]


def test_shift_negative_allowed_in_fwd_outcome_ret_exit_names():
    for tgt in ("df['fwd_ret']", "fwd", "outcome_px", "exit_price", "df['ret_5']", "forward_close"):
        assert hits(f"{tgt} = df.c.shift(-5)\n") == [], tgt
    assert hits("df = df.assign(fwd=df.c.shift(-5))\n") == []
    assert hits("def outcome(df):\n    return df.c.shift(-5)\n") == []


def test_exemption_is_by_token_not_substring():
    # 'retest' and 'extreme' contain ret / exit-like letters but are not fwd/outcome/ret/exit tokens
    assert hits("retest = df.c.shift(-1)\n") == [(1, "shift-negative", "FAIL")]


def test_shift_positive_is_clean():
    assert hits("y = df.c.shift(1)\nz = df.c.shift(periods=3)\n") == []


# ---------------------------------------------------------------- x[i+k]
def test_forward_index_is_fail_outside_fwd_names():
    assert hits("v = c[i + 1]\n") == [(1, "fwd-index", "FAIL")]
    assert hits("v = df.iloc[i + k]\n") == [(1, "fwd-index", "FAIL")]
    assert hits("seg = c[i + 1:]\n") == [(1, "fwd-index", "FAIL")]
    assert hits("seg = c[i:i + 25]\n") == [(1, "fwd-index", "FAIL")]


def test_chunk_and_text_window_slices_are_clean():
    # chunking a list by a named size constant: idx[a:a + CH] is a batch, not a read past the decision bar
    assert hits("part = idx[a:a + CH]\n") == []
    assert hits("for a in range(0, n, CHUNK):\n    part = idx[a:a + CHUNK]\n") == []
    # a text window handed to a regex is string parsing, not a price series
    assert hits("m = re.search(pat, t[q - 400:q + 600])\n") == []
    assert hits("rows = pat.findall(txt[q:q + 600])\n") == []


def test_real_forward_reads_still_fail_next_to_the_exemptions():
    assert hits("sig = c[i + 1] - c[i]\n") == [(1, "fwd-index", "FAIL")]
    assert hits("x = c[i:i + H]\n") == [(1, "fwd-index", "FAIL")]
    assert hits("m = f(c[i - 5:i + 600])\n") == [(1, "pivot-right-neighbour", "FAIL")]   # same window, not handed to a regex
    assert hits("part = idx[a + 1:a + CH]\n") == [(1, "fwd-index", "FAIL")]


def test_forward_index_allowed_in_outcome_names():
    assert hits("fwd = c[i + 1]\n") == []
    assert hits("exit_px = c[t + h]\n") == []
    assert hits("def outcome(c, t):\n    return c[t + 24]\n") == []
    assert hits("v = fwd_close[i + 1]\n") == []


def test_causal_slices_are_clean():
    assert hits("a = c[:i + 1]\nb = c[i - 5:i + 1]\nd = c[i - 1]\ne = c[i]\nf = c[i - w:i]\n") == []


# ---------------------------------------------------------------- pivots
def test_pivot_with_right_neighbour_is_fail():
    src = "sh = [b[i]['h'] for i in prev if b[i]['h'] >= b[i - 1]['h'] and b[i]['h'] >= b[i + 1]['h']]\n"
    assert hits(src) == [(1, "pivot-right-neighbour", "FAIL")]       # the i+1 read is not double counted as fwd-index


def test_centered_window_pivot_is_fail():
    assert hits("ok = H[k] == max(H[k - w:k + w + 1])\n") == [(1, "pivot-right-neighbour", "FAIL")]


def test_left_only_pivot_is_clean():
    assert hits("ok = H[i] > H[i - 1] and H[i] > H[i - 2]\n") == []


# ---------------------------------------------------------------- quantiles
def test_fullsample_quantile_is_warn():
    assert hits("lo, hi = np.quantile(s[ok], [0.33, 0.67])\n") == [(1, "fullsample-quantile", "WARN")]
    assert hits("b = pd.qcut(df.x, 3)\n") == [(1, "fullsample-quantile", "WARN")]
    assert hits("t = np.percentile(x, 90)\n") == [(1, "fullsample-quantile", "WARN")]
    assert hits("t = df.x.quantile(0.9)\n") == [(1, "fullsample-quantile", "WARN")]


def test_windowed_quantile_is_clean():
    assert hits("t = df.x.rolling(50).quantile(0.9)\nu = df.x.expanding(50).quantile(0.9)\n") == []
    assert hits("t = np.percentile(x[i - 50:i], 90)\n") == []


def test_pivot_function_is_warn():
    assert hits("from scipy.signal import argrelextrema\nk = argrelextrema(h, np.greater, order=3)\n") == [(2, "pivot-function", "WARN")]


def test_parse_error_is_warn_not_crash():
    assert hits("def (:\n")[0][1:] == ("parse-error", "WARN")


# ---------------------------------------------------------------- allowlist
def test_allowlist_matches_by_text_not_line_number():
    src = "v = c[i + 1]\n"
    h1 = L.scan_source(src, "MyTradingSys/research/x/s.py")
    h2 = L.scan_source("\n\n# moved down\n" + src, "MyTradingSys/research/x/s.py")
    allow = {h1[0].key: "reviewed: entry at next open"}
    L.apply_allowlist(h2, allow)
    assert h2[0].line == 4 and h2[0].allowlisted and h2[0].reason == "reviewed: entry at next open"
    other = L.scan_source("w = c[j + 1]\n", "MyTradingSys/research/x/s.py")
    L.apply_allowlist(other, allow)
    assert not other[0].allowlisted                                  # different text = new hit


def test_summary_counts_come_from_hit_objects():
    hs = L.scan_source("a = c[i + 1]\nlo = np.quantile(x, .5)\nb = d[j + 1]\n", "f.py")
    allow = {hs[0].key: "r"}
    L.apply_allowlist(hs, allow)
    s = L.summarize(hs, allow | {("gone.py", "fwd-index", "x"): "stale"})
    assert (s["hits"], s["FAIL"], s["WARN"], s["FAIL_new"], s["FAIL_allowlisted"], s["WARN_new"], s["stale_allowlist_rows"]) == (3, 2, 1, 1, 1, 1, 1)


def test_allowlist_roundtrip(tmp_path):
    p = tmp_path / "a.tsv"
    L.write_allowlist({("f.py", "fwd-index", "v = c[i + 1]"): "why"}, p)
    assert L.load_allowlist(p) == {("f.py", "fwd-index", "v = c[i + 1]"): "why"}
    assert b"\r" not in p.read_bytes()


# ---------------------------------------------------------------- the repo
@functools.lru_cache(maxsize=1)
def _repo():
    allow = L.load_allowlist()
    hs = L.apply_allowlist(L.scan_tree(), allow)
    return hs, allow


def test_repo_has_no_new_unreviewed_fail_hits():
    hs, _ = _repo()
    new = [f"{h.file}:{h.line} {h.pattern}  {h.text[:80]}" for h in hs if h.severity == "FAIL" and not h.allowlisted]
    assert not new, ("new look-ahead FAIL hits, fix them or review and add to scripts/dev/lookahead_allowlist.tsv:\n  " + "\n  ".join(new))


def test_allowlist_rows_all_carry_a_reason():
    _, allow = _repo()
    assert allow and all(r.strip() for r in allow.values())


def test_known_hits_are_found_with_the_documented_severity():
    hs, _ = _repo()
    by = {(h.file, h.line): h for h in hs}
    opr = "MyTradingSys/research/opr_preopen_tops_2026-10-16/study.py"
    for ln in (68, 130):
        h = by[(opr, ln)]
        assert (h.pattern, h.severity) == ("fullsample-quantile", "WARN") and "OURS-on-DEV" in (h.reason or "")
    beta = by[("MyTradingSys/research/setup_alpha_beta_2026-10-10/beta_sweep.py", 177)]
    assert (beta.pattern, beta.severity) == ("pivot-right-neighbour", "FAIL") and beta.allowlisted


def test_other_sessions_dirs_are_not_scanned():
    files = {rel for _, rel in L.iter_files()}
    assert not any("pit_levels_2026-10-16" in f or "context_null_2026-10-16" in f for f in files)
    assert any(f.startswith("MyTradingSys/backtest/") for f in files) and any(f.startswith("MyTradingSys/research/") for f in files)
