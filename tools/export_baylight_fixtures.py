#!/usr/bin/env python3
"""Exports solver-verified Baylight dock levels and winning sequences.

Source: /Volumes/MacMiniDev/projects/baylight (commit ca07a94)
Levels: Dock 5 (Locked Bay) and Dock 6 (Pallet Parking)
"""

from collections import deque
import json
from pathlib import Path
import sys

BAYLIGHT_DIR = Path('/Volumes/MacMiniDev/projects/baylight')
sys.path.append(str(BAYLIGHT_DIR / 'Tools'))
import baylight_rules

OUT_FILE = Path(__file__).resolve().parent.parent / 'tools/baylight_fixtures.json'

def solve_level(lvl):
    q = deque([(baylight_rules.start(lvl), [])])
    seen = {baylight_rules.start(lvl).key()}
    while q:
        st, path = q.popleft()
        if baylight_rules.won(lvl, st):
            return path
        for act, nxt in baylight_rules.moves(lvl, st):
            k = nxt.key()
            if k not in seen and baylight_rules.solvable(lvl, nxt):
                seen.add(k)
                q.append((nxt, path + [(act, nxt)]))
    return None

def main():
    levels_path = BAYLIGHT_DIR / 'Assets/_Project/Resources/Levels/levels.txt'
    levels = baylight_rules.parse(str(levels_path))

    target_ids = [5, 6]
    exported_levels = []

    for tid in target_ids:
        lvl = next(l for l in levels if l['id'] == tid)
        solution = solve_level(lvl)
        if not solution:
            raise ValueError(f"Could not find winning sequence for level {tid}")

        solution_data = []
        for act, st in solution:
            bays_clean = [(c if c is not None else None, n) for c, n in st.bays]
            solution_data.append({
                'action': act[0],
                'target': act[1] if len(act) > 1 else None,
                'afterState': {
                    'i': st.i,
                    'bays': bays_clean,
                    'locked': st.locked,
                    'ships': st.ships,
                    'pallet': list(st.pallet)
                }
            })

        exported_levels.append({
            'id': lvl['id'],
            'name': f"Dock {lvl['id']}",
            'subtitle': 'Locked Bay Opening' if lvl['locked'] > 0 else 'Pallet Parking Strategy',
            'bays': lvl['bays'],
            'locked': lvl['locked'],
            'unlock_after': lvl['unlock_after'],
            'pallet': lvl['pallet'],
            'belt': lvl['belt'],
            'tip': lvl['tip'],
            'moveCount': len(solution_data),
            'solutionMoves': solution_data
        })

    data = {
        'schemaVersion': 1,
        'sourceCommit': 'ca07a94',
        'sourceRepo': 'https://github.com/aviisr-games/baylight',
        'levels': exported_levels
    }

    OUT_FILE.write_text(json.dumps(data, indent=2), encoding='utf-8')
    print(f"Exported {len(exported_levels)} levels to {OUT_FILE}")

if __name__ == '__main__':
    main()
