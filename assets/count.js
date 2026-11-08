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

  var ENDPOINT = ''; // e.g. 'https://aviisrgames.goatcounter.com/count'

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

  send(location.pathname, false);

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
})();
