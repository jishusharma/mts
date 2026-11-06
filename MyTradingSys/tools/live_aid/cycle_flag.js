// Cycle-bottom flag line for the live aid. The line itself is computed by research/btc_cycles_2026-11/cycle_bottom_flag.py
// (rule: RULE.md there) and written to cycle_flag_data.js by build_cycle_flag.py; this file only shows it. Fail closed:
// no data or data older than 36 h reads as stale/missing, never as a guess. Observation only: no orders, no sizing.
(function (root) {
  'use strict';
  var STALE_MS = 36 * 3600 * 1000;   // OURS: the line is a daily one; a day and a half old is stale
  function text(data, nowMs) {
    if (!data || typeof data.line !== 'string' || !data.line || !data.built_utc) return 'CYCLE FLAG: NOT_IN_DATA (run build_cycle_flag.py)';
    var built = Date.parse(data.built_utc);
    if (isNaN(built)) return 'CYCLE FLAG: NOT_IN_DATA (bad timestamp)';
    if (nowMs - built > STALE_MS) return 'CYCLE FLAG STALE (built ' + data.built_utc + '; run build_cycle_flag.py): ' + data.line;
    return data.line;
  }
  var api = { STALE_MS: STALE_MS, text: text };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.CYCLEFLAG = api;
})(typeof window !== 'undefined' ? window : this);
