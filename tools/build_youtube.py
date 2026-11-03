#!/usr/bin/env python3
"""Write xml/Custom_1198_SiloYouTube.xml: a YouTube page as the YouTube app
on Android TV lays one out, in Silo's look, from the YouTube add-on:

    python3 tools/build_youtube.py

Pills under the title, as Skyline's other pages (Requests' Discover and
Yours): Search, then Home, Subscriptions and Library, which switch the page.
Home: rows of the app's big 16:9 cards (Recommended, Recently uploaded,
Trending). Subscriptions: the channels at the left (All first), a grid of
the chosen channel's videos at the right. Library: rows of History,
Watch Later, Playlists and Liked. Each row is the add-on's own list, loaded only
once its section shows; OK plays a video, or opens a folder, as the add-on
does. Focus is Skyline's own, as Home's rows (no selection box). The bar's
YouTube tab (tools/build_home.py) opens it, while the add-on is installed.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_home import (BACKGROUND, PILL_GAP, PILL_H, PILLS_TOP, ROOT, SAFE_X, SUB_DIM,  # noqa: E402
                        TAB_DIM, TEXT, TEXT_DIM, TITLE_DIM, focus_sheen)

WINDOW_ID = 1198
ADDON = 'plugin.video.youtube'
YT = 'plugin://%s/' % ADDON
# A row's list: videos only, no "Next page" (the app's rows end too).
ROW_PARAMS = '?hide_folders=true&amp;hide_next_page=true'
PILLS_ID = 100
SECTION = 'Window(Home).Property(silo.youtube.section)'
# A section opened this visit: Kodi loads even a hidden list as the window
# opens, so Subscriptions' and Library's lists have no path until then.
LOADED = 'Window(Home).Property(silo.youtube.loaded.%s)'
SECTIONS = [('home', 'Home'), ('subscriptions', 'Subscriptions'), ('library', 'Library')]
# Search, as the app's: a box before the pills; SiloKodiConnect's keyboard
# (mode=youtubesearch) puts the words and their results' path in properties
# and chooses the 'search' section, a grid of the results.
SEARCH_BOX_W = 420
QUERY = 'Window(Home).Property(silo.youtube.query)'
RESULTS = 'Window(Home).Property(silo.youtube.search)'
RESULTS_ID = 610
RESULTS_COLS = 3
CONTENT_X = SAFE_X
CONTENT_W = 1920 - CONTENT_X
TOP = PILLS_TOP + PILL_H + 28  # under the title and the pills

# The app's cards, as measured on a SHIELD: the chosen row's big (720 x 405,
# two and a half across), the others smaller (528 x 297).
BIG, MEDIUM = (720, 405), (528, 297)
ZOOM = BIG[0] * 100 // MEDIUM[0]  # the chosen row: its medium cards zoomed to the big size
CARD_GAP = 32
TEXT_H = 16 + 70 + 34 + 34 + 24  # a two-line title, the channel, the date


def item_h(size):
    return size[1] + TEXT_H
ROW_LABEL_H = 52
LABEL_GAP = 18  # the focused card's zoom stays clear of its row's label
HOME_LIST = 300
HOME_ROWS = [(301, 'Recommended', 'special/recommendations/'),
             (302, 'Recently uploaded', 'special/my_subscriptions/'),
             (303, 'Trending', 'special/popular_right_now/')]

# Subscriptions: All and the channels, then a grid of a channel's videos.
ALL_ID, CHANNELS_ID, SUBS_GRID = 401, 402, 410
CHANNELS_W = 400
CHANNEL_ROW = 72
GRID_X = CONTENT_X + CHANNELS_W + 40
GRID_COLS = 3
GRID_ITEM_W = (1920 - GRID_X - 24) // GRID_COLS
GRID_W = GRID_ITEM_W - CARD_GAP
GRID_H = GRID_W * 9 // 16
GRID_ITEM_H = GRID_H + TEXT_H
CHANNEL = 'Window(Home).Property(silo.youtube.channel)'

# Library: the app's rows, the account's own lists as the add-on's menu
# opens them: its History (HL) and Watch Later (WL) playlists, Playlists
# (folders, so they stay) and Liked.
LIBRARY_LIST = 510
LIBRARY_ROWS = [(511, 'History', 'special/playlist/HL/'),
                (512, 'Watch Later', 'special/playlist/WL/'),
                (513, 'Playlists', 'channel/mine/playlists/?hide_next_page=true'),
                (514, 'Liked', 'channel/mine/playlist/LL/')]


def shown(section):
    """A section shows while its pill is the chosen one (Home at first)."""
    if section == 'home':
        return '[String.IsEmpty(%s) | String.IsEqual(%s,home)]' % (SECTION, SECTION)
    return 'String.IsEqual(%s,%s)' % (SECTION, section)


def card(width, height, focused, view_id):
    """A video as the app shows one: its picture with the duration in the
    corner, then a two-line title, the channel and the date."""
    has_focus = 'Control.HasFocus(%d)' % view_id
    # No zoom of its own, as the app's: the chosen row is already big, and a card
    # growing stood out of line with the row's title or over its neighbours.
    zoom = ''
    # Skyline's focus, as Home's rows: the zoom, a faint veil and a hairline rim.
    ring = focus_sheen(width, height, 'silo/card_landscape_mask.png', 'silo/card_landscape_rim.png',
                       has_focus, 20) if focused else ''
    return '''
                <control type="group">%(zoom)s
                    <control type="image">
                        <left>6</left><top>6</top><width>%(w)d</width><height>%(h)d</height>
                        <aspectratio>scale</aspectratio>
                        <texture background="true" diffuse="silo/card_landscape_mask.png" fallback="colors/grey.png">$VAR[SiloYouTubeThumb]</texture>
                    </control>
                    <control type="image">
                        <left>6</left><top>6</top><width>%(w)d</width><height>%(h)d</height>
                        <texture border="24" colordiffuse="%(page)s">silo/card_corners.png</texture>
                    </control>
                    <control type="progress">
                        <left>20</left><top>%(pt)d</top><width>%(pw)d</width><height>6</height>
                        <texturebg colordiffuse="66000000">colors/white.png</texturebg>
                        <midtexture colordiffuse="FFFF0033">colors/white.png</midtexture>
                        <info>ListItem.PercentPlayed</info>
                        <visible>Integer.IsGreater(ListItem.PercentPlayed,0)</visible>
                    </control>
                    <!-- The duration in the picture's corner, as the app's. -->
                    <control type="label">
                        <left>%(bx)d</left><top>%(bt)d</top><width>110</width><height>34</height>
                        <align>right</align><aligny>center</aligny>
                        <font>silo_badge</font>
                        <textcolor>%(text)s</textcolor>
                        <label>$INFO[ListItem.Duration]</label>
                        <visible>!String.IsEmpty(ListItem.Duration) + !ListItem.IsFolder</visible>
                    </control>%(ring)s
                    <control type="textbox">
                        <left>6</left><top>%(t1)d</top><width>%(w)d</width><height>64</height>
                        <font>silo_card_title</font>
                        <textcolor>%(title)s</textcolor>
                        <label>$INFO[ListItem.Label]</label>
                    </control>
                    <control type="label">
                        <left>6</left><top>%(t2)d</top><width>%(w)d</width><height>34</height>
                        <font>silo_card_sub</font>
                        <textcolor>%(sub)s</textcolor>
                        <label>$VAR[SiloYouTubeChannel]</label>
                    </control>
                    <control type="label">
                        <left>6</left><top>%(t3)d</top><width>%(w)d</width><height>34</height>
                        <font>silo_card_sub</font>
                        <textcolor>%(sub)s</textcolor>
                        <label>$VAR[SiloYouTubeWhen]</label>
                    </control>
                </control>''' % {
        'zoom': zoom, 'w': width, 'h': height, 'pt': height - 2, 'pw': width - 28, 'text': TEXT, 'ring': ring,
        'page': BACKGROUND,
        'bx': width + 6 - 110 - 14, 'bt': height - 36,
        't1': height + 20, 't2': height + 90, 't3': height + 124,
        'title': TEXT if focused else TITLE_DIM, 'sub': TEXT_DIM if focused else SUB_DIM}


ROW_GAP = 12
BIG_SLOT = ROW_LABEL_H + LABEL_GAP + item_h(MEDIUM) * ZOOM // 100 + ROW_GAP
MEDIUM_SLOT = ROW_LABEL_H + LABEL_GAP + item_h(MEDIUM) + ROW_GAP


def row_property(section):
    """The section's chosen row (0 first), kept while the pills have focus."""
    return 'Window(Home).Property(silo.youtube.row.%s)' % section


