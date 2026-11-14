"""Runs inside .github/workflows/yt-fetch.yml (route g of yt.py): captions from GitHub's own address, written as one JSON per id.

    python scripts/dev/yt_gha_runner.py --ids a,b,c --langs en,hi --out out

Uses only the runner-safe routes (the runner's own address, youtube-transcript-api, public mirrors): nothing here needs a
station's proxies. YT_ALLOW_DIRECT=1 is set by the workflow and nowhere else: a station never calls YouTube from its own
address. Output files `<id>.json` = {"cues": [[sec, text]], "info", "lang", "auto", "route"}, plus summary.json. Public captions
only; the artifact is as public as the repo.
"""
import argparse
import json
import os
import sys
from pathlib import Path

if os.environ.get("GITHUB_ACTIONS") != "true" and not os.environ.get("YT_RUNNER_TEST"):
    sys.exit("refused: this runner uses the machine's own address, so it runs only inside GitHub Actions")
os.environ["YT_ALLOW_DIRECT"] = "1"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import yt  # noqa: E402


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", required=True)
    ap.add_argument("--langs", default="en,hi")
    ap.add_argument("--out", default="out")
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    langs = [l for l in a.langs.split(",") if l.strip()]
    routes = yt.build_routes(runner=True)
    summary = {}
    for raw in a.ids.split(","):
        k, vid = yt.mirrors.classify(raw.strip())
        if k != "video":
            summary[raw] = "BADID"
            continue
        res, route, tried, final = yt.get_captions(vid, routes, langs)
        if res:
            res["route"] = route
            res["cues"] = [[s, t] for s, t in res["cues"]]
            (out / f"{vid}.json").write_text(json.dumps(res, ensure_ascii=False), encoding="utf-8", newline="\n")
            summary[vid] = f"OK via {route}"
        else:
            summary[vid] = "NOCAPS" if final else "FAIL"
        print(vid, summary[vid], "tried:", ", ".join(tried), flush=True)
    (out / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8", newline="\n")
    return 0 if all(v.startswith("OK") for v in summary.values()) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
