# CCU Video DXntdN3jfTg Extract

- **Video ID:** `DXntdN3jfTg`
- **URL:** https://www.youtube.com/watch?v=DXntdN3jfTg
- **Title:** 🚀 Bitcoin’s Bull Flag Breakout: Is Crypto About to Explode? 🤔
- **Channel:** Crypto Crew University
- **Published / Upload Date:** 2026-10-20
- **Duration:** 1276 seconds (~21m 16s)
- **Status:** Captions Unavailable (HTTP Error 429: Too Many Requests)

---

## Caption Fetch Status & Blocker

Captions could not be retrieved due to YouTube rate limiting (`HTTP 429: Too Many Requests`).

### Exact Command Run
```bash
python scripts/dev/fetch_captions_timed.py --analyst CCU DXntdN3jfTg
```

### Exact Error Output
```
ERROR: Unable to download video subtitles for 'en': HTTP Error 429: Too Many Requests
```

### What Was Tried
1. Ran `python scripts/dev/fetch_captions_timed.py --analyst CCU DXntdN3jfTg` to download English auto-captions/timed subtitles.
2. Verified underlying `yt-dlp` subtitle endpoint request `https://www.youtube.com/api/timedtext?v=DXntdN3jfTg...`, which directly responded with `urllib.error.HTTPError: HTTP Error 429: Too Many Requests`.
3. Per task instructions ("On HTTP 429 or no captions write the exact error into the extract file, commit, stop. Never summarise from guessing the video."), no ungrounded summary or fabricated quotes were created.

### BTC Call & Claims
- **BTC Call:** None extractable from captions (no captions available due to HTTP 429).
- **Levels:** None extractable from captions.
- **Bottom-Thesis Vote:** None extractable from captions.
- **Entry / Stop / Target:** None extractable from captions.
