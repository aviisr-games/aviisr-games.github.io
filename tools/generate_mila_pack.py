#!/usr/bin/env python3
"""Build-time vocabulary pack exporter for Mila: English for Kids.

Extracts approved Ministry of Education vocabulary from aviisr-games/english-learning at a pinned
commit (`git show SOURCE_COMMIT:src/lib/vocabulary.ts`). Point MILA_REPO at a local clone.

Generates (self-contained; the worksheet and answer key are rendered from the same data):
- pack-grade3.json (Pre-Band I, Grade 3)
- pack-grade4.json (Band I Core I, Grade 4)
- pack-grade5.json (Band I Core II, Grade 5)
  each with words, matching, wordBank and sentences
- pack.json (copy of Grade 3 pack for backwards compatibility)
- mila/worksheets/index.html: GRADE_DATA and the static Grade 3 markup, rendered with the exact
  string templates setGrade() uses, so Grade 3 -> 4 -> 3 tab switches leave an identical DOM.

Usage: MILA_REPO=~/Repos/english-learning python3 tools/generate_mila_pack.py
"""

import json
import os
from pathlib import Path
import re
import shutil
import subprocess

SOURCE_COMMIT = '0f5b6d6'
SOURCE_FILE = 'src/lib/vocabulary.ts'
MILA_REPO = Path(os.environ.get('MILA_REPO', str(Path.home() / 'Repos/english-learning'))).expanduser()
OUT_DIR = Path(__file__).resolve().parent.parent / 'mila/worksheets'
WORKSHEET_HTML = OUT_DIR / 'index.html'
HEB_LETTERS = ['א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח']

