"""Named colours for Skyline's colour themes: the last build step.

    python3 tools/build_colours.py

The builders write colours as values. This rewrites the ones a theme changes
into the names colors/defaults.xml defines (Silo's values) and the theme
files override (colors/Zephyr.xml, colors/OLED.xml; Kodi's Settings ->
Interface -> Skin -> Colours):

- SkylineBackground, SkylinePanel, SkylineDialog, SkylineCard,
  SkylineCardEmpty: the page, panels and dropdowns, dialogs and cards;
- SkylineLivePanel, SkylineLiveCard, SkylineLiveVeil, SkylineLiveBar: Live
  TV's quick guide, OK screen tiles, schedule veil and title bars;
- SkylineFocus: the focus pill, focus cards and rings (Silo's white);
- SkylineFocusText, SkylineFocusTextDim: text and icons drawn on it (black).

Text stays as it is (every theme is dark), and so does the watched tick,
which is black on a white disc, not on the focus.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_home import ROOT  # noqa: E402

THEMED = {
    'FF0D0F12': 'SkylineBackground',
    'F21C1F24': 'SkylinePanel',
    'FF131417': 'SkylineDialog',
    'FF1A1D27': 'SkylineCard',
    'FF262A31': 'SkylineCardEmpty',
    # Live TV's panels (TiviMate's grey in Silo's theme): the quick guide's and
    # the schedule's, the OK screen's tiles, the schedule's veil, the title bars.
    'F2272A30': 'SkylineLivePanel',
    'E6272A30': 'SkylineLiveCard',
    'CC272A30': 'SkylineLiveVeil',
    'FF33373E': 'SkylineLiveBar',
}
# Textures that show focus (or Silo's white primary button), in Silo's white.
FOCUS_TEXTURES = ('silo/pill.png', 'silo/dialog_button.png', 'silo/card_landscape_mask.png',
                  'silo/card_landscape_focus.png', 'silo/card_poster_focus.png', 'silo/season_ring.png',
                  'silo/avatar_ring.png', 'silo/person_ring.png', 'buttons/thumbnail_focused.png',
                  'silo/round_button.png')
KEEP_BLACK = ('OverlayWatched.png',)  # the watched tick on its white disc


def themed(text):
    for value, name in THEMED.items():
        text = text.replace('colordiffuse="%s"' % value, 'colordiffuse="%s"' % name)
        text = re.sub(r'<(textcolor|backgroundcolor)>%s<' % value, r'<\1>%s<' % name, text)
    # The focus: Silo's white on the shapes that show it.
    text = re.sub(r'(<((?:alt)?texture\w*)( [^>]*)?) colordiffuse="FFEDEDED"([^>]*>)(%s)<' % '|'.join(map(re.escape, FOCUS_TEXTURES)),
                  r'\1 colordiffuse="SkylineFocus"\4\5<', text)
    # What's drawn on the focus: black text and icons.
    text = re.sub(r'<(textcolor|focusedcolor|selectedcolor)>FF000000<', r'<\1>SkylineFocusText<', text)
    text = re.sub(r'<textcolor>(?:8C|99|B3)000000<', '<textcolor>SkylineFocusTextDim<', text)
    text = text.replace('[COLOR 8C000000]', '[COLOR SkylineFocusTextDim]')
    text = re.sub(r'colordiffuse="FF000000"([^>]*)>(?!(?:%s)<)' % '|'.join(map(re.escape, KEEP_BLACK)),
                  r'colordiffuse="SkylineFocusText"\1>', text)
    return text


def main():
    folder = os.path.join(ROOT, 'xml')
    changed = 0
    for name in sorted(os.listdir(folder)):
        if not name.endswith('.xml'):
            continue
        path = os.path.join(folder, name)
        text = open(path, encoding='utf-8').read()
        new = themed(text)
        if new != text:
            open(path, 'w', encoding='utf-8').write(new)
            changed += 1
    print('Named the themed colours in %d files' % changed)


if __name__ == '__main__':
    main()
