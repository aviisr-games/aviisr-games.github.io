/**
 * Mila-only language switcher (mila/assets/lang.js).
 *
 * A trimmed copy of the engine in /assets/i18n.js with no studio-wide strings. Mila pages
 * load only scripts under /mila/, so a later edit to a shared studio script (strings,
 * counters, anything else) can never run on the children's app pages.
 * Uses textContent only; ?lang= and #hash are checked against the page's supported list.
 */

(function () {
  'use strict';

  var AVIISR_LANGS = {
    'he': { nativeName: 'עברית', englishName: 'Hebrew', dir: 'rtl' },
    'en': { nativeName: 'English', englishName: 'English', dir: 'ltr' }
  };

  // Mila pages carry their own translations; no studio-wide strings are loaded here.
  var AVIISR_STRINGS = {};

  window.AVIISR_LANGS = AVIISR_LANGS;
  window.AVIISR_STRINGS = AVIISR_STRINGS;

  // options.storageKey: where an explicit choice is remembered (default 'aviisr_lang', shared across hubs).
  // options.useBrowserLanguage: false pins the page to defaultLang unless the visitor chose otherwise
  // (used by Mila, a Hebrew parent page that must not flip to English on English-language phones).
  function resolveLanguage(supported, defaultLang, options) {
    options = options || {};
    var storageKey = options.storageKey || 'aviisr_lang';
    // 1. URL query param: ?lang=xx
    try {
      var params = new URLSearchParams(window.location.search);
      var qLang = params.get('lang');
      if (qLang && supported.indexOf(qLang) !== -1) return qLang;
    } catch (e) {}

    // 2. URL hash: #en, #he, #ar, etc.
    var hash = (window.location.hash || '').replace(/^#/, '');
    if (hash && supported.indexOf(hash) !== -1) return hash;

    // 3. Stored choice
    try {
      var stored = localStorage.getItem(storageKey);
      if (stored && supported.indexOf(stored) !== -1) return stored;
    } catch (e) {}

    // 4. Browser navigator language
    if (options.useBrowserLanguage === false) return defaultLang || 'en';
    try {
      var nav = (navigator.language || navigator.userLanguage || '').toLowerCase();
      for (var i = 0; i < supported.length; i++) {
        var s = supported[i];
        if (s.toLowerCase() === nav) return s;
      }
      var baseNav = nav.split('-')[0];
      for (var j = 0; j < supported.length; j++) {
        var cand = supported[j];
        if (cand.split('-')[0].toLowerCase() === baseNav) return cand;
      }
    } catch (e) {}

    return defaultLang || 'en';
  }

  function applyLanguage(lang, options) {
    var supported = options.supported || ['en'];
    var translations = options.translations || {};
    var defaultLang = options.defaultLang || 'en';

    if (supported.indexOf(lang) === -1) lang = defaultLang;

    var meta = AVIISR_LANGS[lang] || { nativeName: lang, dir: 'ltr' };
    var dir = meta.dir || 'ltr';

    document.documentElement.lang = lang;
    document.documentElement.dir = dir;

    try {
      localStorage.setItem(options.storageKey || 'aviisr_lang', lang);
    } catch (e) {}

    // Synchronize select dropdowns if present
    var selectElements = document.querySelectorAll('.lang-switcher, #lang-switcher');
    for (var i = 0; i < selectElements.length; i++) {
      selectElements[i].value = lang;
    }

    // Merge global strings + page-specific strings for active language and fallback
    var globalLangTable = AVIISR_STRINGS[lang] || {};
    var pageLangTable = translations[lang] || {};
    var globalFallback = AVIISR_STRINGS[defaultLang] || AVIISR_STRINGS['en'] || {};
    var pageFallback = translations[defaultLang] || translations['en'] || {};

    var i18nNodes = document.querySelectorAll('[data-i18n]');
    for (var k = 0; k < i18nNodes.length; k++) {
      var el = i18nNodes[k];
      var key = el.getAttribute('data-i18n');
      if (!key) continue;
      var val = pageLangTable[key] !== undefined ? pageLangTable[key]
        : (globalLangTable[key] !== undefined ? globalLangTable[key]
        : (pageFallback[key] !== undefined ? pageFallback[key] : globalFallback[key]));
      if (val !== undefined) {
        el.textContent = val;
      }
    }

    // Toggle multi-section visibility for pages using <section id="en">, <section id="he">, <section id="ar">
    var sections = document.querySelectorAll('section[id]');
    var langSectionIds = [];
    var hasExactMatch = false;
    for (var s = 0; s < sections.length; s++) {
      var sid = sections[s].getAttribute('id');
      if (AVIISR_LANGS[sid]) {
        langSectionIds.push(sections[s]);
        if (sid === lang) hasExactMatch = true;
      }
    }
    if (langSectionIds.length > 0) {
      var targetSectionId = hasExactMatch ? lang : (document.getElementById(defaultLang) ? defaultLang : 'en');
      for (var m = 0; m < langSectionIds.length; m++) {
        var sec = langSectionIds[m];
        var secId = sec.getAttribute('id');
        sec.style.display = (secId === targetSectionId) ? '' : 'none';
      }
    }

    // Notify custom listeners if any
    if (typeof options.onLanguageChange === 'function') {
      options.onLanguageChange(lang, meta);
    }
  }

  function renderSwitcher(container, options) {
    if (!container) return;
    var supported = options.supported || ['en'];
    var current = options.current || 'en';

    // Preserve any non-language navigation links (e.g. All Games, Privacy, Support)
    var preservedLinks = [];
    var existingAnchors = container.querySelectorAll('a');
    for (var a = 0; a < existingAnchors.length; a++) {
      var href = existingAnchors[a].getAttribute('href') || '';
      if (href.indexOf('#') !== 0) {
        preservedLinks.push(existingAnchors[a].cloneNode(true));
      }
    }

    var select = document.createElement('select');
    select.id = 'lang-switcher';
    select.className = 'lang-switcher';
    select.setAttribute('aria-label', 'Language');

    for (var i = 0; i < supported.length; i++) {
      var code = supported[i];
      var meta = AVIISR_LANGS[code] || { nativeName: code, englishName: code };
      var opt = document.createElement('option');
      opt.value = code;
      opt.textContent = meta.nativeName + (meta.englishName && meta.englishName !== meta.nativeName ? ' (' + meta.englishName + ')' : '');
      if (code === current) opt.selected = true;
      select.appendChild(opt);
    }

    select.addEventListener('change', function () {
      applyLanguage(this.value, options);
    });

    while (container.firstChild) {
      container.removeChild(container.firstChild);
    }
    container.appendChild(select);

    for (var p = 0; p < preservedLinks.length; p++) {
      var sep = document.createTextNode(' · ');
      container.appendChild(sep);
      container.appendChild(preservedLinks[p]);
    }
  }

  window.AviisrI18n = {
    init: function (options) {
      options = options || {};
      var supported = options.supported || ['en'];
      var defaultLang = options.defaultLang || (supported.indexOf('he') !== -1 && supported[0] === 'he' ? 'he' : 'en');
      options.defaultLang = defaultLang;

      var currentLang = resolveLanguage(supported, defaultLang, options);
      options.current = currentLang;

      // Mount switcher if container exists
      var navContainer = document.querySelector('nav.lang') || document.querySelector('.lang-nav');
      if (navContainer) {
        renderSwitcher(navContainer, options);
      }

      applyLanguage(currentLang, options);

      // Listen to hashchange for anchor links (#en, #he, #ar)
      window.addEventListener('hashchange', function () {
        var h = (window.location.hash || '').replace(/^#/, '');
        if (h && supported.indexOf(h) !== -1) {
          applyLanguage(h, options);
        }
      });
    },
    setLanguage: function (lang, options) {
      applyLanguage(lang, options);
    }
  };
})();
