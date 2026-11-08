#!/usr/bin/env python3
"""Weekly check that each app's store name matches what the website says.

The site promises one name per app (hub H1 = homepage card = store name). If a store
listing is renamed in Play Console, this check fails so the site can be updated with it.

Usage: python3 tools/check_store_listings.py            # site + live Google Play
       python3 tools/check_store_listings.py --offline  # site only (no network)
"""

from pathlib import Path
import html
import re
import sys
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
UA = 'Mozilla/5.0 (compatible; aviisrgames-listing-check)'

# package -> (store name the site uses, hub page)
APPS = {
    'com.aviisrgames.ninely': ('Ninely: Sudoku & Logic Puzzle', 'ninely/index.html'),
    'com.aviisrgames.middleeast2030': ('Middle East 2030: Politics Sim', 'middle-east-2030/index.html'),
    'com.aviisrgames.baylight': ('Baylight: Truck Sort Puzzle', 'baylight/index.html'),
    'com.aviisr.paperroute': ('Morning Paper Route: Bike Game', 'paper-route/index.html'),
}


def site_problems():
    problems = []
    home = html.unescape((ROOT / 'index.html').read_text(encoding='utf-8'))
    for pkg, (name, hub) in APPS.items():
        text = html.unescape((ROOT / hub).read_text(encoding='utf-8'))
        h1s = [re.sub(r'<[^>]+>', '', h).strip() for h in re.findall(r'<h1[^>]*>(.*?)</h1>', text, re.S)]
        if name not in h1s:
            problems.append(f'{hub}: H1 {h1s[:1]} is not the store name "{name}"')
        if f'<h3>{name}</h3>' not in home:
            problems.append(f'index.html: no app card titled "{name}"')
    return problems


def play_title(pkg):
    url = f'https://play.google.com/store/apps/details?id={pkg}&hl=en&gl=US'
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=30) as r:
            page = r.read().decode('utf-8', 'ignore')
    except urllib.error.URLError as e:
        return None, f'could not load ({e})'
    m = re.search(r'<title[^>]*>(.*?)</title>', page, re.S)
    if not m:
        return None, 'no <title> on the listing page'
    return html.unescape(m.group(1)).replace(' - Apps on Google Play', '').strip(), None


def main():
    problems = site_problems()
    if '--offline' not in sys.argv:
        for pkg, (name, _) in APPS.items():
            title, err = play_title(pkg)
            if err:
                problems.append(f'Google Play {pkg}: {err}')
            elif title != name:
                problems.append(f'Google Play {pkg} is now "{title}"; the site says "{name}"')
            else:
                print(f'play  {pkg}: "{title}" matches')
    if problems:
        print('\nStore name drift:')
        for p in problems:
            print(f'  - {p}')
        return 1
    print('\nSite and store names agree.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
