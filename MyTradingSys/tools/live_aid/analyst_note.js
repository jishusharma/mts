// Analyst level note: what happened to one analyst's price level since it was said (operator ask 11-13: "how do I know what the analyst meant after it
// has been broken or reclaimed"). Pure functions, descriptive only, no forecast. All thresholds are OURS (not any analyst's): a bar counts only when it
// closed before `now` and opened on/after the published date 00:00Z; touch = high >= level >= low; a close beyond = close strictly past the level;
// original side = side of the first usable bar's open vs the level; BROKEN = last close-through left price on the other side and it is still there;
// RECLAIMED = was broken, a later close came back to the original side.
(function (root) {
  'use strict';
  var SAID_MAX = 45;
  function p2(n) { return (n < 10 ? '0' : '') + n; }
  function md(ms) { var d = new Date(ms); return p2(d.getUTCMonth() + 1) + '-' + p2(d.getUTCDate()); }
  function mdhm(ms) { var d = new Date(ms); return md(ms) + ' ' + p2(d.getUTCHours()) + ':' + p2(d.getUTCMinutes()) + 'Z'; }
  function who(l) { var w = String(l && l.who || '').trim(); return /^qriptal$/i.test(w) ? 'Habib' : w; }
  function head(l) {
    var w = who(l) || 'Analyst', pub = String(l && l.published || '').slice(5, 10), said = String(l && l.said || '').trim();
    if (said.length > SAID_MAX) said = said.slice(0, SAID_MAX - 1).trim() + '\u2026';
    return w.slice(0, 12) + (pub ? ' ' + pub : '') + (said ? ': "' + said + '"' : '') + '.';
  }
  function status(level, klines, now) {
    var L = level || {}, px = Number(L.price), t0 = Date.parse(String(L.published || '').slice(0, 10) + 'T00:00:00Z');
    if (!isFinite(t0)) t0 = 0;
    var bars = (klines || []).filter(function (k) { return k && +k[0] >= t0 && +k[6] < now; });
    if (!isFinite(px) || bars.length < 2) return { state: 'NO_DATA', since: null, role: null, text: head(L) + ' Not enough closed bars since then to read it.' };
    var side0 = +bars[0][1] >= px ? 1 : -1, cur = side0, touched = false, firstTouch = null, flipAt = null, broken = false;
    bars.forEach(function (k) {
      var hi = +k[2], lo = +k[3], c = +k[4];
      if (hi >= px && px >= lo && !touched) { touched = true; firstTouch = +k[0]; }
      var s = c > px ? 1 : c < px ? -1 : cur;
      if (s !== cur) { cur = s; flipAt = +k[0]; if (!touched) { touched = true; firstTouch = +k[0]; } if (s !== side0) broken = true; }
    });
    var last = +bars[bars.length - 1][4], role = last > px ? 'floor' : 'ceiling', state, since, tail;
    if (cur !== side0) { state = 'BROKEN'; since = flipAt; tail = 'Broken ' + (side0 > 0 ? 'down ' : 'up ') + mdhm(since) + ', now a ' + role + '.'; }
    else if (broken) { state = 'RECLAIMED'; since = flipAt; tail = 'Reclaimed ' + mdhm(since) + ', now a ' + role + '.'; }
    else if (touched) { state = 'HELD'; since = firstTouch; tail = 'Touched ' + mdhm(since) + ', no close through, now a ' + role + '.'; }
    else { state = 'UNTESTED'; since = null; tail = 'Not reached since.'; }
    return { state: state, since: since, role: role, text: head(L) + ' ' + tail };
  }
  function label(item) {
    var w = who(item);
    if (!w) return 'Analyst';
    var pub = String(item.published || '').slice(5, 10), b = String(item.bias || '').toUpperCase();
    return w + (pub ? ' ' + pub : '') + (b === 'BULLISH' || b === 'BEARISH' ? ' ' + b.toLowerCase() : '');
  }
  function zoneLabel(zone) {
    var l = ((zone && zone.items) || []).filter(function (i) { return i && i.src === 'analyst'; }).map(label);
    return l.slice(0, 2).join(' + ') + (l.length > 2 ? ' +' + (l.length - 2) : '');
  }
  var api = { status: status, label: label, zoneLabel: zoneLabel };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.ANOTE = api;
})(typeof window !== 'undefined' ? window : this);
