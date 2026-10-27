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
import os
import sys
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_home import BACKGROUND, ROOT, SAFE_X, TEXT, TEXT_DIM, TITLE_DIM  # noqa: E402

WINDOW_ID = 1191
TYPE = 'Window(Home).Property(silo.browse.type)'
PATH = 'Window(Home).Property(silo.browse.path)'
LETTER = 'Window(Home).Property(silo.browse.letter)'
LIST = 'Window(Home).Property(silo.browse.list)'
GRID_ID, AZ_ID = 50, 60
# Each list has its own grid: Kodi reopens a grid on the title last selected
# in it, so a shared one would open History on a title picked in Favorites.
PERSONAL = {'watchlist': ('Watchlist', 51), 'favorites': ('Favorites', 52), 'history': ('History', 53)}
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


def card(focused, control_id=GRID_ID):
    lit = 'Control.HasFocus(%d)' % control_id
    ring = '''
                <control type="image">
                    <width>%(rw)d</width><height>%(rh)d</height>
                    <texture colordiffuse="%(text)s">silo/card_poster_focus.png</texture>
                    <visible>%(lit)s</visible>
                </control>''' % {'rw': POSTER_W + 12, 'rh': POSTER_H + 12, 'text': TEXT, 'lit': lit} if focused else ''
    title = '''
                <control type="label">
                    <left>6</left><top>%(ty)d</top><width>%(w)d</width><height>44</height>
                    <font>silo_card_title</font>
                    <textcolor>%(colour)s</textcolor>
                    <label>$INFO[ListItem.Label]</label>%(scroll)s
                </control>''' % {'ty': POSTER_H + 18, 'w': POSTER_W, 'colour': TEXT if focused else TITLE_DIM,
                                  'scroll': '\n                    <scroll>true</scroll>' if focused else ''}
    return ring + '''
                <control type="image">
                    <left>6</left><top>6</top><width>%(pw)d</width><height>%(ph)d</height>
                    <aspectratio>scale</aspectratio>
                    <texture background="true" diffuse="silo/card_poster_mask.png" fallback="colors/grey.png">$INFO[ListItem.Art(poster)]</texture>
                </control>
                <!-- The rating is in Silo's poster art itself (top left). -->
                <!-- Watched: a white disc with a dark tick, top right. -->
                <control type="group">
                    <left>%(wx)d</left><top>16</top>
                    <visible>Integer.IsGreater(ListItem.PlayCount,0) | [Integer.IsGreater(ListItem.Property(TotalEpisodes),0) + Integer.IsEqual(ListItem.Property(UnWatchedEpisodes),0)]</visible>
                    <control type="image">
                        <width>44</width><height>44</height>
                        <texture colordiffuse="F2FFFFFF">silo/avatar_mask.png</texture>
                    </control>
                    <control type="image">
                        <left>10</left><top>10</top><width>24</width><height>24</height>
                        <texture colordiffuse="FF000000">OverlayWatched.png</texture>
                    </control>
                </control>%(title)s
                <control type="label">
                    <left>6</left><top>%(yy)d</top><width>%(w)d</width><height>34</height>
                    <font>silo_detail</font>
                    <textcolor>%(dim)s</textcolor>
                    <label>$INFO[ListItem.Year]</label>
                </control>''' % {'pw': POSTER_W, 'ph': POSTER_H, 'text': TEXT, 'wx': POSTER_W - 50, 'title': title,
                                 'yy': POSTER_H + 58, 'w': POSTER_W, 'dim': TEXT_DIM}


def letter_layouts():
    """The A-Z column: dots at rest, letters while it has focus (Kodi picks
    the item layout by condition); the chosen letter is lit either way."""
    lit = 'Control.HasFocus(%d)' % AZ_ID
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
        items += '''
                <item>
                    <label>%s</label>%s
                </item>''' % (letter, ''.join(
                    '\n                    ' + (c + '</onclick>' if c.startswith('<onclick') else '<onclick>%s</onclick>' % c)
                    for c in clicks))
    return items


