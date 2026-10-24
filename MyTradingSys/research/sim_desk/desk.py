"""Simulator desk: one local page. Pick settings (free-form numbers allowed), Run, get a plain verdict and example trades.

  python MyTradingSys/research/sim_desk/desk.py            # one command: starts on a free port, opens the browser, prints the URL (--no-browser to skip)
  python MyTradingSys/research/sim_desk/desk.py --build    # only build the local data cache (once, about a minute)

DEV window only (2022-04-01..2024-06-30); VALIDATION and HOLDOUT are never offered. Every new setting appends one
row to research/layer_lab/TRIALS.md before its result shows; a repeat is served from cache/ and adds none.
cache/ is gitignored (the repo is public: no price data or run output is committed).
"""
import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import math
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import conditions  # noqa: E402
import runs_view  # noqa: E402
TRIALS = HERE.parent / 'layer_lab' / 'TRIALS.md'
CACHE = HERE / 'cache' / 'results'
DEV_FIRST, DEV_LAST = dt.date(2022, 4, 1), dt.date(2024, 6, 30)
PLAUSIBLE_R = 0.10
MIN_TRADES = 30          # same floor as the layer runners (run_rsi_backtest.py MIN_OOS_N)
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


START_USD, RISK_PCT = 1000.0, 1.0   # the page's money line: 1,000 USD, 1 % risked per trade, simple sum (as in the levels result)


def numbers(res):
    """Standard numbers over the FILLED trades in time order: n, win rate, mean net R, profit factor, max drawdown (R, peak to
    trough of the running net R), and the fee split mean gross / fee / net R per trade."""
    filled = np.asarray(res.get('filled', np.ones(len(res['net']), bool)), bool)
    if not filled.any():
        return {'n': 0}
    order = np.argsort(np.asarray(res['touch_t'])[filled], kind='stable')
    net, gross, fees = (np.asarray(res[k], float)[filled][order] for k in ('net', 'gross', 'fees'))
    n = len(net)
    if not n:
        return {'n': 0}
    win, loss = net[net > 0].sum(), -net[net < 0].sum()
    cum = np.cumsum(net)
    dd = float((np.maximum.accumulate(np.r_[0.0, cum])[1:] - cum).max())
    return {'n': n, 'win_rate': float((net > 0).mean()), 'mean_net': float(net.mean()), 'mean_gross': float(gross.mean()),
            'mean_fee': float(fees.mean()), 'sd': float(net.std(ddof=1)) if n > 1 else 0.0, 'profit_factor': float(win / loss) if loss > 0 else None, 'max_dd_r': dd}


def luck(sd, n, tries):
    """R per trade that pure luck reaches as the best of `tries` no-edge setups: sd * sqrt(2 ln N) / sqrt(n) (extreme-value
    approximation for the maximum of N independent normal means). 0 for a single try."""
    if n < 2 or tries < 2:
        return 0.0
    return float(sd * math.sqrt(2 * math.log(tries)) / math.sqrt(n))


def monte_carlo(res, idx, shuffles=1000, seed=7):
    """Reshuffle the filled trades' R `shuffles` times (fixed seed): 5-95 % band of the running R at the curve's trade
    positions `idx` (1-based), and the 5-95 % range of the worst drawdown. Answers: how much of the path is order luck."""
    filled = np.asarray(res.get('filled', np.ones(len(res['net']), bool)), bool)
    net = np.asarray(res['net'], float)[filled]
    if len(net) < 2:
        return None
    rng = np.random.default_rng(seed)
    paths = np.cumsum(rng.permuted(np.tile(net, (shuffles, 1)), axis=1), axis=1)
    peak = np.maximum.accumulate(np.concatenate([np.zeros((shuffles, 1)), paths], axis=1), axis=1)[:, 1:]
    dd = (peak - paths).max(axis=1)
    cols = np.asarray(idx) - 1
    lo, hi = np.percentile(paths[:, cols], [5, 95], axis=0)
    return {'lo': [round(float(x), 3) for x in lo], 'hi': [round(float(x), 3) for x in hi],
            'dd_lo': round(float(np.percentile(dd, 5)), 2), 'dd_hi': round(float(np.percentile(dd, 95)), 2), 'shuffles': shuffles}


