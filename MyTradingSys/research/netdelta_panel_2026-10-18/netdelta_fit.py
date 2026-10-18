"""CoinGlass Net Delta panel candidate fit and regression.

Card: identify-the-coinglass-net-delta-panel-u
Fits Net Delta panel steps against:
  - Candidate A: sign(close-open) * abs(dOI) (Binance public openInterestHist 5m)
  - Candidate A_signed: sign(close-open) * dOI
  - Candidate B: Binance perp taker delta
  - Candidate C: Binance spot taker delta
  - Candidate D: A + B family
"""
import json
import math
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"


def step_formula(
    open_price: float,
    close_price: float,
    oi_open: Optional[float] = None,
    oi_close: Optional[float] = None,
    d_oi: Optional[float] = None,
) -> float:
    """Formula for test_step_formula:

    close < open with OI up gives a negative step.
    close > open with OI down gives a negative step.
    flat bar gives 0.
    """
    if d_oi is None:
        if oi_open is None or oi_close is None:
            raise ValueError("Either d_oi or both oi_open and oi_close must be provided")
        d_oi = oi_close - oi_open

    if close_price > open_price:
        sign = 1.0
    elif close_price < open_price:
        sign = -1.0
    else:
        sign = 0.0

    return sign * d_oi


def candidate_a_step(
    open_price: float,
    close_price: float,
    oi_open: Optional[float] = None,
    oi_close: Optional[float] = None,
    d_oi: Optional[float] = None,
    use_abs: bool = True,
) -> float:
    """Candidate A: sign(close-open) * abs(dOI) per SCREENSHOT_OBSERVATIONS.md:38."""
    if d_oi is None:
        if oi_open is None or oi_close is None:
            raise ValueError("Either d_oi or both oi_open and oi_close must be provided")
        d_oi = oi_close - oi_open

    if close_price > open_price:
        sign = 1.0
    elif close_price < open_price:
        sign = -1.0
    else:
        sign = 0.0

    magnitude = abs(d_oi) if use_abs else d_oi
    return sign * magnitude


def compute_kline_delta(kline_rows: List[List[Any]]) -> Tuple[float, float, float]:
    """Given a list of 1m Binance klines [open_time, open, high, low, close, vol, ..., tbv, ...],

    returns (taker_delta, open_price, close_price).
    taker_delta = sum(2 * tbv - vol) over the rows.
    """
    if not kline_rows:
        return 0.0, 0.0, 0.0
    open_price = float(kline_rows[0][1])
    close_price = float(kline_rows[-1][4])
    taker_delta = sum(2.0 * float(k[9]) - float(k[5]) for k in kline_rows)
    return taker_delta, open_price, close_price


