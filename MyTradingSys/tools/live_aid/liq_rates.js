// Live Aid: how often price kept going after a 1m/2m forced-selling or forced-buying burst. Written by
// MyTradingSys/research/live_aid_liq_meaning_2026-11-13/liq_meaning.py (rewrites only the DATA line). Descriptive, not a signal.
// cont5/15/60 = share of past bursts after which BTCUSDT closed further in the direction of the forced flow (long forced out: down) 5/15/60 min later.
// med15 = median signed % price change over 15 min (+ = up). Bucket edges (USD) are OURS, not sourced.
(function (root) {
  /*DATA*/var DATA = {"asof": "2026-11-13", "span": "none", "source": "xliq_events.jsonl + Binance spot 1m closes", "rows": [], "note": "not measured: no liquidation history on disk (xliq_events.jsonl missing); needs live-aid-liq-history-log-1113"};/*END*/
  var LIQ_RATES = { asof: DATA.asof, span: DATA.span, source: DATA.source, rows: DATA.rows, note: DATA.note };
  // read(win, side, usd): the row whose [lo, hi) holds usd for that window and side, else null (below the smallest bucket, unknown window, no rows).
  LIQ_RATES.read = function (win, side, usd) {
    var r = LIQ_RATES.rows;
    for (var i = 0; i < r.length; i++) if (r[i].win === win && r[i].side === side && usd >= r[i].lo && usd < r[i].hi) return r[i];
    return null;
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = LIQ_RATES; else root.LIQ_RATES = LIQ_RATES;
})(typeof window !== 'undefined' ? window : this);
