# YouTube-only proxy (free Cloudflare WARP)

Operator 2026-11-02 (d-yt-warp-proxy): our home IP is YouTube-429 blocked and the old OpenVPN profile's password is lost.
YouTube caption work goes through free Cloudflare WARP instead. Only YouTube traffic uses it: a local SOCKS port, no
system routes, no admin rights, trading traffic untouched.

Tools (open source, Windows amd64, checksums from each GitHub release): `wgcf` (ViRb3/wgcf) makes a free WARP account and
WireGuard profile; `wireproxy` (whyvl/wireproxy) runs that profile as a SOCKS5 proxy in user space.

## Set up a host (once, about 2 minutes)
All files live in `~/.mts/ytproxy/`, outside the repo (the account file holds a private key: never commit it).
1. `gh release download -R ViRb3/wgcf -p "wgcf_*_windows_amd64.exe"` and `gh release download -R whyvl/wireproxy -p "wireproxy_windows_amd64.tar.gz"`, check the sha256 values against each release's checksums.txt, then `tar xzf` wireproxy.
2. `wgcf register --accept-tos` and then `wgcf generate`, which writes `wgcf-profile.conf`.
3. Write `wireproxy.conf`: `WGConfig = <full path>\wgcf-profile.conf`, a blank line, `[Socks5]`, `BindAddress = 127.0.0.1:40000`.
4. Check: `curl --socks5-hostname 127.0.0.1:40000 https://www.cloudflare.com/cdn-cgi/trace` prints `warp=on`.

## How it is used
`scripts/dev/fetch_captions_timed.py`, and CBP through it, sees `~/.mts/ytproxy/wireproxy.conf` and sends every YouTube
call plus the ipify check through `socks5://127.0.0.1:40000`. It starts wireproxy for the run if the port is closed and
stops it afterwards. If the proxy is set but down, the run exits 2 and makes no request: it never falls back to the home IP.
- Env `YT_PROXY=<url>` overrides the proxy; `YT_PROXY=off` goes direct.
- The guard is keyed by the exit IP: 5 videos per run, lockout 6/24/72 h on a 429; 150 requests per 24 h on the proxy
  (OURS: one CBP run uses ~35, 2 runs a day), 40 on a direct IP; env YT_DAILY_BUDGET overrides.
- If WARP's IP gets a 429 as well, the guard locks that address. A new WARP account does NOT change the exit address (measured 2026-11-12 05:50Z), so do not re-register: take the next path below the same turn.

## Never blocked: path order
Operator 2026-11-12: a YouTube caption block must never stop a task. A block on one path means try the next path the same
turn and report only the result. The guard still rules the scripted path: no scripted retry on a locked address.
1. Guarded fetcher through WARP: `fetch_captions_timed.py` (above). Exit 3 / 429 = locked, go to 2.
2. A fleet machine whose address is not locked: `mts_signal.py ask --to <login> --type task` (general rule: only a machine whose own guard record is not locked; the laptop's was locked until 2026-11-13T13:58Z, so it is not an option today). Ask for the video ids; files come back through the repo.
3. The video's transcript panel in Chrome profile "Browser 2" (steps below). Never "Browser 1".
4. A transcript site opened in the same browser tab or by WebFetch: video id only, no account, no personal data.
5. Audio plus local Whisper on the desktop: `scripts/dev/asr_transcribe.py` (ROUTING.md, local ASR on JIS-NB), then `asr_to_canonical.py`.
6. Another exit: phone hotspot or a laptop on another network (one request, paced, guard rules apply there too).
7. Only then one line to the operator asking for a paste.

Rules for every path: fetch once, cache, share through the repo so no machine fetches a video twice; spread fetches over
machines and pace them, never push one address. Gemini "watch the video" is never a quote source. Quotes pass
`python scripts/dev/verify_extract_quotes.py <extract.md>` (exit 0) against the cached caption file.

### Path 3 steps (worked 2026-11-12 for three videos, no sign-in wall; a Haiku can repeat it)
1. One ToolSearch loads the Chrome tools; call `select_browser` for the device named "Browser 2" first; `tabs_context_mcp` with createIfEmpty.
2. `navigate` a new tab to `https://www.youtube.com/watch?v=<id>`. One video at a time. MUTED AND PAUSED (operator hears the audio): right after every navigate run `javascript_tool` `document.querySelectorAll('video').forEach(v=>{v.muted=true;v.pause()})` (repeat once after the page settles, the player may autoplay); never let a video play with sound.
3. `javascript_tool`: click `#expand` (description), wait 1 s, click the button whose text is "Show transcript", wait 3 s. Check `document.querySelectorAll('transcript-segment-view-model').length` is above 0 (each cue: `H:MM` line, a "N seconds" line, then the text).
4. `get_page_text` on the tab returns the whole transcript (timestamp line, seconds line, text) plus page noise; `javascript_tool` output is cut near 1000 characters, so do not use it to read the text. If a sign-in wall or block shows, stop this path (no second try) and go to path 4.
5. Write `raw_transcripts_canonical/<id>_timed.txt`: header lines `# Video ID`, `# Title`, `# Published`, `# Source: browser transcript panel (auto); uploader: <channel>`, `# Analyst`, `# Duration_s`, `# Word count: 0`, `# ---`, then one `[HH:MM:SS] text` line per cue. Drop the "N seconds" lines and the related-video list.
6. `python scripts/dev/cache_panel_transcript.py raw_transcripts_canonical/<id>_timed.txt` sets the word count and writes `<id>_raw.txt`. The cache folder is git-ignored (the fetcher's cache), so the files stay untracked.
7. Close your tab (`tabs_close_mcp`) as soon as the transcript is read.
