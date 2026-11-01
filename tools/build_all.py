#!/usr/bin/env python3
"""Rebuild every generated skin file, in the one order that works:

    python3 tools/build_all.py

Each builder writes its own XML and its own section of the shared files
(xml/Variables.xml, Timers.xml, Font.xml): it takes its section out and adds
it back at the end, so running them all in this fixed order gives the same
files whatever state they start in. build_colours goes last, as it rewrites
colour values across everything the others wrote. Textures (make_textures.py,
make_rating_logos.swift) and art (make_art.py) are separate and rarely change.
"""
import glob
import os
import subprocess
import sys
import xml.etree.ElementTree as ElementTree

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
BUILDERS = ('build_home', 'build_info', 'build_browse', 'build_search', 'build_upnext', 'build_shortcuts',
            'build_options', 'build_frame', 'build_library', 'build_person', 'build_tv', 'build_requests', 'build_showcase',
            'build_colours')


def main():
    for name in BUILDERS:
        result = subprocess.run([sys.executable, os.path.join(TOOLS, name + '.py')], cwd=ROOT,
                                capture_output=True, text=True)
        if result.returncode:
            sys.stderr.write('%s failed:\n%s%s' % (name, result.stdout, result.stderr))
            return 1
    # Every skin file must still parse (Kodi skips a window that doesn't).
    broken = []
    for path in sorted(glob.glob(os.path.join(ROOT, 'xml', '*.xml'))):
        try:
            ElementTree.parse(path)
        except ElementTree.ParseError as error:
            broken.append('%s: %s' % (os.path.relpath(path, ROOT), error))
    if broken:
        sys.stderr.write('Not well-formed:\n  %s\n' % '\n  '.join(broken))
        return 1
    print('Rebuilt the skin (%d builders); every xml/*.xml parses.' % len(BUILDERS))
    return 0


if __name__ == '__main__':
    sys.exit(main())