def chosen_row(section, number):
    condition = 'String.IsEqual(%s,%d)' % (row_property(section), number)
    return '[String.IsEmpty(%s) | %s]' % (row_property(section), condition) if number == 0 else condition


def row_moves(section, number, count):
    """Where a row slides for each chosen row above it: the chosen one at the
    top, the next under it. Rows above the chosen one are hidden instead
    (row_hidden): Kodi didn't undo their slide and fade on going back up."""
    moves = ''
    for focus in range(number):
        moves += ('\n                <animation effect="slide" end="0,%d" time="260" tween="cubic" easing="out" '
                  'condition="%s">Conditional</animation>' % (BIG_SLOT + (number - focus - 1) * MEDIUM_SLOT,
                                                              chosen_row(section, focus)))
    return moves


def row_hidden(section, number, count):
    """A row above the chosen one is hidden, but Up can still focus it."""
    later = ['String.IsEqual(%s,%d)' % (row_property(section), focus) for focus in range(number + 1, count)]
    if not later:
        return ''
    return ('\n                <visible allowhiddenfocus="true">!%s</visible>'
            '\n                <animation effect="fade" time="160">VisibleChange</animation>'
            % ('[%s]' % ' | '.join(later)))


def row_layouts(list_id):
    return '\n                    <itemlayout width="%d" height="%d">%s\n                    </itemlayout>' \
        '\n                    <focusedlayout width="%d" height="%d">%s\n                    </focusedlayout>' % (
            MEDIUM[0] + CARD_GAP, item_h(MEDIUM), card(MEDIUM[0], MEDIUM[1], False, list_id),
            MEDIUM[0] + CARD_GAP, item_h(MEDIUM), card(MEDIUM[0], MEDIUM[1], True, list_id))


