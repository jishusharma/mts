"""Fabio video pre-screen: flag 250 s windows that show an order ticket / position line.

Why sequential: OpenCV 5.0.0 (libaom AV1) cannot seek in the f398 mp4s past ~400 s
('Corrupt frame detected'), so `extract` decodes once, front to back, and keeps one
frame every STEP seconds in a cache dir. `screen` works on the cache only.

  python scripts/dev/fabio_prescreen.py extract <video_id> [--step 5]
  python scripts/dev/fabio_prescreen.py screen  <video_id> [--out csv]
"""
import argparse, csv, os, sys

VID_DIR = 'F:/MTS/data/fabio_videos'
CACHE = VID_DIR + '/prescreen_cache'
WINDOW = 250
STEP = 5
W, H = 960, 540


# --- detector -------------------------------------------------------------
# An open order/position is drawn on the chart as a solid red (stop) and/or green
# (target / entry) horizontal line that runs from a small labelled box to the price
# axis. Candles are 2-4 px wide, so a single-colour run of >= MIN_RUN pixels in one
# pixel row is the line, not a candle. Coordinates are for the 960x540 cache frame.
MIN_RUN = 60
CHART = (30, 25, 715, 470)  # x0, y0, x1, y1 : excludes right panel, webcam, watermark
# Layouts differ per video: x1 must be the price axis, because only lines that reach it count.
PROFILES = {'Is1HvdfQm5c': (185, 25, 915, 470)}
# Layouts the detector was calibrated on. Others only get 'candidate' (line reaches the axis, may be
# a zone-box edge: Is1HvdfQm5c draws green/red zone boxes and no ticket, so 13/20 windows light up).
VALIDATED = {'DyS79Eb92Ug'}
PAIR_GAP = (6, 150)  # same-colour runs this far apart vertically = a zone box's edges, not an order line
ACTIVE = {'chart': CHART}


def _axis_run(mask, tol=8):
    """Per row: length of the True run that reaches the right edge (within `tol` px).

    An order/position line ends at the price axis; volume-profile bars start at the
    left edge and zone boxes end mid-chart, so they do not count."""
    import numpy as np
    n = mask.shape[1]
    out = np.zeros(mask.shape[0], int)
    for r in range(mask.shape[0]):
        row = mask[r, n - tol:]
        if not row.any():
            continue
        x = n - tol + int(np.flatnonzero(row).max())  # last lit pixel near the edge
        k = 0
        while x - k >= 0 and mask[r, x - k]:
            k += 1
        out[r] = k
    return out


def _single_lines(per_row):
    """Rows whose run is long and has no same-length partner PAIR_GAP away (zone box edges)."""
    import numpy as np
    rows = np.flatnonzero(per_row >= MIN_RUN)
    keep = []
    for r in rows:
        partner = [q for q in rows if PAIR_GAP[0] <= abs(q - r) <= PAIR_GAP[1]]
        if not partner:
            keep.append(r)
    return keep


def frame_has_ticket(bgr):
    import cv2
    h, w = bgr.shape[:2]
    sx, sy = w / 960.0, h / 540.0
    x0, y0, x1, y1 = ACTIVE['chart']
    roi = bgr[int(y0 * sy):int(y1 * sy), int(x0 * sx):int(x1 * sx)]
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    hh, ss, vv = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    red = ((hh <= 12) | (hh >= 170)) & (ss >= 70) & (vv >= 80)
    grn = (hh >= 45) & (hh <= 80) & (ss >= 70) & (vv >= 70)
    return bool(_single_lines(_axis_run(red)) or _single_lines(_axis_run(grn)))


def window_flag(hits, need=2):
    """A window is flagged when >= `need` sampled frames show an order/position line."""
    return sum(1 for h in hits if h) >= need


def extract(vid, step=STEP):
    import cv2
    out = '%s/%s' % (CACHE, vid)
    os.makedirs(out, exist_ok=True)
    cap = cv2.VideoCapture('%s/%s.f398.mp4' % (VID_DIR, vid))
    fps = cap.get(cv2.CAP_PROP_FPS)
    every = max(1, int(round(fps * step)))
    i = n = bad = run = 0
    # A corrupt packet makes grab() return False; the next keyframe usually recovers,
    # so keep going and only give up after a long unbroken failure streak (EOF).
    while run < 3000:
        ok = cap.grab()
        if not ok:
            bad += 1
            run += 1
            i += 1
            continue
        run = 0
        if i % every == 0:
            ok, fr = cap.retrieve()
            if ok:
                t = int(round(i / fps))
                cv2.imwrite('%s/%06d.jpg' % (out, t), cv2.resize(fr, (W, H)),
                            [cv2.IMWRITE_JPEG_QUALITY, 90])
                n += 1
        i += 1
    i -= run  # trailing EOF failures are not frames
    print('%s: %d frames, %d cached, %d failed grabs' % (vid, i, n, bad))


