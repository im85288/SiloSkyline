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
    """alpha_at(x, y) gives a pixel's alpha, or (alpha, (r, g, b)) to colour it too."""
    rows = []
    for y in range(height):
        row = bytearray([0])
        for x in range(width):
            value = alpha_at(x + 0.5, y + 0.5)
            alpha, colour = value if isinstance(value, tuple) else (value, rgb)
            row += bytes(colour) + bytes([max(0, min(255, int(alpha * 255 + 0.5)))])
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


def badge_fill(name='badge_fill.png', size=32, radius=8, rim=1.5):
    """Silo's badge: a faint white fill with a slightly brighter rim (both
    white; the alpha carries them), stretched with border="8"."""
    def alpha(x, y):
        outer = rounded_rect_coverage(x, y, size, size, radius)
        inner = rounded_rect_coverage(x, y, size, size, radius, inset=rim)
        return (outer - inner) * 0.34 + inner * 0.14
    write_png(name, size, size, alpha)


def menu_panel(name='menu_panel.png', size=96, radius=24, rim=1.5):
    """Silo's Apple TV menus: a near-black glass panel (#272A30 at 95%) with a
    faint light rim, stretched with border="28"."""
    def pixel(x, y):
        outer = rounded_rect_coverage(x, y, size, size, radius)
        inner = rounded_rect_coverage(x, y, size, size, radius, inset=rim)
        edge = outer - inner
        # The rim: white at 14% over the panel, mixed into one colour.
        alpha = inner * 0.95 + edge * 0.97
        mix = edge / alpha if alpha else 0
        colour = tuple(int(base + (255 - base) * 0.14 * mix) for base in (0x27, 0x2A, 0x30))
        return alpha, colour
    write_png(name, size, size, pixel)


def epg_now(name='epg_now.png', width=28, height=28, dot=12, line=3):
    """The guide's "now" marker: Kodi stretches it from the grid's start to
    the current time; only its right edge shows, a white line with a dot at
    its top, as TiviMate's (border="0,16,18,0": the dot and the line's
    column keep their size, with clear margin so filtering doesn't smear them)."""
    cx, cy = width - dot / 2.0, dot / 2.0

    def alpha(x, y):
        in_dot = (x - cx) ** 2 + (y - cy) ** 2 <= (dot / 2.0) ** 2
        in_line = abs(x - cx) <= line / 2.0
        return 1.0 if in_dot or in_line else 0.0
    write_png(name, width, height, alpha)


def play_circle(name='play_circle.png', size=64):
    """Silo's Continue Watching mark: a white disc with a play triangle cut out."""
    def in_triangle(px, py):
        # Pointing right, centred a little right of the disc's middle, as Silo's.
        x0, y0, x1, y1, x2, y2 = size * 0.40, size * 0.30, size * 0.40, size * 0.70, size * 0.72, size * 0.50
        def side(ax, ay, bx, by):
            return (px - bx) * (ay - by) - (ax - bx) * (py - by)
        d1, d2, d3 = side(x0, y0, x1, y1), side(x1, y1, x2, y2), side(x2, y2, x0, y0)
        return not ((d1 < 0 or d2 < 0 or d3 < 0) and (d1 > 0 or d2 > 0 or d3 > 0))

    def alpha(x, y):
        disc = rounded_rect_coverage(x, y, size, size, size / 2.0)
        hits = sum(in_triangle(x - 0.5 + (sx + 0.5) / SUB, y - 0.5 + (sy + 0.5) / SUB)
                   for sy in range(SUB) for sx in range(SUB))
        return max(0.0, disc - hits / float(SUB * SUB))
    write_png(name, size, size, alpha)


def pill(size=60):
    """A white capsule end: used with border="30" so it stretches to any width."""
    write_png('pill.png', size, size, lambda x, y: rounded_rect_coverage(x, y, size, size, size / 2.0))


