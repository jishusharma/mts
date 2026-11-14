r"""One shared market-data cache for study trees (card c-drive-worktrees-on-f-1114).

Every study tree used to download the same kline files again into its own runtime_data (50-80 MB per coin, 0.4-0.9 GB per tree).
Use cached(name, producer) instead: the first tree makes the file, every later tree reuses it. The folder is env MTS_DATA_CACHE, else
the host's row in hosts.HOST_PATHS (F:\MTS\data_cache on the desktop), else <tmp>/mts_data_cache. Writes are atomic: tmp file in the
same folder, then os.replace, so a half-written file is never read and two trees fetching at once both end with a whole file.
Stdlib only.
"""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hosts  # noqa: E402


def cache_dir():
    d = hosts.data_cache_dir() or os.path.join(tempfile.gettempdir(), "mts_data_cache")
    Path(d).mkdir(parents=True, exist_ok=True)
    return Path(d)


def cache_path(name):
    """Path of a cache entry; `name` is a relative name like 'binance/BTCUSDT_1m_2022.npz' (no '..', not absolute)."""
    p = Path(name)
    if p.is_absolute() or ".." in p.parts or not p.parts:
        raise ValueError(f"bad cache name: {name!r}")
    return cache_dir() / p


def write_atomic(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    return path


def cold_path(name):
    """Where disk_keep.py moves cold cache files (hosts row `overflow.data`), or None."""
    try:
        import json
        row = (json.loads((Path(__file__).resolve().parents[2] / "MyTradingSys" / "system" / "disk_plan.json").read_text(encoding="utf-8"))
               .get("hosts") or {}).get(hosts.this_host()) or {}
        d = (row.get("overflow") or {}).get("data")
        return Path(d) / name if d and row.get("status") == "KNOWN" else None
    except (OSError, ValueError):
        return None


def cached(name, producer):
    """Bytes-file for `name`: the cached copy when it exists (also in the cold folder), else producer() -> bytes is stored and returned."""
    p = cache_path(name)
    if p.is_file() and p.stat().st_size > 0:
        return p
    c = cold_path(name)
    if c is not None and c.is_file() and c.stat().st_size > 0:
        return c
    return write_atomic(p, producer())
