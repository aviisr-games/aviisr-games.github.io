/* Home page enhancement (optional). The HTML order is already valid for everyone.
 * Android: Google Play badge first in each band. iPhone/iPad: hide the Play badges and show the
 * "not on the App Store yet" note. Never touches the Mila band; bands that have their own App Store
 * badge (Baylight) keep both badges and put the App Store one first on iPhone/iPad. Fails silently. */
(function () {
  'use strict';
  try {
    var ua = navigator.userAgent || '';
    var ios = /iPhone|iPad|iPod/.test(ua) || (/Macintosh/.test(ua) && navigator.maxTouchPoints > 1);
    var android = /Android/.test(ua);
    // The visible "Language" label names the select (the engine adds an English aria-label).
    var sel = document.getElementById('lang-switcher');
    if (sel) sel.removeAttribute('aria-label');
    if (!ios && !android) return;
    var bands = document.querySelectorAll('[data-world]:not([data-world="mila"])');
    for (var i = 0; i < bands.length; i++) {
      var acts = bands[i].querySelector('.acts');
      var badge = bands[i].querySelector('a.play-badge');
      if (!acts || !badge) continue;
      var store = bands[i].querySelector('a.appstore-badge');
      if (store) {
        if (ios && acts.firstElementChild !== store) acts.insertBefore(store, acts.firstChild);
        else if (android && acts.firstElementChild !== badge) acts.insertBefore(badge, acts.firstChild);
        continue;
      }
      if (ios) {
        badge.hidden = true;
        var note = bands[i].querySelector('.ios-note');
        if (note) note.hidden = false;
      } else if (acts.firstElementChild !== badge) {
        acts.insertBefore(badge, acts.firstChild);
      }
    }
  } catch (e) {}
})();
