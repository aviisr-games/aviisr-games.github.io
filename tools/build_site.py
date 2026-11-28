#!/usr/bin/env python3
"""Generate pilot static HTML pages (Home, Ninely, Mila) from site/games.json.

Usage:
  python3 tools/build_site.py          # write index.html, ninely/index.html, mila/index.html
  python3 tools/build_site.py --check  # exit 1 if any generated file is out of date
"""

import html as htmllib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
GAMES_PATH = ROOT / 'site/games.json'


def esc(text):
    return htmllib.escape(str(text), quote=True)


def load_registry():
    return json.loads(GAMES_PATH.read_text(encoding='utf-8'))


def platform_lines(games):
    gp_live = sum(1 for g in games if g.get('googlePlay', {}).get('status') == 'live')
    ios_apps = [g for g in games if g.get('appStore', {}).get('status') == 'live']
    android_only = gp_live - len(ios_apps)

    def fmt_ios(g, lang):
        mkts = g.get('appStore', {}).get('markets', [])
        if lang == 'en':
            name = g['shortTitle']
            scope = 'Israel' if mkts == ['IL'] else ', '.join(mkts)
        elif lang == 'he':
            name = g['storeTitle'].split(' · ')[0]
            scope = 'ישראל' if mkts == ['IL'] else 'ישראל וארה״ב'
        else:
            name = g['shortTitle']
            scope = 'إسرائيل' if mkts == ['IL'] else 'متاح عالمياً'
        return f'{name} ({scope})' if scope else name

    def join_list(items, sep, last):
        return items[0] if len(items) == 1 else sep.join(items[:-1]) + last + items[-1]

    ios_en = join_list([fmt_ios(g, 'en') for g in ios_apps], ', ', ' and ')
    ios_he = join_list([fmt_ios(g, 'he') for g in ios_apps], ', ', ' ו-')
    ios_ar = join_list([fmt_ios(g, 'ar') for g in ios_apps], '، ', ' و')

    en = (
        f'{gp_live} apps on Google Play (IL, US). '
        f'{ios_en} are also on the App Store; the other {android_only} games are Android-only for now, with browser previews below.'
    )
    he = (
        f'{gp_live} אפליקציות ב-Google Play (ישראל וארה״ב). '
        f'{ios_he} זמינות גם ב-App Store; {android_only} המשחקים האחרים זמינים כרגע ל-Android בלבד, עם גרסאות דפדפן להלן.'
    )
    ar = (
        f'{gp_live} تطبيقات على Google Play. '
        f'{ios_ar} متوفرة أيضاً على App Store؛ والألعاب الـ{android_only} الأخرى لنظام Android حالياً مع نسخ متصفح أدناه.'
    )
    return {'en': en, 'he': he, 'ar': ar}


def appstore_svg(size=18):
    return (
        f'<svg viewBox="0 0 170 170" aria-hidden="true" width="{size}" height="{size}" '
        'style="fill:currentColor;flex:none;">'
        '<path d="M150.37 130.25c-2.45 5.66-5.35 10.87-8.71 15.66-4.58 6.53-8.33 11.05-11.22 13.56'
        '-4.48 4.12-9.28 6.23-14.42 6.35-3.69 0-8.14-1.05-13.32-3.18-5.19-2.12-9.97-3.17-14.34-3.17'
        '-4.58 0-9.49 1.05-14.74 3.17-5.26 2.13-9.5 3.24-12.74 3.35-4.35.13-9.16-1.9-14.42-6.08'
        '-3.7-3.08-7.71-7.96-12.04-14.64-5.99-9.28-10.66-19.82-13.99-31.62-3.33-11.79-5-23.01-5-33.64'
        ' 0-14.35 3.58-26.43 10.74-36.24 7.16-9.81 16.27-14.77 27.34-14.88 4.89 0 10.25 1.25 16.08 3.75'
        ' 5.83 2.5 9.77 3.79 11.83 3.87 1.85-.08 5.86-1.39 12.04-3.95 6.18-2.55 11.58-3.73 16.2-3.53'
        ' 12.63.76 22.84 5.37 30.64 13.84-11.09 6.74-16.53 16.08-16.32 28.02.22 9.57 3.97 17.56 11.24 23.97'
        ' 7.28 6.41 15.93 10.05 25.96 10.92-2.39 7.4-5.33 14.78-8.81 22.15zM119.22 31.84'
        'c0-7.39 2.66-14.42 7.98-21.09 5.33-6.67 11.96-10.75 19.89-12.25.33 1.2.54 2.39.65 3.59'
        '.11 1.19.16 2.39.16 3.59 0 7.39-2.82 14.6-8.47 21.63-5.65 7.03-12.28 11-19.89 11.9'
        '-.32-.98-.49-2.12-.49-3.42 0-1.3.06-2.62.17-3.95z"/></svg>'
    )


def render_home(reg):
    games = reg['games']
    by_id = {g['id']: g for g in games}
    ninely = by_id['ninely']
    me2030 = by_id['middle-east-2030']
    baylight = by_id['baylight']
    lines = platform_lines(games)

    # Play Now companion deck links (Baylight + ME2030 + Sudoku Workshop)
    deck_html = []
    for g, sub_key in ((baylight, 'w_deckBay'), (me2030, 'w_deckMe')):
        deck_html.append(
            f'      <a class="decklink" href="{esc(g["browser"])}">'
            f'<img src="{esc(g["assets"]["icon"])}" alt="" width="{g["assets"]["iconWidth"]}" height="{g["assets"]["iconHeight"]}">'
            f'<span><strong><bdi>{esc(g["shortTitle"])}</bdi></strong>'
            f'<small data-i18n="{sub_key}">{esc(g["copy"]["en"]["ctaBrowser"])}</small></span></a>'
        )
    deck_html.append(
        '      <a class="decklink" href="ninely/strategy/">'
        '<img src="assets/icons/ninely.webp" alt="" width="128" height="128">'
        '<span><strong data-i18n="w_deckGuide">Sudoku workshop</strong>'
        '<small data-i18n="w_deckGuideSub">Learn a solving technique</small></span></a>'
    )

    # 5 collection cards generated from site/games.json
    cards_html = []
    for g in games:
        gid = g['id']
        copy_en = g['copy']['en']
        copy_he = g['copy']['he']
        is_mila = (gid == 'mila')
        lang_attrs = ' lang="he" dir="rtl"' if is_mila else ''
        display_copy = copy_he if is_mila else copy_en

        # Keys for dynamic translation (Mila stays isolated Hebrew unless explicit)
        tag_attr = f' data-i18n="card_tag_{gid}"' if not is_mila else ''
        lead_attr = f' data-i18n="card_lead_{gid}"' if not is_mila else ''
        status_attr = f' data-i18n="card_status_{gid}"' if not is_mila else ''
        browser_attr = f' data-i18n="card_browser_{gid}"' if not is_mila else ''

        flag_html = (
            '<span class="tag flag" data-i18n="w_fiction">Fiction</span>'
            if gid == 'middle-east-2030' else ''
        )

        # Title markup matches test_site_data & test_allowlist (<h3>{storeTitle}</h3>)
        if is_mila:
            title_inner = 'מילה · <bdi>Mila</bdi>'
        else:
            title_inner = esc(g['storeTitle'])

        acts = []
        if g.get('browser'):
            btn_cls = 'link' if gid == 'baylight' else 'btn'
            acts.append(
                f'          <a class="{btn_cls}" href="{esc(g["browser"])}"{browser_attr}>'
                f'{esc(display_copy["ctaBrowser"])}</a>'
            )
        if g['googlePlay']['status'] == 'live':
            badge_src = '/assets/badges/google-play-en.png'
            acts.append(
                f'          <a class="play-badge" href="{esc(g["playLink"])}">'
                f'<img data-play-badge data-app="{esc(g["storeTitle"].split(":")[0])}" '
                f'src="{badge_src}" alt="Get it on Google Play: {esc(g["storeTitle"].split(":")[0])}" '
                f'width="150" height="58"></a>'
            )
            if g['appStore']['status'] != 'live':
                acts.append('          <p class="ios-note" data-i18n="w_ios" hidden>Not on the App Store yet.</p>')
        if g['appStore']['status'] == 'live':
            if is_mila:
                acts.append(
                    f'          <a class="appstore-badge" href="{esc(g["appStore"]["url"])}" '
                    'target="_blank" rel="noopener noreferrer" referrerpolicy="no-referrer" '
                    'aria-label="הורדה ב-App Store (ישראל)">'
                    + appstore_svg(18) +
                    '<bdi>App Store</bdi> <bdi class="store-note">(ישראל / Israel)</bdi></a>'
                )
            else:
                acts.append(
                    f'          <a class="appstore-badge" href="{esc(g["appStore"]["url"])}" '
                    'target="_blank" rel="noopener noreferrer" '
                    f'aria-label="Download {esc(g["shortTitle"])} on the App Store">'
                    + appstore_svg(18) +
                    '<bdi>App Store</bdi></a>'
                )

        more_label = 'מידע להורים' if is_mila else 'About, help and privacy'
        more_attr = '' if is_mila else ' data-i18n="moreAbout"'
        more_sr = ': מילה' if is_mila else f': {esc(g["shortTitle"])}'

        cards_html.append(
            f'<section id="{esc(gid)}" data-world="{esc(gid)}" class="game-card"{lang_attrs} '
            f'style="--paper:{esc(g["paperColor"])}" aria-label="{esc(g["storeTitle"])}">\n'
            f'  <div><span class="tag"{tag_attr}>{esc(display_copy["tag"])}</span>{flag_html}</div>\n'
            f'  <div class="id"><img src="{esc(g["assets"]["icon"])}" alt="" '
            f'width="{g["assets"]["iconWidth"]}" height="{g["assets"]["iconHeight"]}">'
            f'<h3>{title_inner}</h3></div>\n'
            f'  <p class="card-lead"{lead_attr}>{esc(display_copy["lead"])}</p>\n'
            f'  <p class="store-line"{status_attr}>{esc(display_copy["storeStatus"])}</p>\n'
            f'  <div class="acts">\n' + '\n'.join(acts) + '\n  </div>\n'
            f'  <a class="app-more" href="{esc(g["hub"])}"><span{more_attr}>{more_label}</span>'
            f'<span class="sr-only">{more_sr}</span></a>\n'
            '</section>'
        )

    # Build translations dict from site/games.json
    translations = {}
    base_ui = {
        'en': {
            'w_skip': 'Skip to content',
            'w_games': 'Games',
            'w_guides': 'Guides',
            'w_notes': 'Notes',
            'w_about': 'About',
            'w_security': 'Security',
            'w_lang': 'Language',
            'navSupport': 'Support',
            'navPrivacy': 'Privacy Policy',
            'w_featured': 'Featured game  /  Ninely',
            'w_heroStart': 'A little more',
            'w_heroAccent': 'logic.',
            'w_heroCaption': 'Ninely',
            'w_playKicker': 'Browser games',
            'w_playTitle': 'Play in your browser',
            'w_dailyKicker': 'Daily Sudoku  /  Ninely',
            'w_dailyTitle': 'Today’s puzzle',
            'w_dailyDesc': 'Open the board in your browser. A new puzzle arrives each day.',
            'w_alsoPlay': 'Also playable',
            'w_deckGuide': 'Sudoku workshop',
            'w_deckGuideSub': 'Learn a solving technique',
            'w_collection': 'The collection',
            'w_fiction': 'Fiction',
            'w_ios': 'Not on the App Store yet.',
            'moreAbout': 'About, help and privacy',
            'contactTitle': 'Studio Contact & Support',
            'contactSub': 'Player inquiries, bug reports, ad privacy requests, or business correspondence:',
            'platformLine': lines['en'],
            'w_deckBay': baylight['copy']['en']['ctaBrowser'],
            'w_deckMe': me2030['copy']['en']['ctaBrowser'],
        },
        'he': {
            'w_skip': 'דלגו לתוכן',
            'w_games': 'משחקים',
            'w_guides': 'מדריכים',
            'w_notes': 'רשימות',
            'w_about': 'אודות',
            'w_security': 'אבטחה',
            'w_lang': 'שפה',
            'navSupport': 'תמיכה',
            'navPrivacy': 'מדיניות פרטיות',
            'w_featured': 'המשחק הנבחר  /  Ninely',
            'w_heroStart': 'עוד רגע של',
            'w_heroAccent': 'היגיון.',
            'w_heroCaption': 'Ninely',
            'w_playKicker': 'משחקי דפדפן',
            'w_playTitle': 'משחקים בדפדפן',
            'w_dailyKicker': 'סודוקו יומי  /  Ninely',
            'w_dailyTitle': 'החידה של היום',
            'w_dailyDesc': 'פותחים את הלוח בדפדפן. בכל יום מחכה חידה חדשה.',
            'w_alsoPlay': 'עוד בדפדפן',
            'w_deckGuide': 'סדנת סודוקו',
            'w_deckGuideSub': 'ללימוד שיטת פתרון',
            'w_collection': 'המשחקים והאפליקציות',
            'w_fiction': 'בדיוני',
            'w_ios': 'עדיין לא ב-App Store.',
            'moreAbout': 'מידע, עזרה ופרטיות',
            'contactTitle': 'יצירת קשר ותמיכה',
            'contactSub': 'פניות שחקנים, דיווח על תקלות, בקשות פרטיות או פניות עסקיות:',
            'platformLine': lines['he'],
            'w_deckBay': baylight['copy']['he']['ctaBrowser'],
            'w_deckMe': me2030['copy']['he']['ctaBrowser'],
        },
        'ar': {
            'w_skip': 'تخطَّ إلى المحتوى',
            'w_games': 'الألعاب',
            'w_guides': 'الأدلة',
            'w_notes': 'الملاحظات',
            'w_about': 'عن الاستوديو',
            'w_security': 'الأمان',
            'w_lang': 'اللغة',
            'navSupport': 'الدعم',
            'navPrivacy': 'سياسة الخصوصية',
            'w_featured': 'اللعبة المختارة  /  Ninely',
            'w_heroStart': 'لحظة أخرى من',
            'w_heroAccent': 'المنطق.',
            'w_heroCaption': 'Ninely',
            'w_playKicker': 'ألعاب المتصفح',
            'w_playTitle': 'العب في المتصفح',
            'w_dailyKicker': 'سودوكو يومي  /  Ninely',
            'w_dailyTitle': 'لغز اليوم',
            'w_dailyDesc': 'افتح اللوح في متصفحك. ينتظرك لغز جديد كل يوم.',
            'w_alsoPlay': 'متاح أيضاً في المتصفح',
            'w_deckGuide': 'ورشة السودوكو',
            'w_deckGuideSub': 'تعلّم تقنية حل',
            'w_collection': 'الألعاب والتطبيقات',
            'w_fiction': 'خيالي',
            'w_ios': 'ليست على App Store بعد.',
            'moreAbout': 'معلومات ومساعدة وخصوصية',
            'contactTitle': 'التواصل والدعم',
            'contactSub': 'استفسارات اللاعبين، تقارير الأخطاء، أو المراسلات الرسمية:',
            'platformLine': lines['ar'],
            'w_deckBay': baylight['copy']['ar']['ctaBrowser'],
            'w_deckMe': me2030['copy']['ar']['ctaBrowser'],
        },
    }
    for lang in ('en', 'he', 'ar'):
        tbl = dict(base_ui[lang])
        nc = ninely['copy'][lang]
        tbl['w_ninelyLead'] = nc['lead']
        tbl['w_ninelyHub'] = nc['ctaHub']
        tbl['w_ninelyBtn'] = nc['ctaBrowser']
        tbl['w_heroCaptionSub'] = nc['caption']
        for g in games:
            if g['id'] == 'mila':
                continue
            gc = g['copy'][lang]
            tbl[f'card_tag_{g["id"]}'] = gc['tag']
            tbl[f'card_lead_{g["id"]}'] = gc['lead']
            tbl[f'card_status_{g["id"]}'] = gc['storeStatus']
            if gc.get('ctaBrowser'):
                tbl[f'card_browser_{g["id"]}'] = gc['ctaBrowser']
        translations[lang] = tbl

    n_shot = ninely['assets']['screenshots'][0]
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>aviisr games · Small mobile games, made with care</title>
<meta name="description" content="aviisr games makes Ninely, Middle East 2030, Morning Paper Route, Baylight and Mila. Five games on Google Play now; Middle East 2030, Baylight and Mila (Israel) also on iPhone.">
<meta name="google-site-verification" content="oh0yHwl6YiX3dvIZYH5wIyc5pM6vJMYK3q-frBAYXlY">
<meta name="google-site-verification" content="oOOd1kEtVYr2Y1KLxcsYjZZEJLcLkjKQKhZO3RPxahU">
<meta name="facebook-domain-verification" content="ujlw9q4t20ufpcquni2zjk27ozhi6c">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta name="google-adsense-account" content="ca-pub-2451365263828795">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https://*.goatcounter.com; object-src 'none'; base-uri 'self';">
<link rel="canonical" href="https://aviisrgames.com/">
<meta property="og:title" content="aviisr games · Small mobile games, made with care">
<meta property="og:type" content="website">
<meta property="og:url" content="https://aviisrgames.com/">
<meta property="og:image" content="https://aviisrgames.com/assets/og/studio.jpg">
<meta property="og:description" content="Ninely, Middle East 2030, Morning Paper Route, Baylight and Mila.">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="stylesheet" href="assets/site.css">
<link rel="stylesheet" href="assets/pilot-2.css">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "aviisr games",
  "url": "https://aviisrgames.com/",
  "logo": "https://aviisrgames.com/favicon.svg",
  "email": "aviisr@aviisrgames.com",
  "sameAs": [
    "https://play.google.com/store/apps/developer?id=Aviisr",
    "https://www.youtube.com/@aviisrgames"
  ]
}}
</script>
<script src="assets/i18n.js"></script>
</head>
<body class="edition page-home">
<a class="skip-link" href="#main" data-i18n="w_skip">Skip to content</a>
<header>
<div class="col bar">
  <a class="logo" href="/" aria-label="aviisr games"><img src="/assets/logo/wordmark-light.svg" alt="" width="128" height="36"></a>
  <nav class="links" aria-label="Main"><a href="#games" data-i18n="w_games">Games</a><a href="ninely/strategy/" data-i18n="w_guides">Guides</a><a href="notes/" data-i18n="w_notes">Notes</a><a href="about/" data-i18n="w_about">About</a><a href="support/" data-i18n="navSupport">Support</a></nav>
  <div class="langbox"><label for="lang-switcher" data-i18n="w_lang">Language</label><nav class="lang"></nav></div>