def trade_list(res):
    """Filled trades in time order for the clickable list: i = position in the run's arrays (what /api/trade takes)."""
    filled = np.flatnonzero(np.asarray(res.get('filled', np.ones(len(res['net']), bool)), bool))
    filled = filled[np.argsort(np.asarray(res['touch_t'])[filled], kind='stable')]
    net = np.asarray(res['net'], float)[filled]
    side = np.asarray(res['side'])[filled] if 'side' in res else np.zeros(len(filled), int)
    return {'i': filled.tolist(), 't': [int(x) for x in np.asarray(res['touch_t'])[filled]], 'side': [int(x) for x in side],
            'r': [round(float(x), 3) for x in net], 'cum': [round(float(x), 3) for x in np.cumsum(net)]}


def trade_chart(study, p, cond, i, cache_dir=CACHE, progress=print):
    """SVG candle chart of trade i (index into the run's arrays after the condition filter), or None."""
    import charts as ch
    q = study.normalize(p)
    res, _ = _raw(study, q, cache_dir, progress)
    cond = conditions.normalize(cond)
    if cond:
        res = _apply_conditions(study, q, res, cond, cache_dir, progress)
    if not 0 <= i < len(res['refs']) or not hasattr(study, 'chart_trade'):
        return None
    tr = study.chart_trade(res['refs'][i], q)
    return ch.svg(tr) if tr else None


def curve(res, points=400):
    """Equity curve of the FILLED trades in time order: cumulative R and USD (start 1,000, 1 % risk, simple sum).
    At most `points` points (even stride, last trade always kept)."""
    filled = np.asarray(res.get('filled', np.ones(len(res['net']), bool)), bool)
    net = np.asarray(res['net'], float)[filled]
    t = np.asarray(res['touch_t'])[filled]
    order = np.argsort(t, kind='stable')
    net, t = net[order], t[order]
    cum = np.cumsum(net)
    idx = np.arange(len(net))
    if len(net) > points:
        idx = np.unique(np.r_[np.linspace(0, len(net) - 1, points).astype(int), len(net) - 1])
    return {'n': int(len(net)), 'idx': (idx + 1).tolist(), 't': [int(x) for x in t[idx]], 'r': [round(float(x), 4) for x in cum[idx]],
            'usd': [round(START_USD * (1 + RISK_PCT / 100 * float(x)), 2) for x in cum[idx]], 'start_usd': START_USD, 'risk_pct': RISK_PCT}


def verdict(st):
    """(word, reason) from the spread of the actual filled trades (Fable review C2; the two-point model is not used here)."""
    n = st.get('n', 0)
    if not n:
        return 'NOT ENOUGH DATA', 'no filled trades with these settings'
    if n < MIN_TRADES:
        return 'NOT ENOUGH DATA', f'only {n} filled trades; at least {MIN_TRADES} are needed before the desk calls it'
    rng = f"95 % range of the average {st['lo']:+.3f} to {st['hi']:+.3f} R"
    if st['hi'] < 0:
        return 'FAILED', f'the whole {rng} is below zero: it loses money after fees'
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


RESULT_VERSION = 3   # 3: results carry the per-idea side (conditions need it)


def _key(study, q):
    code = getattr(study, '_code_hash', lambda: '')()
    raw = json.dumps([study.ID, q, code, RESULT_VERSION], sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()[:20]


def _tag(study, q, cond=None):
    c = conditions.label(cond) if cond else ''
    return f'| sim-desk {study.ID} {study.label(q)}{" ~ if " + c if c else ""} |'


def _append_row(trials_path, study, q, st, word, cond=None):
    res = (f"filled n {st['n']} ({st.get('nofill', 0)} never filled), mean net R {st['mean']:+.3f} [{st['lo']:+.3f}, {st['hi']:+.3f}], worst losing streak {st['streak']}; {word}"
           if st.get('n') else f'n 0; {word}')
    row = (f"| {dt.date.today():%Y-%m-%d} {_tag(study, q, cond)} {CMD} | DEV {q['start']}..{q['end']}; "
           f"VALIDATION/HOLDOUT never offered | {res} |")
    p = Path(trials_path)
    text = p.read_text(encoding='utf-8') if p.exists() else ''
    if text and not text.endswith(NL):
        text += NL
    p.write_text(text + row + NL, encoding='utf-8', newline=NL)


def _raw(study, q, cache_dir, progress):
    """(result arrays, from_cache) for normalized settings q; conditions are not part of the key."""
    cache_dir = Path(cache_dir)
    f = cache_dir / f'{study.ID}_{_key(study, q)}.json'
    if f.exists():
        res = json.loads(f.read_text(encoding='utf-8'))
        return {k: (np.array(v) if k != 'refs' else v) for k, v in res.items()}, True
    res = study.run(q, progress=progress)
    cache_dir.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps({k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in res.items()}), encoding='utf-8')
    return res, False