def get_oi_change(
    oi_rows: List[Dict[str, Any]],
    tf: str,
    t_start: int,
    t_end: int,
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """Returns (oi_start, oi_end, d_oi).

    For sub-5m timeframes (1m, 3m), Binance 5m openInterestHist does not provide 1m resolution;
    proration or window delta is returned if available.
    """
    if not oi_rows or len(oi_rows) < 2:
        return None, None, None

    oi_sorted = sorted(oi_rows, key=lambda x: x["timestamp"])

    if tf in ("1m", "3m"):
        # 5m OI resolution: report prorated 5m change over the enclosing 5m bar
        oi_start = float(oi_sorted[0]["sumOpenInterest"])
        oi_end = float(oi_sorted[-1]["sumOpenInterest"])
        delta_5m = oi_end - oi_start
        factor = (3.0 / 5.0) if tf == "3m" else (1.0 / 5.0)
        d_oi = delta_5m * factor
        return oi_start, oi_end, d_oi

    # Find closest OI records to t_start and t_end
    oi_start_cand = [x for x in oi_sorted if x["timestamp"] <= t_start + 60000]
    oi_end_cand = [x for x in oi_sorted if x["timestamp"] >= t_end - 60000]

    oi_0 = float(oi_start_cand[-1]["sumOpenInterest"]) if oi_start_cand else float(oi_sorted[0]["sumOpenInterest"])
    oi_1 = float(oi_end_cand[0]["sumOpenInterest"]) if oi_end_cand else float(oi_sorted[-1]["sumOpenInterest"])

    return oi_0, oi_1, (oi_1 - oi_0)


def load_dataset() -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    with open(DATA_DIR / "binance_oi_series.json") as f:
        oi_pulls = json.load(f)
    with open(DATA_DIR / "binance_perp_klines.json") as f:
        perp_pulls = json.load(f)
    with open(DATA_DIR / "binance_spot_klines.json") as f:
        spot_pulls = json.load(f)
    return oi_pulls, perp_pulls, spot_pulls


def run_fit(rows: Optional[List[Tuple[str, float, str]]] = None) -> Dict[str, Any]:
    oi_pulls, perp_pulls, spot_pulls = load_dataset()

    # Default to the primary cited rows with valid steps (n=7)
    if rows is None:
        rows = [
            ("C04-09", -50.9, "5m"),
            ("C07-08", -18.0, "5m"),
            ("R-12_forming", -406.0, "12h"),
            ("R-12_sep23", -7000.0, "12h"),
            ("R-25_3m_1327", -550.0, "3m"),
            ("R-25_1m_1230", -79.0, "1m"),
            ("R-25_1m_1231", -21.0, "1m"),
        ]

    per_row = []
    for row_id, panel_val, tf in rows:
        k_perp = perp_pulls[row_id]
        k_spot = spot_pulls[row_id]
        oi_records = oi_pulls[row_id]

        perp_delta, open_p, close_p = compute_kline_delta(k_perp)
        spot_delta, _, _ = compute_kline_delta(k_spot)

        t_start = k_perp[0][0]
        t_end = k_perp[-1][6]
        _, _, d_oi = get_oi_change(oi_records, tf, t_start, t_end)

        if d_oi is not None:
            cand_a = candidate_a_step(open_p, close_p, d_oi=d_oi, use_abs=True)
            cand_a_signed = candidate_a_step(open_p, close_p, d_oi=d_oi, use_abs=False)
        else:
            cand_a = None
            cand_a_signed = None

        cand_b = perp_delta
        cand_c = spot_delta
        cand_d = (cand_a + cand_b) if cand_a is not None else None

        # Compute ratios panel / candidate
        def calc_ratio(c_val):
            if c_val is None or math.isclose(c_val, 0.0, abs_tol=1e-6):
                return None
            return panel_val / c_val

        per_row.append({
            "id": row_id,
            "panel": panel_val,
            "tf": tf,
            "open": open_p,
            "close": close_p,
            "d_oi": d_oi,
            "cand_a": cand_a,
            "cand_a_signed": cand_a_signed,
            "cand_b": cand_b,
            "cand_c": cand_c,
            "cand_d": cand_d,
            "ratio_a": calc_ratio(cand_a),
            "ratio_a_signed": calc_ratio(cand_a_signed),
            "ratio_b": calc_ratio(cand_b),
            "ratio_c": calc_ratio(cand_c),
            "ratio_d": calc_ratio(cand_d),
        })

    # Summary statistics per candidate
    candidates = ["cand_a", "cand_a_signed", "cand_b", "cand_c", "cand_d"]
    ratio_keys = ["ratio_a", "ratio_a_signed", "ratio_b", "ratio_c", "ratio_d"]
    summary = {}

    n_rows = len(per_row)
    for c_key, r_key in zip(candidates, ratio_keys):
        ratios = [r[r_key] for r in per_row if r[r_key] is not None]
        signs_agree = sum(
            1 for r in per_row
            if r[c_key] is not None and (
                (r["panel"] > 0 and r[c_key] > 0) or
                (r["panel"] < 0 and r[c_key] < 0) or
                (r["panel"] == 0 and r[c_key] == 0)
            )
        )
        total_valid = sum(1 for r in per_row if r[c_key] is not None)
        agreement_pct = (signs_agree / total_valid * 100.0) if total_valid > 0 else 0.0

        if ratios:
            sorted_r = sorted(ratios)
            mid = len(sorted_r) // 2
            med = (sorted_r[mid] if len(sorted_r) % 2 != 0 else 0.5 * (sorted_r[mid - 1] + sorted_r[mid]))
            min_r = min(ratios)
            max_r = max(ratios)
            spread_pass = (0.8 <= min_r and max_r <= 1.25)
        else:
            med = None
            min_r = None
            max_r = None
            spread_pass = False

        summary[c_key] = {
            "sign_agreement_count": signs_agree,
            "total_valid": total_valid,
            "sign_agreement_pct": agreement_pct,
            "median_ratio": med,
            "min_ratio": min_r,
            "max_ratio": max_r,
            "spread_pass": spread_pass,
        }

    # Verdict rule:
    # verdict = the candidate with sign agreement >= 80% and ratio spread inside 0.8-1.25,
    # else UNIDENTIFIED with the n rows used (no regression claim under n = 8)
    verdict = f"UNIDENTIFIED (n = {n_rows})"
    if n_rows >= 8:
        for c_key, stats in summary.items():
            if stats["sign_agreement_pct"] >= 80.0 and stats["spread_pass"]:
                verdict = f"CANDIDATE {c_key.upper()} (n = {n_rows})"
                break

    return {
        "per_row": per_row,
        "summary": summary,
        "n_rows": n_rows,
        "verdict": verdict,
    }


if __name__ == "__main__":
    res = run_fit()
    print("=" * 80)
    print(f"VERDICT: {res['verdict']}")
    print("=" * 80)
    print(f"{'Row ID':<16} | {'Panel':<8} | {'Cand A':<10} | {'Cand B':<10} | {'Ratio A':<8} | {'Ratio B':<8}")
    print("-" * 80)
    for r in res["per_row"]:
        ca = f"{r['cand_a']:.1f}" if r['cand_a'] is not None else "N/A"
        cb = f"{r['cand_b']:.1f}"
        ra = f"{r['ratio_a']:.3f}" if r['ratio_a'] is not None else "N/A"
        rb = f"{r['ratio_b']:.3f}" if r['ratio_b'] is not None else "N/A"
        print(f"{r['id']:<16} | {r['panel']:<8.1f} | {ca:<10} | {cb:<10} | {ra:<8} | {rb:<8}")
    print("=" * 80)
    for k, v in res["summary"].items():
        print(f"{k}: sign_agree={v['sign_agreement_count']}/{v['total_valid']} ({v['sign_agreement_pct']:.1f}%), med={v['median_ratio']}, min={v['min_ratio']}, max={v['max_ratio']}")
