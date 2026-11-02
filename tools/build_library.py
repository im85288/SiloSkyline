"""Write xml/Custom_1191_SiloLibrary.xml: Silo's Browse for films and series.

    python3 tools/build_library.py

Movies' and Series' Browse (their tab's dropdown) open it with
Window(Home).Property(silo.browse.type) movies or tvshows and
silo.browse.path the library folder to list. It is Silo's grid: six large
posters to a row (their rating is in Silo's art) with a watched tick, the title and year
under each; selecting one opens its details page (through SiloKodiConnect,
as from Home), not Kodi's play-or-open. On the right, Silo's A-Z: a column of
dots that opens into letters when it has focus; a letter shows only the
titles from it (a leading "The", "A" or "An" set aside), All shows them all.

The avatar card's Watchlist, Favorites and History open it too, with
silo.browse.type watchlist, favorites or history and silo.browse.list the
add-on's row: their own grids keep Silo's order (newest first), with no A-Z.
"""
import json
import re
import os
import sys
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_home import rt_list_marks, RATING_SHOWN, focus_sheen, focus_zoom, watched_mark, BACKGROUND, ROOT, SAFE_X, TEXT, TEXT_DIM, TITLE_DIM, SUB_DIM, GRID_BACKDROP  # noqa: E402

WINDOW_ID = 1191
TYPE = 'Window(Home).Property(silo.browse.type)'
PATH = 'Window(Home).Property(silo.browse.path)'
LETTER = 'Window(Home).Property(silo.browse.letter)'
LIST = 'Window(Home).Property(silo.browse.list)'
GRID_ID, AZ_ID = 50, 60
# Each list has its own grid: Kodi reopens a grid on the title last selected
# in it, so a shared one would open History on a title picked in Favorites.
PERSONAL = {'watchlist': ('Watchlist', 51), 'favorites': ('Favorites', 52), 'history': ('History', 53),
            # Silo's calendar: each started show's next episode (SiloKodiConnect).
            'comingsoon': ('Coming Soon', 54)}
IS_PERSONAL = '!String.IsEmpty(%s)' % LIST
COLS = 6
GRID_X, GRID_TOP = SAFE_X - 6, 252
SORT_TOP = 168
AZ_W = 96
ITEM_W = (1920 - 2 * SAFE_X - AZ_W - 24) // COLS        # a card and its gap
POSTER_W = ITEM_W - 24
POSTER_H = POSTER_W * 3 // 2
ITEM_H = POSTER_H + 12 + 44 + 34 + 26
LETTERS = ['All', '#'] + [chr(c) for c in range(ord('A'), ord('Z') + 1)]
ARTICLES = ('The ', 'A ', 'An ')
DOT_H, LETTER_H = 30, 72

# Silo's Sort (TvLibrarySortOption): (label, Kodi sort, descending first,
# kinds it applies to, Silo's words for ascending and descending). Kept per
# kind in Skin.String(silo.sort.<kind>) and
# Skin.HasSetting(silo.sort.<kind>.desc); choosing the current one flips it.
SORT_ID, SORT_LIST_ID = 70, 71
# The grid's sort: Kodi takes $INFO there, not $VAR, so the window sets these
# from the skin strings when it opens and the Sort list when it changes them.
SORT_BY = 'Window(Home).Property(silo.browse.sort)'
SORT_ORDER = 'Window(Home).Property(silo.browse.order)'
SORTS = [('Title', 'title', False, ('movies', 'tvshows'), ('A–Z', 'Z–A')),
         ('Date Added', 'dateadded', True, ('movies', 'tvshows'), ('Oldest', 'Newest')),
         ('Year', 'year', True, ('movies', 'tvshows'), ('Oldest', 'Newest')),
         ('Rating', 'rating', True, ('movies', 'tvshows'), ('Lowest', 'Highest')),
         ('Runtime', 'runtime', True, ('movies',), ('Shortest', 'Longest')),
         ('Resolution', 'videoresolution', True, ('movies',), ('Lowest', 'Highest'))]
KINDS = ('movies', 'tvshows')
SORT_W, SORT_ROW, SORT_HEAD = 440, 64, 58

# Browse's views, per kind in Skin.String(silo.view.<kind>): Silo's grid (none
# chosen), a hero over two rows of posters (Plex's and Apple TV's), or a list
# beside the focused title's details (Infuse's). Each view has its own path,
# set only while it shows (silo.browse.vpath.<view>): Kodi loads a hidden
# container's path too, and each would hold the whole library.
HERO_ID, LIST_VIEW_ID = 57, 58
VIEW_ID, VIEW_LIST_ID = 72, 73
# Infuse's Unwatched filter: a pill left of View, kept for every Browse list.
UNWATCHED_ID = 74
UNWATCHED = 'Skin.HasSetting(silo.unwatched)'
# Silo's box sets in a films grid: SiloKodiConnect tags each box set's films but
# its first by title, which the grid hides (BOX_SET_MEMBER, kodidb.py); the
# first stands for the box set there, with the set's art, as Silo's grouped
# browse. Not in a set's own folder, which lists them all.
GROUPED = ('[String.StartsWith(%s,videodb://movies/) + !String.StartsWith(%s,videodb://movies/sets/)]' % (PATH, PATH))
BOX_SET = '[Integer.IsGreater(ListItem.SetId,0) + %s]' % GROUPED
BOX_SET_MEMBER = 'Silo box set member'


def library_filter(kind, unwatched, grouped):
    """Kodi's library filter: titles not watched (a show: not every episode),
    and in a films grid without its box sets' other films (BOX_SET)."""
    rules = ([{'field': 'playcount', 'operator': 'is', 'value': ['0']}] if unwatched else []) + \
        ([{'field': 'tag', 'operator': 'isnot', 'value': [BOX_SET_MEMBER]}] if grouped else [])
    rule = {'type': kind, 'rules': {'and': rules}}
    return quote(json.dumps(rule, separators=(',', ':')), safe='')
VIEWS = [('Grid', 'grid', GRID_ID), ('Hero', 'hero', HERO_ID), ('List', 'list', LIST_VIEW_ID)]
VPATH = 'Window(Home).Property(silo.browse.vpath.%s)'
HERO_COLS = 8
HERO_ITEM_W = (1920 - 2 * SAFE_X - AZ_W - 24) // HERO_COLS
HERO_POSTER_W = HERO_ITEM_W - 24
HERO_POSTER_H = HERO_POSTER_W * 3 // 2
HERO_ITEM_H = HERO_POSTER_H + 20
HERO_GRID_TOP = 1080 - 2 * HERO_ITEM_H - 8
LIST_ROW = 66


def view_is(view, kind=None):
    """Whether Browse shows view (for kind, else for the open kind)."""
    def one(k):
        chosen = 'Skin.String(silo.view.%s)' % k
        this = 'String.IsEmpty(%s)' % chosen if view == 'grid' else 'String.IsEqual(%s,%s)' % (chosen, view)
        return this if kind else '[String.IsEqual(%s,%s) + %s]' % (TYPE, k, this)
    return one(kind) if kind else '[%s]' % ' | '.join(one(k) for k in KINDS)


def show_view(path=None):
    """[(condition, action)]: the open kind's view gets Browse's path (path,
    else Window(Home).Property(silo.browse.path)), the others none."""
    out = []
    for _, view, _ in VIEWS:
        out.append((view_is(view), 'SetProperty(silo.browse.vpath.%s,%s,home)' % (view, path or '$INFO[%s]' % PATH)))
        out.append(('!' + view_is(view), 'ClearProperty(silo.browse.vpath.%s,home)' % view))
    return out


def focus_view(action='SetFocus(%d)'):
    """[(condition, action)] focusing the open view's control."""
    return [(view_is(view), action % control) for _, view, control in VIEWS]


def letter_path(kind, letter):
    """The library folder with only the titles from a letter."""
    if letter == 'All':
        return 'videodb://%s/titles/' % kind
    if letter == '#':
        starts = [str(n) for n in range(10)]
    else:
        starts = [letter] + [article + letter for article in ARTICLES]
    rules = {'or': [{'field': 'title', 'operator': 'startswith', 'value': [start]} for start in starts]}
    query = {'type': kind, 'rules': rules}
    return 'videodb://%s/titles/?xsp=%s' % (kind, quote(json.dumps(query, separators=(',', ':')), safe=''))


def box_set_marks(width, height, indent=16, visible=None):
    """A box set card's marks, as Silo's: BOX SET top left, the film count
    bottom right (SiloKodiConnect's set art 'silocount')."""
    pad = ' ' * indent
    return '''
%(p)s<control type="group">
%(p)s    <left>6</left><top>6</top>
%(p)s    <visible>%(box)s</visible>
%(p)s    <control type="image">
%(p)s        <left>14</left><top>14</top><width>132</width><height>40</height>
%(p)s        <texture border="10" colordiffuse="CC000000">silo/badge_solid.png</texture>
%(p)s    </control>
%(p)s    <control type="label">
%(p)s        <left>14</left><top>14</top><width>132</width><height>40</height>
%(p)s        <align>center</align><aligny>center</aligny>
%(p)s        <font>silo_badge</font>
%(p)s        <textcolor>%(text)s</textcolor>
%(p)s        <label>BOX SET</label>
%(p)s    </control>
%(p)s    <control type="image">
%(p)s        <left>0</left><top>%(scrim_y)d</top><width>%(w)d</width><height>90</height>
%(p)s        <texture diffuse="silo/card_poster_mask.png" flipy="false">silo/card_scrim.png</texture>
%(p)s    </control>
%(p)s    <control type="label">
%(p)s        <left>0</left><top>%(count_y)d</top><width>%(count_w)d</width><height>40</height>
%(p)s        <align>right</align><aligny>center</aligny>
%(p)s        <font>silo_detail</font>
%(p)s        <textcolor>%(text)s</textcolor>
%(p)s        <label>[B]$INFO[ListItem.Art(set.silocount)][/B]</label>
%(p)s    </control>
%(p)s</control>''' % {'p': pad, 'box': visible or BOX_SET, 'text': TEXT, 'w': width, 'scrim_y': height - 90,
                       'count_y': height - 52, 'count_w': width - 18}


