"""Write xml/Custom_1190_SiloSearch.xml: a Silo-style search screen.

    python3 tools/build_search.py

The menu bar's Search opens it. It asks for the words when it has none
(Kodi's keyboard, kept in Skin.String(silo.search), so it reopens on the last
search and doesn't ask again when playback ends), shows them in a pill that asks
again when selected, and lists the matching films and shows as Home's poster
cards, filtered from Kodi's library by title: no add-on is involved. Selecting
a title opens its detail page.
"""
import json
import os
import sys
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_home import wordmark, BACKGROUND, POSTER, ROOT, SAFE_X, TEXT, TEXT_DIM, card_layout  # noqa: E402

WINDOW_ID = 1190
QUERY = 'Skin.String(silo.search)'
LOADING = 'silo.search.loading'  # on Home, for a moment after new words
PILL_ID = 100
# (list id, row title, library path, smart-filter type)
# The third row is Silo's own search for titles to request (SiloKodiConnect),
# shown only when the add-on is there and found some.
ROWS = [(201, 'Movies', 'videodb://movies/titles/', 'movies'),
        (202, 'Shows', 'videodb://tvshows/titles/', 'tvshows'),
        (203, 'Request', 'plugin://plugin.video.silokodiconnect/?mode=requests', None)]
# Requests' "Search to request" sets Window(Home).Property(silo.search.mode)
# to requests: only Silo's row shows (the menu bar's Search clears it).
REQUEST_ONLY = 'String.IsEqual(Window(Home).Property(silo.search.mode),requests)'
LIBRARY_LISTS = (201, 202)
ROWS_TOP = 236
# Two rows fit below the pill; the third scrolls into view.
ROW_H = (1080 - ROWS_TOP) // 2


def search_path(path, kind):
    """The library folder filtered to titles containing the search words. The
    filter is URL-encoded around a marker that becomes the words."""
    if kind is None:
        return path + '&amp;search=$INFO[%s]&amp;refresh=$INFO[Window(Home).Property(silokodi.library_updated)]' % QUERY
    marker = 'SILOQUERY'
    rules = {'type': kind, 'order': {'method': 'sorttitle', 'direction': 'ascending'},
             'rules': {'and': [{'field': 'title', 'operator': 'contains', 'value': [marker]}]}}
    encoded = quote(json.dumps(rules, separators=(',', ':')), safe='')
    return path + '?xsp=' + encoded.replace(marker, '$INFO[%s]' % QUERY)


def has_items(list_id):
    has = 'Integer.IsGreater(Container(%d).NumItems,0)' % list_id
    return '[!%s + %s]' % (REQUEST_ONLY, has) if list_id in LIBRARY_LISTS else has


def shown(list_id, condition):
    """A row's visibility: a library row never shows in request-only mode."""
    return '!%s + [%s]' % (REQUEST_ONLY, condition) if list_id in LIBRARY_LISTS else condition


