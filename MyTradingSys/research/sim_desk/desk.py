"""Simulator desk: one local page. Pick settings (free-form numbers allowed), Run, get a plain verdict and example trades.

  python MyTradingSys/research/sim_desk/desk.py            # serves http://127.0.0.1:8765 until Ctrl+C (started by hand)
  python MyTradingSys/research/sim_desk/desk.py --build    # only build the local data cache (once, about a minute)

DEV window only (2022-04-01..2024-06-30); VALIDATION and HOLDOUT are never offered. Every new setting appends one
row to research/layer_lab/TRIALS.md before its result shows; a repeat is served from cache/ and adds none.
cache/ is gitignored (the repo is public: no price data or run output is committed).
"""
import argparse
import datetime as dt
import hashlib
import json
import math
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
TRIALS = HERE.parent / 'layer_lab' / 'TRIALS.md'
CACHE = HERE / 'cache' / 'results'
DEV_FIRST, DEV_LAST = dt.date(2022, 4, 1), dt.date(2024, 6, 30)
PLAUSIBLE_R = 0.10
NL = chr(10)
CMD = '`python MyTradingSys/research/sim_desk/desk.py`'


def check_dates(start, end):
    """Refuse anything outside DEV (same window as the study runner's assert)."""
    try:
        a, b = dt.date.fromisoformat(str(start)), dt.date.fromisoformat(str(end))
    except ValueError:
        raise ValueError(f'dates must be YYYY-MM-DD, got {start!r}, {end!r}')
    if a < DEV_FIRST or b > DEV_LAST:
        raise ValueError(f'only the DEV window {DEV_FIRST}..{DEV_LAST} can be tested here; validation and holdout data stay unread')
    if a > b:
        raise ValueError('start is after end')
    return a.isoformat(), b.isoformat()


def worst_streak(net):
    """Longest run of losing trades in time order."""
    best = cur = 0
    for v in net:
        cur = cur + 1 if v < 0 else 0
        best = max(best, cur)
    return best


def stats(res):
    """n, mean, day-bootstrap 95 % range, power: the study runner's own cell() and Boot (same seed, same days)."""
    import ladder_run as lr
    net = np.asarray(res['net'], float)
    filled = np.asarray(res.get('filled', np.ones(net.size, bool)), bool)
    nofill = int((~filled).sum())
    net = net[filled]
    if net.size == 0:
        return {'n': 0, 'streak': 0, 'nofill': nofill}
    boot = lr.Boot(list(res['all_days']))
    day_idx = np.array([boot.pos[int(d)] for d in np.asarray(res['day'])[filled]])
    order = np.argsort(np.asarray(res['touch_t'])[filled], kind='stable')
    c = lr.cell(net, np.asarray(res['gross'])[filled], np.asarray(res['fees'])[filled], day_idx, order, boot, with_power=True)
    c['streak'] = worst_streak(net[order])
    c['nofill'] = nofill
    return c


def verdict(st):
    """(word, reason) from the spread of the actual filled trades (Fable review C2; the two-point model is not used here)."""
    n = st.get('n', 0)
    if not n:
        return 'NOT ENOUGH DATA', 'no filled trades with these settings'
    rng = f"95 % range of the average {st['lo']:+.3f} to {st['hi']:+.3f} R"
    if st['lo'] > 0:
        return 'PASSED', (f'the whole {rng} is above zero. On DEV only: it needs its one validation run, '
                          'which is not on this desk')
    if st['hi'] < PLAUSIBLE_R and st.get('power_plausible', 0) >= .5:
        return 'FAILED', f'even a small edge of +{PLAUSIBLE_R:.2f} R per trade is ruled out ({rng})'
    mde = st.get('mde_sd')
    small = f'; {n} trades can only rule out edges above about {mde:+.2f} R' if mde and mde == mde else ''
    return 'NOT ENOUGH DATA', f'{rng}: too wide to call either way{small}'


def _rows(path, tag):
    if not Path(path).exists():
        return []
    return [ln for ln in Path(path).read_text(encoding='utf-8').split(NL) if tag in ln]


def count_tries(trials_path, study):
    return len(_rows(trials_path, f'| sim-desk {study.ID} '))


RESULT_VERSION = 2   # 2: results carry the per-idea filled flag