</div>
</header>
<main id="main">

<section class="col editionlead" aria-labelledby="h-hero">
  <div>
    <p class="kicker" data-i18n="w_featured">Featured game  /  Ninely</p>
    <h1 id="h-hero"><span data-i18n="w_heroStart">A little more</span><br><em data-i18n="w_heroAccent">logic.</em></h1>
    <p class="lead" data-i18n="w_ninelyLead">{esc(ninely["copy"]["en"]["lead"])}</p>
    <div class="actions">
      <a class="action" href="{esc(ninely["hub"])}" data-i18n="w_ninelyHub">{esc(ninely["copy"]["en"]["ctaHub"])}</a>
      <a class="action action-secondary" href="{esc(ninely["browser"])}" data-i18n="w_ninelyBtn">{esc(ninely["copy"]["en"]["ctaBrowser"])}</a>
    </div>
    <p class="note" data-i18n="platformLine">{esc(lines["en"])}</p>
  </div>
  <figure class="featureposter">
    <div class="poster" style="--paper:{esc(ninely["paperColor"])}">
      <span class="poster-letter" aria-hidden="true" dir="ltr">{esc(ninely["posterLetter"])}</span>
      <span class="poster-ring" aria-hidden="true"></span>
      <img class="capture" src="{esc(n_shot["src"])}" alt="{esc(n_shot["alt"]["en"])}" width="{n_shot["width"]}" height="{n_shot["height"]}" fetchpriority="high">
    </div>
    <figcaption><span data-i18n="w_heroCaption">Ninely</span><span data-i18n="w_heroCaptionSub">{esc(ninely["copy"]["en"]["caption"])}</span></figcaption>
  </figure>
</section>

<section id="play-now" class="col playhero" aria-labelledby="h-play">
  <p class="kicker" data-i18n="w_playKicker">Browser games</p>
  <h2 id="h-play" data-i18n="w_playTitle">Play in your browser</h2>
  <div class="playlayout">
    <div class="playfocus">
      <div>
        <p class="kicker" data-i18n="w_dailyKicker">Daily Sudoku  /  Ninely</p>
        <h3 data-i18n="w_dailyTitle">Today’s puzzle</h3>
        <p data-i18n="w_dailyDesc">Open the board in your browser. A new puzzle arrives each day.</p>
        <a class="action" href="{esc(ninely["browser"])}" data-i18n="w_ninelyBtn">{esc(ninely["copy"]["en"]["ctaBrowser"])}</a>
      </div>
      <img class="playscreen" src="{esc(n_shot["src"])}" alt="" width="{n_shot["width"]}" height="{n_shot["height"]}" loading="lazy" decoding="async">
    </div>
    <div class="playlist">
      <h3 data-i18n="w_alsoPlay">Also playable</h3>
{chr(10).join(deck_html)}
    </div>
  </div>
</section>

<section class="col block" id="games" aria-labelledby="h-collection">
  <h2 id="h-collection" data-i18n="w_collection">The collection</h2>
  <div class="collection">
{chr(10).join(cards_html)}
  </div>
</section>

<section id="studio" class="col studio" aria-labelledby="h-studio">
  <div class="card">
    <h2 id="h-studio" data-i18n="contactTitle">Studio Contact &amp; Support</h2>
    <p data-i18n="contactSub">Player inquiries, bug reports, ad privacy requests, or business correspondence:</p>
    <p class="mail"><a href="mailto:aviisr@aviisrgames.com">aviisr@aviisrgames.com</a></p>
  </div>
</section>

<footer>
  <div class="col">
    <img class="foot-brand" src="/assets/logo/wordmark-dark.svg" alt="aviisr games" width="128" height="36">
    <div>© aviisr games · <a href="about/" data-i18n="w_about">About</a> · <a href="notes/" data-i18n="w_notes">Notes</a> · <a href="support/" data-i18n="navSupport">Support</a> · <a href="privacy/" data-i18n="navPrivacy">Privacy Policy</a> · <a href="terms/">Terms</a> · <a href="accessibility/">Accessibility</a> · <a href="app-ads.txt">app-ads.txt</a> · <a href="ads.txt">ads.txt</a> · <a href=".well-known/security.txt" data-i18n="w_security">Security</a></div>
  </div>
</footer>
</main>
<script>
(function () {{
  'use strict';

  var translations = {json.dumps(translations, ensure_ascii=False, indent=2)};

  var TITLES = {{
    en: "aviisr games · Small mobile games, made with care",
    he: "aviisr games · משחקי מובייל קטנים, עשויים בקפידה",
    ar: "aviisr games · ألعاب هاتف صغيرة، مصنوعة بعناية"
  }};

  AviisrI18n.init({{
    supported: ['en', 'he', 'ar'],
    translations: translations,
    defaultLang: 'en',
    onLanguageChange: function (lang) {{
      document.title = TITLES[lang] || TITLES.en;
    }}
  }});
}})();
</script>
<script src="/assets/play-badge.js"></script>
<script src="/assets/count.js" defer></script>
<script src="assets/site.js" defer></script>
</body>
</html>
'''


def render_ninely(reg):
    games = reg['games']
    by_id = {g['id']: g for g in games}
    n = by_id['ninely']
    siblings = [by_id['middle-east-2030'], by_id['baylight']]
    shots = n['assets']['screenshots']

    def shot_strip(lang, eager_first=False):
        aria = {'en': 'Ninely screenshots', 'he': 'צילומי מסך של Ninely', 'ar': 'لقطات شاشة من Ninely'}[lang]
        imgs = []
        for idx, s in enumerate(shots):
            attr = 'fetchpriority="high"' if (eager_first and idx == 0) else 'loading="lazy"'
            imgs.append(
                f'<img src="/{esc(s["src"])}" width="{s["width"]}" height="{s["height"]}" '
                f'{attr} decoding="async" alt="{esc(s["alt"][lang])}">'
            )
        dir_attr = ' dir="rtl"' if lang in ('he', 'ar') else ''
        return (
            f'      <div data-lang="{lang}" lang="{lang}"{dir_attr}>'
            f'<div class="screens" role="region" aria-label="{esc(aria)}" tabindex="0">'
            + ''.join(imgs) + '</div></div>'
        )

    more_items = []
    for sib in siblings:
        key = 'w_meH' if sib['id'] == 'middle-east-2030' else 'w_bayH'
        more_items.append(
            f'      <li><a class="mini" data-world="{esc(sib["id"])}" href="/{esc(sib["hub"])}">'
            f'<img src="/{esc(sib["assets"]["icon"])}" alt="" width="{sib["assets"]["iconWidth"]}" height="{sib["assets"]["iconHeight"]}">'
            f'<span><b>{esc(sib["storeTitle"])}</b><span data-i18n="{key}">{esc(sib["copy"]["en"]["headline"])}</span></span></a></li>'
        )

    hub_translations = {
        'en': {
            'w_skip': 'Skip to content',
            'w_games': 'Games',
            'w_lang': 'Language',
            'w_tagNinely': n['copy']['en']['tag'],
            'w_ninelyH': n['copy']['en']['headline'],
            'w_ninelyBtn': n['copy']['en']['ctaBrowser'],
            'w_storeStatus': f'{n["copy"]["en"]["storeStatus"]} · Verified {n["verifiedOn"]}',
            'w_meH': siblings[0]['copy']['en']['headline'],
            'w_bayH': siblings[1]['copy']['en']['headline'],
            'w_guides': 'Strategy guides',
            'w_more': 'More from aviisr games',
            'iphoneSoon': 'Not on iPhone yet',
        },
        'he': {
            'w_skip': 'דלגו לתוכן',
            'w_games': 'משחקים',
            'w_lang': 'שפה',
            'w_tagNinely': n['copy']['he']['tag'],
            'w_ninelyH': n['copy']['he']['headline'],
            'w_ninelyBtn': n['copy']['he']['ctaBrowser'],
            'w_storeStatus': f'{n["copy"]["he"]["storeStatus"]} · אומת {n["verifiedOn"]}',
            'w_meH': siblings[0]['copy']['he']['headline'],
            'w_bayH': siblings[1]['copy']['he']['headline'],
            'w_guides': 'מדריכי אסטרטגיה',
            'w_more': 'עוד מ-aviisr games',
            'iphoneSoon': 'עדיין לא ב-iPhone',
        },
        'ar': {
            'w_skip': 'تخطَّ إلى المحتوى',
            'w_games': 'الألعاب',
            'w_lang': 'اللغة',
            'w_tagNinely': n['copy']['ar']['tag'],
            'w_ninelyH': n['copy']['ar']['headline'],
            'w_ninelyBtn': n['copy']['ar']['ctaBrowser'],
            'w_storeStatus': f'{n["copy"]["ar"]["storeStatus"]} · {n["verifiedOn"]}',
            'w_meH': siblings[0]['copy']['ar']['headline'],
            'w_bayH': siblings[1]['copy']['ar']['headline'],
            'w_guides': 'أدلة الاستراتيجيات',
            'w_more': 'المزيد من aviisr games',
            'iphoneSoon': 'ليست على iPhone بعد',
        },
    }

    return f'''<!doctype html>
<html lang="en">
<head>
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; font-src 'self'; img-src 'self' data: https://*.goatcounter.com; object-src 'none'; base-uri 'self';">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(n["storeTitle"])} · Sudoku with hints that teach</title>
<link rel="canonical" href="https://aviisrgames.com/ninely/">
<meta name="description" content="Ninely: Sudoku that explains every move. Get it on Google Play, play the daily puzzle in your browser, or get help and privacy information.">
<link rel="icon" href="../favicon.svg" type="image/svg+xml">
<meta property="og:title" content="{esc(n["storeTitle"])}">
<meta property="og:type" content="website">
<meta property="og:url" content="https://aviisrgames.com/ninely/">
<meta property="og:image" content="https://aviisrgames.com/assets/og/ninely.jpg">
<meta property="og:description" content="{esc(n["copy"]["en"]["lead"])}">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="../assets/site.css">
<link rel="stylesheet" href="../assets/hub.css">
<link rel="stylesheet" href="../assets/pilot-2.css">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "VideoGame",
  "name": "Ninely: Sudoku & Logic Puzzle",
  "description": "Sudoku that explains every move. Smart Hints teach the logic step by step, with a new daily puzzle every day.",
  "url": "https://aviisrgames.com/ninely/",
  "genre": ["Puzzle", "Logic"],
  "gamePlatform": ["Android"],
  "applicationCategory": "GameApplication",
  "operatingSystem": "Android",
  "inLanguage": ["en", "he", "ar", "ja", "ko", "de", "fr", "nl", "es", "pt-BR", "zh-TW", "zh-CN", "it", "ru", "sv", "da", "nb", "fi"],
  "offers": {{ "@type": "Offer", "price": "0", "priceCurrency": "USD" }},
  "author": {{ "@type": "Organization", "name": "aviisr games", "email": "aviisr@aviisrgames.com" }}
}}
</script>
</head>
<body class="edition page-game">
<a class="skip-link" href="#main" data-i18n="w_skip">Skip to content</a>
<header>
<div class="col bar">
  <a class="logo" href="/" aria-label="aviisr games"><img src="/assets/logo/wordmark-light.svg" alt="" width="128" height="36"></a>
  <nav class="links" aria-label="Main"><a href="/" data-i18n="w_games">Games</a><a href="strategy/" data-i18n="w_guides">Strategy guides</a><a href="/support/" data-i18n="navSupport">Support</a></nav>
  <div class="langbox"><label for="lang-switcher" data-i18n="w_lang">Language</label><nav class="lang"></nav></div>
</div>
</header>
<main id="main">
<section class="mast" data-world="ninely" aria-labelledby="h-hub">
  <div class="col wrap">
    <div class="spread">
      <div class="copy">
        <span class="tag" data-i18n="w_tagNinely">{esc(n["copy"]["en"]["tag"])}</span>
        <div class="id"><img src="/{esc(n["assets"]["icon"])}" alt="" width="{n["assets"]["iconWidth"]}" height="{n["assets"]["iconHeight"]}"><h1 id="h-hub">{esc(n["storeTitle"])}</h1></div>
        <p class="hl" data-i18n="w_ninelyH">{esc(n["copy"]["en"]["headline"])}</p>
        <p class="lead" data-lang="en" lang="en">{esc(n["copy"]["en"]["hubLead"])}</p>
        <p class="lead" data-lang="he" lang="he" dir="rtl">{esc(n["copy"]["he"]["hubLead"])}</p>
        <p class="lead" data-lang="ar" lang="ar" dir="rtl">{esc(n["copy"]["ar"]["hubLead"])}</p>
        <p class="note" data-i18n="w_storeStatus">{esc(hub_translations["en"]["w_storeStatus"])}</p>
        <div class="acts">
          <a class="btn" href="play/" data-i18n="w_ninelyBtn">{esc(n["copy"]["en"]["ctaBrowser"])}</a>
          <a class="play-badge" href="{esc(n["hubPlayLink"])}"><img data-play-badge data-app="Ninely" src="/assets/badges/google-play-en.png" alt="Get it on Google Play: Ninely" width="150" height="58"></a>
          <p class="ios-note" data-i18n="iphoneSoon">Not on iPhone yet</p>
        </div>
      </div>
      <div class="shots">
{shot_strip("en", eager_first=True)}
{shot_strip("he")}
{shot_strip("ar")}
      </div>
    </div>
  </div>
</section>

<div class="col hubbody">
  <div data-lang="en" lang="en"><ul class="benefits"><li>Smart Hints explain the logic behind every move, so you learn instead of guessing.</li><li>Practice each technique in short drills and track your mastery.</li><li>A fresh daily challenge and five levels, from Easy to Master.</li></ul></div>
  <div data-lang="he" lang="he" dir="rtl"><ul class="benefits"><li>רמזים חכמים מסבירים את ההיגיון מאחורי כל צעד, כך שלומדים במקום לנחש.</li><li>תרגול כל טכניקה בתרגילים קצרים ומעקב אחר ההתקדמות.</li><li>אתגר יומי חדש וחמש רמות קושי, מקל ועד מאסטר.</li></ul></div>
  <div data-lang="ar" lang="ar" dir="rtl"><ul class="benefits"><li>تلميحات ذكية تشرح المنطق وراء كل خطوة، فتتعلّم بدل أن تخمّن.</li><li>تدرّب على كل تقنية في تمارين قصيرة وتابع تقدّمك.</li><li>تحدٍّ يومي جديد وخمسة مستويات، من السهل إلى الخبير.</li></ul></div>
  <ul class="hublinks"><li><a href="play/" data-i18n="tryInBrowser">Play in your browser</a></li><li><a href="strategy/" data-i18n="w_guides">Strategy guides</a></li></ul>
  <div class="qr-handoff"><img src="/assets/qr/ninely.svg" alt="QR code that opens this page on your phone" width="112" height="112"><p data-i18n="qrText">On a computer? Point your phone camera at the code to open this page on your phone, then tap the Google Play button.</p></div>

  <section class="more" aria-labelledby="h-more">
    <h2 id="h-more" data-i18n="w_more">More from aviisr games</h2>
    <ul class="minis">
{chr(10).join(more_items)}
    </ul>
  </section>

  <section class="help" aria-labelledby="h-help">
    <h2 id="h-help" data-i18n="navSupport">Support</h2>
    <div data-lang="en" lang="en">
<p>Questions, problems or ideas? Write to us:</p>
<p class="mail"><a href="mailto:aviisr@aviisrgames.com?subject=Ninely%20support">aviisr@aviisrgames.com</a></p>
<p>Tip: in the game, <b>Settings &gt; Send feedback</b> writes the email for you and can attach a technical log. It helps us fix problems faster.</p>
<h2>Ads and privacy</h2>
<p>Choose personalized or non-personalized ads in <b>Settings</b>. You see the same number of ads either way. Usage statistics can be turned off in <b>Settings</b>. See the <a href="privacy.html">privacy policy</a>.</p>
<h2>Purchases</h2>
<p>Bought Remove Ads or VIP on another device or after reinstalling? Use <b>Settings &gt; Restore purchases</b>.</p>
    </div>
    <div data-lang="he" lang="he" dir="rtl">
<p>שאלות, תקלות או רעיונות? כתבו לנו:</p>
<p class="mail"><a href="mailto:aviisr@aviisrgames.com?subject=Ninely%20support">aviisr@aviisrgames.com</a></p>
<p>טיפ: במשחק, <b>הגדרות &gt; שליחת משוב</b> מכין את הדוא"ל ויכול לצרף יומן טכני. זה עוזר לנו לתקן מהר יותר.</p>
<h2>פרסומות ופרטיות</h2>
<p>אפשר לבחור פרסומות מותאמות או לא מותאמות ב<b>הגדרות</b>. מספר הפרסומות זהה בכל מקרה. את סטטיסטיקת השימוש אפשר לכבות ב<b>הגדרות</b>. פרטים ב<a href="privacy.html#he">מדיניות הפרטיות</a>.</p>
<h2>רכישות</h2>
<p>קנית הסרת פרסומות או VIP במכשיר אחר או לפני התקנה מחדש? <b>הגדרות &gt; שחזור רכישות</b>.</p>
    </div>
    <div data-lang="ar" lang="ar" dir="rtl">
