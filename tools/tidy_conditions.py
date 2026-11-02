#!/usr/bin/env python3
"""Simplify double negations in conditions: "!!x" is "x". Builders put a "!"
in front of conditions that may already start with one; Kodi reads both the
same, but the plain form is the one to read. Only conditions change
(condition="..." attributes and <visible> bodies), never labels. Runs in
build_all.py after the builders.

    python3 tools/tidy_conditions.py
"""
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONDITION = re.compile(r'(condition="|<visible(?: allowhiddenfocus="true")?>)([^"<]*)')


def tidy(text):
    return CONDITION.sub(lambda m: m.group(1) + re.sub(r'!!+', lambda n: '' if len(n.group(0)) % 2 == 0 else '!',
                                                        m.group(2)), text)


def main():
    changed = 0
    for path in sorted(glob.glob(os.path.join(ROOT, 'xml', '*.xml'))):
        text = open(path, encoding='utf-8').read()
        new = tidy(text)
        if new != text:
            open(path, 'w', encoding='utf-8').write(new)
            changed += 1
    print('Double negations: %d files tidied' % changed)


if __name__ == '__main__':
    main()
