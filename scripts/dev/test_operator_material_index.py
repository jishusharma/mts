import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "operator_material_index.py")


def snapshot(root):
    return sorted(os.path.join(d, f) for d, _, fs in os.walk(root) for f in fs)


class T(unittest.TestCase):
    def test_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, "src")
            os.makedirs(os.path.join(src, ".git"))
            out = os.path.join(tmp, "out", "h.jsonl")
            for n in ("shot_rsi.png", "b.jpg"):
                with open(os.path.join(src, n), "wb") as f:
                    f.write(b"x")
            with open(os.path.join(src, ".git", "skip.txt"), "w") as f:
                f.write("Tom")
            with open(os.path.join(src, "n.txt"), "w") as f:
                f.write("Malkan divergence secretword")
            with zipfile.ZipFile(os.path.join(src, "d.docx"), "w") as z:
                z.writestr("word/document.xml", "<w:p><w:t>Fabio idea</w:t></w:p>")
            before = snapshot(tmp)
            r = subprocess.run([sys.executable, SCRIPT, "--roots", src, "--host", "h", "--out", out],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            for name in ("shot_rsi", "n.txt", "d.docx", "secretword", "b.jpg"):
                self.assertNotIn(name, r.stdout)
            self.assertIn("rows=4", r.stdout)
            with open(out, encoding="utf-8") as f:
                rows = [json.loads(l) for l in f]
            self.assertEqual(len(rows), 4)
            by = {os.path.basename(x["path"]): x for x in rows}
            self.assertEqual(sorted(by["n.txt"]["topics"]), ["Malkan", "divergence"])
            self.assertEqual(by["d.docx"]["topics"], ["Fabio"])
            self.assertEqual(by["shot_rsi.png"]["topics"], ["RSI"])
            self.assertEqual(sorted(set(snapshot(tmp)) - set(before)), [out])


if __name__ == "__main__":
    unittest.main()