def _apply_conditions(study, q, res, cond, cache_dir, progress):
    minute = None
    if 'ema_rel' in cond or 'atr_lo' in cond:
        from studies import _bars
        minute = _bars.load_1m(progress, q.get('symbol', 'BTCUSDT'))
    b_times = None
    if 'layer_b' in cond:
        if cond['layer_b'] not in STUDIES:
            raise ValueError(f"layer B: no study called {cond['layer_b']!r} (have {', '.join(STUDIES)})")
        b = STUDIES[cond['layer_b']]
        b_res, _ = _raw(b, b.normalize({}), cache_dir, progress)
        b_times = b_res['touch_t']
    from studies import _bars as bars_mod
    keep = conditions.mask(cond, res['touch_t'], res['side'], minute, b_times, bars_mod.resample)
    return conditions.apply(res, keep)


def run_setting(study, p, trials_path=TRIALS, cache_dir=CACHE, progress=print, charts=False, cond=None):
    """Normalize p, run (or read the cache), ledger row for a new setting, verdict. Returns a JSON-ready dict."""
    t0 = time.perf_counter()
    q = study.normalize(p)
    cond = conditions.normalize(cond)
    res, cached = _raw(study, q, cache_dir, progress)
    before = int(np.asarray(res['filled']).sum()) if 'filled' in res else None
    if cond:
        res = _apply_conditions(study, q, res, cond, cache_dir, progress)
    st = stats(res)
    word, reason = verdict(st)
    tried = any(_tag(study, q, cond) in ln for ln in _rows(trials_path, '| sim-desk '))   # keyed on the ledger, not this tree's cache
    if not tried:
        _append_row(trials_path, study, q, st, word, cond)   # the ledger row lands before the result is shown
    out = {'verdict': word, 'reason': reason, 'cached': cached, 'already_tried': tried, 'nofill': st.get('nofill', 0), 'describe': study.describe(q),
           'label': study.label(q), 'settings': q, 'cond': cond, 'cond_label': conditions.label(cond), 'n_before_cond': before, 'n': st.get('n', 0), 'mean': st.get('mean'), 'lo': st.get('lo'),
           'hi': st.get('hi'), 'streak': st.get('streak', 0), 'win_rate': st.get('win_rate'),
           'try_no': count_tries(trials_path, study), 'prior_tries': len(_rows(trials_path, f"| {study.PRIOR_TAG} ")) if hasattr(study, 'PRIOR_TAG') else 0,
           'stats': {k: v for k, v in st.items() if isinstance(v, (int, float))}, 'charts': [], 'curve': curve(res), 'numbers': numbers(res), 'trades': trade_list(res)}
    out['curve']['mc'] = monte_carlo(res, out['curve']['idx']) if out['curve'].get('n') else None
    tries = out['try_no'] + out['prior_tries']
    k = out['numbers']
    out['luck'] = {'tries': tries, 'r': luck(k.get('sd', 0), k.get('n', 0), tries)} if k.get('n') else None
    out['run_seconds'] = round(time.perf_counter() - t0, 2)
    if charts:
        try:
            import charts as ch
            out['charts'] = ch.make(study, q, res)
        except ImportError:
            pass
    return out


# ---- studies: one file each in studies/, found at start (PLUGIN.md) ----
STUDY_DIR = HERE / 'studies'
NEEDS = ('ID', 'params', 'normalize', 'label', 'describe', 'run')


def load_studies(folder=STUDY_DIR):
    """{ID: module} for every studies/*.py (not _private) that has the study functions; anything else is skipped."""
    folder = Path(folder)
    found = {}
    for f in sorted(folder.glob('*.py')):
        if f.name.startswith('_'):
            continue
        name = f'studies.{f.stem}' if folder.resolve() == STUDY_DIR.resolve() else f'desk_study_{f.stem}'
        mod = sys.modules.get(name)
        if mod is None:
            spec = importlib.util.spec_from_file_location(name, f)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[name] = mod    # registered first so build workers can pickle its functions
            try:
                spec.loader.exec_module(mod)
            except Exception as e:
                del sys.modules[name]
                print(f'study {f.name} skipped: {e!r}', flush=True)
                continue
        if all(hasattr(mod, a) for a in NEEDS):
            found[mod.ID] = mod
    return found