def panel(control_id, content, right, visible, up='noop'):
    """The poster grid: content is its <content> element."""
    return '''        <control type="panel" id="%(id)d">
            <left>%(gx)d</left><top>%(gy)d</top>
            <width>%(gw)d</width><height>%(gh)d</height>
            <orientation>vertical</orientation>
            <visible>%(visible)s</visible>
            <onright>%(right)s</onright>
            <onleft>noop</onleft>
            <onup>%(up)s</onup>
            <scrolltime tween="cubic" easing="out">280</scrolltime>
            <!-- Details, not Kodi's play or open (SiloKodiConnect's info page, else Kodi's). -->
            <onclick condition="System.AddonIsEnabled(plugin.video.silokodiconnect)">RunPlugin(plugin://plugin.video.silokodiconnect/?mode=info&amp;type=$INFO[ListItem.DBType]&amp;dbid=$INFO[ListItem.DBID])</onclick>
            <onclick condition="!System.AddonIsEnabled(plugin.video.silokodiconnect)">Action(Info)</onclick>
            <itemlayout width="%(iw)d" height="%(ih)d">%(card)s
            </itemlayout>
            <focusedlayout width="%(iw)d" height="%(ih)d">%(card_focused)s
            </focusedlayout>
            %(content)s
        </control>
''' % {'id': control_id, 'gx': GRID_X, 'gy': GRID_TOP, 'gw': COLS * ITEM_W, 'gh': 1080 - GRID_TOP,
       'visible': visible, 'right': right, 'iw': ITEM_W, 'ih': ITEM_H, 'card': card(False),
       'card_focused': card(True, control_id), 'content': content, 'up': up}


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
        clicks.append((None, 'SetFocus(%d,0,absolute)' % GRID_ID))
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
                    </control>''' % {'iy': (SORT_ROW - 26) // 2, 'ay': (SORT_ROW - 22) // 2, 'lw': SORT_W - 260,
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
            <onleft>noop</onleft><onright>noop</onright><onup>noop</onup>
        </control>%(pill_icons)s
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
''' % {'pill': SORT_ID, 'list': SORT_LIST_ID, 'x': SAFE_X, 'top': SORT_TOP, 'text': TEXT,
       'personal': IS_PERSONAL, 'ly': SORT_TOP + 68, 'frames': frames, 'head': SORT_HEAD,
       'lw': SORT_W - 32, 'lh': len(SORTS) * SORT_ROW, 'row': SORT_ROW, 'normal': row(False), 'focused': row(True),
       'items': items, 'open_list': open_list,
       'pill_icons': pill_icon('FF000000', '!%s + Control.HasFocus(%d)' % (IS_PERSONAL, SORT_ID))
                     + pill_icon(TEXT, '!%s + !Control.HasFocus(%d)' % (IS_PERSONAL, SORT_ID))}


def is_list(key):
    return 'String.IsEqual(%s,%s) + %s' % (TYPE, key, IS_PERSONAL)


def empty_note(key, list_id):
    """Shown when a personal list has nothing in it."""
    return '''        <control type="label">
            <left>%(gx)d</left><top>%(top)d</top>
            <width>%(gw)d</width><height>60</height>
            <font>silo_plot</font>
            <textcolor>%(dim)s</textcolor>
            <label>Nothing here yet. Add titles from Silo and they appear here.</label>
            <visible>%(personal)s + !Container(%(list)d).IsUpdating + Integer.IsEqual(Container(%(list)d).NumItems,0)</visible>
        </control>
''' % {'gx': SAFE_X, 'top': GRID_TOP + 20, 'gw': 1920 - 2 * SAFE_X, 'dim': TEXT_DIM, 'personal': is_list(key),
       'list': list_id}


def build():
    return '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by tools/build_library.py: edit that, not this. -->
<window id="%(window)d">
    <!-- Back from a trailer started from an info page (Kodi leaves it playing): stop it, which reopens the page. -->
    <onload condition="Player.HasVideo + !String.IsEmpty(Window(Home).Property(silokodi.trailer_playing))">PlayerControl(Stop)</onload>
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
            <texture background="true" colordiffuse="40FFFFFF" diffuse="silo/hero_mask.png">$VAR[SiloLibraryFanart]</texture>
        </control>
        <include content="SiloFrame">
            <param name="title">$VAR[SiloLibraryTitle]</param>
            <param name="sub">$VAR[SiloLibrarySub]</param>
        </include>
%(panels)s        <!-- Silo's A-Z. -->
        <control type="list" id="%(az)d">
            <visible>!%(personal)s</visible>
            <left>%(ax)d</left><top>%(gy)d</top>
            <width>%(aw)d</width><height>%(gh)d</height>
            <orientation>vertical</orientation>
            <onleft>%(grid)d</onleft>
            <onright>noop</onright>
            <scrolltime tween="cubic" easing="out">200</scrolltime>%(layouts)s
            <content>%(items)s
            </content>
        </control>
        <!-- A trailer from an info page: its cover (Includes_SiloFrame.xml). -->
        <include>SiloTrailerCover</include>
    </controls>
