"""cbp.load and live_aid read_json: valid JSON that is not an object returns the safe default, never AttributeError."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "MyTradingSys", ROOT / "MyTradingSys" / "tools" / "live_aid"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import cbp  # noqa: E402
import build_analyst_data  # noqa: E402

NON_OBJECTS = ["[]", '"x"', "1", "null"]
EMPTY = {"schema": 1, "rows": [], "rejected": []}


class LoadNonObject(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_cbp_load_non_object_returns_empty_store(self):
        for i, text in enumerate(NON_OBJECTS):
            with self.subTest(payload=text):
                p = self.dir / ("rows_%d.json" % i)
                p.write_text(text, encoding="utf-8")
                self.assertEqual(cbp.load(str(p)), EMPTY)

    def test_cbp_load_missing_and_corrupt_unchanged(self):
        self.assertEqual(cbp.load(str(self.dir / "gone.json")), EMPTY)
        bad = self.dir / "corrupt.json"
        bad.write_text("{not json", encoding="utf-8")
        self.assertEqual(cbp.load(str(bad)), EMPTY)

    def test_cbp_load_object_still_reads_rows(self):
        p = self.dir / "ok.json"
        p.write_text(json.dumps({"rows": [{"analyst": "A"}], "rejected": [["v", "A", "why"]]}), encoding="utf-8")
        got = cbp.load(str(p))
        self.assertEqual(got["rows"], [{"analyst": "A"}])
        self.assertEqual(got["rejected"], [["v", "A", "why"]])

    def test_live_aid_read_json_non_object_returns_default(self):
        for i, text in enumerate(NON_OBJECTS):
            with self.subTest(payload=text):
                p = self.dir / ("roster_%d.json" % i)
                p.write_text(text, encoding="utf-8")
                self.assertEqual(build_analyst_data.read_json(p, {}), {})
                self.assertEqual(build_analyst_data.read_json(p, {"d": 1}), {"d": 1})

    def test_live_aid_read_json_object_and_missing_unchanged(self):
        p = self.dir / "obj.json"
        p.write_text(json.dumps({"analysts": []}), encoding="utf-8")
        self.assertEqual(build_analyst_data.read_json(p, {}), {"analysts": []})
        self.assertEqual(build_analyst_data.read_json(self.dir / "gone.json", 7), 7)


if __name__ == "__main__":
    unittest.main()
