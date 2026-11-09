#!/usr/bin/env python3
"""Fail when the Ninely daily puzzle pack is about to run out.

After the last dated day, /ninely/play/ silently falls back to one practice puzzle, so the
"daily" promise breaks without any error. The weekly workflow runs this check and fails
when fewer than MIN_DAYS days of puzzles remain, which leaves time to regenerate the pack
(see .agent/HANDOFF.md, "Generators").
"""

from datetime import date, timedelta
from pathlib import Path
import json
import sys

MIN_DAYS = 30
PACK = Path(__file__).resolve().parent.parent / 'ninely/play/daily-pack.json'


def runway(today=None):
    days = sorted(json.loads(PACK.read_text(encoding='utf-8'))['days'])
    last = date.fromisoformat(days[-1])
    return last, (last - (today or date.today())).days


def main():
    last, left = runway()
    if left < MIN_DAYS:
        print(f'Ninely daily pack ends {last}: {left} days left (minimum {MIN_DAYS}). Regenerate it.')
        return 1
    print(f'Ninely daily pack ends {last}: {left} days left. OK.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
