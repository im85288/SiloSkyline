"""Write xml/Home.xml: the Silo TV apps' Skyline home for Kodi.

    python3 tools/build_home.py

Layout (Silo TV's 960-unit grid doubled to 1920x1080):
- a top menu bar: Silo, then Search, Home, a tab per library type, Settings;
- the focused title's artwork crisp in the top right, fading toward the left
  and bottom (media/silo/hero_mask.png);
- a marquee bottom-left of it: clear logo or title, a meta line, three lines
  of plot; it never takes focus;
- a band of rows below that owns all focus, filled from the pages and rows
  SiloKodiConnect publishes as Home window properties (silo.*).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = ('home', 'movies', 'series')
TAB_LABELS = {'home': 'Home', 'movies': 'Movies', 'series': 'Series'}
MAX_ROWS = 12
LOOKAHEAD = 4  # rows a move may skip over when they are empty

SAFE_X = 88
BAR_TOP = 56
TEXT = 'FFEDEDED'
TEXT_DIM = 'BFEDEDED'      # Silo's secondary text: 75%
TAB_DIM = 'B3EDEDED'       # Silo's dimmed bar items: 70%
BACKGROUND = 'FF0D0F12'     # Silo's near-black page
ROWS_TOP = 612             # row titles sit where Silo's do

# Cards as Silo TV draws them: dense posters (88x132 units) and backdrops
# (180x101), each with a title and a second line beneath.
POSTER = {'width': 176, 'height': 264, 'gap': 40, 'mask': 'silo/card_poster_mask.png',
          'ring': 'silo/card_poster_focus.png', 'art': '$VAR[SiloPosterArt]',
          'sub': '$VAR[SiloCardYear]'}
LANDSCAPE = {'width': 360, 'height': 202, 'gap': 40, 'mask': 'silo/card_landscape_mask.png',
             'ring': 'silo/card_landscape_focus.png', 'art': '$VAR[SiloLandscapeArt]',
             'sub': '$VAR[SiloCardEpisode]'}
CAPTION_H = 76             # title and second line under a card

# Fonts (Inter, as the Silo apps use); Font.xml gets these between markers.
FONTS = [  # name, file, size
    ('silo_tab', 'Inter-SemiBold.ttf', 30),
    ('silo_row', 'Inter-Bold.ttf', 34),
    ('silo_title', 'Inter-Bold.ttf', 76),
    ('silo_meta', 'Inter-Medium.ttf', 28),
    ('silo_plot', 'Inter-Regular.ttf', 28),
    ('silo_detail', 'Inter-Medium.ttf', 24),
    ('silo_badge', 'Inter-SemiBold.ttf', 20),
    ('silo_card_title', 'Inter-SemiBold.ttf', 26),
    ('silo_card_sub', 'Inter-Medium.ttf', 24),
    ('silo_wordmark', 'Inter-Bold.ttf', 44),
]


def prop(name):
    return 'Window(Home).Property(%s)' % name


def page_visible(page):
    current = prop('silo.page')
    if page == 'home':
        return '[String.IsEmpty(%s) | String.IsEqual(%s,home)]' % (current, current)
    return 'String.IsEqual(%s,%s)' % (current, page)


def list_id(page_index, slot, landscape):
    return 5000 + 100 * page_index + (50 if landscape else 0) + slot


def card_layout(card, focused, control_id=None):
    ring = ''
    zoom = ''
    if focused:
        ring = '''
                        <control type="image">
                            <left>0</left><top>0</top>
                            <width>%(rw)d</width><height>%(rh)d</height>
                            <texture colordiffuse="%(text)s">%(ring)s</texture>
                            <visible>Control.HasFocus(%(id)d)</visible>
                        </control>''' % {'rw': card['width'] + 12, 'rh': card['height'] + 12, 'text': TEXT,
                                         'ring': card['ring'], 'id': control_id}
        # Kodi draws every row's selected item with this layout, focused or
        # not: only the row that has focus shows the ring and the lift.
        zoom = ('\n                        <animation effect="zoom" start="100" end="104" time="160" tween="sine" '
                'center="auto" condition="Control.HasFocus(%d)">Conditional</animation>' % control_id)
    return '''
                    <control type="group">%(zoom)s
                        <control type="image">
                            <left>6</left><top>6</top>
                            <width>%(w)d</width><height>%(h)d</height>
                            <texture background="true" diffuse="%(mask)s" fallback="colors/grey.png">%(art)s</texture>
                            <aspectratio>scale</aspectratio>
                        </control>
                        <control type="progress">
                            <left>18</left><top>%(pt)d</top>
                            <width>%(pw)d</width><height>6</height>
                            <texturebg colordiffuse="66000000">colors/white.png</texturebg>
                            <midtexture colordiffuse="%(text)s">colors/white.png</midtexture>
                            <info>ListItem.PercentPlayed</info>
                            <visible>Integer.IsGreater(ListItem.PercentPlayed,0)</visible>
                        </control>
                        <control type="image">
                            <right>16</right><top>16</top>
                            <width>32</width><height>32</height>
                            <texture colordiffuse="%(text)s">OverlayWatched.png</texture>
                            <visible>Integer.IsGreater(ListItem.PlayCount,0)</visible>
                        </control>%(ring)s
                        <control type="label">
                            <left>6</left><top>%(t1)d</top>
                            <width>%(w)d</width><height>34</height>
                            <font>silo_card_title</font>
                            <textcolor>%(text)s</textcolor>
                            <label>$VAR[SiloCardTitle]</label>
                        </control>
                        <control type="label">
                            <left>6</left><top>%(t2)d</top>
                            <width>%(w)d</width><height>32</height>
                            <font>silo_card_sub</font>
                            <textcolor>%(dim)s</textcolor>
                            <label>%(sub)s</label>
                        </control>
                    </control>''' % {'zoom': zoom, 'w': card['width'], 'h': card['height'], 'mask': card['mask'],
                                    'art': card['art'], 'pt': card['height'] - 12, 'pw': card['width'] - 24,
                                    'text': TEXT, 'dim': TEXT_DIM, 'ring': ring, 'sub': card['sub'],
                                    't1': card['height'] + 20, 't2': card['height'] + 54}


def shown(target):
    """Whether a control is showing. Rows use their own rules ($EXP): Kodi
    stops refreshing Control.IsVisible() for lists inside a hidden group, so
    a Home row kept answering visible after leaving the Home page."""
    if 5000 <= target < 6000:
        return '$EXP[SiloRow%d]' % target
    return 'Control.IsVisible(%d)' % target


def row_rules(page, page_index, slot, landscape):
    key = 'silo.%s.%d' % (page, slot)
    lid = list_id(page_index, slot, landscape)
    style = ('String.IsEqual(%s,landscape)' if landscape else '!String.IsEqual(%s,landscape)') % prop(key + '.style')
    # Empty rows hide, as in Silo; Kodi still loads a list hidden this way.
    return '%s + !String.IsEmpty(%s) + %s + [Integer.IsGreater(Container(%d).NumItems,0) | Container(%d).IsUpdating]' \
        % (page_visible(page), prop(key + '.path'), style, lid, lid)


def first_visible(action, candidates, indent='                    '):
    """<action> tags that focus the first candidate showing. Kodi runs every
    tag whose condition holds, so each excludes the ones before it."""
    out = ''
    for index, target in enumerate(candidates):
        condition = ' + '.join([shown(target)] + ['!' + shown(k) for k in candidates[:index]])
        out += '\n%s<%s condition="%s">SetFocus(%d)</%s>' % (indent, action, condition, target, action)
    return out


def page_rows(page_index, slots):
    return [list_id(page_index, slot, landscape) for slot in slots for landscape in (False, True)]


def moves(page_index, slot):
    """Up and down to the nearest row that is showing (empty rows hide), and
    up from the top row to the menu bar. Kodi doesn't move focus between
    lists in groups inside a grouplist, so each row names its neighbours."""
    # Look a few rows ahead: enough to skip empty rows without bloating the XML.
    down = page_rows(page_index, range(slot + 1, min(MAX_ROWS, slot + LOOKAHEAD) + 1))
    up = page_rows(page_index, range(slot - 1, max(0, slot - LOOKAHEAD), -1))
    out = first_visible('ondown', down) + first_visible('onup', up)
    # The top row goes up to the current page's tab (a button: focusing the
    # bar's grouplist itself leaves left and right with nowhere to go).
    above = ' + '.join('!' + shown(k) for k in up)
    out += '\n                    <onup%s>SetFocus(%d)</onup>' % (' condition="%s"' % above if above else '',
                                                               9002 + page_index)
    return out


def row(page, page_index, slot, landscape):
    card = LANDSCAPE if landscape else POSTER
    key = 'silo.%s.%d' % (page, slot)
    rules = '$EXP[SiloRow%d]' % list_id(page_index, slot, landscape)
    # The library_updated suffix changes when SiloKodiConnect writes the
    # library, which makes Kodi reload the row. Kodi reads a $VAR in a content
    # path only once, when the window opens, so this must stay $INFO: a row
    # without a path logs one harmless error at start-up.
    path = '$INFO[%s]&amp;refresh=$INFO[%s]' % (prop(key + '.path'), prop('silokodi.library_updated'))
    item_w = card['width'] + card['gap']
    item_h = card['height'] + 12 + CAPTION_H
    return '''
            <control type="group">
                <height>%(group_h)d</height>
                <visible>%(rules)s</visible>
                <control type="label">
                    <left>%(x)d</left><top>0</top>
                    <width>1500</width><height>46</height>
                    <font>silo_row</font>
                    <textcolor>%(text)s</textcolor>
                    <label>$INFO[%(title)s]</label>
                </control>
                <control type="list" id="%(id)d">
                    <visible>%(rules)s</visible>
                    <left>%(lx)d</left><top>56</top>
                    <width>%(lw)d</width><height>%(item_h)d</height>
                    <orientation>horizontal</orientation>
                    <scrolltime tween="cubic" easing="out">280</scrolltime>
                    <preloaditems>2</preloaditems>
                    <onclick>Action(Info)</onclick>
                    <onfocus>SetProperty(silo.row,%(id)d,home)</onfocus>%(moves)s
                    <content target="videos">%(path)s</content>
                    <itemlayout width="%(item_w)d" height="%(item_h)d">%(normal)s
                    </itemlayout>
                    <focusedlayout width="%(item_w)d" height="%(item_h)d">%(focused)s
                    </focusedlayout>
                </control>
            </control>''' % {
        'group_h': 56 + item_h + 36, 'rules': rules, 'x': SAFE_X, 'text': TEXT, 'title': prop(key + '.title'),
        'id': list_id(page_index, slot, landscape), 'lx': SAFE_X - 6, 'lw': 1920 - SAFE_X + 6, 'item_h': item_h,
        'moves': moves(page_index, slot), 'path': path, 'item_w': item_w, 'normal': card_layout(card, False),
        'focused': card_layout(card, True, list_id(page_index, slot, landscape))}


BAR_ORDER = [9001, 9002, 9003, 9004, 9009, 9010, 9011]  # Search, Home, Movies, Series, Settings, Power, profile


def bar_moves(control_id):
    """Left, right and down for a bar button. Movies and Series can be
    hidden, so each direction takes the nearest visible button."""
    out = bar_down('                    ')
    index = BAR_ORDER.index(control_id)
    for action, neighbours in (('onright', BAR_ORDER[index + 1:]), ('onleft', BAR_ORDER[:index][::-1])):
        skipped = []
        for target in neighbours:
            condition = ' + '.join(['Control.IsVisible(%d)' % target] + ['!Control.IsVisible(%d)' % k for k in skipped])
            out += '\n                    <%s condition="%s">SetFocus(%d)</%s>' % (action, condition, target, action)
            skipped.append(target)
    return out


def tab(control_id, page, page_index):
    visible = '' if page == 'home' else \
        '\n                <visible>String.Contains(%s,%s)</visible>' % (prop('silo.pages'), page)
    return '''
            <control type="group">
                <width>%(width)d</width><height>60</height>%(visible)s
                <control type="image">
                    <width>%(width)d</width><height>60</height>
                    <texture border="30" colordiffuse="26FFFFFF">silo/pill.png</texture>
                    <visible>%(selected)s + !Control.HasFocus(%(id)d)</visible>
                </control>
                <control type="button" id="%(id)d">%(visible)s
                    <width>%(width)d</width><height>60</height>
                    <label>%(label)s</label>
                    <font>silo_tab</font>
                    <align>center</align><aligny>center</aligny>
                    <textcolor>%(dim)s</textcolor>
                    <focusedcolor>FF000000</focusedcolor>
                    <texturefocus border="30" colordiffuse="%(text)s">silo/pill.png</texturefocus>
                    <texturenofocus />
                    <onclick>SetProperty(silo.page,%(page)s,home)</onclick>
                    <onclick>ClearProperty(silo.row,home)</onclick>%(moves)s
%(focus_rows)s
                </control>
            </control>''' % {'width': 60 + 17 * len(TAB_LABELS[page]), 'visible': visible,
                            'selected': page_visible(page), 'id': control_id, 'label': TAB_LABELS[page],
                            'dim': TAB_DIM, 'text': TEXT, 'page': page,
                            'moves': bar_moves(control_id),
                            'focus_rows': first_visible('onclick', page_rows(page_index, range(1, LOOKAHEAD + 1)))}


def icon_tab(control_id, icon, action):
    return '''
            <control type="group">
                <width>60</width><height>60</height>
                <control type="button" id="%(id)d">
                    <width>60</width><height>60</height>
                    <label />
                    <texturefocus border="30" colordiffuse="%(text)s">silo/pill.png</texturefocus>
                    <texturenofocus />
                    <onclick>%(action)s</onclick>%(moves)s
                </control>
                <control type="image">
                    <left>14</left><top>14</top>
                    <width>32</width><height>32</height>
                    <texture colordiffuse="FF000000">%(icon)s</texture>
                    <visible>Control.HasFocus(%(id)d)</visible>
                </control>
                <control type="image">
                    <left>14</left><top>14</top>
                    <width>32</width><height>32</height>
                    <texture colordiffuse="%(dim)s">%(icon)s</texture>
                    <visible>!Control.HasFocus(%(id)d)</visible>
                </control>
            </control>''' % {'id': control_id, 'text': TEXT, 'action': action, 'icon': icon, 'dim': TAB_DIM,
                            'moves': bar_moves(control_id)}


def avatar():
    """The profile's avatar at the bar's right edge, as in Silo: its picture,
    or its initial in a circle; it opens SiloKodiConnect's menu."""
    has_picture = '!String.IsEmpty(%s)' % prop('silo.avatar')
    return '''
        <control type="group">
            <left>%(left)d</left><top>%(top)d</top>
            <width>64</width><height>64</height>
            <visible>!String.IsEmpty(%(name)s)</visible>
            <control type="button" id="9011">
                <width>64</width><height>64</height>
                <label />
                <texturefocus />
                <texturenofocus />
                <onclick>ActivateWindow(Videos,plugin://plugin.video.silokodiconnect/,return)</onclick>%(moves)s
            </control>
            <control type="image">
                <left>4</left><top>4</top>
                <width>56</width><height>56</height>
                <texture colordiffuse="33FFFFFF">silo/avatar_mask.png</texture>
                <visible>!%(has_picture)s</visible>
            </control>
            <control type="label">
                <left>4</left><top>4</top>
                <width>56</width><height>56</height>
                <align>center</align><aligny>center</aligny>
                <font>silo_tab</font>
                <textcolor>%(text)s</textcolor>
                <label>$INFO[%(initial)s]</label>
                <visible>!%(has_picture)s</visible>
            </control>
            <control type="image">
                <left>4</left><top>4</top>
                <width>56</width><height>56</height>
                <aspectratio>scale</aspectratio>
                <texture background="true" diffuse="silo/avatar_mask.png">$INFO[%(picture)s]</texture>
                <visible>%(has_picture)s</visible>
            </control>
            <control type="image">
                <width>64</width><height>64</height>
                <texture colordiffuse="%(text)s">silo/avatar_ring.png</texture>
                <visible>Control.HasFocus(9011)</visible>
            </control>
        </control>''' % {'left': 1920 - SAFE_X - 64, 'top': BAR_TOP, 'name': prop('silo.profile_name'),
                         'moves': bar_moves(9011), 'has_picture': has_picture, 'text': TEXT,
                         'initial': prop('silo.profile_initial'), 'picture': prop('silo.avatar')}