ROW = '''
            <control type="group">
                <left>0</left><top>0</top><width>%(w)d</width><height>%(slot)d</height>%(hidden)s%(moves)s
                <control type="label">
                    <left>0</left><top>0</top><width>%(w)d</width><height>%(lh)d</height>
                    <aligny>center</aligny>
                    <font>silo_meta</font>
                    <textcolor>%(dim)s</textcolor>
                    <label>%(title)s</label>
                </control>
                <control type="label">
                    <left>0</left><top>%(lh)d</top><width>%(w)d</width><height>80</height>
                    <aligny>center</aligny>
                    <font>silo_detail</font>
                    <textcolor>%(sub)s</textcolor>
                    <label>Nothing here yet</label>
                    <visible>!Container(%(id)d).IsUpdating + Integer.IsEqual(Container(%(id)d).NumItems,0)</visible>
                </control>
                <!-- The chosen row's cards zoom to the big size from their top left;
                     the focused card stays at the left (a fixedlist), as the app's. -->
                <control type="fixedlist" id="%(id)d">
                    <left>-6</left><top>%(lt)d</top><width>%(lw)d</width><height>%(ih)d</height>
                    <orientation>horizontal</orientation>
                    <focusposition>0</focusposition>
                    <movement>0</movement>
                    <scrolltime tween="cubic" easing="out">240</scrolltime>
                    <animation effect="zoom" end="%(zoom)d" center="%(cx)d,%(cy)d" time="260" tween="cubic" easing="out" condition="%(big)s">Conditional</animation>
                    <onfocus>SetProperty(silo.youtube.row.%(section)s,%(number)d,home)</onfocus>
                    <onup>%(up)d</onup>%(down)s%(layouts)s
                    <content target="videos">%(path)s</content>
                </control>
            </control>'''


def row(section, number, count, list_id, title, path, up, down):
    """A row of the app's cards. As the app's, the chosen row is big and at the
    top, the next one medium under it (row_moves, row_layouts)."""
    return ROW % {
        'w': CONTENT_W, 'slot': BIG_SLOT, 'moves': row_moves(section, number, count),
        'hidden': row_hidden(section, number, count), 'lh': ROW_LABEL_H,
        'lt': ROW_LABEL_H + LABEL_GAP, 'dim': TEXT_DIM, 'sub': SUB_DIM, 'title': title, 'id': list_id,
        'lw': CONTENT_W + 6, 'ih': item_h(MEDIUM), 'section': section, 'number': number, 'up': up,
        'layouts': row_layouts(list_id), 'path': path, 'zoom': ZOOM, 'big': chosen_row(section, number),
        # Kodi takes a zoom's centre in the section group's coordinates: the list's top left.
        'cx': -6, 'cy': ROW_LABEL_H + LABEL_GAP,
        'down': '\n                    <ondown>%s</ondown>' % (down or 'noop')}


def row_path(path):
    return YT + path + ('' if '?' in path else ROW_PARAMS)