</window>
''' % {'window': WINDOW_ID, 'grid': GRID_ID, 'background': BACKGROUND, 'letter': LETTER, 'gx': GRID_X,
       'gy': GRID_TOP, 'gh': 1080 - GRID_TOP, 'az': AZ_ID, 'personal': IS_PERSONAL,
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
                         for key, (_, list_id) in PERSONAL.items()),
       'panels': panel(GRID_ID, '<content target="videos" sortby="$INFO[%s]" sortorder="$INFO[%s]">'
                       '$INFO[%s]</content>' % (SORT_BY, SORT_ORDER, PATH), str(AZ_ID), '!' + IS_PERSONAL, str(SORT_ID))
                 + sort_controls()
                 # Each grid has its own path (only the open list's is set: Kodi
                 # loads a grid's path even while it is hidden).
                 + ''.join(panel(list_id, '<content target="videos">$INFO[Window(Home).Property(silo.browse.list.%s)]'
                                 '</content>' % key, 'noop', is_list(key))
                           + empty_note(key, list_id) for key, (_, list_id) in PERSONAL.items()),
       'ax': 1920 - SAFE_X - AZ_W,
       'aw': AZ_W, 'layouts': letter_layouts(), 'items': letter_items()}


VARIABLES = '''
    <!-- Silo Skyline library (tools/build_library.py) -->
    <variable name="SiloLibraryTitle">
%(personal)s        <value condition="String.IsEqual(%(type)s,tvshows)">Series</value>
        <value>Movies</value>
    </variable>
    <variable name="SiloLibrarySub">
%(subs)s        <value>$INFO[Container(%(grid)d).NumItems,, titles]$INFO[%(letter)s,  ·  ,]</value>
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
%(fanarts)s        <value>$INFO[Container(%(grid)d).ListItem.Art(fanart)]</value>
    </variable>
    <!-- end Silo Skyline library -->
''' % {'type': TYPE, 'grid': GRID_ID, 'letter': LETTER,
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


def add_variables():
    path = os.path.join(ROOT, 'xml', 'Variables.xml')
    text = open(path, encoding='utf-8').read()
    start, end = '    <!-- Silo Skyline library (tools/build_library.py) -->', '    <!-- end Silo Skyline library -->\n'
    if start in text:
        text = text[:text.index(start) - 1] + text[text.index(end) + len(end):]
    text = text.replace('</includes>', VARIABLES + '</includes>')
    open(path, 'w', encoding='utf-8').write(text)


TIMER_START, TIMER_END = '    <!-- Silo Skyline library (tools/build_library.py) -->\n', '    <!-- end Silo Skyline library -->\n'
# After a sort change, the grid's top once the re-sorted list is in: a second
# at least (the change reaches the grid on a later frame) and until it has
# stopped updating (a big library takes longer), not a fixed wait.
TIMERS = '''    <timer>
        <name>silo_sort_top</name>
        <start reset="true">String.IsEqual(Window(Home).Property(silo.browse.resort),1)</start>
        <stop>Integer.IsGreaterOrEqual(Skin.TimerElapsedSecs(silo_sort_top),1) + !Container(%(grid)d).IsUpdating | !Window.IsActive(%(window)d)</stop>
        <onstop condition="Window.IsActive(%(window)d)">SetFocus(%(grid)d,0,absolute)</onstop>
        <onstop>ClearProperty(silo.browse.resort,home)</onstop>
    </timer>
''' % {'grid': GRID_ID, 'window': WINDOW_ID}


def add_timers():
    path = os.path.join(ROOT, 'xml', 'Timers.xml')
    text = open(path, encoding='utf-8').read()
    if TIMER_START in text:
        text = text[:text.index(TIMER_START)] + text[text.index(TIMER_END) + len(TIMER_END):]
    text = text.replace('</timers>', TIMER_START + TIMERS + TIMER_END + '</timers>')
    open(path, 'w', encoding='utf-8').write(text)


if __name__ == '__main__':
    with open(os.path.join(ROOT, 'xml', 'Custom_%d_SiloLibrary.xml' % WINDOW_ID), 'w', encoding='utf-8') as handle:
        handle.write(build())
    add_variables()
    add_timers()
    print('Wrote xml/Custom_%d_SiloLibrary.xml, its variables in xml/Variables.xml and its timer in xml/Timers.xml'
          % WINDOW_ID)