def bar_down(indent='            '):
    """Down from the bar: the first row showing, on whichever page is shown
    (only one page's rows are ever visible)."""
    return ''.join(first_visible('ondown', page_rows(index, range(1, LOOKAHEAD + 1)), indent)
                   for index in range(len(PAGES)))


def badge(label, height, font):
    return '''
                <control type="button">
                    <width>auto</width><height>%(h)d</height>
                    <label>%(label)s</label>
                    <font>%(font)s</font>
                    <textoffsetx>12</textoffsetx>
                    <aligny>center</aligny>
                    <enable>false</enable>
                    <disabledcolor>%(text)s</disabledcolor>
                    <texturenofocus border="8" colordiffuse="99EDEDED">silo/badge_outline.png</texturenofocus>
                    <texturefocus border="8" colordiffuse="99EDEDED">silo/badge_outline.png</texturefocus>
                    <visible>$EXP[%(shown)s]</visible>
                </control>''' % {'h': height, 'label': label, 'font': font, 'text': TEXT,
                                  'shown': label.replace('$VAR[', 'Has').rstrip(']')}


def build():
    rows = ''.join(row(page, index, slot, landscape)
                   for index, page in enumerate(PAGES)
                   for slot in range(1, MAX_ROWS + 1)
                   for landscape in (False, True))
    tabs = icon_tab(9001, 'icons/search.png', 'ActivateWindow(1107)')
    tabs += ''.join(tab(9002 + index, page, index) for index, page in enumerate(PAGES))
    tabs += icon_tab(9009, 'icons/settings.png', 'ActivateWindow(Settings)')
    # Estuary keeps the power menu on its home screen; this replaces it.
    tabs += icon_tab(9010, 'icons/power.png', 'ActivateWindow(ShutdownMenu)')
    no_rows = ' + '.join('String.IsEmpty(%s)' % prop('silo.%s.count' % page) for page in ('home',))
    return '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by tools/build_home.py: edit that, not this. -->
