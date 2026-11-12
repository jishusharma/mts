/* Footprint re-read cadence for Live Aid (operator 2026-11-12), pure and timer-free: the page asks "how often should I re-read
   footprint_bias_data.js right now?". Minutes relative to the US open: hourly outside; every 15 min from -2 h; every 1 min from
   -2 to +15 min; every 10 min until +2 h; then hourly. The 10 min (operator said 10-15) is OURS. No OS scheduler: live_aid.html
   runs one 60 s setInterval and re-reads only when this interval has elapsed. */
(function (root) {
  'use strict';
  var M = 60000;
  function cadenceMs(now, usOpenMs) {
    var m = (now - usOpenMs) / M;
    if (m >= -2 && m <= 15) return 1 * M;
    if (m >= -120 && m < -2) return 15 * M;
    if (m > 15 && m <= 120) return 10 * M;
    return 60 * M;
  }
  var api = { cadenceMs: cadenceMs };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.FpCadence = api;
})(typeof self !== 'undefined' ? self : this);
