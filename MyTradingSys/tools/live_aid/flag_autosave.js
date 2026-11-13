// Live Aid flag log -> files on disk without a download click (card live-aid-flag-log-autoexport-1113).
// The browser cannot write a path by itself, so the operator picks ONE folder once (File System Access API; runtime_data/live_aid/ in the
// repo, git-ignored). The handle is kept in IndexedDB; after that every change of the log is written as flag_log_<UTC day>.csv, one file per
// day, rewritten whole (so a day file is never half-written by a crash: createWritable swaps on close). No server, no process, no live tree.
// Pure and injectable for tests: dir = {getFileHandle(name,{create}) -> {createWritable() -> {write,close}}}.
(function (root) {
  'use strict';
  var COLS = ['t', 'kind', 'side', 'level', 'evidence', 'price'];
  function q(v) { var s = v == null ? '' : String(v); return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s; }
  function day(t) { return new Date(+t).toISOString().slice(0, 10); }
  // rows -> { 'flag_log_2026-11-13.csv': csv text } (same header as home.js FLAG_COLS, t as ISO)
  function byDay(rows) {
    var out = {};
    (rows || []).forEach(function (r) {
      if (!isFinite(+r.t)) return;
      var name = 'flag_log_' + day(r.t) + '.csv';
      if (!out[name]) out[name] = [COLS.join(',')];
      out[name].push(COLS.map(function (c) { return q(c === 't' ? new Date(+r.t).toISOString() : r[c]); }).join(','));
    });
    Object.keys(out).forEach(function (k) { out[k] = out[k].join('\n') + '\n'; });
    return out;
  }
  async function save(dir, rows) {
    var files = byDay(rows), names = Object.keys(files);
    for (var i = 0; i < names.length; i++) {
      var fh = await dir.getFileHandle(names[i], { create: true }), w = await fh.createWritable();
      await w.write(files[names[i]]); await w.close();
    }
    return names.length;
  }
  // state machine for the button: 'none' (no folder) | 'resume' (folder remembered, permission needs a click) | 'on'
  async function status(dir) {
    if (!dir) return 'none';
    try { return (await dir.queryPermission({ mode: 'readwrite' })) === 'granted' ? 'on' : 'resume'; } catch (e) { return 'resume'; }
  }
  var api = { COLS: COLS, byDay: byDay, save: save, status: status };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.LAAUTOSAVE = api;
})(typeof window !== 'undefined' ? window : this);
