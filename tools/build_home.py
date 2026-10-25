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
ROWS_TOP = 600             # Silo TV's home hero is 300 units tall

POSTER = {'width': 260, 'height': 390, 'gap': 24, 'mask': 'silo/card_poster_mask.png',
          'ring': 'silo/card_poster_focus.png', 'art': '$VAR[SiloPosterArt]'}
LANDSCAPE = {'width': 360, 'height': 202, 'gap': 24, 'mask': 'silo/card_landscape_mask.png',
             'ring': 'silo/card_landscape_focus.png', 'art': '$VAR[SiloLandscapeArt]'}


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
                    </control>''' % {'zoom': zoom, 'w': card['width'], 'h': card['height'], 'mask': card['mask'],
                                    'art': card['art'], 'pt': card['height'] - 12, 'pw': card['width'] - 24,
                                    'text': TEXT, 'ring': ring}


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
    # library, which makes Kodi reload the row.
    path = '$INFO[%s]&amp;refresh=$INFO[%s]' % (prop(key + '.path'), prop('silokodi.library_updated'))
    item_w = card['width'] + card['gap']
    item_h = card['height'] + 12
    return '''
            <control type="group">
                <height>%(group_h)d</height>
                <visible>%(rules)s</visible>
                <control type="label">
                    <left>%(x)d</left><top>0</top>
                    <width>1500</width><height>44</height>
                    <font>silo_row</font>
                    <textcolor>%(text)s</textcolor>
                    <label>$INFO[%(title)s]</label>
                </control>
                <control type="list" id="%(id)d">
                    <visible>%(rules)s</visible>
                    <left>%(lx)d</left><top>52</top>
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
        'group_h': 52 + item_h + 40, 'rules': rules, 'x': SAFE_X, 'text': TEXT, 'title': prop(key + '.title'),
        'id': list_id(page_index, slot, landscape), 'lx': SAFE_X - 6, 'lw': 1920 - SAFE_X + 6, 'item_h': item_h,
        'moves': moves(page_index, slot), 'path': path, 'item_w': item_w, 'normal': card_layout(card, False),
        'focused': card_layout(card, True, list_id(page_index, slot, landscape))}


BAR_ORDER = [9001, 9002, 9003, 9004, 9009]  # Search, Home, Movies, Series, Settings


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


def bar_down(indent='            '):
    """Down from the bar: the first row showing, on whichever page is shown
    (only one page's rows are ever visible)."""
    return ''.join(first_visible('ondown', page_rows(index, range(1, LOOKAHEAD + 1)), indent)
                   for index in range(len(PAGES)))


def build():
    rows = ''.join(row(page, index, slot, landscape)
                   for index, page in enumerate(PAGES)
                   for slot in range(1, MAX_ROWS + 1)
                   for landscape in (False, True))
    tabs = icon_tab(9001, 'icons/search.png', 'ActivateWindow(1107)')
    tabs += ''.join(tab(9002 + index, page, index) for index, page in enumerate(PAGES))
    tabs += icon_tab(9009, 'icons/settings.png', 'ActivateWindow(Settings)')
    no_rows = ' + '.join('String.IsEmpty(%s)' % prop('silo.%s.count' % page) for page in ('home',))
    return '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by tools/build_home.py: edit that, not this. -->
<window>
    <defaultcontrol always="true">4000</defaultcontrol>
    <onload condition="String.IsEmpty(Window(Home).Property(silo.home.count))">SetFocus(9002)</onload>
    <backgroundcolor>FF000000</backgroundcolor>
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
                <top>228</top>
                <width>620</width><height>160</height>
                <aspectratio align="left" aligny="bottom">keep</aspectratio>
                <fadetime>240</fadetime>
                <texture background="true">$VAR[SiloLogoArt]</texture>
            </control>
            <control type="label">
                <top>228</top>
                <width>1000</width><height>160</height>
                <aligny>bottom</aligny>
                <font>silo_title</font>
                <textcolor>%(text)s</textcolor>
                <label>$VAR[SiloTitle]</label>
            </control>
            <control type="label">
                <top>400</top>
                <width>1000</width><height>36</height>
                <font>silo_meta</font>
                <textcolor>%(text)s</textcolor>
                <label>$VAR[SiloMetaLine]</label>
            </control>
            <control type="textbox">
                <top>444</top>
                <width>860</width><height>120</height>
                <font>silo_plot</font>
                <textcolor>%(dim)s</textcolor>
                <label>$VAR[SiloPlot]</label>
                <autoscroll>false</autoscroll>
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
            <label>Sign in to Silo in SiloKodiConnect to fill this screen.</label>
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
        <control type="label">
            <right>%(x)d</right><top>%(bar_top)d</top>
            <width>300</width><height>64</height>
            <align>right</align><aligny>center</aligny>
            <font>silo_meta</font>
            <textcolor>%(dim)s</textcolor>
            <label>$INFO[System.Time]</label>
        </control>
    </controls>
</window>
''' % {'x': SAFE_X, 'text': TEXT, 'dim': TEXT_DIM, 'rows_top': ROWS_TOP, 'rows_h': 1080 - ROWS_TOP,
       'rows': rows, 'no_rows': no_rows, 'bar_top': BAR_TOP, 'tabs_top': BAR_TOP + 2, 'tabs': tabs,
       'bar_down': bar_down(), 'row_prop': prop('silo.row')}


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
    ('SiloMetaLine', [('String.IsEqual(LI.DBType,episode)', '$INFO[LI.Season,S,]$INFO[LI.Episode, E,]'
                       '$INFO[LI.Title,  ·  ,]$INFO[LI.Duration(mins),  ·  , min]'),
                      ('String.IsEqual(LI.DBType,tvshow)', '$INFO[LI.Year]$INFO[LI.Rating,  ·  ★ ,]'
                       '$INFO[LI.Mpaa,  ·  ,]'),
                      (None, '$INFO[LI.Year]$INFO[LI.Rating,  ·  ★ ,]$INFO[LI.Duration(mins),  ·  , min]'
                       '$INFO[LI.Mpaa,  ·  ,]')]),
    ('SiloPlot', [(None, '$INFO[LI.Plot]')]),
]

CARDS = '''
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


def variables():
    rows = [list_id(index, slot, landscape) for index in range(len(PAGES))
            for slot in range(1, MAX_ROWS + 1) for landscape in (False, True)]
    out = '\n    <!-- Silo Skyline (tools/build_home.py) -->' + CARDS
    for index, page in enumerate(PAGES):
        for slot in range(1, MAX_ROWS + 1):
            for landscape in (False, True):
                out += '    <expression name="SiloRow%d">%s</expression>\n' % (
                    list_id(index, slot, landscape), row_rules(page, index, slot, landscape))
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


def add_variables():
    path = os.path.join(ROOT, 'xml', 'Variables.xml')
    text = open(path, encoding='utf-8').read()
    start, end = '    <!-- Silo Skyline (tools/build_home.py) -->', '    <!-- end Silo Skyline -->\n'
    if start in text:
        text = text[:text.index(start) - 1] + text[text.index(end) + len(end):]
    text = text.replace('</includes>', variables() + '</includes>')
    open(path, 'w', encoding='utf-8').write(text)


if __name__ == '__main__':
    with open(os.path.join(ROOT, 'xml', 'Home.xml'), 'w', encoding='utf-8') as handle:
        handle.write(build())
    add_variables()
    print('Wrote xml/Home.xml and the Silo variables in xml/Variables.xml')
