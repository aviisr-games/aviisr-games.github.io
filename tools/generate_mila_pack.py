#!/usr/bin/env python3
"""Build-time vocabulary pack exporter for Mila: English for Kids.

Extracts approved Pre-Band I (Grade 3) vocabulary from local repository:
/Users/aviisraeli/Documents/Claude/english-learning (commit 0f5b6d6)
"""

import json
from pathlib import Path
import re

MILA_REPO = Path('/Users/aviisraeli/Documents/Claude/english-learning')
VOCAB_FILE = MILA_REPO / 'src/lib/vocabulary.ts'
OUT_PACK = Path(__file__).resolve().parent.parent / 'mila/worksheets/pack-grade3.json'

TARGET_IDS = [
    'dog', 'cat', 'hen', 'sun',
    'pen', 'bag', 'hat', 'box',
    'egg', 'bed', 'boy', 'big'
]

def main():
    if not VOCAB_FILE.exists():
        raise FileNotFoundError(f"Vocabulary source not found: {VOCAB_FILE}")

    content = VOCAB_FILE.read_text(encoding='utf-8')

    # Regex to extract Word objects
    pattern = re.compile(
        r'\{\s*id:\s*[\'\"]([^\'\"]+)[\'\"],\s*'
        r'english:\s*[\'\"]([^\'\"]+)[\'\"],\s*'
        r'hebrew:\s*[\'\"]([^\'\"]+)[\'\"],\s*'
        r'exampleSentence:\s*[\'\"]([^\'\"]+)[\'\"],\s*'
        r'exampleSentenceHebrew:\s*[\'\"]([^\'\"]+)[\'\"],\s*'
        r'image:\s*[\'\"]([^\'\"]+)[\'\"],\s*'
        r'category:\s*[\'\"]([^\'\"]+)[\'\"].*?'
        r'band:\s*[\'\"]([^\'\"]+)[\'\"]',
        re.DOTALL
    )

    found_words = {}
    for match in pattern.finditer(content):
        w_id, eng, heb, ex_en, ex_he, img, cat, band = match.groups()
        found_words[w_id] = {
            'id': w_id,
            'english': eng,
            'hebrew': heb,
            'exampleSentence': ex_en,
            'exampleSentenceHebrew': ex_he,
            'image': img,
            'category': cat,
            'band': band
        }

    words_list = []
    for tid in TARGET_IDS:
        if tid not in found_words:
            raise KeyError(f"Word '{tid}' not found in vocabulary.ts")
        w = found_words[tid]
        if w['band'] != 'pre-band-1':
            raise ValueError(f"Word '{tid}' has band '{w['band']}', expected 'pre-band-1'")
        words_list.append(w)

    pack = {
        'schemaVersion': 1,
        'sourceCommit': '0f5b6d6',
        'sourceFile': 'src/lib/vocabulary.ts',
        'gradeBand': 'pre-band-1',
        'gradeLabelHe': 'כיתה ג׳ (Pre-Band I)',
        'ministryCurriculum': 'Israel Ministry of Education English Curriculum 2020',
        'wordCount': len(words_list),
        'words': words_list
    }

    OUT_PACK.parent.mkdir(parents=True, exist_ok=True)
    OUT_PACK.write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Exported {len(words_list)} words to {OUT_PACK}")

if __name__ == '__main__':
    main()
