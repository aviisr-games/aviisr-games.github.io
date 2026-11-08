#!/usr/bin/env python3
"""Weekly check that every store link on allowlisted pages opens a live listing.

Scans the HTML of allowlisted apps and studio pages for Google Play and App Store
URLs and fetches each one. Exits 1 if any listing is not HTTP 200 (or, for the App
Store, if the iTunes lookup API does not return the app).

Usage: python3 tools/check_store_links.py [--offline]
  --offline  only list the URLs found (no network), for local runs.
"""

from pathlib import Path
import json
import re
import sys
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent.parent

# Studio pages plus allowlisted app folders. Non-allowlisted pages are not scanned.
ALLOWLIST_DIRS = ['ninely', 'middle-east-2030', 'redline-2030', 'paper-route', 'morning-route', 'baylight', 'mila']
STUDIO_PAGES = ['index.html']

PLAY_RE = re.compile(r'https://play\.google\.com/store/apps/details\?id=([\w.]+)')
APPLE_RE = re.compile(r'https://apps\.apple\.com/(?:[a-z]{2}/)?app/(?:[\w-]+/)?id(\d+)')
UA = 'Mozilla/5.0 (compatible; aviisrgames-link-check)'


def allowlisted_html():
    files = [ROOT / p for p in STUDIO_PAGES]
    for d in ALLOWLIST_DIRS:
        files.extend(sorted((ROOT / d).rglob('*.html')))
    return [f for f in files if f.exists()]


def collect():
    play, apple = {}, {}
    for f in allowlisted_html():
        text = f.read_text(encoding='utf-8')
        rel = str(f.relative_to(ROOT))
        for pkg in PLAY_RE.findall(text):
            play.setdefault(pkg, set()).add(rel)
        for app_id in APPLE_RE.findall(text):
            apple.setdefault(app_id, set()).add(rel)
    return play, apple


def http_status(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code
    except urllib.error.URLError:
        return 0


def apple_live(app_id):
    for country in ('us', 'il'):
        url = f'https://itunes.apple.com/lookup?id={app_id}&country={country}'
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=30) as r:
                if json.load(r).get('resultCount', 0) > 0:
                    return True
        except (urllib.error.URLError, ValueError):
            pass
    return False


def main():
    play, apple = collect()
    if '--offline' in sys.argv:
        for pkg, pages in sorted(play.items()):
            print(f'play  {pkg}: {", ".join(sorted(pages))}')
        for app_id, pages in sorted(apple.items()):
            print(f'apple {app_id}: {", ".join(sorted(pages))}')
        return 0

    failures = []
    for pkg, pages in sorted(play.items()):
        code = http_status(f'https://play.google.com/store/apps/details?id={pkg}&hl=en')
        print(f'play  {pkg}: HTTP {code}')
        if code != 200:
            failures.append(f'Google Play {pkg} returned {code} (linked from {", ".join(sorted(pages))})')
    for app_id, pages in sorted(apple.items()):
        live = apple_live(app_id)
        print(f'apple {app_id}: {"live" if live else "NOT FOUND"}')
        if not live:
            failures.append(f'App Store id{app_id} not found (linked from {", ".join(sorted(pages))})')

    if failures:
        print('\nBroken store links:')
        for f in failures:
            print(f'  - {f}')
        return 1
    print(f'\nAll {len(play) + len(apple)} store destinations are live.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
