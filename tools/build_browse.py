"""Write xml/MyVideoNav.xml: Kodi's video browsing window in Silo's style.

    python3 tools/build_browse.py

Browse on a show and the menu behind the profile avatar open this window. It
gets a header (the folder's name and how many items it holds) and one view
per kind of content, each shown only for its content so Kodi always lands on
the right one: a poster grid for films, shows, sets and seasons (51), episode
stills with their details (52), and a list of pills for everything else, such
as an add-on's menu or a folder (50). Estuary's side menu of sorting and view
options is gone, as Silo has none. Films and shows get an A-Z bar (60) right
of the grid, which SiloKodiConnect answers by jumping to the letter.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_home import wordmark, BACKGROUND, ROOT, SAFE_X, TEXT, TEXT_DIM, TITLE_DIM  # noqa: E402

GRID = 'Container.Content(movies) | Container.Content(tvshows) | Container.Content(sets) | Container.Content(seasons)'
EPISODES = 'Container.Content(episodes)'
VIEWS_TOP = 200

# Poster grid: Silo's 2:3 cards, seven to a row.
POSTER_W, POSTER_H, POSTER_GAP = 200, 300, 36
POSTER_ITEM_H = POSTER_H + 12 + 76 + 24
# A-Z bar right of the poster grid, for films and shows: a letter asks
# SiloKodiConnect (NotifyAll) to jump the grid to the first title from it.
JUMP_ID = 60
LETTERS = ['#'] + [chr(c) for c in range(ord('A'), ord('Z') + 1)]
JUMP_ITEM_H = 32
JUMP_W = 68
JUMP_BAR = '[Container.Content(movies) | Container.Content(tvshows)] + Integer.IsGreater(Container.NumItems,20)'
# Episode list: a 16:9 still, then the episode's details beside it.
STILL_W, STILL_H = 360, 202
EPISODE_ITEM_H = STILL_H + 12 + 32


def poster(focused, view_id):
    ring = '''
                    <control type="image">
                        <width>%(rw)d</width><height>%(rh)d</height>
                        <texture colordiffuse="%(text)s">silo/card_poster_focus.png</texture>
                        <visible>Control.HasFocus(%(id)d)</visible>
                    </control>''' % {'rw': POSTER_W + 12, 'rh': POSTER_H + 12, 'text': TEXT, 'id': view_id} \
        if focused else ''
    # Silo dims a card's title until the card has focus.
    title_color = TITLE_DIM
    focused_title = '''
                    <control type="label">
                        <left>6</left><top>%(t1)d</top>
                        <width>%(w)d</width><height>34</height>
                        <font>silo_card_title</font>
                        <textcolor>%(text)s</textcolor>
                        <label>$VAR[SiloBrowseLabel]</label>
                        <scroll>true</scroll>
                        <scrollspeed>50</scrollspeed><scrollsuffix>      </scrollsuffix>
                        <visible>Control.HasFocus(%(id)d)</visible>
                    </control>''' % {'t1': POSTER_H + 20, 'w': POSTER_W, 'text': TEXT, 'id': view_id} \
        if focused else ''
    dim_visible = '\n                        <visible>!Control.HasFocus(%d)</visible>' % view_id if focused else ''
    return '''
                    <control type="image">
                        <left>6</left><top>6</top>
                        <width>%(w)d</width><height>%(h)d</height>
                        <aspectratio>scale</aspectratio>
                        <texture background="true" diffuse="silo/card_poster_mask.png" fallback="colors/grey.png">$VAR[SiloBrowsePoster]</texture>
                    </control>
                    <control type="image">
                        <left>6</left><top>6</top>
                        <width>%(w)d</width><height>%(h)d</height>
                        <texture diffuse="silo/card_poster_mask.png">silo/card_scrim.png</texture>
                        <visible>Integer.IsGreater(ListItem.PercentPlayed,0)</visible>
                    </control>
                    <control type="progress">
                        <left>18</left><top>%(h)d</top>
                        <width>%(pw)d</width><height>6</height>
                        <texturebg colordiffuse="33FFFFFF">colors/white.png</texturebg>
                        <midtexture colordiffuse="%(text)s">colors/white.png</midtexture>
                        <info>ListItem.PercentPlayed</info>
                        <visible>Integer.IsGreater(ListItem.PercentPlayed,0)</visible>
                    </control>
                    <control type="image">
                        <left>%(tick)d</left><top>16</top>
                        <width>32</width><height>32</height>
                        <texture colordiffuse="%(text)s">OverlayWatched.png</texture>
                        <visible>Integer.IsGreater(ListItem.PlayCount,0) | [Integer.IsGreater(ListItem.Property(TotalEpisodes),0) + Integer.IsEqual(ListItem.Property(UnWatchedEpisodes),0)]</visible>
                    </control>%(ring)s
                    <control type="label">
                        <left>6</left><top>%(t1)d</top>
                        <width>%(w)d</width><height>34</height>
                        <font>silo_card_title</font>
                        <textcolor>%(title_color)s</textcolor>
                        <label>$VAR[SiloBrowseLabel]</label>%(dim_visible)s
                    </control>%(focused_title)s
                    <control type="label">
                        <left>6</left><top>%(t2)d</top>
                        <width>%(w)d</width><height>32</height>
                        <font>silo_card_sub</font>
                        <textcolor>%(dim)s</textcolor>
                        <label>$VAR[SiloBrowseSub]</label>
                    </control>''' % {'w': POSTER_W, 'h': POSTER_H, 'pw': POSTER_W - 24, 'text': TEXT, 'dim': TEXT_DIM,
                                     'tick': POSTER_W - 32, 'ring': ring, 't1': POSTER_H + 20, 't2': POSTER_H + 54,
                                     'title_color': title_color, 'dim_visible': dim_visible,
                                     'focused_title': focused_title}


# Collections (SiloKodiConnect's, which carry silo.fan1-3): Silo's fan card,
# three columns. Its first titles' posters fanned at the left (-8, -1 and
# +7 degrees), its name and count at the right.
FANS = 'Container.Content(sets) + String.IsEqual(Container.Property(silo.fans),true)'
# Genres: Silo's chip cloud (capsules, six to a row).
CHIPS = 'Container.Content(genres)'
CHIP_W, CHIP_H, CHIP_GAP = 260, 64, 16
FAN_W, FAN_H, FAN_GAP = 548, 280, 28
MINI_W, MINI_H = 124, 186


def chip(focused, view_id):
    lit = 'Control.HasFocus(%d)' % view_id
    def body(fill, colour, visible):
        return '''
                    <control type="image">
                        <width>%(w)d</width><height>%(h)d</height>
                        <texture border="32" colordiffuse="%(fill)s">silo/pill.png</texture>%(v)s
                    </control>
                    <control type="label">
                        <left>24</left><width>%(lw)d</width><height>%(h)d</height>
                        <align>center</align><aligny>center</aligny>
                        <font>silo_meta</font>
                        <textcolor>%(colour)s</textcolor>
                        <label>$INFO[ListItem.Label]</label>%(v)s
                    </control>''' % {'w': CHIP_W, 'h': CHIP_H, 'lw': CHIP_W - 48, 'fill': fill, 'colour': colour,
                                     'v': '\n                        <visible>%s</visible>' % visible if visible else ''}
    if not focused:
        return body('12FFFFFF', TEXT, '')
    return body(TEXT, 'FF000000', lit) + body('12FFFFFF', TEXT, '!' + lit)


def fan_card(focused, view_id):
    lit = 'Control.HasFocus(%d)' % view_id
    minis = ''
    # Back to front: the right one, the left one, the middle one on top.
    for number, x, angle in ((3, 160, 7), (1, 36, -8), (2, 98, -1)):
        minis += '''
                    <control type="image">
                        <left>%(x)d</left><top>%(y)d</top><width>%(w)d</width><height>%(h)d</height>
                        <aspectratio>scale</aspectratio>
                        <texture background="true" diffuse="silo/card_poster_mask.png" fallback="colors/grey.png">$INFO[ListItem.Property(silo.fan%(n)d)]</texture>
                        <animation effect="rotate" end="%(a)d" center="auto" time="0" condition="true">Conditional</animation>
                        <visible>!String.IsEmpty(ListItem.Property(silo.fan%(n)d))</visible>
                    </control>''' % {'x': x, 'y': (FAN_H - MINI_H) // 2 + 6, 'w': MINI_W, 'h': MINI_H, 'n': number,
                                     'a': -angle}
    ring = '''
                    <control type="image">
                        <width>%d</width><height>%d</height>
                        <texture border="20" colordiffuse="%s">silo/card_landscape_focus.png</texture>
                        <visible>%s</visible>
                    </control>''' % (FAN_W + 12, FAN_H + 12, TEXT, lit) if focused else ''
    zoom = ('\n                    <animation effect="zoom" start="100" end="104" center="auto" time="160" '
            'tween="sine" easing="out" condition="%s">Conditional</animation>' % lit) if focused else ''
    return '''
                <control type="group">%(zoom)s
                    <control type="image">
                        <left>6</left><top>6</top><width>%(w)d</width><height>%(h)d</height>
                        <texture border="24" colordiffuse="FF1E2024">silo/card_landscape_mask.png</texture>
                    </control>%(minis)s
                    <control type="textbox">
                        <left>%(tx)d</left><top>%(ty)d</top><width>%(tw)d</width><height>132</height>
                        <font>silo_row</font>
                        <textcolor>%(text)s</textcolor>
                        <label>$INFO[ListItem.Label]</label>
                    </control>
                    <control type="label">
                        <left>%(tx)d</left><top>%(cy)d</top><width>%(tw)d</width><height>32</height>
                        <font>silo_badge</font>
                        <textcolor>99EDEDED</textcolor>
                        <label>[UPPERCASE]$INFO[ListItem.Property(silo.count),, titles][/UPPERCASE]</label>
                    </control>%(ring)s
                </control>''' % {'zoom': zoom, 'w': FAN_W, 'h': FAN_H, 'minis': minis, 'tx': 292, 'ty': 50,
                                 'tw': FAN_W - 292 - 20, 'cy': FAN_H - 62, 'text': TEXT, 'ring': ring}


def episode(focused, view_id):
    ring = '''
                    <control type="image">
                        <width>%(rw)d</width><height>%(rh)d</height>
                        <texture colordiffuse="%(text)s">silo/card_landscape_focus.png</texture>
                        <visible>Control.HasFocus(%(id)d)</visible>
                    </control>''' % {'rw': STILL_W + 12, 'rh': STILL_H + 12, 'text': TEXT, 'id': view_id} \
        if focused else ''
    title_color = TEXT if focused else TITLE_DIM
    return '''
                    <control type="image">
                        <left>6</left><top>6</top>
                        <width>%(w)d</width><height>%(h)d</height>
                        <aspectratio>scale</aspectratio>
                        <texture background="true" diffuse="silo/card_landscape_mask.png" fallback="colors/grey.png">$INFO[ListItem.Art(thumb)]</texture>
                    </control>
                    <control type="image">
                        <left>6</left><top>6</top>
                        <width>%(w)d</width><height>%(h)d</height>
                        <texture diffuse="silo/card_landscape_mask.png">silo/card_scrim.png</texture>
                        <visible>Integer.IsGreater(ListItem.PercentPlayed,0)</visible>
                    </control>
                    <control type="progress">
                        <left>20</left><top>%(h)d</top>
                        <width>%(pw)d</width><height>6</height>
                        <texturebg colordiffuse="33FFFFFF">colors/white.png</texturebg>
                        <midtexture colordiffuse="%(text)s">colors/white.png</midtexture>
                        <info>ListItem.PercentPlayed</info>
                        <visible>Integer.IsGreater(ListItem.PercentPlayed,0)</visible>
                    </control>
                    <control type="image">
                        <left>%(tick)d</left><top>16</top>
                        <width>32</width><height>32</height>
                        <texture colordiffuse="%(text)s">OverlayWatched.png</texture>
                        <visible>Integer.IsGreater(ListItem.PlayCount,0)</visible>
                    </control>%(ring)s
                    <control type="label">
                        <left>%(x)d</left><top>14</top>
                        <width>1100</width><height>40</height>
                        <font>silo_meta</font>
                        <textcolor>%(title_color)s</textcolor>
                        <label>$VAR[SiloBrowseEpisodeTitle]</label>
                    </control>
                    <control type="label">
                        <left>%(x)d</left><top>58</top>
                        <width>1100</width><height>32</height>
                        <font>silo_detail</font>
                        <textcolor>%(dim)s</textcolor>
                        <label>$INFO[ListItem.Duration(mins),, min]$INFO[ListItem.Premiered, · ,]</label>
                    </control>
                    <control type="textbox">
                        <left>%(x)d</left><top>100</top>
                        <width>1100</width><height>60</height>
                        <font>silo_detail</font>
                        <textcolor>%(dim)s</textcolor>
                        <label>$INFO[ListItem.Plot]</label>
                    </control>''' % {'w': STILL_W, 'h': STILL_H, 'pw': STILL_W - 28, 'text': TEXT, 'dim': TEXT_DIM,
                                     'tick': STILL_W - 32, 'ring': ring, 'x': STILL_W + 52, 'title_color': title_color}


def jump_bar(left):
    """The A-Z bar: the selected title's letter lit, the focused one a pill."""
    current = 'String.IsEqual(ListItem.Label,Container(51).ListItem.SortLetter)'
    items = ''.join('''
                <item>
                    <label>%s</label>
                    <onclick>NotifyAll(silokodi,jump.51.%s)</onclick>
                </item>''' % (letter, letter) for letter in LETTERS)
    letter = '''
                    <control type="label">
                        <width>%(w)d</width><height>%(h)d</height>
                        <align>center</align><aligny>center</aligny>
                        <font>silo_detail</font>
                        <textcolor>%(color)s</textcolor>
                        <label>$INFO[ListItem.Label]</label>%(visible)s
                    </control>'''
    shown = '\n                        <visible>%s</visible>'
    layout = (letter % {'w': JUMP_W, 'h': JUMP_ITEM_H, 'color': TEXT, 'visible': shown % current}
              + letter % {'w': JUMP_W, 'h': JUMP_ITEM_H, 'color': '66EDEDED', 'visible': shown % ('!' + current)})
    # Kodi draws the selected letter's focused layout whether or not the bar
    # has focus: the pill only while it has.
    has_focus = 'Control.HasFocus(%d)' % JUMP_ID
    focused = '''
                    <control type="image">
                        <left>%(x)d</left><top>0</top>
                        <width>%(h)d</width><height>%(h)d</height>
                        <texture border="15" colordiffuse="%(text)s">silo/pill.png</texture>
                        <visible>%(focus)s</visible>
                    </control>''' % {'x': (JUMP_W - JUMP_ITEM_H) // 2, 'h': JUMP_ITEM_H, 'text': TEXT, 'focus': has_focus} \
        + letter % {'w': JUMP_W, 'h': JUMP_ITEM_H, 'color': 'FF000000', 'visible': shown % has_focus} \
        + letter % {'w': JUMP_W, 'h': JUMP_ITEM_H, 'color': TEXT,
                    'visible': shown % ('!%s + %s' % (has_focus, current))} \
        + letter % {'w': JUMP_W, 'h': JUMP_ITEM_H, 'color': '66EDEDED',
                    'visible': shown % ('!%s + !%s' % (has_focus, current))}
    return '''
        <!-- A-Z: jump the poster grid to a letter (SiloKodiConnect's jump.py). -->
        <control type="list" id="%(id)d">
            <left>%(x)d</left><top>%(top)d</top>
            <width>%(w)d</width><height>%(h)d</height>
            <orientation>vertical</orientation>
            <onleft>51</onleft>
            <visible>$EXP[SiloBrowseGrid] + %(bar)s</visible>
            <itemlayout width="%(w)d" height="%(ih)d">%(layout)s
            </itemlayout>
            <focusedlayout width="%(w)d" height="%(ih)d">%(focused)s
            </focusedlayout>
            <content>%(items)s
            </content>
        </control>''' % {'id': JUMP_ID, 'x': left, 'top': VIEWS_TOP + 8, 'w': JUMP_W,
                         'h': JUMP_ITEM_H * len(LETTERS), 'ih': JUMP_ITEM_H, 'bar': JUMP_BAR,
                         'layout': layout, 'focused': focused, 'items': items}


ROW_W, ROW_H, CARD_H = 1110, 104, 92
MENU_ICON = 'Property(silo.menu.icon)'
PROFILE = 'String.IsEqual(ListItem.Property(silo.menu.icon),profile)'
HAS_ICON = '[!String.IsEmpty(ListItem.%s) | !String.StartsWith(ListItem.Icon,Default)]' % MENU_ICON
# Kodi can't test a $VAR, so "has a description" checks what SiloRowDescription reads.
HAS_TEXT = ('[!String.IsEmpty(ListItem.Property(silo.menu.description)) | !String.IsEmpty(ListItem.Plot) | %s]'
            % PROFILE)
# The skin's icons have different margins: each menu icon's box, so the
# glyphs come out about the same size (the rest: ListItem.Icon, 48).
ICON_SIZES = {44: ('sync', 'remove'), 50: ('rewrite',), 56: ('play',), 80: ('rows', 'libraries', 'signout')}


def pill_row(focused, view_id):
    """One row of the list view (add-on menus, folders): a rounded card with
    an icon tile, the label and a one-line description; white when focused.
    SiloKodiConnect's profile row shows the avatar instead of an icon."""
    has_focus = 'Control.HasFocus(%d)' % view_id if focused else 'false'
    fg = 'FF000000'
    def text(colour, condition):
        return '''
                    <control type="label">
                        <left>%(lx)d</left><top>%(t1)d</top>
                        <width>%(w)d</width><height>40</height>
                        <aligny>center</aligny>
                        <font>silo_meta</font>
                        <textcolor>%(colour)s</textcolor>
                        <label>$INFO[ListItem.Label]</label>
                        <visible>%(cond)s + %(has_text)s</visible>
                    </control>
                    <control type="label">
                        <left>%(lx)d</left><top>%(t2)d</top>
                        <width>%(w)d</width><height>32</height>
                        <aligny>center</aligny>
                        <font>silo_detail</font>
                        <textcolor>%(dim)s</textcolor>
                        <label>$VAR[SiloRowDescription]</label>
                        <visible>%(cond)s + %(has_text)s</visible>
                    </control>
                    <control type="label">
                        <left>%(lx)d</left><top>0</top>
                        <width>%(w)d</width><height>%(ch)d</height>
                        <aligny>center</aligny>
                        <font>silo_meta</font>
                        <textcolor>%(colour)s</textcolor>
                        <label>$INFO[ListItem.Label]</label>
                        <visible>%(cond)s + !%(has_text)s</visible>
                    </control>
                    <control type="label">
                        <left>%(l2x)d</left><top>0</top>
                        <width>220</width><height>%(ch)d</height>
                        <align>right</align><aligny>center</aligny>
                        <font>silo_detail</font>
                        <textcolor>%(colour)s</textcolor>
                        <label>$INFO[ListItem.Label2]</label>
                        <visible>%(cond)s</visible>
                    </control>''' % {'lx': 112, 't1': 12, 't2': 50, 'w': ROW_W - 112 - 260, 'colour': colour,
                                 'dim': '99000000' if colour == fg else TEXT_DIM, 'cond': condition, 'has_text': HAS_TEXT,
                                 'ch': CARD_H, 'l2x': ROW_W - 250}
    def icon(colour, condition):
        named = ' | '.join('String.IsEqual(ListItem.%s,%s)' % (MENU_ICON, key)
                           for keys in ICON_SIZES.values() for key in keys)
        boxes = [(size, '[%s]' % ' | '.join('String.IsEqual(ListItem.%s,%s)' % (MENU_ICON, key) for key in keys))
                 for size, keys in ICON_SIZES.items()]
        boxes.append((48, '!%s + !%s + [%s]' % (PROFILE, '[%s]' % named, HAS_ICON)))
        return ''.join('''
                    <control type="image">
                        <left>%(x)d</left><top>%(y)d</top><width>%(s)d</width><height>%(s)d</height>
                        <aspectratio>keep</aspectratio>
                        <texture colordiffuse="%(colour)s">$VAR[SiloRowIcon]</texture>
                        <visible>%(cond)s + %(which)s</visible>
                    </control>''' % {'x': 54 - size // 2, 'y': (CARD_H - size) // 2, 's': size, 'colour': colour,
                                 'cond': condition, 'which': which} for size, which in boxes)
    return '''
                    <control type="image">
                        <width>%(rw)d</width><height>%(ch)d</height>
                        <texture border="24" colordiffuse="F21C1F24">silo/card_landscape_mask.png</texture>
                        <visible>!%(focus)s</visible>
                    </control>
                    <control type="image">
                        <width>%(rw)d</width><height>%(ch)d</height>
                        <texture border="24" colordiffuse="%(text)s">silo/card_landscape_mask.png</texture>
                        <visible>%(focus)s</visible>
                    </control>
                    <!-- SiloKodiConnect's profile row: the profile's avatar. -->
                    <control type="image">
                        <left>24</left><top>%(at)d</top><width>60</width><height>60</height>
                        <texture background="true" diffuse="silo/avatar_mask.png">$INFO[Window(Home).Property(silo.avatar)]</texture>
                        <visible>%(profile)s</visible>
                    </control>%(icon_fg)s%(icon_bg)s%(text_fg)s%(text_bg)s''' % {
        'rw': ROW_W, 'ch': CARD_H, 'text': TEXT, 'focus': has_focus, 'at': (CARD_H - 60) // 2, 'profile': PROFILE,
        'icon_fg': icon(fg, has_focus), 'icon_bg': icon(TEXT, '!' + has_focus),
        'text_fg': text(fg, has_focus), 'text_bg': text(TEXT, '!' + has_focus)}

def build():
    poster_item_w = POSTER_W + POSTER_GAP
    return '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by tools/build_browse.py: edit that, not this. -->
<window>
    <!-- Back from a trailer started from an info page (Kodi leaves it playing): stop it, which reopens the page. -->
    <onload condition="Player.HasVideo + !String.IsEmpty(Window(Home).Property(silokodi.trailer_playing))">PlayerControl(Stop)</onload>
    <defaultcontrol always="true">50</defaultcontrol>
    <backgroundcolor>%(background)s</backgroundcolor>
    <views>50,51,52,53,54</views>
    <controls>
        <control type="image">
            <left>0</left><top>0</top><width>1920</width><height>1080</height>
            <texture colordiffuse="%(background)s">colors/white.png</texture>
        </control>
        <!-- The focused title's artwork, faint in the top right, as on Silo's pages. -->
        <control type="image">
            <!-- 16:9 like the artwork, so Kodi draws it whole: cropped to fit,
                 the fade mask no longer lines up and the left edge shows. -->
            <left>576</left><top>0</top>
            <width>1344</width><height>756</height>
            <aspectratio>stretch</aspectratio>
            <fadetime>240</fadetime>
            <texture background="true" colordiffuse="59FFFFFF" diffuse="silo/hero_mask.png">$VAR[SiloBrowseArt]</texture>
        </control>

        <!-- The shared frame (tools/build_frame.py): where you are and the clock. -->
        <include content="SiloFrame">
            <param name="title">$VAR[SiloBrowseTitle]</param>
            <param name="sub">$VAR[SiloBrowseFacts]</param>
        </include>

        <!-- Everything else: a list of pills. -->
        <control type="list" id="50">
            <left>%(lx)d</left><top>%(views_top)d</top>
            <width>1110</width><height>%(views_h)d</height>
            <orientation>vertical</orientation>
            <scrolltime tween="cubic" easing="out">240</scrolltime>
            <viewtype label="List">list</viewtype>
            <visible>!$EXP[SiloBrowseGrid] + !$EXP[SiloBrowseEpisodes] + !$EXP[SiloBrowseFans] + !$EXP[SiloBrowseChips]</visible>
            <itemlayout width="1110" height="%(row_h)d">%(row)s
            </itemlayout>
            <focusedlayout width="1110" height="%(row_h)d">%(row_focused)s
            </focusedlayout>
        </control>

        <!-- Films, shows, sets and seasons: a poster grid. -->
        <control type="panel" id="51">
            <left>%(gx)d</left><top>%(views_top)d</top>
            <width>%(gw)d</width><height>%(views_h)d</height>
            <orientation>vertical</orientation>
            <scrolltime tween="cubic" easing="out">280</scrolltime>
            <viewtype label="Posters">poster</viewtype>
            <onright condition="%(bar)s">%(jump)d</onright>
            <visible>$EXP[SiloBrowseGrid]</visible>
            <itemlayout width="%(pw)d" height="%(ph)d">%(poster)s
            </itemlayout>
            <focusedlayout width="%(pw)d" height="%(ph)d">%(poster_focused)s
            </focusedlayout>
        </control>
%(jump_bar)s

        <!-- Genres: Silo's chips. -->
        <control type="panel" id="54">
            <left>%(gx)d</left><top>%(views_top)d</top>
            <width>%(gw)d</width><height>%(views_h)d</height>
            <orientation>vertical</orientation>
            <scrolltime tween="cubic" easing="out">240</scrolltime>
            <viewtype label="Genres">panel</viewtype>
            <visible>$EXP[SiloBrowseChips]</visible>
            <itemlayout width="%(cw)d" height="%(ch)d">%(chip)s
            </itemlayout>
            <focusedlayout width="%(cw)d" height="%(ch)d">%(chip_focused)s
            </focusedlayout>
        </control>

        <!-- Silo's collections: fan cards. -->
        <control type="panel" id="53">
            <left>%(gx)d</left><top>%(views_top)d</top>
            <width>%(gw)d</width><height>%(views_h)d</height>
            <orientation>vertical</orientation>
            <scrolltime tween="cubic" easing="out">280</scrolltime>
            <viewtype label="Collections">panel</viewtype>
            <visible>$EXP[SiloBrowseFans]</visible>
            <itemlayout width="%(fw)d" height="%(fh)d">%(fan)s
            </itemlayout>
            <focusedlayout width="%(fw)d" height="%(fh)d">%(fan_focused)s
            </focusedlayout>
        </control>

        <!-- Episodes: stills with their details. -->
        <control type="list" id="52">
            <left>%(gx)d</left><top>%(views_top)d</top>
            <width>%(ew)d</width><height>%(views_h)d</height>
            <orientation>vertical</orientation>
            <scrolltime tween="cubic" easing="out">280</scrolltime>
            <viewtype label="Episodes">list</viewtype>
            <visible>$EXP[SiloBrowseEpisodes]</visible>
            <itemlayout width="%(ew)d" height="%(eh)d">%(episode)s
            </itemlayout>
            <focusedlayout width="%(ew)d" height="%(eh)d">%(episode_focused)s
            </focusedlayout>
        </control>
        <!-- A trailer from an info page: its cover (Includes_SiloFrame.xml). -->
        <include>SiloTrailerCover</include>
    </controls>
</window>
''' % {'wordmark': wordmark(SAFE_X, 56), 'background': BACKGROUND, 'x': SAFE_X, 'text': TEXT, 'dim': TEXT_DIM, 'lx': SAFE_X - 36,
       'views_top': VIEWS_TOP, 'views_h': 1080 - VIEWS_TOP, 'gx': SAFE_X - 6,
       'gw': 1920 - 2 * (SAFE_X - 6), 'pw': poster_item_w, 'ph': POSTER_ITEM_H,
       'ew': 1920 - 2 * (SAFE_X - 6), 'eh': EPISODE_ITEM_H,
       'row': pill_row(False, 50), 'row_h': ROW_H, 'row_focused': pill_row(True, 50),
       'poster': poster(False, 51), 'poster_focused': poster(True, 51),
       'episode': episode(False, 52), 'episode_focused': episode(True, 52),
       'bar': JUMP_BAR, 'jump': JUMP_ID, 'jump_bar': jump_bar(SAFE_X - 6 + 7 * poster_item_w + 30),
       'cw': CHIP_W + CHIP_GAP, 'ch': CHIP_H + CHIP_GAP, 'chip': chip(False, 54), 'chip_focused': chip(True, 54),
       'fw': FAN_W + FAN_GAP, 'fh': FAN_H + FAN_GAP, 'fan': fan_card(False, 53), 'fan_focused': fan_card(True, 53)}


VARIABLES = '''
    <!-- Silo Skyline browse (tools/build_browse.py) -->
    <expression name="SiloBrowseFans">%(fans)s</expression>
    <expression name="SiloBrowseChips">%(chips)s</expression>
    <expression name="SiloBrowseGrid">[%(grid)s] + !$EXP[SiloBrowseFans]</expression>
    <expression name="SiloBrowseEpisodes">%(episodes)s</expression>
    <variable name="SiloBrowseFacts">
        <value condition="Integer.IsGreater(Container.NumItems,0) + [$EXP[SiloBrowseGrid] | $EXP[SiloBrowseEpisodes]]">$INFO[Container.NumItems,, titles]</value>
        <value condition="$EXP[SiloBrowseFans]">$INFO[Container.NumItems,, collections]</value>
        <value condition="$EXP[SiloBrowseChips]">$INFO[Container.NumItems,, genres]</value>
        <value>$INFO[Window(Home).Property(silo.library.facts)]</value>
    </variable>
    <variable name="SiloBrowseTitle">
        <value condition="String.IsEqual(Container.FolderPath,plugin://plugin.video.silokodiconnect/)">SiloKodiConnect</value>
        <value condition="!String.IsEmpty(Container.PluginCategory)">$INFO[Container.PluginCategory]</value>
        <value condition="String.StartsWith(Container.FolderPath,videodb://movies/titles/)">Movies</value>
        <value condition="String.StartsWith(Container.FolderPath,videodb://tvshows/titles/) + Container.Content(tvshows)">Series</value>
        <value condition="Container.Content(episodes) + String.IsEqual(Container.FolderName,Container.ShowTitle)">$INFO[Container.ShowTitle]</value>
        <value condition="!String.IsEmpty(Container.ShowTitle) + Container.Content(episodes)">$INFO[Container.ShowTitle] · $INFO[Container.FolderName]</value>
        <value>$INFO[Container.FolderName]</value>
    </variable>
    <!-- Kodi's "* All seasons" folder: the show's poster, and Silo's wording. -->
    <variable name="SiloBrowsePoster">
        <value condition="!String.IsEmpty(ListItem.Art(poster))">$INFO[ListItem.Art(poster)]</value>
        <value condition="!String.IsEmpty(ListItem.Art(tvshow.poster))">$INFO[ListItem.Art(tvshow.poster)]</value>
        <value>$INFO[Container.Art(tvshow.poster)]</value>
    </variable>
    <variable name="SiloBrowseLabel">
        <value condition="Container.Content(seasons) + String.StartsWith(ListItem.Label,*)">All episodes</value>
        <value>$INFO[ListItem.Label]</value>
    </variable>
    <variable name="SiloBrowseSub">
        <value condition="!String.IsEmpty(ListItem.Property(silo.count))">$INFO[ListItem.Property(silo.count),, titles]</value>
        <value condition="Container.Content(seasons) + Integer.IsGreater(ListItem.Property(TotalEpisodes),0)">$INFO[ListItem.Property(TotalEpisodes),, episodes]</value>
        <value condition="Container.Content(tvshows) + Integer.IsGreater(ListItem.Property(TotalSeasons),0)">$INFO[ListItem.Year]$INFO[ListItem.Property(TotalSeasons), · , seasons]</value>
        <value>$INFO[ListItem.Year]</value>
    </variable>
    <variable name="SiloBrowseEpisodeTitle">
        <value condition="Integer.IsGreater(ListItem.Episode,0) + String.IsEmpty(Container.ShowTitle) + !String.IsEmpty(ListItem.TVShowTitle)">$INFO[ListItem.TVShowTitle] · S$INFO[ListItem.Season] · E$INFO[ListItem.Episode]$INFO[ListItem.Title, · ,]</value>
        <value condition="Integer.IsGreater(ListItem.Episode,0)">S$INFO[ListItem.Season] · E$INFO[ListItem.Episode]$INFO[ListItem.Title, · ,]</value>
        <value>$INFO[ListItem.Label]</value>
    </variable>
    <!-- List rows: SiloKodiConnect's menu names an icon of the skin's own. -->
    <variable name="SiloRowIcon">
        <value condition="String.IsEqual(ListItem.Property(silo.menu.icon),play)">icons/infodialogs/play.png</value>
        <value condition="String.IsEqual(ListItem.Property(silo.menu.icon),rows)">icons/sidemenu/tv.png</value>
        <value condition="String.IsEqual(ListItem.Property(silo.menu.icon),sync)">icons/infodialogs/update.png</value>
        <value condition="String.IsEqual(ListItem.Property(silo.menu.icon),libraries)">icons/sidemenu/videos.png</value>
        <value condition="String.IsEqual(ListItem.Property(silo.menu.icon),rewrite)">silo/start_over.png</value>
        <value condition="String.IsEqual(ListItem.Property(silo.menu.icon),signout)">icons/settings/profiles.png</value>
        <value condition="String.IsEqual(ListItem.Property(silo.menu.icon),remove)">icons/infodialogs/uninstall.png</value>
        <value>$INFO[ListItem.Icon]</value>
    </variable>
    <variable name="SiloRowDescription">
        <value condition="!String.IsEmpty(ListItem.Property(silo.menu.description))">$INFO[ListItem.Property(silo.menu.description)]</value>
        <value condition="String.IsEqual(ListItem.Property(silo.menu.icon),profile)">Profile</value>
        <value>$INFO[ListItem.Plot]</value>
    </variable>
    <variable name="SiloBrowseArt">
        <value condition="Control.HasFocus(%(jump)d)">$INFO[Container(51).ListItem.Art(fanart)]</value>
        <value condition="!String.IsEmpty(ListItem.Art(fanart))">$INFO[ListItem.Art(fanart)]</value>
        <value condition="!String.IsEmpty(ListItem.Art(tvshow.fanart))">$INFO[ListItem.Art(tvshow.fanart)]</value>
        <value>$INFO[Container.Art(fanart)]</value>
    </variable>
    <!-- end Silo Skyline browse -->
''' % {'grid': GRID, 'episodes': EPISODES, 'jump': JUMP_ID, 'fans': FANS, 'chips': CHIPS}


def add_variables():
    path = os.path.join(ROOT, 'xml', 'Variables.xml')
    text = open(path, encoding='utf-8').read()
    start, end = '    <!-- Silo Skyline browse (tools/build_browse.py) -->', '    <!-- end Silo Skyline browse -->\n'
    if start in text:
        text = text[:text.index(start) - 1] + text[text.index(end) + len(end):]
    text = text.replace('</includes>', VARIABLES + '</includes>')
    open(path, 'w', encoding='utf-8').write(text)


if __name__ == '__main__':
    with open(os.path.join(ROOT, 'xml', 'MyVideoNav.xml'), 'w', encoding='utf-8') as handle:
        handle.write(build())
    add_variables()
    print('Wrote xml/MyVideoNav.xml and its variables in xml/Variables.xml')
