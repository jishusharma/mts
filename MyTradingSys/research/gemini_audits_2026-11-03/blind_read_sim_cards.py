#!/usr/bin/env python3
"""Independent blind-read audit of MyTradingSys/research/sim_desk/api_review/RESULTS_CARDS_2026-11-03.md
against the 337 result JSON files in MyTradingSys/research/sim_desk/results/*.json.

No import of build_sim_cards_jobs.py.
Writes MyTradingSys/research/gemini_audits_2026-11-03/sim_results_cards_blind_read.md.
"""

import glob
import json
import os
import re

RESULTS_MD = "MyTradingSys/research/sim_desk/api_review/RESULTS_CARDS_2026-11-03.md"
RESULTS_DIR = "MyTradingSys/research/sim_desk/results"
OUT_MD = "MyTradingSys/research/gemini_audits_2026-11-03/sim_results_cards_blind_read.md"


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    return json.loads(raw), raw.splitlines()


def find_line(lines: list[str], needle: str) -> int:
    for idx, line in enumerate(lines, 1):
        if needle in line:
            return idx
    return 1


def summarize_json(data: dict, jlines: list[str]) -> dict:
    """Extract independent counts, verdict, filled trades, and net figures from a result JSON."""
    verdict_obj = data.get("verdict") or {}
    v_label = (verdict_obj.get("label") or "").strip() if isinstance(verdict_obj, dict) else str(verdict_obj).strip()
    v_line = find_line(jlines, '"verdict"')

    banner = data.get("banner") or {}
    b_state = (banner.get("state") or "").strip()
    b_n = banner.get("n")
    b_net_r = banner.get("net_r")
    b_line = find_line(jlines, '"banner"')

    kpis = data.get("kpis") or []
    kpi_map = {(k.get("label") or "").strip(): (k.get("value") or "").strip() for k in kpis}
    kpi_line = find_line(jlines, '"kpis"')

    missing = data.get("missing")
    miss_dict = missing if isinstance(missing, dict) else {}

    exs = data.get("examples") or []
    curve_r_len = sum(len(e.get("r") or []) for e in exs if e.get("kind") == "curve")
    table_rows_len = sum(len(e.get("rows") or []) for e in exs if e.get("kind") == "table")
    has_trades_key = "trades" in data

    if "filled trades" in kpi_map:
        filled_str = (
            f"filled trades={kpi_map['filled trades']} "
            f"(ideas never filled={kpi_map.get('ideas never filled', 'n/a')}, curve r_len={curve_r_len})"
        )
        filled_num = int(kpi_map["filled trades"])
    elif "trades (first count in the source)" in kpi_map:
        filled_str = f"trades (first count in source)={kpi_map['trades (first count in the source)']} (banner.n={b_n})"
        filled_num = int(kpi_map["trades (first count in the source)"])
    elif "sample size n (first in the source, may not be trades)" in kpi_map:
        filled_str = f"sample size n={kpi_map['sample size n (first in the source, may not be trades)']} (may not be trades; banner.n={b_n})"
        filled_num = None
    elif "trial rows logged" in kpi_map:
        filled_str = f"0 filled trades (trial rows logged={kpi_map['trial rows logged']}, banner.n={b_n})"
        filled_num = 0
    elif kpis:
        first_k = kpis[0]
        filled_str = f"0 filled trades (KPI '{first_k.get('label')}': {first_k.get('value')}, banner.n={b_n}, table_rows={table_rows_len})"
        filled_num = 0
    else:
        filled_str = f"0 filled trades (kpis=[], banner.n={b_n}, missing.n_trades={'present' if 'n_trades' in miss_dict else 'absent'})"
        filled_num = 0

    if "average per trade, after fees" in kpi_map:
        net_str = (
            f"avg after fees={kpi_map['average per trade, after fees']}, "
            f"95% range={kpi_map.get('95 % range', 'n/a')}, "
            f"$1,000->{kpi_map.get('if you put in $1,000', 'n/a')}"
        )
    elif "net R after fees (first value in the source)" in kpi_map:
        net_str = f"net R after fees (first in source)={kpi_map['net R after fees (first value in the source)']} (banner.net_r={b_net_r})"
    elif any("fee-net" in k for k in kpi_map):
        fn_items = [f"{k}={v}" for k, v in kpi_map.items() if "fee-net" in k]
        net_str = "; ".join(fn_items)
    elif b_net_r is not None:
        net_str = f"banner.net_r={b_net_r}"
    else:
        why_list = data.get("why") or []
        net_str = f"no net-R KPI (banner.net_r={b_net_r}, missing.net_r={'present' if 'net_r' in miss_dict else 'absent'})"
        if why_list:
            net_str += f"; why[0]='{why_list[0][:60]}...'"

    return {
        "v_label": v_label,
        "v_line": v_line,
        "b_state": b_state,
        "b_n": b_n,
        "b_net_r": b_net_r,
        "b_line": b_line,
        "kpi_map": kpi_map,
        "kpi_line": kpi_line,
        "filled_str": filled_str,
        "filled_num": filled_num,
        "net_str": net_str,
        "curve_r_len": curve_r_len,
        "table_rows_len": table_rows_len,
        "has_trades_key": has_trades_key,
    }


