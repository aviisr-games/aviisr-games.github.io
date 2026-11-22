#!/usr/bin/env python3
"""Generate static /go/<slug>/index.html pages from site/go_links.json.

Store links are hardcoded at build time (zero query-parameter open redirects),
strictly allowlisted to aviisr games store listings, and hard-isolated from Mila.
They count a cookieless event from the page itself.

Group links are the Ninely Facebook-group hops. Each one loads /assets/count.js
so GoatCounter records a page view of the /go/ path, then redirects to one of the
two allowlisted groups. They are not open redirects, and Mila is excluded.

Usage:
    python3 tools/build_go_links.py          # regenerate go/<slug>/index.html
    python3 tools/build_go_links.py --check  # exit 1 if generated files are stale
"""

from __future__ import annotations

import html
import json
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / 'site/go_links.json'
GO_DIR = ROOT / 'go'

SLUG_RE = re.compile(r'^[a-z0-9-]+$')
ALLOWED_TARGET_PREFIXES = (
    'https://play.google.com/store/apps/details?id=com.aviisr',
    'https://apps.apple.com/',
)
FORBIDDEN_TARGET_TOKENS = ('com.aviisr.mila', '6827490842')
ENDPOINT = 'https://aviisrgames.goatcounter.com/count'
GROUP_REDIRECT_SECONDS = 2
GROUP_COPY = {
    'en': {
        'name': 'Learn Sudoku Techniques',
        'target': 'https://www.facebook.com/groups/learnsudokutechniques',
        'title': 'Taking you to Learn Sudoku Techniques',
        'heading': 'Taking you to the Ninely sudoku group on Facebook',
        'body': (
            'Learn Sudoku Techniques is a public Facebook group run by the solo developer '
            'of Ninely at aviisr games. You do not need the app to take part.'
        ),
        'cta': 'Continue to the group',
    },
    'de': {
        'name': 'Sudoku-Techniken lernen',
        'target': 'https://www.facebook.com/groups/sudokutechnikenlernen',
        'title': 'Weiterleitung zu Sudoku-Techniken lernen',
        'heading': 'Weiterleitung zur Ninely-Sudoku-Gruppe auf Facebook',
        'body': (
            'Sudoku-Techniken lernen ist eine öffentliche Facebook-Gruppe, geleitet vom '
            'alleinigen Entwickler von Ninely bei aviisr games. Die App brauchen Sie nicht, um mitzumachen.'
        ),
        'cta': 'Weiter zur Gruppe',
    },
}


def validate_entry(entry: dict) -> tuple[str, str, str, str]:
    """Validate a single go-link entry and return (slug, app_name, store_name, target)."""
    if not isinstance(entry, dict):
        raise ValueError('Each go-link entry must be a JSON object')

    slug = entry.get('slug', '')
    app_name = entry.get('appName', '')
    store_name = entry.get('storeName', '')
    target = entry.get('target', '')

    if not isinstance(slug, str) or not SLUG_RE.fullmatch(slug):
        raise ValueError(f'Invalid slug {slug!r}: must match ^[a-z0-9-]+$')

    if 'mila' in slug.lower():
        raise ValueError(f'Forbidden Mila slug {slug!r}: Mila is isolated from /go/ redirects')

    if not isinstance(app_name, str) or not app_name.strip():
        raise ValueError(f'Slug {slug!r} requires a non-empty appName')

    if not isinstance(target, str) or not target:
        raise ValueError(f'Slug {slug!r} requires a non-empty target URL')

    if any(ch.isspace() or ch in '<>"\'' for ch in target):
        raise ValueError(f'Slug {slug!r} target contains unsafe characters: {target!r}')

    if not target.startswith(ALLOWED_TARGET_PREFIXES):
        raise ValueError(
            f'Slug {slug!r} target {target!r} is not allowlisted; must start with '
            f'{ALLOWED_TARGET_PREFIXES[0]!r} or {ALLOWED_TARGET_PREFIXES[1]!r}'
        )

    lowered_target = target.lower()
    for token in FORBIDDEN_TARGET_TOKENS:
        if token in lowered_target:
            raise ValueError(f'Slug {slug!r} target references forbidden Mila identifier {token!r}')

    if not store_name:
        store_name = 'Google Play' if target.startswith('https://play.google.com/') else 'App Store'

    return slug, app_name.strip(), store_name.strip(), target


def validate_links(data: dict) -> list[tuple[str, str, str, str]]:
    """Validate the full go_links.json structure."""
    if not isinstance(data, dict) or not isinstance(data.get('links'), list):
        raise ValueError('go_links.json must contain a "links" list')

    seen: set[str] = set()
    validated: list[tuple[str, str, str, str]] = []
    for entry in data['links']:
        item = validate_entry(entry)
        slug = item[0]
        if slug in seen:
            raise ValueError(f'Duplicate slug: {slug!r}')
        seen.add(slug)
        validated.append(item)
    return validated


