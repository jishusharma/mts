COUNTS: MATCH=10 DIFF=0 NOT_IN_DATA=0

# Audit Report: `YT_PROXY.md` vs `fetch_captions_timed.py` and Tests

- **Card**: `gemini-doc-scan-yt-proxy-vs-fetch-captions-1111`
- **Auditor**: Gemini 3.8 Flash (Low)
- **Date**: 2026-11-11
- **Scope In**:
  - `MyTradingSys/system/YT_PROXY.md` (read)
  - `scripts/dev/fetch_captions_timed.py` (read)
  - `scripts/dev/test_yt_proxy.py` (read)
  - `scripts/dev/test_fetch_captions_guard.py` (read)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-doc-scan-yt-proxy-vs-fetch-captions-1111.md` (new)
- **Scope Out**: Read-only audit; no edits to source files, no live-tree edit, no deploy, no `.secrets` or `.env` read.

---

## 1. Summary of Scan

Evaluated 10 testable claims from `MyTradingSys/system/YT_PROXY.md` (lines 14, 18-24) against `scripts/dev/fetch_captions_timed.py` and test suites `scripts/dev/test_yt_proxy.py` and `scripts/dev/test_fetch_captions_guard.py`:
1. `wireproxy.conf` detection and default SOCKS address (`127.0.0.1:40000`).
2. SOCKS proxy routing for YouTube requests via yt-dlp.
3. SOCKS proxy routing for ipify public IP check.
4. Auto-start of wireproxy subprocess when port is closed.
5. Termination of wireproxy subprocess after execution.
6. Fail closed on proxy down / unreachable with exit code 2 (never fallback to direct/home IP).
7. Environment variable override via `YT_PROXY=<url>` and `YT_PROXY=off` for direct connection.
8. Maximum limit of 5 videos per run.
9. Escalating lockout intervals of 6 h, 24 h, and 72 h upon consecutive HTTP 429 errors.
10. Rolling 24 h request budgets: 150 requests on proxy exit, 40 on direct IP, overridable by `YT_DAILY_BUDGET`.

Audit outcome across 10 claims:
- **MATCH (10)**: All 10 claims from `YT_PROXY.md` precisely match the implementation in `scripts/dev/fetch_captions_timed.py` and are verified by test suites `scripts/dev/test_yt_proxy.py` and `scripts/dev/test_fetch_captions_guard.py`.
- **DIFF (0)**: None.
- **NOT_IN_DATA (0)**: None.

---

## 2. Clause Comparison Table

| # | YT_PROXY.md Claim | Code Implementation | Status | Audit Findings & Verification |
|---|---|---|---|---|
| 1 | `YT_PROXY.md:14,18-19`: `wireproxy.conf`: `BindAddress = 127.0.0.1:40000` / `fetch_captions_timed.py ... sees ~/.mts/ytproxy/wireproxy.conf and sends every YouTube call plus the ipify check through socks5://127.0.0.1:40000` | `scripts/dev/fetch_captions_timed.py:77,134-136`: `PROXY_ADDR = ("127.0.0.1", 40000)` and `if (proxy_dir() / "wireproxy.conf").exists(): return "socks5://%s:%d" % PROXY_ADDR` | MATCH | SOURCED (`YT_PROXY.md:14,18-19`, `scripts/dev/fetch_captions_timed.py:77,124-136`, `scripts/dev/test_yt_proxy.py:38-42`). Code checks `wireproxy.conf` in proxy directory and configures `socks5://127.0.0.1:40000`; verified by `test_config_file_selects_local_warp_port`. |
| 2 | `YT_PROXY.md:18-19`: `sends every YouTube call ... through socks5://127.0.0.1:40000` | `scripts/dev/fetch_captions_timed.py:186-191,540-542,600`: `ydl_opts(opts)` injects `opts["proxy"] = url` into yt-dlp calls; `transcript_api_cues` sets `GenericProxyConfig(http_url=proxy_url(), https_url=proxy_url())` | MATCH | SOURCED (`YT_PROXY.md:18-19`, `scripts/dev/fetch_captions_timed.py:186-191,540-542`, `scripts/dev/test_yt_proxy.py:55-77`). Tested by `test_caption_fetch_passes_proxy_to_ytdlp`, confirming yt-dlp receives `proxy="socks5://127.0.0.1:40000"`. |
| 3 | `YT_PROXY.md:18-19`: `sends every YouTube call plus the ipify check through socks5://127.0.0.1:40000` | `scripts/dev/fetch_captions_timed.py:194-206`: `public_ip()` routes ipify query via `yt_dlp.YoutubeDL(ydl_opts({"quiet": True})).urlopen("https://api.ipify.org")` when proxy is active | MATCH | SOURCED (`YT_PROXY.md:18-19`, `scripts/dev/fetch_captions_timed.py:194-206`). When `proxy_url()` is present, `public_ip()` issues the request through yt-dlp using `ydl_opts()`, ensuring the ipify check runs through the proxy to determine the exit IP. |
| 4 | `YT_PROXY.md:19-20`: `It starts wireproxy for the run if the port is closed` | `scripts/dev/fetch_captions_timed.py:147-173,717`: `ensure_proxy()` checks `_port_open(addr)`, executes `wireproxy.exe` via `subprocess.Popen([str(exe), "-c", str(d / "wireproxy.conf")], ...)` if closed, and polls until open | MATCH | SOURCED (`YT_PROXY.md:19-20`, `scripts/dev/fetch_captions_timed.py:147-173,717`, `scripts/dev/test_yt_proxy.py:87-100`). Verified by `test_wireproxy_started_for_run_and_stopped_after`, confirming subprocess launch when port is initially closed. |
| 5 | `YT_PROXY.md:20`: `and stops it afterwards.` | `scripts/dev/fetch_captions_timed.py:175-184,688-696`: `main()` calls `stop_proxy()` in `finally` block; `stop_proxy()` terminates/kills any processes in `_proxy_proc` | MATCH | SOURCED (`YT_PROXY.md:20`, `scripts/dev/fetch_captions_timed.py:175-184,688-696`, `scripts/dev/test_yt_proxy.py:87-100`). Tested by `test_wireproxy_started_for_run_and_stopped_after` asserting `proc.terminate.assert_called_once()`. |
| 6 | `YT_PROXY.md:20`: `If the proxy is set but down, the run exits 2 and makes no request: it never falls back to the home IP.` | `scripts/dev/fetch_captions_timed.py:76,717-720`: `EXIT_PROXY_DOWN = 2`; `if not a.status and not ensure_proxy(): print(...); return EXIT_PROXY_DOWN` | MATCH | SOURCED (`YT_PROXY.md:20`, `scripts/dev/fetch_captions_timed.py:76,717-720`, `scripts/dev/test_yt_proxy.py:78-86`). Verified by `test_dead_proxy_makes_no_request`, returning exit code 2 without calling `fetch` or `YoutubeDL`. |
| 7 | `YT_PROXY.md:21`: `Env YT_PROXY=<url> overrides the proxy; YT_PROXY=off goes direct.` | `scripts/dev/fetch_captions_timed.py:128-136`: `env = (os.environ.get("YT_PROXY") or "").strip(); if env: return None if env.lower() == "off" else env` | MATCH | SOURCED (`YT_PROXY.md:21`, `scripts/dev/fetch_captions_timed.py:128-136`, `scripts/dev/test_yt_proxy.py:50-54`). Tested by `test_env_off_beats_config` and `test_no_config_is_direct`. |
| 8 | `YT_PROXY.md:22`: `The guard is keyed by the exit IP: 5 videos per run` | `scripts/dev/fetch_captions_timed.py:448-473,712`: `guarded_run` checks `used >= max_videos` (`--max-videos` default 5) and marks extra items `DEFERRED` | MATCH | SOURCED (`YT_PROXY.md:22`, `scripts/dev/fetch_captions_timed.py:448-473,712`, `scripts/dev/test_fetch_captions_guard.py:44-50`). Verified by `test_budget_cap_defers_sixth_video`, confirming 5 calls are fetched and the 6th is deferred. |
| 9 | `YT_PROXY.md:22`: `lockout 6/24/72 h on a 429` | `scripts/dev/fetch_captions_timed.py:69,414-430`: `BLOCK_LEVELS_H = (6, 24, 72)` and `until = _utcnow() + timedelta(hours=BLOCK_LEVELS_H[level - 1])` on `mark_blocked()` | MATCH | SOURCED (`YT_PROXY.md:22`, `scripts/dev/fetch_captions_timed.py:69,414-430,443`, `scripts/dev/test_fetch_captions_guard.py:51-58`). Handled upon HTTP 429 detection; verified in guard tests and status reporting format. |
| 10 | `YT_PROXY.md:22-23`: `150 requests per 24 h on the proxy (OURS: one CBP run uses ~35, 2 runs a day), 40 on a direct IP; env YT_DAILY_BUDGET overrides.` | `scripts/dev/fetch_captions_timed.py:70-72,89-94`: `DAILY_BUDGET = 40`, `DAILY_BUDGET_PROXY = 150`, and `int(os.environ.get("YT_DAILY_BUDGET") or (DAILY_BUDGET_PROXY if proxy_url() else DAILY_BUDGET))` | MATCH | SOURCED (`YT_PROXY.md:22-23`, `scripts/dev/fetch_captions_timed.py:70-72,89-94`, `scripts/dev/test_yt_proxy.py:43-49`). Tested by `test_proxy_exit_gets_larger_daily_budget` asserting 40 direct, 150 on proxy config, and override to 7 via `YT_DAILY_BUDGET`. |
