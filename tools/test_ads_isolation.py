"""AdSense isolation: ad code is only ever allowed on the explicit guide-page allowlist."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parent.parent
AD_PAGES = sorted(
    {f'ninely/strategy/{d.name}/index.html'
     for d in (ROOT / 'ninely/strategy').iterdir() if d.is_dir()}
    | {'middle-east-2030/guide/index.html'}
)
AD_MARKERS = ['adsbygoogle', 'googlesyndication', 'pagead', 'doubleclick', 'assets/ads.js']
ROOT_META = 'google-adsense-account'


def html_files():
    return [p for p in ROOT.rglob('*.html') if '.git' not in p.parts]


class AdsIsolation(unittest.TestCase):
    def test_ads_js_is_off_by_default(self):
        js = (ROOT / 'assets/ads.js').read_text(encoding='utf-8')
        self.assertRegex(js, r'var ADS_ENABLED = false;')

    def test_ads_js_has_cmp_and_no_slot_ids_yet(self):
        js = (ROOT / 'assets/ads.js').read_text(encoding='utf-8')
        self.assertIn('fundingchoicesmessages.google.com', js)
        self.assertIn('googlefcPresent', js)
        self.assertIn("var SLOTS = { intro: '', end: '' };", js)
        self.assertLess(js.index('var ADS_ENABLED'), js.index('fundingchoicesmessages'), 'switch must come first')
        self.assertLess(js.index('if (!ADS_ENABLED) { return; }'), js.index('adsbygoogle.js'))

    def test_allowlisted_pages_carry_widened_csp_and_others_do_not(self):
        for p in html_files():
            rel = str(p.relative_to(ROOT))
            text = p.read_text(encoding='utf-8')
            m = re.search(r'Content-Security-Policy" content="([^"]*)"', text)
            csp = m.group(1) if m else ''
            if rel in AD_PAGES:
                for host in ('pagead2.googlesyndication.com', 'fundingchoicesmessages.google.com', 'googleads.g.doubleclick.net'):
                    self.assertIn(host, csp, f'{rel} CSP must allow {host}')
            else:
                self.assertNotIn('google', csp, f'{rel} CSP must stay self-only')

    def test_only_allowlisted_pages_load_ads_js(self):
        loaders = {str(p.relative_to(ROOT)) for p in html_files()
                   if 'assets/ads.js' in p.read_text(encoding='utf-8')}
        self.assertEqual(loaders, set(AD_PAGES))

    def test_no_ad_code_outside_allowlist(self):
        for p in html_files():
            rel = str(p.relative_to(ROOT))
            if rel in AD_PAGES:
                continue
            text = p.read_text(encoding='utf-8')
            for marker in AD_MARKERS:
                self.assertNotIn(marker, text, f'{rel} must not contain {marker}')

    def test_mila_has_no_ad_code_or_adsense_meta(self):
        files = [p for p in (ROOT / 'mila').rglob('*') if p.is_file() and p.suffix in ('.html', '.js', '.json')]
        self.assertTrue(files)
        for p in files:
            text = p.read_text(encoding='utf-8')
            for marker in AD_MARKERS + [ROOT_META]:
                self.assertNotIn(marker, text, f'{p.relative_to(ROOT)} must not contain {marker}')

    def test_adsense_meta_only_on_home(self):
        for p in html_files():
            rel = str(p.relative_to(ROOT))
            has = ROOT_META in p.read_text(encoding='utf-8')
            self.assertEqual(has, rel == 'index.html', rel)

    def test_other_assets_do_not_load_ads(self):
        for name in ('site.js', 'count.js', 'i18n.js', 'play-badge.js'):
            text = (ROOT / 'assets' / name).read_text(encoding='utf-8')
            for marker in AD_MARKERS:
                self.assertNotIn(marker, text, f'assets/{name} must not contain {marker}')

    def test_never_on_excluded_page_kinds(self):
        for rel in AD_PAGES:
            self.assertFalse(re.search(r'privacy|support|mila|play|duel|dock|404', rel), rel)


if __name__ == '__main__':
    unittest.main()