def card(focused, control_id=GRID_ID, size=None):
    """A grid's poster card; size (width, height) for the hero grid's, which
    has no captions (the hero names the title)."""
    if size:
        return hero_card(focused, control_id, *size)
    lit = 'Control.HasFocus(%d)' % control_id
    zoom = focus_zoom(lit, 20) if focused else ''
    title = '''
                <control type="label">
                    <left>6</left><top>%(ty)d</top><width>%(w)d</width><height>44</height>
                    <font>silo_card_title</font>
                    <textcolor>%(colour)s</textcolor>
                    <label>$VAR[SiloBrowseCardTitle]</label>%(scroll)s
                </control>''' % {'ty': POSTER_H + 18, 'w': POSTER_W, 'colour': TEXT if focused else TITLE_DIM,
                                  'scroll': '\n                    <scroll>true</scroll>' if focused else ''}
    return '''
                <control type="group">%(zoom)s
                <control type="image">
                    <left>6</left><top>6</top><width>%(pw)d</width><height>%(ph)d</height>
                    <aspectratio>scale</aspectratio>
                    <texture background="true" diffuse="silo/card_poster_mask.png" fallback="colors/grey.png">$VAR[SiloBrowsePoster]</texture>
                </control>
                <!-- The rating is in Silo's poster art itself (top left). -->
                <!-- Watched: Silo's frosted disc with a white tick, top right. -->%(sheen)s%(watched)s%(box)s%(title)s
                <control type="label">
                    <left>6</left><top>%(yy)d</top><width>%(w)d</width><height>34</height>
                    <font>silo_detail</font>
                    <textcolor>%(dim)s</textcolor>
                    <label>$VAR[SiloBrowseCardSub]</label>
                </control>
                </control>''' % {'pw': POSTER_W, 'ph': POSTER_H, 'zoom': zoom, 'title': title,
                                 'sheen': focus_sheen(POSTER_W, POSTER_H, 'silo/card_poster_mask.png', 'silo/card_poster_rim.png',
                                                      lit, 16) if focused else '',
                                 # A box set's card shows no one film's watched state.
                                 'watched': watched_mark(POSTER_W, POSTER_H, 'silo/card_poster_mask.png',
                                                         '!%s + [Integer.IsGreater(ListItem.PlayCount,0) | '
                                                         '[Integer.IsGreater(ListItem.Property(TotalEpisodes),0) + '
                                                         'Integer.IsEqual(ListItem.Property(UnWatchedEpisodes),0)]]' % BOX_SET,
                                                         lit if focused else '', 16),
                                 'yy': POSTER_H + 58, 'w': POSTER_W, 'dim': TEXT if focused else SUB_DIM,
                                 'box': box_set_marks(POSTER_W, POSTER_H)}


def hero_card(focused, control_id, width, height):
    lit = 'Control.HasFocus(%d)' % control_id
    return '''
                <control type="group">%(zoom)s
                <control type="image">
                    <left>6</left><top>6</top><width>%(w)d</width><height>%(h)d</height>
                    <aspectratio>scale</aspectratio>
                    <texture background="true" diffuse="silo/card_poster_mask.png" fallback="colors/grey.png">$VAR[SiloBrowsePoster]</texture>
                </control>%(sheen)s%(watched)s%(box)s
                </control>''' % {'box': box_set_marks(width, height), 'w': width, 'h': height, 'zoom': focus_zoom(lit, 20) if focused else '',
                                 'sheen': focus_sheen(width, height, 'silo/card_poster_mask.png', 'silo/card_poster_rim.png',
                                                      lit, 16) if focused else '',
                                 'watched': watched_mark(width, height, 'silo/card_poster_mask.png',
                                                         '!%s + [Integer.IsGreater(ListItem.PlayCount,0) | '
                                                         '[Integer.IsGreater(ListItem.Property(TotalEpisodes),0) + '
                                                         'Integer.IsEqual(ListItem.Property(UnWatchedEpisodes),0)]]' % BOX_SET,
                                                         lit if focused else '', 16)}