<window>
    <defaultcontrol always="true">4000</defaultcontrol>
    <onload condition="String.IsEmpty(Window(Home).Property(silo.home.count))">SetFocus(9002)</onload>
    <backgroundcolor>%(background)s</backgroundcolor>
    <controls>
        <!-- The focused title's artwork, crisp at the top right, fading left and down. -->
        <control type="image">
            <left>690</left><top>0</top>
            <width>1230</width><height>756</height>
            <aspectratio align="right" aligny="top">scale</aspectratio>
            <fadetime>240</fadetime>
            <texture background="true" diffuse="silo/hero_mask.png">$VAR[SiloHeroArt]</texture>
        </control>

        <!-- Marquee: never focusable; follows whichever card has focus. -->
        <control type="group">
            <left>%(x)d</left>
            <visible>!String.IsEmpty(%(row_prop)s)</visible>
            <animation effect="fade" start="0" end="100" time="240">Visible</animation>
            <control type="image">
                <top>190</top>
                <width>880</width><height>170</height>
                <aspectratio align="left" aligny="bottom">keep</aspectratio>
                <fadetime>240</fadetime>
                <texture background="true">$VAR[SiloLogoArt]</texture>
            </control>
            <control type="label">
                <top>190</top>
                <width>1100</width><height>170</height>
                <aligny>bottom</aligny>
                <font>silo_title</font>
                <textcolor>%(text)s</textcolor>
                <label>$VAR[SiloTitle]</label>
            </control>
            <!-- Age rating badge, then the info line. -->
            <control type="grouplist">
                <top>376</top>
                <width>1100</width><height>40</height>
                <orientation>horizontal</orientation>
                <itemgap>14</itemgap>
                <usecontrolcoords>true</usecontrolcoords>%(mpaa_badge)s
                <control type="label">
                    <width>auto</width><height>40</height>
                    <aligny>center</aligny>
                    <font>silo_meta</font>
                    <textcolor>%(text)s</textcolor>
                    <label>$VAR[SiloMetaLine]</label>
                </control>
            </control>
            <control type="textbox">
                <top>424</top>
                <width>860</width><height>76</height>
                <font>silo_plot</font>
                <textcolor>%(dim)s</textcolor>
                <label>$VAR[SiloPlot]</label>
                <autoscroll>false</autoscroll>
            </control>
            <control type="label">
                <top>504</top>
                <width>1000</width><height>34</height>
                <font>silo_detail</font>
                <textcolor>%(dim)s</textcolor>
                <label>$VAR[SiloDetail]</label>
            </control>
            <!-- Quality badges. -->
            <control type="grouplist">
                <top>548</top>
                <width>1000</width><height>36</height>
                <orientation>horizontal</orientation>
                <itemgap>12</itemgap>%(quality_badges)s
            </control>
        </control>

        <!-- Rows: own all focus. -->
        <control type="grouplist" id="4000">
            <left>0</left><top>%(rows_top)d</top>
            <width>1920</width><height>%(rows_h)d</height>
            <orientation>vertical</orientation>
            <itemgap>0</itemgap>
            <scrolltime tween="cubic" easing="out">300</scrolltime>
            <onup>9000</onup>%(rows)s
        </control>

        <!-- Before SiloKodiConnect has published any rows. -->
        <control type="label">
            <left>%(x)d</left><top>%(rows_top)d</top>
            <width>1600</width><height>60</height>
            <font>silo_row</font>
            <textcolor>%(dim)s</textcolor>
            <label>$VAR[SiloEmptyHome]</label>
            <visible>%(no_rows)s</visible>
        </control>

        <!-- Top menu bar. -->
        <control type="label">
            <left>%(x)d</left><top>%(bar_top)d</top>
            <width>300</width><height>64</height>
            <aligny>center</aligny>
            <font>silo_wordmark</font>
            <textcolor>%(text)s</textcolor>
            <label>Silo</label>
        </control>
        <control type="grouplist" id="9000">
            <left>0</left><top>%(tabs_top)d</top>
            <width>1920</width><height>60</height>
            <orientation>horizontal</orientation>
            <align>center</align>
            <itemgap>8</itemgap>%(bar_down)s%(tabs)s
        </control>
