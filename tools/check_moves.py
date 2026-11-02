#!/usr/bin/env python3
"""Check that every move names a control that exists: SetFocus(n), and a
plain number in onleft/onright/onup/ondown/onback, must be an id in the same
window (its own controls, or ones its includes bring in). A wrong id is a
key press that silently does nothing on the TV.

    python3 tools/check_moves.py
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ID = re.compile(r'<control[^>]*\bid="(\d+)"')
INCLUDE_DEF = re.compile(r'<include name="([^"]+)"[^>]*>(.*?)</include>', re.S)
INCLUDE_USE = re.compile(r'<include(?:\s+content="([^"]+)")?[^>]*>([^<]*)</include>|<include content="([^"]+)"')
MOVE = re.compile(r'<on(left|right|up|down|back)(?: condition="[^"]*")?>\s*(\d+)\s*</on\1>')
SET_FOCUS = re.compile(r'SetFocus\((\d+)')
PARAM_VALUE = re.compile(r'<param name="[^"]*" value="(\d+)"')


def includes():
    """{include name: its XML}, from every xml file (skins define them anywhere)."""
    found = {}
    for path in glob.glob(os.path.join(ROOT, 'xml', '*.xml')):
        for name, body in INCLUDE_DEF.findall(open(path, encoding='utf-8').read()):
            found.setdefault(name, body)
    return found


def expanded(text, defs, depth=0):
    """text with the includes it uses inlined, a few levels deep."""
    if depth > 6:
        return text
    used = set()
    for content, plain, bare in INCLUDE_USE.findall(text):
        used.add((content or bare or plain).strip())
    return text + ''.join(expanded(defs[name], defs, depth + 1) for name in used if name in defs)


def main():
    defs = includes()
    problems = []
    for path in sorted(glob.glob(os.path.join(ROOT, 'xml', '*.xml'))):
        raw = open(path, encoding='utf-8').read()
        if '<window' not in raw:
            continue  # includes, fonts, variables: checked where they're used
        text = expanded(raw, defs)
        ids = set(ID.findall(text))
        # An include's control can take its id from a parameter (id="$PARAM[...]").
        ids |= set(PARAM_VALUE.findall(text))
        targets = set(t for _, t in MOVE.findall(raw)) | set(SET_FOCUS.findall(raw))
        for target in sorted(targets - ids, key=int):
            problems.append('%s: moves to %s, which has no control' % (os.path.basename(path), target))
    if problems:
        sys.stderr.write('\n'.join(problems) + '\n')
        return 1
    print('Every move names a control in its window.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