def lazy_variables():
    """Library's rows' paths: empty (Kodi waits) until Library is chosen."""
    return ''.join('''    <variable name="SiloYouTubeRow_%d">
        <value condition="!String.IsEmpty(%s)">%s</value>
    </variable>
''' % (list_id, LOADED % 'library', row_path(path)) for list_id, _, path in LIBRARY_ROWS)


def rows_section(group_id, section, rows, first_up=PILLS_ID):
    """The section's rows, the chosen one at the top (see row())."""
    ids = [list_id for list_id, _, _ in rows]
    lazy = section != 'home'  # Home shows first; the others load once chosen (lazy_variables)
    body = ''.join(row(section, n, len(rows), list_id, title,
                       '$VAR[SiloYouTubeRow_%d]' % list_id if lazy else row_path(path),
                       ([first_up] + ids)[n], (ids + [0])[n + 1]) for n, (list_id, title, path) in enumerate(rows))
    return '''
        <!-- %s -->
        <control type="group" id="%d">
            <left>%d</left><top>%d</top><width>%d</width><height>%d</height>
            <visible>%s</visible>%s
        </control>''' % (section.title(), group_id, CONTENT_X, TOP, CONTENT_W, 1080 - TOP, shown(section), body)


def pill(control_id, label, colour, fill, click):
    return '''
                <control type="button" id="%(id)d">
                    <width>auto</width><height>%(h)d</height>
                    <label>%(label)s</label>
                    <font>silo_meta</font>
                    <textoffsetx>22</textoffsetx>
                    <align>center</align><aligny>center</aligny>
                    <textcolor>%(colour)s</textcolor>
                    <focusedcolor>FF000000</focusedcolor>
                    <texturefocus border="24" colordiffuse="%(text)s">silo/pill.png</texturefocus>
                    <texturenofocus border="24" colordiffuse="%(fill)s">silo/pill.png</texturenofocus>
%(clicks)s
                </control>''' % {'id': control_id, 'h': PILL_H, 'label': label, 'colour': colour, 'fill': fill,
                                 'text': TEXT, 'clicks': ''.join('\n                    <onclick>%s</onclick>' % c
                                                                 for c in ([click] if isinstance(click, str) else click))}


def pills_down(indent):
    """Down from the pills: the shown section's first list."""
    return ''.join('\n%s<ondown condition="%s">%d</ondown>' % (indent, shown(key), target)
                   for key, target in (('home', HOME_ROWS[0][0]), ('subscriptions', ALL_ID),
                                       ('library', LIBRARY_ROWS[0][0]), ('search', RESULTS_ID)))


def search_box():
    """The app's search field: a magnifier and what was searched (or Search
    YouTube), the white pill while focused."""
    return '''
                <control type="group" id="%(gid)d">
                    <width>%(w)d</width><height>%(h)d</height>
                    <control type="button" id="%(id)d">
                        <width>%(w)d</width><height>%(h)d</height>
                        <label>$VAR[SiloYouTubeSearchLabel]</label>
                        <font>silo_meta</font>
                        <textoffsetx>62</textoffsetx>
                        <aligny>center</aligny>
                        <textcolor>$VAR[SiloYouTubeSearchText]</textcolor>
                        <focusedcolor>FF000000</focusedcolor>
                        <texturefocus border="24" colordiffuse="%(text)s">silo/pill.png</texturefocus>
                        <texturenofocus border="24" colordiffuse="$VAR[SiloYouTubeSearchFill]">silo/pill.png</texturenofocus>
                        <onclick>RunPlugin(plugin://plugin.video.silokodiconnect/?mode=youtubesearch)</onclick>
                        <!-- In its own group (for the magnifier), it takes none of the
                             pills' moves: its own, the same. -->
                        <onleft>noop</onleft><onup>noop</onup>
                        <onright>%(next)d</onright>%(down)s%(back)s
                    </control>
                    <control type="image">
                        <left>22</left><top>%(it)d</top><width>28</width><height>28</height>
                        <aspectratio>keep</aspectratio>
                        <texture colordiffuse="FF000000">icons/search.png</texture>
                        <visible>Control.HasFocus(%(id)d)</visible>
                    </control>
                    <control type="image">
                        <left>22</left><top>%(it)d</top><width>28</width><height>28</height>
                        <aspectratio>keep</aspectratio>
                        <texture colordiffuse="%(dim)s">icons/search.png</texture>
                        <visible>!Control.HasFocus(%(id)d)</visible>
                    </control>
                </control>''' % {'gid': PILLS_ID + 1000, 'id': PILLS_ID + 1, 'w': SEARCH_BOX_W, 'h': PILL_H,
                                   'it': (PILL_H - 28) // 2, 'text': TEXT, 'dim': TAB_DIM,
                                   'next': PILLS_ID + 2, 'down': pills_down('                        '),
                                   'back': search_back(shown('search')).replace('\n                ', '\n                        ')}


