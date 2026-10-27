"""Read-only view of saved desk runs (results/desk-*.json): a table row per run and one full run for side-by-side.
Only reads files the desk already wrote; fetches nothing. Foreign or broken files are skipped."""
import json
import re
from pathlib import Path

DEV_FIRST, DEV_LAST = '2022-04-01', '2024-06-30'   # same window as desk.check_dates
DATE_RE = re.compile(r'\d{4}-\d{2}-\d{2}')
ID_RE = re.compile(r'^desk-([a-z0-9_]+)-([0-9a-f]{8})$')


def _kpi(doc, start):
    for k in doc.get('kpis') or []:
        if isinstance(k, dict) and str(k.get('label', '')).startswith(start):
            return str(k.get('value', ''))
    return ''


def _nums(text):
    return [float(x) for x in re.findall(r'[-+]?\d+(?:\.\d+)?', text.replace(',', ''))]


def _in_dev(doc):
    ds = DATE_RE.findall(str(doc.get('window', '')))
    return len(ds) >= 2 and all(DEV_FIRST <= d <= DEV_LAST for d in ds[:2])   # no window stated = not shown (fail closed)


def _row(doc):
    m = ID_RE.fullmatch(str(doc.get('id', '')))
    if not m or not _in_dev(doc):
        return None
    n = _nums(_kpi(doc, 'filled trades'))
    mean = _nums(_kpi(doc, 'average per trade'))
    rng = _nums(_kpi(doc, '95 %'))
    v = doc.get('verdict')
    return {'id': doc['id'], 'study': m.group(1), 'hash': m.group(2), 'title': doc.get('title', ''),
            'n': int(n[0]) if n else None, 'mean': mean[0] if mean else None,
            'lo': rng[0] if len(rng) > 1 else None, 'hi': rng[1] if len(rng) > 1 else None,
            'verdict': v.get('label') if isinstance(v, dict) else None}


def list_runs(results_dir):
    rows = []
    for p in sorted(Path(results_dir).glob('desk-*.json')):
        try:
            doc = json.loads(p.read_text(encoding='utf-8'))
            row = _row(doc) if isinstance(doc, dict) else None
        except (OSError, ValueError, TypeError):
            row = None
        if row and not isinstance(doc.get('kpis'), str):
            rows.append(row)
    return rows


def get_run(results_dir, rid):
    """One saved run, full document; None when the id is not a desk run id or the file is missing."""
    if not ID_RE.fullmatch(str(rid or '')):
        return None
    try:
        doc = json.loads((Path(results_dir) / f'{rid}.json').read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return None
    return doc if isinstance(doc, dict) and _in_dev(doc) else None