# ---- questions for the operator, answered on the page; answers stay local (cache/ is gitignored) ----
QUESTIONS = HERE / 'questions.json'
ANSWERS = HERE / 'cache' / 'answers.jsonl'


def _answers(path):
    if not Path(path).exists():
        return []
    return [json.loads(ln) for ln in Path(path).read_text(encoding='utf-8').splitlines() if ln.strip()]


def load_questions(path=QUESTIONS, answers_path=ANSWERS):
    """Seeded questions, each with its latest answer (or None: the default stands)."""
    qs = json.loads(Path(path).read_text(encoding='utf-8'))
    last = {a['id']: a for a in _answers(answers_path)}
    for q in qs:
        q['answer'] = last.get(q['id'])
    return qs


def save_answer(qid, choice, text, path=ANSWERS, questions=QUESTIONS):
    ids = {q['id'] for q in json.loads(Path(questions).read_text(encoding='utf-8'))}
    if qid not in ids:
        raise ValueError('that question is not on the desk')
    row = {'id': qid, 'choice': str(choice or ''), 'text': str(text or '').strip(),
           'at': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'a', encoding='utf-8', newline=NL) as fh:
        fh.write(json.dumps(row) + NL)
    return row


# ---- the page ----
STUDIES = load_studies()
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


RESULTS = HERE / 'results'


def export_result(out, study, results_dir=RESULTS):
    """Write one run as results/desk-<study>-<hash>.json in the standard schema (DESIGN.md) so the hosted page lists it.
    Percent and R only (public repo). Same settings and condition -> same file name, overwritten."""
    key = hashlib.sha256(json.dumps([study.ID, out['settings'], out.get('cond')], sort_keys=True, default=str).encode()).hexdigest()[:8]
    rid = f'desk-{study.ID}-{key}'
    tone = {'FAILED': 'bad', 'PASSED': 'good'}.get(out['verdict'], 'warn')
    c = out.get('curve') or {}
    what = [{'name': 'Study', 'value_plain': f"{study.TITLE}: {out['describe']}", 'label': 'OURS'},
            {'name': 'Settings', 'value_plain': out['label'], 'label': 'OURS'},
            {'name': 'Condition', 'value_plain': out.get('cond_label') or 'none', 'label': 'OURS'}]
    ex = [{'kind': 'curve', 'title': 'Running total of net R, filled trades in time order', 'r': c['r'], 'usd': c['usd'],
           'start_usd': c['start_usd'], 'risk_pct': c['risk_pct']}] if c.get('n') else [{'kind': 'none', 'title': 'no filled trades'}]
    doc = {'id': rid, 'kind': 'backtest', 'parity': None, 'family': 'Desk runs', 'title': f"{study.TITLE}: {out['label']}" + (f" ~ {out['cond_label']}" if out.get('cond_label') else ''),
           'what': what, 'how': 'Run on the local simulator desk: the study re-simulates every idea on development data; the optional condition then keeps only matching trades (post-filter on the cached run). Fees are included; a never-filled idea is not a trade.',
           'window': f"DEV only, {out['settings'].get('start')} to {out['settings'].get('end')} (VALIDATION and HOLDOUT never offered)",
           'verdict': {'label': out['verdict'], 'tone': tone}, 'why': [out['reason']],
           'kpis': [{'label': 'filled trades', 'value': str(out['n'])}, {'label': 'ideas never filled', 'value': str(out['nofill'])},
                    {'label': 'average per trade, after fees', 'value': f"{out['mean']:+.3f} R" if out.get('mean') is not None else '-', 'tone': tone if out['verdict'] != 'NOT ENOUGH DATA' else None},
                    {'label': '95 % range', 'value': f"{out['lo']:+.3f} to {out['hi']:+.3f} R" if out.get('lo') is not None else '-'},
                    {'label': 'if you put in $1,000', 'value': f"${c['usd'][-1]:.0f}" if c.get('n') else '-'},
                    {'label': 'try number', 'value': str(out['try_no'])}],
           'examples': ex, 'source_files': ['MyTradingSys/research/sim_desk/desk.py'], 'commit': 'local desk run'}
    for k in doc['kpis']:
        if k.get('tone') is None:
            k.pop('tone', None)
    d = Path(results_dir)
    d.mkdir(parents=True, exist_ok=True)
    (d / f'{rid}.json').write_text(json.dumps(doc, indent=1, ensure_ascii=False) + NL, encoding='utf-8', newline=NL)
    return rid


