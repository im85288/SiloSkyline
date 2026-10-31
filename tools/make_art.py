"""Write resources/icon.png and resources/fanart.jpg: the skin's picture in
Kodi's skin list, from the mark and splash (run make_textures.py first).
Needs Pillow.

    python3 tools/make_art.py
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = os.path.join(root, 'resources')
mark = Image.open(root + '/media/silo/skyline_mark.png').convert('RGBA')
bg = Image.open(root + '/media/silo/splash_bg.png').convert('RGB').resize((1920, 1080), Image.BICUBIC)
bold = lambda n: ImageFont.truetype(root + '/fonts/Inter-Bold.ttf', n)
medium = lambda n: ImageFont.truetype(root + '/fonts/Inter-Medium.ttf', n)

def wordmark(draw, cx, y, size):
    """Skyline's name, centred on cx."""
    font = bold(size)
    draw.text((cx - draw.textlength('Skyline', font=font) / 2, y), 'Skyline', font=font, fill=(0xED, 0xED, 0xED))

# Fanart (1920x1080): the splash.
fan = bg.copy().convert('RGBA')
m = mark.resize((300, 300), Image.LANCZOS); fan.alpha_composite(m, (810, 250))
d = ImageDraw.Draw(fan); wordmark(d, 960, 600, 110)
d.text((960, 770), 'A Kodi skin for Silo', font=medium(40), fill=(0x9A, 0x9A, 0x9A), anchor='mm')
fan.convert('RGB').save(out + '/fanart.jpg', quality=90)
# Icon (512x512): the mark on the splash colours, with the name.
ic = bg.crop((420, 0, 1500, 1080)).resize((512, 512), Image.BICUBIC).convert('RGBA')
m = mark.resize((300, 300), Image.LANCZOS); ic.alpha_composite(m, (106, 46))
d = ImageDraw.Draw(ic); wordmark(d, 256, 360, 64)
ic.convert('RGB').save(out + '/icon.png')
