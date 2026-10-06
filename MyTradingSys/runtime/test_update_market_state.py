import unittest
import tempfile
import json
import os
from pathlib import Path
from update_market_state import find_latest_snapshot, load_snapshot, atomic_write


class TestUpdateMarketState(unittest.TestCase):
    """Pure-function tests for update_market_state module."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_find_latest_snapshot_no_files(self):
        """find_latest_snapshot raises FileNotFoundError when no snapshots exist."""
        snap_dir = Path(self.temp_dir) / "snapshots"
        snap_dir.mkdir(parents=True, exist_ok=True)

        # Temporarily patch SNAPSHOT_DIR
        import update_market_state as ums
        old_snap_dir = ums.SNAPSHOT_DIR
        try:
            ums.SNAPSHOT_DIR = snap_dir
            with self.assertRaises(FileNotFoundError):
                find_latest_snapshot()
        finally:
            ums.SNAPSHOT_DIR = old_snap_dir

    def test_find_latest_snapshot_single_file(self):
        """find_latest_snapshot returns the only snapshot when one exists."""
        snap_dir = Path(self.temp_dir) / "snapshots"
        snap_dir.mkdir(parents=True, exist_ok=True)

        snap_file = snap_dir / "BTCUSDT_1.json"
        snap_file.write_text('{"price": 100}', encoding="utf-8")

        import update_market_state as ums
        old_snap_dir = ums.SNAPSHOT_DIR
        try:
            ums.SNAPSHOT_DIR = snap_dir
            result = find_latest_snapshot()
            self.assertEqual(result, str(snap_file))
        finally:
            ums.SNAPSHOT_DIR = old_snap_dir

    def test_find_latest_snapshot_multiple_files(self):
        """find_latest_snapshot returns the most recently modified snapshot."""
        snap_dir = Path(self.temp_dir) / "snapshots"
        snap_dir.mkdir(parents=True, exist_ok=True)

        # Create multiple files with different modification times
        files = []
        for i in range(3):
            snap_file = snap_dir / f"BTCUSDT_{i}.json"
            snap_file.write_text(f'{{"price": {100 + i}}}', encoding="utf-8")
            files.append(snap_file)

        # Touch the last file to make it most recent
        import time
        time.sleep(0.01)
        files[-1].touch()

        import update_market_state as ums
        old_snap_dir = ums.SNAPSHOT_DIR
        try:
            ums.SNAPSHOT_DIR = snap_dir
            result = find_latest_snapshot()
            self.assertEqual(result, str(files[-1]))
        finally:
            ums.SNAPSHOT_DIR = old_snap_dir

    def test_load_snapshot_valid_json(self):
        """load_snapshot parses valid JSON snapshot file."""
        snap_file = Path(self.temp_dir) / "snapshot.json"
        snap_data = {"price": 42000, "volume": 1234.5}
        snap_file.write_text(json.dumps(snap_data), encoding="utf-8")

        result = load_snapshot(str(snap_file))
        self.assertEqual(result, snap_data)

    def test_load_snapshot_utf8_handling(self):
        """load_snapshot correctly handles UTF-8 encoded files."""
        snap_file = Path(self.temp_dir) / "snapshot.json"
        snap_data = {"symbol": "BTCUSDT", "note": "test"}
        snap_file.write_text(json.dumps(snap_data), encoding="utf-8")

        result = load_snapshot(str(snap_file))
        self.assertEqual(result["symbol"], "BTCUSDT")

    def test_load_snapshot_missing_file(self):
        """load_snapshot raises FileNotFoundError for missing files."""
        missing = Path(self.temp_dir) / "missing.json"
        with self.assertRaises(FileNotFoundError):
            load_snapshot(str(missing))

    def test_atomic_write_creates_file(self):
        """atomic_write creates a new file with correct content."""
        target = Path(self.temp_dir) / "output.txt"
        content = "test content\n"

        atomic_write(target, content)

        self.assertTrue(target.exists())
        self.assertEqual(target.read_text(encoding="utf-8"), content)

    def test_atomic_write_overwrites_existing(self):
        """atomic_write replaces existing file atomically."""
        target = Path(self.temp_dir) / "output.txt"
        target.write_text("old content", encoding="utf-8")

        new_content = "new content\n"
        atomic_write(target, new_content)

        self.assertEqual(target.read_text(encoding="utf-8"), new_content)

    def test_atomic_write_creates_parent_dirs(self):
        """atomic_write creates parent directories if they don't exist."""
        target = Path(self.temp_dir) / "subdir" / "deep" / "output.txt"
        content = "nested content\n"

        atomic_write(target, content)

        self.assertTrue(target.exists())
        self.assertEqual(target.read_text(encoding="utf-8"), content)

    def test_atomic_write_newline_handling(self):
        """atomic_write preserves newlines correctly."""
        target = Path(self.temp_dir) / "output.txt"
        content = "line1\nline2\nline3\n"

        atomic_write(target, content)

        result = target.read_text(encoding="utf-8")
        self.assertEqual(result, content)


if __name__ == "__main__":
    unittest.main()
