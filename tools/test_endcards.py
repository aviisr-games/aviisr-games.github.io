#!/usr/bin/env python3
"""End-of-play cards on the Middle East 2030 briefing and the Baylight dock."""

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parent.parent

PAGES = {
    'middle-east-2030/briefing/index.html': 'com.aviisrgames.middleeast2030',
    'baylight/dock/index.html': 'com.aviisrgames.baylight',
}


def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


def card_open_tag(text):
    m = re.search(r'<div[^>]*\bid="end-card"[^>]*>', text)
    return m.group(0) if m else ''


class EndCardTests(unittest.TestCase):

    def test_one_win_link_for_own_package(self):
        for rel, pkg in PAGES.items():
            text = read(rel)
            wins = re.findall(r'href="([^"]*utm_medium=playable-win[^"]*)"', text)
            self.assertEqual(len(wins), 1, rel)
            self.assertIn('id=' + pkg + '&amp;', wins[0], rel)
            self.assertIn('utm_campaign=' + {
                'com.aviisrgames.middleeast2030': 'middle-east-2030',
                'com.aviisrgames.baylight': 'baylight'}[pkg] + '-playable-win', wins[0], rel)

    def test_card_is_announced_and_focusable(self):
        # Dock: the card itself is the result, so it is announced and takes focus.
        dock = card_open_tag(read('baylight/dock/index.html'))
        self.assertRegex(dock, r'role="status"|aria-live="polite"')
        self.assertIn('tabindex="-1"', dock)
        # Briefing: the term result comes first. Focus goes to the headline, and the store card is a
        # plain labelled region (a live region around a whole card reads everything or nothing).
        text = read('middle-east-2030/briefing/index.html')
        card = card_open_tag(text)
        self.assertIn('role="region"', card)
        self.assertNotIn('aria-live', card)
        self.assertRegex(text, r'id="final-headline"[^>]*tabindex="-1"')
        self.assertIn("getElementById('final-headline')", text)
        for rel in PAGES:
            self.assertNotIn('role="dialog"', card_open_tag(read(rel)), rel)

    def test_no_app_store_and_iphone_note(self):
        for rel in PAGES:
            text = read(rel)
            self.assertNotIn('apps.apple.com', text, rel)
            self.assertIn('Not on iPhone yet', text, rel)

    def test_briefing_keeps_fiction_notice(self):
        text = read('middle-east-2030/briefing/index.html')
        self.assertIn('Work of Fiction', text)
        self.assertIn('data-i18n="fictionNotice"', text)

    def test_briefing_translations_have_new_key(self):
        text = read('middle-east-2030/briefing/index.html')
        self.assertIn('data-i18n="endCardLine"', text)
        for lang in ('en', 'he', 'ar'):
            m = re.search(r'\n    ' + lang + r': \{(.*?)\n    \}', text, re.S)
            self.assertTrue(m, lang)
            self.assertIn('endCardLine:', m.group(1), lang)

    def test_dock_card_has_play_again_and_is_hidden_until_win(self):
        text = read('baylight/dock/index.html')
        self.assertIn('id="btn-play-again"', text)
        self.assertIn('hidden', card_open_tag(text))
        # shown only for hand-played wins, same rule as the counter
        self.assertIn('if (!auto && isWon()) showEndCard();', text)

    def test_no_emoji_or_timers_in_cards(self):
        text = read('baylight/dock/index.html')
        card = re.search(r'<div[^>]*id="end-card".*?</button>', text, re.S).group(0)
        self.assertNotRegex(card, r'[\U0001F300-\U0001FAFF☀-➿]')


if __name__ == '__main__':
    unittest.main()
