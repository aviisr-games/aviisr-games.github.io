/*
 * Aggregate, cookieless page and store-click counter for aviisrgames.com.
 *
 * Off by default: nothing is sent until ENDPOINT is set to a GoatCounter
 * count URL (https://<code>.goatcounter.com/count). GoatCounter stores no
 * cookies and no personal data; we send only the path, an event name and
 * the referrer's origin.
 *
 * Never loaded on /mila/** (children's app) or on privacy/support pages.
 * The /mila/ check below is a second guard in case the include is copied
 * there by mistake. Visitors with Do Not Track or Global Privacy Control
 * are not counted.
 */
(function () {
  'use strict';

  var ENDPOINT = 'https://aviisrgames.goatcounter.com/count';

  // Playables call this defensively: if (window.aviisrCount) window.aviisrCount('play_start/ninely');
  // It stays a no-op whenever the counter is disabled (see the guards below).
  window.aviisrCount = function () {};

  if (!ENDPOINT) return;
  if (/^\/mila(\/|$)/.test(location.pathname)) return;
  if (navigator.doNotTrack === '1' || window.doNotTrack === '1' || navigator.globalPrivacyControl === true) return;

  function send(path, isEvent) {
    var q = 'p=' + encodeURIComponent(path) + (isEvent ? '&e=true' : '');
    if (!isEvent && document.referrer) {
      try { q += '&r=' + encodeURIComponent(new URL(document.referrer).origin); } catch (e) { /* ignore */ }
    }
    q += '&rnd=' + Math.random().toString(36).slice(2);
    var img = new Image();
    img.referrerPolicy = 'no-referrer';
    img.src = ENDPOINT + '?' + q;
  }

  // Named events: path-like names only (no ids, no free text), each sent at most once per page view.
  var NAME_RE = /^[a-z_]+(\/[A-Za-z0-9_-][A-Za-z0-9_.-]*){1,3}$/;
  var seen = {};
  function count(name) {
    try {
      if (typeof name !== 'string' || name.length > 80 || !NAME_RE.test(name)) return;
      if (seen[name]) return;
      seen[name] = true;
      send(name, true);
    } catch (e) { /* never throw into the page */ }
  }
  window.aviisrCount = count;

  send(location.pathname, false);

  // qr_land/<page>: a phone opened this page from the desktop QR code (?src=qr).
  if (/[?&]src=qr(&|$)/.test(location.search)) send('qr_land' + location.pathname, true);

  // store_click/<package>/<page>: counted once per link per page view.
  var clicked = {};
  document.addEventListener('click', function (e) {
    var a = e.target && e.target.closest ? e.target.closest('a[href*="play.google.com/store/apps/details"]') : null;
    if (!a) return;
    var m = /[?&]id=([\w.]+)/.exec(a.href);
    var key = (m ? m[1] : 'unknown') + location.pathname;
    if (clicked[key]) return;
    clicked[key] = true;
    send('store_click/' + (m ? m[1] : 'unknown') + location.pathname, true);
  }, true);

  // card_click/<game>/<play|hub>: home page cards, derived from the link target (never /mila/).
  var CARDS = {
    '/ninely/play/': ['ninely', 'play'], '/ninely/': ['ninely', 'hub'],
    '/middle-east-2030/briefing/': ['me2030', 'play'], '/middle-east-2030/': ['me2030', 'hub'],
    '/baylight/dock/': ['baylight', 'play'], '/baylight/': ['baylight', 'hub'],
    '/paper-route/': ['paper-route', 'hub']
  };
  var onHome = /^\/(index\.html)?$/.test(location.pathname);

  // contact_click/<page>: a mailto: link was clicked (page = path without slashes, "home" for /).
  document.addEventListener('click', function (e) {
    try {
      var a = e.target && e.target.closest ? e.target.closest('a[href]') : null;
      if (!a) return;
      var href = a.getAttribute('href') || '';
      if (/^mailto:/i.test(href)) {
        var page = location.pathname.replace(/index\.html$/, '').replace(/^\/+|\/+$/g, '').replace(/[^A-Za-z0-9_.\/-]/g, '_');
        count('contact_click/' + (page || 'home'));
        return;
      }
      if (!onHome) return;
      var u = new URL(href, location.href);
      if (u.origin !== location.origin) return;
      var path = u.pathname.replace(/index\.html$/, '');
      if (/^\/mila(\/|$)/.test(path)) return;
      var hit = CARDS[path];
      if (hit) count('card_click/' + hit[0] + '/' + hit[1]);
    } catch (err) { /* ignore */ }
  }, true);
})();
