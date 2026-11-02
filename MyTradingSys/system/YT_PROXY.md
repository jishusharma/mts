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
- The guard is unchanged and keyed by the exit IP: 5 videos per run, 40 requests per 24 h, lockout 6/24/72 h on a 429.
- If WARP's IP gets a 429 as well, run `wgcf register` again for a new account, or wait for the lockout to end.
