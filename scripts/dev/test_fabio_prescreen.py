import sys, pathlib, unittest
try:
    import cv2, numpy as np
    HAS_CV = True
except ImportError:  # CI image without OpenCV: skip the frame tests only. A module-level SkipTest collects 0 tests,
    HAS_CV = False   # pytest exits 5 and run_extra_tests.py counts that as FAIL (CI red 2026-10-13, Step 3xt).
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import fabio_prescreen as p

W, H = 960, 540


def chart():
    """Dark chart with candle-like noise: small lime/red candles, grey level line."""
    fr = np.full((H, W, 3), 25, np.uint8)
    rng = np.random.default_rng(1)
    for x in range(60, 640, 6):
        y = int(250 + 60 * np.sin(x / 40) + rng.integers(-20, 20))
        col = (0, 255, 0) if rng.integers(0, 2) else (40, 40, 220)  # BGR lime / red
        fr[y:y + 14, x:x + 3] = col
    fr[300, 60:710] = (110, 110, 110)  # grey level line
    return fr


def with_ticket(fr, stop=True, target=True):
    fr = fr.copy()
    if stop:   # red stop label + line to the price axis
        fr[318:327, 492:565] = (50, 60, 205)
        fr[322, 565:715] = (50, 60, 205)
    if target:  # green target label + line
        fr[238:247, 492:565] = (70, 170, 50)
        fr[242, 565:715] = (70, 170, 50)
    return fr


@unittest.skipUnless(HAS_CV, 'cv2/numpy not installed')
class T(unittest.TestCase):
    def test_ticket_frame_flagged(self):
        self.assertTrue(p.frame_has_ticket(with_ticket(chart())))

    def test_stop_line_alone_flagged(self):
        self.assertTrue(p.frame_has_ticket(with_ticket(chart(), target=False)))

    def test_blank_chart_not_flagged(self):
        self.assertFalse(p.frame_has_ticket(chart()))

    def test_talking_heads_not_flagged(self):
        self.assertFalse(p.frame_has_ticket(np.full((H, W, 3), (90, 110, 130), np.uint8)))


class Window(unittest.TestCase):  # pure Python: runs with or without OpenCV
    def test_window_needs_two_hits(self):
        self.assertFalse(p.window_flag([True] + [False] * 49))
        self.assertTrue(p.window_flag([False] * 10 + [True, True] + [False] * 38))


if __name__ == '__main__':
    unittest.main()