def switches(width=112, height=56):
    """An on/off switch drawn at twice its size on screen (56x28): on is a
    filled track with a cut-out knob on the right, off an outlined track with
    a knob on the left."""
    knob = height / 2.0 - 7
    def on(x, y):
        track = rounded_rect_coverage(x, y, width, height, height / 2.0)
        hole = rounded_rect_coverage(x - (width - height / 2.0 - knob), y - (height / 2.0 - knob), 2 * knob, 2 * knob, knob)
        return max(0.0, track - hole)
    def off(x, y):
        ring = rounded_rect_coverage(x, y, width, height, height / 2.0) \
            - rounded_rect_coverage(x, y, width, height, height / 2.0, inset=4)
        dot = rounded_rect_coverage(x - (height / 2.0 - knob), y - (height / 2.0 - knob), 2 * knob, 2 * knob, knob)
        return max(ring, dot)
    write_png('switch_on.png', width, height, on)
    write_png('switch_off.png', width, height, off)


def scrim(height=256):
    """Vertical black scrim, opaque at the bottom, for text over artwork."""
    write_png('scrim_bottom.png', 4, height, lambda x, y: smoothstep(y / float(height)) * 0.9, rgb=(0, 0, 0))
    # The Live TV quick guide's edge: solid at the left fading to clear (white, so colordiffuse colours it).
    write_png('scrim_side.png', height, 4, lambda x, y: 1 - smoothstep(x / float(height)))



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
    card_mask('card_poster_mask.png', 176, 264, 18)
    card_mask('card_landscape_mask.png', 360, 202, 20)
    # Rings sit 6 px outside the card on each side.
    focus_ring('card_poster_focus.png', 188, 276, 18, 4)
    focus_ring('card_landscape_focus.png', 372, 214, 20, 4)
    # Silo's Apple TV focus: a thin rim just inside the card, at the card's size.
    focus_ring('card_poster_rim.png', 176, 264, 18, 1)
    focus_ring('card_landscape_rim.png', 360, 202, 20, 1)
    # Badges: a 2 px outline, stretched with border="8".
    focus_ring('badge_outline.png', 32, 32, 8, 2)
    badge_fill()
    menu_panel()
    epg_now()
    play_circle()
    # Silo's skip pill outline (Up Next's Skip intro), stretched with border="48".
    focus_ring('pill_ring.png', 96, 96, 48, 4)
    # Silo's season pills: a 2 px outline at the pills' own size, border="28".
    focus_ring('season_ring.png', 56, 56, 28, 2)
    pill()
    switches()
    scrim()
    # Cast photos: round, with a ring 6 px outside the photo.
    # Cast photos: a round mask, and a ring 6 px outside the photo.
    card_mask('person_mask.png', 172, 172, 86)
    focus_ring('person_ring.png', 184, 184, 92, 4)
    # The profile avatar in the menu bar, and its focus ring 4 px outside it.
    card_mask('avatar_mask.png', 56, 56, 28)
    card_scrim()
    # Silo's player buttons at rest: a 38% black disc with a 24% white ring.
    def osd_button(x, y, size=76, ring=2.0):
        disc = rounded_rect_coverage(x, y, size, size, size / 2.0)
        inner = rounded_rect_coverage(x, y, size, size, size / 2.0, inset=ring)
        ring_part = disc - inner
        alpha = ring_part * 0.24 + inner * 0.38 + ring_part * 0.38 * (1 - 0.24)
        if alpha <= 0:
            return 0.0
        grey = int(255 * ring_part * 0.24 / alpha)
        return alpha, (grey, grey, grey)
    write_png('osd_button_rest.png', 76, 76, osd_button)
    # Dialog buttons: a rounded bar inset 10 px, so neighbours in a row don't
    # touch; stretched with border="46".
    # The busy spinner: Silo's Material arc, three quarters of a 6 px ring.
    def arc(x, y, size=96.0, stroke=6.0):
        import math
        r_out, r_in = size / 2.0, size / 2.0 - stroke
        hits = 0
        for sy in range(SUB):
            for sx in range(SUB):
                px = x - 0.5 + (sx + 0.5) / SUB - size / 2.0
                py = y - 0.5 + (sy + 0.5) / SUB - size / 2.0
                d = math.hypot(px, py)
                if r_in <= d <= r_out and math.atan2(py, px) % (2 * math.pi) < 1.5 * math.pi:
                    hits += 1
        return hits / float(SUB * SUB)
    write_png('spinner_arc.png', 96, 96, arc)
    write_png('dialog_button.png', 100, 100, lambda x, y: rounded_rect_coverage(x, y, 100, 100, 36, inset=10))
    # A focused row in the player's settings list: the white bar on the
    # dialog's own colour, as a Kodi button draws only its focus texture.
    def dialog_row_focus(x, y):
        bar = rounded_rect_coverage(x, y, 100, 100, 36, inset=10)
        grey = int(0xED * bar + 0x13 * (1 - bar))
        return 1.0, (grey, int(0xED * bar + 0x14 * (1 - bar)), int(0xED * bar + 0x17 * (1 - bar)))
    write_png('dialog_row_focus.png', 100, 100, dialog_row_focus)
    # Start over (an info page's Play from beginning): a ring open at its top
    # left, an arrowhead on the open end turning it anticlockwise, and a
    # small play triangle inside.
    def start_over(x, y, size=64.0, stroke=6.0):
        import math
        c, r = size / 2.0, size * 0.34
        end = math.radians(200)  # the ring runs from here round to 290 degrees
        tip_x, tip_y = c + r * math.cos(end), c + r * math.sin(end)
        hits = 0
        for sy in range(SUB):
            for sx in range(SUB):
                px = x - 0.5 + (sx + 0.5) / SUB
                py = y - 0.5 + (sy + 0.5) / SUB
                dx, dy = px - c, py - c
                angle = math.degrees(math.atan2(dy, dx)) % 360
                ring = abs(math.hypot(dx, dy) - r) <= stroke / 2 and not 200 < angle < 290
                # Arrowhead: a triangle on the ring's end, pointing up (along the turn).
                hx, hy = px - tip_x, tip_y - py
                head = 0 <= hy <= size * 0.16 and abs(hx) <= size * 0.12 * (1 - hy / (size * 0.16))
                # Play triangle, pointing right, centred.
                tx, ty = px - c + size * 0.02, py - c
                play = -size * 0.09 <= tx <= size * 0.11 and abs(ty) <= (size * 0.11 - tx) * 0.58
                hits += ring or head or play
        return hits / float(SUB * SUB)
    write_png('start_over.png', 64, 64, start_over)
    # Silo's player skips (back 10 s, forward 30 s): an open ring with an
    # arrowhead on its top end; the skin writes the seconds inside.
    def skip_ring(x, y, forward, size=64.0, stroke=5.0):
        import math
        c, r = size / 2.0 + 2, size * 0.36
        hits = 0
        for sy in range(SUB):
            for sx in range(SUB):
                px = x - 0.5 + (sx + 0.5) / SUB
                py = y - 0.5 + (sy + 0.5) / SUB
                if forward:
                    px = size - px  # the mirror image
                dx, dy = px - c, py - c
                angle = math.degrees(math.atan2(dy, dx)) % 360
                ring = abs(math.hypot(dx, dy) - r) <= stroke / 2 and not 225 < angle < 275
                # Arrowhead at the ring's top end (275 degrees), pointing left.
                tip_x = c + r * math.cos(math.radians(275))
                tip_y = c + r * math.sin(math.radians(275))
                hx, hy = tip_x - px, py - tip_y
                head = -size * 0.02 <= hx <= size * 0.15 and abs(hy) <= size * 0.11 * (1 - hx / (size * 0.15))
                hits += ring or head
        return hits / float(SUB * SUB)
    write_png('skip_back.png', 64, 64, lambda x, y: skip_ring(x, y, False))
    write_png('skip_forward.png', 64, 64, lambda x, y: skip_ring(x, y, True))
    # Player button icons at a button's full size (Kodi stretches a radio
    # button's icon to it), so drawn in its middle: close (an X) and Silo's
    # Options (three sliders, each with a knob).
    def close_x(x, y, size=96.0, stroke=6.5):
        hits = 0
        for sy in range(SUB):
            for sx in range(SUB):
                px = x - 0.5 + (sx + 0.5) / SUB - size / 2
                py = y - 0.5 + (sy + 0.5) / SUB - size / 2
                inside = max(abs(px), abs(py)) <= size * 0.17
                diagonal = min(abs(px - py), abs(px + py)) / 1.4142 <= stroke / 2
                hits += inside and diagonal
        return hits / float(SUB * SUB)
    write_png('close.png', 96, 96, close_x)

    def sliders(x, y, size=96.0, stroke=5.0):
        knobs = ((0.36, 0.40), (0.50, 0.60), (0.64, 0.46))  # (row, knob position) as fractions
        hits = 0
        for sy in range(SUB):
            for sx in range(SUB):
                px = (x - 0.5 + (sx + 0.5) / SUB) / size
                py = (y - 0.5 + (sy + 0.5) / SUB) / size
                for row, knob in knobs:
                    line = abs(py - row) <= stroke / 2 / size and 0.32 <= px <= 0.68
                    handle = abs(py - row) <= 0.055 and abs(px - knob) <= 0.03
                    if line or handle:
                        hits += 1
                        break
        return hits / float(SUB * SUB)
    write_png('options.png', 96, 96, sliders)
    # Skyline's mark: its own shape, not Silo's (Silo's brand policy keeps
    # its three-bar logo and colours for Silo itself): a round dusk sky,
    # violet to coral, with a white city skyline across its lower half.
    DUSK_TOP, DUSK_BOTTOM, CITY = (0x6C, 0x4D, 0xF2), (0xFF, 0x86, 0x5E), (0xF7, 0xF4, 0xF2)
    buildings = ((0.10, 0.58), (0.20, 0.47), (0.30, 0.62), (0.38, 0.36), (0.48, 0.55), (0.58, 0.44),
                 (0.68, 0.60), (0.76, 0.50), (0.86, 0.64))  # (left edge, roof) as fractions, 0.10 wide

    def skyline(x, y, size=192.0):
        disc = rounded_rect_coverage(x, y, size, size, size / 2.0)
        if disc <= 0:
            return 0.0
        u, v = x / size, y / size
        sky = tuple(int(a + (b - a) * v) for a, b in zip(DUSK_TOP, DUSK_BOTTOM))
        hits = 0
        for sy in range(SUB):
            for sx in range(SUB):
                pu = (x - 0.5 + (sx + 0.5) / SUB) / size
                pv = (y - 0.5 + (sy + 0.5) / SUB) / size
                city = pv >= 0.80 or any(left <= pu < left + 0.10 and pv >= roof for left, roof in buildings)
                spire = abs(pu - 0.43) < 0.012 and 0.24 <= pv < 0.36  # one tower's mast
                hits += city or spire
        lit = hits / float(SUB * SUB)
        colour = tuple(int(c * (1 - lit) + w * lit) for c, w in zip(sky, CITY))
        return disc, colour
    write_png('skyline_mark.png', 192, 192, skyline)
    # The bar's up chevron (a tab with a sub-menu): two strokes meeting at the top.
    def chevron_up(x, y, w=56.0, h=32.0, stroke=5.0):
        hits = 0
        for sy in range(SUB):
            for sx in range(SUB):
                px = x - 0.5 + (sx + 0.5) / SUB
                py = y - 0.5 + (sy + 0.5) / SUB
                # Distance to the polyline (6, h-6) -> (w/2, 6) -> (w-6, h-6).
                import math
                def seg(ax, ay, bx, by):
                    t = max(0.0, min(1.0, ((px - ax) * (bx - ax) + (py - ay) * (by - ay)) / ((bx - ax) ** 2 + (by - ay) ** 2)))
                    return math.hypot(px - ax - t * (bx - ax), py - ay - t * (by - ay))
                d = min(seg(6, h - 6, w / 2, 6), seg(w / 2, 6, w - 6, h - 6))
                hits += d <= stroke / 2
        return hits / float(SUB * SUB)
    write_png('chevron_up.png', 56, 32, chevron_up)

    # The sub-menu's icons (Silo's dropdown): Recommended (a four-point
    # sparkle and a small one), Browse (a 2x2 grid), Collections (stacked cards).
    def sparkle(x, y, size=48.0):
        def star(px, py, cx, cy, r):
            dx, dy = abs(px - cx) / r, abs(py - cy) / r
            return dx ** 0.5 + dy ** 0.5 <= 1
        hits = 0
        for sy in range(SUB):
            for sx in range(SUB):
                px = x - 0.5 + (sx + 0.5) / SUB
                py = y - 0.5 + (sy + 0.5) / SUB
                hits += star(px, py, size * 0.42, size * 0.56, size * 0.36) or star(px, py, size * 0.78, size * 0.22, size * 0.16)
        return hits / float(SUB * SUB)
    write_png('menu_recommended.png', 48, 48, sparkle)
    write_png('menu_browse.png', 48, 48, lambda x, y: max(
        rounded_rect_coverage(x - ox, y - oy, 16, 16, 4) for ox in (6, 26) for oy in (6, 26)))
    def stack(x, y):
        back = rounded_rect_coverage(x - 14, y - 6, 28, 22, 4) - rounded_rect_coverage(x - 14, y - 6, 28, 22, 4, inset=3)
        front = rounded_rect_coverage(x - 6, y - 16, 30, 26, 4)
        return max(back if x < 8 or y < 18 or x > 42 else 0, front)
    write_png('menu_collections.png', 48, 48, stack)

    # The avatar card's icons (Silo's profile menu), drawn as shapes on a 48 px grid.
    import math
    def shape(inside):
        def alpha(x, y):
            hits = 0
            for sy in range(SUB):
                for sx in range(SUB):
                    hits += bool(inside(x - 0.5 + (sx + 0.5) / SUB, y - 0.5 + (sy + 0.5) / SUB))
            return hits / float(SUB * SUB)
        return alpha
    def person(x, y):
        head = (x - 24) ** 2 + (y - 15) ** 2 <= 8 ** 2
        body = y <= 41 and ((x - 24) / 16.0) ** 2 + ((y - 42) / 14.0) ** 2 <= 1
        return head or body
    def bookmark(x, y):
        return 12 <= x <= 36 and 6 <= y <= 42 and y <= 42 - (10 - abs(x - 24) * 10 / 12.0) * (y > 30)
    def bookmark_outline(x, y):
        """Not on the watchlist: the bookmark's outline, 3.5 px."""
        inner = 15.5 <= x <= 32.5 and 9.5 <= y <= 42 and y <= 37.5 - (6.5 - abs(x - 24) * 6.5 / 8.5) * (y > 30)
        return bookmark(x, y) and not inner
    def heart(x, y):
        u, v = (x - 24) / 17.0, (27 - y) / 17.0
        return (u * u + v * v - 1) ** 3 - u * u * v ** 3 <= 0
    def clock(x, y):
        r = math.hypot(x - 24, y - 24)
        return 15 <= r <= 19 or (22 <= x <= 26 and 12 <= y <= 26) or (22 <= x <= 33 and 22 <= y <= 26)
    def gear(x, y):
        r = math.hypot(x - 24, y - 24)
        outer = 19 if math.cos(8 * math.atan2(y - 24, x - 24)) > 0.1 else 14.5
        return 6.5 <= r <= outer
    def sign_out(x, y):
        frame = (8 <= x <= 12 and 8 <= y <= 40) or (8 <= x <= 25 and (8 <= y <= 12 or 36 <= y <= 40))
        arrow = (18 <= x <= 34 and 22 <= y <= 26) or (31 <= x <= 42 and abs(y - 24) <= (42 - x) * 0.85)
        return frame or arrow
    def magnifier(x, y):
        return 13 <= math.hypot(x - 20, y - 20) <= 17.5 or (abs((x - y)) <= 3.2 and 30 <= (x + y) / 2 <= 42)
    # Silo's Sort icons (Material SwapVert, Check, ArrowUpward/Downward).
    def seg_dist(px, py, ax, ay, bx, by):
        t = max(0.0, min(1.0, ((px - ax) * (bx - ax) + (py - ay) * (by - ay)) / float((bx - ax) ** 2 + (by - ay) ** 2)))
        return math.hypot(px - ax - t * (bx - ax), py - ay - t * (by - ay))
    def arrow(x, y, up=True):
        yy = y if up else 48 - y
        head = seg_dist(x, yy, 24, 8, 12, 20) <= 2.6 or seg_dist(x, yy, 24, 8, 36, 20) <= 2.6
        return head or (abs(x - 24) <= 2.6 and 9 <= yy <= 40)
    def swap_vert(x, y):
        def small(px, py):  # an up arrow in a 24-wide column
            head = seg_dist(px, py, 16, 8, 8, 16) <= 2.4 or seg_dist(px, py, 16, 8, 24, 16) <= 2.4
            return head or (abs(px - 16) <= 2.4 and 9 <= py <= 34)
        return small(x, y) or small(48 - x, 48 - y)
    def check(x, y):
        return seg_dist(x, y, 10, 25, 20, 35) <= 3 or seg_dist(x, y, 20, 35, 39, 14) <= 3
    for name, inside in (('sort', swap_vert), ('check', check), ('arrow_up', lambda x, y: arrow(x, y, True)),
                         ('arrow_down', lambda x, y: arrow(x, y, False))):
        write_png('%s.png' % name, 48, 48, shape(inside))
    # A sub-menu entry's default icon (none chosen in Customise home menu):
    # a list, three rows each with a dot.
    def list_rows(x, y):
        rows = (12, 24, 36)
        return any((x - 9) ** 2 + (y - r) ** 2 <= 3.4 ** 2 or (16 <= x <= 40 and abs(y - r) <= 2.4) for r in rows)
    for name, inside in (('default', list_rows), ('search', magnifier), ('profile', person), ('watchlist', bookmark), ('watchlist_add', bookmark_outline), ('favorites', heart),
                         ('history', clock), ('settings', gear), ('signout', sign_out)):
        write_png('menu_%s.png' % name, 48, 48, shape(inside))

    # The splash: a near-black with soft glows of the mark's dusk colours
    # rising from the bottom (drawn small; Kodi stretches it smoothly).
    def splash_bg(x, y, w=384.0, h=216.0):
        import math
        u, v = x / w, y / h
        rgb = [0x0D, 0x0F, 0x12]
        for (gx, gy, radius, strength, tint) in ((0.12, 1.08, 0.75, 0.40, DUSK_TOP), (0.62, 1.12, 0.45, 0.18, DUSK_BOTTOM),
                                                  (0.92, 1.0, 0.55, 0.28, (0xC2, 0x4F, 0xB8))):
            d = math.hypot((u - gx) * w / h, v - gy) / radius
            glow = strength * max(0.0, 1 - d) ** 2
            rgb = [c + (t - c) * glow for c, t in zip(rgb, tint)]
        return 1.0, tuple(int(c + 0.5) for c in rgb)
    write_png('splash_bg.png', 384, 216, splash_bg)
    person_placeholder()
    focus_ring('avatar_ring.png', 64, 64, 32, 3)
    print('Wrote', ', '.join(sorted(os.listdir(OUT))))