<p>أسئلة أو مشكلات أو أفكار؟ راسلنا:</p>
<p class="mail"><a href="mailto:aviisr@aviisrgames.com?subject=Ninely%20support">aviisr@aviisrgames.com</a></p>
<p>نصيحة: في اللعبة، <b>الإعدادات &gt; إرسال ملاحظات</b> يجهّز الرسالة ويمكنه إرفاق سجل تقني. يساعدنا ذلك على إصلاح المشكلات بسرعة.</p>
<h2>الإعلانات والخصوصية</h2>
<p>اختر إعلانات مخصصة أو غير مخصصة من <b>الإعدادات</b>. عدد الإعلانات هو نفسه في الحالتين. ويمكن إيقاف إحصائيات الاستخدام من <b>الإعدادات</b>. التفاصيل في <a href="privacy.html#ar">سياسة الخصوصية</a>.</p>
<h2>المشتريات</h2>
<p>اشتريت إزالة الإعلانات أو VIP على جهاز آخر أو قبل إعادة التثبيت؟ <b>الإعدادات &gt; استعادة المشتريات</b>.</p>
    </div>
  </section>
  <section class="about" lang="en" dir="ltr" aria-labelledby="h-about">
    <h2 id="h-about">Why Ninely teaches instead of just checking</h2>
    <p>Most sudoku apps tell you a number is wrong and stop there. We built Ninely around a different question: when you are stuck, what is the next piece of reasoning you are missing? A Smart Hint names the technique, points at the cells involved and explains why the move is safe, so each hint is a small lesson you can reuse on the next puzzle.</p>
    <p>The five levels, from Easy to Master, are tied to the techniques a puzzle needs rather than to how few clues it shows. An Easy board can be finished with singles alone. Hard boards ask for pairs, and the top levels expect triples or fish patterns such as X-Wing and Swordfish. Moving up therefore means learning something new, not just playing faster.</p>
    <p>To play well, work in a steady order. Scan for singles first, add pencil marks only when the easy moves are gone, and remove a digit from the notes as soon as you place it. Treat a hint as feedback: ask which technique it used, and try to find the same pattern yourself next time. Short drills for each technique help it stick.</p>
    <p>The daily puzzle gives everyone the same board, so it works as a ten-minute habit. If you would rather read first, the <a href="strategy/how-to-solve-sudoku/">step-by-step solving guide</a> covers the whole ladder in plain language.</p>
    <p>Want to talk through techniques with other players? <a href="/go/nfb-en-hub/">Learn Sudoku Techniques</a> is a small public Facebook group run by the solo developer of Ninely at aviisr games. You do not need the app to join.</p>
  </section>
</div>

<footer>
  <div class="col">
    <img class="foot-brand" src="/assets/logo/wordmark-dark.svg" alt="aviisr games" width="128" height="36">
    <div>© aviisr games · <a href="/support/" data-i18n="navSupport">Support</a> · <a href="privacy.html" data-i18n="navPrivacy">Privacy Policy</a> · <a href="/" data-i18n="navAllGames">All Games</a></div>
  </div>
</footer>
</main>
<script src="../assets/i18n.js"></script>
<script>
  AviisrI18n.init({{
    supported: ['en', 'he', 'ar'],
    defaultLang: 'en',
    translations: {json.dumps(hub_translations, ensure_ascii=False, indent=4)}
  }});
</script>
<script src="/assets/play-badge.js"></script>
<script src="/assets/count.js" defer></script>
<script src="../assets/site.js" defer></script>
</body>
</html>
'''


def render_mila(reg):
    m = next(g for g in reg['games'] if g['id'] == 'mila')
    icon_rel = m['assets']['icon'].removeprefix('mila/')
    story_shot = m['assets']['screenshots'][0]
    home_shot = m['assets']['screenshots'][1]
    words_shot = m['assets']['screenshots'][2]

    # Worksheet cards generated directly from site/games.json (A07 parity)
    ws_cards = []
    ws_he = {}
    ws_en = {}
    for w in m['worksheets']:
        g = w['grade']
        ws_he[f'print{g}Title'] = w['heTitle']
        ws_he[f'print{g}Desc'] = w['heDesc']
        ws_he[f'print{g}Btn'] = w['heBtn']
        ws_en[f'print{g}Title'] = w['enTitle']
        ws_en[f'print{g}Desc'] = w['enDesc']
        ws_en[f'print{g}Btn'] = w['enBtn']
        ws_cards.append(
            f'          <div class="card print-card">\n'
            f'            <h3 data-i18n="print{g}Title">{esc(w["heTitle"])}</h3>\n'
            f'            <p data-i18n="print{g}Desc">{esc(w["heDesc"])}</p>\n'
            f'            <a class="btn-print-sheet" href="{esc(w["href"])}" data-i18n="print{g}Btn">{esc(w["heBtn"])}</a>\n'
            f'          </div>'
        )

    translations = {
        'he': {
            'skipLink': 'דילוג לתוכן',
            'navFamily': 'למשפחות',
            'navWorksheets': 'דפי עבודה להדפסה',
            'navSupport': 'תמיכה במילה',
            'navPrivacy': 'פרטיות',
            'navAllGames': 'כל המשחקים',
            'heroKicker': 'מילה · אנגלית לכיתות א׳–ו׳',
            'milaHeroStart': 'מתרגלים אנגלית',
            'milaHeroAccent': 'בבית.',
            'milaHeroLead': m['copy']['he']['lead'],
            'storeStatus': f'{m["copy"]["he"]["storeStatus"]} · אומת {m["verifiedOn"]}',
            'iconOriginNote': m['assets']['iconGapNote']['he'],
            'appStoreLabel': 'App Store (ישראל / Israel)',
            'screenCap1': story_shot['alt']['he'],
            'screenCap2': home_shot['alt']['he'],
            'screenCap3': words_shot['alt']['he'],
            'sampleTitle': 'פעילות לדוגמה מתוך מילה',
            'sampleSub': 'כרטיסיית אוצר מילים והבנת הנקרא — האזנה איטית, תרגום עברי בלחיצה ומשפט דוגמה:',
            'sampleWordTrans': 'כלב',
            'sampleSentHeb': 'לדן יש כלב ידידותי.',
            'sampleNote': 'בלי עונשים ובלי פסילות: אחרי טעות מקבלים רמז ברור והסבר בעברית.',
            'curriculumTitle': 'התאמה לכיתות א׳–ו׳ ורשימות משרד החינוך',
            'curriculumDesc': 'באפליקציה 1,270 מילים בארבע רמות. מכיתה ג׳ מתרגלים גם מילים לפי רשימות משרד החינוך Pre-Band I ו-Band I. מילה אינה קשורה למשרד החינוך.',
            'grade12Badge': 'כיתות א׳–ב׳',
            'grade12Title': 'אנגלית בעל פה וללא קריאה',
            'grade12Desc': 'צלילים, אותיות ה-ABC והאזנה למילים ראשונות עם תמונות ברורות (בכיתות א׳–ב׳ אין רשימת מילים רשמית של משרד החינוך).',
            'grade3Badge': 'כיתה ג׳',
            'grade3Title': 'אותיות, צלילים ומילים ראשונות',
            'grade3Desc': 'היכרות עם אותיות באנגלית, צלילים, אותיות ניקוד ומילים ראשונות (Pre-Band I).',
            'grade4Badge': 'כיתה ד׳',
            'grade4Title': 'אוצר מילים וסיפורים קצרים',
            'grade4Desc': 'מילים מרשימת Pre-Band I וסיפורים קצרים להבנת הנקרא, עם הקראה ותרגום לעברית.',
            'grade56Badge': 'כיתות ה׳–ו׳',
            'grade56Title': 'אוצר מילים והבנת הנקרא',
            'grade56Desc': 'מילים מרשימת Band I, השלמת משפטים, סיפורים קצרים (54 סיפורים בסך הכל) ואתגר האלופים.',
            'pillarsTitle': 'רכישה חד-פעמית ופרטיות ללא פשרות',
            'pillarsSub': 'במילה אין פרסומות, אין מנוי חודשי ואין כלי מעקב או אנליטיקה.',
            'pil1Title': 'בלי פרסומות',
            'pil1Desc': 'אפס פרסומות קופצות, אפס סרטוני שיווק ואפס קידום משחקים אחרים.',
            'pil2Title': 'רכישה חד-פעמית (₪49.90)',
            'pil2Desc': 'מתחילים בחינם (20 מילים בכל קבוצה, לוח ABC ודוגמאות סיפור). הגרסה המלאה נפתחת בתשלום חד-פעמי מאחורי שער הורים.',
            'pil3Title': 'פרטיות מלאה במכשיר',
            'pil3Desc': 'נתוני התרגול נשמרים במכשיר ועשויים להיכלל בגיבוי iCloud או Android. הרכישה נבדקת מול החנות ללא שליחת מידע לשרתים שלנו.',
            'privacyLink': 'לקריאת מדיניות הפרטיות המלאה של מילה ←',
            'printTitle': 'כרטיסיות ודפי עבודה להדפסה בבית',
            'printSub': 'בחרו את השכבה המדויקת — דף העבודה ומפתח התשובות נפתחים בהתאמה מלאה לשכבה שנבחרה.',
            'faqTitle': 'שאלות נפוצות',
            'faq1Q': 'לאילו כיתות האפליקציה מתאימה?',
            'faq1A': 'האפליקציה נבנתה במיוחד עבור ילדים בכיתות א׳ עד ו׳ בישראל. התוכן מותאם לשנת הלימודים וגם לתרגול קצר בחופשות.',
            'faq2Q': 'האם האפליקציה דורשת חיבור לאינטרנט?',
            'faq2A': 'לא. כל אוצר המילים, ההקלטות הקוליות והסיפורים שמורים בתוך האפליקציה. ניתן לתרגל ללא רשת.',
            'faq3Q': 'האם אפשר להשתמש בכמה ילדים באותו מכשיר?',
            'faq3A': 'כן. באזור ההורים תוכלו להוסיף פרופיל לכל ילד, עם רצף אימון ודו״ח שבועי נפרד. הרכישה מכסה את כל הילדים במכשיר.',
            'faq4Q': 'איך יוצרים קשר אם יש שאלה?',
            'faq4Pre': 'אפשר לכתוב אלינו ישירות לכתובת',
            'faq4Mid': 'או לבקר ב',
            'faq4Support': 'עמוד התמיכה של מילה',
            'footerCopy': '© aviisr games. כל הזכויות שמורות.',
            'footerNonAffil': 'מילה היא אפליקציה עצמאית שפותחה על ידי aviisr games לתרגול בבית לצד בית הספר, ואינה קשורה למשרד החינוך.',
            **ws_he,
        },
        'en': {
            'skipLink': 'Skip to content',
            'navFamily': 'For families',
            'navWorksheets': 'Worksheets (HE/EN)',
            'navSupport': 'Mila support',
            'navPrivacy': 'Privacy',
            'navAllGames': 'All Games',
            'heroKicker': 'Mila · English for Grades 1–6',
            'milaHeroStart': 'A little English,',
            'milaHeroAccent': 'at home.',
            'milaHeroLead': m['copy']['en']['lead'],
            'storeStatus': f'{m["copy"]["en"]["storeStatus"]} · Verified {m["verifiedOn"]}',
            'iconOriginNote': m['assets']['iconGapNote']['en'],
            'appStoreLabel': 'App Store (ישראל / Israel)',
            'screenCap1': story_shot['alt']['en'],
            'screenCap2': home_shot['alt']['en'],
            'screenCap3': words_shot['alt']['en'],
            'sampleTitle': 'Sample Activity Inside Mila',
            'sampleSub': 'A vocabulary & story card — clear pronunciation, instant Hebrew tap-translation, and an example sentence:',
            'sampleWordTrans': 'כלב (dog)',
            'sampleSentHeb': 'לדן יש כלב ידידותי.',
            'sampleNote': 'No penalties or lockouts: mistakes show a clear hint and Hebrew explanation.',
            'curriculumTitle': 'Grades 1–6 Alignment & Curriculum Fit',
            'curriculumDesc': 'Mila includes 1,270 words across four bands. From grade 3, words align with Ministry of Education Pre-Band I and Band I lists (Mila is independent and not affiliated with the Ministry).',
            'grade12Badge': 'Grades 1–2',
            'grade12Title': 'Spoken English before reading',
            'grade12Desc': 'Phonics, ABC letters, and listening to first words with clear pictures (grades 1–2 have no official Ministry word list).',
            'grade3Badge': 'Grade 3',
            'grade3Title': 'Letters, sounds and first words',
            'grade3Desc': 'English letters, sounds, vowels, and first Pre-Band I vocabulary words.',
            'grade4Badge': 'Grade 4',
            'grade4Title': 'Vocabulary and short stories',
            'grade4Desc': 'Pre-Band I words and short reading-comprehension stories with read-aloud and Hebrew translation.',
            'grade56Badge': 'Grades 5–6',
            'grade56Title': 'Vocabulary and reading comprehension',
            'grade56Desc': 'Band I words, sentence completion, 54 illustrated short stories, and the Champions Challenge.',
            'pillarsTitle': 'Fair One-Time Purchase & Privacy',
            'pillarsSub': 'Mila has zero ads, no monthly subscription, and zero third-party trackers.',
            'pil1Title': 'Zero Ads',
            'pil1Desc': 'No pop-ups, no video ads, and no cross-promotion to other studio games.',
            'pil2Title': 'One-Time Purchase (₪49.90)',
            'pil2Desc': 'Start free (20 words per band, ABC board, and story samples). Unlock all content once behind a parent math gate.',
            'pil3Title': 'On-Device Privacy',
            'pil3Desc': 'Practice stays on your device (and optional iCloud/Android backup). Purchases are verified with the store without sending practice data to our servers.',
            'privacyLink': 'Read Mila’s full privacy policy →',
            'printTitle': 'Printable Practice Sheets (Hebrew & English)',
            'printSub': 'Pick the exact grade below. Note for adults: the printable sheets and answer keys are intentionally written in Hebrew and English for Hebrew-speaking learners.',
            'faqTitle': 'Frequently Asked Questions',
            'faq1Q': 'Which school grades is Mila designed for?',
            'faq1A': 'Mila is designed for Hebrew-speaking children in grades 1 through 6 in Israel, covering school-year vocabulary and short holiday refreshers.',
            'faq2Q': 'Does Mila require an internet connection?',
            'faq2A': 'No. All vocabulary, audio recordings, and stories are stored inside the app so children can practice offline anywhere.',
            'faq3Q': 'Can multiple children use the same device?',
            'faq3A': 'Yes. Inside the Parent Area you can add separate child profiles with individual streaks and weekly reports. The one-time unlock covers every child on the device.',
            'faq4Q': 'How do we reach support?',
            'faq4Pre': 'Email us directly at',
            'faq4Mid': 'or visit the',
            'faq4Support': 'Mila support page',
            'footerCopy': '© aviisr games. All rights reserved.',
            'footerNonAffil': 'Mila is an independent app developed by aviisr games for home English practice alongside school. It is not affiliated with the Ministry of Education.',
            **ws_en,
        },
    }

    return f'''<!doctype html>