def search_back(condition=None):
    """Back while a search's results show: clears it, YouTube's Home again."""
    # Kodi checks each action's condition as it runs: the words, cleared last,
    # keep it true until Home's first row has focus.
    cond = ' condition="!String.IsEmpty(%s)"' % QUERY if condition else ''
    return ''.join('\n                <onback%s>%s</onback>' % (cond, action) for action in (
        'ClearProperty(silo.youtube.search,home)', 'ClearProperty(silo.youtube.section,home)',
        'SetFocus(%d)' % HOME_ROWS[0][0], 'ClearProperty(silo.youtube.query,home)'))


def search_results():
    """The results, a grid of the app's cards under what was searched."""
    item_w = MEDIUM[0] + CARD_GAP
    return '''
        <!-- Search -->
        <control type="group">
            <visible>%(shown)s</visible>
            <control type="label">
                <left>%(x)d</left><top>%(top)d</top><width>%(w)d</width><height>%(lh)d</height>
                <aligny>center</aligny>
                <font>silo_meta</font>
                <textcolor>%(dim)s</textcolor>
                <label>$INFO[%(query)s,Results for “,”]</label>
            </control>
            <control type="label">
                <left>%(x)d</left><top>%(gt)d</top><width>%(w)d</width><height>80</height>
                <font>silo_detail</font>
                <textcolor>%(sub)s</textcolor>
                <label>Nothing found</label>
                <visible>!Container(%(id)d).IsUpdating + Integer.IsEqual(Container(%(id)d).NumItems,0)</visible>
            </control>
            <control type="panel" id="%(id)d">
                <left>%(gx)d</left><top>%(gt)d</top><width>%(gw)d</width><height>%(gh)d</height>
                <orientation>vertical</orientation>
                <scrolltime tween="cubic" easing="out">280</scrolltime>
                <onup>%(pills)d</onup>
                <!-- Back from the results: YouTube's Home again, as the app's. -->%(back)s
                <itemlayout width="%(iw)d" height="%(ih)d">%(card)s
                </itemlayout>
                <focusedlayout width="%(iw)d" height="%(ih)d">%(card_focused)s
                </focusedlayout>
                <content target="videos">$INFO[%(results)s]</content>
            </control>
        </control>''' % {'shown': shown('search'), 'x': CONTENT_X, 'top': TOP, 'w': CONTENT_W, 'lh': ROW_LABEL_H,
                          'dim': TEXT_DIM, 'sub': SUB_DIM, 'query': QUERY, 'id': RESULTS_ID, 'pills': PILLS_ID,
                          'gx': CONTENT_X - 6, 'gt': TOP + ROW_LABEL_H + LABEL_GAP,
                          'gw': item_w * RESULTS_COLS, 'gh': 1080 - TOP - ROW_LABEL_H - LABEL_GAP,
                          'iw': item_w, 'ih': item_h(MEDIUM), 'results': RESULTS, 'back': search_back(),
                          'card': card(MEDIUM[0], MEDIUM[1], False, RESULTS_ID),
                          'card_focused': card(MEDIUM[0], MEDIUM[1], True, RESULTS_ID)}


def pills():
    """Search, then the sections, as Requests' pills: the chosen section's
    pill stays lit; dimmed until Up from the content reaches them."""
    buttons = search_box()
    for number, (key, label) in enumerate(SECTIONS, 2):
        buttons += pill(PILLS_ID + number, label, '$VAR[SiloYouTubePill_%s]' % key, '$VAR[SiloYouTubePillFill_%s]' % key,
                        ['SetProperty(silo.youtube.section,%s,home)' % key,
                         'SetProperty(silo.youtube.loaded.%s,1,home)' % key])
    down = pills_down('            ')
    return '''
        <control type="grouplist" id="%(id)d">
            <left>%(x)d</left><top>%(top)d</top><width>%(w)d</width><height>%(h)d</height>
            <orientation>horizontal</orientation>
            <itemgap>%(gap)d</itemgap>
            <animation effect="fade" start="100" end="50" time="200" condition="!ControlGroup(%(id)d).HasFocus()">Conditional</animation>
            <onup>noop</onup><onleft>noop</onleft><onright>noop</onright>%(down)s%(back)s%(buttons)s
        </control>''' % {'id': PILLS_ID, 'x': SAFE_X, 'top': PILLS_TOP, 'w': 1920 - 2 * SAFE_X, 'h': PILL_H,
                         'gap': PILL_GAP, 'down': down, 'buttons': buttons,
                         'back': search_back(shown('search'))}