%(avatar)s
    </controls>
</window>
''' % {'x': SAFE_X, 'text': TEXT, 'dim': TEXT_DIM, 'rows_top': ROWS_TOP, 'rows_h': 1080 - ROWS_TOP,
       'rows': rows, 'no_rows': no_rows, 'bar_top': BAR_TOP, 'tabs_top': BAR_TOP + 2, 'tabs': tabs,
       'bar_down': bar_down(), 'avatar': avatar(), 'row_prop': prop('silo.row'), 'background': BACKGROUND,
       'mpaa_badge': badge('$VAR[SiloMpaa]', 40, 'silo_meta'),
       'quality_badges': ''.join(badge('$VAR[SiloBadge%d]' % n, 36, 'silo_badge') for n in (1, 2, 3))}


# The hero and marquee read from the row that last had focus (silo.row), so
# they stay put while the menu bar has focus, as in Silo. Each entry is a
# (condition, value) template; LI stands for that row's ListItem.
HERO = [
    ('SiloHeroArt', [('!String.IsEmpty(LI.Art(fanart))', '$INFO[LI.Art(fanart)]'),
                     ('!String.IsEmpty(LI.Art(tvshow.fanart))', '$INFO[LI.Art(tvshow.fanart)]'),
                     (None, '$INFO[LI.Art(landscape)]')]),
    ('SiloLogoArt', [('!String.IsEmpty(LI.Art(clearlogo))', '$INFO[LI.Art(clearlogo)]'),
                     (None, '$INFO[LI.Art(tvshow.clearlogo)]')]),
    # Empty when there is a logo: the logo stands in for the title.
    ('SiloTitle', [('!String.IsEmpty(LI.Art(clearlogo)) | !String.IsEmpty(LI.Art(tvshow.clearlogo))', ''),
                   ('String.IsEqual(LI.DBType,episode)', '$INFO[LI.TVShowTitle]'),
                   (None, '$INFO[LI.Label]')]),
    # Silo: "S02E02 · Song 2" for an episode, "2005 · IMDb 8.4 · Horror" otherwise.
    ('SiloMetaLine', [('String.IsEqual(LI.DBType,episode)', '$INFO[LI.Property(silo.code)]$INFO[LI.Title, · ,]'),
                      (None, '$INFO[LI.Year]$INFO[LI.Property(silo.rating), · ,]'
                       '$INFO[LI.Property(silo.genre), · ,]')]),
    ('SiloPlot', [(None, '$INFO[LI.Plot]')]),
    # "Aired Sep 25, 2026 · Tom Hardy, Helen Mirren, Pierce Brosnan"
    ('SiloDetail', [('String.IsEqual(LI.DBType,episode)', '$INFO[LI.Property(silo.aired)]'
                     '$INFO[LI.Property(silo.cast), · ,]'),
                    (None, '$INFO[LI.Property(silo.cast)]')]),
    ('SiloMpaa', [(None, '$INFO[LI.Property(silo.mpaa)]')]),
    ('SiloBadge1', [(None, '$INFO[LI.Property(silo.badge1)]')]),
    ('SiloBadge2', [(None, '$INFO[LI.Property(silo.badge2)]')]),
    ('SiloBadge3', [(None, '$INFO[LI.Property(silo.badge3)]')]),
]

CARDS = '''
    <variable name="SiloCardTitle">
        <value condition="String.IsEqual(ListItem.DBType,episode)">$INFO[ListItem.TVShowTitle]</value>
        <value>$INFO[ListItem.Label]</value>
    </variable>
    <variable name="SiloCardEpisode">
        <value condition="String.IsEqual(ListItem.DBType,episode)">$INFO[ListItem.Property(silo.code)]$INFO[ListItem.Title, • ,]</value>
        <value>$INFO[ListItem.Year]</value>
    </variable>
    <variable name="SiloCardYear">
        <value condition="String.IsEqual(ListItem.DBType,episode)">$INFO[ListItem.Property(silo.code)]</value>
        <value>$INFO[ListItem.Year]</value>
    </variable>
    <variable name="SiloPosterArt">
        <value condition="!String.IsEmpty(ListItem.Art(poster))">$INFO[ListItem.Art(poster)]</value>
        <value condition="!String.IsEmpty(ListItem.Art(tvshow.poster))">$INFO[ListItem.Art(tvshow.poster)]</value>
        <value>$INFO[ListItem.Art(thumb)]</value>
    </variable>
    <variable name="SiloLandscapeArt">
        <value condition="String.IsEqual(ListItem.DBType,episode) + !String.IsEmpty(ListItem.Art(thumb))">$INFO[ListItem.Art(thumb)]</value>
        <value condition="!String.IsEmpty(ListItem.Art(landscape))">$INFO[ListItem.Art(landscape)]</value>
        <value condition="!String.IsEmpty(ListItem.Art(fanart))">$INFO[ListItem.Art(fanart)]</value>
        <value>$INFO[ListItem.Art(tvshow.fanart)]</value>
    </variable>
