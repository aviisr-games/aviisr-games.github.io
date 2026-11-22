/* Google AdSense + Google "Privacy & messaging" (CMP) loader for the allowlisted guide pages only
 * (see tools/test_ads_isolation.py). Never include this file on /mila/, privacy, support, 404,
 * game or hub pages.
 *
 * OFF by default: ADS_ENABLED is false, so this file does nothing and no request leaves the page.
 *
 * To turn ads on (a separate, reviewed change, after AdSense approval):
 *  1. In AdSense, create the consent message under Privacy & messaging for aviisrgames.com
 *     (EEA, UK and Switzerland, Google-certified TCF CMP) and publish it.
 *  2. Create two display ad units in AdSense and paste their numeric slot ids into SLOTS below.
 *  3. Set ADS_ENABLED to true and update tools/test_ads_isolation.py.
 * The allowlisted pages already carry the widened Content-Security-Policy.
 */
(function () {
  'use strict';
  var ADS_ENABLED = false;
  var CLIENT = 'ca-pub-2451365263828795';
  var SLOTS = { intro: '', end: '' }; // AdSense display unit ids; an empty id means no unit
  if (!ADS_ENABLED) { return; }

  // Respect Global Privacy Control: no ad code at all for visitors who send it.
  if (navigator.globalPrivacyControl === true) { return; }

  // Google "Privacy & messaging": consent message for EEA, UK and Switzerland visitors.
  var cmp = document.createElement('script');
  cmp.async = true;
  cmp.src = 'https://fundingchoicesmessages.google.com/i/pub-2451365263828795?ers=1';
  document.head.appendChild(cmp);
  (function signalGooglefcPresent() {
    if (!window.frames.googlefcPresent) {
      if (document.body) {
        var f = document.createElement('iframe');
        f.style.cssText = 'width:0;height:0;border:none;z-index:-1000;left:-1000px;top:-1000px;display:none';
        f.name = 'googlefcPresent';
        document.body.appendChild(f);
      } else {
        setTimeout(signalGooglefcPresent, 0);
      }
    }
  })();

  // Footer link so a visitor can change or withdraw the consent choice.
  var footer = document.querySelector('footer');
  if (footer) {
    var a = document.createElement('a');
    a.href = '#privacy-settings';
    a.textContent = 'Privacy settings';
    a.addEventListener('click', function (e) {
      e.preventDefault();
      window.googlefc = window.googlefc || {};
      window.googlefc.callbackQueue = window.googlefc.callbackQueue || [];
      window.googlefc.callbackQueue.push({
        CONSENT_DATA_READY: function () {
          if (window.googlefc && window.googlefc.showRevocationMessage) { window.googlefc.showRevocationMessage(); }
        }
      });
      if (window.googlefc.showRevocationMessage) { window.googlefc.showRevocationMessage(); }
    });
    footer.appendChild(document.createTextNode(' · '));
    footer.appendChild(a);
  }

  // Ad units: at most two per guide, outside the interactive board, never over content.
  function unit(slot, before) {
    if (!slot || !before || !before.parentNode) { return; }
    var wrap = document.createElement('div');
    wrap.className = 'ad-unit';
    wrap.style.cssText = 'min-height:280px;margin:24px 0;text-align:center';
    var ins = document.createElement('ins');
    ins.className = 'adsbygoogle';
    ins.style.display = 'block';
    ins.setAttribute('data-ad-client', CLIENT);
    ins.setAttribute('data-ad-slot', slot);
    ins.setAttribute('data-ad-format', 'auto');
    ins.setAttribute('data-full-width-responsive', 'true');
    wrap.appendChild(ins);
    before.parentNode.insertBefore(wrap, before);
    (window.adsbygoogle = window.adsbygoogle || []).push({});
  }
  var sections = document.querySelectorAll('.guide-main > .guide-section');
  if (sections.length > 1) { unit(SLOTS.intro, sections[1]); }
  unit(SLOTS.end, document.querySelector('.guide-main > .practice-cta'));

  var s = document.createElement('script');
  s.async = true;
  s.crossOrigin = 'anonymous';
  s.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=' + CLIENT;
  document.head.appendChild(s);
})();