def channel_row(focused):
    pill_image = ''
    if focused:
        pill_image = '''
                    <control type="image">
                        <width>%(w)d</width><height>%(h)d</height>
                        <texture border="30" colordiffuse="%(text)s">silo/pill.png</texture>
                        <visible>Control.HasFocus(%(id)d)</visible>
                    </control>''' % {'w': CHANNELS_W, 'h': CHANNEL_ROW - 8, 'text': TEXT, 'id': CHANNELS_ID}
    return '''%(pill)s
                    <control type="image">
                        <left>14</left><top>8</top><width>48</width><height>48</height>
                        <aspectratio>scale</aspectratio>
                        <texture background="true" diffuse="silo/avatar_mask.png" fallback="colors/grey.png">$INFO[ListItem.Icon]</texture>
                    </control>
                    <control type="label">
                        <left>78</left><top>0</top><width>%(lw)d</width><height>%(h)d</height>
                        <aligny>center</aligny>
                        <font>silo_meta</font>
                        <textcolor>%(c)s</textcolor>
                        <label>$INFO[ListItem.Label]</label>
                    </control>''' % {'pill': pill_image, 'lw': CHANNELS_W - 96, 'h': CHANNEL_ROW - 8,
                                     'c': '$VAR[SiloYouTubeRowText]' if focused else TEXT}


def subscriptions():
    """The app's Subscriptions: All and the channels, then the chosen one's videos."""
    return '''
        <!-- Subscriptions -->
        <control type="group">
            <visible>%(shown)s</visible>
            <control type="button" id="%(all)d">
                <left>%(x)d</left><top>%(top)d</top><width>%(cw)d</width><height>%(rh)d</height>
                <label>All</label>
                <font>silo_meta</font>
                <textoffsetx>78</textoffsetx>
                <aligny>center</aligny>
                <textcolor>%(text)s</textcolor>
                <focusedcolor>FF000000</focusedcolor>
                <texturefocus border="30" colordiffuse="%(text)s">silo/pill.png</texturefocus>
                <texturenofocus border="30" colordiffuse="$VAR[SiloYouTubeAllPill]">silo/pill.png</texturenofocus>
                <onleft>noop</onleft><onup>%(pills)d</onup>
                <ondown>%(channels)d</ondown>
                <onright>%(grid)d</onright>
                <onclick>ClearProperty(silo.youtube.channel,home)</onclick>
                <onclick>SetFocus(%(grid)d)</onclick>
            </control>
            <control type="label">
                <left>%(x)d</left><top>%(atop)d</top><width>%(cw)d</width><height>40</height>
                <font>silo_badge</font>
                <textcolor>%(dim)s</textcolor>
                <label>CHANNELS</label>
            </control>
            <control type="list" id="%(channels)d">
                <left>%(x)d</left><top>%(ltop)d</top><width>%(cw)d</width><height>%(lh)d</height>
                <orientation>vertical</orientation>
                <scrolltime tween="cubic" easing="out">200</scrolltime>
                <onleft>noop</onleft><onup>%(all)d</onup>
                <onright>%(grid)d</onright>
                <!-- A channel's videos at the right, as the app's (not its page). -->
                <onclick>SetProperty(silo.youtube.channel,$INFO[ListItem.FolderPath],home)</onclick>
                <onclick>SetFocus(%(grid)d)</onclick>
                <itemlayout width="%(cw)d" height="%(row)d">%(channel)s
                </itemlayout>
                <focusedlayout width="%(cw)d" height="%(row)d">%(channel_focused)s
                </focusedlayout>
                <content target="videos">$VAR[SiloYouTubeChannels]</content>
            </control>
            <control type="label">
                <left>%(gx)d</left><top>%(top)d</top><width>%(gw)d</width><height>%(rh)d</height>
                <aligny>center</aligny>
                <font>silo_meta</font>
                <textcolor>%(dim)s</textcolor>
                <label>$VAR[SiloYouTubeChannelTitle]</label>
            </control>
            <control type="label">
                <left>%(gx)d</left><top>%(gtop)d</top><width>%(gw)d</width><height>80</height>
                <font>silo_detail</font>
                <textcolor>%(sub)s</textcolor>
                <label>Nothing here yet</label>
                <visible>!Container(%(grid)d).IsUpdating + Integer.IsEqual(Container(%(grid)d).NumItems,0)</visible>
            </control>
            <control type="panel" id="%(grid)d">
                <left>%(gx6)d</left><top>%(gtop)d</top><width>%(gw)d</width><height>%(gh)d</height>
                <orientation>vertical</orientation>
                <scrolltime tween="cubic" easing="out">280</scrolltime>
                <onleft>%(channels)d</onleft><onup>%(pills)d</onup>
                <itemlayout width="%(giw)d" height="%(gih)d">%(card)s
                </itemlayout>
                <focusedlayout width="%(giw)d" height="%(gih)d">%(card_focused)s
                </focusedlayout>
                <content target="videos">$VAR[SiloYouTubeChannelPath]</content>
            </control>
        </control>''' % {
        'shown': shown('subscriptions'), 'all': ALL_ID, 'channels': CHANNELS_ID, 'grid': SUBS_GRID, 'pills': PILLS_ID,
        'x': CONTENT_X, 'top': TOP, 'cw': CHANNELS_W, 'rh': CHANNEL_ROW - 8, 'text': TEXT, 'dim': TEXT_DIM, 'sub': SUB_DIM,
        'atop': TOP + CHANNEL_ROW + 8, 'ltop': TOP + CHANNEL_ROW + 52, 'lh': 1080 - TOP - CHANNEL_ROW - 52,
        'row': CHANNEL_ROW, 'channel': channel_row(False), 'channel_focused': channel_row(True),
        'gx': GRID_X, 'gx6': GRID_X - 6, 'gtop': TOP + CHANNEL_ROW, 'gw': 1920 - GRID_X, 'gh': 1080 - TOP - CHANNEL_ROW,
        'giw': GRID_ITEM_W, 'gih': GRID_ITEM_H, 'card': card(GRID_W, GRID_H, False, SUBS_GRID),
        'card_focused': card(GRID_W, GRID_H, True, SUBS_GRID)}


