#!/usr/bin/env python3
"""Build-time vocabulary pack exporter for Mila: English for Kids.

Extracts approved Ministry of Education vocabulary from local repository:
/Users/aviisraeli/Documents/Claude/english-learning (commit 0f5b6d6)

Generates:
- pack-grade3.json (Pre-Band I, Grade 3)
- pack-grade4.json (Band I Core I, Grade 4)
- pack-grade5.json (Band I Core II, Grade 5)
- pack.json (copy of Grade 3 pack for backwards compatibility)
"""

import json
from pathlib import Path
import re
import shutil

MILA_REPO = Path('/Users/aviisraeli/Documents/Claude/english-learning')
VOCAB_FILE = MILA_REPO / 'src/lib/vocabulary.ts'
OUT_DIR = Path(__file__).resolve().parent.parent / 'mila/worksheets'

GRADES_CONFIG = [
    {
        'grade': 3,
        'filename': 'pack-grade3.json',
        'band': 'pre-band-1',
        'labelHe': 'כיתה ג׳ (Pre-Band I)',
        'target_ids': [
            'dog', 'cat', 'hen', 'sun',
            'pen', 'bag', 'hat', 'box',
            'egg', 'bed', 'boy', 'big'
        ]
    },
    {
        'grade': 4,
        'filename': 'pack-grade4.json',
        'band': 'band-1-core-1',
        'labelHe': 'כיתה ד׳ (Band I Core I)',
        'target_ids': [
            'happy', 'cold', 'fish', 'book',
            'girl', 'ball', 'car', 'apple',
            'small', 'shoe', 'dress', 'coat'
        ]
    },
    {
        'grade': 5,
        'filename': 'pack-grade5.json',
        'band': 'band-1-core-2',
        'labelHe': 'כיתה ה׳ (Band I Core II)',
        'target_ids': [
            'rabbit', 'snake', 'candy', 'cookie',
            'soup', 'tomato', 'shirt', 'sock',
            'glasses', 'camera', 'key', 'ruler'
        ]
    }
]


def parse_vocabulary(content: str):
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
    return found_words


def main():
    if not VOCAB_FILE.exists():
        raise FileNotFoundError(f"Vocabulary source not found: {VOCAB_FILE}")

    content = VOCAB_FILE.read_text(encoding='utf-8')
    found_words = parse_vocabulary(content)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for cfg in GRADES_CONFIG:
        words_list = []
        for tid in cfg['target_ids']:
            if tid not in found_words:
                raise KeyError(f"Word '{tid}' not found in vocabulary.ts")
            w = found_words[tid]
            if w['band'] != cfg['band']:
                raise ValueError(f"Word '{tid}' has band '{w['band']}', expected '{cfg['band']}'")
            words_list.append(w)

        pack = {
            'schemaVersion': 1,
            'sourceCommit': '0f5b6d6',
            'sourceFile': 'src/lib/vocabulary.ts',
            'gradeBand': cfg['band'],
            'gradeLabelHe': cfg['labelHe'],
            'ministryCurriculum': 'Israel Ministry of Education English Curriculum 2020',
            'wordCount': len(words_list),
            'words': words_list
        }

        out_path = OUT_DIR / cfg['filename']
        out_path.write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"Exported {len(words_list)} words to {out_path}")

    # For backwards compatibility, copy pack-grade3.json to pack.json
    shutil.copyfile(OUT_DIR / 'pack-grade3.json', OUT_DIR / 'pack.json')
    print(f"Copied pack-grade3.json to {OUT_DIR / 'pack.json'}")


if __name__ == '__main__':
    main()
