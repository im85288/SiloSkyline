"""Write xml/MyVideoNav.xml: Kodi's video browsing window in Silo's style.

    python3 tools/build_browse.py

Browse on a show and the menu behind the profile avatar open this window. It
gets a header (the folder's name and how many items it holds) and one view
per kind of content, each shown only for its content so Kodi always lands on
the right one: a poster grid for films, shows, sets and seasons (51), episode
stills with their details (52), and a list of pills for everything else, such
as an add-on's menu or a folder (50). Estuary's side menu of sorting and view
options is gone, as Silo has none.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_home import BACKGROUND, ROOT, SAFE_X, TEXT, TEXT_DIM, TITLE_DIM  # noqa: E402

GRID = 'Container.Content(movies) | Container.Content(tvshows) | Container.Content(sets) | Container.Content(seasons)'
EPISODES = 'Container.Content(episodes)'
VIEWS_TOP = 200

# Poster grid: Silo's 2:3 cards, seven to a row.
POSTER_W, POSTER_H, POSTER_GAP = 200, 300, 36
POSTER_ITEM_H = POSTER_H + 12 + 76 + 24
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


def pill_row(focused, view_id):
    pill = '''
                    <control type="image">
                        <left>0</left><top>6</top>
                        <width>%(w)d</width><height>64</height>
                        <texture border="30" colordiffuse="%(text)s">silo/pill.png</texture>
                        <visible>Control.HasFocus(%(id)d)</visible>
                    </control>''' % {'w': 1100, 'text': TEXT, 'id': view_id} if focused else ''
    labels = []
    for color, visible in ((('FF000000', 'Control.HasFocus(%d)' % view_id), (TEXT, '!Control.HasFocus(%d)' % view_id))
                           if focused else ((TEXT, ''),)):
        labels.append('''
                    <control type="label">
                        <left>36</left><top>6</top>
                        <width>800</width><height>64</height>
                        <aligny>center</aligny>
                        <font>silo_meta</font>
                        <textcolor>%(color)s</textcolor>
                        <label>$INFO[ListItem.Label]</label>%(visible)s
                    </control>
                    <control type="label">
                        <left>840</left><top>6</top>
                        <width>224</width><height>64</height>
                        <align>right</align><aligny>center</aligny>
                        <font>silo_detail</font>
                        <textcolor>%(color)s</textcolor>
                        <label>$INFO[ListItem.Label2]</label>%(visible)s
                    </control>''' % {'color': color, 'visible': '\n                        <visible>%s</visible>' % visible
                                     if visible else ''})
    return pill + ''.join(labels)


def build():
    poster_item_w = POSTER_W + POSTER_GAP
    return '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by tools/build_browse.py: edit that, not this. -->
<window>
    <defaultcontrol always="true">50</defaultcontrol>
    <backgroundcolor>%(background)s</backgroundcolor>
    <views>50,51,52</views>
    <controls>
        <control type="image">
            <left>0</left><top>0</top><width>1920</width><height>1080</height>
            <texture colordiffuse="%(background)s">colors/white.png</texture>
        </control>
        <!-- The focused title's artwork, faint in the top right, as on Silo's pages. -->
        <control type="image">
            <left>690</left><top>0</top>
            <width>1230</width><height>756</height>
            <aspectratio align="right" aligny="top">scale</aspectratio>
            <fadetime>240</fadetime>
            <colordiffuse>59FFFFFF</colordiffuse>
            <texture background="true" diffuse="silo/hero_mask.png">$VAR[SiloBrowseArt]</texture>
        </control>

        <control type="label">
            <left>%(x)d</left><top>56</top>
            <width>300</width><height>64</height>
            <aligny>center</aligny>
            <font>silo_wordmark</font>
            <textcolor>%(text)s</textcolor>
            <label>Silo</label>
        </control>
        <control type="grouplist">
            <left>%(x)d</left><top>124</top>
            <width>1600</width><height>56</height>
            <orientation>horizontal</orientation>
            <itemgap>20</itemgap>
            <control type="label">
                <width>auto</width><height>56</height>
                <aligny>center</aligny>
                <font>silo_row</font>
                <textcolor>%(text)s</textcolor>
                <label>$VAR[SiloBrowseTitle]</label>
            </control>
            <control type="label">
                <width>auto</width><height>56</height>
                <aligny>center</aligny>
                <font>silo_meta</font>
                <textcolor>%(dim)s</textcolor>
                <label>$INFO[Container.NumItems]</label>
                <visible>Integer.IsGreater(Container.NumItems,0) + [$EXP[SiloBrowseGrid] | $EXP[SiloBrowseEpisodes]]</visible>
            </control>
        </control>

        <!-- Everything else: a list of pills. -->
        <control type="list" id="50">
            <left>%(lx)d</left><top>%(views_top)d</top>
            <width>1110</width><height>%(views_h)d</height>
            <orientation>vertical</orientation>
            <scrolltime tween="cubic" easing="out">240</scrolltime>
            <viewtype label="List">list</viewtype>
            <visible>!$EXP[SiloBrowseGrid] + !$EXP[SiloBrowseEpisodes]</visible>
            <itemlayout width="1110" height="76">%(row)s
            </itemlayout>
            <focusedlayout width="1110" height="76">%(row_focused)s
            </focusedlayout>
        </control>

        <!-- Films, shows, sets and seasons: a poster grid. -->
        <control type="panel" id="51">
            <left>%(gx)d</left><top>%(views_top)d</top>
            <width>%(gw)d</width><height>%(views_h)d</height>
            <orientation>vertical</orientation>
            <scrolltime tween="cubic" easing="out">280</scrolltime>
            <viewtype label="Posters">poster</viewtype>
            <visible>$EXP[SiloBrowseGrid]</visible>
            <itemlayout width="%(pw)d" height="%(ph)d">%(poster)s
            </itemlayout>
            <focusedlayout width="%(pw)d" height="%(ph)d">%(poster_focused)s
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
    </controls>
</window>
''' % {'background': BACKGROUND, 'x': SAFE_X, 'text': TEXT, 'dim': TEXT_DIM, 'lx': SAFE_X - 36,
       'views_top': VIEWS_TOP, 'views_h': 1080 - VIEWS_TOP, 'gx': SAFE_X - 6,
       'gw': 1920 - 2 * (SAFE_X - 6), 'pw': poster_item_w, 'ph': POSTER_ITEM_H,
       'ew': 1920 - 2 * (SAFE_X - 6), 'eh': EPISODE_ITEM_H,
       'row': pill_row(False, 50), 'row_focused': pill_row(True, 50),
       'poster': poster(False, 51), 'poster_focused': poster(True, 51),
       'episode': episode(False, 52), 'episode_focused': episode(True, 52)}


VARIABLES = '''
    <!-- Silo Skyline browse (tools/build_browse.py) -->
    <expression name="SiloBrowseGrid">%(grid)s</expression>
    <expression name="SiloBrowseEpisodes">%(episodes)s</expression>
    <variable name="SiloBrowseTitle">
        <value condition="String.IsEqual(Container.FolderPath,plugin://plugin.video.silokodiconnect/)">SiloKodiConnect</value>
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
        <value condition="Container.Content(seasons) + Integer.IsGreater(ListItem.Property(TotalEpisodes),0)">$INFO[ListItem.Property(TotalEpisodes),, episodes]</value>
        <value condition="Container.Content(tvshows) + Integer.IsGreater(ListItem.Property(TotalSeasons),0)">$INFO[ListItem.Year]$INFO[ListItem.Property(TotalSeasons), · , seasons]</value>
        <value>$INFO[ListItem.Year]</value>
    </variable>
    <variable name="SiloBrowseEpisodeTitle">
        <value condition="Integer.IsGreater(ListItem.Episode,0)">S$INFO[ListItem.Season] · E$INFO[ListItem.Episode]$INFO[ListItem.Title, · ,]</value>
        <value>$INFO[ListItem.Label]</value>
    </variable>
    <variable name="SiloBrowseArt">
        <value condition="!String.IsEmpty(ListItem.Art(fanart))">$INFO[ListItem.Art(fanart)]</value>
        <value condition="!String.IsEmpty(ListItem.Art(tvshow.fanart))">$INFO[ListItem.Art(tvshow.fanart)]</value>
        <value>$INFO[Container.Art(fanart)]</value>
    </variable>
    <!-- end Silo Skyline browse -->
''' % {'grid': GRID, 'episodes': EPISODES}


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