def library():
    """The app's Library: History, Watch Later, Playlists and Liked, as rows."""
    return rows_section(LIBRARY_LIST, 'library', LIBRARY_ROWS)


def build():
    return '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by tools/build_youtube.py: edit that, not this. -->
<window id="%(window)d" type="window">
    <defaultcontrol always="true">%(first)d</defaultcontrol>
    <!-- Home, its first row focused, as the app opens. -->
    <onload>ClearProperty(silo.youtube.section,home)</onload>
    <onload>ClearProperty(silo.youtube.row.home,home)</onload>
    <onload>ClearProperty(silo.youtube.row.library,home)</onload>
    <onload>ClearProperty(silo.youtube.loaded.subscriptions,home)</onload>
    <onload>ClearProperty(silo.youtube.loaded.library,home)</onload>
    <onload>ClearProperty(silo.youtube.query,home)</onload>
    <onload>ClearProperty(silo.youtube.search,home)</onload>
    <backgroundcolor>%(background)s</backgroundcolor>
    <controls>
        <control type="image">
            <left>0</left><top>0</top><width>1920</width><height>1080</height>
            <texture colordiffuse="%(background)s">colors/white.png</texture>
        </control>
        <include content="SiloFrame">
            <param name="title">YouTube</param>
            <param name="sub"></param>
        </include>
%(home_rows)s
%(subscriptions)s
%(library)s
%(search)s
%(pills)s
    </controls>
</window>
''' % {'window': WINDOW_ID, 'first': HOME_ROWS[0][0], 'background': BACKGROUND,
       'home_rows': rows_section(HOME_LIST, 'home', HOME_ROWS), 'subscriptions': subscriptions(),
       'library': library(), 'search': search_results(), 'pills': pills()}


def pill_variables():
    out = ''
    for key, _ in SECTIONS:
        chosen = shown(key)
        out += '''    <variable name="SiloYouTubePill_%(k)s">
        <value condition="%(c)s">%(text)s</value>
        <value>%(dim)s</value>
    </variable>
    <variable name="SiloYouTubePillFill_%(k)s">
        <value condition="%(c)s">33FFFFFF</value>
        <value>12FFFFFF</value>
    </variable>