GRADES_CONFIG = [
    {
        'grade': 3,
        'title': 'מילה (Mila) — ערכת לימוד אנגלית לכיתה ג׳',
        'sub': '12 כרטיסיות גזירה ודפי עבודה מודפסים ללימוד ותרגול אוצר מילים ראשוני באנגלית ללא מסכים.',
        'curriculum': 'מבוסס על רשימת המילים הרשמית <em>Pre-Band I</em> של משרד החינוך (תוכנית הלימודים באנגלית 2020) עבור תלמידי כיתה ג׳. הערכה כוללת מילות CVC בסיסיות, תרגום מדויק לעברית ומשפטי דוגמה.',
        'filename': 'pack-grade3.json',
        'band': 'pre-band-1',
        'labelHe': 'כיתה ג׳ (Pre-Band I)',
        'target_ids': [
            'dog', 'cat', 'hen', 'sun',
            'pen', 'bag', 'hat', 'box',
            'egg', 'bed', 'boy', 'big'
        ],
        # Part B: left column order, then the order of the Hebrew column (letters א..ח).
        'matching_left': ['dog', 'cat', 'sun', 'hen', 'pen', 'bag', 'hat', 'box'],
        'matching_right': ['hat', 'sun', 'dog', 'bag', 'cat', 'box', 'pen', 'hen'],
        # Part C: word bank and sentence order (each sentence is that word's exampleSentence).
        'word_bank': ['dog', 'cat', 'pen', 'egg', 'bed', 'big'],
        'sentence_ids': ['egg', 'cat', 'dog', 'pen', 'bed', 'big']
    },
    {
        'grade': 4,
        'title': 'מילה (Mila) — ערכת לימוד אנגלית לכיתה ד׳',
        'sub': '12 כרטיסיות גזירה ודפי עבודה מודפסים ללימוד ותרגול אוצר מילים (Band I Core I) ללא מסכים.',
        'curriculum': 'מבוסס על רשימת המילים הרשמית <em>Band I Core I</em> של משרד החינוך (תוכנית הלימודים באנגלית 2020) עבור תלמידי כיתה ד׳. הערכה כוללת שמות עצם, תארים ופעלים בסיסיים, תרגום מדויק לעברית ומשפטי דוגמה.',
        'filename': 'pack-grade4.json',
        'band': 'band-1-core-1',
        'labelHe': 'כיתה ד׳ (Band I Core I)',
        'target_ids': [
            'happy', 'cold', 'fish', 'book',
            'girl', 'ball', 'car', 'apple',
            'small', 'shoe', 'dress', 'coat'
        ],
        # Part B: left column order, then the order of the Hebrew column (letters א..ח).
        'matching_left': ['happy', 'cold', 'fish', 'book', 'girl', 'ball', 'car', 'apple'],
        'matching_right': ['book', 'fish', 'car', 'happy', 'apple', 'cold', 'ball', 'girl'],
        # Part C: word bank and sentence order (each sentence is that word's exampleSentence).
        'word_bank': ['happy', 'cold', 'fish', 'ball', 'car', 'shoe'],
        'sentence_ids': ['fish', 'happy', 'car', 'cold', 'ball', 'shoe']
    },
    {
        'grade': 5,
        'title': 'מילה (Mila) — ערכת לימוד אנגלית לכיתה ה׳',
        'sub': '12 כרטיסיות גזירה ודפי עבודה מודפסים ללימוד ותרגול אוצר מילים (Band I Core II) ללא מסכים.',
        'curriculum': 'מבוסס על רשימת המילים הרשמית <em>Band I Core II</em> של משרד החינוך (תוכנית הלימודים באנגלית 2020) עבור תלמידי כיתה ה׳. הערכה כוללת שמות עצם, תארים ומאכלים מורחבים, תרגום מדויק לעברית ומשפטי דוגמה.',
        'filename': 'pack-grade5.json',
        'band': 'band-1-core-2',
        'labelHe': 'כיתה ה׳ (Band I Core II)',
        'target_ids': [
            'rabbit', 'snake', 'candy', 'cookie',
            'soup', 'tomato', 'shirt', 'sock',
            'glasses', 'camera', 'key', 'ruler'
        ],
        # Part B: left column order, then the order of the Hebrew column (letters א..ח).
        'matching_left': ['rabbit', 'snake', 'candy', 'cookie', 'soup', 'tomato', 'shirt', 'sock'],
        'matching_right': ['cookie', 'snake', 'shirt', 'rabbit', 'tomato', 'soup', 'sock', 'candy'],
        # Part C: word bank and sentence order (each sentence is that word's exampleSentence).
        'word_bank': ['rabbit', 'snake', 'soup', 'glasses', 'camera', 'ruler'],
        'sentence_ids': ['rabbit', 'snake', 'soup', 'glasses', 'camera', 'ruler']
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


def build_matching(cfg, words):
    by_id = {w['id']: w for w in words}
    letter_of = {wid: HEB_LETTERS[i] for i, wid in enumerate(cfg['matching_right'])}
    assert sorted(cfg['matching_left']) == sorted(cfg['matching_right']), cfg['grade']
    return [
        {
            'num': i + 1,
            'eng': by_id[left]['english'],
            'emoji': by_id[left]['image'],
            'hebLetter': HEB_LETTERS[i],
            'hebText': by_id[right]['hebrew'],
            'answerLetter': letter_of[left],
            'answerText': by_id[left]['hebrew'],
        }
        for i, (left, right) in enumerate(zip(cfg['matching_left'], cfg['matching_right']))
    ]


def build_sentences(cfg, words):
    by_id = {w['id']: w for w in words}
    out = []
    for i, wid in enumerate(cfg['sentence_ids']):
        w = by_id[wid]
        sentence, word = w['exampleSentence'], w['english']
        pos = sentence.find(word)
        if pos < 0 or sentence.find(word, pos + 1) >= 0:
            raise ValueError(f"'{word}' must appear exactly once in its example sentence: {sentence}")
        out.append({
            'num': i + 1,
            'answer': word,
            'engPre': sentence[:pos],
            'engPost': sentence[pos + len(word):],
            'hebHint': w['exampleSentenceHebrew'].rstrip('.?!'),
        })
    return out


# The four renderers below must stay character-for-character identical to setGrade() in
# mila/worksheets/index.html (tools/test_monetization_pilot.py checks both directions).
def render_cards(words):
    return ''.join(
        '<div class="flashcard">'
        f'<div class="flashcard-emoji">{w["image"]}</div>'
        f'<div class="flashcard-word"><span class="bidi-eng" lang="en">{w["english"]}</span></div>'
        f'<div class="flashcard-trans">{w["hebrew"]}</div>'
        f'<div class="flashcard-sentence"><span class="bidi-eng" lang="en">{w["exampleSentence"]}</span><br>{w["exampleSentenceHebrew"]}</div>'
        '</div>'
        for w in words)


def render_matching(matching):
    return ''.join(
        '<tr>'
        f'<td>{m["num"]}. <span class="bidi-eng" lang="en">{m["eng"]}</span> {m["emoji"]}</td>'
        '<td style="text-align: center;">⚪</td>'
        f'<td>{m["hebLetter"]}. {m["hebText"]}</td>'
        '</tr>'
        for m in matching)


def render_word_bank(bank):
    return 'מחסן מילים: &nbsp;' + ' &nbsp;·&nbsp; '.join(
        f'<span class="bidi-eng" lang="en">{w}</span>' for w in bank)


def render_sentences(sentences):
    return ''.join(
        '<div class="sentence-item">'
        f'<span class="bidi-eng" lang="en">{s["num"]}. {s["engPre"]}<span class="blank-line"></span>{s["engPost"]}</span> &nbsp; ({s["hebHint"]})'
        '</div>'
        for s in sentences)


STATIC_SLOTS = [
    # (opening tag, closing lookahead, renderer)
    ('<div class="cards-grid" id="cards-grid">', r'</div>\s*</section>', lambda g: render_cards(g['words'])),
    ('<tbody id="match-table-body">', r'</tbody>', lambda g: render_matching(g['matching'])),
    ('<div class="word-bank" id="word-bank">', r'</div>', lambda g: render_word_bank(g['wordBank'])),
    ('<div id="sentence-list">', r'</div>\s*<div class="no-print"', lambda g: render_sentences(g['sentences'])),
]


def grade_data_entry(cfg, pack):
    return {
        'grade': cfg['grade'],
        'title': cfg['title'],
        'sub': cfg['sub'],
        'curriculum': cfg['curriculum'],
        'words': [{k: w[k] for k in ('id', 'english', 'hebrew', 'exampleSentence', 'exampleSentenceHebrew', 'image')}
                  for w in pack['words']],
        'matching': [{k: m[k] for k in ('num', 'eng', 'emoji', 'hebLetter', 'hebText')} for m in pack['matching']],
        'wordBank': pack['wordBank'],
        'sentences': [{k: s[k] for k in ('num', 'engPre', 'engPost', 'hebHint')} for s in pack['sentences']],
    }


def render_worksheet(html, grade_data):
    """Rewrite GRADE_DATA (JSON, valid JS) and the static Grade 3 markup in the worksheet."""
    body = json.dumps(grade_data, ensure_ascii=False, indent=2)
    html, n = re.subn(r'var GRADE_DATA = \{.*?\n\};\n', lambda _: f'var GRADE_DATA = {body};\n', html, flags=re.DOTALL)
    if n != 1:
        raise ValueError('GRADE_DATA block not found exactly once')
    g3 = grade_data['3']
    for opening, closing, render in STATIC_SLOTS:
        pattern = re.escape(opening) + r'(.*?)(?=' + closing + ')'
        html, n = re.subn(pattern, lambda _: opening + render(g3), html, count=1, flags=re.DOTALL)
        if n != 1:
            raise ValueError(f'static slot not found: {opening}')
    return html


def read_vocabulary():
    return subprocess.run(
        ['git', '-C', str(MILA_REPO), 'show', f'{SOURCE_COMMIT}:{SOURCE_FILE}'],
        check=True, capture_output=True, text=True).stdout


def main():
    content = read_vocabulary()
    found_words = parse_vocabulary(content)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    grade_data = {}

    for cfg in GRADES_CONFIG:
        words_list = []
        for tid in cfg['target_ids']:
            if tid not in found_words:
                raise KeyError(f"Word '{tid}' not found in vocabulary.ts")
            w = found_words[tid]
            if w['band'] != cfg['band']:
                raise ValueError(f"Word '{tid}' has band '{w['band']}', expected '{cfg['band']}'")
            words_list.append(w)
        ids = set(cfg['target_ids'])
        for key in ('matching_left', 'word_bank', 'sentence_ids'):
            if not set(cfg[key]) <= ids:
                raise ValueError(f"Grade {cfg['grade']} {key} uses words outside the pack")

        pack = {
            'schemaVersion': 1,
            'sourceCommit': SOURCE_COMMIT,
            'sourceFile': SOURCE_FILE,
            'gradeBand': cfg['band'],
            'gradeLabelHe': cfg['labelHe'],
            'ministryCurriculum': 'Israel Ministry of Education English Curriculum 2020',
            'wordCount': len(words_list),
            'words': words_list,
            'matching': build_matching(cfg, words_list),
            'wordBank': [w for w in cfg['word_bank']],
            'sentences': build_sentences(cfg, words_list),
        }

        out_path = OUT_DIR / cfg['filename']
        out_path.write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"Exported {len(words_list)} words, {len(pack['matching'])} matches, "
              f"{len(pack['sentences'])} sentences to {out_path}")
        grade_data[str(cfg['grade'])] = grade_data_entry(cfg, pack)

    # For backwards compatibility, copy pack-grade3.json to pack.json
    shutil.copyfile(OUT_DIR / 'pack-grade3.json', OUT_DIR / 'pack.json')
    print(f"Copied pack-grade3.json to {OUT_DIR / 'pack.json'}")

    html = WORKSHEET_HTML.read_text(encoding='utf-8')
    WORKSHEET_HTML.write_text(render_worksheet(html, grade_data), encoding='utf-8')
    print(f"Rendered GRADE_DATA and static Grade 3 markup into {WORKSHEET_HTML}")


if __name__ == '__main__':
    main()
