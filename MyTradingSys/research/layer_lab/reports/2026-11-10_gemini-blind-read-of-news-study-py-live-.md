MATCH: 7 | DIFF: 0 | NOT_IN_DATA: 0

# Gemini Blind Read Report: `news_study.py` vs Module Docstring Specification

- **Card**: `gemini-blind-read-of-news-study-py-live-`
- **Date**: 2026-11-10 UTC
- **Reader**: Gemini (`gemini-3.8-flash-low`, blind read worker, JIS-NUC)
- **Target File**: `MyTradingSys/tools/live_aid/news_study.py`
- **Scope In Read**:
  - `MyTradingSys/tools/live_aid/news_study.py` (lines 1-9 module docstring specification, lines 10-115 implementation)
- **Scope Out Respected**:
  - No edits to read files (`news_study.py`, `news_weight.js`, `sample_tree_news.json`, `news_events.csv`).
  - No edits to live tree, no deployment, no `.secrets` or `.env` access, no trading/orders.

---

## 1. Specification Clauses Extracted from Docstring (`news_study.py:1-9`)

SOURCED: `MyTradingSys/tools/live_aid/news_study.py:1-9`:
1. **Clause 1 (Goal / Purpose)**:
   > "News study: the BTC move 15 m and 60 m after each saved Tree News item, per class (card news-weight-bias-flash-1108)." (`news_study.py:1`)
2. **Clause 2 (Descriptive counts only, no edge claim)**:
   > "Counts only, no edge claim: 20 items are far too few to say any class moves the market; this prints what happened after each saved headline so the W and chip rules in news_weight.js can be read against real minutes. Context only; nothing here feeds a gate, size or order." (`news_study.py:3-4`)
3. **Clause 3 (Input Items Sample)**:
   > "Items: research/news_feeds_2026-10-30/sample_tree_news.json (the existing 20-item sample)." (`news_study.py:5`)
4. **Clause 4 (Class Classification via node and news_weight.js)**:
   > "Class = news_weight.js classify() (called through node)." (`news_study.py:5`)
5. **Clause 5 (Price Feed)**:
   > "Prices: public Binance 1m klines (no key)." (`news_study.py:6`)
6. **Clause 6 (Move Definition Parity with news_events.csv btc_r15 / btc_r60)**:
   > "Move = close of the 15th (60th) minute from the headline minute vs the close of the minute before it, the same definition as research/news_effects_2026-11/news_events.csv btc_r15 / btc_r60." (`news_study.py:6-7`)
7. **Clause 7 (Younger than 15 m / 60 m NA Rule)**:
   > "An item younger than 15 m (60 m) reads NA." (`news_study.py:7`)

---

## 2. Code Verification & Trace Analysis

### Clause 1 & 2: Goal, Reporting, Counts Only & Context Disclaimers
- **Implementation**:
  - `report()` (`news_study.py:78-95`) groups headlines by class, computes `r15` and `r60` for each item, formats timestamps as `%m-%d %H:%M UTC`, and accumulates counts:
    - `n15`, `n60`: total measured items (`r is not None`).
    - `u15`, `u60`: count of positive return items (`r > 0`).
    - `down`: `n - u`.
  - Printed output explicitly prefixes and suffixes:
    - `"news_study: %d saved Tree News items, BTCUSDT 1m from %s, counts only, no edge claim"` (`news_study.py:108`).
    - `"Counts only: 20 items, no class has enough rows to say it moves BTC; the catalogue (news_events.csv, 123 verified rows) is the evidence, not this."` (`news_study.py:110`).
- **Verdict**: MATCH.

### Clause 3: Input Items Sample
- **Implementation**:
  - Line 26: `SAMPLE = HERE.parent.parent / "research" / "news_feeds_2026-10-30" / "sample_tree_news.json"`.
  - Line 99: `items = json.loads(SAMPLE.read_text(encoding="utf-8"))`.
  - Verifying the file on disk confirms 20 items saved from Tree News (`len(items) == 20`).
- **Verdict**: MATCH.

### Clause 4: Class Classification via node Calling news_weight.js classify()
- **Implementation**:
  - Lines 43-49:
    ```python
    def classify(titles):
        node = shutil.which("node")
        if not node:
            return ["OTHER"] * len(titles)
        js = "const NW=require(process.argv[1]);const t=JSON.parse(require('fs').readFileSync(0,'utf8'));process.stdout.write(JSON.stringify(t.map(x=>NW.classify(x))));"
        p = subprocess.run([node, "-e", js, str(JS)], input=json.dumps(titles), capture_output=True, text=True, timeout=30)
        return json.loads(p.stdout) if p.returncode == 0 else ["OTHER"] * len(titles)
    ```
  - In `main()` line 100: `classes = classify([str(x.get("title", "")).split("\n")[0] for x in items])`.
  - Node executes `-e` requiring `news_weight.js`, calling `NW.classify(x)` for each headline title and writing JSON to stdout. Falls back safely to `OTHER` if node is not found or fails.
- **Verdict**: MATCH.

### Clause 5: Public Binance 1m Klines (No Key)
- **Implementation**:
  - Line 29: `URLS = ("https://fapi.binance.com/fapi/v1/klines", "https://api.binance.com/api/v3/klines")`.
  - Lines 52-72 (`fetch(t_from, t_to)`):
    - Uses public endpoints with query parameters `symbol=BTCUSDT&interval=1m&limit=1000&startTime=%d&endTime=%d` without API keys.
    - Uses `_doh_urlopen` (`MyTradingSys/runtime/binance_doh.py`) to bypass local ISP DNS blocks when resolving Binance hosts.
    - Falls back to `api.binance.com` if `fapi.binance.com` errors.
    - Successfully fetched live klines during live execution on host.
