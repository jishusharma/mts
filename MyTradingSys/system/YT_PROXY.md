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
3. WITHDRAWN (operator 2026-11-12 13:45Z): no Chrome tool from any session until the operator names a deviceId in chat; never select by the "Browser 1/2" label. Skip to path 4. Steps below are history.
4. A public transcript site, now SCRIPTED (2026-11-12): `fetch_captions_timed.py` switches to it by itself on a lock, a 429 or an
   unfetched id (`scripts/dev/yt_transcript_sites.py`, a public Invidious instance; video id or channel handle only, no account, no
   cookies, generic User-Agent, 4 s pauses (OURS), never a YouTube request from this address). Same cache files, header `# Source: public
   transcript site <host>`. Instances come and go and some sit behind a bot check (never worked around): env `YT_SITE_INSTANCES`
   overrides the list. Worked 2026-11-12 on a locked address (yt.chocolatemoo53.com; yewtu.be, kome.ai, youtubetotranscript.com sit
   behind a bot check, tactiq needs an app token, other Invidious/Piped hosts were down).
5. Audio plus local Whisper on the desktop: `scripts/dev/asr_transcribe.py` (ROUTING.md, local ASR on JIS-NB), then `asr_to_canonical.py`.
6. Another exit: phone hotspot or a laptop on another network (one request, paced, guard rules apply there too).
7. Only then one line to the operator asking for a paste.

Waiting list: a video no scripted path got is appended (id, channel, time, paths tried) to `~/.mts/yt_waiting.json` (git-ignored,
next to the block record; env `YT_WAITING_FILE`). `python scripts/dev/fetch_captions_timed.py --waiting` prints it (entries already
cached are hidden). `cbp_run.py` records its skipped videos there and prints a count line, so a run never ends with "+0 rows" and no
reason. A Claude desktop session drains it by path 3, then `cache_panel_transcript.py` clears the entry.

Which path each model kind can run:

| Model kind | Paths it can run |
|---|---|
| Claude desktop session (has Chrome) | all: 1 to 7, and it drains the waiting list by path 3 |
| Claude background worker without Chrome | 1 and 4 (scripted, automatic), 5 if on the desktop, waiting list, fleet ask (2) |
| Gemini, Codex, DeepSeek chat | 1 and 4 (scripted, automatic), waiting list, fleet ask (2); never "watch the video" |

CBP pacing (OURS): the 2026-11-12 02:53Z lock followed one CBP run of 65 YouTube requests in one hour. `cbp_run.py` now pauses 30 s between
analysts, fetches at most 3 videos per analyst and starts no new analyst once 30 requests went out in the last hour (the skipped ones
go through path 4).

Rules for every path: fetch once, cache, share through the repo so no machine fetches a video twice; spread fetches over
machines and pace them, never push one address. Gemini "watch the video" is never a quote source. Quotes pass
`python scripts/dev/verify_extract_quotes.py <extract.md>` (exit 0) against the cached caption file.

### Path 3 steps (worked 2026-11-12 for three videos, no sign-in wall; a Haiku can repeat it)
1. One ToolSearch loads the Chrome tools; do NOT run until the operator names a deviceId (path withdrawn); then `select_browser` that deviceId; `tabs_context_mcp` with createIfEmpty.
2. `navigate` a new tab to `https://www.youtube.com/watch?v=<id>`. One video at a time. MUTED AND PAUSED (operator hears the audio): right after every navigate run `javascript_tool` `document.querySelectorAll('video').forEach(v=>{v.muted=true;v.pause()})` (repeat once after the page settles, the player may autoplay); never let a video play with sound.
3. Copy note: a clipboard copy of the transcript works only after a click inside the transcript panel (the page ignores copy before that); `get_page_text` below needs no clipboard.
3b. `javascript_tool`: click `#expand` (description), wait 1 s, click the button whose text is "Show transcript", wait 3 s. Check `document.querySelectorAll('transcript-segment-view-model').length` is above 0 (each cue: `H:MM` line, a "N seconds" line, then the text).
4. `get_page_text` on the tab returns the whole transcript (timestamp line, seconds line, text) plus page noise; `javascript_tool` output is cut near 1000 characters, so do not use it to read the text. If a sign-in wall or block shows, stop this path (no second try) and go to path 4.
5. Write `raw_transcripts_canonical/<id>_timed.txt`: header lines `# Video ID`, `# Title`, `# Published`, `# Source: browser transcript panel (auto); uploader: <channel>`, `# Analyst`, `# Duration_s`, `# Word count: 0`, `# ---`, then one `[HH:MM:SS] text` line per cue. Drop the "N seconds" lines and the related-video list.
6. `python scripts/dev/cache_panel_transcript.py raw_transcripts_canonical/<id>_timed.txt` sets the word count and writes `<id>_raw.txt`. The cache folder is git-ignored (the fetcher's cache), so the files stay untracked.
7. Close your tab (`tabs_close_mcp`) as soon as the transcript is read.
