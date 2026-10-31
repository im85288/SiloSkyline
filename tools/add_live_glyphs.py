#!/usr/bin/env python3
"""Give the skin's Inter fonts the superscript letters IPTV guides use for
"Live" (ᴸᶦᵛᵉ) and "New" (ᴺᵉʷ): Inter lacks ᴸ, ᶦ and ᴺ, which Kodi drew as boxes.
They're copied from Noto Sans (same units per em), outlines decomposed.

    python3 tools/add_live_glyphs.py   (needs fontTools; run once per Inter update)
"""
import os

from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

FONTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fonts')
SOURCE = 'NotoSans-Regular.ttf'
CHARS = 'ᴸᶦᴺ'  # Live (ᴸᶦᵛᵉ) and New (ᴺᵉʷ); Inter has ᵛ, ᵉ and ʷ


def add(target, source):
    font = TTFont(os.path.join(FONTS, target))
    donor = TTFont(os.path.join(FONTS, SOURCE))
    if font['head'].unitsPerEm != donor['head'].unitsPerEm:
        raise SystemExit('%s: units per em differ from %s' % (target, SOURCE))
    cmap, donor_cmap, glyphs = font.getBestCmap(), donor.getBestCmap(), donor.getGlyphSet()
    added = []
    for char in CHARS:
        if ord(char) in cmap:
            continue
        name = donor_cmap[ord(char)]
        recording = DecomposingRecordingPen(glyphs)
        glyphs[name].draw(recording)
        pen = TTGlyphPen(None)
        recording.replay(pen)
        new = 'live.%04X' % ord(char)
        font['glyf'][new] = pen.glyph()
        font['hmtx'][new] = donor['hmtx'][name]
        for table in font['cmap'].tables:
            if table.isUnicode():
                table.cmap[ord(char)] = new
        added.append(char)
    # The glyf table adds new glyphs to its order; the font's follows it.
    font.setGlyphOrder(font['glyf'].glyphOrder)
    if added:
        font.save(os.path.join(FONTS, target))
    print(target, 'added', ''.join(added) or 'nothing')


if __name__ == '__main__':
    for name in sorted(os.listdir(FONTS)):
        if name.startswith('Inter-') and name.endswith('.ttf'):
            add(name, SOURCE)
