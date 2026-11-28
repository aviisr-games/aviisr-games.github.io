"""Regression checks for legal-page integration with the current generated site."""
from pathlib import Path
from html.parser import HTMLParser
import unittest

ROOT = Path(__file__).resolve().parents[1]

class Structure(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.mains = []
        self.scripts = []
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'main':
            self.mains.append(attrs.get('id'))
        if tag == 'script':
            self.scripts.append(attrs.get('src', ''))

class LegalPagesTests(unittest.TestCase):
    def test_skip_links_have_unique_main_targets(self):
        for name in ['terms/index.html', 'accessibility/index.html',
                     'mila/privacy/index.html', 'mila/support/index.html',
                     'middle-east-2030/privacy/index.html', 'redline-2030/privacy/index.html']:
            with self.subTest(page=name):
                text = (ROOT / name).read_text()
                self.assertEqual(Structure(text).mains, ['main'])
                self.assertIn('href="#main"', text)

    def test_new_legal_pages_do_not_load_tracking_or_ads(self):
        for name in ['terms/index.html', 'accessibility/index.html']:
            self.assertEqual(Structure((ROOT / name).read_text()).scripts, [])

    def test_mila_retains_family_activation_and_deletion_disclosures(self):
        text = (ROOT / 'mila/privacy/index.html').read_text()
        self.assertIn('Google Cloud (Firebase)', text)
        self.assertIn('within 30 days', text)
        self.assertIn('תוך 30 יום', text)
        self.assertIn('Optional activation on additional family devices', text)

    def test_studio_notice_and_links_survive_generation(self):
        import build_site
        text = build_site.render_privacy({})
        self.assertIn('Amendment 13', text)
        self.assertIn('href="/terms/"', text)
        self.assertIn('href="/accessibility/"', text)

if __name__ == '__main__':
    unittest.main()
