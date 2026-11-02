"""A release's notes: changelog.txt's "[B]X.Y.Z[/B]" entry, then how to install.

    python3 .github/release_notes.py 0.5.0
"""
import re
import sys

version = sys.argv[1]
changelog = open('changelog.txt', encoding='utf-8').read()
found = re.search(r'^\[B\]%s\[/B\]\n(.*?)(?=^\[B\]|\Z)' % re.escape(version), changelog, re.S | re.M)
if not found:
    sys.exit('changelog.txt has no [B]%s[/B] entry' % version)
lines, entry = [], found.group(1).strip()
for line in entry.splitlines():
    if line.startswith('•'):
        lines.append('- ' + line[1:].strip())
    elif lines:
        lines[-1] += ' ' + line.strip()  # a wrapped line continues its bullet
print('\n'.join(lines))
print('\n**Install:** download `skin.silo.skyline-%s.zip` below and use Kodi\'s *Add-ons → Install from zip file* '
      '(installs over earlier versions). Requires Kodi 21.' % version)