def _key(study, q):
    code = getattr(study, '_code_hash', lambda: '')()
    raw = json.dumps([study.ID, q, code, RESULT_VERSION], sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()[:20]


def _tag(study, q):
    return f'| sim-desk {study.ID} {study.label(q)} |'


def _append_row(trials_path, study, q, st, word):
    res = (f"filled n {st['n']} ({st.get('nofill', 0)} never filled), mean net R {st['mean']:+.3f} [{st['lo']:+.3f}, {st['hi']:+.3f}], worst losing streak {st['streak']}; {word}"
           if st.get('n') else f'n 0; {word}')
    row = (f"| {dt.date.today():%Y-%m-%d} {_tag(study, q)} {CMD} | DEV {q['start']}..{q['end']}; "
           f"VALIDATION/HOLDOUT never offered | {res} |")
    p = Path(trials_path)
    text = p.read_text(encoding='utf-8') if p.exists() else ''
    if text and not text.endswith(NL):
        text += NL
    p.write_text(text + row + NL, encoding='utf-8', newline=NL)


def run_setting(study, p, trials_path=TRIALS, cache_dir=CACHE, progress=print, charts=False):
    """Normalize p, run (or read the cache), ledger row for a new setting, verdict. Returns a JSON-ready dict."""
    q = study.normalize(p)
    cache_dir = Path(cache_dir)
    f = cache_dir / f'{study.ID}_{_key(study, q)}.json'
    cached = f.exists()
    if cached:
        res = json.loads(f.read_text(encoding='utf-8'))
        res = {k: (np.array(v) if k != 'refs' else v) for k, v in res.items()}
    else:
        res = study.run(q, progress=progress)
        cache_dir.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps({k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in res.items()}), encoding='utf-8')
    st = stats(res)
    word, reason = verdict(st)
    tried = any(_tag(study, q) in ln for ln in _rows(trials_path, '| sim-desk '))   # keyed on the ledger, not this tree's cache
    if not tried:
        _append_row(trials_path, study, q, st, word)   # the ledger row lands before the result is shown
    out = {'verdict': word, 'reason': reason, 'cached': cached, 'already_tried': tried, 'nofill': st.get('nofill', 0), 'describe': study.describe(q),
           'label': study.label(q), 'settings': q, 'n': st.get('n', 0), 'mean': st.get('mean'), 'lo': st.get('lo'),
           'hi': st.get('hi'), 'streak': st.get('streak', 0), 'win_rate': st.get('win_rate'),
           'try_no': count_tries(trials_path, study), 'prior_tries': len(_rows(trials_path, f"| {getattr(study, 'PRIOR_TAG', '-')} ")),
           'stats': {k: v for k, v in st.items() if isinstance(v, (int, float))}, 'charts': []}
    if charts:
        try:
            import charts as ch
            out['charts'] = ch.make(study, q, res)
        except ImportError:
            pass
    return out


# ---- the page ----
import study_levels  # noqa: E402

STUDIES = {study_levels.ID: study_levels}
LOCK = threading.Lock()
PROGRESS = {'line': ''}


def _clean(o):
    if isinstance(o, dict):
        return {k: _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, float) and not math.isfinite(o):
        return None
    if isinstance(o, np.generic):
        return _clean(o.item())
    return o


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype='application/json'):
        data = body if isinstance(body, bytes) else json.dumps(_clean(body)).encode()
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *a):
        pass

    def do_GET(self):
        if self.path in ('/', '/index.html'):
            return self._send(200, (HERE / 'page.html').read_bytes(), 'text/html; charset=utf-8')
        if self.path == '/api/studies':
            return self._send(200, [{'id': s.ID, 'title': s.TITLE, 'params': s.params(), 'defaults': s.normalize({}),
                                     'tries': count_tries(TRIALS, s)} for s in STUDIES.values()])
        if self.path == '/api/progress':
            return self._send(200, PROGRESS)
        self._send(404, {'error': 'not found'})

    def do_POST(self):
        if self.path != '/api/run':
            return self._send(404, {'error': 'not found'})
        try:
            body = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))) or b'{}')
            study = STUDIES[body.get('study', study_levels.ID)]
            with LOCK:
                PROGRESS['line'] = 'running...'
                out = run_setting(study, body.get('params', {}), progress=lambda s: PROGRESS.update(line=s), charts=True)
                PROGRESS['line'] = ''
            self._send(200, out)
        except (ValueError, KeyError) as e:
            PROGRESS['line'] = ''
            self._send(400, {'error': f'Could not run: {e}'})
        except FileNotFoundError:
            PROGRESS['line'] = ''
            self._send(400, {'error': 'The price data folder was not found on this machine; the desk needs the 1m bars.'})
        except Exception as e:   # anything else: one plain line, the detail stays in the desk window
            PROGRESS['line'] = ''
            print(f'desk error: {e!r}', flush=True)
            self._send(500, {'error': 'Something went wrong in the run; nothing was logged. Details are in the desk window.'})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, default=8765)
    ap.add_argument('--build', action='store_true', help='only build the data cache, then exit')
    a = ap.parse_args()
    if a.build:
        study_levels.build_cache()
        return
    srv = ThreadingHTTPServer(('127.0.0.1', a.port), Handler)
    print(f'Simulator desk on http://127.0.0.1:{a.port}  (Ctrl+C stops it)', flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