- **Verdict**: MATCH.

### Clause 6: Minute Indexing & Move Definition Parity with news_events.csv btc_r15 / btc_r60
- **Implementation**:
  - SOURCED `news_study.py:32-40`:
    ```python
    def move(rows, t, minutes):
        m0 = t // MIN * MIN
        a, b = rows.get(m0 - MIN), rows.get(m0 + (minutes - 1) * MIN)
        if a is None or b is None or a <= 0:
            return None
        return (b / a - 1) * 100
    ```
  - Detailed indexing check:
    - Let $t$ be headline timestamp in ms. $m0 = (t // 60000) * 60000$ is the start of the headline minute bar.
    - Baseline close $a = rows[m0 - 60000]$: close of the minute bar immediately before the headline minute.
    - Target close for 15-minute move (`minutes=15`): $b = rows[m0 + (15 - 1) * 60000] = rows[m0 + 14 * 60000]$.
      - Bar $0$ is $[m0, m0 + 60000)$ (1st minute).
      - Bar $14$ is $[m0 + 14 * 60000, m0 + 15 * 60000)$, which is the 15th closed 1m bar after the headline. Its close is the close of the 15th minute.
    - Target close for 60-minute move (`minutes=60`): $b = rows[m0 + (60 - 1) * 60000] = rows[m0 + 59 * 60000]$.
      - Bar $59$ is $[m0 + 59 * 60000, m0 + 60 * 60000)$, which is the 60th closed 1m bar after the headline. Its close is the close of the 60th minute.
    - Return formula: $(b / a - 1) * 100$.
  - Comparison with `MyTradingSys/research/news_effects_2026-11/build_events.py:406-412,424-433` (the generator of `news_events.csv` `btc_r15` / `btc_r60`):
    - In `build_events.py`:
      - $m = int(t0.timestamp() // 60) * 60 * 1000$
      - $p0 = float(ks[m - 60000][4])$
      - $r15 = (float(ks[m + 14 * 60000][4]) / p0 - 1) * 100$
      - $r60 = (float(ks[m + 59 * 60000][4]) / p0 - 1) * 100$
    - In `measure()`:
      - $res['r%d' % h] = round((c(m + (h - 1) * 60000) / p0 - 1) * 100, 4)$ where $h \in (1, 5, 15, 60, 240)$.
    - The indexing ($m0 - 1\text{m}$, $m0 + 14\text{m}$, $m0 + 59\text{m}$) and percentage calculation $((b / a - 1) * 100)$ are mathematically and structurally identical.
- **Verdict**: MATCH.

### Clause 7: NA Rule for Younger Items (< 15 m / < 60 m) or Missing Bars
- **Implementation**:
  - In `move(rows, t, minutes)`:
    - If either baseline bar `a` ($m0 - MIN$) or target bar `b` ($m0 + (minutes - 1) * MIN$) is missing from `rows` (e.g. because future closed 1m bars have not completed yet, or if a bar is missing), `move()` returns `None`.
  - In `fmt(x)` (`news_study.py:74-75`):
    - `return "NA" if x is None else "%+.2f" % x`.
  - When an item is younger than 15 m or 60 m relative to fetched klines, the corresponding bar is not present in `rows`, returning `None`, which renders as `"NA"` in `report()`.
- **Verdict**: MATCH.

---

## 3. Findings Table

| Item / Clause | Docstring Spec | Code Implementation | Verification / Diff | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Clause 1** | Study BTC move 15m/60m per class | Lines 86-94: iterates classes, calls `move(rows, it["time"], 15)` and `move(rows, it["time"], 60)` | Grouped by class, displays r15% and r60% for each item | **MATCH** |
| **Clause 2** | Counts only, no edge claim | Lines 94, 108, 110: prints summary counts, disclaimers | Prints n15, u15, down, n60, u60, down; prints context only warning | **MATCH** |
| **Clause 3** | Sample: `research/news_feeds_2026-10-30/sample_tree_news.json` | Line 26, 99: reads `sample_tree_news.json` directly | Correct path resolution; loads 20 items | **MATCH** |
| **Clause 4** | Class = `news_weight.js classify()` via node | Lines 43-49, 100: calls `node -e` requiring `news_weight.js` and invoking `classify()` | Matches; falls back cleanly to OTHER if node fails | **MATCH** |
| **Clause 5** | Prices: public Binance 1m klines (no key) | Lines 29, 52-72: public Binance futures/spot kline endpoints via DoH | No API key needed; pagination handles range | **MATCH** |
| **Clause 6** | Move definition: 15th/60th minute close vs close of minute before | Lines 32-40: $a = rows[m0 - MIN]$, $b = rows[m0 + (minutes - 1) * MIN]$, $(b/a - 1)*100$ | Exact parity with `build_events.py` `btc_r15` / `btc_r60` | **MATCH** |
| **Clause 7** | Item younger than 15m/60m reads NA | Lines 37-39, 74-75: returns `None` if bar missing, `fmt(None)` returns `"NA"` | Verified; missing/future bars render as `"NA"` | **MATCH** |

**Summary Findings**: No findings / discrepancies detected. All 7 clauses match the docstring specification exactly.
