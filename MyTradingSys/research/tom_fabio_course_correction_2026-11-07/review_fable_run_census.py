"""Run the unmodified census script with api.binance.com rewritten to the public mirror (api.binance.com is unreachable here)."""
import importlib.util, sys, urllib.request
from pathlib import Path

SRC = Path(sys.argv[1])
CACHE = sys.argv[2]
spec = importlib.util.spec_from_file_location("auction_census", SRC)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

_orig_get = mod._get
def _get(url):
    return _orig_get(url.replace("https://api.binance.com/", "https://data-api.binance.vision/"))
mod._get = _get
mod.main(CACHE)
