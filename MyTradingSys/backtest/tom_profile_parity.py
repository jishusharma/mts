"""Computed side of tom-profile-parity-check; no verdicts, signals or outcomes.

Use explicit profile anchors verified from a frame before comparing drawn levels:
  python MyTradingSys/backtest/tom_profile_parity.py --raw work/dax_archive \
    --start 2025-12-22T00:00:00Z --at 2025-12-22T06:25:00Z --out profile.json

The profile implementation and constants are extracted UNCHANGED at runtime from
MarketDataSnapshot.java, compiled in an isolated local directory with Jackson.
This avoids compiling unrelated/live engine classes and works with Java 11+.
The unmodified dynamic-grid buildVp uses 1m bars directly, as daily_vp does.
No assumed UTC-day anchor is evidence of the profile Tom drew.
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / "src/main/java/datafeed/MarketDataSnapshot.java"


def profile_shape_fraction(low, high, widest_price):
    """Return the widest/POC price position within a profile's own range."""
    low, high, widest_price = float(low), float(high), float(widest_price)
    if high <= low:
        raise ValueError("profile high must be greater than profile low")
    if not low <= widest_price <= high:
        raise ValueError("widest price must lie within the profile range")
    return (widest_price - low) / (high - low)


def profile_shape_matches(drawn_fraction, computed_fraction, row_fraction):
    """Compare normalized histogram shapes within one drawn-row height."""
    if row_fraction < 0:
        raise ValueError("row fraction must be non-negative")
    return abs(float(drawn_fraction) - float(computed_fraction)) <= float(row_fraction)


def engine_source():
    text = SOURCE.read_text(encoding="utf-8")
    start = text.index("    private ObjectNode buildVp(List<JsonNode> bars, boolean includeHvnsLvns) {")
    end = text.index("    private ObjectNode buildVwap(", start)
    methods = text[start:end]
    constants = []
    for name in ("VALUE_AREA_PCT", "CONFIDENCE_LOW", "CONFIDENCE_MEDIUM"):
        match = re.search(r"    private static final (?:double|String) " + name + r" = [^;]+;", text)
        if not match:
            raise ValueError("engine constant missing: " + name)
        constants.append(match.group())
    return "\n".join(constants) + "\n" + methods


