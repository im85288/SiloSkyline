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
# Pages with a tab in the bar, then 'custom': the rows of a custom menu item
# (Skin Shortcuts) the user opened.
TABBED = ('home', 'movies', 'series', 'requests')
PAGES = TABBED + ('custom',)
TAB_LABELS = {'home': 'Home', 'movies': 'Movies', 'series': 'Series', 'requests': 'Requests'}
MAX_ROWS = 12
# Custom menu items (Skin Shortcuts): bar slots, and widgets per item.
CUSTOM_SLOTS = 5
WIDGETS = 6
CUSTOM_IDS = list(range(9031, 9031 + CUSTOM_SLOTS))
SHORTCUTS = 9100  # hidden list holding Skin Shortcuts' main menu
SUBMENU = 9240    # the dropdown of a custom item's submenu
HOME_CARDS = 25   # cards in a published row (SiloKodiConnect rows.CARDS)
# Pages whose rows are SiloKodiConnect's published cards (Movies' and
# Series' rows are native Kodi lists where they can be, plugin rows otherwise).
PUBLISHED_PAGES = ('home', 'requests')
POSTER_ONLY = ('requests',)  # Silo's request rows are all posters
# Cards per published row: every slot is parsed as the skin loads (on a SHIELD,
# 2,200 slots took 25 s; Home's 600, 1 s), so other pages show fewer.
PAGE_CARDS = {'home': HOME_CARDS}
OTHER_CARDS = 12
HOME_CARD_FIELDS = ('type', 'dbid', 'card.title', 'card.sub', 'card.wide_sub', 'hero.title', 'hero.meta',
                    'hero.detail', 'plot', 'mpaa', 'badge1', 'badge2', 'badge3', 'tint', 'percent', 'playcount',
                    'art.poster', 'art.landscape', 'art.fanart', 'art.clearlogo', 'request.type', 'request.tmdb')
# Rows a page can show; Requests has Your requests and Silo's few discovery
# rows, and every slot costs Home.xml size.
# Silo's libraries have 6 rows each: fewer slots keep Home.xml quick to load.
PAGE_ROWS = {'movies': 8, 'series': 8, 'requests': 8, 'custom': WIDGETS}


def rows_of(page):
    return PAGE_ROWS.get(page, MAX_ROWS)
LOOKAHEAD = 4  # rows a move may skip over when they are empty

SAFE_X = 88
BAR_TOP = 56
TEXT = 'FFEDEDED'
TEXT_DIM = 'BFEDEDED'      # Silo's secondary text: 75%
TAB_DIM = 'B3EDEDED'       # Silo's dimmed bar items: 70%
TITLE_DIM = 'C7EDEDED'     # a card's title until it has focus: 78%
BACKGROUND = 'FF0D0F12'     # Silo's near-black page
ROWS_TOP = 592             # row titles sit where Silo's do (Silo TV, October 2026)
# As in Silo, the row band shows the focused row and a sliver of the next
# row's title, never its cards. Each row is the band's full height with its
# content in the top ROW_PITCH, and rows overlap by the rest (a negative
# item gap): Kodi scrolls a grouplist just far enough to show the focused
# row whole, which puts it at the top and the next title in the last 24 px
# (just below a poster row's captions, as in Silo).
BAND_H = 1080 - ROWS_TOP
ROW_PITCH = BAND_H - 24
# Cards sit this far below their row's title, leaving Silo's gap between them.
CARDS_TOP = 96

# Cards as Silo TV draws them: dense posters (88x132 units) and backdrops
# (180x101), each with a title and a second line beneath.
POSTER = {'name': 'Poster', 'width': 176, 'height': 264, 'gap': 40, 'mask': 'silo/card_poster_mask.png',
          'ring': 'silo/card_poster_focus.png', 'art': '$VAR[SiloPosterArt]',
          'sub': '$VAR[SiloCardYear]', 'radius': 12}
LANDSCAPE = {'name': 'Landscape', 'width': 360, 'height': 202, 'gap': 40, 'mask': 'silo/card_landscape_mask.png',
             'ring': 'silo/card_landscape_focus.png', 'art': '$VAR[SiloLandscapeArt]',
             'sub': '$VAR[SiloCardEpisode]', 'radius': 14}
CAPTION_H = 76             # title and second line under a card

