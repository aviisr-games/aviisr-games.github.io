import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class AppAdsRecordsTests(unittest.TestCase):
    def test_seller_record_count_is_unchanged(self):
        """Only comment lines may change; the 1,157 seller records (2026-11-19) are pinned."""
        lines = (ROOT / 'app-ads.txt').read_text(encoding='utf-8').splitlines()
        records = [l for l in lines if re.search(r',\s*(DIRECT|RESELLER)\b', l) and not l.lstrip().startswith('#')]
        self.assertEqual(len(records), 1157)

    def test_header_lists_current_apps(self):
        first = (ROOT / 'app-ads.txt').read_text(encoding='utf-8').splitlines()[0]
        self.assertIn('Beamwise', first)
        self.assertNotIn('Casino', first)


if __name__ == '__main__':
    unittest.main()