def row(index, list_id, title, path, kind):
    others = [r[0] for r in ROWS]
    above = others[:index][::-1]
    below = others[index + 1:]
    moves = ''
    for action, targets in (('onup', above), ('ondown', below)):
        skipped = []
        for target in targets:
            condition = ' + '.join([has_items(target)] + ['!' + has_items(k) for k in skipped])
            moves += '\n                    <%s condition="%s">SetFocus(%d)</%s>' % (action, condition, target, action)
            skipped.append(target)
    moves += '\n                    <onup%s>SetFocus(%d)</onup>' % (
        ' condition="%s"' % ' + '.join('!' + has_items(k) for k in above) if above else '', PILL_ID)
    item_w = POSTER['width'] + POSTER['gap']
    item_h = POSTER['height'] + 12 + 76
    return '''
            <control type="group">
                <height>%(row_h)d</height>
                <visible>%(group_shown)s</visible>
                <control type="label">
                    <left>%(x)d</left>
                    <width>1500</width><height>46</height>
                    <font>silo_row</font>
                    <textcolor>%(text)s</textcolor>
                    <label>%(title)s$INFO[Container(%(id)d).NumItems,  ·  ,]</label>
                    <visible>%(title_shown)s</visible>
                </control>
                <control type="list" id="%(id)d">
                    <!-- The list's own condition lets Kodi load it while it is hidden:
                         it doesn't process a list inside a hidden group. -->
                    <visible>%(group_shown)s</visible>
                    <left>%(lx)d</left><top>56</top>
                    <width>%(lw)d</width><height>%(item_h)d</height>
                    <orientation>horizontal</orientation>
                    <scrolltime tween="cubic" easing="out">280</scrolltime>
                    <!-- Through SiloKodiConnect, when it is there, so the page has
                         Silo's details and More Like This, as from Home. -->
                    <onclick condition="!String.IsEmpty(ListItem.Property(silo.request.tmdb)) + System.AddonIsEnabled(plugin.video.silokodiconnect)">RunPlugin(plugin://plugin.video.silokodiconnect/?mode=request_info&amp;type=$INFO[ListItem.Property(silo.request.type)]&amp;tmdb=$INFO[ListItem.Property(silo.request.tmdb)])</onclick>
                    <onclick condition="!String.IsEmpty(ListItem.Property(silo.request.tmdb)) + !System.AddonIsEnabled(plugin.video.silokodiconnect)">Action(Info)</onclick>
                    <onclick condition="String.IsEmpty(ListItem.Property(silo.request.tmdb)) + System.AddonIsEnabled(plugin.video.silokodiconnect)">RunPlugin(plugin://plugin.video.silokodiconnect/?mode=info&amp;type=$INFO[ListItem.DBType]&amp;dbid=$INFO[ListItem.DBID])</onclick>
                    <onclick condition="String.IsEmpty(ListItem.Property(silo.request.tmdb)) + !System.AddonIsEnabled(plugin.video.silokodiconnect)">Action(Info)</onclick>%(moves)s
                    <content target="videos">%(path)s</content>
                    <itemlayout width="%(item_w)d" height="%(item_h)d">%(normal)s
                    </itemlayout>
                    <focusedlayout width="%(item_w)d" height="%(item_h)d">%(focused)s
                    </focusedlayout>
                </control>
            </control>''' % {'row_h': ROW_H, 'has': has_items(list_id), 'id': list_id, 'x': SAFE_X, 'text': TEXT,
                             'title': title, 'lx': SAFE_X - 6, 'lw': 1920 - SAFE_X + 6, 'item_h': item_h,
                             'item_w': item_w, 'moves': moves, 'path': search_path(path, kind),
                             'normal': card_layout(POSTER, False), 'focused': card_layout(POSTER, True, list_id),
                             'loading': LOADING,
                             'group_shown': shown(list_id, '%s | Container(%d).IsUpdating | String.IsEqual(Window(Home).Property(%s),1)'
                                                  % (has_items(list_id), list_id, LOADING)),
                             'title_shown': shown(list_id, '%s | Container(%d).IsUpdating' % (has_items(list_id), list_id))}


def build():
    lists = [r[0] for r in ROWS]
    pill_down = ''
    for index, target in enumerate(lists):
        condition = ' + '.join([has_items(target)] + ['!' + has_items(k) for k in lists[:index]])
        pill_down += '\n                <ondown condition="%s">SetFocus(%d)</ondown>' % (condition, target)
    nothing = ' + '.join('!%s + !Container(%d).IsUpdating' % (has_items(k), k) for k in lists) \
        + ' + !String.IsEqual(Window(Home).Property(%s),1)' % LOADING
    return '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by tools/build_search.py: edit that, not this. -->