# Fonts (Inter, as the Silo apps use); Font.xml gets these between markers.
FONTS = [  # name, file, size
    ('silo_tab', 'Inter-SemiBold.ttf', 30),
    ('silo_row', 'Inter-Bold.ttf', 34),
    ('silo_title', 'Inter-Bold.ttf', 76),
    ('silo_osd_title', 'Inter-Bold.ttf', 46),  # the player's episode or film title
    ('silo_meta', 'Inter-Medium.ttf', 28),
    ('silo_plot', 'Inter-Regular.ttf', 28),
    ('silo_detail', 'Inter-Medium.ttf', 24),
    ('silo_badge', 'Inter-SemiBold.ttf', 20),
    ('silo_card_title', 'Inter-SemiBold.ttf', 26),
    ('silo_card_sub', 'Inter-Medium.ttf', 24),
    ('silo_wordmark', 'Inter-Bold.ttf', 44),
    ('silo_wordmark_light', 'Inter-Medium.ttf', 44),  # "Skyline" beside "Silo"
    ('silo_title_light', 'Inter-Medium.ttf', 76),
    ('silo_key', 'Inter-Medium.ttf', 40),
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


def home_waiting(row):
    """Home before a row has focus, showing its published row `row`'s first
    card (row 1's, or row 2's when row 1 has none)."""
    condition = ('String.IsEmpty(%s) + [String.IsEqual(%s,home) | String.IsEmpty(%s)] + Integer.IsGreater(%s,0)'
                 % (prop('silo.row'), prop('silo.page'), prop('silo.page'), prop('silo.home.%d.cards' % row)))
    return condition if row == 1 else condition + ' + !Integer.IsGreater(%s,0)' % prop('silo.home.1.cards')


def waiting_rows():
    """[(condition, list id)]: on a page other than Home, before any row has
    had focus, the hero shows the selected item of the page's first loaded
    row (Kodi gives a list's item without focus), not a black hero."""
    out = []
    for index, page in enumerate(PAGES):
        if page == 'home':
            continue
        for slot in (1, 2):
            for landscape in (False, True):
                target = list_id(index, slot, landscape)
                out.append(('String.IsEmpty(%s) + %s + Integer.IsGreater(Container(%d).NumItems,0)'
                            % (prop('silo.row'), page_visible(page), target), target))
    return out


def card_layout(card, focused, control_id=None):
    """A row's card: the shared include from Includes_SiloCards.xml (a
    focused card is told its list's id), which keeps Home.xml small."""
    if not focused:
        return '\n                    <include>SiloCard%s</include>' % card['name']
    return ('\n                    <include content="SiloCardFocused%s"><param name="id" value="%d" /></include>'
            % (card['name'], control_id))


def published_item(prefix):
    """One card slot of a published row: its fields from the Home window."""
    return ('\n                        <item><label>$INFO[Window(Home).Property(%s.label)]</label>' % prefix +
            ''.join('<property name="home.%s">$INFO[Window(Home).Property(%s.%s)]</property>' % (field, prefix, field)
                    for field in HOME_CARD_FIELDS) +
            '<visible>!String.IsEmpty(Window(Home).Property(%s.type))</visible></item>' % prefix)


def write_card_includes():
    """The card includes every row (Home, Search, More Like This) uses, and
    a Home card: one item of SiloKodiConnect's published rows."""
    home_card = '''
    <include name="SiloHomeCard">
        <param name="p" />
        <definition>
            <item>
                <label>$INFO[Window(Home).Property($PARAM[p].label)]</label>%s
                <visible>!String.IsEmpty(Window(Home).Property($PARAM[p].type))</visible>
            </item>
        </definition>
    </include>''' % ''.join('\n                <property name="home.%s">$INFO[Window(Home).Property($PARAM[p].%s)]</property>'
                            % (field, field) for field in HOME_CARD_FIELDS)
    includes = home_card + ''.join('''
    <include name="SiloCard%(name)s">%(normal)s
    </include>
    <include name="SiloCardFocused%(name)s">
        <param name="id" />
        <definition>%(focused)s
        </definition>
    </include>''' % {'name': card['name'], 'normal': card_body(card, False), 'focused': card_body(card, True)}
                       for card in (POSTER, LANDSCAPE))
    with open(os.path.join(ROOT, 'xml', 'Includes_SiloCards.xml'), 'w') as handle:
        handle.write('<?xml version="1.0" encoding="UTF-8"?>\n<!-- Generated by tools/build_home.py: Silo\'s cards, '
                     'shared by every row. -->\n<includes>%s\n</includes>\n' % includes)
    path = os.path.join(ROOT, 'xml', 'Includes.xml')
    text = open(path).read()
    if 'Includes_SiloCards.xml' not in text:
        text = text.replace('\t<include file="Includes_Home.xml" />',
                            '\t<include file="Includes_Home.xml" />\n\t<include file="Includes_SiloCards.xml" />', 1)
        with open(path, 'w') as handle:
            handle.write(text)


def card_body(card, focused, control_id='$PARAM[id]'):
    ring = ''
    zoom = ''
    if focused:
        ring = '''
                        <control type="image">
                            <left>0</left><top>0</top>
                            <width>%(rw)d</width><height>%(rh)d</height>
                            <texture colordiffuse="%(text)s">%(ring)s</texture>
                            <visible>Control.HasFocus(%(id)s)</visible>
                        </control>''' % {'rw': card['width'] + 12, 'rh': card['height'] + 12, 'text': TEXT,
                                         'ring': card['ring'], 'id': control_id}
        # Kodi draws every row's selected item with this layout, focused or
        # not: only the row that has focus shows the ring and the lift.
        zoom = ('\n                        <animation effect="zoom" start="100" end="104" time="160" tween="sine" '
                'center="auto" condition="Control.HasFocus(%s)">Conditional</animation>' % control_id)
    # Silo dims a card's title until the card has focus.
    title_visible = title_focused = ''
    if focused:
        title_visible = '\n                            <visible>!Control.HasFocus(%s)</visible>' % control_id
        title_focused = '''
                        <control type="label">
                            <left>6</left><top>%(t1)d</top>
                            <width>%(w)d</width><height>34</height>
                            <font>silo_card_title</font>
                            <textcolor>%(text)s</textcolor>
                            <label>$VAR[SiloCardTitle]</label>
                            <!-- The whole title, scrolling, on the focused card. -->
                            <scroll>true</scroll>
                            <scrollspeed>50</scrollspeed><scrollsuffix>      </scrollsuffix>
                            <visible>Control.HasFocus(%(id)s)</visible>
                        </control>''' % {'t1': card['height'] + 20, 'w': card['width'], 'text': TEXT, 'id': control_id}
    return '''
                    <control type="group">%(zoom)s
                        <control type="image">
                            <left>6</left><top>6</top>
                            <width>%(w)d</width><height>%(h)d</height>
                            <texture background="true" diffuse="%(mask)s" fallback="colors/grey.png">%(art)s</texture>
                            <aspectratio>scale</aspectratio>
                        </control>
                        <control type="image">
                            <left>6</left><top>6</top>
                            <width>%(w)d</width><height>%(h)d</height>
                            <texture diffuse="%(mask)s">silo/card_scrim.png</texture>
                        </control>
                        <control type="progress">
                            <left>%(px)d</left><top>%(pt)d</top>
                            <width>%(pw)d</width><height>6</height>
                            <texturebg colordiffuse="33FFFFFF">colors/white.png</texturebg>
                            <midtexture colordiffuse="%(text)s">colors/white.png</midtexture>
                            <info>ListItem.PercentPlayed</info>
                            <visible>Integer.IsGreater(ListItem.PercentPlayed,0)</visible>
                        </control>
                        <control type="progress">
                            <left>%(px)d</left><top>%(pt)d</top>
                            <width>%(pw)d</width><height>6</height>
                            <texturebg colordiffuse="33FFFFFF">colors/white.png</texturebg>
                            <midtexture colordiffuse="%(text)s">colors/white.png</midtexture>
                            <info>ListItem.Property(home.percent)</info>
                            <visible>!String.IsEmpty(ListItem.Property(home.percent))</visible>
                        </control>
                        <control type="image">
                            <right>16</right><top>16</top>
                            <width>32</width><height>32</height>
                            <texture colordiffuse="%(text)s">OverlayWatched.png</texture>
                            <visible>Integer.IsGreater(ListItem.PlayCount,0) | !String.IsEmpty(ListItem.Property(home.playcount))</visible>
                        </control>%(ring)s
                        <control type="label">
                            <left>6</left><top>%(t1)d</top>
                            <width>%(w)d</width><height>34</height>
                            <font>silo_card_title</font>
                            <textcolor>%(title_color)s</textcolor>
                            <label>$VAR[SiloCardTitle]</label>%(title_visible)s
                        </control>%(title_focused)s
                        <control type="label">
                            <left>6</left><top>%(t2)d</top>
                            <width>%(w)d</width><height>32</height>
                            <font>silo_card_sub</font>
                            <textcolor>%(dim)s</textcolor>
                            <label>%(sub)s</label>
                        </control>
                    </control>''' % {'zoom': zoom, 'w': card['width'], 'h': card['height'], 'mask': card['mask'],
                                    'art': card['art'], 'title_color': TITLE_DIM, 'title_visible': title_visible,
                                    'title_focused': title_focused,
                                    # On the card's bottom edge, short of the rounded corners
                                    # (Kodi can't clip a progress bar to the card's mask).
                                    'px': 6 + card['radius'], 'pt': card['height'], 'pw': card['width'] - 2 * card['radius'],
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
    if page in PUBLISHED_PAGES:
        # Published cards: the row shows when SiloKodiConnect has cards for
        # it. Not the list's item count: Kodi doesn't evaluate a hidden list's
        # items, so the row would wait for the page's loading flag.
        return '%s + !String.IsEmpty(%s) + %s + Integer.IsGreater(%s,0)' % (
            page_visible(page), prop(key + '.path'), style, prop(key + '.cards'))
    # Empty rows hide, as in Silo; Kodi still loads a list hidden this way.
    # silo.<page>.loading (SiloKodiConnect) keeps rows shown while they load:
    # Kodi never loads a hidden list whose path changed.
    return ('%s + !String.IsEmpty(%s) + %s + [Integer.IsGreater(Container(%d).NumItems,0) | Container(%d).IsUpdating'
            ' | String.IsEqual(%s,1)]' % (page_visible(page), prop(key + '.path'), style, lid, lid,
                                         prop('silo.%s.loading' % page)))


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
    down = page_rows(page_index, range(slot + 1, min(rows_of(PAGES[page_index]), slot + LOOKAHEAD) + 1))
    up = page_rows(page_index, range(slot - 1, max(0, slot - LOOKAHEAD), -1))
    out = first_visible('ondown', down) + first_visible('onup', up)
    # The top row goes up to the current page's tab (a button: focusing the
    # bar's grouplist itself leaves left and right with nowhere to go).
    above = ' + '.join('!' + shown(k) for k in up)
    target = '%d' % (9002 + page_index) if PAGES[page_index] in TABBED else '$INFO[%s]' % prop('silo.custom.button')
    out += '\n                    <onup%s>SetFocus(%s)</onup>' % (' condition="%s"' % above if above else '', target)
    return out


def row(page, page_index, slot, landscape):
    card = LANDSCAPE if landscape else POSTER
    key = 'silo.%s.%d' % (page, slot)
    rules = '$EXP[SiloRow%d]' % list_id(page_index, slot, landscape)
    # SiloKodiConnect publishes each row's path under its style (the slot has
    # a poster and a landscape list, so only the list that shows loads), empty
    # until the page has been viewed, and with a refresh token it changes when
    # it writes the library, which reloads the row. An empty path keeps Kodi
    # from trying the row too early: a list whose load failed never retries.
    # Kodi reads a $VAR in a content path only once, so this must stay $INFO.
    path = '$INFO[%s]' % prop(key + ('.landscape' if landscape else '.poster'))
    if page == 'custom':
        # A Skin Shortcuts widget: any Kodi path, used as it is.
        path = '$INFO[%s]' % prop(key + '.path')
    # Home's, Movies', Series' and Requests' rows: the cards SiloKodiConnect
    # publishes, in Silo's order, so a row draws at once (no plugin, no
    # Python) and keeps Silo's ranking. A custom page's widgets are any
    # Kodi path, so they load as they are.
    content = '<content target="videos">%s</content>' % path
    if page != 'custom':
        # A Kodi library row (Movies' and Series' Recently Added, say) comes
        # in its sort from SiloKodiConnect: Kodi ignores a videodb path's own
        # order, and sorts before it cuts the row to its limit. Empty for a
        # plugin row, which keeps its order.
        content = '<content target="videos" sortby="$INFO[%s]" sortorder="$INFO[%s]" limit="$INFO[%s]">%s</content>' % (
            prop(key + '.sort'), prop(key + '.order'), prop(key + '.limit'), path)
    if page in POSTER_ONLY and landscape:
        content = '<content></content>'  # never shown: no slots to parse
    elif page in PUBLISHED_PAGES:
        # Written out, not an include with a parameter: Kodi expands those
        # slowly as the skin loads (thousands of them took 25 s on a SHIELD).
        content = '<content>%s\n                    </content>' % ''.join(
            published_item('silo.%s.%d.%d' % (page, slot, card))
            for card in range(1, PAGE_CARDS.get(page, OTHER_CARDS) + 1))
    item_w = card['width'] + card['gap']
    item_h = card['height'] + 12 + CAPTION_H
    return '''
            <control type="group">
                <height>%(group_h)d</height>
                <visible>%(rules)s</visible>
                <!-- Silo marks Continue Watching with a play icon before its title. -->
                <control type="image">
                    <left>%(x)d</left><top>9</top>
                    <width>28</width><height>28</height>
                    <texture colordiffuse="%(text)s">silo/play_circle.png</texture>
                    <visible>String.IsEqual(%(type)s,continue_watching)</visible>
                </control>
                <control type="label">
                    <left>%(x)d</left><top>0</top>
                    <width>1500</width><height>46</height>
                    <font>silo_row</font>
                    <textcolor>%(text)s</textcolor>
                    <label>$INFO[%(title)s]</label>
                    <visible>!String.IsEqual(%(type)s,continue_watching)</visible>
                </control>
                <control type="label">
                    <left>%(icon_x)d</left><top>0</top>
                    <width>1500</width><height>46</height>
                    <font>silo_row</font>
                    <textcolor>%(text)s</textcolor>
                    <label>$INFO[%(title)s]</label>
                    <visible>String.IsEqual(%(type)s,continue_watching)</visible>
                </control>
                <control type="list" id="%(id)d">
                    <visible>%(rules)s</visible>
                    <left>%(lx)d</left><top>%(cards_top)d</top>
                    <width>%(lw)d</width><height>%(item_h)d</height>
                    <orientation>horizontal</orientation>
                    <scrolltime tween="cubic" easing="out">280</scrolltime>
                    <preloaditems>2</preloaditems>
                    <!-- A title Silo can request opens with Silo's full details. -->
                    <onclick condition="!String.IsEmpty(ListItem.Property(silo.request.tmdb)) + System.AddonIsEnabled(plugin.video.silokodiconnect)">RunPlugin(plugin://plugin.video.silokodiconnect/?mode=request_info&amp;type=$INFO[ListItem.Property(silo.request.type)]&amp;tmdb=$INFO[ListItem.Property(silo.request.tmdb)])</onclick>
                    <!-- A published card opens its info page through SiloKodiConnect:
                         a title Silo can request, its request page. -->
                    <onclick condition="!String.IsEmpty(ListItem.Property(home.request.tmdb))">RunPlugin(plugin://plugin.video.silokodiconnect/?mode=request_info&amp;type=$INFO[ListItem.Property(home.request.type)]&amp;tmdb=$INFO[ListItem.Property(home.request.tmdb)])</onclick>
                    <onclick condition="!String.IsEmpty(ListItem.Property(home.type)) + String.IsEmpty(ListItem.Property(home.request.tmdb))">RunPlugin(plugin://plugin.video.silokodiconnect/?mode=info&amp;type=$INFO[ListItem.Property(home.type)]&amp;dbid=$INFO[ListItem.Property(home.dbid)])</onclick>
                    <onclick condition="String.IsEmpty(ListItem.Property(home.type)) + [String.IsEmpty(ListItem.Property(silo.request.tmdb)) | !System.AddonIsEnabled(plugin.video.silokodiconnect)]">Action(Info)</onclick>
                    <onfocus>SetProperty(silo.row,%(id)d,home)</onfocus>%(moves)s
                    %(content)s
                    <itemlayout width="%(item_w)d" height="%(item_h)d">%(normal)s
                    </itemlayout>
                    <focusedlayout width="%(item_w)d" height="%(item_h)d">%(focused)s
                    </focusedlayout>
                </control>
            </control>''' % {
        'group_h': BAND_H, 'rules': rules, 'x': SAFE_X, 'text': TEXT, 'title': prop(key + '.title'), 'type': prop(key + '.type'), 'icon_x': SAFE_X + 42,
        'cards_top': CARDS_TOP, 'id': list_id(page_index, slot, landscape), 'lx': SAFE_X - 6, 'lw': 1920 - SAFE_X + 6, 'item_h': item_h,
        'moves': moves(page_index, slot), 'path': path, 'content': content, 'item_w': item_w, 'normal': card_layout(card, False),
        'focused': card_layout(card, True, list_id(page_index, slot, landscape))}


# Silo dims the whole bar to 70% while focus is down in the rows.
BAR_DIM = '!ControlGroup(9000).HasFocus() + !Control.HasFocus(9011)'
BAR_ORDER = [9001, 9002, 9003, 9004, 9005] + CUSTOM_IDS + [9009, 9010, 9011]  # Search, tabs, custom items, Settings, Power, profile


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


# Silo's library sections for a page's tab (TvLibraryPill.set): Up from the tab
# shows them as a row of pills above the bar; OK and Down go to the page. Collections are
# the page's libraries' collections, linked by SiloKodiConnect.
SECTIONS = {
    'movies': [('Recommended', None), ('Browse', 'videodb://movies/titles/'),
               ('Collections', '$INFO[Window(Home).Property(silo.movies.collections)]')],
    'series': [('Recommended', None), ('Browse', 'videodb://tvshows/titles/'),
               ('Collections', '$INFO[Window(Home).Property(silo.series.collections)]')],
}
BAR_GAP = 8


def tab_width(page):
    return 60 + 17 * len(TAB_LABELS[page])


def open_sections(page, control_id):
    """Up from a tab with sections opens them: a row of pills above the bar
    (a chevron over the focused tab says it has them); Down comes back."""
    if page not in SECTIONS:
        return ''
    return '                    <onup>SetFocus(%d,0,absolute)</onup>\n' % (control_id + 200)


def bar_positions():
    """Each bar button's left edge: the bar is a centred grouplist."""
    widths = [60] + [tab_width(page) for page in TABBED] + [60, 60]
    ids = [9001] + [9002 + index for index in range(len(TABBED))] + [9009, 9010]
    total = sum(widths) + BAR_GAP * (len(widths) - 1)
    x, out = (1920 - total) // 2, {}
    for control_id, width in zip(ids, widths):
        out[control_id] = x
        x += width + BAR_GAP
    return out


SUB_TOP, SUB_H, SUB_ITEM_W = 0, 52, 250  # the row of sub-menu pills above the bar


def submenu_row(x, list_id, back, content):
    """A row of sub-menu pills above the bar, from x: present but faded out
    until it has focus (Kodi can't focus a hidden control); Down and Back
    return to the tab."""
    return '''
        <control type="group">
            <left>%(x)d</left><top>%(top)d</top>
            <animation effect="fade" start="100" end="0" time="120" condition="!Control.HasFocus(%(id)d)">Conditional</animation>
            <control type="list" id="%(id)d">
                <width>%(w)d</width><height>%(h)d</height>
                <orientation>horizontal</orientation>
                <ondown>%(back)s</ondown>
                <onback>%(back)s</onback>
                <onup>noop</onup><onleft>noop</onleft><onright>noop</onright>
                <itemlayout width="%(iw)d" height="%(h)d">
                    <control type="image">
                        <top>4</top><width>%(pw)d</width><height>44</height>
                        <texture border="22" colordiffuse="E61C1F24">silo/pill.png</texture>
                    </control>
                    <control type="label">
                        <top>4</top><width>%(pw)d</width><height>44</height>
                        <align>center</align><aligny>center</aligny>
                        <font>silo_meta</font>
                        <textcolor>%(text)s</textcolor>
                        <label>$INFO[ListItem.Label]</label>
                    </control>
                </itemlayout>
                <focusedlayout width="%(iw)d" height="%(h)d">
                    <control type="image">
                        <top>4</top><width>%(pw)d</width><height>44</height>
                        <texture border="22" colordiffuse="%(text)s">silo/pill.png</texture>
                    </control>
                    <control type="label">
                        <top>4</top><width>%(pw)d</width><height>44</height>
                        <align>center</align><aligny>center</aligny>
                        <font>silo_meta</font>
                        <textcolor>FF000000</textcolor>
                        <label>$INFO[ListItem.Label]</label>
                    </control>
                </focusedlayout>
                <content>%(content)s
                </content>
            </control>
        </control>''' % {'x': x, 'top': SUB_TOP, 'id': list_id, 'w': 1920 - x - 40, 'h': SUB_H, 'iw': SUB_ITEM_W,
                         'pw': SUB_ITEM_W - 12, 'back': back, 'text': TEXT, 'content': content}


def chevron(x, width, visible):
    """A small up chevron over a tab: Up opens its sub-menu."""
    return '''
        <control type="image">
            <left>%d</left><top>%d</top><width>28</width><height>16</height>
            <texture colordiffuse="%s">silo/chevron_up.png</texture>
            <visible>%s</visible>
        </control>''' % (x + (width - 28) // 2, BAR_TOP - 22, TEXT, visible)


def custom_submenu():
    """A custom item's submenu (Skin Shortcuts' entries for the item selected
    in the hidden menu list), as a row of pills above the first custom item
    (their places vary), with its chevron."""
    x = bar_positions()[9005] + tab_width('requests') + BAR_GAP
    first = CUSTOM_IDS[0]
    has = 'String.IsEqual(%s,True)' % shortcut(0, 'Property(hasSubmenu)')
    return (submenu_row(x - 6, SUBMENU, 'SetFocus($INFO[%s])' % prop('silo.submenu.from'),
                        '<include>skinshortcuts-submenu</include>')
            + chevron(x, 120, 'Control.HasFocus(%d) + %s' % (first, has)))


def sections_menus():
    """The Movies and Series sections, as rows of pills above their tabs."""
    out = ''
    positions = bar_positions()
    for index, page in enumerate(PAGES):
        if page not in SECTIONS:
            continue
        tab_id = 9002 + index
        items = ''
        for label, path in SECTIONS[page]:
            # Recommended: the page itself (its rows).
            actions = ['ActivateWindow(Videos,%s,return)' % path] if path else \
                ['SetProperty(silo.page,%s,home)' % page, 'ClearProperty(silo.row,home)', 'SetFocus(4000)']
            items += '''
                    <item>
                        <label>%s</label>%s
                    </item>''' % (label, ''.join('\n                        <onclick>%s</onclick>' % a for a in actions))
        out += submenu_row(positions[tab_id] - 6, tab_id + 200, tab_id, items)
        out += chevron(positions[tab_id], tab_width(page), 'Control.HasFocus(%d)' % tab_id)
    return out

def tab(control_id, page, page_index):
    visible = '' if page == 'home' else \
        '\n                <visible>String.Contains(%s,%s)</visible>' % (prop('silo.pages'), page)
    # The group has an id (the button's + 300) so the grouplist can point the
    # custom buttons beside it here.
    return '''
            <control type="group" id="%(group)d">
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
%(open_sections)s                    <onclick%(unless_open)s>SetProperty(silo.page,%(page)s,home)</onclick>
                    <onclick%(unless_open)s>ClearProperty(silo.row,home)</onclick>%(moves)s
%(focus_rows)s
                </control>
            </control>''' % {'width': tab_width(page), 'visible': visible, 'group': control_id + 300,
                            'selected': page_visible(page), 'id': control_id,
                            'label': TAB_LABELS[page],
                            'dim': TAB_DIM, 'text': TEXT, 'page': page,
                            'moves': bar_moves(control_id),
                            'focus_rows': first_visible('onclick', page_rows(page_index, range(1, LOOKAHEAD + 1))),
                            'unless_open': '',
                            'open_sections': open_sections(page, control_id)}


def icon_tab(control_id, icon, action):
    return '''
            <control type="group" id="%(group)d">
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
            </control>''' % {'id': control_id, 'group': control_id + 300, 'text': TEXT, 'action': action, 'icon': icon, 'dim': TAB_DIM,
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
            <animation effect="fade" start="100" end="70" time="200" condition="%(bar_dim)s">Conditional</animation>
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
                         'initial': prop('silo.profile_initial'), 'picture': prop('silo.avatar'),
                         'bar_dim': BAR_DIM}


def shortcut(slot, field):
    return 'Container(%d).ListItemAbsolute(%d).%s' % (SHORTCUTS, slot, field)


def custom_items():
    """The user's own menu items (Skin Shortcuts), as tabs after Requests.
    An item with widgets opens them as rows (the 'custom' page); any other
    runs its action. Returns the hidden list holding the menu, and the tabs."""
    index = PAGES.index('custom')
    buttons = ''
    for slot, control_id in enumerate(CUSTOM_IDS):
        label = shortcut(slot, 'Label')
        has_widgets = '!String.IsEmpty(%s)' % shortcut(slot, 'Property(widgetPath)')
        # OK opens the submenu only for an item with nothing else to show;
        # otherwise Up does (as the tabs' sections).
        to_submenu = 'String.IsEqual(%s,True) + !%s' % (shortcut(slot, 'Property(hasSubmenu)'), has_widgets)
        go = '%s + ![%s]' % (has_widgets, to_submenu)
        actions = ''
        for n in range(1, WIDGETS + 1):
            suffix = '' if n == 1 else '.%d' % n
            for key, field in (('title', 'widgetName'), ('path', 'widgetPath')):
                actions += ('\n                    <onclick condition="%s">SetProperty(silo.custom.%d.%s,$INFO[%s],home)'
                            '</onclick>' % (go, n, key, shortcut(slot, 'Property(%s%s)' % (field, suffix))))
            # The card style chosen in the menu editor, else from what it lists.
            chosen = shortcut(slot, 'Property(widgetStyle%s)' % suffix)
            wide = ('[String.IsEqual(%s,landscape) | [String.IsEmpty(%s) + String.IsEqual(%s,episodes)]]'
                    % (chosen, chosen, shortcut(slot, 'Property(widgetType%s)' % suffix)))
            actions += ('\n                    <onclick condition="%s + %s">SetProperty(silo.custom.%d.style,landscape,home)'
                        '</onclick>\n                    <onclick condition="%s + !%s">'
                        'SetProperty(silo.custom.%d.style,poster,home)</onclick>' % (go, wide, n, go,
                                                                                     wide, n))
        buttons += '''
                <control type="button" id="%(id)d">
                    <visible>!String.IsEmpty(%(label)s)</visible>
                    <width>auto</width><height>60</height>
                    <label>$INFO[%(label)s]</label>
                    <font>silo_tab</font>
                    <textoffsetx>24</textoffsetx>
                    <align>center</align><aligny>center</aligny>
                    <textcolor>%(dim)s</textcolor>
                    <focusedcolor>FF000000</focusedcolor>
                    <texturefocus border="30" colordiffuse="%(text)s">silo/pill.png</texturefocus>
                    <texturenofocus border="30" colordiffuse="%(nofocus)s">silo/pill.png</texturenofocus>%(moves)s
                    <onclick condition="!%(has_widgets)s + ![%(to_submenu)s]">$INFO[%(path)s]</onclick>
                    <onclick condition="%(go)s">SetProperty(silo.page,custom,home)</onclick>
                    <onclick condition="%(go)s">ClearProperty(silo.row,home)</onclick>
                    <onclick condition="%(go)s">SetProperty(silo.custom.button,%(id)d,home)</onclick>%(actions)s
                    <onclick condition="%(go)s">SetProperty(silo.custom.loading,1,home)</onclick>
                    <onclick condition="%(to_submenu)s">SetProperty(silo.submenu.from,%(id)d,home)</onclick>
                    <onclick condition="%(to_submenu)s">SetFocus(%(shortcuts)d,%(slot)d,absolute)</onclick>
                    <onclick condition="%(to_submenu)s">SetFocus(%(submenu)d,0,absolute)</onclick>
                    <onup condition="%(has_submenu)s">SetProperty(silo.submenu.from,%(id)d,home)</onup>
                    <onup condition="%(has_submenu)s">SetFocus(%(shortcuts)d,%(slot)d,absolute)</onup>
                    <onup condition="%(has_submenu)s">SetFocus(%(submenu)d,0,absolute)</onup>
                </control>''' % {'label': label, 'id': control_id, 'dim': TAB_DIM, 'text': TEXT, 'has_widgets': has_widgets,
                             'path': shortcut(slot, 'Property(path)'), 'actions': actions,
                             'go': go, 'to_submenu': to_submenu, 'shortcuts': SHORTCUTS, 'slot': slot,
                             'submenu': SUBMENU, 'has_submenu': 'String.IsEqual(%s,True)' % shortcut(slot, 'Property(hasSubmenu)'),
                             'nofocus': '$VAR[SiloCustomTab%d]' % control_id,
                             # Left and right come from the grouplist: Kodi points its direct
                             # children at their neighbours (passing hidden ones), over ours.
                             'moves': bar_down('                    ')}
    return '''
        <!-- Skin Shortcuts' main menu, built into script-skinshortcuts-includes.xml. -->
        <control type="list" id="%d">
            <left>-3000</left><top>0</top><width>10</width><height>10</height>
            <itemlayout width="10" height="10" />
            <focusedlayout width="10" height="10" />
            <content><include>skinshortcuts-mainmenu</include></content>
        </control>''' % SHORTCUTS, buttons

def custom_tab_variables():
    """A custom item's faint pill while its page shows, as the tabs'."""
    out = ''
    for control_id in CUSTOM_IDS:
        out += ('    <variable name="SiloCustomTab%d">\n'
                '        <value condition="String.IsEqual(%s,custom) + String.IsEqual(%s,%d)">26FFFFFF</value>\n'
                '        <value>00FFFFFF</value>\n    </variable>\n' % (control_id, prop('silo.page'),
                                                                        prop('silo.custom.button'), control_id))
    return out


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
                    <!-- Silo's badge: a faint fill with a brighter rim. -->
                    <texturenofocus border="8">silo/badge_fill.png</texturenofocus>
                    <texturefocus border="8">silo/badge_fill.png</texturefocus>
                    <visible>$EXP[%(shown)s]</visible>
                </control>''' % {'h': height, 'label': label, 'font': font, 'text': TEXT,
                                  'shown': label.replace('$VAR[', 'Has').rstrip(']')}


def build():
    rows = ''.join(row(page, index, slot, landscape)
                   for index, page in enumerate(PAGES)
                   for slot in range(1, rows_of(page) + 1)
                   for landscape in (False, True))
    tabs = icon_tab(9001, 'icons/search.png', 'ActivateWindow(1190)')
    tabs += ''.join(tab(9002 + index, page, index) for index, page in enumerate(TABBED))
    shortcuts_list, custom_tabs = custom_items()
    tabs += custom_tabs
    tabs += icon_tab(9009, 'icons/settings.png', 'ActivateWindow(Settings)')
    # Estuary keeps the power menu on its home screen; this replaces it.
    tabs += icon_tab(9010, 'icons/power.png', 'ActivateWindow(ShutdownMenu)')
    no_rows = ' + '.join('String.IsEmpty(%s)' % prop('silo.%s.count' % page) for page in ('home',))
    return '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by tools/build_home.py: edit that, not this. -->
<window>
    <defaultcontrol always="true">4000</defaultcontrol>
    <onload condition="String.IsEmpty(Window(Home).Property(silo.home.count))">SetFocus(9002)</onload>
    <!-- Kodi starting: the first-row timer may take focus from the bar for a while. -->
    <onload condition="String.IsEmpty(Window(Home).Property(silo.home.count))">SetProperty(silo.startup,1,home)</onload>
    <onload condition="String.IsEmpty(Window(Home).Property(silo.home.count))">AlarmClock(silostartup,ClearProperty(silo.startup,home),00:%(splash_max)d,silent)</onload>
    <!-- Skin Shortcuts writes the user's menu into script-skinshortcuts-includes.xml when it changed. -->
    <onload condition="System.HasAddon(script.skinshortcuts)">RunScript(script.skinshortcuts,type=buildxml&amp;mainmenuID=%(shortcuts)d&amp;group=mainmenu)</onload>
    <backgroundcolor>%(background)s</backgroundcolor>
    <controls>
        <!-- Silo's ambient wash: the focused title's colour, richest behind the art
             (top right) and carried dimmed to the bottom left. -->
        <control type="image">
            <left>0</left><top>0</top><width>1920</width><height>1080</height>
            <texture colordiffuse="$VAR[SiloHeroTint]">silo/tint_wash.png</texture>
            <!-- Hidden under a dialog: Kodi then reads the colour from the dialog's
                 window, finds no row and draws the wash white. -->
            <visible>$EXP[HasSiloTint] + !System.HasActiveModalDialog + !Window.IsVisible(shutdownmenu) + !Window.IsVisible(contextmenu)</visible>
            <animation effect="fade" start="100" end="0" time="160">Hidden</animation>
            <animation effect="fade" start="0" end="100" time="400">Visible</animation>
        </control>
        <!-- The focused title's artwork, crisp at the top right, fading left and down. -->
        <control type="image">
            <!-- 16:9 like the artwork, so Kodi draws it whole: cropped to fit,
                 the fade mask no longer lines up and the left edge shows. -->
            <left>576</left><top>0</top>
            <width>1344</width><height>756</height>
            <aspectratio>stretch</aspectratio>
            <fadetime>240</fadetime>
            <texture background="true" diffuse="silo/hero_mask.png">$VAR[SiloHeroArt]</texture>
        </control>

        <!-- Marquee: never focusable; follows whichever card has focus (on
             Home, its first card until a row has focus). -->
        <control type="group">
            <left>%(x)d</left>
            <visible>!String.IsEmpty(%(row_prop)s) | [[String.IsEqual(Window(Home).Property(silo.page),home) | String.IsEmpty(Window(Home).Property(silo.page))] + [Integer.IsGreater(Window(Home).Property(silo.home.1.cards),0) | Integer.IsGreater(Window(Home).Property(silo.home.2.cards),0)]] | %(waiting)s</visible>
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
            <itemgap>%(row_overlap)d</itemgap>
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
%(wordmark)s
        <!-- Starts where the built-in tabs sit centred, so Movies and Series stay
             over their dropdowns; the user's own items extend it to the right. -->
        <control type="grouplist" id="9000">
            <animation effect="fade" start="100" end="70" time="200" condition="%(bar_dim)s">Conditional</animation>
            <left>%(bar_left)d</left><top>%(tabs_top)d</top>
            <width>%(bar_w)d</width><height>60</height>
            <orientation>horizontal</orientation>
            <itemgap>8</itemgap>%(bar_down)s%(tabs)s
        </control>
%(avatar)s
%(custom)s
%(sections)s%(splash)s
    </controls>
</window>
''' % {'x': SAFE_X, 'text': TEXT, 'dim': TEXT_DIM, 'rows_top': ROWS_TOP, 'rows_h': BAND_H,
       'row_overlap': ROW_PITCH - BAND_H,
       'rows': rows, 'no_rows': no_rows, 'bar_top': BAR_TOP, 'tabs_top': BAR_TOP + 2, 'tabs': tabs,
       'bar_down': bar_down(), 'avatar': avatar(), 'custom': shortcuts_list,
       'bar_left': bar_positions()[9001], 'bar_w': 1920 - SAFE_X - 64 - 16 - bar_positions()[9001], 'shortcuts': SHORTCUTS, 'sections': sections_menus() + custom_submenu(), 'bar_dim': BAR_DIM, 'row_prop': prop('silo.row'), 'wordmark': wordmark(SAFE_X, BAR_TOP, '\n            <animation effect="fade" start="100" end="70" time="200" condition="%s">Conditional</animation>' % BAR_DIM), 'waiting': ' | '.join('[%s]' % c for c, _ in waiting_rows()), 'background': BACKGROUND, 'splash_max': SPLASH_MAX,
       # The age rating as Silo draws it: the quality badges' size, centred on the info line.
       'splash': splash(), 'mpaa_badge': badge('$VAR[SiloMpaa]', 34, 'silo_badge').replace(
           '<width>auto</width><height>34</height>', '<top>3</top><width>auto</width><height>34</height>', 1),
       'quality_badges': ''.join(badge('$VAR[SiloBadge%d]' % n, 36, 'silo_badge') for n in (1, 2, 3))}


# The hero and marquee read from the row that last had focus (silo.row), so
# they stay put while the menu bar has focus, as in Silo. Each entry is a
# (condition, value) template; LI stands for that row's ListItem.
# A Home card: an item SiloKodiConnect published as properties (rows.py).
HOME_CARD = '!String.IsEmpty(LI.Property(home.type))'
HERO_STATIC = {'SiloHeroArt': 'home.art.fanart', 'SiloLogoArt': 'home.art.clearlogo', 'SiloTitle': 'home.hero.title', 'SiloMetaLine': 'home.hero.meta', 'SiloPlot': 'home.plot', 'SiloDetail': 'home.hero.detail', 'SiloMpaa': 'home.mpaa', 'SiloHeroTint': 'home.tint', 'SiloBadge1': 'home.badge1', 'SiloBadge2': 'home.badge2', 'SiloBadge3': 'home.badge3'}

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
    # A Requests card: its state (Requested, Downloading, Available...).
    ('SiloDetail', [('!String.IsEmpty(LI.Property(silo.request.label))', '$INFO[LI.Property(silo.request.label)]'),
                    ('String.IsEqual(LI.DBType,episode)', '$INFO[LI.Property(silo.aired)]'
                     '$INFO[LI.Property(silo.cast), · ,]'),
                    (None, '$INFO[LI.Property(silo.cast)]')]),
    ('SiloMpaa', [(None, '$INFO[LI.Property(silo.mpaa)]')]),
    ('SiloHeroTint', [(None, '$INFO[LI.Property(silo.tint)]')]),
    ('SiloBadge1', [(None, '$INFO[LI.Property(silo.badge1)]')]),
    ('SiloBadge2', [(None, '$INFO[LI.Property(silo.badge2)]')]),
    ('SiloBadge3', [(None, '$INFO[LI.Property(silo.badge3)]')]),
]

CARDS = '''
    <variable name="SiloCardTitle">
        <value condition="!String.IsEmpty(ListItem.Property(home.type))">$INFO[ListItem.Property(home.card.title)]</value>
        <value condition="String.IsEqual(ListItem.DBType,episode)">$INFO[ListItem.TVShowTitle]</value>
        <value>$INFO[ListItem.Label]</value>
    </variable>
    <variable name="SiloCardEpisode">
        <value condition="!String.IsEmpty(ListItem.Property(home.type))">$INFO[ListItem.Property(home.card.wide_sub)]</value>
        <value condition="String.IsEqual(ListItem.DBType,episode)">$INFO[ListItem.Property(silo.code)]$INFO[ListItem.Title, • ,]</value>
        <value>$INFO[ListItem.Year]</value>
    </variable>
    <variable name="SiloCardYear">
        <value condition="!String.IsEmpty(ListItem.Property(home.type))">$INFO[ListItem.Property(home.card.sub)]</value>
        <value condition="!String.IsEmpty(ListItem.Property(silo.request.label))">$INFO[ListItem.Property(silo.request.label)]</value>
        <value condition="String.IsEqual(ListItem.DBType,episode)">$INFO[ListItem.Property(silo.code)]</value>
        <value>$INFO[ListItem.Year]</value>
    </variable>
    <variable name="SiloPosterArt">
        <value condition="!String.IsEmpty(ListItem.Property(home.type))">$INFO[ListItem.Property(home.art.poster)]</value>
        <value condition="!String.IsEmpty(ListItem.Art(poster))">$INFO[ListItem.Art(poster)]</value>
        <value condition="!String.IsEmpty(ListItem.Art(tvshow.poster))">$INFO[ListItem.Art(tvshow.poster)]</value>
        <value>$INFO[ListItem.Art(thumb)]</value>
    </variable>
    <variable name="SiloLandscapeArt">
        <value condition="!String.IsEmpty(ListItem.Property(home.type))">$INFO[ListItem.Property(home.art.landscape)]</value>
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
    rows = [list_id(index, slot, landscape) for index, page in enumerate(PAGES)
            for slot in range(1, rows_of(page) + 1) for landscape in (False, True)]
    out = '\n    <!-- Silo Skyline (tools/build_home.py) -->' + CARDS + custom_tab_variables()
    for index, page in enumerate(PAGES):
        for slot in range(1, rows_of(page) + 1):
            for landscape in (False, True):
                out += '    <expression name="SiloRow%d">%s</expression>\n' % (
                    list_id(index, slot, landscape), row_rules(page, index, slot, landscape))
    # Kodi's conditions can't test a $VAR, so each badge's "has text" is an
    # expression over the remembered row, like the hero variables.
    for name, item_property in (('SiloMpaa', 'silo.mpaa'), ('SiloTint', 'silo.tint'),
                                ('SiloBadge1', 'silo.badge1'),
                                ('SiloBadge2', 'silo.badge2'), ('SiloBadge3', 'silo.badge3')):
        home_property = 'home.' + item_property.split('.', 1)[1]
        terms = ['[String.IsEqual(%s,%d) + [!String.IsEmpty(Container(%d).ListItem.Property(%s)) | '
                 '!String.IsEmpty(Container(%d).ListItem.Property(%s))]]'
                 % (prop('silo.row'), row_id, row_id, item_property, row_id, home_property) for row_id in rows]
        terms += ['[%s + [!String.IsEmpty(Container(%d).ListItem.Property(%s)) | '
                  '!String.IsEmpty(Container(%d).ListItem.Property(%s))]]'
                  % (waiting, row_id, item_property, row_id, home_property) for waiting, row_id in waiting_rows()]
        terms += ['[%s + !String.IsEmpty(%s)]' % (home_waiting(row), prop('silo.home.%d.1.%s' % (row, home_property[5:])))
                  for row in (1, 2)]
        out += '    <expression name="Has%s">%s</expression>\n' % (name, ' | '.join(terms))
    out += EMPTY_HOME
    for name, entries in HERO:
        # A Home card (SiloKodiConnect's published rows) carries its text ready.
        entries = [(HOME_CARD, '$INFO[LI.Property(%s)]' % HERO_STATIC[name])] + entries
        out += '    <variable name="%s">\n' % name
        for row_id in rows:
            item = 'Container(%d).ListItem' % row_id
            mine = 'String.IsEqual(%s,%d)' % (prop('silo.row'), row_id)
            for condition, value in entries:
                full = mine + (' + [%s]' % condition.replace('LI', item) if condition else '')
                out += '        <value condition="%s">%s</value>\n' % (full, value.replace('LI', item))
        # Switching to Home clears the remembered row until the first row takes
        # focus (a timer): show Home's first card meanwhile, not a black hero.
        if name in HERO_STATIC:
            field = HERO_STATIC[name][len('home.'):]
            for row in (1, 2):
                out += '        <value condition="%s">$INFO[%s]</value>\n' % (
                    home_waiting(row), prop('silo.home.%d.1.%s' % (row, field)))
        # Another page before a row has focus: its first loaded row's item.
        for waiting, row_id in waiting_rows():
            item = 'Container(%d).ListItem' % row_id
            for condition, value in entries:
                full = waiting + (' + [%s]' % condition.replace('LI', item) if condition else '')
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
    and focus is nowhere (Home's default row couldn't take it), never on the
    bar or the avatar, then focuses the first row showing a second later; it
    starts again if that row was still loading. Timers.xml gets its conditions in full: it has no $EXP."""
    ready, focus = [], []
    for index, page in enumerate(PAGES):
        rows = [(slot, landscape) for slot in range(1, LOOKAHEAD + 1) for landscape in (False, True)]
        loaded = ' | '.join('Integer.IsGreater(Container(%d).NumItems,0)' % list_id(index, slot, landscape)
                            for slot, landscape in rows)
        # Not from the bar, where someone chose to be (a tab's page fills its
        # hero from its first row without focus), except as Kodi starts.
        ready.append('[%s + [%s] + [[!ControlGroup(9000).HasFocus() + !Control.HasFocus(9011)] | '
                     '!String.IsEmpty(%s)]]' % (page_visible(page), loaded, prop('silo.startup')))
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
            + splash_timer() + TIMER_END)


SPLASH_MAX = 20  # seconds: the splash never holds longer, whatever happens


def splash_timer():
    """Lifts the splash (silo.ready) once Home's first rows have items, or
    after SPLASH_MAX seconds (signed out, no rows, Silo unreachable)."""
    loaded = ' | '.join('Integer.IsGreater(Container(%d).NumItems,0)' % list_id(0, slot, landscape)
                        for slot in (1, 2) for landscape in (False, True))
    return ('    <timer>\n'
            '        <name>silo_splash</name>\n'
            '        <description>Lift the start-up splash once Home has rows (tools/build_home.py)</description>\n'
            '        <start>Window.IsActive(home) + String.IsEmpty(%(ready)s)</start>\n'
            '        <stop>%(loaded)s | Integer.IsGreaterOrEqual(Skin.TimerElapsedSecs(silo_splash),%(max)d)</stop>\n'
            '        <onstop>SetProperty(silo.ready,1,home)</onstop>\n'
            '    </timer>\n' % {'ready': prop('silo.ready'), 'loaded': loaded, 'max': SPLASH_MAX})


def wordmark(x, top, extra=''):
    """Silo Skyline's mark and name, top left on Home, Browse and Search."""
    return '''        <!-- Silo Skyline's mark and name (media/silo/skyline_mark.png). -->
        <control type="grouplist">
            <left>%(x)d</left><top>%(top)d</top>
            <width>440</width><height>64</height>
            <orientation>horizontal</orientation>
            <itemgap>12</itemgap>
            <usecontrolcoords>true</usecontrolcoords>%(extra)s
            <control type="image">
                <top>6</top><width>52</width><height>52</height>
                <texture>silo/skyline_mark.png</texture>
            </control>
            <control type="label">
                <width>auto</width><height>64</height>
                <aligny>center</aligny>
                <font>silo_wordmark</font>
                <textcolor>%(text)s</textcolor>
                <label>Silo</label>
            </control>
            <control type="label">
                <width>auto</width><height>64</height>
                <aligny>center</aligny>
                <font>silo_wordmark_light</font>
                <textcolor>%(dim)s</textcolor>
                <label>Skyline</label>
            </control>
        </control>''' % {'x': x, 'top': top, 'extra': extra, 'text': TEXT, 'dim': TEXT_DIM}


def splash():
    """Silo's start-up screen over Home until its first rows are in (a
    property, so it shows once per Kodi start, never on returning to Home)."""
    return '''
        <control type="group">
            <visible>String.IsEmpty(%(ready)s)</visible>
            <animation effect="fade" start="100" end="0" time="400">Hidden</animation>
            <control type="image">
                <width>1920</width><height>1080</height>
                <texture>silo/splash_bg.png</texture>
            </control>
            <control type="image">
                <left>840</left><top>270</top><width>240</width><height>240</height>
                <texture>silo/skyline_mark.png</texture>
            </control>
            <control type="grouplist">
                <left>0</left><top>540</top><width>1920</width><height>110</height>
                <orientation>horizontal</orientation>
                <align>center</align>
                <itemgap>22</itemgap>
                <control type="label">
                    <width>auto</width><height>110</height>
                    <aligny>center</aligny>
                    <font>silo_title</font>
                    <textcolor>%(text)s</textcolor>
                    <label>Silo</label>
                </control>
                <control type="label">
                    <width>auto</width><height>110</height>
                    <aligny>center</aligny>
                    <font>silo_title_light</font>
                    <textcolor>BFEDEDED</textcolor>
                    <label>Skyline</label>
                </control>
            </control>
            <control type="image">
                <left>936</left><top>720</top><width>48</width><height>48</height>
                <animation effect="rotate" start="0" end="-360" center="auto" time="900" loop="true" reversible="false" condition="true">Conditional</animation>
                <texture colordiffuse="99EDEDED">silo/spinner_arc.png</texture>
            </control>
        </control>''' % {'ready': prop('silo.ready'), 'background': BACKGROUND, 'text': TEXT}


TIMER_START, TIMER_END = '    <!-- Silo Skyline (tools/build_home.py) -->\n', '    <!-- end Silo Skyline -->\n'


def add_timer():
    path = os.path.join(ROOT, 'xml', 'Timers.xml')
    text = open(path, encoding='utf-8').read()
    if TIMER_START in text:
        text = text[:text.index(TIMER_START)] + text[text.index(TIMER_END) + len(TIMER_END):]
    text = text.replace('</timers>', first_row_timer() + '</timers>')
    open(path, 'w', encoding='utf-8').write(text)


if __name__ == '__main__':
    write_card_includes()
    with open(os.path.join(ROOT, 'xml', 'Home.xml'), 'w', encoding='utf-8') as handle:
        handle.write(build())
    add_variables()
    add_fonts()
    add_timer()
    print('Wrote xml/Home.xml, the Silo variables in xml/Variables.xml, its fonts in xml/Font.xml and its '
          'start-up focus timer in xml/Timers.xml')
