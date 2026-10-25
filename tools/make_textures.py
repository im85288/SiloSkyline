"""Generate Silo Skyline's textures into media/silo/ (pure Python, no Pillow).

    python3 tools/make_textures.py

Kodi multiplies an image's alpha by its <diffuse> texture, stretched to the
control's size, so masks are drawn at the size the skin uses them.
"""
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
    """Skyline's corner mask, with Silo's stops (TvRootHeroBackdrop): clear at
    the left edge to solid at 68% of the width, and solid down to 58% of the
    height, then clear at the bottom, each a straight ramp."""
    def alpha(x, y):
        from_left = min(1.0, x / (width * 0.68))
        from_bottom = min(1.0, max(0.0, (height - y) / (height * 0.42)))
        return from_left * from_bottom
    write_png('hero_mask.png', width, height, alpha)


def tint_wash(width=192, height=108):
    """Silo's ambient wash, drawn in white for the skin to colour with the
    title's tint: diagonal from the top right (opaque) to the bottom left
    (18%), through 50% at 45% of the way (TvRootHeroBackdrop's stops)."""
    stops = [(0.00, 1.0), (0.12, 0.91), (0.26, 0.76), (0.45, 0.5), (0.62, 0.385), (0.80, 0.282), (1.00, 0.18)]
    # Compose's linearGradient from (w, 0) to (0, h) on a 1920x1080 page.
    page_w, page_h = 1920.0, 1080.0

    def alpha(x, y):
        px, py = x / width * page_w, y / height * page_h
        t = ((page_w - px) * page_w + py * page_h) / (page_w ** 2 + page_h ** 2)
        t = min(1.0, max(0.0, t))
        for (t0, a0), (t1, a1) in zip(stops, stops[1:]):
            if t <= t1:
                return a0 + (a1 - a0) * (t - t0) / (t1 - t0)
        return stops[-1][1]
    write_png('tint_wash.png', width, height, alpha)


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



def card_scrim(height=256):
    """Silo's card scrim: clear over the top half, then darkening to 60% black
    at the bottom edge. Drawn with the card's mask as its diffuse."""
    write_png('card_scrim.png', 4, height,
              lambda x, y: 0.6 * smoothstep((y / float(height) - 0.5) / 0.5), rgb=(0, 0, 0))


def person_placeholder(size=172):
    """A head-and-shoulders silhouette in a grey circle, for cast without a
    photo (Kodi can't take a name's initials in a skin)."""
    r = size / 2.0

    def alpha(x, y):
        hits = 0
        for sy in range(SUB):
            for sx in range(SUB):
                px = x - 0.5 + (sx + 0.5) / SUB
                py = y - 0.5 + (sy + 0.5) / SUB
                if (px - r) ** 2 + (py - r) ** 2 > r * r:
                    continue
                head = (px - r) ** 2 + (py - size * 0.40) ** 2 <= (size * 0.17) ** 2
                body = ((px - r) / (size * 0.32)) ** 2 + ((py - size * 0.95) / (size * 0.30)) ** 2 <= 1
                hits += 1 if not (head or body) else 0
        return hits / float(SUB * SUB)
    # The circle is grey; the figure is cut out and drawn lighter under it.
    write_png('person_placeholder.png', size, size, alpha, rgb=(0x2A, 0x2E, 0x35))


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    hero_mask()
    tint_wash()
    card_mask('card_poster_mask.png', 176, 264, 12)
    card_mask('card_landscape_mask.png', 360, 202, 14)
    # Rings sit 6 px outside the card on each side.
    focus_ring('card_poster_focus.png', 188, 276, 18, 4)
    focus_ring('card_landscape_focus.png', 372, 214, 20, 4)
    # Badges: a 2 px outline, stretched with border="8".
    focus_ring('badge_outline.png', 32, 32, 8, 2)
    pill()
    scrim()
    # Cast photos: round, with a ring 6 px outside the photo.
    # Cast photos: a round mask, and a ring 6 px outside the photo.
    card_mask('person_mask.png', 172, 172, 86)
    focus_ring('person_ring.png', 184, 184, 92, 4)
    # The profile avatar in the menu bar, and its focus ring 4 px outside it.
    card_mask('avatar_mask.png', 56, 56, 28)
    card_scrim()
    person_placeholder()
    focus_ring('avatar_ring.png', 64, 64, 32, 3)
    print('Wrote', ', '.join(sorted(os.listdir(OUT))))