def render_page(slug: str, app_name: str, store_name: str, target: str) -> str:
    """Render a static, cookieless redirect page with hardcoded target URL."""
    safe_app = html.escape(app_name, quote=True)
    safe_store = html.escape(store_name, quote=True)
    safe_href = html.escape(target, quote=True)
    js_target = json.dumps(target).replace('</', '<\\/')
    js_event = json.dumps(f'go/{slug}').replace('</', '<\\/')
    js_endpoint = json.dumps(ENDPOINT)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="robots" content="noindex, nofollow">
  <meta name="referrer" content="no-referrer">
  <title>Opening {safe_app} on {safe_store}…</title>
  <style>
    :root {{
      color-scheme: light dark;
      --bg: #f6f7f9;
      --card: #ffffff;
      --text: #14181f;
      --muted: #525d6d;
      --accent: #0f62fe;
      --accent-text: #ffffff;
      --border: #dce1e8;
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{
        --bg: #0f131a;
        --card: #171d27;
        --text: #f0f3f7;
        --muted: #a6b0bf;
        --accent: #4589ff;
        --accent-text: #0b1018;
        --border: #2a3342;
      }}
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      padding: 24px;
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}
    main {{
      width: 100%;
      max-width: 420px;
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 28px 24px;
      text-align: center;
    }}
    h1 {{
      margin: 0 0 10px;
      font-size: 1.2rem;
      line-height: 1.35;
    }}
    p {{
      margin: 0 0 20px;
      color: var(--muted);
      font-size: 0.95rem;
      line-height: 1.5;
    }}
    .cta {{
      display: inline-block;
      padding: 12px 20px;
      border-radius: 10px;
      background: var(--accent);
      color: var(--accent-text);
      text-decoration: none;
      font-weight: 600;
      font-size: 0.95rem;
    }}
    .brand {{
      margin-top: 18px;
      margin-bottom: 0;
      font-size: 0.8rem;
      color: var(--muted);
    }}
  </style>
</head>
<body>
  <main>
    <h1>Opening {safe_app} on {safe_store}…</h1>
    <p>You are being redirected to the official store listing.</p>
    <a class="cta" href="{safe_href}" rel="noopener noreferrer">Continue to {safe_store}</a>
    <noscript>
      <p style="margin-top: 16px;">JavaScript is disabled. <a href="{safe_href}" rel="noopener noreferrer">Open {safe_app} on {safe_store}</a>.</p>
    </noscript>
    <p class="brand">aviisr games</p>
  </main>
  <script>
    (function () {{
      'use strict';
      var TARGET = {js_target};
      var ENDPOINT = {js_endpoint};
      var dnt = navigator.doNotTrack === '1' || window.doNotTrack === '1' || navigator.globalPrivacyControl === true;
      if (!dnt) {{
        try {{
          var url = ENDPOINT + '?p=' + encodeURIComponent({js_event}) + '&e=true&rnd=' + Math.random().toString(36).slice(2);
          if (typeof navigator.sendBeacon === 'function') {{
            navigator.sendBeacon(url);
          }} else if (typeof fetch === 'function') {{
            fetch(url, {{ mode: 'no-cors', keepalive: true, credentials: 'omit', referrerPolicy: 'no-referrer' }}).catch(function () {{}});
          }}
        }} catch (e) {{ /* never block redirect */ }}
      }}
      setTimeout(function () {{
        window.location.replace(TARGET);
      }}, 300);
    }})();
  </script>
