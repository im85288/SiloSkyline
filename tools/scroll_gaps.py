#!/usr/bin/env python3
"""Give every scrolling label a gap, as Silo's: without one Kodi runs the
end of a title into its start ("MeYou Are No"). Runs last in build_all.py,
over generated and hand-written files alike; a label with its own gap keeps it.

    python3 tools/scroll_gaps.py
"""
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAP = '<scrollsuffix>     ·     </scrollsuffix>'
SCROLL = re.compile(r'<scroll>true</scroll>')


def with_gaps(text):
    out, last = [], 0
    for match in SCROLL.finditer(text):
        # The rest of this control: up to its next control or its end.
        rest = text[match.end():]
        end = min([i for i in (rest.find('</control>'), rest.find('<control')) if i >= 0] or [len(rest)])
        if 'scrollsuffix' in rest[:end] or 'scrollsuffix' in text[max(0, match.start() - 400):match.start()].split('<control')[-1]:
            continue
        out.append(text[last:match.end()] + GAP)
        last = match.end()
    return ''.join(out) + text[last:]


def main():
    changed = 0
    for path in sorted(glob.glob(os.path.join(ROOT, 'xml', '*.xml'))):
        text = open(path, encoding='utf-8').read()
        new = with_gaps(text)
        if new != text:
            open(path, 'w', encoding='utf-8').write(new)
            changed += 1
    print('Scroll gaps: %d files' % changed)


if __name__ == '__main__':
    main()