def render_page():
    """page.html with the wired studies named in the HTML itself (works before any script runs); built from STUDIES, no study is named here."""
    import html
    names = ''.join(f'<span class="chip" data-study="{html.escape(s.ID)}">{html.escape(s.TITLE)}</span>' for s in STUDIES.values())
    return (HERE / 'page.html').read_text(encoding='utf-8').replace('<!--STUDIES-->', names).encode('utf-8')


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
        self.path = self.path.split('?', 1)[0]
        if self.path in ('/', '/index.html'):
            return self._send(200, render_page(), 'text/html; charset=utf-8')
        if self.path == '/api/runs':
            return self._send(200, runs_view.list_runs(RESULTS))
        if self.path.startswith('/api/runs/'):
            doc = runs_view.get_run(RESULTS, self.path[len('/api/runs/'):])
            return self._send(200 if doc else 404, doc or {'error': 'no such run'})
        if self.path == '/api/studies':
            return self._send(200, [{'id': s.ID, 'title': s.TITLE, 'params': s.params(), 'defaults': s.normalize({}),
                                     'tries': count_tries(TRIALS, s)} for s in STUDIES.values()])
        if self.path == '/api/conditions':
            return self._send(200, {'fields': conditions.FIELDS, 'defaults': conditions.DEFAULT, 'layers': list(STUDIES)})
        if self.path == '/api/progress':
            return self._send(200, PROGRESS)
        if self.path == '/api/questions':
            return self._send(200, load_questions())
        self._send(404, {'error': 'not found'})

    def do_POST(self):
        if self.path == '/api/answer':
            try:
                body = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))) or b'{}')
                return self._send(200, save_answer(body.get('id'), body.get('choice'), body.get('text')))
            except ValueError as e:
                return self._send(400, {'error': f'Not saved: {e}'})
        if self.path == '/api/trade':
            try:
                body = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))) or b'{}')
                if body.get('study') not in STUDIES:
                    raise ValueError('pick a study')
                with LOCK:
                    svg = trade_chart(STUDIES[body['study']], body.get('params', {}), body.get('cond'), int(body.get('i', -1)),
                                      progress=lambda s: PROGRESS.update(line=s))
                return self._send(200, {'svg': svg})
            except (ValueError, KeyError, FileNotFoundError) as e:
                return self._send(400, {'error': f'No chart: {e}'})
        if self.path != '/api/run':
            return self._send(404, {'error': 'not found'})
        try:
            body = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))) or b'{}')
            if body.get('study') not in STUDIES:
                raise ValueError('pick a study')
            study = STUDIES[body['study']]
            with LOCK:
                PROGRESS['line'] = 'running...'
                out = run_setting(study, body.get('params', {}), progress=lambda s: PROGRESS.update(line=s), charts=True, cond=body.get('cond'))
                PROGRESS['line'] = ''
            try:
                out['result_id'] = export_result(out, study)
            except OSError as e:
                print(f'result file not written: {e!r}', flush=True)
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


class DeskServer(ThreadingHTTPServer):
    allow_reuse_address = False   # on Windows reuse lets two desks share one port
    daemon_threads = True


def start_server(port=8765, open_browser=True):
    """Bind 127.0.0.1 on `port`, or the next free one (port 0 = any free port). Returns (server, url); the caller serves."""
    srv = None
    for p in ([0] if port == 0 else range(port, port + 30)):
        try:
            srv = DeskServer(('127.0.0.1', p), Handler)
            break
        except OSError:
            continue
    if srv is None:
        srv = DeskServer(('127.0.0.1', 0), Handler)
    url = f'http://127.0.0.1:{srv.server_address[1]}'
    if open_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    return srv, url


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, default=8765, help='first port to try (the next free one is used if busy)')
    ap.add_argument('--no-browser', action='store_true', help='do not open the browser')
    ap.add_argument('--build', action='store_true', help='only build the data cache, then exit')
    a = ap.parse_args()
    if a.build:
        for s in STUDIES.values():
            if hasattr(s, 'build_cache'):
                s.build_cache()
        return
    srv, url = start_server(a.port, open_browser=not a.no_browser)
    print(f'Simulator desk on {url}  (Ctrl+C stops it)', flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
