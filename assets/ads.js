/* Google AdSense loader for the allowlisted guide pages only (see tools/test_ads_isolation.py).
 *
 * OFF by default: ADS_ENABLED is false, so this file does nothing and no request leaves the page.
 * Never include this file on /mila/, privacy, support, 404, game or hub pages.
 *
 * To turn ads on (after AdSense approval, a separate reviewed PR):
 *  1. Set ADS_ENABLED to true and update tools/test_ads_isolation.py.
 *  2. Turn on Google "Privacy & messaging" (the Google-certified consent message) for aviisrgames.com
 *     in AdSense, so EEA/UK/CH visitors get the consent choice before personalised ads.
 *  3. Widen the Content-Security-Policy on the allowlisted pages only:
 *     script-src + https://pagead2.googlesyndication.com https://*.google.com https://*.googletagservices.com;
 *     frame-src https://googleads.g.doubleclick.net https://tpc.googlesyndication.com https://*.google.com;
 *     img-src + https:; connect-src https://pagead2.googlesyndication.com https://*.google.com.
 *  4. Add manual ad units (max 2 per guide, never inside the interactive board).
 */
(function () {
  'use strict';
  var ADS_ENABLED = false;
  var CLIENT = 'ca-pub-2451365263828795';
  if (!ADS_ENABLED) { return; }
  var s = document.createElement('script');
  s.async = true;
  s.crossOrigin = 'anonymous';
  s.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=' + CLIENT;
  document.head.appendChild(s);
})();
