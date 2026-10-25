"""Generate Silo Skyline's textures into media/silo/ (pure Python, no Pillow).

    python3 tools/make_textures.py

Kodi multiplies an image's alpha by its <diffuse> texture, stretched to the
control's size, so masks are drawn at the size the skin uses them.
"""
import math
import os
import struct
import zlib

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'media', 'silo')
SUB = 4  # supersampling per axis for smooth edges


def write_png(name, width, height, alpha_at, rgb=(255, 255, 255)):
    rows = []
    for y in range(height):
        row = bytearray([0])
        for x in range(width):
            row += bytes(rgb) + bytes([max(0, min(255, int(alpha_at(x + 0.5, y + 0.5) * 255 + 0.5)))])
        rows.append(bytes(row))

    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
    data = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(b''.join(rows), 9)) + chunk(b'IEND', b''))
    with open(os.path.join(OUT, name), 'wb') as handle:
        handle.write(data)


def smoothstep(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def rounded_rect_coverage(x, y, width, height, radius, inset=0.0):
    """Anti-aliased coverage of a rounded rectangle at pixel centre (x, y)."""
    hits = 0
    for sy in range(SUB):
        for sx in range(SUB):
            px = x - 0.5 + (sx + 0.5) / SUB
            py = y - 0.5 + (sy + 0.5) / SUB
            left, top, right, bottom = inset, inset, width - inset, height - inset
            r = max(0.0, radius - inset)
            if not (left <= px <= right and top <= py <= bottom):
                continue
            cx = min(max(px, left + r), right - r)
            cy = min(max(py, top + r), bottom - r)
            if (px - cx) ** 2 + (py - cy) ** 2 <= r * r:
                hits += 1
    return hits / float(SUB * SUB)


def hero_mask(width=640, height=400):
    """Skyline's corner mask: crisp at the top right, fading out toward the
    left (over 55% of the width) and the bottom (over 45% of the height)."""
    def alpha(x, y):
        from_left = smoothstep(x / (width * 0.55))
        from_bottom = smoothstep((height - y) / (height * 0.45))
        return from_left * from_bottom
    write_png('hero_mask.png', width, height, alpha)


def card_mask(name, width, height, radius):
    write_png(name, width, height, lambda x, y: rounded_rect_coverage(x, y, width, height, radius))


def focus_ring(name, width, height, radius, thickness):
    def alpha(x, y):
        outer = rounded_rect_coverage(x, y, width, height, radius)
        inner = rounded_rect_coverage(x, y, width, height, radius, inset=thickness)
        return max(0.0, outer - inner)
    write_png(name, width, height, alpha)


def pill(size=60):
    """A white capsule end: used with border="30" so it stretches to any width."""
    write_png('pill.png', size, size, lambda x, y: rounded_rect_coverage(x, y, size, size, size / 2.0))


def scrim(height=256):
    """Vertical black scrim, opaque at the bottom, for text over artwork."""
    write_png('scrim_bottom.png', 4, height, lambda x, y: smoothstep(y / float(height)) * 0.9, rgb=(0, 0, 0))


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    hero_mask()
    card_mask('card_poster_mask.png', 260, 390, 14)
    card_mask('card_landscape_mask.png', 360, 202, 14)
    # Rings sit 6 px outside the card on each side.
    focus_ring('card_poster_focus.png', 272, 402, 20, 4)
    focus_ring('card_landscape_focus.png', 372, 214, 20, 4)
    pill()
    scrim()
    print('Wrote', ', '.join(sorted(os.listdir(OUT))))
