"""Write xml/MyVideoNav.xml: Kodi's video browsing window in Silo's style.

    python3 tools/build_browse.py

Browse on a show and the menu behind the profile avatar open this window. It
gets a header (the folder's name and how many items it holds) and one view
per kind of content, each shown only for its content so Kodi always lands on
the right one: a poster grid for films, shows, sets and seasons (51), episode
stills with their details (52), and a list of pills for everything else, such
as an add-on's menu or a folder (50). Films and shows have two more views,
Kodi's own as any skin's (so an add-on's films get them too): a hero over two
rows of posters (55, Plex's and Apple TV's) and a list beside the focused
title's details (56, Infuse's). Left from a view opens a side panel with
Kodi's View, Sort by and Order buttons (2, 3, 4), as Estuary's; Kodi keeps
the chosen view per folder. Films and shows get an A-Z bar (60) right of the
view, which SiloKodiConnect answers by jumping to the letter.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_home import rt_list_marks, wordmark, focus_sheen, focus_zoom, watched_mark, BACKGROUND, ROOT, SAFE_X, TEXT, TEXT_DIM, TITLE_DIM, SUB_DIM, GRID_BACKDROP  # noqa: E402

# An add-on's videos (content videos) get the poster grid too, and its views.
GRID = ('Container.Content(movies) | Container.Content(tvshows) | Container.Content(sets) | Container.Content(seasons)'
        ' | Container.Content(videos)')
HERO_VIEW, DETAIL_VIEW = 55, 56
TITLE_VIEWS = (51, HERO_VIEW, DETAIL_VIEW)  # the views films and shows can use
MENU_ID, MENU_W = 9000, 560
EPISODES = 'Container.Content(episodes)'
VIEWS_TOP = 200

# Poster grid: Silo's 2:3 cards, six to a row, the size of Browse's
# (tools/build_library.py) so a collection or genre reads the same.
POSTER_COLS = 6
POSTER_GAP = 24
POSTER_W = (1920 - 2 * SAFE_X - 96 - 24) // POSTER_COLS - POSTER_GAP
POSTER_H = POSTER_W * 3 // 2
POSTER_ITEM_H = POSTER_H + 12 + 76 + 24
# A-Z bar right of the poster grid, for films and shows: a letter asks
# SiloKodiConnect (NotifyAll) to jump the grid to the first title from it.
JUMP_ID = 60
LETTERS = ['#'] + [chr(c) for c in range(ord('A'), ord('Z') + 1)]
# The library's own films and shows only: an add-on's lists are seldom in title order.
JUMP_BAR = ('[Container.Content(movies) | Container.Content(tvshows)] + Integer.IsGreater(Container.NumItems,20)'
            ' + String.StartsWith(Container.FolderPath,videodb://)')
# Episode list: a 16:9 still, then the episode's details beside it.
STILL_W, STILL_H = 360, 202
WATCHED = ('Integer.IsGreater(ListItem.PlayCount,0) | [Integer.IsGreater(ListItem.Property(TotalEpisodes),0)'
           ' + Integer.IsEqual(ListItem.Property(UnWatchedEpisodes),0)]')
EPISODE_ITEM_H = STILL_H + 12 + 32


def poster(focused, view_id):
    zoom = focus_zoom('Control.HasFocus(%d)' % view_id) if focused else ''
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
                <control type="group">%(zoom)s
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
%(sheen)s%(watched)s
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
                        <textcolor>%(sub_colour)s</textcolor>
                        <label>$VAR[SiloBrowseSub]</label>
                    </control>
                </control>''' % {'w': POSTER_W, 'h': POSTER_H, 'pw': POSTER_W - 24, 'text': TEXT, 'dim': TEXT_DIM,
                                     'watched': watched_mark(POSTER_W, POSTER_H, 'silo/card_poster_mask.png', WATCHED,
                                                            'Control.HasFocus(%d)' % view_id if focused else '', 20), 'zoom': zoom,
                                     'sheen': focus_sheen(POSTER_W, POSTER_H, 'silo/card_poster_mask.png', 'silo/card_poster_rim.png',
                                                          'Control.HasFocus(%d)' % view_id, 20) if focused else '', 't1': POSTER_H + 20, 't2': POSTER_H + 54,
                                     'title_color': title_color, 'dim_visible': dim_visible,
                                     'sub_colour': TEXT if focused else SUB_DIM,
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
    zoom = focus_zoom(lit, 20) if focused else ''
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
                    </control>
                </control>''' % {'zoom': zoom, 'w': FAN_W, 'h': FAN_H, 'minis': minis, 'tx': 292, 'ty': 50,
                                 'tw': FAN_W - 292 - 20, 'cy': FAN_H - 62, 'text': TEXT}


def episode(focused, view_id):
    title_color = TEXT if focused else TITLE_DIM
    zoom = focus_zoom('Control.HasFocus(%d)' % view_id) if focused else ''
    return '''
                <control type="group">%(zoom)s
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
%(sheen)s%(watched)s
                </control>
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
                        <label>$INFO[ListItem.Duration(mins),, min]$INFO[ListItem.Art(siloaired), · ,]</label>
                    </control>
                    <control type="textbox">
                        <left>%(x)d</left><top>100</top>
                        <width>1100</width><height>60</height>
                        <font>silo_detail</font>
                        <textcolor>%(dim)s</textcolor>
                        <label>$INFO[ListItem.Plot]</label>
                    </control>''' % {'w': STILL_W, 'h': STILL_H, 'pw': STILL_W - 28, 'text': TEXT, 'dim': TEXT_DIM,
                                     'watched': watched_mark(STILL_W, STILL_H, 'silo/card_landscape_mask.png', 'Integer.IsGreater(ListItem.PlayCount,0)',
                                                            'Control.HasFocus(%d)' % view_id if focused else '', 24),
                                     'zoom': zoom, 'x': STILL_W + 52,
                                     'sheen': focus_sheen(STILL_W, STILL_H, 'silo/card_landscape_mask.png', 'silo/card_landscape_rim.png',
                                                          'Control.HasFocus(%d)' % view_id, 20) if focused else '', 'title_color': title_color}


def to_view(tag, indent):
    """<tag>s that focus whichever title view is showing."""
    return ''.join('%s<%s condition="Control.IsVisible(%d)">%d</%s>\n' % (indent, tag, view, view, tag) for view in TITLE_VIEWS)


def jump_bar():
    """The A-Z column (Browse's, tools/build_library.py): the selected title's
    letter lit; a letter jumps the grid to it (SiloKodiConnect's jump.py)."""
    from build_library import AZ_W, letter_layouts
    current = '[%s]' % ' | '.join('[Control.IsVisible(%d) + String.IsEqual(ListItem.Label,Container(%d).ListItem.SortLetter)]'
                                  % (view, view) for view in TITLE_VIEWS)
    items = ''.join('''
                <item>
                    <label>%s</label>%s
                </item>''' % (letter, ''.join('''
                    <onclick condition="Control.IsVisible(%d)">NotifyAll(silokodi,jump.%d.%s)</onclick>'''
                                              % (view, view, letter) for view in TITLE_VIEWS)) for letter in LETTERS)
    return '''
        <!-- A-Z: jump the poster grid to a letter (SiloKodiConnect's jump.py). -->
        <control type="list" id="%(id)d">
            <left>%(x)d</left><top>%(top)d</top>
            <width>%(w)d</width><height>%(h)d</height>
            <orientation>vertical</orientation>
%(back)s            <onright>noop</onright>
            <scrolltime tween="cubic" easing="out">200</scrolltime>
            <visible>$EXP[SiloBrowseGrid] + %(bar)s</visible>%(layouts)s
            <content>%(items)s
            </content>
        </control>''' % {'id': JUMP_ID, 'x': 1920 - SAFE_X - AZ_W, 'top': VIEWS_TOP, 'w': AZ_W,
                         'h': 1080 - VIEWS_TOP, 'bar': JUMP_BAR,
                         'layouts': letter_layouts(JUMP_ID, current), 'items': items,
                         'back': to_view('onleft', '            ')}


# The hero view: eight smaller posters to a row, two rows under the hero.
HERO_ITEM_W = (1920 - 2 * SAFE_X - 96 - 24) // 8
HERO_POSTER_W = HERO_ITEM_W - 24
HERO_POSTER_H = HERO_POSTER_W * 3 // 2
HERO_ITEM_H = HERO_POSTER_H + 24
HERO_TOP = 1080 - 2 * HERO_ITEM_H
# The list view: rows on the left, the details on the right.
# Their view types aren't "list" or "poster": Kodi opens a folder it has no
# view for in the first view of its default type, which is to stay the grid.
DETAIL_ROW, DETAIL_LIST_W = 66, 780
DETAIL_X = SAFE_X + DETAIL_LIST_W + 20
DETAIL_INFO_X = DETAIL_X + 330
DETAIL_INFO_W = 1920 - SAFE_X - 96 - 24 - DETAIL_INFO_X
DETAIL_W = 1920 - SAFE_X - 96 - 24 - DETAIL_X
# A library film's or show's OK: its details page (SiloKodiConnect's), as
# Browse's; anything else does what Kodi does.
INFO_CLICK = ('\n            <onclick condition="System.AddonIsEnabled(plugin.video.silokodiconnect) + '
              '[Container.Content(movies) | Container.Content(tvshows)] + Integer.IsGreater(ListItem.DBID,0)">'
              'RunPlugin(plugin://plugin.video.silokodiconnect/?mode=info&amp;type=$INFO[ListItem.DBType]'
              '&amp;dbid=$INFO[ListItem.DBID])</onclick>')


def hero_poster(focused, view_id):
    """The hero view's poster: no captions (the hero names the title)."""
    lit = 'Control.HasFocus(%d)' % view_id
    return '''
                <control type="group">%(zoom)s
                <control type="image">
                    <left>6</left><top>6</top><width>%(w)d</width><height>%(h)d</height>
                    <aspectratio>scale</aspectratio>
                    <texture background="true" diffuse="silo/card_poster_mask.png" fallback="colors/grey.png">$VAR[SiloBrowsePoster]</texture>
                </control>%(sheen)s%(watched)s
                </control>''' % {'w': HERO_POSTER_W, 'h': HERO_POSTER_H, 'zoom': focus_zoom(lit, 20) if focused else '',
                                 'sheen': focus_sheen(HERO_POSTER_W, HERO_POSTER_H, 'silo/card_poster_mask.png',
                                                      'silo/card_poster_rim.png', lit, 16) if focused else '',
                                 'watched': watched_mark(HERO_POSTER_W, HERO_POSTER_H, 'silo/card_poster_mask.png', WATCHED,
                                                         'Control.HasFocus(%d)' % view_id if focused else '', 16)}


def detail_row(focused):
    """A row of the list view: the title and its year; the focused row black
    on the white pill while the list has focus."""
    lit = 'Control.HasFocus(%d)' % DETAIL_VIEW

    def parts(colour, dim, visible):
        v = '\n                    <visible>%s</visible>' % visible if visible else ''
        return '''
                <control type="label">
                    <left>28</left><width>%(lw)d</width><height>%(row)d</height>
                    <aligny>center</aligny>
                    <font>silo_meta</font>
                    <textcolor>%(c)s</textcolor>
                    <label>$VAR[SiloBrowseLabel]</label>%(v)s
                </control>
                <control type="label">
                    <right>28</right><width>140</width><height>%(row)d</height>
                    <align>right</align><aligny>center</aligny>
                    <font>silo_meta</font>
                    <textcolor>%(d)s</textcolor>
                    <label>$INFO[ListItem.Year]</label>%(v)s
                </control>''' % {'row': DETAIL_ROW, 'lw': DETAIL_LIST_W - 200, 'c': colour, 'd': dim, 'v': v}
    if not focused:
        return parts(TITLE_DIM, SUB_DIM, '')
    return '''
                <control type="image">
                    <left>4</left><top>4</top><width>%(w)d</width><height>%(h)d</height>
                    <texture border="28" colordiffuse="%(text)s">silo/pill.png</texture>
                    <visible>%(lit)s</visible>
                </control>''' % {'w': DETAIL_LIST_W - 8, 'h': DETAIL_ROW - 8, 'text': TEXT, 'lit': lit} \
        + parts('FF000000', '8C000000', lit) + parts(TEXT, TEXT_DIM, '!' + lit)


def rating_marks(indent):
    """IMDb's and TMDB's marks with their scores, as the hero's."""
    out = ''
    for rating, mark, width, height, top in (('imdb', 'silo/imdb.png', 60, 28, 6),
                                             ('themoviedb', 'silo/tmdb.png', 165, 30, 5)):
        # TMDB's from SiloKodiConnect's extras (Kodi's lists load only the default
        # rating), else Kodi's own (an add-on's titles).
        score = 'ListItem.Rating(%s)' % rating
        if rating == 'themoviedb':
            score = 'ListItem.Art(silotmdb)'
        out += '''
%(i)s<control type="image">
%(i)s    <top>%(top)d</top><width>%(w)d</width><height>%(h)d</height>
%(i)s    <texture>%(mark)s</texture>
%(i)s    <visible>!String.IsEmpty(%(score)s)</visible>
%(i)s</control>
%(i)s<control type="label">
%(i)s    <width>auto</width><height>40</height>
%(i)s    <aligny>center</aligny>
%(i)s    <font>silo_meta</font>
%(i)s    <textcolor>%(dim)s</textcolor>
%(i)s    <label> [B]$INFO[%(score)s][/B]   </label>
%(i)s    <visible>!String.IsEmpty(%(score)s)</visible>
%(i)s</control>''' % {'i': indent, 'top': top, 'w': width, 'h': height, 'mark': mark, 'score': score, 'dim': TEXT_DIM}
    return out + rt_list_marks('ListItem', indent, TEXT_DIM)


def mpaa_badge(indent):
    return '''
%(i)s<control type="button">
%(i)s    <width>auto</width><height>36</height>
%(i)s    <label>$INFO[ListItem.Mpaa]</label>
%(i)s    <font>silo_badge</font>
%(i)s    <textoffsetx>12</textoffsetx>
%(i)s    <aligny>center</aligny>
%(i)s    <enable>false</enable>
%(i)s    <disabledcolor>%(text)s</disabledcolor>
%(i)s    <texturenofocus border="8" colordiffuse="B3FFFFFF">silo/badge_outline.png</texturenofocus>
%(i)s    <texturefocus border="8" colordiffuse="B3FFFFFF">silo/badge_outline.png</texturefocus>
%(i)s    <visible>!String.IsEmpty(ListItem.Mpaa)</visible>
%(i)s</control>''' % {'i': indent, 'text': TEXT}


def title_art(left, top, width, height):
    """The focused title's clearlogo, or its name without one."""
    return '''
            <control type="image">
                <left>%(x)d</left><top>%(y)d</top><width>%(w)d</width><height>%(h)d</height>
                <aspectratio align="left" aligny="bottom">keep</aspectratio>
                <texture background="true">$INFO[ListItem.Art(clearlogo)]</texture>
            </control>
            <control type="label">
                <left>%(x)d</left><top>%(y)d</top><width>%(w)d</width><height>%(h)d</height>
                <aligny>bottom</aligny>
                <font>silo_osd_title</font>
                <textcolor>%(text)s</textcolor>
                <label>$INFO[ListItem.Label]</label>
                <visible>String.IsEmpty(ListItem.Art(clearlogo))</visible>
            </control>''' % {'x': left, 'y': top, 'w': width, 'h': height, 'text': TEXT}


def facts_line(left, top, width, indent='                ', marks=True):
    """Age badge, then year · runtime · genre, then the rating marks (marks)."""
    return '''
            <control type="grouplist">
                <left>%(x)d</left><top>%(y)d</top><width>%(w)d</width><height>40</height>
                <orientation>horizontal</orientation>
                <itemgap>14</itemgap>
                <usecontrolcoords>true</usecontrolcoords>%(mpaa)s
                <control type="label">
                    <width>auto</width><height>40</height>
                    <aligny>center</aligny>
                    <font>silo_meta</font>
                    <textcolor>%(dim)s</textcolor>
                    <label>$INFO[ListItem.Year]$INFO[ListItem.Duration(mins),  ·  , min]$VAR[SiloViewGenre]</label>
                </control>%(marks)s
            </control>''' % {'x': left, 'y': top, 'w': width, 'dim': TEXT_DIM, 'mpaa': mpaa_badge(indent),
                             'marks': rating_marks(indent) if marks else ''}


def title_views():
    """The hero and list views, and what each draws of the focused title."""
    return '''
        <!-- Films and shows, as a hero: the focused title over two rows of posters. -->
        <control type="group">
            <visible>Control.IsVisible(%(hero)d)</visible>
            <control type="image">
                <left>576</left><top>0</top><width>1344</width><height>756</height>
                <aspectratio>stretch</aspectratio>
                <fadetime>240</fadetime>
                <texture background="true" colordiffuse="99FFFFFF" diffuse="silo/hero_mask.png">$VAR[SiloViewArt]</texture>
            </control>%(hero_title)s%(hero_facts)s
            <control type="textbox">
                <left>%(x)d</left><top>%(plot_y)d</top><width>980</width><height>66</height>
                <font>silo_detail</font>
                <textcolor>%(text)s</textcolor>
                <label>$INFO[ListItem.Plot]</label>
            </control>
        </control>
        <control type="panel" id="%(hero)d">
            <left>%(gx)d</left><top>%(hero_top)d</top>
            <width>%(hw)d</width><height>%(hh)d</height>
            <orientation>vertical</orientation>
            <scrolltime tween="cubic" easing="out">280</scrolltime>
            <viewtype label="Hero">bigwide</viewtype>
            <visible>$EXP[SiloBrowseTitles]</visible>
            <onleft>%(menu)d</onleft>
            <onright condition="%(bar)s">%(jump)d</onright>%(click)s
            <itemlayout width="%(hiw)d" height="%(hih)d">%(hero_card)s
            </itemlayout>
            <focusedlayout width="%(hiw)d" height="%(hih)d">%(hero_card_focused)s
            </focusedlayout>
        </control>

        <!-- Films and shows, as a list beside the focused title's details. -->
        <control type="group">
            <visible>Control.IsVisible(%(detail)d)</visible>
            <control type="image">
                <left>%(dx)d</left><top>%(top)d</top><width>300</width><height>450</height>
                <aspectratio>scale</aspectratio>
                <texture background="true" diffuse="silo/card_poster_mask.png" fallback="colors/grey.png">$VAR[SiloBrowsePoster]</texture>
            </control>%(detail_title)s%(detail_facts)s
            <!-- The ratings on their own line: the column is too narrow for them beside the facts. -->
            <control type="grouplist">
                <left>%(ix)d</left><top>%(marks_y)d</top><width>%(iw)d</width><height>40</height>
                <orientation>horizontal</orientation>
                <usecontrolcoords>true</usecontrolcoords>%(detail_marks)s
            </control>
            <control type="label">
                <left>%(ix)d</left><top>%(badges_y)d</top><width>%(iw)d</width><height>40</height>
                <font>silo_meta</font>
                <textcolor>%(dim)s</textcolor>
                <label>$INFO[ListItem.Art(silobadge1)]$INFO[ListItem.Art(silobadge2),  ·  ,]$INFO[ListItem.Art(silobadge3),  ·  ,]</label>
            </control>
            <control type="textbox">
                <left>%(ix)d</left><top>%(cast_y)d</top><width>%(iw)d</width><height>90</height>
                <font>silo_detail</font>
                <textcolor>%(dim)s</textcolor>
                <label>$INFO[ListItem.Art(silocast)]</label>
            </control>
            <control type="textbox">
                <left>%(dx)d</left><top>%(dplot_y)d</top><width>%(dw)d</width><height>%(dplot_h)d</height>
                <font>silo_detail</font>
                <textcolor>%(text)s</textcolor>
                <label>$INFO[ListItem.Plot]</label>
            </control>
        </control>
        <control type="list" id="%(detail)d">
            <left>%(gx)d</left><top>%(top)d</top>
            <width>%(lw)d</width><height>%(lh)d</height>
            <orientation>vertical</orientation>
            <scrolltime tween="cubic" easing="out">200</scrolltime>
            <viewtype label="List">biginfo</viewtype>
            <visible>$EXP[SiloBrowseTitles]</visible>
            <onleft>%(menu)d</onleft>
            <onright condition="%(bar)s">%(jump)d</onright>%(click)s
            <itemlayout width="%(lw)d" height="%(row)d">%(row_normal)s
            </itemlayout>
            <focusedlayout width="%(lw)d" height="%(row)d">%(row_focused)s
            </focusedlayout>
        </control>
''' % {'hero': HERO_VIEW, 'detail': DETAIL_VIEW, 'menu': MENU_ID, 'x': SAFE_X, 'text': TEXT, 'dim': TEXT_DIM,
       'hero_title': title_art(SAFE_X, 206, 820, 130), 'hero_facts': facts_line(SAFE_X, 344, 1200),
       'plot_y': 394, 'gx': SAFE_X - 6, 'hero_top': HERO_TOP, 'hw': 8 * HERO_ITEM_W + 12, 'hh': 1080 - HERO_TOP,
       'hiw': HERO_ITEM_W, 'hih': HERO_ITEM_H, 'hero_card': hero_poster(False, HERO_VIEW),
       'hero_card_focused': hero_poster(True, HERO_VIEW), 'bar': JUMP_BAR, 'jump': JUMP_ID, 'click': INFO_CLICK,
       'dx': DETAIL_X, 'top': VIEWS_TOP, 'ix': DETAIL_INFO_X, 'iw': DETAIL_INFO_W, 'dw': DETAIL_W,
       'detail_title': title_art(DETAIL_INFO_X, VIEWS_TOP, DETAIL_INFO_W, 120),
       'detail_facts': facts_line(DETAIL_INFO_X, VIEWS_TOP + 136, DETAIL_INFO_W, marks=False),
       'detail_marks': rating_marks('                '), 'marks_y': VIEWS_TOP + 184,
       'badges_y': VIEWS_TOP + 234, 'cast_y': VIEWS_TOP + 282, 'dplot_y': VIEWS_TOP + 480,
       'dplot_h': 1080 - VIEWS_TOP - 520, 'lw': DETAIL_LIST_W, 'lh': 1080 - VIEWS_TOP - 24, 'row': DETAIL_ROW,
       'row_normal': detail_row(False), 'row_focused': detail_row(True)}


def side_menu():
    """Estuary's side panel in Silo's look: Kodi's own View, Sort by and Order
    buttons (Kodi labels them "View: ..." and "Sort by: ..." and does what they
    say). It waits off screen and slides in while it has focus."""
    back = to_view('onright', '                ') + to_view('onback', '                ')
    return '''
        <!-- View and sort, from the left (Left from a view's first column). -->
        <control type="group">
            <left>-%(w)d</left>
            <animation effect="slide" start="0,0" end="%(w)d,0" time="220" tween="cubic" easing="out" condition="ControlGroup(%(menu)d).HasFocus">Conditional</animation>
            <control type="image">
                <left>0</left><top>0</top><width>%(w)d</width><height>1080</height>
                <texture colordiffuse="F21C1F24">colors/white.png</texture>
            </control>
            <control type="label">
                <left>%(x)d</left><top>%(ty)d</top><width>%(bw)d</width><height>40</height>
                <aligny>center</aligny>
                <font>silo_badge</font>
                <textcolor>99EDEDED</textcolor>
                <label>VIEW AND SORT</label>
            </control>
            <control type="grouplist" id="%(menu)d">
                <left>%(bx)d</left><top>%(top)d</top><width>%(bw)d</width><height>400</height>
                <orientation>vertical</orientation>
                <itemgap>8</itemgap>
                <onleft>noop</onleft><onup>noop</onup><ondown>noop</ondown>
%(back)s                <control type="button" id="2">
                    <width>%(bw)d</width>
                    <include>DefaultSettingButton</include>
                </control>
                <control type="button" id="3">
                    <width>%(bw)d</width>
                    <include>DefaultSettingButton</include>
                </control>
                <control type="radiobutton" id="4">
                    <width>%(bw)d</width>
                    <label>Descending</label>
                    <include>DefaultSettingButton</include>
                </control>
            </control>
        </control>
''' % {'w': MENU_W, 'menu': MENU_ID, 'x': SAFE_X, 'bx': SAFE_X - 24, 'bw': MENU_W - SAFE_X - 40,
       'ty': VIEWS_TOP - 56, 'top': VIEWS_TOP, 'back': back}


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
    <!-- A video left playing behind the menus (Back from the player, a trailer's
         page, or Live TV left from the guide): stopped, as in Silo's apps, since
         these pages cover the screen and there's no way back to it. Kodi saves
         where it stopped; the TV guide keeps Live TV playing in its preview. -->
    <onload condition="Player.HasVideo">PlayerControl(Stop)</onload>
    <defaultcontrol always="true">50</defaultcontrol>
    <backgroundcolor>%(background)s</backgroundcolor>
    <views>50,51,52,53,54,%(hero_view)d,%(detail_view)d</views>
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
            <texture background="true" colordiffuse="%(backdrop)s" diffuse="silo/hero_mask.png">$VAR[SiloBrowseArt]</texture>
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
            <onleft condition="$EXP[SiloBrowseTitles]">%(menu)d</onleft>
            <onright condition="%(bar)s">%(jump)d</onright>%(click)s
            <visible>$EXP[SiloBrowseGrid]</visible>
            <itemlayout width="%(pw)d" height="%(ph)d">%(poster)s
            </itemlayout>
            <focusedlayout width="%(pw)d" height="%(ph)d">%(poster_focused)s
            </focusedlayout>
        </control>
%(jump_bar)s
%(title_views)s
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
%(side_menu)s
        <!-- A trailer from an info page: its cover (Includes_SiloFrame.xml). -->
        <include>SiloTrailerCover</include>
    </controls>
</window>
''' % {'backdrop': GRID_BACKDROP, 'wordmark': wordmark(SAFE_X, 56), 'background': BACKGROUND, 'x': SAFE_X, 'text': TEXT, 'dim': TEXT_DIM, 'lx': SAFE_X - 36,
       'views_top': VIEWS_TOP, 'views_h': 1080 - VIEWS_TOP, 'gx': SAFE_X - 6,
       'gw': 1920 - 2 * (SAFE_X - 6), 'pw': poster_item_w, 'ph': POSTER_ITEM_H,
       'ew': 1920 - 2 * (SAFE_X - 6), 'eh': EPISODE_ITEM_H,
       'row': pill_row(False, 50), 'row_h': ROW_H, 'row_focused': pill_row(True, 50),
       'poster': poster(False, 51), 'poster_focused': poster(True, 51),
       'episode': episode(False, 52), 'episode_focused': episode(True, 52),
       'bar': JUMP_BAR, 'jump': JUMP_ID, 'jump_bar': jump_bar(),
       'cw': CHIP_W + CHIP_GAP, 'ch': CHIP_H + CHIP_GAP, 'chip': chip(False, 54), 'chip_focused': chip(True, 54),
       'fw': FAN_W + FAN_GAP, 'fh': FAN_H + FAN_GAP, 'fan': fan_card(False, 53), 'fan_focused': fan_card(True, 53),
       'hero_view': HERO_VIEW, 'detail_view': DETAIL_VIEW, 'menu': MENU_ID, 'click': INFO_CLICK,
       'title_views': title_views(), 'side_menu': side_menu()}


VARIABLES = '''
    <!-- Silo Skyline browse (tools/build_browse.py) -->
    <expression name="SiloBrowseFans">%(fans)s</expression>
    <expression name="SiloBrowseChips">%(chips)s</expression>
    <expression name="SiloBrowseGrid">[%(grid)s] + !$EXP[SiloBrowseFans]</expression>
    <expression name="SiloBrowseEpisodes">%(episodes)s</expression>
    <!-- Films and shows: the views they have beside the poster grid (hero, list). -->
    <expression name="SiloBrowseTitles">[Container.Content(movies) | Container.Content(tvshows) | Container.Content(videos)] + !$EXP[SiloBrowseFans]</expression>
    <!-- The genre in a view's facts: SiloKodiConnect's first (kept in the library), else Kodi's. -->
    <variable name="SiloViewGenre">
        <value condition="!String.IsEmpty(ListItem.Art(silogenre))">$INFO[ListItem.Art(silogenre),  ·  ,]</value>
        <value>$INFO[ListItem.Genre,  ·  ,]</value>
    </variable>
    <variable name="SiloViewArt">
        <value condition="!String.IsEmpty(ListItem.Art(fanart))">$INFO[ListItem.Art(fanart)]</value>
        <value>$INFO[ListItem.Art(tvshow.fanart)]</value>
    </variable>
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
        <value condition="Integer.IsGreater(ListItem.Episode,0) + String.IsEmpty(Container.ShowTitle) + !String.IsEmpty(ListItem.TVShowTitle)">$INFO[ListItem.TVShowTitle] · S$INFO[ListItem.Season] E$INFO[ListItem.Episode]$INFO[ListItem.Title, · ,]</value>
        <value condition="Integer.IsGreater(ListItem.Episode,0)">S$INFO[ListItem.Season] E$INFO[ListItem.Episode]$INFO[ListItem.Title, · ,]</value>
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
        <!-- The hero view draws its own, stronger. -->
        <value condition="Control.IsVisible(%(hero_view)d)"></value>
%(jump_arts)s
        <value condition="!String.IsEmpty(ListItem.Art(fanart))">$INFO[ListItem.Art(fanart)]</value>
        <value condition="!String.IsEmpty(ListItem.Art(tvshow.fanart))">$INFO[ListItem.Art(tvshow.fanart)]</value>
        <value>$INFO[Container.Art(fanart)]</value>
    </variable>
    <!-- end Silo Skyline browse -->
''' % {'grid': GRID, 'episodes': EPISODES, 'jump': JUMP_ID, 'fans': FANS, 'chips': CHIPS, 'hero_view': HERO_VIEW,
       'jump_arts': ''.join('        <value condition="Control.HasFocus(%d) + Control.IsVisible(%d)">'
                            '$INFO[Container(%d).ListItem.Art(fanart)]</value>\n' % (JUMP_ID, view, view)
                            for view in TITLE_VIEWS)}


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