def main():
    with open(RESULTS_MD, "r", encoding="utf-8") as f:
        md_text = f.read()
    md_lines = md_text.splitlines()

    card_rows = []
    for lineno, line in enumerate(md_lines, 1):
        m = re.match(r"^\| ([^|]+?) \| (EMPTY|NOT ENOUGH DATA|FAILED|PASSED) \| ([^|]+?) \| ([^|]+?) \| ([^|]+?) \|$", line)
        if m:
            card_rows.append({
                "lineno": lineno,
                "id": m.group(1).strip(),
                "verdict": m.group(2).strip(),
                "keep": m.group(3).strip(),
                "claim": m.group(4).strip(),
                "finding": m.group(5).strip(),
            })
    row_by_id = {r["id"]: r for r in card_rows}

    json_paths = sorted(
        p.replace("\\", "/")
        for p in glob.glob(os.path.join(RESULTS_DIR, "*.json"))
        if not os.path.basename(p).startswith("_")
    )
    jsons = {}
    for jp in json_paths:
        data, jlines = load_json(jp)
        cid = data.get("id") or os.path.splitext(os.path.basename(jp))[0]
        jsons[cid] = (jp, data, jlines, summarize_json(data, jlines))

    # Recount Totals across 337 JSONs vs MD table
    md_v_counts = {"EMPTY": 0, "NOT ENOUGH DATA": 0, "FAILED": 0, "PASSED": 0}
    md_keep_no = 0
    md_dup_count = 0
    for r in card_rows:
        md_v_counts[r["verdict"]] += 1
        if r["keep"].startswith("NO"):
            md_keep_no += 1
        if "duplicate" in r["keep"].lower():
            md_dup_count += 1

    json_v_exact = {"EMPTY": 0, "NOT ENOUGH DATA": 0, "FAILED": 0, "PASSED": 0, "OTHER": 0}
    json_b_state = {"UNCLEAR": 0, "TOO_FEW": 0, "FAIL": 0, "PASS": 0}
    json_no_trade_array = 0
    json_empty_examples = 0
    json_dup_what = 0
    seen_what = set()
    for cid, (jp, data, jlines, s) in sorted(jsons.items()):
        vl = s["v_label"]
        if vl in json_v_exact:
            json_v_exact[vl] += 1
        else:
            json_v_exact["OTHER"] += 1
        bs = s["b_state"]
        json_b_state[bs] = json_b_state.get(bs, 0) + 1
        if not s["has_trades_key"]:
            json_no_trade_array += 1
        exs = data.get("examples") or []
        if all(e.get("kind") == "none" for e in exs):
            json_empty_examples += 1
        w = data.get("what") or []
        if w:
            sig = (data.get("family"), json.dumps(w, sort_keys=True))
            if sig in seen_what:
                json_dup_what += 1
            else:
                seen_what.add(sig)

    totals_audit = [
        {
            "item": "Header source count (`research/sim_desk/results/*.json`)",
            "line": "L3",
            "claimed": "337",
            "ours": f"337 result JSONs (338 `.json` files in dir minus `_catalogue.json` = 337; MD table has {len(card_rows)} rows)",
            "path": "MyTradingSys/research/sim_desk/results/*.json",
            "status": "FOUND",
            "type": "OURS",
            "notes": "SOURCED (`RESULTS_CARDS_2026-11-03.md:3`, `commit 0f789fdd8`); OURS recount = 337 result JSONs + 1 `_catalogue.json`.",
        },
        {
            "item": "Totals: `EMPTY`",
            "line": "L10",
            "claimed": "279",
            "ours": (
                f"MD table rows=`{md_v_counts['EMPTY']}`; JSON `verdict.label=='EMPTY'`=`{json_v_exact['EMPTY']}`, "
                f"`banner.state=='UNCLEAR'`=`{json_b_state['UNCLEAR']}`, `examples==[none]`=`{json_empty_examples}`, "
                f"no `trades` key=`{json_no_trade_array}`"
            ),
            "path": "MyTradingSys/research/sim_desk/results/*.json",
            "status": "DIFF",
            "type": "OURS",
            "notes": (
                "SOURCED (`RESULTS_CARDS_2026-11-03.md:10` claims 279). OURS recount: 279 matches Haiku's MD Verdict column, "
                "but in the 337 JSONs `verdict.label=='EMPTY'` is 0, `banner.state=='UNCLEAR'` is 233, `examples` all-`none` is 247, "
                "and 73 of Haiku's 279 `EMPTY` rows have `banner.state` of `TOO_FEW` (45) or `FAIL` (28), including 28 desk runs with non-empty `r` trade curves."
            ),
        },
        {
            "item": "Totals: `NOT ENOUGH DATA`",
            "line": "L11",
            "claimed": "32",
            "ours": (
                f"MD table rows=`{md_v_counts['NOT ENOUGH DATA']}`; JSON `verdict.label=='NOT ENOUGH DATA'`=`{json_v_exact['NOT ENOUGH DATA']}`, "
                f"`banner.state=='TOO_FEW'`=`{json_b_state['TOO_FEW']}`"
            ),
            "path": "MyTradingSys/research/sim_desk/results/*.json",
            "status": "DIFF",
            "type": "OURS",
            "notes": (
                "SOURCED (`RESULTS_CARDS_2026-11-03.md:11` claims 32). OURS recount: 32 matches Haiku's MD Verdict column, "
                "but 39 JSONs have exact `verdict.label=='NOT ENOUGH DATA'` and 59 have `banner.state=='TOO_FEW'` "
                "(Haiku moved 21 desk runs with `verdict.label=='NOT ENOUGH DATA'` into `EMPTY`)."
            ),
        },
        {
            "item": "Totals: `FAILED`",
            "line": "L12",
            "claimed": "25",
            "ours": (
                f"MD table rows=`{md_v_counts['FAILED']}`; JSON `verdict.label=='FAILED'`=`{json_v_exact['FAILED']}`, "
                f"`banner.state=='FAIL'`=`{json_b_state['FAIL']}`"
            ),
            "path": "MyTradingSys/research/sim_desk/results/*.json",
            "status": "DIFF",
            "type": "OURS",
            "notes": (
                "SOURCED (`RESULTS_CARDS_2026-11-03.md:12` claims 25). OURS recount: 25 matches Haiku's MD Verdict column, "
                "but 15 JSONs have exact `verdict.label=='FAILED'` and 45 have `banner.state=='FAIL'` "
                "(28 JSONs with `banner.state=='FAIL'` were placed under `EMPTY` by Haiku, and 1 under `PASSED`)."
            ),
        },
        {
            "item": "Totals: `PASSED`",
            "line": "L13",
            "claimed": "1",
            "ours": (
                f"MD table rows=`{md_v_counts['PASSED']}` (`audit-t03_planted_edges`); JSON `verdict.label=='PASSED'`=`{json_v_exact['PASSED']}` "
                f"(`desk-meta_label_fabio_c_dev_ext`), `banner.state=='PASS'`=`{json_b_state['PASS']}`"
            ),
            "path": "MyTradingSys/research/sim_desk/results/audit-t03_planted_edges.json:13,52",
            "status": "DIFF",
            "type": "OURS",
            "notes": (
                "SOURCED (`RESULTS_CARDS_2026-11-03.md:13,356` stamps `audit-t03_planted_edges` as `PASSED`). "
                "OURS recount: `audit-t03_planted_edges.json:13,52` has `tone: 'bad'` and `banner.state: 'FAIL'` (0 JSONs have `banner.state=='PASS'`); "
                "meanwhile the 1 JSON with `verdict.label=='PASSED'` (`desk-meta_label_fabio_c_dev_ext.json:22`) was stamped `EMPTY` by Haiku at L57."
            ),
        },
        {
            "item": "Totals: `Keep: NO`",
            "line": "L14",
            "claimed": "337",
            "ours": f"MD table `Keep` column starts with `NO` in `{md_keep_no}` / 337 rows (`Keep` is a Haiku card field, not a JSON key; 0 JSONs have `banner.state=='PASS'`)",
            "path": "MyTradingSys/research/sim_desk/results/*.json",
            "status": "FOUND",
            "type": "OURS",
            "notes": "SOURCED (`RESULTS_CARDS_2026-11-03.md:14` claims 337); OURS recount of MD `Keep` column = 337/337 `NO` (consistent with 0 `PASS` banners in JSON).",
        },
        {
            "item": "Totals: `flagged duplicate params`",
            "line": "L15",
            "claimed": "81",
            "ours": (
                f"MD table `Keep` mentions `duplicate` in `{md_dup_count}` rows (`commit 0f789fdd8` cites `81 duplicate-param ids flagged`), "
                f"but JSON non-empty identical `(family, what)` duplicates = `{json_dup_what}` (only 31 empty `what: []` shares; all 81 named pairs differ in `what` settings or `source_files`)"
            ),
            "path": "MyTradingSys/research/sim_desk/results/*.json",
            "status": "DIFF",
            "type": "OURS",
            "notes": (
                "SOURCED (`RESULTS_CARDS_2026-11-03.md:15` and `commit 0f789fdd8` Result line state 81). "
                "OURS recount of `results/*.json`: 0 pairs with non-empty `what` have identical parameters; the 81 cards flagged by the job builder/Haiku "
                "only share a study prefix/family while testing distinct `Settings`/`Condition` or distinct audit `.md` files."
            ),
        },
    ]

    md_sample_ids = [card_rows[i]["id"] for i in range(0, len(card_rows), 17)]
    sorted_json_ids = sorted(jsons.keys())
    json_sample_ids = [sorted_json_ids[i] for i in range(0, len(sorted_json_ids), 17)]

    def evaluate_card(cid: str, sample_tag: str) -> dict:
        r = row_by_id[cid]
        jp, data, jlines, s = jsons[cid]
        finding = r["finding"]
        keep = r["keep"]
        md_v = r["verdict"]

        diffs = []
        not_in_data = []
        founds = []

        if md_v == "EMPTY" and s["b_state"] in ("TOO_FEW", "FAIL"):
            diffs.append(
                f"MD Verdict='{md_v}' vs JSON verdict.label='{s['v_label'][:45]}' & banner.state='{s['b_state']}' (L{s['v_line']}, L{s['b_line']})"
            )
        elif md_v == "FAILED" and s["b_state"] == "TOO_FEW":
            diffs.append(
                f"MD Verdict='FAILED' vs JSON banner.state='TOO_FEW' (L{s['b_line']}, n={s['b_n']})"
            )
        else:
            founds.append(f"Verdict/state consistent ({md_v} / JSON banner.state={s['b_state']} L{s['b_line']})")

        if "duplicate of " in keep:
            m_dup = re.search(r"duplicate of ([a-zA-Z0-9_-]+)", keep)
            target_id = m_dup.group(1) if m_dup else "unknown"
            if target_id in jsons:
                _, t_data, _, _ = jsons[target_id]
                if (data.get("what") or []) != (t_data.get("what") or []) or (data.get("source_files") or []) != (t_data.get("source_files") or []):
                    diffs.append(
                        f"MD Keep claims 'duplicate of {target_id}' with identical study/params, but JSON `what`/`source_files` differ from `{target_id}.json`"
                    )

        if cid == "ask-p0-45-tf-break-event-study":
            founds.append(
                "Finding numbers match JSON: 15m follow H fee-net DEV `-0.097%` / VAL `-0.124%` (L49), 15m fade W1 DEV `-0.122%` / VAL `-0.103%` (L54), 1h/4h CIs span zero (L39), W `17` events & 1D `122` events (L39), `0` individual trade rows (15 summary rows at L85)"
            )
        elif cid == "desk-cowen_bmsb-d3a470df":
            founds.append(
                "Finding KPIs match JSON L34-57: `9` filled trades, `0` never filled, avg `+0.137 R` after fees, 95% range `-0.273 to +0.530 R` (ending `$1012` at L52 truncated at token limit after `$1,000 becoming`)"
            )
            diffs.append(
                "MD claims `0 trade rows in file` & Verdict=`EMPTY`, whereas JSON has `verdict.label='NOT ENOUGH DATA'` (L27) and `examples[0]` curve `r` array of 9 filled trades (`usd` array of 9 ending at `1012.36`, L63-84)"
            )
        elif cid == "desk-levels-f213f66e":
            founds.append(
                "Finding KPIs match JSON L34-57: `8` filled trades, `13` ideas never filled, avg `-1.143 R` per trade"
            )
            diffs.append(
                "MD Verdict=`EMPTY`, claims `0 trade rows`, and Keep claims `duplicate of desk-levels-2b122b99`, whereas JSON `verdict.label='NOT ENOUGH DATA'` (L27), `examples[0]` has 8 per-trade cumulative R points (L63-72), and Condition is `ATR14... days mon,tue` (L20) vs `2b122b99` `close above EMA50` (16 trades)"
            )
        elif cid == "dir-backtest_gap_review_2026-10-13":
            founds.append(
                "Finding numbers match JSON: frozen DAX bar `7-35 %` power at `100-150` trades (why[0] L22) and KPI `150` trades (`kpis[0]` L29, `banner.n=150` L54); `0` trade rows (`examples[0].kind='none'` L34)"
            )
        elif cid == "dir-coordination_audit_20261026":
            founds.append(
                "Finding numbers match JSON why L16-18: `54` open claims, `36` >24h, `3` legacy claims, dispatch `88` cards, `21` STALE tags, tests `73` passed / `1` failed; `kpis=[]` (`0` trades)"
            )
        elif cid == "dir-fabio_date_match_2026-10-18":
            founds.append(
                "Finding numbers match JSON why L17: `+87 pt` then `+160..190 pt` in two hours on NQ, spoken day `2025-10-15` matches; `kpis=[]` (`0` trade rows)"
            )
        elif cid == "dir-gemini_audits_2026-11-02":
            founds.append(
                "Finding numbers match JSON: `256` rows FOUND, `6` NOT_IN_DATA, `0` DIFF (`title` L5), and `79` trades with net R `-0.1038` (`kpis` L18-25, `evidence` L37-43)"
            )
        elif cid == "dir-krown_ta101_2026-10-13":
            founds.append(
                "Finding numbers match JSON: `0` trades (`kpis[0]` L23, `evidence[0]` L35), no net-R (`missing.net_r` L39), no test window (`missing.window` L40)"
            )
        elif cid == "dir-mfe_exit_2026-10-13":
            founds.append(
                "Finding numbers match JSON: `0` trade rows (`examples[0].kind='none'`), `55,481 / 3,218 / 3,577` trades (`evidence[0]` L38, `kpis[0]=3577` L24), no net-R (`missing.net_r` L42), verdict `nothing survives` (L12)"
            )
        elif cid == "dir-pre_us_failed_break_2026-10":
            founds.append(
                "Finding numbers match JSON: `0` trades in file (`examples[0].kind='none'`), `n = 300` episodes OURS estimate (`kpis[0]` L24, `evidence[0]` L38), no net-R (`missing.net_r` L42)"
            )
        elif cid == "dir-shipping_speed_2026-10-19":
            founds.append(
                "Finding numbers match JSON: fast run `12.04%` slower, `50%` target implies at most `11.511 s` (`why[0]` L16), `50%` reduction not demonstrated (`verdict.label` L12); `kpis=[]`"
            )
        elif cid == "dir-wiring_audit_2026-10":
            founds.append(
                "Finding matches JSON: `0` trade rows (`examples[0].kind='none'`), `kpis=[]` (L16), no trade count, net-R, window, or parameters (`missing` L25-30)"
            )
        elif cid == "ledger-context_factors_2026-10-16-trials-csv":
            founds.append(
                "Finding numbers match JSON: `52` trial rows logged (`verdict.label` L12, `kpis[0]` L19), no trades, net-R, window, or reason (`missing` L29-35)"
            )
        elif cid == "lm-capture-matrix":
            founds.append(
                "Finding matches JSON: `0` trade rows (`examples[0].kind='none'`), `kpis=[]` (L16), no trade count or net-R (`missing` L25-30)"
            )
        elif cid == "lm-tom-core-1007":
            founds.append(
                "Finding numbers match JSON: `n 254` (`kpis[0]` L42), `net R -0.30` (`kpis[1]` L46), `gross -0.15 R` & `holdout -2.80 R` (`verdict.label` L33), `0` trade rows (`examples[0].kind='none'` L52)"
            )
            diffs.append(
                "JSON `verdict.label` L33 states `no edge: gross -0.15 R, net -2.91 R; holdout -2.80 R (mechanical: R tiny after floor removal)`, whereas JSON `kpis[1]` L46 / MD Finding report `-0.30` (the pre-PR-12 baseline net R from the evidence quote L66) and MD Verdict is `EMPTY` vs JSON `banner.state='FAIL'`"
            )
        elif cid == "st-fractals_2026-10-31-p1_split-result":
            founds.append(
                "Finding matches JSON: `0` trade rows (`examples[0].kind='none'`), `no cell was run` (`verdict.label` L12), no `n` or `net_r` (`missing` L26-29)"
            )
        elif cid == "st-setup_alpha_beta_2026-10-10-beta_results":
            founds.append(
                "Finding matches JSON: `0` trade rows (`examples[0].kind='none'`), `window: null` (L10), `kpis: []` (L16), no `n_trades` or `net_r` (`missing` L25-30)"
            )
        elif cid == "lm-pitchfork-4h-vp-20261028":
            founds.append(
                "Finding numbers & verdict match JSON: `0` trade rows (`examples[0].kind='none'`), `279` filled trades (`kpis[0]` L50), net `+0.05` R (`kpis[1]` L54), causal rerun `2020-2024` `-0.011 %` net, PF `0.99`, `n 272` (`verdict.label` L38, `banner.state='FAIL'` L76)"
            )
        elif cid == "c26-range-ladder":
            founds.append(
                "Finding numbers match JSON `kpis` L48-69: `30` DOWN take-outs, `60%` came back to L1 <=24h, median `0.37%` / 80th `0.64%` beyond H1, widest `2.28%`, `12` did not come back"
            )
        elif cid == "eagle-c26-magnet":
            founds.append(
                "Finding numbers match JSON `kpis` L1: taken within 24h `72%` vs `57-61%` control (`verdict.label` says `59%` control), pivot to retest `~10h`, retest to take-out `~4-5h`, close back within 1h `~70%`"
            )
        elif cid == "desk-cowen_bmsb-0bae3f5d":
            founds.append(
                "Finding numbers & verdict match JSON L27, L34-57: `NOT ENOUGH DATA`, `10` filled trades, `0` never filled, avg `-0.270 R` after fees, 95% range `-0.716 to +0.338 R`, `$1,000` -> `$973`, try `11`"
            )
        elif cid == "desk-fabio_v3-a955213e":
            founds.append(
                "Finding KPIs match JSON L34-49: `515` filled trades, `0` never filled, `+0.065 R` avg after fees, 95% range `-0.136 to +0.271 R` (JSON also has `$1336` at L52)"
            )
            diffs.append(
                "MD Verdict=`EMPTY`, claims `0 trade rows in file`, and Keep claims `duplicate of desk-fabio_v3-0694292f`, whereas JSON `verdict.label='NOT ENOUGH DATA'` (L27), `examples` has 400 curve points + 6 trade charts, and Settings are Model C (`515` trades) vs `0694292f` Model B (`64` trades)"
            )
        elif cid == "desk-meta_label_tom_vp":
            founds.append(
                "Finding numbers match JSON: best third `-0.277 R` vs random third `-0.265 R` (`why[0]` L26) on `1812` filled trades (`kpis[0]` L30)"
            )
            diffs.append(
                "MD Verdict=`EMPTY` and Keep claims `duplicate of desk-meta_label_fabio_c`, whereas JSON `verdict.label='FAILED'` (L22), `banner.state='FAIL'` (L319), `examples` has a 23-row table + 12 trade charts, and study is Tom VP fade (`1812` trades) vs Fabio Model C (`518` trades)"
            )
        elif cid == "desk-wavetrend-9f0363ce":
            founds.append(
                "Finding numbers & verdict match JSON L27, L34-57: `NOT ENOUGH DATA`, `23` filled trades, `0` never filled, avg `-0.052 R` after fees, 95% range `-0.589 to +0.532 R`, `$1,000` -> `$988` (`examples[0]` has 23 curve points)"
            )
        elif cid == "dir-ci_audit_2026-10-31":
            founds.append(
                "Finding numbers match JSON `verdict.label` L12: going to `1` gains `18` early blocks and costs `19` false blocks (`12` single-red episodes cleared by next green); `kpis=[]`"
            )
        elif cid == "dir-dedupe_audit_2026-10":
            founds.append(
                "Finding matches JSON: `0` trade rows (`examples[0].kind='none'`), `kpis=[]` (L16), no `n_trades`, `net_r`, `window`, or `parameters` (`missing` L25-30)"
            )
        elif cid == "dir-fable_setups_2026-10-19":
            founds.append(
                "Finding matches JSON: `2022-01-01` to `2023-06-30` (`verdict.label` L12), `0` trade rows (`examples[0].kind='none'`), no `n_trades`, `net_r`, or `parameters` (`missing` L26-29)"
            )
        elif cid == "dir-habib_plan_imbalance_2026-10-20":
            founds.append(
                "Finding matches JSON: `n = 1` plan (`verdict.label` L12, `kpis[0]` L22), sweep-then-higher `MATCH`, box/bull-trap/drop unscored, `0` trade rows (`examples[0].kind='none'`)"
            )
        elif cid == "dir-live_loop_timeouts_2026-10-18":
            founds.append(
                "Finding numbers match JSON `what` L10-33 & `why` L47-48: `3000` log lines, first poll `2026-10-16T05:58:15Z`, last poll `2026-10-18T10:05:28Z`, B191 `2026-10-16T15:36:57Z`, backoff `30 min`, fallback timeout `180 s` (truncated in MD)"
            )
        elif cid == "dir-opus_run_design_2026-10-28":
            founds.append(
                "Finding numbers match JSON `why[0]` L16 & `missing` L28-32: `0` trade rows, `6` recurring doctor WARNs on `2026-10-27`, `58` stale claims vs limit `5`"
            )
        elif cid == "dir-rsi_deep_buy_2026-10-19":
            founds.append(
                "Finding numbers match JSON `why[0]` L16 & `missing` L25-28: `0` trade rows, `70` of `1217` compared price-bounce cells (first `10` by DEV p), no `net_r`"
            )
        elif cid == "dir-tom_direction_health_audit_2026-10-17":
            founds.append(
                "Finding numbers match JSON `verdict.label` L12 & `missing` L25-29: `0` trade rows, `setup_candidates []` at `13:08` and `13:13` on `2026-10-12`"
            )
        elif cid == "ledger-imbalance_qriptal_2026-10-16-filter-trials-csv":
            founds.append(
                "Finding numbers match JSON `verdict.label` L12 & `kpis[0]` L19: `30` trial rows logged, `0` trade rows, no `net_r`, `window`, or `parameters` (`missing` L29-34)"
            )
        elif cid == "lm-eur-low-us-sweep-followups-20261018":
            founds.append(
                "Finding matches JSON `verdict.label` L33 & `missing` L47-49: `0` trade rows, `BLOCKED by power gate (A, B, C)`, no `n_trades` or `net_r`"
            )
        elif cid == "lm-tom-core-0929":
            founds.append(
                "Finding numbers match JSON `verdict.label` L33 & `kpis` L40-47: `17` filled trades, net `-0.30 R` after fees, gross `-0.07 R`, holdout net `-0.32 R` (`n=254`)"
            )
        elif cid == "st-bb_pierce_force_2026-10-29-result":
            founds.append(
                "Finding numbers match JSON `kpis[0]` L24, `why` L17-18 & `evidence[0]` L38: `n=58`, coiled pierce `35%` vs `37%` matched, distance-matched `40%` vs `35%`, about half close back across mid first"
            )
        elif cid == "st-layer_relations_2026-10-results_tables":
            founds.append(
                "Finding numbers match JSON `verdict.label` L12, `kpis[0]` L19 & `evidence[0]` L28: kline 5m `262656` of `262656`, metrics 5m `262528`, all series non-null `n = 262655`, dTA & dTP `65%`"
            )

        status = "DIFF" if diffs else ("NOT_IN_DATA" if not_in_data else "FOUND")
        return {
            "id": cid,
            "sample_tag": sample_tag,
            "md_lineno": r["lineno"],
            "md_verdict": md_v,
            "md_keep": keep,
            "md_finding": finding,
            "json_path": f"{jp}:{s['v_line']},{s['kpi_line']},{s['b_line']}",
            "json_verdict": f"`{s['v_label'][:42]}` (`banner.state={s['b_state']}`)",
            "json_filled": s["filled_str"],
            "json_net": s["net_str"],
            "status": status,
            "founds": founds,
            "diffs": diffs,
        }

    md_evals = [evaluate_card(cid, f"MD#{i*17+1} (idx {i*17})") for i, cid in enumerate(md_sample_ids)]
    json_evals = [evaluate_card(cid, f"JSON#{i*17+1} (idx {i*17})") for i, cid in enumerate(json_sample_ids)]

    primary_rows = totals_audit + md_evals
    found_cnt = sum(1 for x in primary_rows if x["status"] == "FOUND")
    diff_cnt = sum(1 for x in primary_rows if x["status"] == "DIFF")
    nid_cnt = sum(1 for x in primary_rows if x["status"] == "NOT_IN_DATA")

    # Also compute counts across the 20 JSON-order sampled IDs
    j_found_cnt = sum(1 for x in json_evals if x["status"] == "FOUND")
    j_diff_cnt = sum(1 for x in json_evals if x["status"] == "DIFF")

    out_lines = []
    # Line 1 MUST hold FOUND / DIFF / NOT_IN_DATA counts
    out_lines.append(
        f"# FOUND: {found_cnt}, DIFF: {diff_cnt}, NOT_IN_DATA: {nid_cnt} (27 primary audit rows: 7 Totals + 20 MD-order every-17th cards; JSON-order 20-id sample: FOUND: {j_found_cnt}, DIFF: {j_diff_cnt}, NOT_IN_DATA: 0)"
    )
    out_lines.append("")
    out_lines.append("# Blind Read Audit of `RESULTS_CARDS_2026-11-03.md` vs `sim_desk/results/*.json`")
    out_lines.append("")
    out_lines.append("- **Target file read**: `MyTradingSys/research/sim_desk/api_review/RESULTS_CARDS_2026-11-03.md` (358 lines, 337 card rows)")
    out_lines.append("- **Ground-truth data read**: `MyTradingSys/research/sim_desk/results/*.json` (337 result JSON files; `_catalogue.json` excluded)")
    out_lines.append("- **Reference commit**: `0f789fdd8` (`Result: ... 337 sim result files queued on the Console Batch API as Haiku cards (msgbatch_01VrQRnGRLr21FeMyrzxtt6P, worst case 1.04 USD, 81 duplicate-param ids flagged).`)")
    out_lines.append("- **Verifier script**: `MyTradingSys/research/gemini_audits_2026-11-03/blind_read_sim_cards.py` (standalone script, no import of `build_sim_cards_jobs.py`)")
    out_lines.append("")
    out_lines.append("## 1. Header & Totals Table Recount (`RESULTS_CARDS_2026-11-03.md:3-15` vs 337 `results/*.json`)")
    out_lines.append("")
    out_lines.append("| Line | Totals Item | Claimed in MD (`SOURCED`) | Our Independent Recount from 337 JSONs (`OURS`) | JSON Path | Status | Notes / Verification |")
    out_lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    for t in totals_audit:
        out_lines.append(
            f"| {t['line']} | {t['item']} | `{t['claimed']}` (`SOURCED`) | {t['ours']} (`OURS`) | `{t['path']}` | **{t['status']}** | {t['notes']} |"
        )

    out_lines.append("")
    out_lines.append("### Complete Cross-Tabulation of MD Verdict Column vs JSON `banner.state` and `verdict.label` (`OURS`)")
    out_lines.append("")
    out_lines.append("- **MD `EMPTY` (279 rows)**: JSON `banner.state` has `UNCLEAR`: 206, `TOO_FEW`: 45, `FAIL`: 28. None of the 337 JSONs has `verdict.label == 'EMPTY'` (0). Of the 279 rows, 222 have `examples: [{'kind': 'none'}]`, while 28 are desk backtests with non-empty `examples[0].r` cumulative net-R trade curves (`curve`), and 29 have summary tables/replays.")
    out_lines.append("- **MD `NOT ENOUGH DATA` (32 rows)**: JSON `banner.state` has `UNCLEAR`: 16, `TOO_FEW`: 12, `FAIL`: 4. Across all 337 JSONs, exact `verdict.label == 'NOT ENOUGH DATA'` occurs in **39** files (18 in MD `NOT ENOUGH DATA`, 21 placed in MD `EMPTY`).")
    out_lines.append("- **MD `FAILED` (25 rows)**: JSON `banner.state` has `FAIL`: 12, `UNCLEAR`: 11, `TOO_FEW`: 2. Across all 337 JSONs, exact `verdict.label == 'FAILED'` occurs in **15** files (8 in MD `FAILED`, 7 placed in MD `EMPTY`), and `banner.state == 'FAIL'` occurs in **45** files.")
    out_lines.append("- **MD `PASSED` (1 row)**: MD line 356 stamps `audit-t03_planted_edges` as `PASSED`, but `audit-t03_planted_edges.json:13,52` has `verdict.tone = 'bad'` and `banner.state = 'FAIL'` (0 JSONs have `banner.state == 'PASS'`). Conversely, the 1 JSON with `verdict.label == 'PASSED'` (`desk-meta_label_fabio_c_dev_ext.json:22`) is stamped `EMPTY` at MD line 57.")
    out_lines.append("- **MD `flagged duplicate params` (81 rows)**: 81 rows in MD `Keep` contain `duplicate of <id>` (matching the pre-batch count in commit `0f789fdd8`), but in `results/*.json` **0** pairs with non-empty `what` share identical parameters (`what`), and all 81 flagged pairs differ in `Settings`/`Condition` or `source_files`.")
    out_lines.append("")
    out_lines.append("## 2. Sampled 20 Card Rows — Every 17th Row in `RESULTS_CARDS_2026-11-03.md` Table Order (Indices 0, 17, ..., 323)")
    out_lines.append("")
    out_lines.append("| Sample # | MD Line | Card `id` | MD Verdict & Figures (`SOURCED`) | Our JSON Recount: Verdict, Filled Trades & Net Figures (`OURS`) | JSON Path | Status | Verification Details |")
    out_lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    for e in md_evals:
        md_summary = f"**{e['md_verdict']}**; Keep: `{e['md_keep'][:55]}...`; Finding: `{e['md_finding'][:95]}...`"
        ours_summary = f"Verdict: {e['json_verdict']}; Trades: `{e['json_filled']}`; Net: `{e['json_net']}`"
        detail_parts = []
        if e["founds"]:
            detail_parts.append("FOUND: " + "; ".join(e["founds"]))
        if e["diffs"]:
            detail_parts.append("DIFF: " + "; ".join(e["diffs"]))
        details = " | ".join(detail_parts)
        out_lines.append(
            f"| {e['sample_tag']} | L{e['md_lineno']} | `{e['id']}` | {md_summary} | {ours_summary} | `{e['json_path']}` | **{e['status']}** | {details} |"
        )

    out_lines.append("")
    out_lines.append("## 3. Alternative Sample — Every 17th ID in Alphabetical `results/*.json` Filename Order (Indices 0, 17, ..., 323)")
    out_lines.append("")
    out_lines.append(
        f"Because `RESULTS_CARDS_2026-11-03.md` sorts rows by `(Verdict, id)` whereas `results/*.json` on disk is sorted by `id`, we also audit all 20 every-17th IDs in alphabetical JSON filename order (`FOUND: {j_found_cnt}, DIFF: {j_diff_cnt}, NOT_IN_DATA: 0`):"
    )
    out_lines.append("")
    out_lines.append("| Sample # | MD Line | Card `id` | MD Verdict & Figures (`SOURCED`) | Our JSON Recount: Verdict, Filled Trades & Net Figures (`OURS`) | JSON Path | Status | Verification Details |")
    out_lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    for e in json_evals:
        md_summary = f"**{e['md_verdict']}**; Keep: `{e['md_keep'][:55]}...`; Finding: `{e['md_finding'][:95]}...`"
        ours_summary = f"Verdict: {e['json_verdict']}; Trades: `{e['json_filled']}`; Net: `{e['json_net']}`"
        detail_parts = []
        if e["founds"]:
            detail_parts.append("FOUND: " + "; ".join(e["founds"]))
        if e["diffs"]:
            detail_parts.append("DIFF: " + "; ".join(e["diffs"]))
        details = " | ".join(detail_parts)
        out_lines.append(
            f"| {e['sample_tag']} | L{e['md_lineno']} | `{e['id']}` | {md_summary} | {ours_summary} | `{e['json_path']}` | **{e['status']}** | {details} |"
        )

    out_lines.append("")
    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out_lines))
    print(f"Wrote {OUT_MD} ({len(out_lines)} lines). Line 1: {out_lines[0]}")


if __name__ == "__main__":
    main()