<html lang="he" dir="rtl">
<head>
  <meta charset="utf-8">
  <link rel="icon" href="../assets/icons/mila.webp" type="image/webp">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>מילה - אנגלית לילדים (כיתות א׳–ו׳) | תרגול מותאם אישית בבית</title>
  <meta name="description" content="מילה היא אפליקציה לתרגול אנגלית לילדים דוברי עברית בכיתות א׳–ו׳. בלי פרסומות או מנוי. התרגול עובד גם בלי אינטרנט.">
  <meta name="referrer" content="strict-origin-when-cross-origin">
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; font-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'self';">
  <link rel="canonical" href="https://aviisrgames.com/mila/">
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://aviisrgames.com/mila/">
  <meta property="og:title" content="מילה - אנגלית לילדים (כיתות א׳–ו׳)">
  <meta property="og:description" content="תרגול אנגלית בבית לילדים דוברי עברית. מילים, צלילים וסיפורים קצרים. בלי פרסומות או מנוי.">
  <meta property="og:image" content="https://aviisrgames.com/mila/assets/og-mila.png">
  <meta name="twitter:card" content="summary_large_image">
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    "name": "מילה - אנגלית לילדים (Mila - English for Kids)",
    "description": "English practice for Hebrew-speaking children in grades 1–6. Practice works offline. No ads or subscriptions.",
    "url": "https://aviisrgames.com/mila/",
    "applicationCategory": "EducationalApplication",
    "inLanguage": ["he", "en"],
    "author": {{ "@type": "Organization", "name": "aviisr games", "email": "aviisr@aviisrgames.com" }}
  }}
  </script>
  <style>
    :root {{
      --cream:#faf5ff;--ink:#1e1435;--muted:#4f436b;--lilac:#d3b8fa;--accent:#5b21b6;--accent-dark:#43138c;
      --line:#d8c8ef;--surface:#ffffff;--success:#047857;
      --body:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Arial Hebrew",Arial,sans-serif;
      --serif:"Iowan Old Style",Baskerville,Georgia,"Times New Roman",serif;
    }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; background:var(--cream); color:var(--ink); font:400 1rem/1.6 var(--body); }}
    img {{ display:block; max-width:100%; }}
    a {{ color:var(--accent); font-weight:650; text-decoration-thickness:1px; text-underline-offset:.18em; }}
    a:hover {{ text-decoration-thickness:2px; }}
    :focus-visible {{ outline:3px solid #1e3a8a; outline-offset:3px; box-shadow:0 0 0 5px #fff; }}
    .skip-link {{ position:absolute; inset-inline-start:12px; top:-80px; z-index:99; background:#1e1435; color:#fff; padding:10px 14px; border-radius:8px; text-decoration:none; }}
    .skip-link:focus {{ top:8px; }}
    .wrap {{ width:min(92%,1200px); margin-inline:auto; }}
    header {{ border-block-end:1px solid var(--line); background:var(--cream); }}
    .bar {{ display:flex; flex-wrap:wrap; align-items:center; gap:8px 20px; min-height:74px; padding-block:8px; }}
    .brand {{ margin-inline-end:auto; display:inline-flex; align-items:center; min-height:44px; }}
    .brand img {{ width:128px; height:36px; }}
    .nav-links {{ display:flex; flex-wrap:wrap; align-items:center; gap:6px 18px; }}
    .nav-links a {{ display:inline-flex; align-items:center; min-height:44px; color:var(--ink); text-decoration:none; font-size:.96rem; }}
    .nav-links a:hover {{ text-decoration:underline; }}
    .lang-switcher {{ min-height:44px; padding-inline:10px; border:1px solid var(--line); border-radius:8px; background:#fff; color:var(--ink); font:inherit; }}

    .spread {{ display:grid; grid-template-columns:1.08fr .92fr; gap:4.5%; align-items:center; padding-block:clamp(28px,4vw,54px); border-block-end:1px solid var(--ink); }}
    .kicker {{ display:flex; align-items:center; gap:12px; margin:0 0 14px; font-weight:750; font-size:.86rem; color:var(--muted); }}
    .familyicon {{ width:50px; height:50px; border-radius:12px; border:1px solid var(--line); }}
    h1 {{ margin:0; font:800 clamp(2.4rem,5.2vw,4.3rem)/1.06 var(--body); letter-spacing:-.025em; color:var(--ink); }}
    html[lang=en] h1 {{ font-family:var(--serif); font-weight:600; }}
    h1 em {{ font-style:normal; color:var(--accent); }}
    .lead {{ margin:16px 0 0; font-size:clamp(1.08rem,1.5vw,1.25rem); max-width:40ch; }}
    .store-status {{ margin:12px 0 0; font-size:.9rem; font-weight:700; color:var(--accent-dark); }}
    .icon-note {{ margin:8px 0 0; font-size:.84rem; color:var(--muted); max-width:48ch; }}
    .actions {{ display:flex; flex-wrap:wrap; gap:12px 14px; align-items:center; margin-top:20px; }}
    .appstore-badge {{
      display:inline-flex; align-items:center; gap:8px; min-height:48px; padding:10px 18px; border-radius:8px;
      background:#1e1435; color:#fff; text-decoration:none; font-weight:700; font-size:.96rem;
    }}
    .appstore-badge:hover {{ background:#34235e; }}
    .play-badge img {{ height:52px; width:auto; }}

    .poster {{
      position:relative; isolation:isolate; display:grid; place-items:center; height:clamp(290px,31vw,430px);
      overflow:hidden; background:var(--lilac); border-radius:10px; border:1px solid rgba(30,20,53,.14);
    }}
    .poster-letter {{ position:absolute; inset-inline-start:-.04em; top:-.26em; font:italic 700 clamp(260px,32vw,440px)/1.1 var(--serif); color:rgba(91,33,182,.22); z-index:-1; user-select:none; }}
    .poster-ring {{ position:absolute; inset-inline-start:46%; top:6%; height:118%; aspect-ratio:1; border:1px solid rgba(255,255,255,.65); border-radius:50%; z-index:-1; }}
    .poster .capture {{ height:82%; width:auto; max-width:65%; object-fit:contain; transform:rotate(4deg); border-radius:14px; border:2px solid #101426; box-shadow:8px 12px 0 rgba(30,20,53,.28); background:#fff; }}

    section.band {{ padding-block:clamp(28px,3.8vw,46px); border-block-end:1px solid var(--line); }}
    section.band h2 {{ margin:0 0 10px; font:800 clamp(1.55rem,2.6vw,2.15rem)/1.15 var(--body); color:var(--ink); }}
    .section-sub {{ margin:0 0 22px; color:var(--muted); max-width:58ch; }}

    .sample-box {{ display:grid; grid-template-columns:minmax(220px,300px) 1fr; gap:20px; align-items:center; background:#fff; border:1px solid var(--line); border-radius:12px; padding:20px; }}
    .sample-card {{ background:#faf5ff; border:2px dashed var(--accent); border-radius:10px; padding:16px; text-align:center; }}
    .sample-emoji {{ font-size:2.4rem; line-height:1.2; }}
    .sample-word {{ font-size:1.45rem; font-weight:800; color:var(--ink); margin-top:4px; }}
    .sample-trans {{ font-weight:700; color:var(--accent-dark); margin:4px 0 8px; }}
    .sample-sent {{ font-size:.92rem; color:var(--muted); border-block-start:1px solid var(--line); padding-top:8px; }}

    .screenshots-row {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:16px; margin-top:22px; }}
    .screenshot-card {{ background:#fff; border:1px solid var(--line); border-radius:12px; overflow:hidden; }}
    .screenshot-card img {{ width:100%; height:auto; }}
    .screenshot-caption {{ padding:10px 12px; font-size:.9rem; font-weight:700; color:var(--ink); text-align:center; }}

    .grid-3 {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr)); gap:16px; }}
    .grid-2 {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:16px; }}
    .card {{ background:#fff; border:1px solid var(--line); border-radius:12px; padding:20px; }}
    .card h3 {{ margin:0 0 8px; font-size:1.15rem; color:var(--accent-dark); }}
    .card p {{ margin:0; color:var(--muted); font-size:.96rem; }}

    .grade-item {{ display:flex; align-items:flex-start; gap:14px; background:#fff; border:1px solid var(--line); border-radius:12px; padding:16px; margin-bottom:12px; }}
    .grade-badge {{ background:var(--accent); color:#fff; font-weight:800; padding:6px 12px; border-radius:8px; white-space:nowrap; font-size:.92rem; }}
    .grade-desc h3 {{ margin:0 0 4px; font-size:1.05rem; color:var(--ink); }}
    .grade-desc p {{ margin:0; font-size:.94rem; color:var(--muted); }}

    .print-card {{ display:flex; flex-direction:column; gap:10px; }}
    .btn-print-sheet {{
      margin-top:auto; display:inline-flex; align-items:center; justify-content:center; min-height:44px; padding:9px 14px;
      border-radius:8px; background:var(--accent); color:#fff; text-decoration:none; font-weight:700; font-size:.94rem;
    }}
    .btn-print-sheet:hover {{ background:var(--accent-dark); text-decoration:none; }}

    .faq-item {{ background:#fff; border:1px solid var(--line); border-radius:12px; padding:18px; margin-bottom:12px; }}
    .faq-q {{ font-weight:800; color:var(--accent-dark); margin-bottom:6px; }}
    .faq-a {{ color:var(--muted); }}

    footer {{ background:#101426; color:#e7dfd1; padding-block:28px 34px; margin-top:32px; }}
    .foot {{ display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:14px; }}
    .foot img {{ width:128px; height:36px; }}
    footer a {{ color:#fff4e4; text-decoration:none; }}
    footer a:hover {{ text-decoration:underline; }}
    .non-affil {{ font-size:.86rem; color:#c8c3d4; margin-top:12px; max-width:65ch; }}

    @media (max-width:820px) {{
      .spread,.sample-box,.screenshots-row {{ grid-template-columns:1fr; }}
    }}
    @media (max-width:640px) {{
      .nav-links {{ width:100%; border-block-start:1px solid var(--line); padding-top:6px; }}
      .grade-item {{ flex-direction:column; }}
    }}
    @media (prefers-reduced-motion:reduce) {{ * {{ transition:none !important; }} }}
  </style>
</head>
<body class="edition page-mila">
  <a class="skip-link" href="#main" data-i18n="skipLink">דילוג לתוכן</a>
  <header>
    <div class="wrap bar">
      <a class="brand" href="../" aria-label="aviisr games"><img src="/assets/logo/wordmark-light.svg" alt="" width="128" height="36"></a>
      <nav class="nav-links" aria-label="ניווט">
        <a href="#family" data-i18n="navFamily">למשפחות</a>
        <a href="worksheets/" data-i18n="navWorksheets">דפי עבודה להדפסה</a>
        <a href="support/" data-i18n="navSupport">תמיכה במילה</a>
        <a href="privacy/" data-i18n="navPrivacy">פרטיות</a>
        <a href="../" data-i18n="navAllGames">כל המשחקים</a>
      </nav>
      <nav class="lang" aria-label="שפה"></nav>
    </div>
  </header>

  <main id="main">
    <section class="wrap spread" aria-labelledby="h-mila">
      <div>
        <p class="kicker"><img class="familyicon" src="{esc(icon_rel)}" alt="איור מילה מתוך App Store ישראל" width="{m["assets"]["iconWidth"]}" height="{m["assets"]["iconHeight"]}"><span data-i18n="heroKicker">מילה · אנגלית לכיתות א׳–ו׳</span></p>
        <h1 id="h-mila"><span data-i18n="milaHeroStart">מתרגלים אנגלית</span><br><em data-i18n="milaHeroAccent">בבית.</em></h1>
        <p class="lead" data-i18n="milaHeroLead">{esc(m["copy"]["he"]["lead"])}</p>
        <p class="store-status" data-i18n="storeStatus">{esc(translations["he"]["storeStatus"])}</p>
        <p class="icon-note" data-i18n="iconOriginNote">{esc(m["assets"]["iconGapNote"]["he"])}</p>
        <div class="actions">
          <a class="appstore-badge" href="{esc(m["appStore"]["url"])}" target="_blank" rel="noopener noreferrer" referrerpolicy="no-referrer" aria-label="הורדה ב-App Store (ישראל)">
            {appstore_svg(20)}
            <span data-i18n="appStoreLabel">App Store (ישראל / Israel)</span>
          </a>
          <a class="play-badge" href="{esc(m["hubPlayLink"])}" referrerpolicy="no-referrer"><img data-play-badge data-app="מילה · Mila" src="/assets/badges/google-play-iw.png" alt="Get it on Google Play: מילה · Mila" width="150" height="58"></a>
        </div>
      </div>
      <div class="poster">
        <span class="poster-letter" aria-hidden="true" dir="ltr">{esc(m["posterLetter"])}</span>
        <span class="poster-ring" aria-hidden="true"></span>
        <img class="capture" src="{esc(story_shot["src"].removeprefix("mila/"))}" alt="{esc(story_shot["alt"]["he"])}" width="{story_shot["width"]}" height="{story_shot["height"]}" fetchpriority="high">
      </div>
    </section>

    <section class="wrap band" id="sample" aria-labelledby="h-sample">
      <h2 id="h-sample" data-i18n="sampleTitle">פעילות לדוגמה מתוך מילה</h2>
      <p class="section-sub" data-i18n="sampleSub">כרטיסיית אוצר מילים והבנת הנקרא — האזנה איטית, תרגום עברי בלחיצה ומשפט דוגמה:</p>
      <div class="sample-box">
        <div class="sample-card">
          <div class="sample-emoji" aria-hidden="true">🐶</div>
          <div class="sample-word" dir="ltr" lang="en">dog</div>
          <div class="sample-trans" data-i18n="sampleWordTrans">כלב</div>
          <div class="sample-sent"><div dir="ltr" lang="en">Dan has a friendly dog.</div><div data-i18n="sampleSentHeb">לדן יש כלב ידידותי.</div></div>
        </div>
        <div>
          <p data-i18n="sampleNote">בלי עונשים ובלי פסילות: אחרי טעות מקבלים רמז ברור והסבר בעברית.</p>
          <div class="screenshots-row" role="group" aria-label="צילומי מסך מהאפליקציה">
            <div class="screenshot-card"><img src="{esc(story_shot["src"].removeprefix("mila/"))}" alt="{esc(story_shot["alt"]["he"])}" width="{story_shot["width"]}" height="{story_shot["height"]}" loading="lazy"><div class="screenshot-caption" data-i18n="screenCap1">{esc(story_shot["alt"]["he"])}</div></div>
            <div class="screenshot-card"><img src="{esc(home_shot["src"].removeprefix("mila/"))}" alt="{esc(home_shot["alt"]["he"])}" width="{home_shot["width"]}" height="{home_shot["height"]}" loading="lazy"><div class="screenshot-caption" data-i18n="screenCap2">{esc(home_shot["alt"]["he"])}</div></div>
            <div class="screenshot-card"><img src="{esc(words_shot["src"].removeprefix("mila/"))}" alt="{esc(words_shot["alt"]["he"])}" width="{words_shot["width"]}" height="{words_shot["height"]}" loading="lazy"><div class="screenshot-caption" data-i18n="screenCap3">{esc(words_shot["alt"]["he"])}</div></div>
          </div>
        </div>
      </div>
    </section>

    <section class="wrap band" id="curriculum" aria-labelledby="h-curr">
      <h2 id="h-curr" data-i18n="curriculumTitle">התאמה לכיתות א׳–ו׳ ורשימות משרד החינוך</h2>
      <p class="section-sub" data-i18n="curriculumDesc">באפליקציה 1,270 מילים בארבע רמות. מכיתה ג׳ מתרגלים גם מילים לפי רשימות משרד החינוך Pre-Band I ו-Band I. מילה אינה קשורה למשרד החינוך.</p>
      <div class="grade-item"><div class="grade-badge" data-i18n="grade12Badge">כיתות א׳–ב׳</div><div class="grade-desc"><h3 data-i18n="grade12Title">אנגלית בעל פה וללא קריאה</h3><p data-i18n="grade12Desc">צלילים, אותיות ה-ABC והאזנה למילים ראשונות עם תמונות ברורות (בכיתות א׳–ב׳ אין רשימת מילים רשמית של משרד החינוך).</p></div></div>
      <div class="grade-item"><div class="grade-badge" data-i18n="grade3Badge">כיתה ג׳</div><div class="grade-desc"><h3 data-i18n="grade3Title">אותיות, צלילים ומילים ראשונות</h3><p data-i18n="grade3Desc">היכרות עם אותיות באנגלית, צלילים, אותיות ניקוד ומילים ראשונות (Pre-Band I).</p></div></div>
      <div class="grade-item"><div class="grade-badge" data-i18n="grade4Badge">כיתה ד׳</div><div class="grade-desc"><h3 data-i18n="grade4Title">אוצר מילים וסיפורים קצרים</h3><p data-i18n="grade4Desc">מילים מרשימת Pre-Band I וסיפורים קצרים להבנת הנקרא, עם הקראה ותרגום לעברית.</p></div></div>
      <div class="grade-item"><div class="grade-badge" data-i18n="grade56Badge">כיתות ה׳–ו׳</div><div class="grade-desc"><h3 data-i18n="grade56Title">אוצר מילים והבנת הנקרא</h3><p data-i18n="grade56Desc">מילים מרשימת Band I, השלמת משפטים, סיפורים קצרים (54 סיפורים בסך הכל) ואתגר האלופים.</p></div></div>
    </section>

    <section class="wrap band" id="family" aria-labelledby="h-family">
      <h2 id="h-family" data-i18n="pillarsTitle">רכישה חד-פעמית ופרטיות ללא פשרות</h2>
      <p class="section-sub" data-i18n="pillarsSub">במילה אין פרסומות, אין מנוי חודשי ואין כלי מעקב או אנליטיקה.</p>
      <div class="grid-3">
        <div class="card"><h3 data-i18n="pil1Title">בלי פרסומות</h3><p data-i18n="pil1Desc">אפס פרסומות קופצות, אפס סרטוני שיווק ואפס קידום משחקים אחרים.</p></div>
        <div class="card"><h3 data-i18n="pil2Title">רכישה חד-פעמית (₪49.90)</h3><p data-i18n="pil2Desc">מתחילים בחינם (20 מילים בכל קבוצה, לוח ABC ודוגמאות סיפור). הגרסה המלאה נפתחת בתשלום חד-פעמי מאחורי שער הורים.</p></div>
        <div class="card"><h3 data-i18n="pil3Title">פרטיות מלאה במכשיר</h3><p data-i18n="pil3Desc">נתוני התרגול נשמרים במכשיר ועשויים להיכלל בגיבוי iCloud או Android. הרכישה נבדקת מול החנות ללא שליחת מידע לשרתים שלנו.</p></div>
      </div>
      <p style="margin-top:16px;"><a href="privacy/" data-i18n="privacyLink">לקריאת מדיניות הפרטיות המלאה של מילה ←</a></p>
    </section>

    <section class="wrap band" id="printables" aria-labelledby="h-print">
      <h2 id="h-print" data-i18n="printTitle">כרטיסיות ודפי עבודה להדפסה בבית</h2>
      <p class="section-sub" data-i18n="printSub">בחרו את השכבה המדויקת — דף העבודה ומפתח התשובות נפתחים בהתאמה מלאה לשכבה שנבחרה.</p>
      <div class="grid-2">
{chr(10).join(ws_cards)}
      </div>
    </section>

    <section class="wrap band" id="faq" aria-labelledby="h-faq">
      <h2 id="h-faq" data-i18n="faqTitle">שאלות נפוצות</h2>
      <div class="faq-item"><div class="faq-q" data-i18n="faq1Q">{esc(translations["he"]["faq1Q"])}</div><div class="faq-a" data-i18n="faq1A">{esc(translations["he"]["faq1A"])}</div></div>
      <div class="faq-item"><div class="faq-q" data-i18n="faq2Q">{esc(translations["he"]["faq2Q"])}</div><div class="faq-a" data-i18n="faq2A">{esc(translations["he"]["faq2A"])}</div></div>
      <div class="faq-item"><div class="faq-q" data-i18n="faq3Q">{esc(translations["he"]["faq3Q"])}</div><div class="faq-a" data-i18n="faq3A">{esc(translations["he"]["faq3A"])}</div></div>
      <div class="faq-item"><div class="faq-q" data-i18n="faq4Q">{esc(translations["he"]["faq4Q"])}</div><div class="faq-a"><span data-i18n="faq4Pre">{esc(translations["he"]["faq4Pre"])}</span> <a href="mailto:aviisr@aviisrgames.com">aviisr@aviisrgames.com</a> <span data-i18n="faq4Mid">{esc(translations["he"]["faq4Mid"])}</span> <a href="support/" data-i18n="faq4Support">{esc(translations["he"]["faq4Support"])}</a>.</div></div>
    </section>
  </main>

  <footer>
    <div class="wrap foot">
      <img src="/assets/logo/wordmark-dark.svg" alt="aviisr games" width="128" height="36">
      <div><a href="support/" data-i18n="navSupport">תמיכה במילה</a> · <a href="privacy/" data-i18n="navPrivacy">פרטיות</a> · <a href="worksheets/" data-i18n="navWorksheets">דפי עבודה להדפסה</a> · <a href="mailto:aviisr@aviisrgames.com">aviisr@aviisrgames.com</a></div>
    </div>
    <div class="wrap">
      <p data-i18n="footerCopy">{esc(translations["he"]["footerCopy"])}</p>
      <p class="non-affil" data-i18n="footerNonAffil">{esc(translations["he"]["footerNonAffil"])}</p>
    </div>
  </footer>

<script src="assets/lang.js"></script>
<script>
  var MILA_TITLES = {{
    he: "מילה - אנגלית לילדים (כיתות א׳–ו׳) | תרגול מותאם אישית בבית",
    en: "Mila — English for Hebrew-Speaking Kids (Grades 1–6)"
  }};
  AviisrI18n.init({{
    supported: ['he', 'en'],
    defaultLang: 'he',
    storageKey: 'aviisr_lang_mila',
    useBrowserLanguage: false,
    onLanguageChange: function (lang) {{
      document.title = MILA_TITLES[lang] || MILA_TITLES.he;
      var row = document.querySelector('.screenshots-row');
      if (row) row.setAttribute('aria-label', lang === 'en' ? 'App screenshots' : 'צילומי מסך מהאפליקציה');
      var badge = document.querySelector('img[data-play-badge]');
      if (badge) {{
        badge.setAttribute('src', lang === 'en' ? '/assets/badges/google-play-en.png' : '/assets/badges/google-play-iw.png');
        badge.alt = lang === 'en' ? 'Get it on Google Play: Mila' : 'השיגו ב-Google Play: מילה';
      }}
    }},
    translations: {json.dumps(translations, ensure_ascii=False, indent=6)}
  }});
</script>
</body>
</html>
'''


def render_baylight(reg):
    games = reg['games']
    by_id = {g['id']: g for g in games}
    b = by_id['baylight']
    siblings = [by_id['ninely'], by_id['paper-route']]
    shots = b['assets']['screenshots']
    imgs = []
    for idx, s in enumerate(shots):
        attr = 'fetchpriority="high"' if idx == 0 else 'loading="lazy"'
        imgs.append(
            f'<img src="/{esc(s["src"])}" width="{s["width"]}" height="{s["height"]}" '
            f'{attr} decoding="async" alt="{esc(s["alt"]["en"])}">'
        )
    more_items = []
    for sib in siblings:
        key = 'w_ninelyH' if sib['id'] == 'ninely' else 'w_mprH'
        more_items.append(
            f'      <li><a class="mini" data-world="{esc(sib["id"])}" href="/{esc(sib["hub"])}">'
            f'<img src="/{esc(sib["assets"]["icon"])}" alt="" width="{sib["assets"]["iconWidth"]}" height="{sib["assets"]["iconHeight"]}">'
            f'<span><b>{esc(sib["storeTitle"])}</b><span data-i18n="{key}">{esc(sib["copy"]["en"]["headline"])}</span></span></a></li>'
        )
    store_status = f'{b["copy"]["en"]["storeStatus"]} · Verified {b["verifiedOn"]}'
    return f'''<!doctype html>
<html lang="en">
<head>
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; font-src 'self'; img-src 'self' data: https://*.goatcounter.com; object-src 'none'; base-uri 'self';">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(b["storeTitle"])} · One-thumb sorting puzzle</title>
<link rel="canonical" href="https://aviisrgames.com/baylight/">
<meta name="description" content="Baylight: Truck Sort Puzzle. Tap a bay, stack three of a kind, ship the truck. Get it on Google Play, the App Store, or load a dock in your browser.">
<link rel="icon" href="../favicon.svg" type="image/svg+xml">
<meta property="og:title" content="{esc(b["storeTitle"])}">
<meta property="og:type" content="website">
<meta property="og:url" content="https://aviisrgames.com/baylight/">
<meta property="og:image" content="https://aviisrgames.com/assets/og/baylight.jpg">
<meta property="og:description" content="{esc(b["copy"]["en"]["lead"])}">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="../assets/site.css">
<link rel="stylesheet" href="../assets/hub.css">
<link rel="stylesheet" href="../assets/pilot-2.css">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "VideoGame",
  "name": "Baylight: Truck Sort Puzzle",
  "description": "Tap a bay, stack three of a kind, ship the truck. A one-thumb sorting puzzle in short rounds.",
  "url": "https://aviisrgames.com/baylight/",
  "genre": ["Puzzle", "Casual"],
  "gamePlatform": ["Android", "iOS"],
  "applicationCategory": "GameApplication",
  "operatingSystem": "Android, iOS",
  "inLanguage": ["en", "he", "ar"],
  "offers": {{ "@type": "Offer", "price": "0", "priceCurrency": "USD" }},
  "author": {{ "@type": "Organization", "name": "aviisr games", "email": "aviisr@aviisrgames.com" }}
}}
</script>
</head>
<body class="edition page-game">
<a class="skip-link" href="#main" data-i18n="w_skip">Skip to content</a>
<header>
<div class="col bar">
  <a class="logo" href="/" aria-label="aviisr games"><img src="/assets/logo/wordmark-light.svg" alt="" width="128" height="36"></a>
  <nav class="links" aria-label="Main"><a href="/" data-i18n="w_games">Games</a><a href="tips/">Baylight tips</a><a href="/support/" data-i18n="navSupport">Support</a></nav>
  <div class="langbox"><label for="lang-switcher" data-i18n="w_lang">Language</label><nav class="lang"></nav></div>
</div>
</header>
<main id="main">
<section class="mast" data-world="baylight" aria-labelledby="h-hub">
  <div class="col wrap">
    <div class="spread">
      <div class="copy">
        <span class="tag" data-i18n="w_tagBay">{esc(b["copy"]["en"]["tag"])}</span>
        <div class="id"><img src="/{esc(b["assets"]["icon"])}" alt="" width="{b["assets"]["iconWidth"]}" height="{b["assets"]["iconHeight"]}"><h1 id="h-hub">{esc(b["storeTitle"])}</h1></div>
        <p class="hl" data-i18n="w_bayH">{esc(b["copy"]["en"]["headline"])}</p>
        <p class="lead" data-i18n="baylightDesc">{esc(b["copy"]["en"]["lead"])}</p>
        <p class="note">{esc(store_status)}</p>
        <div class="acts">
          <a class="play-badge" href="{esc(b["hubPlayLink"])}"><img data-play-badge data-app="Baylight" src="/assets/badges/google-play-en.png" alt="Get it on Google Play: Baylight" width="150" height="58"></a>
          <a class="appstore-badge" href="{esc(b["appStore"]["url"])}" target="_blank" rel="noopener noreferrer" aria-label="Download Baylight on the App Store">{appstore_svg(18)}<bdi>App Store</bdi></a>
          <a class="link" href="dock/">{esc(b["copy"]["en"]["ctaBrowser"])}</a>
        </div>
      </div>
      <div class="shots">
        <div class="screens" role="region" aria-label="Baylight screenshots" tabindex="0">{''.join(imgs)}</div>
      </div>
    </div>
  </div>
</section>

<div class="col hubbody">
  <ul class="benefits"><li>No timers, no lives, no pressure: a calm puzzle you play with one thumb.</li><li>Every color has its own pattern, so the game is fully playable with colorblindness.</li><li>Plays offline with no account or sign-in, across 100 short levels.</li></ul>
  <ul class="hublinks"><li><a href="dock/">Load a dock in your browser</a></li><li><a href="tips/">Baylight tips</a></li></ul>
  <div class="qr-handoff"><img src="/assets/qr/baylight.svg" alt="QR code that opens this page on your phone" width="112" height="112"><p data-i18n="qrText">On a computer? Point your phone camera at the code to open this page on your phone, then tap Google Play or App Store.</p></div>

  <section class="more" aria-labelledby="h-more">
    <h2 id="h-more" data-i18n="w_more">More from aviisr games</h2>
    <ul class="minis">
{chr(10).join(more_items)}
    </ul>
  </section>

  <section class="help" aria-labelledby="h-help">
    <h2 id="h-help" data-i18n="navSupport">Support</h2>
    <h2>Help and contact</h2>
    <p>Email <a href="mailto:aviisr@aviisrgames.com?subject=Baylight%20support">aviisr@aviisrgames.com</a>. Tell us your device model, your operating system version and what happened. We reply by email.</p>
    <h2>Common questions</h2>
    <p><b>A bay jammed.</b> Nothing is lost. Undo is free twice at first, then once after ads start, or restart the level.</p>
    <p><b>Ads.</b> After Bay 5: a small banner at the top, an occasional full-screen ad after Next, and optional videos for bonuses. No Ads in the shop removes ads.</p>
    <p><b>I want to stop the usage data.</b> Turn off <b>Settings &gt; Share usage data</b>.</p>
    <p><b>I want my data deleted.</b> Delete the game to remove everything on your device. For data held by Unity, email us and we will help.</p>
    <h2>Privacy</h2>
    <p>Read the <a href="privacy.html">Privacy Policy</a>.</p>
  </section>
  <section class="about" aria-labelledby="h-about">
    <h2 id="h-about">What makes Baylight different</h2>
    <p>Many sorting puzzles reward speed or punish a single mistake. Baylight was designed to feel like tidying a loading dock at the end of a shift: slow, satisfying and forgiving. There are no timers and no lives, so you can stop mid-level, think, and come back without losing anything.</p>
    <p>The rule is simple. Parcels arrive one after another, you tap a bay to place the next one, and three matching parcels fill a truck that drives away. The challenge comes from limited space. Every parcel you place changes what the next few moves can do, so the game rewards looking ahead rather than reacting.</p>
    <p>A few habits make levels easier. Look at the queue of upcoming parcels before you tap, and decide where each of the next two or three will go. Keep one bay for the color you see most. Use the pallet to park a parcel only when it buys you a better move, since it is a limited resource and a bay that jams is harder to recover than one you left open.</p>
    <p>Accessibility shaped the design from the start. Each color carries its own pattern, so players with color blindness can tell parcels apart by shape alone, and nothing in a level depends on reaction speed. Rounds are short, and the game works offline, which makes it a good fit for a commute or a waiting room.</p>
    <p>If you want a taste first, the <a href="dock/">browser dock</a> lets you load a puzzle without installing anything. For strategy, read <a href="tips/">Baylight tips: how to clear a dock</a>.</p>
  </section>
</div>

<footer>
  <div class="col">
    <img class="foot-brand" src="/assets/logo/wordmark-dark.svg" alt="aviisr games" width="128" height="36">
    <div>© aviisr games · <a href="/support/" data-i18n="navSupport">Support</a> · <a href="privacy.html" data-i18n="navPrivacy">Privacy Policy</a> · <a href="/" data-i18n="navAllGames">All Games</a></div>
  </div>
</footer>
</main>
<script src="../assets/i18n.js"></script>
<script>
  AviisrI18n.init({{
    supported: ['en'],
    defaultLang: 'en',
    translations: {{
      en: {{ w_skip: "Skip to content", w_games: "Games", w_lang: "Language", w_tagBay: "Sorting puzzle", w_bayH: "Stack three. Ship the truck.", w_ninelyH: "Sudoku that explains every move.", w_mprH: "Deliver before sunrise.", w_more: "More from aviisr games" }}
    }}
  }});
</script>
<script src="/assets/play-badge.js"></script>
<script src="/assets/count.js" defer></script>
<script src="../assets/site.js" defer></script>
</body>
</html>
'''


def render_paper_route(reg):
    games = reg['games']
    by_id = {g['id']: g for g in games}
    p = by_id['paper-route']
    siblings = [by_id['ninely'], by_id['baylight']]
    shots = p['assets']['screenshots']
    imgs = []
    for idx, s in enumerate(shots):
        attr = 'fetchpriority="high"' if idx == 0 else 'loading="lazy"'
        imgs.append(
            f'<img src="/{esc(s["src"])}" width="{s["width"]}" height="{s["height"]}" '
            f'{attr} decoding="async" alt="{esc(s["alt"]["en"])}">'
        )
    more_items = []
    for sib in siblings:
        key = 'w_ninelyH' if sib['id'] == 'ninely' else 'w_bayH'
        more_items.append(
            f'      <li><a class="mini" data-world="{esc(sib["id"])}" href="/{esc(sib["hub"])}">'
            f'<img src="/{esc(sib["assets"]["icon"])}" alt="" width="{sib["assets"]["iconWidth"]}" height="{sib["assets"]["iconHeight"]}">'
            f'<span><b>{esc(sib["storeTitle"])}</b><span data-i18n="{key}">{esc(sib["copy"]["en"]["headline"])}</span></span></a></li>'
        )
    translations = {
        'en': {
            'w_skip': 'Skip to content',
            'w_games': 'Games',
            'navSupport': 'Support',
            'w_lang': 'Language',
            'w_tagMpr': p['copy']['en']['tag'],
            'w_mprH': p['copy']['en']['headline'],
            'mprDesc': p['copy']['en']['lead'],
            'w_storeStatus': f'{p["copy"]["en"]["storeStatus"]} · Not on iPhone yet · Verified {p["verifiedOn"]}',
            'iphoneSoon': 'Not on iPhone yet',
            'w_ninelyH': siblings[0]['copy']['en']['headline'],
            'w_bayH': siblings[1]['copy']['en']['headline'],
            'w_more': 'More from aviisr games',
            'navPrivacy': 'Privacy Policy',
            'navAllGames': 'All Games',
        },
        'he': {
            'w_skip': 'דלגו לתוכן',
            'w_games': 'משחקים',
            'navSupport': 'תמיכה',
            'w_lang': 'שפה',
            'w_tagMpr': p['copy']['he']['tag'],
            'w_mprH': p['copy']['he']['headline'],
            'mprDesc': p['copy']['he']['lead'],
            'w_storeStatus': f'{p["copy"]["he"]["storeStatus"]} · עדיין לא ב-iPhone · אומת {p["verifiedOn"]}',
            'iphoneSoon': 'עדיין לא ב-iPhone',
            'w_ninelyH': siblings[0]['copy']['he']['headline'],
            'w_bayH': siblings[1]['copy']['he']['headline'],
            'w_more': 'עוד מ-aviisr games',
            'navPrivacy': 'מדיניות פרטיות',
            'navAllGames': 'כל המשחקים',
        },
        'ar': {
            'w_skip': 'تخطَّ إلى المحتوى',
            'w_games': 'الألعاب',
            'navSupport': 'الدعم',
            'w_lang': 'اللغة',
            'w_tagMpr': p['copy']['ar']['tag'],
            'w_mprH': p['copy']['ar']['headline'],
            'mprDesc': p['copy']['ar']['lead'],
            'w_storeStatus': f'{p["copy"]["ar"]["storeStatus"]} · ليست على iPhone بعد · {p["verifiedOn"]}',
            'iphoneSoon': 'ليست على iPhone بعد',
            'w_ninelyH': siblings[0]['copy']['ar']['headline'],
            'w_bayH': siblings[1]['copy']['ar']['headline'],
            'w_more': 'المزيد من aviisr games',
            'navPrivacy': 'سياسة الخصوصية',
            'navAllGames': 'جميع الألعاب',
        },
    }
    return f'''<!doctype html>
<html lang="en">
<head>
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; font-src 'self'; img-src 'self' data: https://*.goatcounter.com; object-src 'none'; base-uri 'self';">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(p["storeTitle"])} · One-thumb arcade</title>
<meta name="description" content="Ride your morning route, throw the paper and deliver before sunrise. A one-thumb bike arcade game on Google Play.">
<link rel="canonical" href="https://aviisrgames.com/paper-route/">
<link rel="icon" href="../favicon.svg" type="image/svg+xml">
<meta property="og:title" content="{esc(p["storeTitle"])}">
<meta property="og:type" content="website">
<meta property="og:url" content="https://aviisrgames.com/paper-route/">
<meta property="og:image" content="https://aviisrgames.com/assets/og/paper-route.jpg">
<meta property="og:description" content="{esc(p["copy"]["en"]["headline"])}">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="../assets/site.css">
<link rel="stylesheet" href="../assets/hub.css">
<link rel="stylesheet" href="../assets/pilot-2.css">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "VideoGame",
  "name": "Morning Paper Route: Bike Game",
  "description": "Ride your morning route, throw the paper and deliver before sunrise. A one-thumb bike arcade game on Google Play.",
  "url": "https://aviisrgames.com/paper-route/",
  "genre": ["Arcade", "Action"],
  "gamePlatform": ["Android"],
  "applicationCategory": "GameApplication",
  "operatingSystem": "Android",
  "inLanguage": ["en", "he", "ar", "tr", "de", "fr", "es", "ja", "ko", "pt-BR", "ru"],
  "offers": {{ "@type": "Offer", "price": "0", "priceCurrency": "USD" }},
  "author": {{ "@type": "Organization", "name": "aviisr games", "email": "aviisr@aviisrgames.com" }}
}}
</script>
</head>
<body class="edition page-game">
<a class="skip-link" href="#main" data-i18n="w_skip">Skip to content</a>
<header>
<div class="col bar">
  <a class="logo" href="/" aria-label="aviisr games"><img src="/assets/logo/wordmark-light.svg" alt="" width="128" height="36"></a>
  <nav class="links" aria-label="Main"><a href="/" data-i18n="w_games">Games</a><a href="/support/" data-i18n="navSupport">Support</a></nav>
  <div class="langbox"><label for="lang-switcher" data-i18n="w_lang">Language</label><nav class="lang"></nav></div>
</div>
</header>
<main id="main">
<section class="mast" data-world="paper-route" aria-labelledby="h-hub">
  <div class="col wrap">
    <div class="spread">
      <div class="copy">
        <span class="tag" data-i18n="w_tagMpr">{esc(p["copy"]["en"]["tag"])}</span>
        <div class="id"><img src="/{esc(p["assets"]["icon"])}" alt="" width="{p["assets"]["iconWidth"]}" height="{p["assets"]["iconHeight"]}"><h1 id="h-hub">{esc(p["storeTitle"])}</h1></div>
        <p class="hl" data-i18n="w_mprH">{esc(p["copy"]["en"]["headline"])}</p>
        <p class="lead" data-i18n="mprDesc">{esc(p["copy"]["en"]["lead"])}</p>
        <p class="note" data-i18n="w_storeStatus">{esc(translations["en"]["w_storeStatus"])}</p>
        <div class="acts">
          <a class="play-badge" href="{esc(p["hubPlayLink"])}"><img data-play-badge data-app="Morning Paper Route" src="/assets/badges/google-play-en.png" alt="Get it on Google Play: Morning Paper Route" width="150" height="58"></a>
          <p class="ios-note" data-i18n="iphoneSoon">Not on iPhone yet</p>
        </div>
      </div>
      <div class="shots">
        <div class="screens" role="region" aria-label="Morning Paper Route screenshots" tabindex="0">{''.join(imgs)}</div>
      </div>
    </div>
  </div>
</section>

<div class="col hubbody">
  <div data-lang="en" lang="en" dir="ltr" class="about">
    <h2>About the Game</h2>
    <p>Steer with one thumb, throw with the other, and land the morning paper in every subscriber's mailbox.</p>
    <ul class="benefits">
      <li>7 days that get faster and busier: chasing dogs, cars backing out, drones, skaters</li>
      <li>Mailbox or porch, combos, wheelie throws, close calls, window bonuses and a bonus run at the end of each day</li>
      <li>3 stars per day, personal bests, daily missions, and a week that loops at a higher speed</li>
      <li>Cosmetics earned with in-game coins only</li>
      <li>Throw-path preview, one-handed and left-handed controls, haptics, Reduced Motion, 11 languages</li>
    </ul>
  </div>
  <div data-lang="he" lang="he" dir="rtl" class="about">
    <h2>על המשחק</h2>
    <p>כוונו באגודל אחד, זרקו עם השני, והנחיתו את עיתון הבוקר בתיבת הדואר של כל מנוי.</p>
    <ul class="benefits">
      <li>7 ימים שהולכים והופכים מהירים ועמוסים יותר: כלבים רודפים, מכוניות שיוצאות ברוורס, רחפנים, גולשי סקייטבורד</li>
      <li>תיבת דואר או מרפסת, קומבואים, זריקות בזמן רכיבה על גלגל אחד, חמיקות בקושי, בונוסי חלונות וסבב בונוס בסוף כל יום</li>
      <li>3 כוכבים בכל יום, שיאים אישיים, משימות יומיות, ושבוע שחוזר על עצמו במהירות גבוהה יותר</li>
      <li>פריטי עיצוב שמרוויחים במטבעות המשחק בלבד</li>
      <li>תצוגה מקדימה של מסלול הזריקה, שליטה ביד אחת ומצב לשמאליים, רטט, הפחתת תנועה, 11 שפות</li>
    </ul>
  </div>
  <div data-lang="ar" lang="ar" dir="rtl" class="about">
    <h2>عن اللعبة</h2>
    <p>وجّه الدراجة بإبهام واحد، وارمِ الصحيفة بالآخر، واجعلها تهبط في صندوق بريد كل مشترك.</p>
    <ul class="benefits">
      <li>7 أيام تزداد سرعةً وازدحامًا: كلاب تطارد، وسيارات تخرج إلى الخلف، وطائرات مسيّرة، ومتزلجون</li>
      <li>صندوق بريد أو شرفة، وسلاسل متتالية، ورميات أثناء رفع العجلة، ونجاة بشق الأنفس، ومكافآت النوافذ، وجولة مكافأة في نهاية كل يوم</li>
      <li>3 نجوم في كل يوم، وأفضل نتائجك الشخصية، ومهام يومية، وأسبوع يتكرر بسرعة أعلى</li>
      <li>عناصر تجميلية تُكسب بعملات اللعبة فقط</li>
      <li>معاينة مسار الرمي، وتحكم بيد واحدة ووضع لمستخدمي اليد اليسرى، واهتزاز لمسي، وتقليل الحركة، و11 لغة</li>
    </ul>
  </div>
  <ul class="hublinks"><li><a href="privacy/" data-i18n="navPrivacy">Privacy Policy</a></li></ul>
  <div class="qr-handoff"><img src="/assets/qr/paper-route.svg" alt="QR code that opens this page on your phone" width="112" height="112"><p data-i18n="qrText">On a computer? Point your phone camera at the code to open this page on your phone, then tap the Google Play button.</p></div>

  <section class="more" aria-labelledby="h-more">
    <h2 id="h-more" data-i18n="w_more">More from aviisr games</h2>
    <ul class="minis">
{chr(10).join(more_items)}
    </ul>
  </section>

  <section class="help" aria-labelledby="h-help">
    <h2 id="h-help" data-i18n="navSupport">Support</h2>
    <div data-lang="en" lang="en" dir="ltr">
      <h2>Questions</h2>
      <p><strong>Are there ads?</strong> Optional video ads can revive you, refill your papers or double your coins, and a short ad can play between days, never during a ride.</p>
      <p><strong>How do I remove ads?</strong> Buy "Remove ads" once in Settings or the Cosmetics shop. It turns off the ad between days. The optional reward videos (revive, extra papers, double coins) stay available whenever you want them.</p>
      <p><strong>I reinstalled or changed phones.</strong> Open Settings and tap "Restore purchases" (signed in to the same Google Play or App Store account).</p>
      <p><strong>How do I turn off personalized ads?</strong> Settings &gt; Ad privacy choices &gt; Non-personalized ads. On iPhone you can also turn off tracking in the system Settings.</p>
      <p><strong>Does the game need the internet?</strong> No, you can play offline. Ads and purchases need a connection.</p>
      <p><strong>I saw an inappropriate ad.</strong> Use "Report an ad" in Settings, or email us.</p>
      <h2>Support and Contact</h2>
      <p>Found a problem or have an idea? Use "Send feedback" in Settings, or write to us:</p>
      <p class="mail"><a href="mailto:aviisr@aviisrgames.com">aviisr@aviisrgames.com</a></p>
      <p><a href="privacy/">Read our Privacy Policy →</a></p>
    </div>
    <div data-lang="he" lang="he" dir="rtl">
      <h2>שאלות</h2>
      <p><strong>יש פרסומות?</strong> פרסומות וידאו אופציונליות יכולות להחיות אתכם, למלא את מלאי העיתונים או להכפיל את המטבעות, ופרסומת קצרה עשויה להופיע בין הימים, אף פעם לא באמצע רכיבה.</p>
      <p><strong>איך מסירים פרסומות?</strong> קנו פעם אחת "הסרת פרסומות" בהגדרות או בחנות פריטי העיצוב. זה מבטל את הפרסומת שבין הימים. סרטוני התגמול האופציונליים (החייאה, עיתונים נוספים, הכפלת מטבעות) נשארים זמינים בכל עת שתרצו.</p>
      <p><strong>התקנתי מחדש או החלפתי טלפון.</strong> פתחו את ההגדרות והקישו על "שחזור רכישות" (מחוברים לאותו חשבון <bdi>Google Play</bdi> או <bdi>App Store</bdi>).</p>
      <p><strong>איך מכבים פרסומות מותאמות אישית?</strong> הגדרות &gt; בחירות פרטיות לפרסומות &gt; פרסומות לא מותאמות אישית. ב<bdi>iPhone</bdi> אפשר גם לכבות מעקב בהגדרות המערכת.</p>
      <p><strong>האם המשחק צריך אינטרנט?</strong> לא, אפשר לשחק ללא חיבור. פרסומות ורכישות דורשות חיבור.</p>
      <p><strong>ראיתי פרסומת לא הולמת.</strong> השתמשו ב"דיווח על פרסומת" בהגדרות, או כתבו לנו בדוא"ל.</p>
      <h2>תמיכה ויצירת קשר</h2>
      <p>מצאתם בעיה או יש לכם רעיון? השתמשו ב"שליחת משוב" בהגדרות, או כתבו לנו:</p>
      <p class="mail"><a href="mailto:aviisr@aviisrgames.com">aviisr@aviisrgames.com</a></p>
      <p><a href="privacy/">לקריאת מדיניות הפרטיות שלנו ←</a></p>
    </div>
    <div data-lang="ar" lang="ar" dir="rtl">
      <h2>أسئلة</h2>
      <p><strong>هل توجد إعلانات؟</strong> يمكن لإعلانات الفيديو الاختيارية أن تعيدك إلى اللعب، أو تملأ مخزون الصحف، أو تضاعف عملاتك. وقد يظهر إعلان قصير بين الأيام، ولا يظهر أبدًا أثناء الجولة.</p>
      <p><strong>كيف أزيل الإعلانات؟</strong> اشترِ "إزالة الإعلانات" مرة واحدة من الإعدادات أو من متجر العناصر التجميلية. يوقف ذلك الإعلان بين الأيام. تبقى إعلانات المكافآت الاختيارية (الإحياء، وصحف إضافية، ومضاعفة العملات) متاحة متى شئت.</p>
      <p><strong>أعدت التثبيت أو غيّرت الهاتف.</strong> افتح الإعدادات واضغط "استعادة المشتريات" (مع تسجيل الدخول إلى حساب <bdi>Google Play</bdi> أو <bdi>App Store</bdi> نفسه).</p>
      <p><strong>كيف أوقف الإعلانات المخصصة؟</strong> الإعدادات &gt; خيارات خصوصية الإعلانات &gt; إعلانات غير مخصصة. على <bdi>iPhone</bdi> يمكنك أيضًا إيقاف التتبع من إعدادات النظام.</p>
      <p><strong>هل تحتاج اللعبة إلى الإنترنت؟</strong> لا، يمكنك اللعب دون اتصال. الإعلانات والمشتريات تحتاج إلى اتصال.</p>
      <p><strong>رأيت إعلانًا غير لائق.</strong> استخدم "الإبلاغ عن إعلان" في الإعدادات، أو راسلنا بالبريد.</p>
      <h2>الدعم والتواصل</h2>
      <p>وجدت مشكلة أو لديك فكرة؟ استخدم "إرسال ملاحظات" في الإعدادات، أو راسلنا:</p>
      <p class="mail"><a href="mailto:aviisr@aviisrgames.com">aviisr@aviisrgames.com</a></p>
      <p><a href="privacy/">اقرأ سياسة الخصوصية ←</a></p>
    </div>
  </section>
</div>

<footer>
  <div class="col">
    <img class="foot-brand" src="/assets/logo/wordmark-dark.svg" alt="aviisr games" width="128" height="36">
    <div>© aviisr games · <a href="/support/" data-i18n="navSupport">Support</a> · <a href="privacy/" data-i18n="navPrivacy">Privacy Policy</a> · <a href="/" data-i18n="navAllGames">All Games</a></div>
  </div>
</footer>
</main>
<script src="../assets/i18n.js"></script>
<script>
  AviisrI18n.init({{
    supported: ['en', 'he', 'ar'],
    defaultLang: 'en',
    translations: {json.dumps(translations, ensure_ascii=False, indent=6)}
  }});
</script>
<script src="/assets/play-badge.js"></script>
<script src="/assets/count.js" defer></script>
<script src="../assets/site.js" defer></script>
</body>
</html>
'''


def render_me2030_en(reg):
    games = reg['games']
    by_id = {g['id']: g for g in games}
    me = by_id['middle-east-2030']
    siblings = [by_id['ninely'], by_id['baylight']]
    shots = me['assets']['screenshots']
    imgs = []
    for idx, s in enumerate(shots):
        attr = 'fetchpriority="high"' if idx == 0 else 'loading="lazy"'
        imgs.append(
            f'<img src="/{esc(s["src"])}" width="{s["width"]}" height="{s["height"]}" '
            f'{attr} decoding="async" alt="{esc(s["alt"]["en"])}">'
        )
    more_items = []
    for sib in siblings:
        more_items.append(
            f'      <li><a class="mini" data-world="{esc(sib["id"])}" href="/{esc(sib["hub"])}">'
            f'<img src="/{esc(sib["assets"]["icon"])}" alt="" width="{sib["assets"]["iconWidth"]}" height="{sib["assets"]["iconHeight"]}">'
            f'<span><b>{esc(sib["storeTitle"])}</b><span>{esc(sib["copy"]["en"]["headline"])}</span></span></a></li>'
        )
    return f'''<!doctype html>
<html lang="en">
<head>
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https://*.goatcounter.com; object-src 'none'; base-uri 'self';">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(me["storeTitle"])}</title>
<meta name="description" content="Middle East 2030 is a geopolitical strategy game and political simulator for Android and iPhone. A work of fiction. Lead a nation and see tomorrow's front page.">
<link rel="canonical" href="https://aviisrgames.com/middle-east-2030/">
<link rel="alternate" hreflang="en" href="https://aviisrgames.com/middle-east-2030/">
<link rel="alternate" hreflang="he" href="https://aviisrgames.com/middle-east-2030/he/">
<link rel="alternate" hreflang="x-default" href="https://aviisrgames.com/middle-east-2030/">
<link rel="icon" href="../favicon.svg" type="image/svg+xml">
<meta property="og:title" content="{esc(me["storeTitle"])}">
<meta property="og:type" content="website">
<meta property="og:url" content="https://aviisrgames.com/middle-east-2030/">
<meta property="og:image" content="https://aviisrgames.com/assets/og/middle-east-2030.jpg">
<meta property="og:description" content="Govern one month at a time and read tomorrow's front page on your term.">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="../assets/site.css">
<link rel="stylesheet" href="../assets/hub.css">
<link rel="stylesheet" href="../assets/pilot-2.css">
<link rel="stylesheet" href="../assets/hub-me2030.css">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "VideoGame",
  "name": "Middle East 2030: Politics Sim",
  "description": "Deep political strategy simulation set in 2030. Choose from 8 regional capitals and read tomorrow's morning front page.",
  "url": "https://aviisrgames.com/middle-east-2030/",
  "genre": ["Strategy", "Simulation"],
  "gamePlatform": ["Android", "iOS"],
  "applicationCategory": "GameApplication",
  "operatingSystem": "Android, iOS",
  "inLanguage": ["en", "he", "ar", "tr", "de", "fr", "es", "ja", "ko", "pt-BR", "ru", "nl", "it", "zh-TW"],
  "offers": {{ "@type": "Offer", "price": "0", "priceCurrency": "USD" }},
  "author": {{ "@type": "Organization", "name": "aviisr games", "email": "aviisr@aviisrgames.com" }},
  "sameAs": [
    "https://play.google.com/store/apps/details?id={esc(me["googlePlay"]["package"])}",
    "{esc(me["appStore"]["url"])}"
  ]
}}
</script>
</head>
<body class="edition page-game">
<a class="skip-link" href="#main">Skip to content</a>
<header>
<div class="col bar">
  <a class="logo" href="/" aria-label="aviisr games"><img src="/assets/logo/wordmark-light.svg" alt="" width="128" height="36"></a>
  <nav class="links" aria-label="Main"><a href="/">Games</a><a href="guide/">Strategy guide</a><a href="/support/">Support</a></nav>
  <nav class="langbox" aria-label="Language"><a id="he" href="he/" hreflang="he" lang="he">עברית</a></nav>
</div>
</header>
<main id="main">
<section class="mast me" data-world="middle-east-2030" aria-labelledby="h-hub">
  <div class="col">
    <div class="plate">
      <h1 id="h-hub">{esc(me["storeTitle"])}</h1>
      <p class="dateline"><span>Morning edition</span><span>An invented 2030</span><span>aviisr games</span></p>
    </div>
    <p class="fiction" role="note">A political strategy game for Android and iPhone. A work of fiction set in an invented 2030: no event, headline or leader in it is real.</p>
    <div class="wrap">
      <div class="copy">
        <p class="hl">{esc(me["copy"]["en"]["headline"])}</p>
        <p class="lead">Pick one of eight capitals, take the chair, and govern one month at a time through a term of six to eight months. Each month one decision is enough (a second is optional), then one tap prints the morning paper and tomorrow's front page shows what your choices did.</p>
        <p class="lead">New players get a short guided first term that ends at their first paper, and every finished term builds a career: Rising Leader, Negotiator, Strategist, Veteran, Statesman.</p>
        <p class="note">Google Play (IL, US) &amp; App Store - Verified {esc(me["verifiedOn"])}</p>
        <div class="acts">
          <a class="btn" href="briefing/">Play the 3-month briefing</a>
          <a class="play-badge" href="{esc(me["hubPlayLink"])}"><img data-play-badge data-app="Middle East 2030" src="/assets/badges/google-play-en.png" alt="Get it on Google Play: Middle East 2030" width="150" height="58"></a>
          <a class="appstore-badge" href="{esc(me["appStore"]["url"])}" target="_blank" rel="noopener noreferrer" aria-label="Download Middle East 2030 on the App Store">{appstore_svg(18)}<bdi>App Store</bdi></a>
        </div>
        <p class="guide"><a class="link" href="guide/">Coalition Strategy &amp; Chair Guide</a></p>
      </div>
      <div class="shots">
        <div class="screens" role="region" aria-label="Middle East 2030 screenshots" tabindex="0">{''.join(imgs)}</div>
      </div>
    </div>
    <div class="cols">
      <div><span class="k">Each month</span><h2>One decision is enough</h2><p>A second is optional. Then one tap prints the morning paper.</p></div>
      <div><span class="k">The morning after</span><h2>Read what you did</h2><p>Tomorrow's front page shows what your choices did.</p></div>
      <div><span class="k">Term after term</span><h2>Build a career</h2><p>Rising Leader, Negotiator, Strategist, Veteran, Statesman.</p></div>
    </div>
  </div>
</section>

<div class="col hubbody">
  <ul class="hublinks"><li><a href="guide/">Scenario Timeline &amp; Chair Guide</a></li><li><a href="support/">Support &amp; Help</a></li><li><a href="privacy/">Privacy Policy</a></li></ul>
  <div class="qr-handoff"><img src="/assets/qr/middle-east-2030.svg" alt="QR code that opens this page on your phone" width="112" height="112"><p>On a computer? Point your phone camera at the code to open this page on your phone, then tap Google Play or App Store.</p></div>

  <section class="more" aria-labelledby="h-more">
    <h2 id="h-more">More from aviisr games</h2>
    <ul class="minis">
{chr(10).join(more_items)}
    </ul>
  </section>
  <section class="about" lang="en" dir="ltr" aria-labelledby="h-about">
    <h2 id="h-about">About the game and how to play it well</h2>
    <p>Middle East 2030 is a work of fiction. It takes place in an invented 2030, and every event, headline and leader in it is made up for the game. It is a strategy simulation meant to be read and thought about, and its tone fits an Everyone 10+ rating: the consequences are shown through newspaper headlines and numbers, not through graphic scenes.</p>
    <p>We chose a morning newspaper as the main screen because it makes cause and effect easy to see. You act in the evening, and the next front page tells you what happened. That loop teaches the central lesson of the game: a choice that helps one group can cost you trust with another, and the bill often arrives a month later.</p>
    <p>Each term is short, six to eight months, so you can finish one in a sitting and try a different approach straight away. The eight capitals start with different pressures, which is why the same decision can work well in one chair and badly in another.</p>
    <p>To do well, avoid chasing a single measure. Check every gauge before you commit, notice which problem is growing fastest and deal with it early, and keep the optional second decision for the month when you can afford it. Losing a term is useful, because the paper explains why. The <a href="briefing/">3-month briefing</a> runs in your browser, and the <a href="guide/">chair guide</a> describes each starting position.</p>
  </section>
</div>

<footer>
  <div class="col">
    <img class="foot-brand" src="/assets/logo/wordmark-dark.svg" alt="aviisr games" width="128" height="36">
    <div>© aviisr games · <a href="support/">Support</a> · <a href="privacy/">Privacy Policy</a> · <a href="/">All Games</a></div>
  </div>
</footer>
</main>
<script src="/assets/play-badge.js"></script>
<script src="/assets/count.js" defer></script>
<script src="../assets/site.js" defer></script>
</body>
</html>
'''


def render_me2030_he(reg):
    games = reg['games']
    by_id = {g['id']: g for g in games}
    me = by_id['middle-east-2030']
    siblings = [by_id['ninely'], by_id['baylight']]
    shots = me['assets']['screenshots']
    imgs = []
    for idx, s in enumerate(shots):
        attr = 'fetchpriority="high"' if idx == 0 else 'loading="lazy"'
        imgs.append(
            f'<img src="/{esc(s["src"])}" width="{s["width"]}" height="{s["height"]}" '
            f'{attr} decoding="async" alt="{esc(s["alt"]["he"])}">'
        )
    more_items = []
    for sib in siblings:
        more_items.append(
            f'      <li><a class="mini" data-world="{esc(sib["id"])}" href="/{esc(sib["hub"])}">'
            f'<img src="/{esc(sib["assets"]["icon"])}" alt="" width="{sib["assets"]["iconWidth"]}" height="{sib["assets"]["iconHeight"]}">'
            f'<span><b><bdi>{esc(sib["storeTitle"])}</bdi></b><span>{esc(sib["copy"]["he"]["headline"])}</span></span></a></li>'
        )
    return f'''<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https://*.goatcounter.com; object-src 'none'; base-uri 'self';">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>המזרח התיכון 2030: משחק פוליטי</title>
<meta name="description" content="משחק אסטרטגיה וסימולציה פוליטית ל-Android ול-iPhone. יצירת בדיון המתרחשת בשנת 2030 מומצאת. בחרו אחת משמונה בירות, החליטו חודש אחר חודש וקראו את עיתון הבוקר.">
<link rel="canonical" href="https://aviisrgames.com/middle-east-2030/he/">
<link rel="alternate" hreflang="en" href="https://aviisrgames.com/middle-east-2030/">
<link rel="alternate" hreflang="he" href="https://aviisrgames.com/middle-east-2030/he/">
<link rel="alternate" hreflang="x-default" href="https://aviisrgames.com/middle-east-2030/">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<meta property="og:title" content="המזרח התיכון 2030: משחק פוליטי">
<meta property="og:type" content="website">
<meta property="og:locale" content="he_IL">
<meta property="og:url" content="https://aviisrgames.com/middle-east-2030/he/">
<meta property="og:image" content="https://aviisrgames.com/assets/og/middle-east-2030.jpg">
<meta property="og:description" content="הובילו את המדינה חודש אחר חודש, והכותרת של מחר מראה את ההשפעה של ההחלטות שלכם.">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="/assets/site.css">
<link rel="stylesheet" href="/assets/hub.css">
<link rel="stylesheet" href="/assets/pilot-2.css">
<link rel="stylesheet" href="/assets/hub-me2030.css">
</head>
<body class="edition page-game">
<a class="skip-link" href="#main">דלגו לתוכן</a>
<header>
<div class="col bar">
  <a class="logo" href="/" aria-label="aviisr games"><img src="/assets/logo/wordmark-light.svg" alt="" width="128" height="36"></a>
  <nav class="links" aria-label="ראשי"><a href="/">משחקים</a><a href="/middle-east-2030/guide/">מדריך אסטרטגיה</a><a href="/support/">תמיכה</a></nav>
  <nav class="langbox" aria-label="שפה"><a href="/middle-east-2030/" hreflang="en" lang="en" dir="ltr">English</a></nav>
</div>
</header>
<main id="main">
<section class="mast me" data-world="middle-east-2030" aria-labelledby="h-hub">
  <div class="col">
    <div class="plate">
      <h1 id="h-hub">המזרח התיכון 2030: משחק פוליטי</h1>
      <p class="dateline"><span>מהדורת הבוקר</span><span>2030 מומצאת</span><span><bdi>aviisr games</bdi></span></p>
    </div>
    <p class="fiction" role="note">משחק אסטרטגיה וסימולציה פוליטית ל-<bdi>Android</bdi> ול-<bdi>iPhone</bdi>. יצירת בדיון המתרחשת בשנת 2030 מומצאת. שום אירוע, כותרת או מנהיג במשחק אינם אמיתיים.</p>
    <div class="wrap">
      <div class="copy">
        <p class="hl">{esc(me["copy"]["he"]["headline"])}</p>
        <p class="lead">בחרו אחת משמונה בירות, שבו בכיסא המנהיג והובילו את המדינה חודש אחר חודש לאורך קדנציה מלאה. בכל חודש מספיקה החלטה אחת (השנייה רשות), ואז הקשה אחת מדפיסה את עיתון הבוקר, והכותרת של מחר מראה את ההשפעה של ההחלטות שלכם.</p>
        <p class="lead">שחקנים חדשים מקבלים קדנציה ראשונה מודרכת וקצרה שמסתיימת בעיתון הראשון, וכל קדנציה שמסתיימת בונה קריירה: כוכב עולה, מגשר, אסטרטג, ותיק, מדינאי.</p>
        <p class="note"><bdi>Google Play</bdi> ו-<bdi>App Store</bdi> - אומת {esc(me["verifiedOn"])}</p>
        <div class="acts">
          <a class="btn" href="/middle-east-2030/briefing/">שחקו בתדרוך המשברים</a>
          <a class="play-badge" href="{esc(me["hubPlayLink"])}"><img data-play-badge data-app="Middle East 2030" src="/assets/badges/google-play-iw.png" alt="Get it on Google Play: Middle East 2030" width="150" height="58"></a>
          <a class="appstore-badge" href="{esc(me["appStore"]["url"])}" target="_blank" rel="noopener noreferrer" aria-label="הורדה ב-App Store">{appstore_svg(18)}<bdi>App Store</bdi></a>
        </div>
        <p class="guide"><a class="link" href="/middle-east-2030/guide/">מדריך אסטרטגיה וכיסאות (<bdi>EN</bdi>)</a></p>
      </div>
      <div class="shots">
        <div class="screens" role="region" aria-label="צילומי מסך מהמשחק" tabindex="0">{''.join(imgs)}</div>
      </div>
    </div>
    <div class="cols">
      <div><span class="k">בכל חודש</span><h2>החלטה אחת מספיקה</h2><p>השנייה רשות. ואז הקשה אחת מדפיסה את עיתון הבוקר.</p></div>
      <div><span class="k">בבוקר שאחרי</span><h2>קראו מה עשיתם</h2><p>הכותרת של מחר מראה את ההשפעה של ההחלטות שלכם.</p></div>
      <div><span class="k">קדנציה אחר קדנציה</span><h2>בנו קריירה</h2><p>כוכב עולה, מגשר, אסטרטג, ותיק, מדינאי.</p></div>
    </div>
  </div>
</section>

<div class="col hubbody">
  <ul class="hublinks"><li><a href="/middle-east-2030/guide/">מדריך אסטרטגיה</a></li><li><a href="/middle-east-2030/support/#he">תמיכה ושירות</a></li><li><a href="/middle-east-2030/privacy/">מדיניות פרטיות</a></li></ul>
  <div class="qr-handoff"><img src="/assets/qr/middle-east-2030.svg" alt="קוד QR שפותח את דף המשחק בטלפון" width="112" height="112"><p>במחשב? כוונו את מצלמת הטלפון לקוד כדי לפתוח את הדף הזה בטלפון, ואז הקישו על <bdi>Google Play</bdi> או על <bdi>App Store</bdi>.</p></div>

  <section class="more" aria-labelledby="h-more">
    <h2 id="h-more">עוד מ-<bdi>aviisr games</bdi></h2>
    <ul class="minis">
{chr(10).join(more_items)}
    </ul>
  </section>
</div>

<footer>
  <div class="col">
    <img class="foot-brand" src="/assets/logo/wordmark-dark.svg" alt="aviisr games" width="128" height="36">
    <div>© <bdi>aviisr games</bdi> · <a href="/middle-east-2030/support/#he">תמיכה</a> · <a href="/middle-east-2030/privacy/">מדיניות פרטיות</a> · <a href="/">כל המשחקים</a></div>
  </div>
</footer>
</main>
<script src="/assets/play-badge.js"></script>
<script src="/assets/count.js" defer></script>
<script src="/assets/site.js" defer></script>
</body>
</html>
'''


def studio_header_and_footer(has_lang=False):
    lang_nav = '<div class="langbox"><label for="lang-switcher" data-i18n="w_lang">Language</label><nav class="lang"></nav></div>' if has_lang else ''
    header = f'''<a class="skip-link" href="#main" data-i18n="w_skip">Skip to content</a>
<header>
<div class="col bar">
  <a class="logo" href="../" aria-label="aviisr games"><img src="/assets/logo/wordmark-light.svg" alt="" width="128" height="36"></a>
  <nav class="links" aria-label="Main"><a href="../" data-i18n="w_games">Games</a><a href="../ninely/strategy/" data-i18n="w_guides">Guides</a><a href="../notes/" data-i18n="w_notes">Notes</a><a href="../about/" data-i18n="w_about">About</a><a href="../support/" data-i18n="navSupport">Support</a></nav>
  {lang_nav}
</div>
</header>'''
    footer = '''<footer>
  <div class="col">
    <img class="foot-brand" src="/assets/logo/wordmark-dark.svg" alt="aviisr games" width="128" height="36">
    <div>© aviisr games · <a href="../" data-i18n="w_games">Games</a> · <a href="../about/" data-i18n="w_about">About</a> · <a href="../notes/" data-i18n="w_notes">Notes</a> · <a href="../support/" data-i18n="navSupport">Support</a> · <a href="../privacy/" data-i18n="navPrivacy">Privacy Policy</a> · <a href="/terms/">Terms</a> · <a href="/accessibility/">Accessibility</a> · <a href="mailto:aviisr@aviisrgames.com">aviisr@aviisrgames.com</a></div>
  </div>
</footer>'''
    return header, footer


def render_about(reg):
    header, footer = studio_header_and_footer(has_lang=True)
    translations = {
        'en': {
            'w_skip': 'Skip to content', 'w_games': 'Games', 'w_guides': 'Guides', 'w_notes': 'Notes',
            'w_about': 'About', 'navSupport': 'Support', 'navPrivacy': 'Privacy Policy', 'w_lang': 'Language',
            'h1': 'About aviisr games',
            'sub': 'An independent studio making small mobile games, and writing about how they work.',
            'whoH': 'Who we are',
            'who1': 'aviisr games is a one-person studio run by Avi Israeli. We publish all five titles on Google Play (IL, US), with Middle East 2030, Baylight (IL, US) and Mila (on the App Store in Israel) also available on the App Store: Ninely (a sudoku game that explains every move), Middle East 2030 (a political strategy simulation set in an invented 2030), Baylight (a one-thumb truck-sorting puzzle), Morning Paper Route (a bike arcade game) and Mila (an English-learning app for children in Hebrew-speaking families).',
            'who2': 'The games are small on purpose. Each one tries to do one thing well, to start fast and to respect the player\'s time and privacy. This website follows the same rule: static pages, no accounts, no sign-up forms, and an aggregate visit counter that excludes children\'s and policy pages.',
            'whatH': 'What you will find here',
            'what1': 'Game pages: each public title has its own hub with verified store links, real screenshots and, where available, a browser version you can try without installing anything.',
            'what2': 'Sudoku guides: twelve step-by-step guides to human-logic solving techniques, from naked singles to Swordfish and Y-Wing, with solver-checked example boards.',
            'what3': 'Strategy guide: a companion dossier for Middle East 2030 covering the eight playable capitals, monthly choices and briefing outcomes.',
            'what4': 'Devlog notes: short notes on how we generate puzzles, verify browser solvers and design game rules.',
            'what5': 'Printable worksheets: free Hebrew and English flashcards and practice sheets for Mila learners, with matched answer keys.',
            'adsH': 'Advertising and privacy',
            'adsP': 'Our mobile games on Google Play (and Middle East 2030 and Baylight on the App Store) are free and may show ads or offer optional purchases, as described in each game\'s privacy policy; Mila is available on Google Play and the App Store in Israel with no ads and a one-time unlock. On this website, only the 12 Sudoku strategy guide pages and the Middle East 2030 strategy guide load advertising via Google AdSense (when permitted by consent and Global Privacy Control). Game hubs, browser playables, notes, About, support pages, privacy pages and every Mila page are ad-free.',
            'contactH': 'Contact',
            'contactP': 'Questions, bug reports, corrections to a guide, or business enquiries are all welcome. Tell us the page or app, your device and what happened. We reply by email.',
        },
        'he': {
            'w_skip': 'דלגו לתוכן', 'w_games': 'משחקים', 'w_guides': 'מדריכים', 'w_notes': 'רשימות',
            'w_about': 'אודות', 'navSupport': 'תמיכה', 'navPrivacy': 'מדיניות פרטיות', 'w_lang': 'שפה',
            'h1': 'אודות aviisr games',
            'sub': 'סטודיו עצמאי שיוצר משחקי מובייל קטנים וכותב בשקיפות על אופן הפיתוח שלהם.',
            'whoH': 'מי אנחנו',
            'who1': 'aviisr games הוא סטודיו עצמאי של אבי ישראלי. חמשת הכותרים הפומביים שלנו זמינים ב-Google Play (ישראל וארה״ב), כאשר Middle East 2030, Baylight (ישראל וארה״ב) ומילה (ב-App Store בישראל) זמינות גם ב-App Store: Ninely (סודוקו שמסביר כל צעד), Middle East 2030 (סימולציית אסטרטגיה בדיונית), Baylight (פאזל מיון משלוחים), Morning Paper Route (ארקייד אופניים) ומילה (לימוד אנגלית לילדים דוברי עברית).',
            'who2': 'המשחקים קצרים וממוקדים בכוונה. גם האתר בנוי באותה גישה: דפים סטטיים, בלי חשבונות משתמש, בלי טפסי הרשמה ועם מונה כללי שמחריג לחלוטין דפי ילדים, תמיכה ופרטיות.',
            'whatH': 'מה תמצאו באתר',
            'what1': 'דפי משחקים: דף ייעודי לכל כותר עם קישורי חנויות מאומתים, צילומי מסך אמיתיים וגרסאות דפדפן להתנסות מיידית.',
            'what2': 'מדריכי סודוקו: תריסר מדריכים לשיטות פתרון מבוססות היגיון, עם לוחות דוגמה שנבדקו בתוכנה לפתרון יחיד.',
            'what3': 'מדריך אסטרטגיה: מדריך נלווה ל-Middle East 2030 הכולל את שמונה הבירות ו-8 תוצאות התדריך.',
            'what4': 'רשימות פיתוח (Notes): הסברים טכניים על מחולל הסודוקו היומי, בודק הפתרונות של Baylight ותכנון המשחקים.',
            'what5': 'דפי עבודה להדפסה: כרטיסיות ודפי תרגול בעברית ובאנגלית לתלמידי מילה, עם מפתחות תשובות תואמים.',
            'adsH': 'פרסום ופרטיות',
            'adsP': 'המשחקים החינמיים בחנויות עשויים להציג פרסומות או הצעות רכישה כמפורט במדיניות הפרטיות של כל משחק; מילה זמינה ב-Google Play וב-App Store בישראל ללא פרסומות ובמודל רכישה חד-פעמית. באתר עצמו, פרסומות Google AdSense נטענות אך ורק ב-12 מדריכי הסודוקו ובמדריך האסטרטגיה של Middle East 2030 (בכפוף להסכמה ול-Global Privacy Control). דפי הבית, המשחקים, התמיכה, הפרטיות, אודות וכל דפי מילה נקיים מפרסומות.',
            'contactH': 'יצירת קשר',
            'contactP': 'שאלות, דיווחים על תקלות, הערות למדריכים או פניות עסקיות יתקבלו בברכה. ציינו את האפליקציה או העמוד ואת דגם המכשיר ונחזור אליכם בדוא״ל.',
        },
        'ar': {
            'w_skip': 'تخطَّ إلى المحتوى', 'w_games': 'الألعاب', 'w_guides': 'الأدلة', 'w_notes': 'الملاحظات',
            'w_about': 'عن الاستوديو', 'navSupport': 'الدعم', 'navPrivacy': 'سياسة الخصوصية', 'w_lang': 'اللغة',
            'h1': 'عن aviisr games',
            'sub': 'استوديو مستقل يصنع ألعاب هاتف صغيرة ويشرح آلية عملها بوضوح.',
            'whoH': 'من نحن',
            'who1': 'aviisr games استوديو مستقل يديره آفي إسرائيلي. تتوفر عناويننا الخمسة على Google Play، كما تتوفر Middle East 2030 وBaylight (عالمياً وإسرائيل والولايات المتحدة) وميلا (في إسرائيل) على App Store أيضاً: Ninely وMiddle East 2030 وBaylight وMorning Paper Route وميلا.',
            'who2': 'صُممت الألعاب لتكون خفيفة وسريعة وتحترم وقت اللاعب وخصوصيته. وهذا الموقع يتبع المبدأ نفسه: صفحات ثابتة بلا حسابات وبلا تتبع شخصي.',
            'whatH': 'ماذا ستجد هنا',
            'what1': 'صفحات الألعاب: صفحة لكل عنوان مع روابط متاجر موثقة ولقطات حقيقية وتجارب متصفح.',
            'what2': 'أدلة السودوكو: 12 دليلاً لتقنيات الحل المنطقي بأمثلة متحقق منها برمجياً.',
            'what3': 'دليل الاستراتيجية لـ Middle East 2030 وتفاصيل العواصم الثماني.',
            'what4': 'ملاحظات التطوير حول توليد الألغاز وبرامج التحقق.',
            'what5': 'أوراق عمل قابلة للطباعة لتطبيق ميلا مع مفاتيح الحل.',
            'adsH': 'الإعلانات والخصوصية',
            'adsP': 'على هذا الموقع، تظهر إعلانات Google AdSense فقط على صفحات أدلة السودوكو الـ12 ودليل Middle East 2030 (وفق إعدادات الخصوصية والموافقة). أما صفحات الألعاب والدعم والخصوصية وعن الاستوديو وجميع صفحات ميلا فهي خالية من الإعلانات تماماً.',
            'contactH': 'التواصل',
            'contactP': 'نرحب بأسئلتكم وتقارير الأخطاء واقتراحات التحسين عبر البريد الإلكتروني.',
        },
    }
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>About aviisr games · Small mobile games, made with care</title>
<meta name="description" content="Who makes aviisr games, verified store availability across Google Play and the App Store, and advertising and privacy practices.">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; object-src 'none'; base-uri 'self';">
<link rel="canonical" href="https://aviisrgames.com/about/">
<link rel="icon" href="../favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="../assets/site.css">
<link rel="stylesheet" href="../assets/pilot-2.css">
</head>
<body class="edition page-studio">
{header}
<main id="main" class="col studio" style="max-width:920px;padding-block:32px 48px">
  <h1 data-i18n="h1" style="font-size:clamp(2rem,4.5vw,3.1rem)">About aviisr games</h1>
  <p class="lead" data-i18n="sub" style="margin-bottom:24px">An independent studio making small mobile games, and writing about how they work.</p>

  <section class="card">
    <h2 data-i18n="whoH">Who we are</h2>
    <p data-i18n="who1">{esc(translations["en"]["who1"])}</p>
    <p data-i18n="who2">{esc(translations["en"]["who2"])}</p>
  </section>

  <section class="card">
    <h2 data-i18n="whatH">What you will find here</h2>
    <ul>
      <li data-i18n="what1">{esc(translations["en"]["what1"])}</li>
      <li data-i18n="what2">{esc(translations["en"]["what2"])}</li>
      <li data-i18n="what3">{esc(translations["en"]["what3"])}</li>
      <li data-i18n="what4">{esc(translations["en"]["what4"])}</li>
      <li data-i18n="what5">{esc(translations["en"]["what5"])}</li>
    </ul>
    <p style="margin-top:12px"><a href="../ninely/strategy/">Sudoku guides</a> · <a href="../middle-east-2030/guide/">Middle East 2030 guide</a> · <a href="../notes/">Studio notes</a></p>
  </section>

  <section class="card">
    <h2 data-i18n="adsH">Advertising and privacy</h2>
    <p data-i18n="adsP">{esc(translations["en"]["adsP"])}</p>
    <p><a href="../privacy/" data-i18n="navPrivacy">Privacy Policy</a></p>
  </section>

  <section class="card">
    <h2 data-i18n="contactH">Contact</h2>
    <p class="mail"><a href="mailto:aviisr@aviisrgames.com">aviisr@aviisrgames.com</a></p>
    <p data-i18n="contactP">{esc(translations["en"]["contactP"])}</p>
    <p><a href="../support/" data-i18n="navSupport">Support</a></p>
  </section>
</main>
{footer}
<script src="../assets/i18n.js"></script>
<script>
  AviisrI18n.init({{
    supported: ['en', 'he', 'ar'],
    defaultLang: 'en',
    translations: {json.dumps(translations, ensure_ascii=False, indent=4)}
  }});
</script>
<script src="../assets/site.js" defer></script>
</body>
</html>
'''


def render_support(reg):
    header, footer = studio_header_and_footer(has_lang=True)
    translations = {
        'en': {
            'w_skip': 'Skip to content', 'w_games': 'Games', 'w_guides': 'Guides', 'w_notes': 'Notes',
            'w_about': 'About', 'navSupport': 'Support', 'navPrivacy': 'Privacy Policy', 'w_lang': 'Language',
            'h1': 'Support',
            'sub': 'Help for each of our apps, or write to the studio directly.',
            'pickH': 'Pick your app',
            'writeH': 'Write to us',
            'write1': 'Tell us the app, your device model, the operating system version and what happened. We reply by email.',
            'write2': 'Purchases are made through Google Play or the App Store. To restore an eligible purchase after reinstalling or switching devices, use Restore purchases inside the app Settings screen.',
        },
        'he': {
            'w_skip': 'דלגו לתוכן', 'w_games': 'משחקים', 'w_guides': 'מדריכים', 'w_notes': 'רשימות',
            'w_about': 'אודות', 'navSupport': 'תמיכה', 'navPrivacy': 'מדיניות פרטיות', 'w_lang': 'שפה',
            'h1': 'תמיכה ועזרה',
            'sub': 'בחרו את המשחק או האפליקציה לקבלת עזרה, או כתבו לנו ישירות.',
            'pickH': 'בחרו אפליקציה',
            'writeH': 'כתבו לנו',
            'write1': 'ציינו את שם האפליקציה, דגם המכשיר, גרסת מערכת ההפעלה ומה קרה. אנו עונים בדוא״ל.',
            'write2': 'רכישות מתבצעות דרך Google Play או App Store. לשחזור רכישה אחרי התקנה מחדש או החלפת מכשיר, השתמשו באפשרות שחזור רכישות (Restore purchases) במסך ההגדרות באפליקציה.',
        },
        'ar': {
            'w_skip': 'تخطَّ إلى المحتوى', 'w_games': 'الألعاب', 'w_guides': 'الأدلة', 'w_notes': 'الملاحظات',
            'w_about': 'عن الاستوديو', 'navSupport': 'الدعم', 'navPrivacy': 'سياسة الخصوصية', 'w_lang': 'اللغة',
            'h1': 'الدعم',
            'sub': 'المساعدة لكل تطبيق أو تواصل معنا مباشرة.',
            'pickH': 'اختر التطبيق',
            'writeH': 'راسلنا',
            'write1': 'اذكر اسم التطبيق وطراز الجهاز وإصدار النظام وما حدث وسنرد عبر البريد الإلكتروني.',
            'write2': 'تتم المشتريات عبر Google Play أو App Store. لاستعادة المشتريات بعد إعادة التثبيت، استخدم خيار استعادة المشتريات في إعدادات التطبيق.',
        },
    }
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Support · aviisr games</title>
<meta name="description" content="Help for aviisr games apps: Ninely, Middle East 2030, Morning Paper Route, Baylight and Mila.">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; object-src 'none'; base-uri 'self';">
<link rel="canonical" href="https://aviisrgames.com/support/">
<link rel="icon" href="../favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="../assets/site.css">
<link rel="stylesheet" href="../assets/pilot-2.css">
</head>
<body class="edition page-studio">
{header}
<main id="main" class="col studio" style="max-width:920px;padding-block:32px 48px">
  <h1 data-i18n="h1" style="font-size:clamp(2rem,4.5vw,3.1rem)">Support</h1>
  <p class="lead" data-i18n="sub" style="margin-bottom:24px">Help for each of our apps, or write to the studio directly.</p>

  <section class="card">
    <h2 data-i18n="pickH">Pick your app</h2>
    <ul>
      <li><a href="../ninely/">Ninely: Sudoku &amp; Logic Puzzle</a></li>
      <li><a href="../middle-east-2030/support/">Middle East 2030: Politics Sim</a></li>
      <li><a href="../paper-route/">Morning Paper Route: Bike Game</a></li>
      <li><a href="../baylight/">Baylight: Truck Sort Puzzle</a></li>
      <li><a href="../mila/support/" lang="he" dir="rtl">מילה · Mila (תמיכה בעברית)</a></li>
    </ul>
  </section>

  <section class="card">
    <h2 data-i18n="writeH">Write to us</h2>
    <p class="mail"><a href="mailto:aviisr@aviisrgames.com">aviisr@aviisrgames.com</a></p>
    <p data-i18n="write1">{esc(translations["en"]["write1"])}</p>
    <p data-i18n="write2">{esc(translations["en"]["write2"])}</p>
  </section>
</main>
{footer}
<script src="../assets/i18n.js"></script>
<script>
  AviisrI18n.init({{
    supported: ['en', 'he', 'ar'],
    defaultLang: 'en',
    translations: {json.dumps(translations, ensure_ascii=False, indent=4)}
  }});
</script>
<script src="../assets/site.js" defer></script>
</body>
</html>
'''


def render_privacy(reg):
    header, footer = studio_header_and_footer(has_lang=False)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Privacy · aviisr games</title>
<meta name="description" content="Privacy policies for each aviisr games app, and for this website, which has no accounts and no forms, and loads ads only on the 13 reviewed guide pages.">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; object-src 'none'; base-uri 'self';">
<link rel="canonical" href="https://aviisrgames.com/privacy/">
<link rel="icon" href="../favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="../assets/site.css">
<link rel="stylesheet" href="../assets/pilot-2.css">
</head>
<body class="edition page-studio">
{header}
<main id="main" class="col studio" style="max-width:920px;padding-block:32px 48px">
  <h1 style="font-size:clamp(2rem,4.5vw,3.1rem)">Privacy</h1>
  <p class="lead" style="margin-bottom:24px">Each app has its own privacy policy. This page also explains what this website collects.</p>

  <section class="card">
    <h2>App privacy policies</h2>
    <ul>
      <li><a href="../ninely/privacy.html">Ninely: Sudoku &amp; Logic Puzzle</a></li>
      <li><a href="../middle-east-2030/privacy/">Middle East 2030: Politics Sim</a></li>
      <li><a href="../paper-route/privacy/">Morning Paper Route: Bike Game</a></li>
      <li><a href="../baylight/privacy.html">Baylight: Truck Sort Puzzle</a></li>
      <li><a href="../beamwise/privacy.html">RayVane (formerly Beamwise)</a></li>
      <li><a href="../mila/privacy/" lang="he" dir="rtl">מילה · Mila (מדיניות פרטיות בעברית)</a></li>
    </ul>
  </section>

  <section class="card">
    <h2>This website</h2>
    <ul>
      <li><b>No accounts, no forms.</b> The site loads no third-party fonts or cross-site trackers. Apart from the advertising described below, which runs only on 13 specific guide pages, the website sets no cookies.</li>
      <li><b>Visit counting.</b> Selected studio, game and guide pages, including the Ninely Facebook-group redirect pages under /go/nfb-*, include an aggregate counter (GoatCounter) that adds up totals only. The group redirect pages count visits to each redirect path, not Facebook group joins. They send no cookies or personal identifiers to GoatCounter. After the redirect, Facebook processes the visit under its own privacy policy. The counter records page paths, referring origin, browser/OS family (from headers without saving raw headers), Google Play outbound clicks, home game-card clicks, QR/YouTube entry tags, first browser move/hint/completion events, language switcher picks, and contact email clicks. Nothing links events together or identifies visitors. It never loads on any Mila page, support page or privacy page, ignores visitors with Do Not Track or Global Privacy Control, and excludes Mila links on shared pages.</li>
      <li><b>Advertising on 13 reviewed guide pages.</b> Only the 12 Sudoku strategy guides (<code>/ninely/strategy/how-to-solve-sudoku/</code>, <code>glossary/</code>, and the 10 technique guides) and the Middle East 2030 strategy guide (<code>/middle-east-2030/guide/</code>) load Google AdSense and Google Funding Choices. Where loaded and permitted, Google and its partners may use cookies, beacons or IP addresses to serve and measure ads. See <a href="https://policies.google.com/technologies/partner-sites" rel="noopener">how Google uses partner-site data</a>, manage ad personalization at <a href="https://adssettings.google.com" rel="noopener">adssettings.google.com</a>, or opt out via <a href="https://www.aboutads.info" rel="noopener">aboutads.info</a>. Ads are never loaded on home, game hubs, playables, privacy or support pages, or any Mila page.</li>
      <li><b>Your choice in the EEA, the UK and Switzerland, and Global Privacy Control.</b> Visitors with Global Privacy Control enabled never load ad code. In consent-required regions, Google's TCF consent dialog asks before personalized/cookie-based ads load, and an on-page <b>Privacy settings</b> link lets you revisit or withdraw consent at any time.</li>
      <li><b>Language choice.</b> Your selected display language is stored locally in your browser (<code>localStorage</code>) and never leaves your device.</li>
      <li><b>Hosting.</b> Hosted on GitHub Pages, which keeps standard edge/server access logs under GitHub's privacy statement.</li>
    </ul>
    <p>Questions: <a href="mailto:aviisr@aviisrgames.com">aviisr@aviisrgames.com</a></p>
  </section>
<section class="card">
<h2 style="margin-top:0">Israeli Privacy Protection Law (Amendment 13)</h2>
<p>In accordance with Israel's Protection of Privacy Law, 5741-1981 (as amended by Amendment 13, effective August 14, 2025):</p>
<ul>
<li><b>Database controller &amp; contact:</b> aviisr games (Avi Israeli Rozin, Israel), <a href="mailto:aviisr@aviisrgames.com">aviisr@aviisrgames.com</a>.</li>
<li><b>Voluntary provision &amp; consequences:</b> You are not legally required to provide personal data to browse this site. All pages and browser games work without an account or forms. If you decline ad cookies or enable Do Not Track / Global Privacy Control, you can still use the entire site; optional features such as personalised ads on guide pages or email support replies require the relevant data.</li>
<li><b>Third-party recipients &amp; cross-border transfers:</b> Technical request data or advertising data on guide pages may be processed by our infrastructure and service providers — GitHub Pages (hosting), GoatCounter (cookieless aggregate visit totals), Google (AdSense on allowlisted guide pages and Gmail for support emails you send us) — including servers in the United States and the European Union.</li>
<li><b>Your statutory rights:</b> Under Section 13 (right to inspect personal data) and Section 14 (right to request correction or deletion of inaccurate, incomplete, unclear, or outdated personal data) of the Protection of Privacy Law, you may submit a request at any time to <a href="mailto:aviisr@aviisrgames.com">aviisr@aviisrgames.com</a>.</li>
</ul>
</section>
</main>
{footer}
</body>
</html>
'''


def render_notes(reg):
    header, footer = studio_header_and_footer(has_lang=False)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Notes from aviisr games · Devlogs and design notes</title>
<meta name="description" content="Devlogs and design notes from aviisr games: how our puzzles are made, checked and designed.">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; object-src 'none'; base-uri 'self';">
<link rel="canonical" href="https://aviisrgames.com/notes/">
<link rel="icon" href="../favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="../assets/site.css">
<link rel="stylesheet" href="../assets/pilot-2.css">
</head>
<body class="edition page-studio">
{header}
<main id="main" class="col studio" style="max-width:920px;padding-block:32px 48px">
  <h1 style="font-size:clamp(2rem,4.5vw,3.1rem)">Notes from aviisr games</h1>
  <p class="lead" style="margin-bottom:24px">Devlogs and design notes from a small studio.</p>

  <section class="card">
    <h2>About these notes</h2>
    <p>We make small mobile games, and we like to explain how they work. These notes cover real engineering and design decisions in more detail than a store listing allows.</p>
    <p>They are written in plain language about what our puzzle generators, browser solvers and game rules actually do. Spot an error or want a note on a topic? Write to <a href="mailto:aviisr@aviisrgames.com">aviisr@aviisrgames.com</a>.</p>
  </section>

  <section class="card">
    <h2>Notes</h2>
    <ul>
      <li><a href="./ninely-daily-puzzle/"><b>How the Ninely daily puzzle is made</b></a><br>How each day's Ninely puzzle is generated, verified for a unique solution, and graded by solver technique tier.</li>
      <li><a href="./baylight-dock-solver/"><b>Building a solver-checked puzzle for the browser</b></a><br>How the Baylight browser dock uses a BFS state solver to validate winnable docks and step hints.</li>
      <li><a href="./middle-east-2030-design/"><b>Designing Middle East 2030: one decision a month and a morning paper</b></a><br>Why the game is set in an invented 2030, its monthly decision loop, and the guided first term.</li>
    </ul>
  </section>

  <section class="card">
    <h2>More to read</h2>
    <p>Explore the <a href="../ninely/strategy/">Sudoku guides hub</a> and the <a href="../ninely/strategy/glossary/">Sudoku glossary</a>, or read the <a href="../middle-east-2030/guide/">Middle East 2030 strategy guide</a>.</p>
  </section>
</main>
{footer}
</body>
</html>
'''


TARGETS = [
    ('index.html', render_home),
    ('ninely/index.html', render_ninely),
    ('mila/index.html', render_mila),
    ('baylight/index.html', render_baylight),
    ('paper-route/index.html', render_paper_route),
    ('middle-east-2030/index.html', render_me2030_en),
    ('middle-east-2030/he/index.html', render_me2030_he),
    ('about/index.html', render_about),
    ('support/index.html', render_support),
    ('privacy/index.html', render_privacy),
    ('notes/index.html', render_notes),
]


def main():
    reg = load_registry()
    check_mode = '--check' in sys.argv
    stale = []
    for rel, fn in TARGETS:
        path = ROOT / rel
        rendered = fn(reg)
        if check_mode:
            current = path.read_text(encoding='utf-8') if path.exists() else ''
            if current != rendered:
                stale.append(rel)
        else:
            path.write_text(rendered, encoding='utf-8')
            print(f'Wrote {rel}')
    if check_mode:
        if stale:
            print('Stale generated files:', ', '.join(stale))
            print('Run: python3 tools/build_site.py')
            return 1
        print('All generated pilot pages are up to date.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