<window id="%(window)d">
    <!-- Back from a trailer started from an info page (Kodi leaves it playing): stop it, which reopens the page. -->
    <onload condition="Player.HasVideo + !String.IsEmpty(Window(Home).Property(silokodi.trailer_playing))">PlayerControl(Stop)</onload>
    <defaultcontrol always="true">%(pill)d</defaultcontrol>
    <backgroundcolor>%(background)s</backgroundcolor>
    <onload condition="String.IsEmpty(%(query)s)">Skin.SetString(silo.search)</onload>
    <controls>
        <control type="image">
            <left>0</left><top>0</top><width>1920</width><height>1080</height>
            <texture colordiffuse="%(background)s">colors/white.png</texture>
        </control>
        <!-- The focused title's artwork, faint in the top right. -->
        <control type="image">
            <!-- 16:9 like the artwork, so Kodi draws it whole: cropped to fit,
                 the fade mask no longer lines up and the left edge shows. -->
            <left>576</left><top>0</top>
            <width>1344</width><height>756</height>
            <aspectratio>stretch</aspectratio>
            <fadetime>240</fadetime>
            <texture background="true" colordiffuse="59FFFFFF" diffuse="silo/hero_mask.png">$INFO[Container.ListItem.Art(fanart)]</texture>
        </control>
        <!-- The shared frame (tools/build_frame.py). -->
        <include content="SiloFrame">
            <param name="title">$VAR[SiloSearchTitle]</param>
        </include>

        <!-- The search words, in a pill that asks for them again. -->
        <control type="group">
            <left>%(x)d</left><top>158</top>
            <control type="button" id="%(pill)d">
                <width>900</width><height>64</height>
                <label />
                <texturefocus border="30" colordiffuse="%(text)s">silo/pill.png</texturefocus>
                <texturenofocus border="30" colordiffuse="26FFFFFF">silo/pill.png</texturenofocus>
                <onclick>Skin.SetString(silo.search)</onclick>
                <!-- Kodi never loads a hidden list whose path changed: a row with
                     no titles for the last words would stay hidden and empty, so
                     every row shows while the new words load. -->
                <onclick>SetProperty(%(loading)s,1,home)</onclick>
                <onclick>AlarmClock(silosearch,ClearProperty(%(loading)s,home),00:04,silent)</onclick>%(pill_down)s
            </control>
            <control type="image">
                <left>24</left><top>16</top>
                <width>32</width><height>32</height>
                <texture colordiffuse="FF000000">icons/search.png</texture>
                <visible>Control.HasFocus(%(pill)d)</visible>
            </control>
            <control type="image">
                <left>24</left><top>16</top>
                <width>32</width><height>32</height>
                <texture colordiffuse="%(dim)s">icons/search.png</texture>
                <visible>!Control.HasFocus(%(pill)d)</visible>
            </control>
            <control type="label">
                <left>76</left><width>800</width><height>64</height>
                <aligny>center</aligny>
                <font>silo_meta</font>
                <textcolor>FF000000</textcolor>
                <label>$VAR[SiloSearchPill]</label>
                <visible>Control.HasFocus(%(pill)d)</visible>
            </control>
            <control type="label">
                <left>76</left><width>800</width><height>64</height>
                <aligny>center</aligny>
                <font>silo_meta</font>
                <textcolor>%(text)s</textcolor>
                <label>$VAR[SiloSearchPill]</label>
                <visible>!Control.HasFocus(%(pill)d)</visible>
            </control>
        </control>

        <control type="label">
            <left>%(x)d</left><top>%(rows_top)d</top>
            <width>1500</width><height>46</height>
            <font>silo_row</font>
            <textcolor>%(dim)s</textcolor>
            <label>No titles match "$INFO[%(query)s]"</label>
            <visible>!String.IsEmpty(%(query)s) + %(nothing)s</visible>
        </control>
        <control type="grouplist">
            <top>%(rows_top)d</top>
            <width>1920</width><height>%(rows_h)d</height>
            <orientation>vertical</orientation>
            <itemgap>0</itemgap>
            <scrolltime tween="cubic" easing="out">300</scrolltime>
            <visible>!String.IsEmpty(%(query)s)</visible>%(rows)s
        </control>
        <!-- A trailer from an info page: its cover (Includes_SiloFrame.xml). -->
        <include>SiloTrailerCover</include>
    </controls>
</window>
''' % {'wordmark': wordmark(SAFE_X, 56), 'window': WINDOW_ID, 'pill': PILL_ID, 'background': BACKGROUND, 'x': SAFE_X, 'text': TEXT, 'dim': TEXT_DIM,
       'pill_down': pill_down, 'rows_top': ROWS_TOP, 'rows_h': 1080 - ROWS_TOP, 'query': QUERY,
       'nothing': nothing, 'rows': ''.join(row(i, *r) for i, r in enumerate(ROWS)), 'loading': LOADING}


VARIABLES = '''
    <!-- Silo Skyline search (tools/build_search.py) -->
    <variable name="SiloSearchTitle">
        <value condition="%(request_only)s">Search to request</value>
        <value>Search</value>
    </variable>
    <variable name="SiloSearchPill">
        <value condition="String.IsEmpty(%(query)s) + %(request_only)s">Find a film or show to request</value>
        <value condition="String.IsEmpty(%(query)s)">Search films and shows</value>
        <value>$INFO[%(query)s]</value>
    </variable>
    <!-- end Silo Skyline search -->
''' % {'query': QUERY, 'request_only': REQUEST_ONLY}


def add_variables():
    path = os.path.join(ROOT, 'xml', 'Variables.xml')
    text = open(path, encoding='utf-8').read()
    start, end = '    <!-- Silo Skyline search (tools/build_search.py) -->', '    <!-- end Silo Skyline search -->\n'
    if start in text:
        text = text[:text.index(start) - 1] + text[text.index(end) + len(end):]
    text = text.replace('</includes>', VARIABLES + '</includes>')
    open(path, 'w', encoding='utf-8').write(text)


if __name__ == '__main__':
    with open(os.path.join(ROOT, 'xml', 'Custom_%d_SiloSearch.xml' % WINDOW_ID), 'w', encoding='utf-8') as handle:
        handle.write(build())
    add_variables()
    print('Wrote xml/Custom_%d_SiloSearch.xml and its variables in xml/Variables.xml' % WINDOW_ID)