def letter_layouts(list_id=AZ_ID, chosen=None):
    """Silo's A-Z column, shared by every screen that has one: dots at rest,
    letters while it has focus (Kodi picks the item layout by condition);
    the chosen letter is lit either way. chosen: the condition for an item
    being the current letter (Browse's: the letter it filters to)."""
    lit = 'Control.HasFocus(%d)' % list_id
    if chosen is None:
        # A condition compares with another info label as it is (a $INFO in one is an error).
        chosen = '[String.IsEqual(ListItem.Label,%s) | [String.IsEqual(ListItem.Label,All) + String.IsEmpty(%s)]]' % (
            LETTER, LETTER)
    dot = '''
                <control type="image">
                    <left>%(x)d</left><top>%(y)d</top><width>10</width><height>10</height>
                    <texture colordiffuse="%(c)s">silo/avatar_mask.png</texture>
                    <visible>%(v)s</visible>
                </control>'''
    dots = (dot % {'x': (AZ_W - 10) // 2, 'y': (DOT_H - 10) // 2, 'c': TEXT, 'v': chosen}
            + dot % {'x': (AZ_W - 10) // 2, 'y': (DOT_H - 10) // 2, 'c': '59EDEDED', 'v': '!' + chosen})
    def letter(colour, visible):
        return '''
                <control type="label">
                    <width>%(w)d</width><height>%(h)d</height>
                    <align>center</align><aligny>center</aligny>
                    <font>silo_tab</font>
                    <textcolor>%(c)s</textcolor>
                    <label>$INFO[ListItem.Label]</label>%(v)s
                </control>''' % {'w': AZ_W, 'h': LETTER_H, 'c': colour,
                                 'v': '\n                    <visible>%s</visible>' % visible if visible else ''}
    square = '''
                <control type="image">
                    <left>12</left><top>6</top><width>%(w)d</width><height>%(h)d</height>
                    <texture border="20" colordiffuse="%(c)s">silo/card_landscape_mask.png</texture>%(v)s
                </control>'''
    resting = (square % {'w': AZ_W - 24, 'h': LETTER_H - 12, 'c': '33FFFFFF', 'v': '\n                    <visible>%s</visible>' % chosen}
               + letter(TEXT, chosen) + letter(TEXT_DIM, '!' + chosen))
    focused = (square % {'w': AZ_W - 24, 'h': LETTER_H - 12, 'c': TEXT, 'v': ''} + letter('FF000000', ''))
    return '''
            <itemlayout width="%(w)d" height="%(dh)d" condition="!%(lit)s">%(dots)s
            </itemlayout>
            <focusedlayout width="%(w)d" height="%(dh)d" condition="!%(lit)s">%(dots)s
            </focusedlayout>
            <itemlayout width="%(w)d" height="%(lh)d" condition="%(lit)s">%(resting)s
            </itemlayout>
            <focusedlayout width="%(w)d" height="%(lh)d" condition="%(lit)s">%(focused)s
            </focusedlayout>''' % {'w': AZ_W, 'dh': DOT_H, 'lh': LETTER_H, 'lit': lit, 'dots': dots,
                                   'resting': resting, 'focused': focused}


def letter_items():
    items = ''
    for letter in LETTERS:
        clicks = ['ClearProperty(silo.browse.letter,home)' if letter == 'All'
                  else 'SetProperty(silo.browse.letter,%s,home)' % letter]
        for kind in ('movies', 'tvshows'):
            clicks.append('<onclick condition="String.IsEqual(%s,%s)">SetProperty(silo.browse.path,%s,home)'
                          % (TYPE, kind, letter_path(kind, letter)))
            # The open view loads the letter's titles (the others stay empty).
            for _, view, _ in VIEWS:
                clicks.append('<onclick condition="String.IsEqual(%s,%s) + %s">SetProperty(silo.browse.vpath.%s,%s,home)'
                              % (TYPE, kind, view_is(view, kind), view, letter_path(kind, letter)))
        items += '''
                <item>
                    <label>%s</label>%s
                </item>''' % (letter, ''.join(
                    '\n                    ' + (c + '</onclick>' if c.startswith('<onclick') else '<onclick>%s</onclick>' % c)
                    for c in clicks))
    return items


def panel(control_id, content, right, visible, up='noop', hero=False, left='<onleft>noop</onleft>'):
    """The poster grid (hero: the hero view's smaller one under the hero):
    content is its <content> element."""
    return '''        <control type="panel" id="%(id)d">
            <left>%(gx)d</left><top>%(gy)d</top>
            <width>%(gw)d</width><height>%(gh)d</height>
            <orientation>vertical</orientation>
            <visible>%(visible)s</visible>
            <onright>%(right)s</onright>
            %(left)s
            <onup>%(up)s</onup>
            <scrolltime tween="cubic" easing="out">280</scrolltime>
            <!-- Details, not Kodi's play or open (SiloKodiConnect's info page, else Kodi's). -->
            <!-- A box set's card opens the box set (SiloKodiConnect's page for Kodi's movie set). -->
            <onclick condition="System.AddonIsEnabled(plugin.video.silokodiconnect) + %(box)s">RunPlugin(plugin://plugin.video.silokodiconnect/?mode=info&amp;type=set&amp;dbid=$INFO[ListItem.SetId])</onclick>
            <onclick condition="System.AddonIsEnabled(plugin.video.silokodiconnect) + !%(box)s">RunPlugin(plugin://plugin.video.silokodiconnect/?mode=info&amp;type=$INFO[ListItem.DBType]&amp;dbid=$INFO[ListItem.DBID])</onclick>
            <onclick condition="!System.AddonIsEnabled(plugin.video.silokodiconnect)">Action(Info)</onclick>
            <itemlayout width="%(iw)d" height="%(ih)d">%(card)s
            </itemlayout>
            <focusedlayout width="%(iw)d" height="%(ih)d">%(card_focused)s
            </focusedlayout>
            %(content)s
        </control>
''' % dict({'box': BOX_SET, 'id': control_id, 'gx': GRID_X, 'gy': GRID_TOP, 'gw': COLS * ITEM_W, 'gh': 1080 - GRID_TOP,
            'visible': visible, 'right': right, 'iw': ITEM_W, 'ih': ITEM_H, 'card': card(False),
            'card_focused': card(True, control_id), 'content': content, 'up': up, 'left': left},
           **({'gy': HERO_GRID_TOP, 'gw': HERO_COLS * HERO_ITEM_W, 'gh': 1080 - HERO_GRID_TOP, 'iw': HERO_ITEM_W,
               'ih': HERO_ITEM_H, 'card': card(False, control_id, (HERO_POSTER_W, HERO_POSTER_H)),
               'card_focused': card(True, control_id, (HERO_POSTER_W, HERO_POSTER_H))} if hero else {}))


def sort_current(kind, value):
    """The kind's sort is value (none chosen yet reads as Title)."""
    current = 'String.IsEqual(Skin.String(silo.sort.%s),%s)' % (kind, value)
    return '[%s | String.IsEmpty(Skin.String(silo.sort.%s))]' % (current, kind) if value == 'title' else current


def sort_controls():
    """Silo's Sort button above the grid and its list, shown while either
    has focus. Choosing a sort applies it and goes back to the grid's top."""
    items = ''
    for label, value, desc, kinds, _ in SORTS:
        clicks = []
        for kind in kinds:
            this = 'String.IsEqual(%s,%s)' % (TYPE, kind)
            same, other = '%s + %s' % (this, sort_current(kind, value)), '%s + !%s' % (this, sort_current(kind, value))
            desc_now = 'Skin.HasSetting(silo.sort.%s.desc)' % kind
            # The same sort again flips it. The skin string is set last, so
            # the conditions before it still see the old sort.
            clicks += [(same + ' + ' + desc_now, 'SetProperty(silo.browse.order,ascending,home)'),
                       (same + ' + !' + desc_now, 'SetProperty(silo.browse.order,descending,home)'),
                       (same, 'Skin.ToggleSetting(silo.sort.%s.desc)' % kind),
                       (other, ('Skin.SetBool(silo.sort.%s.desc)' if desc else 'Skin.Reset(silo.sort.%s.desc)') % kind),
                       (other, 'SetProperty(silo.browse.order,%s,home)' % ('descending' if desc else 'ascending')),
                       (other, 'SetProperty(silo.browse.sort,%s,home)' % value),
                       (other, 'Skin.SetString(silo.sort.%s,%s)' % (kind, value))]
        # Back to the grid's top, and again once the re-sorted list is in
        # (the silo_sort_top timer): Kodi reselects the title that was selected.
        clicks += focus_view('SetFocus(%d,0,absolute)')
        clicks.append((None, 'SetProperty(silo.browse.resort,1,home)'))
        items += '''
                <item>
                    <label>%s</label>
                    <property name="sort">%s</property>%s
                    <visible>%s</visible>
                </item>''' % (label, value, ''.join(
            '\n                    <onclick%s>%s</onclick>' % (' condition="%s"' % c if c else '', a) for c, a in clicks),
            ' | '.join('String.IsEqual(%s,%s)' % (TYPE, kind) for kind in kinds))
    def row(focused):
        # The chosen sort's row has Silo's tick, and its direction (a word and
        # an arrow) on the right. A condition compares with another info label
        # as it is; none chosen yet means Title.
        chosen = '[%s]' % ' | '.join(
            '[String.IsEqual(%s,%s) + [String.IsEqual(ListItem.Property(sort),Skin.String(silo.sort.%s)) | '
            '[String.IsEqual(ListItem.Property(sort),title) + String.IsEmpty(Skin.String(silo.sort.%s))]]]'
            % (TYPE, kind, kind, kind) for kind in KINDS)
        # The focused row is black on the white pill only while the list has
        # focus: with the Sort button focused it is drawn as the others.
        lit = 'Control.HasFocus(%d)' % SORT_LIST_ID
        def parts(colour, dim, visible):
            both = lambda c: '<visible>%s</visible>' % ' + '.join(x for x in (c, visible) if x)
            return '''
                    <control type="image">
                        <left>22</left><top>%(iy)d</top><width>26</width><height>26</height>
                        <texture colordiffuse="%(colour)s">silo/check.png</texture>
                        %(v_chosen)s
                    </control>
                    <control type="label">
                        <left>62</left><width>%(lw)d</width><height>%(row)d</height>
                        <aligny>center</aligny>
                        <font>silo_meta</font>
                        <textcolor>%(colour)s</textcolor>
                        <label>$INFO[ListItem.Label]</label>
                        %(v)s
                    </control>
                    <control type="label">
                        <right>56</right><width>140</width><height>%(row)d</height>
                        <align>right</align><aligny>center</aligny>
                        <font>silo_meta</font>
                        <textcolor>%(dim)s</textcolor>
                        <label>$VAR[SiloSortDirection]</label>
                        %(v_chosen)s
                    </control>
                    <control type="image">
                        <right>22</right><top>%(ay)d</top><width>22</width><height>22</height>
                        <texture colordiffuse="%(colour)s">$VAR[SiloSortArrowIcon]</texture>
                        %(v_chosen)s
                    </control>''' % {'box': BOX_SET, 'iy': (SORT_ROW - 26) // 2, 'ay': (SORT_ROW - 22) // 2, 'lw': SORT_W - 260,
                                     'row': SORT_ROW, 'colour': colour, 'dim': dim, 'v': both(''),
                                     'v_chosen': both(chosen)}
        if not focused:
            return parts(TEXT, '99EDEDED', '')
        return '''
                    <control type="image">
                        <left>4</left><top>4</top><width>%(w)d</width><height>%(h)d</height>
                        <texture border="28" colordiffuse="%(text)s">silo/pill.png</texture>
                        <visible>%(lit)s</visible>
                    </control>''' % {'w': SORT_W - 40, 'h': SORT_ROW - 8, 'text': TEXT, 'lit': lit} \
            + parts('FF000000', '8C000000', lit) + parts(TEXT, '99EDEDED', '!' + lit)
    # OK or Down opens the list on the current sort (its place among the
    # sorts the kind offers).
    open_list = ''
    for kind in ('movies', 'tvshows'):
        offered = [value for _, value, _, kinds, _ in SORTS if kind in kinds]
        for index, value in enumerate(offered):
            condition = 'String.IsEqual(%s,%s) + %s' % (TYPE, kind, sort_current(kind, value))
            for action in ('onclick', 'ondown'):
                open_list += '            <%s condition="%s">SetFocus(%d,%d,absolute)</%s>\n' % (
                    action, condition, SORT_LIST_ID, index, action)
    # The card fits the kind's sorts (Series has fewer than Movies).
    frames = ''.join('''
            <control type="image">
                <width>%(w)d</width><height>%(h)d</height>
                <texture border="24" colordiffuse="F21C1F24">silo/card_landscape_mask.png</texture>
                <visible>String.IsEqual(%(type)s,%(kind)s)</visible>
            </control>''' % {'w': SORT_W, 'type': TYPE, 'kind': kind,
                            'h': SORT_HEAD + 16 + SORT_ROW * len([1 for *_, kinds, _ in SORTS if kind in kinds])}
                     for kind in KINDS)
    # Silo's Sort button: its swap icon, "Sort · Title" and the direction,
    # dimmed. It is as wide as its words; the spaces leave room for the icon.
    pill_icon = lambda colour, visible: '''
            <control type="image">
                <left>%d</left><top>%d</top><width>26</width><height>26</height>
                <texture colordiffuse="%s">silo/sort.png</texture>
                <visible>%s</visible>
            </control>''' % (SAFE_X + 26, SORT_TOP + 15, colour, visible)
    return '''        <!-- Silo's Sort: a pill above the grid, its list below it. -->
        <control type="button" id="%(pill)d">
            <left>%(x)d</left><top>%(top)d</top>
            <width>auto</width><height>56</height>
            <label>        Sort · $VAR[SiloSortLabel]  $VAR[SiloSortPillDirection]</label>
            <font>silo_meta</font>
            <textoffsetx>28</textoffsetx>
            <aligny>center</aligny>
            <textcolor>%(text)s</textcolor>
            <focusedcolor>FF000000</focusedcolor>
            <texturefocus border="28" colordiffuse="%(text)s">silo/pill.png</texturefocus>
            <texturenofocus border="28" colordiffuse="26FFFFFF">silo/pill.png</texturenofocus>
            <visible>!%(personal)s</visible>
%(open_list)s
            <onleft>noop</onleft><onright>%(unwatched)d</onright><onup>noop</onup>
        </control>%(pill_icons)s
        <!-- DROPDOWN -->
        <control type="group">
            <left>%(x)d</left><top>%(ly)d</top>
            <visible>Control.HasFocus(%(pill)d) | Control.HasFocus(%(list)d)</visible>
            <animation effect="fade" start="0" end="100" time="140">Visible</animation>%(frames)s
            <control type="label">
                <left>28</left><top>16</top><width>%(lw)d</width><height>40</height>
                <aligny>center</aligny>
                <font>silo_badge</font>
                <textcolor>99EDEDED</textcolor>
                <label>SORT BY</label>
            </control>
            <control type="list" id="%(list)d">
                <left>16</left><top>%(head)d</top><width>%(lw)d</width><height>%(lh)d</height>
                <orientation>vertical</orientation>
                <onup>%(pill)d</onup><onback>%(pill)d</onback>
                <onleft>noop</onleft><onright>noop</onright><ondown>noop</ondown>
                <itemlayout width="%(lw)d" height="%(row)d">%(normal)s
                </itemlayout>
                <focusedlayout width="%(lw)d" height="%(row)d">%(focused)s
                </focusedlayout>
                <content>%(items)s
                </content>
            </control>
        </control>
        <!-- END DROPDOWN -->
''' % {'pill': SORT_ID, 'list': SORT_LIST_ID, 'x': SAFE_X, 'top': SORT_TOP, 'text': TEXT,
       'personal': IS_PERSONAL, 'ly': SORT_TOP + 68, 'frames': frames, 'head': SORT_HEAD,
       'lw': SORT_W - 32, 'lh': len(SORTS) * SORT_ROW, 'row': SORT_ROW, 'normal': row(False), 'focused': row(True),
       'items': items, 'open_list': open_list, 'view': VIEW_ID, 'unwatched': UNWATCHED_ID,
       'pill_icons': pill_icon('FF000000', '!%s + Control.HasFocus(%d)' % (IS_PERSONAL, SORT_ID))
                     + pill_icon(TEXT, '!%s + !Control.HasFocus(%d)' % (IS_PERSONAL, SORT_ID))}


def marks(item, indent):
    """IMDb's and TMDB's marks with their scores (as the hero's), for item."""
    out = ''
    for rating, mark, width, height, top in (('imdb', 'silo/imdb.png', 60, 28, 6), ('themoviedb', 'silo/tmdb.png', 165, 30, 5)):
        # TMDB's from SiloKodiConnect's extras: Kodi's lists load only the default rating.
        score = ('%s.Art(silotmdb)' % item) if rating == 'themoviedb' else '%s.Rating(%s)' % (item, rating)
        out += """
%(i)s<control type="image">
%(i)s    <top>%(top)d</top><width>%(w)d</width><height>%(h)d</height>
%(i)s    <texture>%(mark)s</texture>
%(i)s    <visible>!String.IsEmpty(%(score)s) + %(on)s</visible>
%(i)s</control>
%(i)s<control type="label">
%(i)s    <width>auto</width><height>40</height>
%(i)s    <aligny>center</aligny>
%(i)s    <font>silo_meta</font>
%(i)s    <textcolor>%(dim)s</textcolor>
%(i)s    <label> [B]$INFO[%(score)s][/B]   </label>
%(i)s    <visible>!String.IsEmpty(%(score)s) + %(on)s</visible>
%(i)s</control>""" % {'i': indent, 'top': top, 'w': width, 'h': height, 'mark': mark, 'score': score, 'on': RATING_SHOWN[rating], 'dim': TEXT_DIM}
    return out + rt_list_marks(item, indent, TEXT_DIM)


def title_art(item, left, top, width, height, hidden='false'):
    """The title's clearlogo, or its name in Silo's title font without one;
    neither while hidden (a box set has its own name)."""
    return """
        <control type="image">
            <left>%(x)d</left><top>%(y)d</top><width>%(w)d</width><height>%(h)d</height>
            <aspectratio align="left" aligny="bottom">keep</aspectratio>
            <texture background="true">$INFO[%(item)s.Art(clearlogo)]</texture>
            <visible>!%(hidden)s</visible>
        </control>
        <control type="label">
            <left>%(x)d</left><top>%(y)d</top><width>%(w)d</width><height>%(h)d</height>
            <aligny>bottom</aligny>
            <font>silo_osd_title</font>
            <textcolor>%(text)s</textcolor>
            <label>$INFO[%(item)s.Label]</label>
            <visible>String.IsEmpty(%(item)s.Art(clearlogo)) + !%(hidden)s</visible>
        </control>""" % {'x': left, 'y': top, 'w': width, 'h': height, 'item': item, 'text': TEXT, 'hidden': hidden}


# A title's facts as the hero's: year, runtime (a film), genre (SiloKodiConnect's
# first, kept in the library as silogenre), and its age rating.
def facts(item):
    return ('$INFO[%(i)s.Mpaa,,  ·  ]$INFO[%(i)s.Year]$INFO[%(i)s.Duration(mins),  ·  , min]'
            '$INFO[%(i)s.Art(silogenre),  ·  ,]' % {'i': item})


def view_controls():
    """The View pill (right of Sort, at the right edge), its list, and the
    hero and list views with their details."""
    hero, lst = 'Container(%d).ListItem' % HERO_ID, 'Container(%d).ListItem' % LIST_VIEW_ID
    hero_box = BOX_SET.replace('ListItem.', hero + '.')
    pick = ''
    for label, view, control in VIEWS:
        clicks = [(c, a) for c, a in [(None, 'ClearProperty(silo.browse.vpath.%s,home)' % v) for _, v, _ in VIEWS if v != view]]
        clicks.append((None, 'SetProperty(silo.browse.vpath.%s,$INFO[%s],home)' % (view, PATH)))
        for kind in KINDS:
            this = 'String.IsEqual(%s,%s)' % (TYPE, kind)
            clicks.append((this, 'Skin.Reset(silo.view.%s)' % kind if view == 'grid' else 'Skin.SetString(silo.view.%s,%s)' % (kind, view)))
        # Focus once its titles are in (silo_browse_view_focus).
        clicks.append((None, 'SetProperty(silo.browse.focusview,1,home)'))
        pick += """
                <item>
                    <label>%s</label>
                    <property name="view">%s</property>%s
                </item>""" % (label, view, ''.join('\n                    <onclick%s>%s</onclick>' % (
                    ' condition="%s"' % c if c else '', a) for c, a in clicks))
    chosen = '[%s]' % ' | '.join('[String.IsEqual(ListItem.Property(view),%s) + %s]' % (v, view_is(v)) for _, v, _ in VIEWS)
    lit = 'Control.HasFocus(%d)' % VIEW_LIST_ID
    def row(focused):
        def parts(colour, visible):
            v = ' + '.join(x for x in (visible,) if x)
            return """
                    <control type="image">
                        <left>22</left><top>%(iy)d</top><width>26</width><height>26</height>
                        <texture colordiffuse="%(c)s">silo/check.png</texture>
                        <visible>%(chosen)s%(v2)s</visible>
                    </control>
                    <control type="label">
                        <left>62</left><width>200</width><height>%(row)d</height>
                        <aligny>center</aligny>
                        <font>silo_meta</font>
                        <textcolor>%(c)s</textcolor>
                        <label>$INFO[ListItem.Label]</label>%(v1)s
                    </control>""" % {'iy': (SORT_ROW - 26) // 2, 'c': colour, 'chosen': chosen, 'row': SORT_ROW,
                                     'v2': ' + ' + v if v else '', 'v1': '\n                        <visible>%s</visible>' % v if v else ''}
        if not focused:
            return parts(TEXT, '')
        return """
                    <control type="image">
                        <left>4</left><top>4</top><width>%(w)d</width><height>%(h)d</height>
                        <texture border="28" colordiffuse="%(text)s">silo/pill.png</texture>
                        <visible>%(lit)s</visible>
                    </control>""" % {'w': VIEW_W - 40, 'h': SORT_ROW - 8, 'text': TEXT, 'lit': lit} \
            + parts('FF000000', lit) + parts(TEXT, '!' + lit)
    # OK or Down on the pill opens the list on the current view.
    open_list = ''.join('            <%s condition="%s">SetFocus(%d,%d,absolute)</%s>\n' % (a, view_is(v), VIEW_LIST_ID, n, a)
                        for n, (_, v, _) in enumerate(VIEWS) for a in ('onclick', 'ondown'))
    return """        <!-- Browse's views: a View pill on Sort's line, at the right, and its
             list below it (shown while either has focus, as Sort's). -->
        <control type="button" id="%(pill)d">
            <right>%(px)d</right><top>%(top)d</top>
            <width>%(pw)d</width><height>56</height>
            <label>View · $VAR[SiloBrowseViewLabel]</label>
            <font>silo_meta</font>
            <align>center</align><aligny>center</aligny>
            <textcolor>%(text)s</textcolor>
            <focusedcolor>FF000000</focusedcolor>
            <texturefocus border="28" colordiffuse="%(text)s">silo/pill.png</texturefocus>
            <texturenofocus border="28" colordiffuse="26FFFFFF">silo/pill.png</texturenofocus>
            <visible>!%(personal)s</visible>
%(open_list)s            <onleft>%(unwatched)d</onleft><onright>noop</onright><onup>noop</onup>
        </control>
        <!-- Unwatched only (Infuse): a toggle left of View; Down goes to the titles. -->
        <control type="button" id="%(unwatched)d">
            <right>%(ux)d</right><top>%(top)d</top>
            <width>%(uw)d</width><height>56</height>
            <label>Show · $VAR[SiloBrowseShowLabel]</label>
            <font>silo_meta</font>
            <align>center</align><aligny>center</aligny>
            <textcolor>%(text)s</textcolor>
            <focusedcolor>FF000000</focusedcolor>
            <texturefocus border="28" colordiffuse="%(text)s">silo/pill.png</texturefocus>
            <texturenofocus border="28" colordiffuse="26FFFFFF">silo/pill.png</texturenofocus>
            <visible>!%(personal)s</visible>
            <onclick>Skin.ToggleSetting(silo.unwatched)</onclick>
%(unwatched_down)s            <onleft>%(sort)d</onleft><onright>%(pill)d</onright><onup>noop</onup>
        </control>
        <!-- DROPDOWN -->
        <control type="group">
            <right>%(px)d</right><top>%(ly)d</top><width>%(vw)d</width>
            <visible>Control.HasFocus(%(pill)d) | Control.HasFocus(%(list)d)</visible>
            <animation effect="fade" start="0" end="100" time="140">Visible</animation>
            <control type="image">
                <width>%(vw)d</width><height>%(fh)d</height>
                <texture border="24" colordiffuse="F21C1F24">silo/card_landscape_mask.png</texture>
            </control>
            <control type="label">
                <left>28</left><top>16</top><width>%(lw)d</width><height>40</height>
                <aligny>center</aligny>
                <font>silo_badge</font>
                <textcolor>99EDEDED</textcolor>
                <label>VIEW</label>
            </control>
            <control type="list" id="%(list)d">
                <left>16</left><top>%(head)d</top><width>%(lw)d</width><height>%(lh)d</height>
                <orientation>vertical</orientation>
                <onup>%(pill)d</onup><onback>%(pill)d</onback>
                <onleft>noop</onleft><onright>noop</onright><ondown>noop</ondown>
                <itemlayout width="%(lw)d" height="%(row)d">%(normal)s
                </itemlayout>
                <focusedlayout width="%(lw)d" height="%(row)d">%(focused)s
                </focusedlayout>
                <content>%(items)s
                </content>
            </control>
        </control>
        <!-- END DROPDOWN -->
        <!-- HERO BACKDROP -->
        <control type="group">
            <visible>!%(personal)s + %(is_hero)s</visible>
            <control type="image">
                <left>576</left><top>0</top><width>1344</width><height>756</height>
                <aspectratio>scale</aspectratio>
                <fadetime>240</fadetime>
                <texture background="true" colordiffuse="80FFFFFF" diffuse="silo/hero_mask.png">$VAR[SiloBrowseHeroFanart]</texture>
            </control>
            <!-- The header, Sort and View stay readable over a bright picture. -->
            <control type="image">
                <left>0</left><top>0</top><width>1920</width><height>320</height>
                <texture flipy="true" colordiffuse="CCFFFFFF">silo/scrim_bottom.png</texture>
            </control>
        </control>
        <!-- END HERO BACKDROP -->
        <!-- The hero view: the focused title over two rows of posters. -->
        <control type="group">
            <visible>!%(personal)s + %(is_hero)s</visible>%(hero_title)s
            <!-- A box set: its name, "Box set · 8 films · 2001 – 2011" and overview
                 (SiloKodiConnect's set art), as Silo's box set page. -->
            <control type="label">
                <left>%(sx)d</left><top>236</top><width>1200</width><height>130</height>
                <aligny>bottom</aligny>
                <font>silo_osd_title</font>
                <textcolor>%(text)s</textcolor>
                <label>$INFO[%(hero)s.Set]</label>
                <visible>%(hero_box)s</visible>
            </control>
            <control type="label">
                <left>%(sx)d</left><top>%(fy)d</top><width>1100</width><height>40</height>
                <aligny>center</aligny>
                <font>silo_meta</font>
                <textcolor>%(dim)s</textcolor>
                <label>Box set$INFO[%(hero)s.Art(set.silocount),  ·  ,]$INFO[%(hero)s.Art(set.siloyears),  ·  ,]</label>
                <visible>%(hero_box)s</visible>
            </control>
            <control type="textbox">
                <left>%(sx)d</left><top>%(py)d</top><width>960</width><height>62</height>
                <font>silo_detail</font>
                <textcolor>%(text)s</textcolor>
                <label>$INFO[%(hero)s.Art(set.silooverview)]</label>
                <visible>%(hero_box)s</visible>
            </control>
            <control type="grouplist">
                <visible>!%(hero_box)s</visible>
                <left>%(sx)d</left><top>%(fy)d</top><width>1100</width><height>40</height>
                <orientation>horizontal</orientation>
                <usecontrolcoords>true</usecontrolcoords>
                <control type="label">
                    <width>auto</width><height>40</height>
                    <aligny>center</aligny>
                    <font>silo_meta</font>
                    <textcolor>%(dim)s</textcolor>
                    <label>%(hero_facts)s   </label>
                </control>%(hero_marks)s
            </control>
            <control type="textbox">
                <left>%(sx)d</left><top>%(py)d</top><width>960</width><height>62</height>
                <font>silo_detail</font>
                <textcolor>%(dim)s</textcolor>
                <label>$INFO[%(hero)s.Plot]</label>
                <visible>!%(hero_box)s</visible>
            </control>
        </control>
        <!-- The list view's details: the focused title's poster and facts. -->
        <control type="group">
            <visible>!%(personal)s + %(is_list)s</visible>
            <control type="image">
                <left>576</left><top>0</top><width>1344</width><height>756</height>
                <aspectratio>stretch</aspectratio>
                <fadetime>240</fadetime>
                <texture background="true" colordiffuse="%(backdrop)s" diffuse="silo/hero_mask.png">$INFO[%(lst)s.Art(fanart)]</texture>
            </control>
            <control type="image">
                <left>%(dx)d</left><top>%(dy)d</top><width>300</width><height>450</height>
                <aspectratio>scale</aspectratio>
                <texture background="true" diffuse="silo/card_poster_mask.png" fallback="colors/grey.png">$INFO[%(lst)s.Art(poster)]</texture>
            </control>%(list_title)s
            <control type="label">
                <left>%(ix)d</left><top>%(iy)d</top><width>%(iw)d</width><height>40</height>
                <font>silo_meta</font>
                <textcolor>%(dim)s</textcolor>
                <label>%(list_facts)s</label>
            </control>
            <control type="label">
                <left>%(ix)d</left><top>%(by)d</top><width>%(iw)d</width><height>40</height>
                <font>silo_meta</font>
                <textcolor>%(dim)s</textcolor>
                <label>$INFO[%(lst)s.Art(silobadge1)]$INFO[%(lst)s.Art(silobadge2),  ·  ,]$INFO[%(lst)s.Art(silobadge3),  ·  ,]</label>
            </control>
            <control type="grouplist">
                <left>%(ix)d</left><top>%(ry)d</top><width>%(iw)d</width><height>40</height>
                <orientation>horizontal</orientation>
                <usecontrolcoords>true</usecontrolcoords>%(list_marks)s
            </control>
            <control type="textbox">
                <left>%(ix)d</left><top>%(cy)d</top><width>%(iw)d</width><height>90</height>
                <font>silo_detail</font>
                <textcolor>%(dim)s</textcolor>
                <label>$INFO[%(lst)s.Art(silocast)]</label>
            </control>
            <control type="textbox">
                <left>%(dx)d</left><top>%(ply)d</top><width>%(plw)d</width><height>260</height>
                <font>silo_detail</font>
                <textcolor>%(dim)s</textcolor>
                <label>$INFO[%(lst)s.Plot]</label>
            </control>
        </control>
        <control type="list" id="%(lv)d">
            <left>%(lx)d</left><top>%(gy)d</top><width>%(lvw)d</width><height>%(gh)d</height>
            <orientation>vertical</orientation>
            <visible>!%(personal)s + %(is_list)s</visible>
            <onup>%(sort)d</onup><onright>%(az)d</onright><onleft>noop</onleft>
            <scrolltime tween="cubic" easing="out">200</scrolltime>
            <!-- A box set's card opens the box set (SiloKodiConnect's page for Kodi's movie set). -->
            <onclick condition="System.AddonIsEnabled(plugin.video.silokodiconnect) + %(box)s">RunPlugin(plugin://plugin.video.silokodiconnect/?mode=info&amp;type=set&amp;dbid=$INFO[ListItem.SetId])</onclick>
            <onclick condition="System.AddonIsEnabled(plugin.video.silokodiconnect) + !%(box)s">RunPlugin(plugin://plugin.video.silokodiconnect/?mode=info&amp;type=$INFO[ListItem.DBType]&amp;dbid=$INFO[ListItem.DBID])</onclick>
            <onclick condition="!System.AddonIsEnabled(plugin.video.silokodiconnect)">Action(Info)</onclick>
            <itemlayout width="%(lvw)d" height="%(lrow)d">%(lrow_normal)s
            </itemlayout>
            <focusedlayout width="%(lvw)d" height="%(lrow)d">%(lrow_focused)s
            </focusedlayout>
            <content target="videos" sortby="$INFO[%(sort_by)s]" sortorder="$INFO[%(sort_order)s]">$INFO[%(vpath_list)s]$VAR[SiloBrowseFilter_list]</content>
        </control>
""" % {'box': BOX_SET, 'list': VIEW_LIST_ID, 'pill': VIEW_ID, 'px': SAFE_X + AZ_W + 24, 'pw': 260, 'top': SORT_TOP,
       'unwatched': UNWATCHED_ID, 'ux': SAFE_X + AZ_W + 24 + 260 + 16, 'uw': 300,
       'unwatched_down': ''.join('            <ondown condition="%s">%s</ondown>\n' % (c, a) for c, a in focus_view()),
       'ly': SORT_TOP + 68, 'open_list': open_list, 'fh': SORT_HEAD + 16 + SORT_ROW * len(VIEWS), 'head': SORT_HEAD,
       'x': SAFE_X, 'text': TEXT, 'dim': TEXT_DIM, 'personal': IS_PERSONAL, 'sort': SORT_ID, 'vw': VIEW_W,
       'lw': VIEW_W - 32,
       'lh': SORT_ROW * len(VIEWS), 'row': SORT_ROW, 'normal': row(False), 'focused': row(True), 'items': pick,
       'is_hero': view_is('hero'), 'is_list': view_is('list'), 'hero': hero, 'lst': lst, 'backdrop': GRID_BACKDROP,
       'hero_title': title_art(hero, SAFE_X, 236, 760, 130, hero_box).replace('\n        ', '\n            '),
       'hero_box': hero_box,
       'sx': SAFE_X, 'fy': 378, 'py': 424, 'hero_facts': facts(hero), 'hero_marks': marks(hero, '                '),
       'dx': SAFE_X + 812, 'dy': GRID_TOP, 'ix': SAFE_X + 812 + 330, 'iw': 1920 - SAFE_X - AZ_W - 24 - (SAFE_X + 812 + 330),
       'list_title': title_art(lst, SAFE_X + 812 + 330, GRID_TOP, 1920 - SAFE_X - AZ_W - 24 - (SAFE_X + 812 + 330), 140).replace('\n        ', '\n            '),
       'iy': GRID_TOP + 156, 'by': GRID_TOP + 204, 'ry': GRID_TOP + 252, 'cy': GRID_TOP + 306,
       'list_facts': facts(lst), 'list_marks': marks(lst, '                '),
       'ply': GRID_TOP + 480, 'plw': 1920 - SAFE_X - AZ_W - 24 - (SAFE_X + 812),
       'lv': LIST_VIEW_ID, 'lx': SAFE_X - 6, 'gy': GRID_TOP, 'lvw': 780, 'gh': 1080 - GRID_TOP - 24, 'az': AZ_ID,
       'box': BOX_SET, 'lrow': LIST_ROW, 'lrow_normal': list_row(False), 'lrow_focused': list_row(True),
       'sort_by': SORT_BY, 'sort_order': SORT_ORDER, 'vpath_list': VPATH % 'list'}


VIEW_W = 300  # the View list's card


def list_row(focused):
    """A row of the list view: the title, its year on the right, and Silo's
    watched tick; the focused row black on the white pill while it has focus."""
    lit = 'Control.HasFocus(%d)' % LIST_VIEW_ID
    def parts(colour, dim, visible):
        v = '\n                    <visible>%s</visible>' % visible if visible else ''
        return """
                <control type="label">
                    <left>28</left><width>600</width><height>%(row)d</height>
                    <aligny>center</aligny>
                    <font>silo_meta</font>
                    <textcolor>%(c)s</textcolor>
                    <label>$INFO[ListItem.Label]</label>%(v)s
                </control>
                <control type="label">
                    <right>28</right><width>140</width><height>%(row)d</height>
                    <align>right</align><aligny>center</aligny>
                    <font>silo_meta</font>
                    <textcolor>%(d)s</textcolor>
                    <label>$INFO[ListItem.Year]</label>%(v)s
                </control>""" % {'row': LIST_ROW, 'c': colour, 'd': dim, 'v': v}
    if not focused:
        return parts(TITLE_DIM, SUB_DIM, '')
    return """
                <control type="image">
                    <left>4</left><top>4</top><width>772</width><height>%(h)d</height>
                    <texture border="28" colordiffuse="%(text)s">silo/pill.png</texture>
                    <visible>%(lit)s</visible>
                </control>""" % {'h': LIST_ROW - 8, 'text': TEXT, 'lit': lit} \
        + parts('FF000000', '8C000000', lit) + parts(TEXT, TEXT_DIM, '!' + lit)


def is_list(key):
    return 'String.IsEqual(%s,%s) + %s' % (TYPE, key, IS_PERSONAL)


def empty_note(key, list_id):
    """Shown when a personal list has nothing in it."""
    return '''        <control type="label">
            <left>%(gx)d</left><top>%(top)d</top>
            <width>%(gw)d</width><height>60</height>
            <font>silo_plot</font>
            <textcolor>%(dim)s</textcolor>
            <label>%(note)s</label>
            <visible>%(personal)s + !Container(%(list)d).IsUpdating + Integer.IsEqual(Container(%(list)d).NumItems,0)</visible>
        </control>
''' % {'gx': SAFE_X, 'top': GRID_TOP + 20, 'gw': 1920 - 2 * SAFE_X, 'dim': TEXT_DIM, 'personal': is_list(key),
       'list': list_id, 'note': 'No new episodes of your shows in the next two weeks.' if key == 'comingsoon'
       else 'Nothing here yet. Add titles from Silo and they appear here.'}


# Silo's collections, here rather than in Kodi's library window (where OK
# plays): silo.browse.type collections shows the fan cards (silo.browse.list.collections,
# SiloKodiConnect's mode=collections); one chosen, or one from Home's Collections
# row, is type collection: its titles by name with the A-Z (SiloKodiConnect's
# jump), OK opening details. A card opens its collection in a window of its
# own (COLLECTION_WINDOW, this window again), so Kodi's Back returns to the
# cards: Back in a window always closes it, whatever a control's onback does.
FANS_ID, COLLECTION_ID, COLLECTION_AZ = 56, 55, 61
# The library's genres as Silo's chips (silo.browse.type genres, the list in
# silo.browse.list.genres, the kind in silo.browse.genrekind). One chosen opens
# its titles in COLLECTION_WINDOW, as a collection does, with Browse's sorts and
# views (silo.browse.genre its name) and no A-Z: a letter's filter drops the genre.
GENRES_ID = 59
GENRE = 'Window(Home).Property(silo.browse.genre)'
COLLECTION_WINDOW = 1193
JUMP_LETTERS = ['#'] + [chr(c) for c in range(ord('A'), ord('Z') + 1)]


def collection_controls():
    from build_browse import fan_card, FAN_W, FAN_H, FAN_GAP
    is_fans, is_one = is_list('collections'), is_list('collection')
    grid = panel(COLLECTION_ID, '<content target="videos" sortby="title" sortorder="ascending">'
                 '$INFO[Window(Home).Property(silo.browse.list.collection)]</content>', str(COLLECTION_AZ), is_one)
    current = 'String.IsEqual(ListItem.Label,Container(%d).ListItem.SortLetter)' % COLLECTION_ID
    items = ''.join('''
                <item>
                    <label>%s</label>
                    <onclick>NotifyAll(silokodi,jump.%d.%s)</onclick>
                </item>''' % (letter, COLLECTION_ID, letter) for letter in JUMP_LETTERS)
    from build_browse import chip, CHIP_W, CHIP_H, CHIP_GAP
    genres = '''        <control type="panel" id="%(id)d">
            <left>%(gx)d</left><top>%(gy)d</top>
            <width>%(gw)d</width><height>%(gh)d</height>
            <orientation>vertical</orientation>
            <visible>%(visible)s</visible>
            <scrolltime tween="cubic" easing="out">240</scrolltime>
            <onclick>SetProperty(silo.browse.from,genres,home)</onclick>
            <onclick>SetProperty(silo.browse.genre,$INFO[ListItem.Label],home)</onclick>
            <onclick>SetProperty(silo.browse.path,$INFO[ListItem.FolderPath],home)</onclick>
            <onclick>ClearProperty(silo.browse.letter,home)</onclick>
            <onclick>ClearProperty(silo.browse.list,home)</onclick>
            <onclick>SetProperty(silo.browse.type,$INFO[Window(Home).Property(silo.browse.genrekind)],home)</onclick>
            <onclick>ActivateWindow(%(window)d)</onclick>
            <itemlayout width="%(iw)d" height="%(ih)d">%(chip)s
            </itemlayout>
            <focusedlayout width="%(iw)d" height="%(ih)d">%(chip_focused)s
            </focusedlayout>
            <content target="videos">$INFO[Window(Home).Property(silo.browse.list.genres)]</content>
        </control>
''' % {'id': GENRES_ID, 'gx': GRID_X, 'gy': GRID_TOP, 'gw': 1920 - 2 * SAFE_X, 'gh': 1080 - GRID_TOP,
       'visible': is_list('genres'), 'window': COLLECTION_WINDOW, 'iw': CHIP_W + CHIP_GAP, 'ih': CHIP_H + CHIP_GAP,
       'chip': chip(False, GENRES_ID), 'chip_focused': chip(True, GENRES_ID)}
    return genres + grid + '''        <control type="list" id="%(az)d">
            <visible>%(one)s</visible>
            <left>%(ax)d</left><top>%(gy)d</top>
            <width>%(aw)d</width><height>%(gh)d</height>
            <orientation>vertical</orientation>
            <onleft>%(grid)d</onleft><onright>noop</onright>
            <scrolltime tween="cubic" easing="out">200</scrolltime>%(layouts)s
            <content>%(items)s
            </content>
        </control>
        <control type="panel" id="%(fans)d">
            <left>%(gx)d</left><top>%(gy)d</top>
            <width>%(fw)d</width><height>%(gh)d</height>
            <orientation>vertical</orientation>
            <visible>%(is_fans)s</visible>
            <scrolltime tween="cubic" easing="out">280</scrolltime>
            <onclick>SetProperty(silo.browse.from,collections,home)</onclick>
            <onclick>SetProperty(silo.browse.title,$INFO[ListItem.Label],home)</onclick>
            <onclick>SetProperty(silo.browse.list.collection,$INFO[ListItem.FolderPath],home)</onclick>
            <onclick>SetProperty(silo.browse.list,$INFO[ListItem.FolderPath],home)</onclick>
            <onclick>SetProperty(silo.browse.type,collection,home)</onclick>
            <onclick>ActivateWindow(%(collection_window)d)</onclick>
            <itemlayout width="%(iw)d" height="%(ih)d">%(fan)s
            </itemlayout>
            <focusedlayout width="%(iw)d" height="%(ih)d">%(fan_focused)s
            </focusedlayout>
            <content target="videos">$INFO[Window(Home).Property(silo.browse.list.collections)]</content>
        </control>
''' % {'az': COLLECTION_AZ, 'one': is_one, 'ax': 1920 - SAFE_X - AZ_W, 'gy': GRID_TOP, 'aw': AZ_W,
       'gh': 1080 - GRID_TOP, 'grid': COLLECTION_ID,
       'layouts': letter_layouts(COLLECTION_AZ, current), 'items': items, 'fans': FANS_ID, 'gx': GRID_X,
       'fw': 3 * (FAN_W + FAN_GAP), 'is_fans': is_fans, 'iw': FAN_W + FAN_GAP, 'ih': FAN_H + FAN_GAP,
       'fan': fan_card(False, FANS_ID), 'fan_focused': fan_card(True, FANS_ID),
       'collection_window': COLLECTION_WINDOW}


def arrange(text):
    """The window with the hero's backdrop behind the header and the Sort and
    View lists above everything (Kodi draws controls in order)."""
    backdrops = re.findall(r'        <!-- HERO BACKDROP -->\n(.*?)        <!-- END HERO BACKDROP -->\n', text, re.S)
    dropdowns = re.findall(r'        <!-- DROPDOWN -->\n(.*?)        <!-- END DROPDOWN -->\n', text, re.S)
    text = re.sub(r'        <!-- (HERO BACKDROP|DROPDOWN) -->\n.*?        <!-- END \1 -->\n', '', text, flags=re.S)
    frame = '        <include content="SiloFrame">'
    text = text.replace(frame, ''.join(backdrops) + frame, 1)
    spinner = '        <!-- A list from SiloKodiConnect still loading. -->'
    return text.replace(spinner, ''.join(dropdowns) + spinner, 1)


def build():
    return arrange('''<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by tools/build_library.py: edit that, not this. -->
<window id="%(window)d">
    <!-- Back from a trailer started from an info page (Kodi leaves it playing): stop it, which reopens the page. -->
    <!-- A video left playing behind the menus (Back from the player, a trailer's
         page, or Live TV left from the guide): stopped, as in Silo's apps, since
         these pages cover the screen and there's no way back to it. Kodi saves
         where it stopped; the TV guide keeps Live TV playing in its preview. -->
    <onload condition="Player.HasVideo">PlayerControl(Stop)</onload>
    <defaultcontrol always="true">%(grid)d</defaultcontrol>
%(onload)s
    <backgroundcolor>%(background)s</backgroundcolor>
    <controls>
        <include>SiloPage</include>
        <!-- The focused title's artwork, faint behind the grid. -->
        <control type="image">
            <left>576</left><top>0</top><width>1344</width><height>756</height>
            <aspectratio>stretch</aspectratio>
            <fadetime>240</fadetime>
            <texture background="true" colordiffuse="%(backdrop)s" diffuse="silo/hero_mask.png">$VAR[SiloLibraryFanart]</texture>
        </control>
        <include content="SiloFrame">
            <param name="title">$VAR[SiloLibraryTitle]</param>
            <param name="sub">$VAR[SiloLibrarySub]</param>
        </include>
%(panels)s        <!-- Silo's A-Z (not in a genre: a letter's filter would drop it). -->
        <control type="list" id="%(az)d">
            <visible>!%(personal)s + String.IsEmpty(%(genre)s)</visible>
            <left>%(ax)d</left><top>%(gy)d</top>
            <width>%(aw)d</width><height>%(gh)d</height>
            <orientation>vertical</orientation>
%(az_left)s
            <onright>noop</onright>
            <scrolltime tween="cubic" easing="out">200</scrolltime>%(layouts)s
            <content>%(items)s
            </content>
        </control>
        <!-- A list from SiloKodiConnect still loading. -->
        <control type="image">
            <left>928</left><top>508</top><width>64</width><height>64</height>
            <texture colordiffuse="99EDEDED">silo/spinner_arc.png</texture>
            <animation effect="rotate" start="0" end="-360" center="auto" time="900" loop="true" condition="true">Conditional</animation>
            <visible>%(loading)s</visible>
        </control>
        <!-- A trailer from an info page: its cover (Includes_SiloFrame.xml). -->
        <include>SiloTrailerCover</include>
    </controls>
</window>
''' % {'backdrop': GRID_BACKDROP, 'window': WINDOW_ID, 'grid': GRID_ID, 'background': BACKGROUND, 'letter': LETTER, 'gx': GRID_X,
       'gy': GRID_TOP, 'gh': 1080 - GRID_TOP, 'az': AZ_ID, 'personal': IS_PERSONAL, 'genre': GENRE,
       'loading': ' | '.join('[%s + Container(%d).IsUpdating]' % (is_list(key), list_id)
                             for key, list_id in [('collections', 56), ('collection', 55)]
                             + [(key, list_id) for key, (_, list_id) in PERSONAL.items()]),
       'onload': ''.join('    <onload condition="String.IsEqual(%s,%s)">SetProperty(silo.browse.sort,%s,home)</onload>\n'
                         '    <onload condition="String.IsEqual(%s,%s) + !String.IsEmpty(Skin.String(silo.sort.%s))">'
                         'SetProperty(silo.browse.sort,$INFO[Skin.String(silo.sort.%s)],home)</onload>\n'
                         '    <onload condition="String.IsEqual(%s,%s) + Skin.HasSetting(silo.sort.%s.desc)">'
                         'SetProperty(silo.browse.order,descending,home)</onload>\n'
                         '    <onload condition="String.IsEqual(%s,%s) + !Skin.HasSetting(silo.sort.%s.desc)">'
                         'SetProperty(silo.browse.order,ascending,home)</onload>\n'
                         % (TYPE, kind, 'title', TYPE, kind, kind, kind, TYPE, kind, kind, TYPE, kind, kind)
                         for kind in ('movies', 'tvshows'))
                 + ''.join('    <onload condition="%s">SetFocus(%d)</onload>\n' % (is_list(key), list_id)
                         for key, (_, list_id) in PERSONAL.items())
                 + '    <onload condition="%s">SetFocus(%d)</onload>\n' % (is_list('collections'), FANS_ID)
                 + '    <onload condition="%s">SetFocus(%d)</onload>\n' % (is_list('collection'), COLLECTION_ID)
                 + '    <onload condition="%s">SetFocus(%d)</onload>\n' % (is_list('genres'), GENRES_ID)
                 # The open view loads Browse's path (the others none), and the
                 # hero or list view takes focus once its titles are in.
                 + ''.join('    <onload condition="%s">%s</onload>\n' % (c, a) for c, a in show_view())
                 + '    <onload condition="!%s + [%s | %s]">SetProperty(silo.browse.focusview,1,home)</onload>\n'
                 % (IS_PERSONAL, view_is('hero'), view_is('list')),
       'panels': panel(GRID_ID, '<content target="videos" sortby="$INFO[%s]" sortorder="$INFO[%s]">'
                       '$INFO[%s]$VAR[SiloBrowseFilter_grid]</content>' % (SORT_BY, SORT_ORDER, VPATH % 'grid'), str(AZ_ID),
                       '!%s + %s' % (IS_PERSONAL, view_is('grid')), str(SORT_ID))
                 + panel(HERO_ID, '<content target="videos" sortby="$INFO[%s]" sortorder="$INFO[%s]">'
                         '$INFO[%s]$VAR[SiloBrowseFilter_hero]</content>' % (SORT_BY, SORT_ORDER, VPATH % 'hero'), str(AZ_ID),
                         '!%s + %s' % (IS_PERSONAL, view_is('hero')), str(SORT_ID), hero=True)
                 + sort_controls() + view_controls()
                 # Each grid has its own path (only the open list's is set: Kodi
                 # loads a grid's path even while it is hidden).
                 + ''.join(panel(list_id, '<content target="videos">$INFO[Window(Home).Property(silo.browse.list.%s)]'
                                 '</content>' % key, 'noop', is_list(key))
                           + empty_note(key, list_id) for key, (_, list_id) in PERSONAL.items())
                 + collection_controls(),
       'ax': 1920 - SAFE_X - AZ_W,
       'aw': AZ_W, 'layouts': letter_layouts(), 'items': letter_items(),
       'az_left': ''.join('            <onleft condition="%s">%d</onleft>\n' % (c, ctrl) for c, ctrl in
                          [(view_is(v), ctrl) for _, v, ctrl in VIEWS]).rstrip('\n')})


VARIABLES = '''
    <!-- Silo Skyline library (tools/build_library.py) -->
    <variable name="SiloLibraryTitle">
%(personal)s        <value condition="String.IsEqual(%(type)s,collections)">Collections</value>
        <value condition="String.IsEqual(%(type)s,genres)">Genres</value>
        <value condition="!String.IsEmpty(%(genre)s)">$INFO[%(genre)s]</value>
        <value condition="String.IsEqual(%(type)s,collection)">$INFO[Window(Home).Property(silo.browse.title)]</value>
        <value condition="String.IsEqual(%(type)s,tvshows)">Series</value>
        <value>Movies</value>
    </variable>
    <variable name="SiloLibrarySub">
%(subs)s        <value condition="String.IsEqual(%(type)s,collections)">$INFO[Container(56).NumItems,, collections]</value>
        <value condition="String.IsEqual(%(type)s,genres)">$INFO[Container(%(genres)d).NumItems,, genres]</value>
        <value condition="String.IsEqual(%(type)s,collection)">$INFO[Container(55).NumItems,, titles]</value>
%(view_subs)s        <value>$INFO[Container(%(grid)d).NumItems,, titles]$INFO[%(letter)s,  ·  ,]</value>
    </variable>
    <variable name="SiloBrowseSort">
%(sort_values)s        <value>title</value>
    </variable>
    <variable name="SiloBrowseOrder">
%(order_values)s        <value>ascending</value>
    </variable>
    <variable name="SiloSortLabel">
%(label_values)s        <value>Title</value>
    </variable>
    <variable name="SiloSortDirection">
%(direction_values)s        <value>A–Z</value>
    </variable>
    <variable name="SiloSortPillDirection">
        <value condition="Control.HasFocus(%(pill)d)">[COLOR 8C000000]$VAR[SiloSortDirection][/COLOR]</value>
        <value>[COLOR 99EDEDED]$VAR[SiloSortDirection][/COLOR]</value>
    </variable>
    <variable name="SiloSortArrowIcon">
%(arrow_values)s        <value>silo/arrow_up.png</value>
    </variable>
    <variable name="SiloLibraryFanart">
%(fanarts)s        <value condition="String.IsEqual(%(type)s,collections)">$INFO[Container(56).ListItem.Art(fanart)]</value>
        <value condition="String.IsEqual(%(type)s,collection)">$INFO[Container(55).ListItem.Art(fanart)]</value>
%(view_fanarts)s        <value>$INFO[Container(%(grid)d).ListItem.Art(fanart)]</value>
    </variable>
    <variable name="SiloBrowseViewLabel">
%(view_labels)s        <value>Grid</value>
    </variable>
    <!-- end Silo Skyline library -->
''' % {'type': TYPE, 'grid': GRID_ID, 'letter': LETTER, 'genre': GENRE, 'genres': GENRES_ID,
       'view_subs': ''.join('        <value condition="%s">$INFO[Container(%d).NumItems,, titles]$INFO[%s,  ·  ,]</value>\n'
                            % (view_is(v), ctrl, LETTER) for _, v, ctrl in VIEWS[1:]),
       # The hero and list views draw the backdrop themselves.
       'view_labels': ''.join('        <value condition="%s">%s</value>\n' % (view_is(v), label)
                              for label, v, _ in VIEWS[1:]),
       'view_fanarts': ''.join('        <value condition="%s"></value>\n' % view_is(v) for _, v, _ in VIEWS[1:]),
       'personal': ''.join('        <value condition="%s">%s</value>\n' % (is_list(key), title)
                           for key, (title, _) in PERSONAL.items()),
       'subs': ''.join('        <value condition="%s + Integer.IsGreater(Container(%d).NumItems,0)">'
                       '$INFO[Container(%d).NumItems,, titles]</value>\n        <value condition="%s"></value>\n'
                       % (is_list(key), list_id, list_id, is_list(key)) for key, (_, list_id) in PERSONAL.items()),
       'sort_values': ''.join('        <value condition="String.IsEqual(%s,%s) + !String.IsEmpty(Skin.String(silo.sort.%s))">'
                              '$INFO[Skin.String(silo.sort.%s)]</value>\n' % (TYPE, kind, kind, kind)
                              for kind in ('movies', 'tvshows')),
       'order_values': ''.join('        <value condition="String.IsEqual(%s,%s) + Skin.HasSetting(silo.sort.%s.desc)">'
                               'descending</value>\n' % (TYPE, kind, kind) for kind in ('movies', 'tvshows')),
       'label_values': ''.join('        <value condition="String.IsEqual(%s,%s) + String.IsEqual(Skin.String(silo.sort.%s),%s)">'
                               '%s</value>\n' % (TYPE, kind, kind, value, label)
                               for kind in KINDS for label, value, _, kinds, _ in SORTS if kind in kinds),
       'arrow_values': ''.join('        <value condition="String.IsEqual(%s,%s) + Skin.HasSetting(silo.sort.%s.desc)">'
                               'silo/arrow_down.png</value>\n' % (TYPE, kind, kind) for kind in KINDS),
       'direction_values': ''.join(
           '        <value condition="String.IsEqual(%s,%s) + %s + %sSkin.HasSetting(silo.sort.%s.desc)">%s</value>\n'
           % (TYPE, kind, sort_current(kind, value), '' if down else '!', kind, words[down])
           for kind in KINDS for _, value, _, kinds, words in SORTS if kind in kinds for down in (0, 1)),
       'pill': SORT_ID,
       'fanarts': ''.join('        <value condition="%s">$INFO[Container(%d).ListItem.Art(fanart)]</value>\n'
                          % (is_list(key), list_id) for key, (_, list_id) in PERSONAL.items())}


def filter_variables():
    """The Show pill's label, and each view's filter for its list path while
    Unwatched is on, and for a films grid always (its box sets' other films
    hidden): Kodi's filter option, '&' when the path has a query."""
    out = '''    <!-- A grid card's line under its title: its own (Coming Soon's date and
         episode, SiloKodiConnect's silo.caption), else its year. -->
    <variable name="SiloBrowseCardSub">
        <value condition="%(box)s">$INFO[ListItem.Art(set.siloyears)]</value>
        <value condition="!String.IsEmpty(ListItem.Property(silo.caption))">$INFO[ListItem.Property(silo.caption)]</value>
        <value>$INFO[ListItem.Year]</value>
    </variable>
    <variable name="SiloBrowseCardTitle">
        <value condition="%(box)s">$INFO[ListItem.Set]</value>
        <value>$INFO[ListItem.Label]</value>
    </variable>
    <variable name="SiloBrowsePoster">
        <value condition="%(box)s + !String.IsEmpty(ListItem.Art(set.poster))">$INFO[ListItem.Art(set.poster)]</value>
        <value>$INFO[ListItem.Art(poster)]</value>
    </variable>
    <variable name="SiloBrowseHeroFanart">
        <value condition="%(hero_box)s + !String.IsEmpty(Container(%(hero_id)d).ListItem.Art(set.fanart))">$INFO[Container(%(hero_id)d).ListItem.Art(set.fanart)]</value>
        <value>$INFO[Container(%(hero_id)d).ListItem.Art(fanart)]</value>
    </variable>
    <variable name="SiloBrowseShowLabel">
        <value condition="%(unwatched)s">Unwatched</value>
        <value>All</value>
    </variable>
''' % {'unwatched': UNWATCHED, 'box': BOX_SET, 'hero_id': HERO_ID,
       'hero_box': BOX_SET.replace('ListItem.', 'Container(%d).ListItem.' % HERO_ID)}
    for _, view, _ in VIEWS:
        path = VPATH % view
        out += '    <variable name="SiloBrowseFilter_%s">\n' % view
        # A films grid hides its box sets' other films (BOX_SET) whether or not Unwatched is on.
        cases = [('tvshows', ['String.IsEqual(%s,tvshows)' % TYPE, UNWATCHED], True, False),
                 ('movies', [UNWATCHED, GROUPED], True, True),
                 ('movies', [GROUPED], False, True),
                 ('movies', [UNWATCHED], True, False)]
        for kind, conditions, unwatched, grouped in cases:
            for joiner, has_query in (('&amp;', True), ('?', False)):
                parts = conditions + [('' if has_query else '!') + 'String.Contains(%s,?)' % path]
                out += '        <value condition="%s">%sfilter=%s</value>\n' % (
                    ' + '.join(parts), joiner, library_filter(kind, unwatched, grouped))
        out += '    </variable>\n'
    return out


def add_variables():
    path = os.path.join(ROOT, 'xml', 'Variables.xml')
    text = open(path, encoding='utf-8').read()
    start, end = '    <!-- Silo Skyline library (tools/build_library.py) -->', '    <!-- end Silo Skyline library -->\n'
    if start in text:
        text = text[:text.index(start) - 1] + text[text.index(end) + len(end):]
    text = text.replace('</includes>', VARIABLES.replace(start + '\n', start + '\n' + filter_variables(), 1) + '</includes>')
    open(path, 'w', encoding='utf-8').write(text)


TIMER_START, TIMER_END = '    <!-- Silo Skyline library (tools/build_library.py) -->\n', '    <!-- end Silo Skyline library -->\n'
# After a sort change, the grid's top once the re-sorted list is in: a second
# at least (the change reaches the grid on a later frame) and until it has
# stopped updating (a big library takes longer), not a fixed wait.
# Browse, or its copy for a collection's or a genre's titles.
BROWSE_ACTIVE = '[Window.IsActive(%d) | Window.IsActive(%d)]' % (WINDOW_ID, COLLECTION_WINDOW)
TIMERS = '''    <timer>
        <name>silo_sort_top</name>
        <start reset="true">String.IsEqual(Window(Home).Property(silo.browse.resort),1)</start>
        <stop>Integer.IsGreaterOrEqual(Skin.TimerElapsedSecs(silo_sort_top),1) + !Container(%(grid)d).IsUpdating + !Container(%(hero)d).IsUpdating + !Container(%(list)d).IsUpdating | !%(window)s</stop>
%(tops)s        <onstop>ClearProperty(silo.browse.resort,home)</onstop>
    </timer>
    <timer>
        <name>silo_browse_view_focus</name>
        <description>Browse's view takes focus once its titles are in, after opening or choosing it (Kodi can't focus an empty list)</description>
        <start reset="true">%(window)s + String.IsEqual(Window(Home).Property(silo.browse.focusview),1) + [[%(is_grid)s + Integer.IsGreater(Container(%(grid)d).NumItems,0)] | [%(is_hero)s + Integer.IsGreater(Container(%(hero)d).NumItems,0)] | [%(is_list)s + Integer.IsGreater(Container(%(list)d).NumItems,0)]]</start>
        <stop>true</stop>
%(focus)s        <onstop>ClearProperty(silo.browse.focusview,home)</onstop>
    </timer>
''' % {'grid': GRID_ID, 'hero': HERO_ID, 'list': LIST_VIEW_ID, 'window': BROWSE_ACTIVE,
       'is_grid': view_is('grid'), 'is_hero': view_is('hero'), 'is_list': view_is('list'),
       'tops': ''.join('        <onstop condition="%s + %s">%s</onstop>\n' % (BROWSE_ACTIVE, c, a)
                       for c, a in focus_view('SetFocus(%d,0,absolute)')),
       'focus': ''.join('        <onstop condition="%s + %s">%s</onstop>\n' % (BROWSE_ACTIVE, c, a)
                        for c, a in focus_view())}
# A list from SiloKodiConnect can still be loading as the window opens, and
# Kodi can't focus an empty list (its onload SetFocus fails and focus is
# lost): focus each one once it has items, unless something of it has focus.
FOCUS_WHEN_LOADED = ([('collections', 56), ('collection', 55), ('genres', GENRES_ID)]
                     + [(key, list_id) for key, (_, list_id) in PERSONAL.items()])
TIMERS += ''.join('''    <timer>
        <name>silo_focus_%(key)s</name>
        <start reset="true">[Window.IsActive(%(window)d) | Window.IsActive(%(other)d)] + !System.HasModalDialog + !Window.IsActive(movieinformation) + String.IsEqual(Window(Home).Property(silo.browse.type),%(key)s) + !String.IsEmpty(Window(Home).Property(silo.browse.list)) + Integer.IsGreater(Container(%(id)d).NumItems,0) + !Control.HasFocus(%(id)d) + !Control.HasFocus(61)</start>
        <stop>true</stop>
        <onstop condition="[Window.IsActive(%(window)d) | Window.IsActive(%(other)d)] + !System.HasModalDialog + !Window.IsActive(movieinformation) + !Control.HasFocus(%(id)d)">SetFocus(%(id)d)</onstop>
    </timer>
''' % {'key': key, 'id': list_id, 'window': WINDOW_ID, 'other': COLLECTION_WINDOW} for key, list_id in FOCUS_WHEN_LOADED)


def add_timers():
    path = os.path.join(ROOT, 'xml', 'Timers.xml')
    text = open(path, encoding='utf-8').read()
    if TIMER_START in text:
        text = text[:text.index(TIMER_START)] + text[text.index(TIMER_END) + len(TIMER_END):]
    text = text.replace('</timers>', TIMER_START + TIMERS + TIMER_END + '</timers>')
    open(path, 'w', encoding='utf-8').write(text)


if __name__ == '__main__':
    text = build()
    with open(os.path.join(ROOT, 'xml', 'Custom_%d_SiloLibrary.xml' % WINDOW_ID), 'w', encoding='utf-8') as handle:
        handle.write(text)
    # The collection a card opened, over the cards; leaving it shows the cards again.
    back = '\n'.join('    <onunload condition="String.IsEqual(Window(Home).Property(silo.browse.from),collections)">%s</onunload>'
                     % action for action in ('SetProperty(silo.browse.type,collections,home)',
                                             'SetProperty(silo.browse.list,$INFO[Window(Home).Property(silo.browse.list.collections)],home)'))
    # A genre's titles, over the genres; leaving them shows the genres again.
    back += '\n' + '\n'.join('    <onunload condition="String.IsEqual(Window(Home).Property(silo.browse.from),genres)">%s</onunload>'
                             % action for action in ('ClearProperty(silo.browse.genre,home)',
                                                     'SetProperty(silo.browse.type,genres,home)',
                                                     'SetProperty(silo.browse.list,$INFO[Window(Home).Property(silo.browse.list.genres)],home)'))
    with open(os.path.join(ROOT, 'xml', 'Custom_%d_SiloCollection.xml' % COLLECTION_WINDOW), 'w', encoding='utf-8') as handle:
        handle.write(text.replace('<window id="%d">' % WINDOW_ID, '<window id="%d">\n%s' % (COLLECTION_WINDOW, back), 1))
    add_variables()
    add_timers()
    print('Wrote xml/Custom_%d_SiloLibrary.xml, its variables in xml/Variables.xml and its timer in xml/Timers.xml'
          % WINDOW_ID)