def screen(vid, out=None, dur=None):
    """Per-250 s window flags from the frame cache -> CSV window_start,window_end,flag,hits,samples,frame_ref."""
    import cv2
    ACTIVE['chart'] = PROFILES.get(vid, CHART)
    d = '%s/%s' % (CACHE, vid)
    ts = sorted(int(f[:-4]) for f in os.listdir(d) if f.endswith('.jpg'))
    rows = []
    for w0 in range(0, (ts[-1] // WINDOW + 1) * WINDOW, WINDOW):
        hit_t = []
        inw = [t for t in ts if w0 <= t < w0 + WINDOW]
        for t in inw:
            fr = cv2.imread('%s/%06d.jpg' % (d, t))
            if fr is not None and frame_has_ticket(fr):
                hit_t.append(t)
        flag = window_flag([True] * len(hit_t))
        label = ('trade' if vid in VALIDATED else 'candidate') if flag else 'no-hit'
        if len(inw) < WINDOW // STEP * 0.9 and w0 + WINDOW < (dur or 10 ** 9):
            label = 'incomplete'  # cache still being written; rerun screen later
        rows.append((w0, w0 + WINDOW, label, len(hit_t), len(inw),
                     '%s/%06d.jpg' % (d, hit_t[0]) if hit_t else ''))
    out = out or 'MyTradingSys/research/fabio_transfer/PRESCREEN_%s.csv' % vid
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['window_start', 'window_end', 'flag', 'hit_frames', 'sampled_frames', 'first_hit_frame'])
        w.writerows(rows)
    print('%s: %d windows, %d flagged -> %s' % (vid, len(rows), sum(r[2] == 'trade' for r in rows), out))


def calibrate(ledger='MyTradingSys/research/fabio_transfer/FABIO_TRADE_LEDGER.csv'):
    """Run the detector on the ledger's lowres 2x2 sheets (960x540 cells, same geometry as the cache)."""
    import cv2, re
    L = VID_DIR + '/lowres/'
    rows = list(csv.DictReader(open(ledger, encoding='utf-8')))

    def sheet_hits(name):
        im = cv2.imread(L + name)
        h, w = im.shape[:2]
        cw, ch = w // 2, h // 2
        return sum(frame_has_ticket(im[r * ch:(r + 1) * ch, c * cw:(c + 1) * cw]) for r in (0, 1) for c in (0, 1))
    trades, empties = [], []
    for r in rows:
        f = r['frame'].split(';')[0].split('/')[-1]
        if not os.path.exists(L + f):
            continue
        if re.fullmatch(r'F[0-9]+', r['id']) and r['video'] == 'DyS79Eb92Ug':
            trades.append((r['id'], f, sheet_hits(f)))
        elif r['id'].startswith('F-noTrade'):
            empties.append((r['id'], f, sheet_hits(f)))
    for t in trades:
        print('trade ', *t)
    for e in empties:
        print('empty ', *e)
    print('recall (sheets with >=1 hit cell): %d/%d' % (sum(t[2] >= 1 for t in trades), len(trades)))
    print('false flags (empty windows, >=1 hit cell): %d/%d' % (sum(e[2] >= 1 for e in empties), len(empties)))


def ledger_windows(vid, out=None, ledger='MyTradingSys/research/fabio_transfer/FABIO_TRADE_LEDGER.csv'):
    """250 s window truth for a video the ledger already covers: trade / no-trade / unread.

    Used for DyS79Eb92Ug: the NUC copy of that mp4 holds only its first ~450 s (rest is a
    zero-filled sparse file), so it cannot be screened here; its windows were read on JIS-NB."""
    import re
    rows = [r for r in csv.DictReader(open(ledger, encoding='utf-8')) if r['video'] == vid]
    trade, empty = set(), set()
    for r in rows:
        m = re.match(r'F-noTrade-(?:[A-Za-z0-9]+-)?([0-9]+)-([0-9]+)$', r['id'])
        if m:
            empty.update(range(int(m[1]) // WINDOW * WINDOW, int(m[2]), WINDOW))
        elif re.fullmatch(r'F[0-9]+(-draft-[0-9]+-[0-9]+)?|F[0-9]+-[mx]', r['id']):
            t = re.search(r't=([0-9]+)', r['note'])
            if t:
                trade.add(int(t[1]) // WINDOW * WINDOW)
        elif r['id'].endswith('-z'):
            t = re.search(r't=([0-9]+)', r['note'])
            if t:
                empty.add(int(t[1]) // WINDOW * WINDOW)
    end = max(trade | empty) + WINDOW
    out = out or 'MyTradingSys/research/fabio_transfer/PRESCREEN_%s.csv' % vid
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['window_start', 'window_end', 'flag', 'source'])
        for w0 in range(0, end, WINDOW):
            flag = 'trade' if w0 in trade else ('no-trade' if w0 in empty else 'unread')
            w.writerow([w0, w0 + WINDOW, flag, 'ledger'])
    print('%s: ledger windows -> %s' % (vid, out))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['extract', 'screen', 'calibrate', 'ledger'])
    ap.add_argument('vid', nargs='?')
    ap.add_argument('--step', type=int, default=STEP)
    ap.add_argument('--out')
    a = ap.parse_args()
    if a.cmd == 'extract':
        extract(a.vid, a.step)
    elif a.cmd == 'screen':
        screen(a.vid, a.out)
    elif a.cmd == 'ledger':
        ledger_windows(a.vid, a.out)
    else:
        calibrate()