</body>
</html>
"""


def validate_groups(data: dict) -> list[tuple[str, str, str, str]]:
    """Validate Facebook-group hops. Returns (slug, lang, group_name, target)."""
    raw = data.get('groups', [])
    if raw is None:
        raw = []
    if not isinstance(raw, list):
        raise ValueError('go_links.json "groups" must be a list')

    store_slugs = {item[0] for item in validate_links(data)}
    seen: set[str] = set()
    validated: list[tuple[str, str, str, str]] = []
    for entry in raw:
        if not isinstance(entry, dict):
            raise ValueError('Each group entry must be a JSON object')
        slug = entry.get('slug', '')
        lang = entry.get('lang', '')
        if not isinstance(slug, str) or not SLUG_RE.fullmatch(slug):
            raise ValueError(f'Invalid group slug {slug!r}: must match ^[a-z0-9-]+$')
        if 'mila' in slug.lower():
            raise ValueError(f'Forbidden Mila slug {slug!r}: Mila is isolated from /go/ redirects')
        if lang not in GROUP_COPY:
            raise ValueError(f'Slug {slug!r} lang {lang!r} must be one of {sorted(GROUP_COPY)}')
        if not slug.startswith(f'nfb-{lang}-'):
            raise ValueError(f'Slug {slug!r} must start with nfb-{lang}-')
        if slug in seen or slug in store_slugs:
            raise ValueError(f'Duplicate slug: {slug!r}')
        seen.add(slug)
        copy = GROUP_COPY[lang]
        validated.append((slug, lang, copy['name'], copy['target']))
    return validated


def render_group_page(slug: str, lang: str) -> str:
    """A real HTML hop: count.js records the path, then a visible redirect to the group."""
    if lang not in GROUP_COPY:
        raise ValueError(f'Unknown group language {lang!r}')
    copy = GROUP_COPY[lang]
    target = copy['target']
    safe_href = html.escape(target, quote=True)
    js_target = json.dumps(target).replace('</', '<\\/')
    delay_ms = GROUP_REDIRECT_SECONDS * 1000
    text = {key: html.escape(copy[key], quote=True) for key in ('title', 'heading', 'body', 'cta')}

    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="robots" content="noindex, nofollow">
  <meta name="referrer" content="no-referrer">
  <meta http-equiv="refresh" content="{GROUP_REDIRECT_SECONDS}; url={safe_href}">
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https://*.goatcounter.com; object-src 'none'; base-uri 'self';">
  <title>{text['title']}</title>
  <style>
    :root {{
      color-scheme: light dark;
      --bg: #f6f7f9;
      --card: #ffffff;
      --text: #14181f;
      --muted: #525d6d;
      --accent: #0f62fe;
      --accent-text: #ffffff;
      --border: #dce1e8;
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{
        --bg: #0f131a;
        --card: #171d27;
        --text: #f0f3f7;
        --muted: #a6b0bf;
        --accent: #4589ff;
        --accent-text: #0b1018;
        --border: #2a3342;
      }}
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      padding: 24px;
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}
    main {{
      width: 100%;
      max-width: 420px;
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 28px 24px;
      text-align: center;
    }}
    h1 {{
      margin: 0 0 10px;
      font-size: 1.2rem;
      line-height: 1.35;
    }}
    p {{
      margin: 0 0 20px;
      color: var(--muted);
      font-size: 0.95rem;
      line-height: 1.5;
    }}
    .cta {{
      display: inline-block;
      padding: 12px 20px;
      border-radius: 10px;
      background: var(--accent);
      color: var(--accent-text);
      text-decoration: none;
      font-weight: 600;
      font-size: 0.95rem;
    }}
    .brand {{
      margin-top: 18px;
      margin-bottom: 0;
      font-size: 0.8rem;
      color: var(--muted);
    }}
  </style>
</head>
<body>
  <main>
    <h1>{text['heading']}</h1>
    <p>{text['body']}</p>
    <a class="cta" href="{safe_href}" rel="noopener noreferrer">{text['cta']}</a>
    <p class="brand">aviisr games</p>
  </main>
  <script src="/assets/count.js" defer></script>
  <script>
    setTimeout(function () {{
      window.location.replace({js_target});
    }}, {delay_ms});
  </script>
</body>
</html>
"""


def build_all(config_path: Path = CONFIG_PATH, go_dir: Path = GO_DIR, check: bool = False) -> int:
    data = json.loads(config_path.read_text(encoding='utf-8'))
    entries = validate_links(data)
    groups = validate_groups(data)
    expected_slugs = {slug for slug, _, _, _ in entries} | {slug for slug, _, _, _ in groups}

    if check:
        if not go_dir.is_dir():
            print('go/ directory is missing: run python3 tools/build_go_links.py')
            return 1
        actual_slugs = {p.name for p in go_dir.iterdir() if p.is_dir()}
        if actual_slugs != expected_slugs:
            print(f'go/ slugs out of sync: expected {sorted(expected_slugs)}, found {sorted(actual_slugs)}')
            return 1
        for slug, app_name, store_name, target in entries:
            page_path = go_dir / slug / 'index.html'
            expected_html = render_page(slug, app_name, store_name, target)
            if not page_path.is_file() or page_path.read_text(encoding='utf-8') != expected_html:
                print(f'go/{slug}/index.html is stale: run python3 tools/build_go_links.py')
                return 1
        for slug, lang, _, _ in groups:
            page_path = go_dir / slug / 'index.html'
            expected_html = render_group_page(slug, lang)
            if not page_path.is_file() or page_path.read_text(encoding='utf-8') != expected_html:
                print(f'go/{slug}/index.html is stale: run python3 tools/build_go_links.py')
                return 1
        print(f'go/ redirects are up to date ({len(entries)} store, {len(groups)} group)')
        return 0

    go_dir.mkdir(parents=True, exist_ok=True)
    for existing in list(go_dir.iterdir()):
        if existing.is_dir() and existing.name not in expected_slugs:
            shutil.rmtree(existing)

    for slug, app_name, store_name, target in entries:
        page_dir = go_dir / slug
        page_dir.mkdir(parents=True, exist_ok=True)
        (page_dir / 'index.html').write_text(
            render_page(slug, app_name, store_name, target),
            encoding='utf-8',
        )

    for slug, lang, _, _ in groups:
        page_dir = go_dir / slug
        page_dir.mkdir(parents=True, exist_ok=True)
        (page_dir / 'index.html').write_text(
            render_group_page(slug, lang),
            encoding='utf-8',
        )

    print(f'Generated {len(entries)} store and {len(groups)} group pages under go/')
    return 0


def main() -> int:
    check = '--check' in sys.argv
    return build_all(check=check)


if __name__ == '__main__':
    sys.exit(main())