'''


# Home's message before SiloKodiConnect has published any rows: it publishes
# silokodi.signed_in as soon as its service starts.
EMPTY_HOME = '''    <variable name="SiloEmptyHome">
        <value condition="!System.AddonIsEnabled(plugin.video.silokodiconnect)">Install SiloKodiConnect and sign in to Silo to fill this screen.</value>
        <value condition="String.IsEqual(Window(Home).Property(silokodi.signed_in),false)">Sign in to Silo in SiloKodiConnect to fill this screen.</value>
        <value>Loading Silo…</value>
    </variable>
'''


def variables():
    rows = [list_id(index, slot, landscape) for index in range(len(PAGES))
            for slot in range(1, MAX_ROWS + 1) for landscape in (False, True)]
    out = '\n    <!-- Silo Skyline (tools/build_home.py) -->' + CARDS
    for index, page in enumerate(PAGES):
        for slot in range(1, MAX_ROWS + 1):
            for landscape in (False, True):
                out += '    <expression name="SiloRow%d">%s</expression>\n' % (
                    list_id(index, slot, landscape), row_rules(page, index, slot, landscape))
    # Kodi's conditions can't test a $VAR, so each badge's "has text" is an
    # expression over the remembered row, like the hero variables.
    for name, item_property in (('SiloMpaa', 'silo.mpaa'), ('SiloBadge1', 'silo.badge1'),
                                ('SiloBadge2', 'silo.badge2'), ('SiloBadge3', 'silo.badge3')):
        terms = ['[String.IsEqual(%s,%d) + !String.IsEmpty(Container(%d).ListItem.Property(%s))]'
                 % (prop('silo.row'), row_id, row_id, item_property) for row_id in rows]
        out += '    <expression name="Has%s">%s</expression>\n' % (name, ' | '.join(terms))
    out += EMPTY_HOME
    for name, entries in HERO:
        out += '    <variable name="%s">\n' % name
        for row_id in rows:
            item = 'Container(%d).ListItem' % row_id
            mine = 'String.IsEqual(%s,%d)' % (prop('silo.row'), row_id)
            for condition, value in entries:
                full = mine + (' + [%s]' % condition.replace('LI', item) if condition else '')
                out += '        <value condition="%s">%s</value>\n' % (full, value.replace('LI', item))
        out += '    </variable>\n'
    return out + '    <!-- end Silo Skyline -->\n'


def add_fonts():
    path = os.path.join(ROOT, 'xml', 'Font.xml')
    text = open(path, encoding='utf-8').read()
    start, end = '\t\t<!-- Silo Skyline: Inter, as the Silo TV apps use -->\n', '\t\t<!-- end Silo Skyline -->\n'
    while start in text:
        text = text[:text.index(start)] + text[text.index(end, text.index(start)) + len(end):] \
            if end in text[text.index(start):] else text.replace(start, '', 1)
    block = start + ''.join('\t\t<font>\n\t\t\t<name>%s</name>\n\t\t\t<filename>%s</filename>\n'
                            '\t\t\t<size>%d</size>\n\t\t</font>\n' % font for font in FONTS) + end
    text = text.replace('\t</fontset>', block + '\t</fontset>')
    open(path, 'w', encoding='utf-8').write(text)


def add_variables():
    path = os.path.join(ROOT, 'xml', 'Variables.xml')
    text = open(path, encoding='utf-8').read()
    start, end = '    <!-- Silo Skyline (tools/build_home.py) -->', '    <!-- end Silo Skyline -->\n'
    if start in text:
        text = text[:text.index(start) - 1] + text[text.index(end) + len(end):]
    text = text.replace('</includes>', variables() + '</includes>')
    open(path, 'w', encoding='utf-8').write(text)


def first_row_timer():
    """A skin timer (xml/Timers.xml) that puts focus on the first row once it
    has loaded, so the hero is filled at start-up: rows load after Home opens,
    and Kodi can't focus an empty list. It waits until no row has been chosen
    and focus is on the current page's tab or off the bar (avatar included), then focuses the
    first row showing a second later; it starts again if that row was still
    loading. Timers.xml gets its conditions in full: it has no $EXP."""
    ready, focus = [], []
    for index, page in enumerate(PAGES):
        rows = [(slot, landscape) for slot in range(1, LOOKAHEAD + 1) for landscape in (False, True)]
        loaded = ' | '.join('Integer.IsGreater(Container(%d).NumItems,0)' % list_id(index, slot, landscape)
                            for slot, landscape in rows)
        ready.append('[%s + [%s] + [Control.HasFocus(%d) | [!ControlGroup(9000).HasFocus() + '
                     '!Control.HasFocus(9011)]]]'
                     % (page_visible(page), loaded, 9002 + index))
        shown_rows = [('[%s]' % row_rules(page, index, slot, landscape), list_id(index, slot, landscape))
                      for slot, landscape in rows]
        for position, (rule, target) in enumerate(shown_rows):
            condition = ' + '.join([rule] + ['![%s]' % earlier[1:-1] for earlier, _ in shown_rows[:position]])
            focus.append('        <onstop condition="%s + String.IsEmpty(%s)">SetFocus(%d)</onstop>\n'
                         % (condition, prop('silo.row'), target))
    name = 'silo_first_row'
    return (TIMER_START + '    <timer>\n'
            '        <name>%s</name>\n'
            '        <description>Focus the first Silo row once it has loaded (tools/build_home.py)</description>\n'
            '        <start reset="true">Window.IsActive(home) + String.IsEmpty(%s) + [%s]</start>\n'
            '        <stop>Integer.IsGreaterOrEqual(Skin.TimerElapsedSecs(%s),1) | !Window.IsActive(home) | '
            '!String.IsEmpty(%s)</stop>\n%s'
            '    </timer>\n' % (name, prop('silo.row'), ' | '.join(ready), name, prop('silo.row'), ''.join(focus))
            + TIMER_END)


TIMER_START, TIMER_END = '    <!-- Silo Skyline (tools/build_home.py) -->\n', '    <!-- end Silo Skyline -->\n'


def add_timer():
    path = os.path.join(ROOT, 'xml', 'Timers.xml')
    text = open(path, encoding='utf-8').read()
    if TIMER_START in text:
        text = text[:text.index(TIMER_START)] + text[text.index(TIMER_END) + len(TIMER_END):]
    text = text.replace('</timers>', first_row_timer() + '</timers>')
    open(path, 'w', encoding='utf-8').write(text)


if __name__ == '__main__':
    with open(os.path.join(ROOT, 'xml', 'Home.xml'), 'w', encoding='utf-8') as handle:
        handle.write(build())
    add_variables()
    add_fonts()
    add_timer()
    print('Wrote xml/Home.xml, the Silo variables in xml/Variables.xml, its fonts in xml/Font.xml and its '
          'start-up focus timer in xml/Timers.xml')