''' % {'k': key, 'c': chosen, 'text': TEXT, 'dim': TAB_DIM}
    return out


VARIABLES = '''
    <!-- Silo Skyline YouTube (tools/build_youtube.py) -->
%(pills)s    <variable name="SiloYouTubeSearchLabel">
        <value condition="!String.IsEmpty(%(query)s)">$INFO[%(query)s]</value>
        <value>Search YouTube</value>
    </variable>
    <variable name="SiloYouTubeSearchText">
        <value condition="String.IsEqual(%(section)s,search)">%(text)s</value>
        <value>%(dim)s</value>
    </variable>
    <variable name="SiloYouTubeSearchFill">
        <value condition="String.IsEqual(%(section)s,search)">33FFFFFF</value>
        <value>12FFFFFF</value>
    </variable>
    <variable name="SiloYouTubeSection">
        <value condition="String.IsEqual(%(section)s,subscriptions)">Subscriptions</value>
        <value condition="String.IsEqual(%(section)s,library)">Library</value>
        <value>Home</value>
    </variable>
    <variable name="SiloYouTubeThumb">
        <value condition="!String.IsEmpty(ListItem.Art(thumb))">$INFO[ListItem.Art(thumb)]</value>
        <value>$INFO[ListItem.Icon]</value>
    </variable>
    <!-- The app's second line, the channel; the add-on names it as the studio (or the artist). -->
    <variable name="SiloYouTubeChannel">
        <value condition="String.IsEqual(ListItem.Studio,Untitled) | String.IsEqual(ListItem.Artist,Untitled)"></value>
        <value condition="!String.IsEmpty(ListItem.Studio)">$INFO[ListItem.Studio]</value>
        <value>$INFO[ListItem.Artist]</value>
    </variable>
    <variable name="SiloYouTubeWhen">
        <value condition="!String.IsEmpty(ListItem.Premiered)">$INFO[ListItem.Premiered]</value>
        <value>$INFO[ListItem.Date]</value>
    </variable>
    <variable name="SiloYouTubeRowText">
        <value condition="Control.HasFocus(%(channels)d)">FF000000</value>
        <value>%(text)s</value>
    </variable>
    <variable name="SiloYouTubeAllPill">
        <value condition="String.IsEmpty(%(channel)s)">33FFFFFF</value>
        <value>00FFFFFF</value>
    </variable>
    <!-- The chosen channel's videos, or All: the subscriptions' newest. -->
    <variable name="SiloYouTubeChannels">
        <value condition="!String.IsEmpty(%(subs_loaded)s)">%(yt)ssubscriptions/list/</value>
    </variable>
    <variable name="SiloYouTubeChannelPath">
        <value condition="String.IsEmpty(%(subs_loaded)s)"></value>
        <value condition="String.Contains(%(channel)s,?)">$INFO[%(channel)s]%(more)s</value>
        <value condition="!String.IsEmpty(%(channel)s)">$INFO[%(channel)s]%(params)s</value>
        <value>%(yt)sspecial/my_subscriptions/%(params)s</value>
    </variable>
    <variable name="SiloYouTubeChannelTitle">
        <value condition="!String.IsEmpty(%(channel)s)">Latest</value>
        <value>Most recent</value>
    </variable>
    <!-- end Silo Skyline YouTube -->
''' % {'pills': pill_variables() + lazy_variables(), 'subs_loaded': LOADED % 'subscriptions', 'query': QUERY, 'dim': TAB_DIM,
       'section': SECTION, 'channels': CHANNELS_ID, 'text': TEXT, 'channel': CHANNEL,
       'yt': YT, 'params': ROW_PARAMS, 'more': ROW_PARAMS.replace('?', '&amp;', 1)}


def add_variables():
    path = os.path.join(ROOT, 'xml', 'Variables.xml')
    text = open(path, encoding='utf-8').read()
    start, end = '    <!-- Silo Skyline YouTube (tools/build_youtube.py) -->', '    <!-- end Silo Skyline YouTube -->\n'
    if start in text:
        text = text[:text.index(start) - 1] + text[text.index(end) + len(end):]
    text = text.replace('</includes>', VARIABLES + '</includes>')
    open(path, 'w', encoding='utf-8').write(text)


if __name__ == '__main__':
    with open(os.path.join(ROOT, 'xml', 'Custom_%d_SiloYouTube.xml' % WINDOW_ID), 'w', encoding='utf-8') as handle:
        handle.write(build())
    add_variables()
    print('Wrote xml/Custom_%d_SiloYouTube.xml and its variables in xml/Variables.xml' % WINDOW_ID)
