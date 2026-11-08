/*
 * Shows Google's official, unaltered "Get it on Google Play" badge in the page language.
 * Markup: <a class="play-badge" href="https://play.google.com/store/apps/details?id=...">
 *           <img data-play-badge src="/assets/badges/google-play-en.png" alt="Get it on Google Play" width="150" height="58"></a>
 */
(function () {
  'use strict';
  var FILE = { en: 'en', he: 'iw', ar: 'ar' };
  var ALT = { en: 'Get it on Google Play', he: 'השיגו ב-Google Play', ar: 'احصل عليه من Google Play' };
  function sync() {
    var lang = (document.documentElement.lang || 'en').split('-')[0];
    if (!FILE[lang]) lang = 'en';
    var imgs = document.querySelectorAll('img[data-play-badge]');
    for (var i = 0; i < imgs.length; i++) {
      var want = '/assets/badges/google-play-' + FILE[lang] + '.png';
      if (imgs[i].getAttribute('src') !== want) imgs[i].setAttribute('src', want);
      imgs[i].alt = ALT[lang];
    }
  }
  sync();
  new MutationObserver(sync).observe(document.documentElement, { attributes: true, attributeFilter: ['lang'] });
})();