class EngineProfile:
    def __enter__(self):
        work = REPO / "work"
        work.mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(prefix="profile_", dir=work)
        root = Path(self.tmp.name)
        try:
            impl = engine_source()
            self.sha256 = hashlib.sha256(impl.encode()).hexdigest()
            m2 = Path(os.environ.get("MTS_M2") or Path.home() / ".m2/repository")
            kinds = ("databind", "core", "annotations")
            # Require one coherent Jackson version rather than mix cached versions.
            found = {k: {p.parent.name:p for p in m2.glob(
                "com/fasterxml/jackson/core/jackson-" + k + "/*/jackson-" + k + "-*.jar")}
                for k in kinds}
            common = set.intersection(*(set(found[k]) for k in kinds))
            if not common:
                raise RuntimeError("Need a common jackson-databind/core/annotations version in MTS_M2 or Maven cache")
            version = sorted(common)[-1]
            self.cp = os.pathsep.join([str(root)] + [str(found[k][version]) for k in kinds])
            java = (
                "import java.util.*;\n"
                "import com.fasterxml.jackson.databind.*;\n"
                "import com.fasterxml.jackson.databind.node.*;\n"
                "public class ProfileOnly {\n"
                "private final ObjectMapper mapper = new ObjectMapper();\n"
                + impl +
                "\npublic static void main(String[] args) throws Exception {\n"
                "ProfileOnly p = new ProfileOnly();\n"
                "JsonNode input = p.mapper.readTree(new java.io.File(args[0]));\n"
                "List<JsonNode> bars = new ArrayList<>();\n"
                "input.forEach(bars::add);\n"
                "ObjectNode profile = p.buildVp(bars, false);\n"
                "ObjectNode levels = p.mapper.createObjectNode();\n"
                "for (String key : new String[]{\"poc\",\"vah\",\"val\"}) levels.set(key, profile.get(key));\n"
                "System.out.println(p.mapper.writeValueAsString(levels));\n"
                "}\n}\n"
            )
            src = root / "ProfileOnly.java"
            src.write_text(java, encoding="utf-8", newline="\n")
            self._run(["javac","-encoding","UTF-8","-cp",self.cp,"-d",str(root),str(src)])
            self.root = root
            return self
        except BaseException:
            self.tmp.cleanup()
            raise

    def _run(self, cmd):
        result = subprocess.run(cmd, cwd=self.tmp.name, capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError("profile Java failed:\n" + result.stdout + result.stderr)
        return result.stdout

    def profile(self, rows):
        if not rows or sum(r[5] for r in rows) <= 0:
            return None
        path = self.root / "bars.json"
        path.write_text(json.dumps(rows, allow_nan=False), encoding="utf-8", newline="\n")
        return json.loads(self._run(["java","-cp",self.cp,"ProfileOnly",str(path)]))

    def __exit__(self, *args):
        self.tmp.cleanup()


def select_bars(raw, start_ms, as_of_ms, symbol="GER40"):
    """Select only closed minutes in [start, as_of), preserving gaps."""
    if start_ms >= as_of_ms:
        raise ValueError("start must precede as-of")
    start = dt.datetime.fromtimestamp(start_ms/1000,dt.timezone.utc)
    end = dt.datetime.fromtimestamp((as_of_ms-1)/1000,dt.timezone.utc)
    months = []
    cursor = start.replace(day=1,hour=0,minute=0,second=0,microsecond=0)
    while cursor <= end:
        months.append(cursor.strftime("%Y-%m"))
        cursor = cursor.replace(year=cursor.year+1,month=1) if cursor.month == 12 else cursor.replace(month=cursor.month+1)
    rows = []
    for month in months:
        path = Path(raw)/"klines"/f"{symbol}-1m-{month}.csv"
        if not path.is_file():
            raise FileNotFoundError(path)
        with path.open(encoding="utf-8",newline="") as stream:
            for row in csv.reader(stream):
                t = int(row[0])
                if start_ms <= t and t + 60000 <= as_of_ms:
                    rows.append([t] + [float(v) for v in row[1:6]])
    rows.sort(key=lambda row:row[0])
    if len({row[0] for row in rows}) != len(rows):
        raise ValueError("duplicate minute in selected window")
    return rows


def instant(value):
    value = dt.datetime.fromisoformat(value.replace("Z","+00:00"))
    if value.tzinfo is None:
        raise ValueError("explicit timezone required")
    return value.astimezone(dt.timezone.utc)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw",required=True)
    parser.add_argument("--start",required=True,help="verified profile start, inclusive ISO time")
    parser.add_argument("--at",required=True,help="as-of ISO time; only closed bars")
    parser.add_argument("--out",required=True)
    args = parser.parse_args(argv)
    start, at = instant(args.start), instant(args.at)
    rows = select_bars(args.raw, int(start.timestamp()*1000), int(at.timestamp()*1000))
    with EngineProfile() as engine:
        result = {"profile_start_utc":start.isoformat().replace("+00:00","Z"),
                  "as_of_utc":at.isoformat().replace("+00:00","Z"),
                  "bar_count":len(rows),"levels":engine.profile(rows),
                  "first_bar_ms":rows[0][0] if rows else None,
                  "last_bar_ms":rows[-1][0] if rows else None,
                  "volume_sum":sum(row[5] for row in rows),
                  "engine_source":"src/main/java/datafeed/MarketDataSnapshot.java buildVp",
                  "engine_sha256":engine.sha256,
                  "feed":"Dukascopy DEUIDXEUR 1m BID CFD feed volume",
                  "comparison_status":"NOT_IN_DATA",
                  "reason":"Drawn price, axis tick, profile anchor and frame time require verified frame read."}
    Path(args.out).write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(f"computed {len(rows)} closed 1m bars -> {args.out}")
    return result


if __name__ == "__main__":
    main()
