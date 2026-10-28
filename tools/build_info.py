"""Write xml/DialogVideoInfo.xml: the Silo TV apps' detail page for Kodi.

    python3 tools/build_info.py

Silo's detail page (Skyline): the title's artwork crisp in the top right,
fading into the page; top left the clear logo, a facts line, a three-line
synopsis, a credit line, quality badges and an action row (a Play/Resume
pill, then round buttons); the cast below.

Kodi drives this window through fixed control ids, kept here: 8 Play (Browse
for a show), 11 Trailer, 14 Versions, 50 the cast list Kodi fills. Text comes
from Kodi's own info labels, which the info window always has.
"""
import json
import os
import re
import sys
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_home import focus_sheen, focus_zoom, watched_disc, BACKGROUND, POSTER, ROOT, SAFE_X, TEXT, TEXT_DIM, card_layout  # noqa: E402

# Silo's detail hero: 100 px down (tvOS 100pt on a 1080pt canvas).
TOP = 100


def badge(label, condition, font='silo_badge', height=36):
    return '''
                <control type="button">
                    <width>auto</width><height>%(h)d</height>
                    <label>%(label)s</label>
                    <font>%(font)s</font>
                    <textoffsetx>12</textoffsetx>
                    <aligny>center</aligny>
                    <enable>false</enable>
                    <disabledcolor>%(text)s</disabledcolor>
                    <!-- Outlined, as on Silo's Apple TV app. -->
                    <texturenofocus border="8" colordiffuse="B3FFFFFF">silo/badge_outline.png</texturenofocus>
                    <texturefocus border="8" colordiffuse="B3FFFFFF">silo/badge_outline.png</texturefocus>
                    <visible>%(condition)s</visible>
                </control>''' % {'h': height, 'label': label, 'font': font, 'text': TEXT, 'condition': condition}


# The round buttons in the row's order, with their names: the focused one
# opens into a white pill with its name, as in Silo's Apple TV app.
ROUND_BUTTONS = [(304, 'Start over'), (302, 'Previous'), (11, 'Trailer'), (351, 'Trailer'), (352, 'Watchlist'),
                 (14, 'Versions'), (303, 'More')]


MORE_WINDOW, MORE_LIST = 1194, 3810
MORE = 'Window(Home).Property(silo.more.%s)'
MORE_OPEN = 'Window.IsActive(%d)' % MORE_WINDOW
# A title watched (a show: every episode), or as the More menu just set it.
WATCHED = ('[String.IsEqual(Window(movieinformation).Property(silo.marked),watched) | '
           '[String.IsEmpty(Window(movieinformation).Property(silo.marked)) + [Integer.IsGreater(ListItem.PlayCount,0) | '
           '[String.IsEqual(ListItem.DBType,tvshow) + Integer.IsGreater(ListItem.Property(TotalEpisodes),0) + '
           'Integer.IsEqual(ListItem.Property(UnWatchedEpisodes),0)]]]]')


def more_opener():
    """More's onclick (after its first): hand the menu the title, whether it's
    watched and which round buttons come before More (the menu is its own
    window, so Back closes only it), then open it."""
    steps = ['SetProperty(silo.more.type,$INFO[ListItem.DBType],home)',
             'SetProperty(silo.more.dbid,$INFO[ListItem.DBID],home)',
             'ClearProperty(silo.more.watched,home)',
             ('SetProperty(silo.more.watched,1,home)', WATCHED)]
    for other, _ in ROUND_BUTTONS[:-1]:
        steps += ['ClearProperty(silo.more.b%d,home)' % other,
                  ('SetProperty(silo.more.b%d,1,home)' % other, 'Control.IsVisible(%d)' % (other + 1000))]
    steps.append('ActivateWindow(%d)' % MORE_WINDOW)
    out = 'noop</onclick>'
    for step in steps:
        action, condition = step if isinstance(step, tuple) else (step, None)
        out += '\n                    <onclick%s>%s</onclick>' % (
            ' condition="%s"' % condition if condition else '', action)
    # round_button closes the last <onclick>.
    return out[:-len('</onclick>')].replace('noop</onclick>\n                    <onclick>', '', 1)


def more_menu():
    """More's menu, as Silo's Apple TV app draws its menus: a dark glass panel
    under the button with a small heading, the focused row a white bar. A
    dialog of its own (Back closes it, not the info page), hung under More
    wherever More is: Play is 340 wide and each round button before More 80
    (64 and the row's gap)."""
    def row(control_id, label, action, visible):
        return '''
                <control type="button" id="%(id)d">
                    <width>536</width><height>64</height>
                    <label>%(label)s</label>
                    <font>silo_meta</font>
                    <textoffsetx>24</textoffsetx>
                    <aligny>center</aligny>
                    <textcolor>%(text)s</textcolor>
                    <focusedcolor>FF000000</focusedcolor>
                    <texturefocus border="20" colordiffuse="%(text)s">silo/card_landscape_mask.png</texturefocus>
                    <texturenofocus />
                    <onclick>RunPlugin(plugin://plugin.video.silokodiconnect/?mode=mark&amp;type=$INFO[%(type)s]&amp;dbid=$INFO[%(dbid)s]&amp;action=%(action)s)</onclick>
                    <onclick>Dialog.Close(%(window)d)</onclick>
                    <onup>Dialog.Close(%(window)d)</onup>
                    <visible>%(visible)s</visible>
                </control>''' % {'id': control_id, 'label': label, 'text': TEXT, 'action': action, 'visible': visible,
                                  'type': MORE % 'type', 'dbid': MORE % 'dbid', 'window': MORE_WINDOW}
    slides = ''.join('\n        <animation effect="slide" end="80,0" time="0" condition="String.IsEqual(%s,1)">'
                     'Conditional</animation>' % (MORE % ('b%d' % other)) for other, _ in ROUND_BUTTONS[:-1])
    watched = 'String.IsEqual(%s,1)' % (MORE % 'watched')
    return '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by tools/build_info.py: the info page's More menu. -->
<window id="%(window)d" type="dialog">
    <defaultcontrol always="true">%(list)d</defaultcontrol>
    <controls>
    <control type="group">
        <left>%(x)d</left><top>%(y)d</top>
        <animation effect="fade" start="0" end="100" time="160">WindowOpen</animation>
        <animation effect="slide" start="0,-12" end="0,0" time="160" tween="sine" easing="out">WindowOpen</animation>
        <animation effect="fade" start="100" end="0" time="120">WindowClose</animation>%(slides)s
        <control type="image">
            <width>560</width><height>140</height>
            <texture border="28">silo/menu_panel.png</texture>
        </control>
        <control type="label">
            <left>36</left><top>14</top><width>480</width><height>32</height>
            <font>silo_badge</font>
            <textcolor>80EDEDED</textcolor>
            <label>[UPPERCASE]$VAR[SiloMoreHeading][/UPPERCASE]</label>
        </control>
        <control type="grouplist" id="%(list)d">
            <left>12</left><top>58</top><width>536</width><height>64</height>
            <orientation>vertical</orientation>%(rows)s
        </control>
    </control>
    </controls>
</window>
''' % {'x': SAFE_X + 340 + 16, 'y': TOP + 470 + 64 + 14, 'slides': slides, 'list': MORE_LIST, 'window': MORE_WINDOW,
       'rows': row(MORE_LIST + 1, '$VAR[SiloMoreWatched]', 'watched', '!' + watched) +
       row(MORE_LIST + 2, '$VAR[SiloMoreUnwatched]', 'unwatched', watched)}


def opened_by(label):
    """How much wider a round button is open: its name in silo_tab (about 16 px
    a character) and the pill's end."""
    return 16 * len(label) + 30


def round_button(control_id, icon, visible, onclick=''):
    """A round icon at rest; with focus, a white pill with its name. The
    button stays round and in place (Kodi's grouplist can't resize it): the
    pill reaches past it, and the buttons after it slide over to make room."""
    action = '\n                    <onclick>%s</onclick>' % onclick if onclick else ''
    lit = 'Control.HasFocus(%d)' % control_id
    if control_id == 303:
        lit = '[%s | %s]' % (lit, MORE_OPEN)
    label = dict(ROUND_BUTTONS)[control_id]
    earlier = [(other, opened_by(name)) for other, name in ROUND_BUTTONS[:[i for i, _ in ROUND_BUTTONS].index(control_id)]]
    slides = ''.join('\n                    <animation effect="slide" end="%d,0" time="180" tween="sine" easing="out" '
                     'condition="Control.HasFocus(%d)">Conditional</animation>' % (width, other) for other, width in earlier)
    return '''
                <control type="group" id="%(group)d">
                    <width>64</width><height>64</height>
                    <visible>%(visible)s</visible>%(slides)s
                    <control type="button" id="%(id)d">
                        <width>64</width><height>64</height>
                        <label />
                        <texturefocus />
                        <texturenofocus border="30" colordiffuse="33FFFFFF">silo/pill.png</texturenofocus>%(action)s
                    </control>
                    <control type="group">
                        <visible>%(lit)s</visible>
                        <animation effect="zoom" start="40,100" end="100,100" center="0,32" time="180" tween="sine" easing="out">Visible</animation>
                        <control type="image">
                            <width>%(open_w)d</width><height>64</height>
                            <texture border="30" colordiffuse="%(text)s">silo/pill.png</texture>
                        </control>
                        <control type="label">
                            <left>62</left><width>%(label_w)d</width><height>64</height>
                            <aligny>center</aligny>
                            <font>silo_tab</font>
                            <textcolor>FF000000</textcolor>
                            <label>%(label)s</label>
                        </control>
                    </control>
                    <control type="image">
                        <left>16</left><top>16</top>
                        <width>32</width><height>32</height>
                        <texture colordiffuse="FF000000">%(icon)s</texture>
                        <visible>%(lit)s</visible>
                    </control>
                    <control type="image">
                        <left>16</left><top>16</top>
                        <width>32</width><height>32</height>
                        <texture colordiffuse="%(text)s">%(icon)s</texture>
                        <visible>!%(lit)s</visible>
                    </control>
                </control>''' % {'id': control_id, 'icon': icon, 'visible': visible, 'text': TEXT, 'action': action,
                                  'group': control_id + 1000, 'lit': lit, 'label': label, 'slides': slides,
                                  'open_w': 64 + opened_by(label), 'label_w': opened_by(label) - 4}


def build():
    episode = 'String.IsEqual(ListItem.DBType,episode)'
    has_logo = '[!String.IsEmpty(ListItem.Art(clearlogo)) | !String.IsEmpty(ListItem.Art(tvshow.clearlogo))]'
    # Silo's own badges from the widget item, else Kodi's stream details.
    silo_badges = '!String.IsEmpty(ListItem.Property(silo.badge1))'
    badges = ''.join([badge('$INFO[ListItem.Property(silo.badge%d)]' % n,
                            '!String.IsEmpty(ListItem.Property(silo.badge%d))' % n) for n in (1, 2, 3)] + [
        badge('$INFO[ListItem.VideoResolution]$VAR[SiloDetailResolutionSuffix]',
              '!%s + !String.IsEmpty(ListItem.VideoResolution)' % silo_badges),
        badge('$VAR[SiloDetailHdr]', '!%s + !String.IsEmpty(ListItem.HdrType)' % silo_badges),
        badge('$VAR[SiloDetailAudio]', '!%s + !String.IsEmpty(ListItem.AudioCodec)' % silo_badges),
    ])
    return '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by tools/build_info.py: edit that, not this. -->
<window>
    <defaultcontrol always="true">308</defaultcontrol>
    <onload condition="%(show)s">SetFocus(300)</onload>
    <onload condition="%(request)s">SetFocus(301)</onload>
    <onload condition="String.IsEqual(Window(home).Property(silo.from_rail),1) + Integer.IsGreater(Container(70).NumItems,0)">SetFocus(70)</onload>
    <onload condition="String.IsEqual(Window(home).Property(silo.from_rail),1)">SetFocus(5000)</onload>
    <onload>ClearProperty(silo.from_rail,home)</onload>
    <onload>SetProperty(silo.tint,$INFO[ListItem.Property(silo.tint)],movieinformation)</onload>
    <onload>SetProperty(silo.content_id,$INFO[ListItem.Property(silo.content_id)],movieinformation)</onload>
    <!-- For Trailers & More, where ListItem is the video: the page's own title and art. -->
    <onload>SetProperty(silo.page_type,$INFO[ListItem.DBType],movieinformation)</onload>
    <onload>SetProperty(silo.page_dbid,$INFO[ListItem.DBID],movieinformation)</onload>
    <onload>SetProperty(silo.page_fanart,$INFO[ListItem.Art(fanart)],movieinformation)</onload>
    <onload>SetProperty(silo.episode_id,$INFO[ListItem.DBID],movieinformation)</onload>
    <onload>SetProperty(silo.episode_number,$INFO[ListItem.Episode],movieinformation)</onload>
    <onload>SetProperty(silo.episode_season,$INFO[ListItem.Season],movieinformation)</onload>
    <onunload>ClearProperty(silo.jump,movieinformation)</onunload>
    <!-- Back from its trailer: the cover under the page can go. -->
    <onload>ClearProperty(silokodi.trailer_playing,home)</onload>
    <onload>ClearProperty(silokodi.trailer_return,home)</onload>
    <backgroundcolor>%(background)s</backgroundcolor>
    <controls>
        <control type="image">
            <left>0</left><top>0</top><width>1920</width><height>1080</height>
            <texture colordiffuse="%(background)s">colors/white.png</texture>
        </control>
        <!-- Silo's ambient wash in the title's colour (widget items carry it). -->
        <control type="image">
            <left>0</left><top>0</top><width>1920</width><height>1080</height>
            <!-- The page's own copy: with another dialog over it (More's menu), ListItem
                 is that dialog's, and an empty colour would draw the wash white. -->
            <texture colordiffuse="$INFO[Window(movieinformation).Property(silo.tint)]">silo/tint_wash.png</texture>
            <visible>!String.IsEmpty(Window(movieinformation).Property(silo.tint))</visible>
        </control>
        <control type="image">
            <!-- 16:9 like the artwork, so Kodi draws it whole: cropped to fit,
                 the fade mask no longer lines up and the left edge shows. -->
            <left>576</left><top>0</top>
            <width>1344</width><height>756</height>
            <aspectratio>stretch</aspectratio>
            <fadetime>240</fadetime>
            <texture background="true" diffuse="silo/hero_mask.png">$VAR[SiloDetailArt]</texture>
        </control>

        <control type="group">
            <left>%(x)d</left><top>%(top)d</top>
            <!-- Logo, or the title in text. -->
            <control type="image">
                <width>820</width><height>160</height>
                <aspectratio align="left" aligny="bottom">keep</aspectratio>
                <texture background="true">$VAR[SiloDetailLogo]</texture>
                <visible>%(has_logo)s</visible>
            </control>
            <control type="label">
                <width>1100</width><height>160</height>
                <aligny>bottom</aligny>
                <font>silo_title</font>
                <textcolor>%(text)s</textcolor>
                <label>$VAR[SiloDetailTitle]</label>
                <visible>!%(has_logo)s</visible>
            </control>
            <!-- Age rating, then the facts. -->
            <control type="grouplist">
                <top>180</top>
                <width>1200</width><height>40</height>
                <orientation>horizontal</orientation>
                <itemgap>0</itemgap>
                <usecontrolcoords>true</usecontrolcoords>%(mpaa)s
                <control type="image">
                    <width>14</width><height>40</height>
                    <texture />
                    <visible>[!String.IsEmpty(ListItem.Mpaa) | !String.IsEmpty(ListItem.Property(silo.mpaa))]</visible>
                </control>
                <control type="label">
                    <width>auto</width><height>40</height>
                    <aligny>center</aligny>
                    <font>silo_meta</font>
                    <textcolor>%(text)s</textcolor>
                    <label>$VAR[SiloDetailFacts]</label>
                </control>
                <!-- The rating sources' marks are images (IMDb in its colours, TMDB as
                     Silo's Apple TV app shows it), so the line is in parts around them. -->
                <control type="label">
                    <width>auto</width><height>40</height>
                    <aligny>center</aligny>
                    <font>silo_meta</font>
                    <textcolor>%(text)s</textcolor>
                    <label>%(facts_dot)s</label>
                    <visible>%(imdb_shown)s</visible>
                </control>
                <control type="image">
                    <top>6</top><width>60</width><height>28</height>
                    <texture>silo/imdb.png</texture>
                    <visible>%(imdb_shown)s</visible>
                </control>
                <control type="label">
                    <width>auto</width><height>40</height>
                    <aligny>center</aligny>
                    <font>silo_meta</font>
                    <textcolor>%(text)s</textcolor>
                    <label>$VAR[SiloDetailFactsImdb]</label>
                </control>
                <control type="label">
                    <width>auto</width><height>40</height>
                    <aligny>center</aligny>
                    <font>silo_meta</font>
                    <textcolor>%(text)s</textcolor>
                    <label>%(facts_dot)s</label>
                    <visible>%(tmdb_shown)s</visible>
                </control>
                <control type="image">
                    <top>5</top><width>165</width><height>30</height>
                    <texture>silo/tmdb.png</texture>
                    <visible>%(tmdb_shown)s</visible>
                </control>
                <control type="label">
                    <width>auto</width><height>40</height>
                    <aligny>center</aligny>
                    <font>silo_meta</font>
                    <textcolor>%(text)s</textcolor>
                    <label>$VAR[SiloDetailFactsTmdb]</label>
                </control>
            </control>
            <control type="textbox">
                <top>236</top>
                <width>1080</width><height>106</height>
                <font>silo_plot</font>
                <textcolor>%(text)s</textcolor>
                <label>$VAR[SiloDetailPlot]</label>
            </control>
            <control type="label">
                <top>362</top>
                <width>1000</width><height>34</height>
                <font>silo_detail</font>
                <textcolor>B3EDEDED</textcolor>
                <label>$VAR[SiloDetailCredit]</label>
            </control>
            <!-- Silo's Version / Audio / Subtitles line, else the quality badges. -->
            <control type="label">
                <top>400</top>
                <width>1300</width><height>40</height>
                <aligny>center</aligny>
                <font>silo_detail</font>
                <textcolor>E6EDEDED</textcolor>
                <label>$VAR[SiloDetailTech]</label>
                <visible>%(has_tech)s</visible>
            </control>
            <control type="grouplist">
                <top>406</top>
                <width>1000</width><height>36</height>
                <orientation>horizontal</orientation>
                <itemgap>12</itemgap>%(badges)s
                <visible>!%(has_tech)s</visible>
            </control>
            <!-- Actions: Play (or Resume / Browse), then round buttons. -->
            <control type="grouplist" id="5000">
                <top>470</top>
                <width>1200</width><height>64</height>
                <orientation>horizontal</orientation>
                <itemgap>16</itemgap>
                <ondown condition="%(show)s">60</ondown>
                <ondown condition="%(episode)s + %(episode_pills)s">65</ondown>
                <ondown condition="%(episode)s + !%(episode_pills)s + %(has_season)s">64</ondown>
                <ondown condition="!%(show)s + ![%(episode)s + %(has_season)s]">70</ondown>
                <!-- A show: Play or Resume its next episode, as in Silo (Kodi's button 8
                     would Browse); Browse once every episode is watched. Kodi reserves
                     ids 5-15 in this window (12 chooses art), so this is 300. -->
                <control type="button" id="300">
                    <width>340</width><height>64</height>
                    <label>$VAR[SiloDetailNextLabel]</label>
                    <font>silo_tab</font>
                    <textoffsetx>40</textoffsetx>
                    <align>center</align><aligny>center</aligny>
                    <textcolor>%(text)s</textcolor>
                    <focusedcolor>FF000000</focusedcolor>
                    <texturefocus border="30" colordiffuse="%(text)s">silo/pill.png</texturefocus>
                    <texturenofocus border="30" colordiffuse="33FFFFFF">silo/pill.png</texturenofocus>
                    <!-- Another season chosen: its first episode, as Silo's Apple TV app does. -->
                    <onclick condition="%(other_season)s">PlayMedia($ESCINFO[Container(61).ListItemAbsolute(0).FileNameAndPath],noresume)</onclick>
                    <onclick condition="!%(other_season)s + %(has_next)s + Integer.IsGreater(Container(62).ListItem.PercentPlayed,0)">PlayMedia($ESCINFO[Container(62).ListItem.FileNameAndPath],resume)</onclick>
                    <onclick condition="!%(other_season)s + %(has_next)s + !Integer.IsGreater(Container(62).ListItem.PercentPlayed,0)">PlayMedia($ESCINFO[Container(62).ListItem.FileNameAndPath],noresume)</onclick>
                    <onclick condition="!%(other_season)s + !%(has_next)s">ActivateWindow(Videos,videodb://tvshows/titles/$INFO[ListItem.DBID]/,return)</onclick>
                    <onclick>Dialog.Close(movieinformation)</onclick>
                    <visible>%(show)s</visible>
                </control>
                <!-- A Requests card: Request it, or its state when Silo already has it. -->
                <control type="button" id="301">
                    <visible>%(request)s</visible>
                    <width>340</width><height>64</height>
                    <label>$VAR[SiloRequestLabel]</label>
                    <font>silo_tab</font>
                    <textoffsetx>40</textoffsetx>
                    <align>center</align><aligny>center</aligny>
                    <textcolor>%(text)s</textcolor>
                    <focusedcolor>FF000000</focusedcolor>
                    <texturefocus border="30" colordiffuse="%(text)s">silo/pill.png</texturefocus>
                    <texturenofocus border="30" colordiffuse="33FFFFFF">silo/pill.png</texturenofocus>
                    <!-- The plugin first: closing the page first loses its title. -->
                    <onclick condition="String.IsEqual(ListItem.Property(silo.request.requestable),true)">RunPlugin(plugin://plugin.video.silokodiconnect/?mode=request&amp;type=$INFO[ListItem.Property(silo.request.type)]&amp;tmdb=$INFO[ListItem.Property(silo.request.tmdb)]&amp;title=$ESCINFO[ListItem.Title])</onclick>
                    <onclick condition="String.IsEqual(ListItem.Property(silo.request.requestable),true)">Dialog.Close(movieinformation)</onclick>
                </control>
                <!-- Play or Resume, with Silo's play icon. Its group has an id: the
                     grouplist moves only between children with ids. -->
                <control type="group" id="1008">
                    <width>340</width><height>64</height>
                    <visible>!%(show)s + !%(request)s</visible>
                    <!-- Not Kodi's Play button (id 8), which asks whether to resume:
                         Resume resumes, as in Silo, and Start over plays from the start. -->
                    <control type="button" id="308">
                        <width>340</width><height>64</height>
                        <label />
                        <onclick condition="ListItem.IsResumable">PlayMedia($ESCINFO[ListItem.FileNameAndPath],resume)</onclick>
                        <onclick condition="!ListItem.IsResumable">PlayMedia($ESCINFO[ListItem.FileNameAndPath],noresume)</onclick>
                        <onclick>Dialog.Close(movieinformation)</onclick>
                        <texturefocus border="30" colordiffuse="%(text)s">silo/pill.png</texturefocus>
                        <texturenofocus border="30" colordiffuse="33FFFFFF">silo/pill.png</texturenofocus>
                    </control>
                    <!-- The label beside the icon (a button's own label is inset on
                         both sides, and scrolled when it didn't fit). -->
                    <control type="label">
                        <left>78</left><width>250</width><height>64</height>
                        <aligny>center</aligny>
                        <font>silo_tab</font>
                        <textcolor>FF000000</textcolor>
                        <label>$VAR[SiloDetailPlayLabel]</label>
                        <visible>Control.HasFocus(308)</visible>
                    </control>
                    <control type="label">
                        <left>78</left><width>250</width><height>64</height>
                        <aligny>center</aligny>
                        <font>silo_tab</font>
                        <textcolor>%(text)s</textcolor>
                        <label>$VAR[SiloDetailPlayLabel]</label>
                        <visible>!Control.HasFocus(308)</visible>
                    </control>
                    <control type="image">
                        <left>36</left><top>18</top><width>28</width><height>28</height>
                        <texture colordiffuse="FF000000">osd/fullscreen/buttons/play.png</texture>
                        <visible>Control.HasFocus(308)</visible>
                    </control>
                    <control type="image">
                        <left>36</left><top>18</top><width>28</width><height>28</height>
                        <texture colordiffuse="%(text)s">osd/fullscreen/buttons/play.png</texture>
                        <visible>!Control.HasFocus(308)</visible>
                    </control>
                </control>%(start_over)s%(previous)s%(trailer)s%(silo_trailer)s%(watchlist)s%(versions)s%(more)s
            </control>
        </control>

        <!-- A show's next episode: the first unwatched one, specials aside. Off
             screen rather than hidden, so Kodi loads it. -->
        <control type="list" id="62">
            <left>-3000</left><top>0</top>
            <width>10</width><height>10</height>
            <content target="videos">%(next_path)s</content>
            <itemlayout width="10" height="10" />
            <focusedlayout width="10" height="10" />
            <visible>%(show)s</visible>
        </control>

        <!-- Below the actions: a show's seasons and episodes, then the cast;
             the column scrolls to whichever has focus. -->
        <control type="grouplist" id="7000">
            <top>%(lower_top)d</top>
            <width>1920</width><height>%(lower_h)d</height>
            <orientation>vertical</orientation>
            <itemgap>0</itemgap>
            <scrolltime tween="cubic" easing="out">300</scrolltime>
            <!-- Seasons (Kodi's own season folders), then the chosen season's episodes. -->
            <control type="group">
                <height>%(episodes_h)d</height>
                <visible>%(show)s</visible>
                <control type="list" id="60">
                    <left>%(lx)d</left><top>0</top>
                    <width>%(lw)d</width><height>56</height>
                    <orientation>horizontal</orientation>
                    <onup>5000</onup>
                    <ondown>61</ondown>
                    <scrolltime tween="cubic" easing="out">200</scrolltime>
                    <content target="videos">videodb://tvshows/titles/$INFO[ListItem.DBID]/</content>
                    <itemlayout width="%(pill_item)d" height="56">%(season)s
                    </itemlayout>
                    <focusedlayout width="%(pill_item)d" height="56">%(season_focused)s
                    </focusedlayout>
                </control>
                <control type="list" id="61">
                    <left>%(lx)d</left><top>76</top>
                    <width>%(lw)d</width><height>%(episode_h)d</height>
                    <orientation>horizontal</orientation>
                    <onup>60</onup>
                    <ondown condition="Integer.IsGreater(Container(70).NumItems,0)">70</ondown>
                    <ondown condition="!Integer.IsGreater(Container(70).NumItems,0) + %(has_videos)s">71</ondown>
                    <scrolltime tween="cubic" easing="out">280</scrolltime>
                    <onclick>PlayMedia($ESCINFO[ListItem.FileNameAndPath])</onclick>
                    <onclick>Dialog.Close(movieinformation)</onclick>
                    <content target="videos">$INFO[Container(60).ListItem.FolderPath]</content>
                    <itemlayout width="400" height="%(episode_h)d">%(episode_card)s
                    </itemlayout>
                    <focusedlayout width="400" height="%(episode_h)d">%(episode_card_focused)s
                    </focusedlayout>
                </control>
            </control>
            <!-- An episode: the rest of its season, as in Silo, on the current one. -->
            <control type="group">
                <height>%(episodes_h)d</height>
                <!-- Shown while the pills load too: the rail loads from them, and Kodi
                     doesn't load a list inside a hidden group. -->
                <visible>%(episode)s + [%(has_season)s | Container(64).IsUpdating | Integer.IsGreater(Container(65).NumItems,0) | Container(65).IsUpdating]</visible>
                <!-- Silo's season pills when the show has more than one season, else
                     the season's name. -->
%(show_pill)s
                <control type="list" id="65">
                    <visible>%(episode)s + !String.IsEmpty(ListItem.Property(silo.show_path))</visible>
                    <animation effect="fade" start="0" end="0" time="0" condition="!%(episode_pills)s">Conditional</animation>
                    <left>%(pills_x)d</left><top>0</top>
                    <onleft>309</onleft>
                    <width>%(lw)d</width><height>56</height>
                    <orientation>horizontal</orientation>
                    <onup>5000</onup>
                    <ondown>64</ondown>
                    <scrolltime tween="cubic" easing="out">200</scrolltime>
                    <content target="videos">$INFO[ListItem.Property(silo.show_path)]</content>
                    <itemlayout width="%(pill_item)d" height="56">%(episode_season)s
                    </itemlayout>
                    <focusedlayout width="%(pill_item)d" height="56">%(episode_season_focused)s
                    </focusedlayout>
                </control>
                <control type="label">
                    <left>%(x)d</left>
                    <width>1000</width><height>56</height>
                    <aligny>center</aligny>
                    <font>silo_row</font>
                    <textcolor>%(text)s</textcolor>
                    <label>$VAR[SiloEpisodeSeason]</label>
                    <visible>!%(episode_pills)s</visible>
                </control>
                <control type="list" id="64">
                    <visible>%(episode)s</visible>
                    <left>%(lx)d</left><top>76</top>
                    <width>%(lw)d</width><height>%(episode_h)d</height>
                    <orientation>horizontal</orientation>
                    <onup condition="%(episode_pills)s">65</onup>
                    <onup condition="!%(episode_pills)s">5000</onup>
                    <ondown condition="Integer.IsGreater(Container(70).NumItems,0)">70</ondown>
                    <ondown condition="!Integer.IsGreater(Container(70).NumItems,0) + %(has_videos)s">71</ondown>
                    <ondown condition="!Integer.IsGreater(Container(70).NumItems,0) + !%(has_videos)s">63</ondown>
                    <scrolltime tween="cubic" easing="out">280</scrolltime>
                    <onclick>PlayMedia($ESCINFO[ListItem.FileNameAndPath])</onclick>
                    <onclick>Dialog.Close(movieinformation)</onclick>
                    <!-- $INFO, not a $VAR: Kodi reads a $VAR here only when the page opens. -->
                    <content target="videos">$INFO[Container(65).ListItem.FolderPath]</content>
                    <itemlayout width="400" height="%(episode_h)d">%(season_card)s
                    </itemlayout>
                    <focusedlayout width="400" height="%(episode_h)d">%(season_card_focused)s
                    </focusedlayout>
                </control>
            </control>
            <!-- Cast & crew: Kodi fills list 50. -->
            <control type="group">
                <height>%(cast_h)d</height>
                <!-- From the title's own cast, not list 50's items: Kodi doesn't
                     refresh a list inside a hidden group. -->
                <visible>Integer.IsGreater(Container(70).NumItems,0) | !String.IsEmpty(ListItem.Cast)</visible>
                <control type="label">
                    <left>%(x)d</left>
                    <width>1000</width><height>46</height>
                    <font>silo_row</font>
                    <textcolor>%(text)s</textcolor>
                    <label>Cast &amp; Crew</label>
                </control>
                <control type="list" id="70">
                    <!-- Not Kodi's cast list (control 50), which searches the library for a
                         chosen name: SiloKodiConnect's, so a name opens the person page. -->
                    <content target="videos">plugin://plugin.video.silokodiconnect/?mode=cast&amp;type=$INFO[ListItem.DBType]&amp;dbid=$INFO[ListItem.DBID]</content>
                    <left>%(lx)d</left><top>60</top>
                    <width>%(lw)d</width><height>280</height>
                    <orientation>horizontal</orientation>
                    <onup condition="%(show)s">61</onup>
                    <onup condition="%(episode)s + %(has_season)s">64</onup>
                    <onup condition="!%(show)s + ![%(episode)s + %(has_season)s]">5000</onup>
                    <!-- A cast member's page (SiloKodiConnect: Silo's person, their titles here). -->
                    <onclick>RunPlugin(plugin://plugin.video.silokodiconnect/?mode=person&amp;id=$INFO[Window(movieinformation).Property(silo.content_id)]&amp;name=$INFO[ListItem.Label])</onclick>
                    <scrolltime tween="cubic" easing="out">280</scrolltime>
                    <ondown condition="%(has_videos)s">71</ondown>
                    <ondown condition="!%(has_videos)s + %(has_similar)s">63</ondown>
                    <itemlayout width="220" height="280">%(person)s
                    </itemlayout>
                    <focusedlayout width="220" height="280">%(person_focused)s
                    </focusedlayout>
                </control>
            </control>
            <!-- Trailers & More: the title's YouTube videos from Silo (SiloKodiConnect),
                 as Silo's Apple TV app; one plays as the Trailer button's does. -->
            <control type="group">
                <height>%(videos_h)d</height>
                <visible>%(has_videos)s | Container(71).IsUpdating</visible>
                <control type="label">
                    <left>%(x)d</left>
                    <width>1000</width><height>46</height>
                    <font>silo_row</font>
                    <textcolor>%(text)s</textcolor>
                    <label>Trailers &amp; More</label>
                </control>
                <control type="list" id="71">
                    <content target="videos">plugin://plugin.video.silokodiconnect/?mode=videos&amp;id=$INFO[Window(movieinformation).Property(silo.content_id)]</content>
                    <left>%(lx)d</left><top>56</top>
                    <width>%(lw)d</width><height>%(video_item_h)d</height>
                    <orientation>horizontal</orientation>
                    <scrolltime tween="cubic" easing="out">280</scrolltime>
                    <onup condition="Integer.IsGreater(Container(70).NumItems,0)">70</onup>
                    <onup condition="!Integer.IsGreater(Container(70).NumItems,0) + %(show)s">61</onup>
                    <onup condition="!Integer.IsGreater(Container(70).NumItems,0) + !%(show)s">5000</onup>
                    <ondown condition="%(has_similar)s">63</ondown>%(video_play)s
                    <itemlayout width="%(video_item_w)d" height="%(video_item_h)d">%(video_card)s
                    </itemlayout>
                    <focusedlayout width="%(video_item_w)d" height="%(video_item_h)d">%(video_card_focused)s
                    </focusedlayout>
                </control>
            </control>
            <!-- More Like This: same-genre titles from the library, best rated
                 first (SiloKodiConnect's silo.similar). -->
            <control type="group">
                <height>%(similar_h)d</height>
                <visible>%(has_similar)s | Container(63).IsUpdating</visible>
                <control type="label">
                    <left>%(x)d</left>
                    <width>1000</width><height>46</height>
                    <font>silo_row</font>
                    <textcolor>%(text)s</textcolor>
                    <label>More Like This</label>
                </control>
                <control type="list" id="63">
                    <visible>%(has_similar)s | Container(63).IsUpdating</visible>
                    <left>%(lx)d</left><top>56</top>
                    <width>%(lw)d</width><height>%(similar_item_h)d</height>
                    <orientation>horizontal</orientation>
                    <scrolltime tween="cubic" easing="out">280</scrolltime>
                    <onup condition="%(has_videos)s">71</onup>
                    <onup condition="!%(has_videos)s + Integer.IsGreater(Container(70).NumItems,0)">70</onup>
                    <onup condition="!%(has_videos)s + !Integer.IsGreater(Container(70).NumItems,0) + %(show)s">61</onup>
                    <onup condition="!%(has_videos)s + !Integer.IsGreater(Container(70).NumItems,0) + !%(show)s">5000</onup>
                    <!-- Kodi can't open an info page from inside one: close this one and
                         have SiloKodiConnect open the chosen title's. That page opens with
                         the column below still scrolled to this rail; silo.from_rail has
                         its onload scroll it back to the top. -->
                    <onclick>SetProperty(silo.from_rail,1,home)</onclick>
                    <onclick>Dialog.Close(movieinformation)</onclick>
                    <onclick condition="String.IsEmpty(ListItem.Property(silo.request.tmdb))">RunPlugin(plugin://plugin.video.silokodiconnect/?mode=info&amp;type=$INFO[ListItem.DBType]&amp;dbid=$INFO[ListItem.DBID])</onclick>
                    <onclick condition="!String.IsEmpty(ListItem.Property(silo.request.tmdb))">RunPlugin(plugin://plugin.video.silokodiconnect/?mode=request_info&amp;type=$INFO[ListItem.Property(silo.request.type)]&amp;tmdb=$INFO[ListItem.Property(silo.request.tmdb)])</onclick>
                    <content target="videos" sortby="rating" sortorder="descending">$INFO[ListItem.Property(silo.similar)]</content>
                    <itemlayout width="%(similar_item_w)d" height="%(similar_item_h)d">%(similar_card)s
                    </itemlayout>
                    <focusedlayout width="%(similar_item_w)d" height="%(similar_item_h)d">%(similar_card_focused)s
                    </focusedlayout>
                </control>
            </control>
        </control>
    </controls>
</window>
''' % {'background': BACKGROUND, 'x': SAFE_X, 'top': TOP, 'text': TEXT, 'dim': TEXT_DIM, 'has_logo': has_logo,
       'facts_dot': FACTS_DOT, 'imdb_shown': split_ratings(VARIABLES)[1], 'tmdb_shown': split_ratings(VARIABLES)[2], 'other_season': OTHER_SEASON,
       'mpaa': badge('$VAR[SiloDetailMpaa]', '[!String.IsEmpty(ListItem.Mpaa) | '
                     '!String.IsEmpty(ListItem.Property(silo.mpaa))]', 'silo_badge', 34).replace(
                         '<height>34</height>', '<top>3</top><height>34</height>', 1),
       'badges': badges, 'pills_x': SAFE_X - 6 + PILL_ITEM_W - 50, 'pill_item': PILL_ITEM_W, 'show_pill': show_pill(),
       'has_tech': '[!String.IsEmpty(ListItem.Property(silo.version)) | !String.IsEmpty(ListItem.Property(silo.audio)) | %s]' % 'Control.HasFocus(64) | Control.HasFocus(65) | Control.HasFocus(61) | Control.HasFocus(60)',
       # Play from the beginning, when Play would resume (Silo's More menu has it;
       # here it's a button, as there's no other way to it).
       'start_over': round_button(304, 'silo/start_over.png', '!%s + %s + ListItem.IsResumable' % (SHOW, NOT_REQUEST),
                                  'PlayMedia($ESCINFO[ListItem.FileNameAndPath],noresume)</onclick>\n'
                                  '                    <onclick>Dialog.Close(movieinformation)'),
       'previous': round_button(302, 'osd/fullscreen/buttons/previous.png', 'String.IsEqual(ListItem.DBType,episode)',
                                'RunPlugin(plugin://plugin.video.silokodiconnect/?mode=previous&amp;dbid=$INFO[ListItem.DBID])'),
       'more': round_button(303, 'icons/menu.png',
                            '[String.IsEqual(ListItem.DBType,episode) | String.IsEqual(ListItem.DBType,movie) | String.IsEqual(ListItem.DBType,tvshow)] + String.IsEmpty(ListItem.Property(silo.request.tmdb))',
                            more_opener()),
       'trailer': round_button(11, 'icons/infodialogs/trailer.png', '!String.IsEmpty(ListItem.Trailer)'),
       # Silo's trailer (SiloKodiConnect's silo.trailer, a YouTube id) when the
       # library has none: played by the YouTube add-on, which it offers to
       # install when it's missing.
       'silo_trailer': round_button(
           351, 'icons/infodialogs/trailer.png',
           'String.IsEmpty(ListItem.Trailer) + !String.IsEmpty(ListItem.Property(silo.trailer))',
           'noop</onclick>\n'
           # The page closes for the trailer and SiloKodiConnect reopens it
           # when the trailer stops, ends or never starts (silokodi.trailer_return).
           # Meanwhile the window under it shows a cover with the title's
           # fanart (SiloTrailerCover, while silokodi.trailer_playing is set);
           # the page clears it as it opens.
           '                    <onclick condition="System.HasAddon(plugin.video.youtube)">'
           'SetProperty(silokodi.trailer_art,$INFO[ListItem.Art(fanart)],home)</onclick>\n'
           '                    <onclick condition="System.HasAddon(plugin.video.youtube)">'
           'SetProperty(silokodi.trailer_return,$INFO[ListItem.DBType]|$INFO[ListItem.DBID],home)</onclick>\n'
           '                    <onclick condition="System.HasAddon(plugin.video.youtube)">'
           'SetProperty(silokodi.trailer_playing,1,home)</onclick>\n'
           '                    <onclick condition="System.HasAddon(plugin.video.youtube)">'
           'PlayMedia(plugin://plugin.video.youtube/play/?video_id=$INFO[ListItem.Property(silo.trailer)])</onclick>\n'
           # Closed, so the player's own controls get the remote (left open,
           # even unseen, the page takes OK).
           '                    <onclick condition="System.HasAddon(plugin.video.youtube)">Dialog.Close(movieinformation)</onclick>\n'
           '                    <onclick condition="!System.HasAddon(plugin.video.youtube)">InstallAddon(plugin.video.youtube)'),
       # Silo's watchlist, for a film or series: a filled bookmark when on it.
       'watchlist': round_button(
           352, '$VAR[SiloWatchlistIcon]', '!String.IsEmpty(ListItem.Property(silo.watchlist))',
           'noop</onclick>\n'
           '                    <onclick condition="$EXP[SiloOnWatchlist]">RunPlugin(plugin://plugin.video.silokodiconnect/'
           '?mode=watchlist&amp;id=$INFO[ListItem.Property(silo.content_id)]&amp;add=0)</onclick>\n'
           '                    <onclick condition="!$EXP[SiloOnWatchlist]">RunPlugin(plugin://plugin.video.silokodiconnect/'
           '?mode=watchlist&amp;id=$INFO[ListItem.Property(silo.content_id)]&amp;add=1)'),
       'versions': round_button(14, 'icons/infodialogs/versions.png',
                                'String.IsEqual(ListItem.DBType,movie) + Integer.IsGreater(ListItem.VideoVersionsCount,1)'),
       'lx': SAFE_X - 6, 'lw': 1920 - SAFE_X + 6, 'person': person(False), 'person_focused': person(True),
       'has_similar': 'Integer.IsGreater(Container(63).NumItems,0)', 'similar_h': SECTION_H,
       'has_videos': HAS_VIDEOS, 'videos_h': SECTION_H, 'video_play': video_play(),
       'video_item_w': VIDEO_W + 40, 'video_item_h': VIDEO_H + 12 + 84,
       'video_card': video_card(False), 'video_card_focused': video_card(True),
       'similar_item_w': POSTER['width'] + POSTER['gap'], 'similar_item_h': POSTER['height'] + 12 + 76,
       'similar_card': card_layout(POSTER, False), 'similar_card_focused': card_layout(POSTER, True, 63),
       'has_season': 'Integer.IsGreater(Container(64).NumItems,0)', 'episode_pills': EPISODE_PILLS,
       'episode_season': season(False, 65), 'episode_season_focused': season(True, 65),
       'season_card': episode_card(False, 64), 'season_card_focused': episode_card(True, 64, CURRENT),
       'request': '!String.IsEmpty(ListItem.Property(silo.request.tmdb))', 'episode': episode, 'show': SHOW, 'has_next': HAS_NEXT, 'next_path': NEXT_EPISODE, 'lower_top': LOWER_TOP, 'lower_h': 1080 - LOWER_TOP,
       'episodes_h': SECTION_H, 'episode_h': EPISODE_H, 'cast_h': SECTION_H,
       'season': season(False), 'season_focused': season(True),
       'episode_card': episode_card(False), 'episode_card_focused': episode_card(True)}


# A series Silo can request is a tvshow to Kodi too, but has no library
# seasons or episodes: those sections are for library shows only.
NOT_REQUEST = 'String.IsEmpty(ListItem.Property(silo.request.tmdb))'
SHOW = '[String.IsEqual(ListItem.DBType,tvshow) + %s]' % NOT_REQUEST
EPISODE_PILLS = '[Integer.IsGreater(Container(65).NumItems,1) | Container(65).IsUpdating]'
# On an episode's page: the episode opened (silo.episode_id, set on load).
CURRENT = 'String.IsEqual(ListItem.DBID,Window(movieinformation).Property(silo.episode_id))'
HAS_NEXT = '[Integer.IsGreater(Container(62).NumItems,0) + %s]' % NOT_REQUEST
NEXT_EPISODE = 'videodb://tvshows/titles/$INFO[ListItem.DBID]/-1/?xsp=' + quote(json.dumps(
    {'type': 'episodes', 'order': {'method': 'episode', 'direction': 'ascending'}, 'limit': 1,
     'rules': {'and': [{'field': 'playcount', 'operator': 'is', 'value': ['0']},
                       {'field': 'season', 'operator': 'greaterthan', 'value': ['0']}]}},
    separators=(',', ':')), safe='')
LOWER_TOP = 676
# An episode card: a 360x202 still, then "S1 · E2 · Title" and its runtime.
EPISODE_H = 202 + 12 + 76
# Each section below the actions is exactly as tall as the column, so the
# column scrolls a whole section at a time: no strip of the one above.
SECTION_H = 1080 - LOWER_TOP


PILL_W, PILL_ITEM_W = 168, 184  # a season pill, and its slot with the gap


def show_pill():
    """Silo's Show pill before an episode's season pills: the series page."""
    return '''
                <control type="button" id="309">
                    <left>%(x)d</left><top>0</top>
                    <width>118</width><height>56</height>
                    <label>Show</label>
                    <font>silo_meta</font>
                    <align>center</align><aligny>center</aligny>
                    <textcolor>%(dim)s</textcolor>
                    <focusedcolor>FF000000</focusedcolor>
                    <texturefocus border="28" colordiffuse="%(text)s">silo/pill.png</texturefocus>
                    <texturenofocus border="28" colordiffuse="59FFFFFF">silo/season_ring.png</texturenofocus>
                    <onup>5000</onup>
                    <onright>65</onright>
                    <ondown>64</ondown>
                    <onclick>SetProperty(silo.from_rail,1,home)</onclick>
                    <!-- The episode's id while this page is open (RunPlugin runs later). -->
                    <onclick>RunPlugin(plugin://plugin.video.silokodiconnect/?mode=show&amp;episode=$INFO[ListItem.DBID])</onclick>
                    <onclick>Dialog.Close(movieinformation)</onclick>
                    <visible>%(episode)s + %(pills)s</visible>
                </control>''' % {'x': SAFE_X, 'dim': TEXT_DIM, 'text': TEXT, 'episode': 'String.IsEqual(ListItem.DBType,episode)',
                         'pills': EPISODE_PILLS}


def season(focused, list_id=60):
    """A season pill as Silo's Apple TV app draws them: a faint chip, the
    chosen season a lighter one, and white with dark text while focused."""
    def pill(texture, colour, visible=''):
        return '''
                        <control type="image">
                            <width>%(w)d</width><height>56</height>
                            <texture border="28" colordiffuse="%(colour)s">%(texture)s</texture>%(visible)s
                        </control>''' % {'w': PILL_W, 'colour': colour, 'texture': texture,
                                         'visible': '<visible>%s</visible>' % visible if visible else ''}

    def label(colour, visible=''):
        return '''
                        <control type="label">
                            <width>%(w)d</width><height>56</height>
                            <align>center</align><aligny>center</aligny>
                            <font>silo_meta</font>
                            <textcolor>%(colour)s</textcolor>
                            <label>$VAR[SiloSeasonLabel]</label>%(visible)s
                        </control>''' % {'w': PILL_W, 'colour': colour,
                                         'visible': '<visible>%s</visible>' % visible if visible else ''}
    has = 'Control.HasFocus(%d)' % list_id
    if focused:
        return (pill('silo/pill.png', TEXT, has) + label('FF000000', has) +
                pill('silo/pill.png', '38FFFFFF', '!' + has) + label(TEXT, '!' + has))
    return pill('silo/pill.png', '14FFFFFF') + label(TEXT)


def episode_title(scroll, visible):
    """An episode card's "S01E01 · Title": scrolling only while its row has focus."""
    return '''
                        <control type="label">
                            <left>6</left><top>222</top>
                            <width>360</width><height>34</height>
                            <font>silo_card_title</font>
                            <textcolor>%(text)s</textcolor>
                            <label>$VAR[SiloEpisodeCode]$INFO[ListItem.Title, · ,]</label>%(scroll)s%(visible)s
                        </control>''' % {'text': TEXT,
                                         'scroll': '\n                            <scroll>true</scroll><scrollspeed>50</scrollspeed>'
                                                   '<scrollsuffix>     ·     </scrollsuffix>' if scroll else '',
                                         'visible': '\n                            <visible>%s</visible>' % visible if visible else ''}


def episode_card(focused, list_id=61, current='String.IsEqual(ListItem.DBID,Container(62).ListItem.DBID)'):
    """An episode card: a still with progress and watched marks, then
    "S1 · E2 · Title" and the runtime. `current` marks Silo's current episode
    (the next one on a show's page, the opened one on an episode's)."""
    lit = 'Control.HasFocus(%d)' % list_id
    zoom = focus_zoom(lit) if focused else ''
    # Focus as on Silo's Apple TV app; Silo's current episode keeps the rim alone.
    sheen = (focus_sheen(360, 202, 'silo/card_landscape_mask.png', 'silo/card_landscape_rim.png', lit) + '''
                        <control type="image">
                            <left>6</left><top>6</top>
                            <width>360</width><height>202</height>
                            <texture colordiffuse="33FFFFFF">silo/card_landscape_rim.png</texture>
                            <visible>!%s + %s</visible>
                        </control>''' % (lit, current)) if focused else ''
    return '''
                    <control type="group">%(zoom)s
                        <control type="image">
                            <left>6</left><top>6</top>
                            <width>360</width><height>202</height>
                            <aspectratio>scale</aspectratio>
                            <texture background="true" diffuse="silo/card_landscape_mask.png" fallback="DefaultTVShows.png">$INFO[ListItem.Art(thumb)]</texture>
                        </control>
                        <control type="progress">
                            <left>18</left><top>192</top>
                            <width>336</width><height>6</height>
                            <info>ListItem.PercentPlayed</info>
                            <texturebg colordiffuse="66FFFFFF">colors/white.png</texturebg>
                            <midtexture colordiffuse="%(text)s">colors/white.png</midtexture>
                            <visible>Integer.IsGreater(ListItem.PercentPlayed,0)</visible>
                        </control>
%(sheen)s%(watched)s
%(titles)s
                        <control type="label">
                            <left>6</left><top>256</top>
                            <width>360</width><height>30</height>
                            <font>silo_detail</font>
                            <textcolor>99EDEDED</textcolor>
                            <label>$INFO[ListItem.Premiered]$INFO[ListItem.Duration(mins), · , min]</label>
                        </control>
                    </control>''' % {'zoom': zoom, 'sheen': sheen, 'text': TEXT, 'dim': TEXT_DIM,
                                         'watched': watched_disc(366 - 10 - 40, 16, 'Integer.IsGreater(ListItem.PlayCount,0)'),
                                         'titles': ''.join(episode_title(scroll, visible) for scroll, visible in
                                                           (((True, lit), (False, '!' + lit)) if focused else ((False, ''),)))}



HAS_VIDEOS = 'Integer.IsGreater(Container(71).NumItems,0)'
VIDEO_W, VIDEO_H = 448, 252     # Silo's Apple TV trailer cards, 16:9
PAGE = 'Window(movieinformation).Property(silo.page_%s)'


def video_card(focused):
    """A Trailers & More card: YouTube's thumbnail with a play icon, its name
    and "YouTube" under it, centred; focus as the other cards."""
    lit = 'Control.HasFocus(71)'
    return '''
                    <control type="group">%(zoom)s
                        <control type="image">
                            <left>6</left><top>6</top><width>%(w)d</width><height>%(h)d</height>
                            <aspectratio>scale</aspectratio>
                            <texture background="true" diffuse="silo/card_landscape_mask.png" fallback="colors/grey.png">$INFO[ListItem.Art(thumb)]</texture>
                        </control>
                        <control type="image">
                            <left>%(px)d</left><top>%(py)d</top><width>56</width><height>56</height>
                            <texture colordiffuse="E6FFFFFF">silo/play_circle.png</texture>
                        </control>%(sheen)s
                        <control type="label">
                            <left>6</left><top>%(t1)d</top><width>%(w)d</width><height>34</height>
                            <align>center</align>
                            <font>silo_card_title</font>
                            <textcolor>%(title)s</textcolor>
                            <label>$INFO[ListItem.Label]</label>
                        </control>
                        <control type="label">
                            <left>6</left><top>%(t2)d</top><width>%(w)d</width><height>30</height>
                            <align>center</align>
                            <font>silo_card_sub</font>
                            <textcolor>99EDEDED</textcolor>
                            <label>$INFO[ListItem.Label2]</label>
                        </control>
                    </control>''' % {'zoom': focus_zoom(lit) if focused else '', 'w': VIDEO_W, 'h': VIDEO_H,
                                      'px': 6 + VIDEO_W // 2 - 28, 'py': 6 + VIDEO_H // 2 - 28,
                                      'sheen': focus_sheen(VIDEO_W, VIDEO_H, 'silo/card_landscape_mask.png',
                                                           'silo/card_landscape_rim.png', lit) if focused else '',
                                      't1': VIDEO_H + 20, 't2': VIDEO_H + 54, 'title': TEXT}


def video_play():
    """A video's onclick: the Trailer button's way (tools: silo_trailer), with
    the page's own title and art, as ListItem is the video here."""
    youtube = 'System.HasAddon(plugin.video.youtube)'
    steps = [('SetProperty(silokodi.trailer_art,$INFO[%s],home)' % (PAGE % 'fanart')),
             ('SetProperty(silokodi.trailer_return,$INFO[%s]|$INFO[%s],home)' % (PAGE % 'type', PAGE % 'dbid')),
             'SetProperty(silokodi.trailer_playing,1,home)',
             'PlayMedia(plugin://plugin.video.youtube/play/?video_id=$INFO[ListItem.Property(silo.video.key)])',
             'Dialog.Close(movieinformation)']
    out = ''.join('\n                    <onclick condition="%s">%s</onclick>' % (youtube, step) for step in steps)
    return out + '\n                    <onclick condition="!%s">InstallAddon(plugin.video.youtube)</onclick>' % youtube


def person(focused):
    # Silo's Apple TV app grows the photo on focus; no ring.
    zoom = focus_zoom('Control.HasFocus(70)', 20) if focused else ''
    return '''
                    <control type="image">
                        <left>20</left><top>6</top>
                        <width>172</width><height>172</height>
                        <!-- Cropped to fill the circle; scalediffuse="false" keeps the round
                             mask on the control instead of stretching it with the photo. -->
                        <aspectratio scalediffuse="false">scale</aspectratio>
                        <texture background="true" diffuse="silo/person_mask.png" fallback="silo/person_placeholder.png">$INFO[ListItem.Art(thumb)]</texture>%(zoom)s
                    </control>
                    <control type="label">
                        <left>0</left><top>196</top>
                        <width>212</width><height>34</height>
                        <align>center</align>
                        <font>silo_card_title</font>
                        <textcolor>%(text)s</textcolor>
                        <label>$INFO[ListItem.Label]</label>
                    </control>
                    <control type="label">
                        <left>0</left><top>230</top>
                        <width>212</width><height>32</height>
                        <align>center</align>
                        <font>silo_card_sub</font>
                        <textcolor>%(dim)s</textcolor>
                        <label>$INFO[ListItem.Label2]</label>
                    </control>''' % {'zoom': zoom, 'text': TEXT, 'dim': TEXT_DIM}


VARIABLES = '''
    <!-- Silo Skyline detail (tools/build_info.py) -->
    <variable name="SiloDetailArt">
        <value condition="!String.IsEmpty(ListItem.Art(fanart))">$INFO[ListItem.Art(fanart)]</value>
        <value condition="!String.IsEmpty(ListItem.Art(tvshow.fanart))">$INFO[ListItem.Art(tvshow.fanart)]</value>
        <value>$INFO[ListItem.Art(landscape)]</value>
    </variable>
    <variable name="SiloDetailLogo">
        <value condition="!String.IsEmpty(ListItem.Art(clearlogo))">$INFO[ListItem.Art(clearlogo)]</value>
        <value>$INFO[ListItem.Art(tvshow.clearlogo)]</value>
    </variable>
    <variable name="SiloDetailTitle">
        <value condition="String.IsEqual(ListItem.DBType,episode)">$INFO[ListItem.TVShowTitle]</value>
        <value>$INFO[ListItem.Title]</value>
    </variable>
    <variable name="SiloRequestLabel">
        <value condition="String.IsEqual(ListItem.Property(silo.request.requestable),true)">Request</value>
        <value condition="!String.IsEmpty(ListItem.Property(silo.request.label))">$INFO[ListItem.Property(silo.request.label)]</value>
        <value>Not available to request</value>
    </variable>
    <variable name="SiloDetailMpaa">
        <value condition="!String.IsEmpty(ListItem.Mpaa)">$INFO[ListItem.Mpaa]</value>
        <value>$INFO[ListItem.Property(silo.mpaa)]</value>
    </variable>
    <variable name="SiloDetailFacts">
        <value condition="Control.HasFocus(64) | [Control.HasFocus(65) + Integer.IsGreater(Container(64).NumItems,0)]">$INFO[Container(64).ListItem.Premiered]$INFO[Container(64).ListItem.Duration(mins), · , min]$INFO[Container(64).ListItem.Rating(imdb), · [COLOR BFEDEDED]IMDb[/COLOR] [B],[/B]]$INFO[Container(64).ListItem.Rating(themoviedb), · [COLOR BFEDEDED]TMDB[/COLOR] [B],[/B]]$INFO[Container(64).ListItem.Season, · Season ,]$INFO[Container(64).ListItem.Episode, · Episode ,]</value>
        <value condition="Control.HasFocus(61) | [Control.HasFocus(60) + Integer.IsGreater(Container(61).NumItems,0)]">$INFO[Container(61).ListItem.Premiered]$INFO[Container(61).ListItem.Duration(mins), · , min]$INFO[Container(61).ListItem.Rating(imdb), · [COLOR BFEDEDED]IMDb[/COLOR] [B],[/B]]$INFO[Container(61).ListItem.Rating(themoviedb), · [COLOR BFEDEDED]TMDB[/COLOR] [B],[/B]]$INFO[Container(61).ListItem.Season, · Season ,]$INFO[Container(61).ListItem.Episode, · Episode ,]</value>
        <value condition="!String.IsEmpty(ListItem.Property(silo.request.tmdb)) + !String.IsEmpty(ListItem.Property(silo.request.seasons))">$INFO[ListItem.Year]$INFO[ListItem.Genre, · ,]$INFO[ListItem.Property(silo.rating), · ,]$INFO[ListItem.Property(silo.request.seasons), · , seasons]</value>
        <value condition="!String.IsEmpty(ListItem.Property(silo.request.tmdb))">$INFO[ListItem.Year]$INFO[ListItem.Genre, · ,]$INFO[ListItem.Property(silo.rating), · ,]$INFO[ListItem.Duration(mins), · , min]</value>
        <!-- Silo's order: date · runtime · IMDb · TMDB · Season · Episode. -->
        <value condition="String.IsEqual(ListItem.DBType,episode) + !String.IsEmpty(ListItem.Property(silo.air_date))">$INFO[ListItem.Property(silo.air_date)]$INFO[ListItem.Duration(mins), · , min]$INFO[ListItem.Property(silo.rating.imdb), · [COLOR BFEDEDED]IMDb[/COLOR] [B],[/B]]$INFO[ListItem.Property(silo.rating.tmdb), · [COLOR BFEDEDED]TMDB[/COLOR] [B],[/B]]$INFO[ListItem.Season, · Season ,]$INFO[ListItem.Episode, · Episode ,]</value>
        <value condition="String.IsEqual(ListItem.DBType,movie) + [!String.IsEmpty(ListItem.Property(silo.rating.imdb)) | !String.IsEmpty(ListItem.Property(silo.rating.tmdb))]">$INFO[ListItem.Year]$INFO[ListItem.Duration(mins), · , min]$INFO[ListItem.Property(silo.rating.imdb), · [COLOR BFEDEDED]IMDb[/COLOR] [B],[/B]]$INFO[ListItem.Property(silo.rating.tmdb), · [COLOR BFEDEDED]TMDB[/COLOR] [B],[/B]]$VAR[SiloDetailGenres]</value>
        <value condition="String.IsEqual(ListItem.DBType,tvshow) + [!String.IsEmpty(ListItem.Property(silo.rating.imdb)) | !String.IsEmpty(ListItem.Property(silo.rating.tmdb))]">$INFO[ListItem.Year]$VAR[SiloDetailSeasons]$INFO[ListItem.Property(silo.rating.imdb), · [COLOR BFEDEDED]IMDb[/COLOR] [B],[/B]]$INFO[ListItem.Property(silo.rating.tmdb), · [COLOR BFEDEDED]TMDB[/COLOR] [B],[/B]]$VAR[SiloDetailGenres]</value>
        <value condition="String.IsEqual(ListItem.DBType,episode) + !String.IsEmpty(ListItem.Property(silo.code))">$INFO[ListItem.Property(silo.code)]$INFO[ListItem.Title, · ,]$INFO[ListItem.Property(silo.aired), · ,]$INFO[ListItem.Duration(mins), · , min]</value>
        <value condition="String.IsEqual(ListItem.DBType,episode)">$INFO[ListItem.Season,S,]$INFO[ListItem.Episode,E,]$INFO[ListItem.Title, · ,]$INFO[ListItem.Premiered, · ,]$INFO[ListItem.Duration(mins), · , min]</value>
        <value condition="String.IsEqual(ListItem.DBType,tvshow) + !String.IsEmpty(ListItem.Property(silo.genre))">$INFO[ListItem.Year]$INFO[ListItem.Property(silo.genre), · ,]$INFO[ListItem.Property(silo.rating), · ,]$INFO[ListItem.Property(TotalEpisodes), · , episodes]</value>
        <value condition="!String.IsEqual(ListItem.DBType,tvshow) + !String.IsEmpty(ListItem.Property(silo.genre))">$INFO[ListItem.Year]$INFO[ListItem.Property(silo.genre), · ,]$INFO[ListItem.Property(silo.rating), · ,]$INFO[ListItem.Duration(mins), · , min]</value>
        <value condition="String.IsEqual(ListItem.DBType,tvshow)">$INFO[ListItem.Year]$INFO[ListItem.Genre, · ,]$VAR[SiloDetailRating]$VAR[SiloDetailSeasons]</value>
        <value>$INFO[ListItem.Year]$INFO[ListItem.Genre, · ,]$VAR[SiloDetailRating]$INFO[ListItem.Duration(mins), · , min]</value>
    </variable>
    <variable name="SiloDetailPlot">
        <value condition="Control.HasFocus(64) | [Control.HasFocus(65) + Integer.IsGreater(Container(64).NumItems,0)]">$INFO[Container(64).ListItem.Title,, · ]$INFO[Container(64).ListItem.Plot]</value>
        <value condition="Control.HasFocus(61) | [Control.HasFocus(60) + Integer.IsGreater(Container(61).NumItems,0)]">$INFO[Container(61).ListItem.Title,, · ]$INFO[Container(61).ListItem.Plot]</value>
        <value condition="String.IsEqual(ListItem.DBType,episode)">$INFO[ListItem.Title,, · ]$INFO[ListItem.Plot]</value>
        <value>$INFO[ListItem.Plot]</value>
    </variable>
    <variable name="SiloDetailTech">
        <value condition="Control.HasFocus(64) | [Control.HasFocus(65) + Integer.IsGreater(Container(64).NumItems,0)]">$INFO[Container(64).ListItem.VideoResolution,[COLOR 8CEDEDED]VERSION[/COLOR]  ,]$VAR[SiloFocusHdr]          [COLOR 8CEDEDED]AUDIO[/COLOR]  $VAR[SiloFocusAudio]</value>
        <value condition="Control.HasFocus(61) | [Control.HasFocus(60) + Integer.IsGreater(Container(61).NumItems,0)]">$INFO[Container(61).ListItem.VideoResolution,[COLOR 8CEDEDED]VERSION[/COLOR]  ,]$VAR[SiloFocusHdr61]          [COLOR 8CEDEDED]AUDIO[/COLOR]  $VAR[SiloFocusAudio61]</value>
        <value>$INFO[ListItem.Property(silo.version),[COLOR 8CEDEDED]VERSION[/COLOR]  ,          ]$INFO[ListItem.Property(silo.audio),[COLOR 8CEDEDED]AUDIO[/COLOR]  ,          ]$INFO[ListItem.Property(silo.subtitles),[COLOR 8CEDEDED]SUBTITLES[/COLOR]  ,]</value>
    </variable>
    <!-- The episode row's focused card: its formats, as the tech line names them. -->
    <variable name="SiloFocusHdr">
        <value condition="String.IsEqual(Container(64).ListItem.HdrType,dolbyvision)"> · Dolby Vision</value>
        <value condition="String.IsEqual(Container(64).ListItem.HdrType,hdr10plus)"> · HDR10+</value>
        <value condition="String.IsEqual(Container(64).ListItem.HdrType,hdr10)"> · HDR10</value>
        <value condition="String.IsEqual(Container(64).ListItem.HdrType,hlg)"> · HLG</value>
    </variable>
    <variable name="SiloFocusHdr61">
        <value condition="String.IsEqual(Container(61).ListItem.HdrType,dolbyvision)"> · Dolby Vision</value>
        <value condition="String.IsEqual(Container(61).ListItem.HdrType,hdr10plus)"> · HDR10+</value>
        <value condition="String.IsEqual(Container(61).ListItem.HdrType,hdr10)"> · HDR10</value>
        <value condition="String.IsEqual(Container(61).ListItem.HdrType,hlg)"> · HLG</value>
    </variable>
    <variable name="SiloFocusAudio">
        <value condition="String.IsEqual(Container(64).ListItem.AudioCodec,eac3_ddp_atmos)">EAC3 Atmos$VAR[SiloFocusLayout]</value>
        <value condition="String.IsEqual(Container(64).ListItem.AudioCodec,truehd_atmos)">TrueHD Atmos$VAR[SiloFocusLayout]</value>
        <value condition="String.IsEqual(Container(64).ListItem.AudioCodec,dtshd_ma)">DTS-HD MA$VAR[SiloFocusLayout]</value>
        <value condition="String.IsEqual(Container(64).ListItem.AudioCodec,dca)">DTS$VAR[SiloFocusLayout]</value>
        <value>[UPPERCASE]$INFO[Container(64).ListItem.AudioCodec][/UPPERCASE]$VAR[SiloFocusLayout]</value>
    </variable>
    <variable name="SiloFocusAudio61">
        <value condition="String.IsEqual(Container(61).ListItem.AudioCodec,eac3_ddp_atmos)">EAC3 Atmos$VAR[SiloFocusLayout61]</value>
        <value condition="String.IsEqual(Container(61).ListItem.AudioCodec,truehd_atmos)">TrueHD Atmos$VAR[SiloFocusLayout61]</value>
        <value condition="String.IsEqual(Container(61).ListItem.AudioCodec,dtshd_ma)">DTS-HD MA$VAR[SiloFocusLayout61]</value>
        <value condition="String.IsEqual(Container(61).ListItem.AudioCodec,dca)">DTS$VAR[SiloFocusLayout61]</value>
        <value>[UPPERCASE]$INFO[Container(61).ListItem.AudioCodec][/UPPERCASE]$VAR[SiloFocusLayout61]</value>
    </variable>
    <variable name="SiloFocusLayout">
        <value condition="Integer.IsEqual(Container(64).ListItem.AudioChannels,2)"> · 2.0</value>
        <value condition="Integer.IsEqual(Container(64).ListItem.AudioChannels,6)"> · 5.1</value>
        <value condition="Integer.IsEqual(Container(64).ListItem.AudioChannels,8)"> · 7.1</value>
        <value>$INFO[Container(64).ListItem.AudioChannels, · , ch]</value>
    </variable>
    <variable name="SiloFocusLayout61">
        <value condition="Integer.IsEqual(Container(61).ListItem.AudioChannels,2)"> · 2.0</value>
        <value condition="Integer.IsEqual(Container(61).ListItem.AudioChannels,6)"> · 5.1</value>
        <value condition="Integer.IsEqual(Container(61).ListItem.AudioChannels,8)"> · 7.1</value>
        <value>$INFO[Container(61).ListItem.AudioChannels, · , ch]</value>
    </variable>
    <variable name="SiloDetailCredit">
        <value condition="!String.IsEqual(ListItem.DBType,movie) + !String.IsEmpty(ListItem.Property(silo.cast))">Starring $INFO[ListItem.Property(silo.cast)]</value>
        <value condition="!String.IsEmpty(ListItem.Director)">Directed by $INFO[ListItem.Director]</value>
        <value condition="!String.IsEmpty(ListItem.Property(silo.cast))">Starring $INFO[ListItem.Property(silo.cast)]</value>
        <value>$INFO[ListItem.Studio]</value>
    </variable>
    <variable name="SiloDetailPlayLabel">
        <value condition="String.IsEqual(ListItem.DBType,tvshow) | String.IsEqual(ListItem.DBType,season)">$LOCALIZE[1024]</value>
        <value condition="String.IsEqual(ListItem.DBType,episode) + ListItem.IsResumable">Resume S$INFO[ListItem.Season]:E$INFO[ListItem.Episode]</value>
        <value condition="String.IsEqual(ListItem.DBType,episode)">Play S$INFO[ListItem.Season]:E$INFO[ListItem.Episode]</value>
        <value condition="ListItem.IsResumable">Resume</value>
        <value>$LOCALIZE[208]</value>
    </variable>
    <variable name="SiloDetailResolutionSuffix">
        <value condition="String.IsEqual(ListItem.VideoResolution,4K)"></value>
        <value>P</value>
    </variable>
    <!-- On the watchlist: a toggle on this page (SiloKodiConnect sets
         Window(movieinformation) silo.watchlist.for/.now), else as it opened. -->
    <expression name="SiloOnWatchlist">[String.IsEqual(Window(movieinformation).Property(silo.watchlist.for),ListItem.Property(silo.content_id)) + String.IsEqual(Window(movieinformation).Property(silo.watchlist.now),true)] | [!String.IsEqual(Window(movieinformation).Property(silo.watchlist.for),ListItem.Property(silo.content_id)) + String.IsEqual(ListItem.Property(silo.watchlist),true)]</expression>
    <variable name="SiloWatchlistIcon">
        <value condition="$EXP[SiloOnWatchlist]">silo/menu_watchlist.png</value>
        <value>silo/menu_watchlist_add.png</value>
    </variable>
    <variable name="SiloDetailHdr">
        <value condition="String.IsEqual(ListItem.HdrType,dolbyvision)">DOLBY VISION</value>
        <value condition="String.IsEqual(ListItem.HdrType,hdr10plus)">HDR10+</value>
        <value condition="String.IsEqual(ListItem.HdrType,hdr10)">HDR10</value>
        <value condition="String.IsEqual(ListItem.HdrType,hlg)">HLG</value>
        <value>$INFO[ListItem.HdrType]</value>
    </variable>
    <!-- Kodi's stream details as Silo's badge: "DTS 5.1", not "dts 6". -->
    <variable name="SiloDetailAudio">
        <value>$VAR[SiloDetailAudioCodec]$VAR[SiloDetailAudioLayout]</value>
    </variable>
    <variable name="SiloDetailAudioCodec">
        <value condition="String.IsEqual(ListItem.AudioCodec,eac3_ddp_atmos) | String.IsEqual(ListItem.AudioCodec,truehd_atmos)">ATMOS</value>
        <value condition="String.IsEqual(ListItem.AudioCodec,eac3)">DD+</value>
        <value condition="String.IsEqual(ListItem.AudioCodec,ac3)">DD</value>
        <value condition="String.IsEqual(ListItem.AudioCodec,truehd)">TRUEHD</value>
        <value condition="String.IsEqual(ListItem.AudioCodec,dtshd_ma)">DTS-HD MA</value>
        <value condition="String.IsEqual(ListItem.AudioCodec,dtshd_hra)">DTS-HD</value>
        <value condition="String.IsEqual(ListItem.AudioCodec,dca)">DTS</value>
        <value condition="String.IsEqual(ListItem.AudioCodec,dts)">DTS</value>
        <value condition="String.IsEqual(ListItem.AudioCodec,aac)">AAC</value>
        <value condition="String.IsEqual(ListItem.AudioCodec,flac)">FLAC</value>
        <value condition="String.IsEqual(ListItem.AudioCodec,opus)">OPUS</value>
        <value condition="String.IsEqual(ListItem.AudioCodec,mp3)">MP3</value>
        <value condition="String.IsEqual(ListItem.AudioCodec,pcm)">PCM</value>
        <value>$INFO[ListItem.AudioCodec]</value>
    </variable>
    <variable name="SiloDetailAudioLayout">
        <value condition="Integer.IsEqual(ListItem.AudioChannels,1)"> 1.0</value>
        <value condition="Integer.IsEqual(ListItem.AudioChannels,2)"> 2.0</value>
        <value condition="Integer.IsEqual(ListItem.AudioChannels,6)"> 5.1</value>
        <value condition="Integer.IsEqual(ListItem.AudioChannels,8)"> 7.1</value>
        <value>$INFO[ListItem.AudioChannels, ,]</value>
    </variable>
    <!-- The rating named by its source, as Silo shows it (SiloKodiConnect stores
         IMDb's, else TMDB's). -->
    <variable name="SiloDetailRating">
        <value condition="!String.IsEmpty(ListItem.Rating(imdb))">$INFO[ListItem.Rating(imdb), · [COLOR BFEDEDED]IMDb[/COLOR] [B],[/B]]</value>
        <value condition="!String.IsEmpty(ListItem.Rating(themoviedb))">$INFO[ListItem.Rating(themoviedb), · [COLOR BFEDEDED]TMDB[/COLOR] [B],[/B]]</value>
        <value>$INFO[ListItem.Rating, · ★ ,]</value>
    </variable>
    <variable name="SiloDetailSeasons">
        <value condition="Integer.IsEqual(ListItem.Property(TotalSeasons),1)"> · 1 Season</value>
        <value condition="Integer.IsGreater(ListItem.Property(TotalSeasons),1)">$INFO[ListItem.Property(TotalSeasons), · , Seasons]</value>
        <!-- Kodi gives this page no TotalSeasons: count its season pills. -->
        <value condition="String.IsEqual(ListItem.DBType,tvshow) + Integer.IsEqual(Container(60).NumItems,1)"> · 1 Season</value>
        <value condition="String.IsEqual(ListItem.DBType,tvshow) + Integer.IsGreater(Container(60).NumItems,1)">$INFO[Container(60).NumItems, · , Seasons]</value>
    </variable>
    <!-- Silo's first two genres ("Drama, Crime"), from SiloKodiConnect. -->
    <!-- More's menu: its heading, and its rows' names (a show's are for every episode). -->
    <variable name="SiloMoreHeading">
        <value condition="String.IsEqual(Window(Home).Property(silo.more.type),tvshow)">Series</value>
        <value condition="String.IsEqual(Window(Home).Property(silo.more.type),episode)">Episode</value>
        <value>Film</value>
    </variable>
    <variable name="SiloMoreWatched">
        <value condition="String.IsEqual(Window(Home).Property(silo.more.type),tvshow)">Mark series as watched</value>
        <value>Mark as watched</value>
    </variable>
    <variable name="SiloMoreUnwatched">
        <value condition="String.IsEqual(Window(Home).Property(silo.more.type),tvshow)">Mark series as unwatched</value>
        <value>Mark as unwatched</value>
    </variable>
    <variable name="SiloDetailGenres">
        <value condition="!String.IsEmpty(ListItem.Property(silo.genres))">$INFO[ListItem.Property(silo.genres), · ,]</value>
        <value>$INFO[ListItem.Property(silo.genre), · ,]</value>
    </variable>
    <!-- An episode card's code, as Silo writes it: S01E01. -->
    <variable name="SiloEpisodeCode">
        <value condition="Integer.IsLess(ListItem.Season,10) + Integer.IsLess(ListItem.Episode,10)">S0$INFO[ListItem.Season]E0$INFO[ListItem.Episode]</value>
        <value condition="Integer.IsLess(ListItem.Season,10)">S0$INFO[ListItem.Season]E$INFO[ListItem.Episode]</value>
        <value condition="Integer.IsLess(ListItem.Episode,10)">S$INFO[ListItem.Season]E0$INFO[ListItem.Episode]</value>
        <value>S$INFO[ListItem.Season]E$INFO[ListItem.Episode]</value>
    </variable>
    <variable name="SiloDetailNextLabel">
        <value condition="[Integer.IsGreater(Container(61).NumItems,0) + !String.IsEqual(Container(61).ListItemAbsolute(0).Season,Container(62).ListItem.Season)]">Play S$INFO[Container(61).ListItemAbsolute(0).Season]:E$INFO[Container(61).ListItemAbsolute(0).Episode]</value>
        <value condition="Integer.IsGreater(Container(62).NumItems,0) + Integer.IsGreater(Container(62).ListItem.PercentPlayed,0)">Resume S$INFO[Container(62).ListItem.Season]:E$INFO[Container(62).ListItem.Episode]</value>
        <value condition="Integer.IsGreater(Container(62).NumItems,0)">Play S$INFO[Container(62).ListItem.Season]:E$INFO[Container(62).ListItem.Episode]</value>
        <value condition="Container(62).IsUpdating">$LOCALIZE[208]</value>
        <value>$LOCALIZE[1024]</value>
    </variable>
    <variable name="SiloEpisodeSeason">
        <value condition="Integer.IsEqual(ListItem.Season,0)">Specials</value>
        <value>Season $INFO[ListItem.Season]</value>
    </variable>
    <variable name="SiloSeasonLabel">
        <value condition="String.StartsWith(ListItem.Label,*)">All episodes</value>
        <value>$INFO[ListItem.Label]</value>
    </variable>
    <!-- end Silo Skyline detail -->
'''


FACTS_DOT = '  [COLOR 80EDEDED]·[/COLOR]  '


def rating_mark(source):
    # The score's info label alone: no brackets, so it can't reach back into the labels before it.
    return re.compile(r'\$INFO\[([^,\[\]$]+), · \[COLOR BFEDEDED\]%s\[/COLOR\] \[B\],\[/B\]\]' % source)


IMDB_MARK, TMDB_MARK = rating_mark('IMDb'), rating_mark('TMDB')


def split_ratings(variables):
    """The facts line around the rating sources' marks (images): SiloDetailFacts
    up to IMDb's, SiloDetailFactsImdb from its score up to TMDB's,
    SiloDetailFactsTmdb from that score on; and when each mark shows (the
    value Kodi picks has that score)."""
    block = re.search(r'    <variable name="SiloDetailFacts">\n(.*?)    </variable>\n', variables, re.S)
    parts = ([], [], [])
    shown = {'imdb': [], 'tmdb': []}
    earlier = []
    for condition, value in re.findall(r'        <value(?: condition="([^"]*)")?>(.*)</value>\n', block.group(1)):
        attribute = ' condition="%s"' % condition if condition else ''
        imdb, tmdb = IMDB_MARK.search(value), TMDB_MARK.search(value)
        pieces = ['', '', '']
        rest = value
        if tmdb:
            pieces[2] = '$INFO[%s,  [B],[/B]]%s' % (tmdb.group(1), rest[tmdb.end():])
            rest = rest[:tmdb.start()]
        if imdb:
            pieces[1] = '$INFO[%s,  [B],[/B]]%s' % (imdb.group(1), rest[imdb.end():])
            rest = rest[:imdb.start()]
        pieces[0] = rest
        for part, piece in zip(parts, pieces):
            part.append('        <value%s>%s</value>\n' % (attribute, piece))
        for key, mark in (('imdb', imdb), ('tmdb', tmdb)):
            if mark:
                terms = (['[%s]' % condition] if condition else []) + ['![%s]' % c for c in earlier] + \
                    ['!String.IsEmpty(%s)' % mark.group(1)]
                shown[key].append('[%s]' % ' + '.join(terms))
        if condition:
            earlier.append(condition)
    replaced = ''.join('    <variable name="%s">\n%s    </variable>\n' % (name, ''.join(part)) for name, part in
                       zip(('SiloDetailFacts', 'SiloDetailFactsImdb', 'SiloDetailFactsTmdb'), parts))
    variables = variables.replace(block.group(0), replaced)
    # Silo's facts separator: a dim dot in wide gaps (measured on its Apple TV app).
    for name in ('SiloDetailFacts', 'SiloDetailFactsImdb', 'SiloDetailFactsTmdb', 'SiloDetailSeasons',
                 'SiloDetailGenres', 'SiloDetailRating'):
        found = re.search(r'    <variable name="%s">\n.*?    </variable>\n' % name, variables, re.S).group(0)
        variables = variables.replace(found, found.replace(' · ', FACTS_DOT))
    return (variables,
            ' | '.join(shown['imdb']) or 'false', ' | '.join(shown['tmdb']) or 'false')


def add_variables():
    path = os.path.join(ROOT, 'xml', 'Variables.xml')
    text = open(path, encoding='utf-8').read()
    start, end = '    <!-- Silo Skyline detail (tools/build_info.py) -->', '    <!-- end Silo Skyline detail -->\n'
    if start in text:
        text = text[:text.index(start) - 1] + text[text.index(end) + len(end):]
    text = text.replace('</includes>', split_ratings(VARIABLES)[0] + '</includes>')
    open(path, 'w', encoding='utf-8').write(text)


JUMP = 'Window(movieinformation).Property(silo.jump)'
# A show's page with a season chosen other than its next episode's (or with
# no next episode): Play plays that season's first episode.
OTHER_SEASON = ('[Integer.IsGreater(Container(61).NumItems,0) + '
                '!String.IsEqual(Container(61).ListItemAbsolute(0).Season,Container(62).ListItem.Season)]')
NEXT = 'Container(62).ListItem'
MAX_SEASONS, MAX_EPISODES = 40, 60


def jump_timers():
    """Two skin timers that open a show's page on its next episode, as Silo
    does: once the season pills have loaded, select the next episode's season
    (by its number, so an "All seasons" or Specials pill doesn't throw it off);
    once that season's episodes have loaded, select the episode by its number.
    Focus goes back to Play/Resume each time, and each runs once per opening
    (silo.jump), never while you are moving around the page."""
    page = 'Window.IsActive(movieinformation) + Control.HasFocus(300)'
    loaded = 'Integer.IsGreater(Container(%d).NumItems,0) + !Container(%d).IsUpdating'

    def timer(name, start, actions):
        return ('    <timer>\n        <name>%s</name>\n'
                '        <description>Open a show\'s page on its next episode (tools/build_info.py)</description>\n'
                '        <start reset="true">%s</start>\n'
                '        <stop>Integer.IsGreaterOrEqual(Skin.TimerElapsedSecs(%s),0)</stop>\n%s    </timer>\n'
                % (name, start, name, ''.join('        <onstop condition="Window.IsActive(movieinformation)%s">%s</onstop>\n'
                                              % (' + ' + c if c else '', action) for c, action in actions)))
    season = timer('silo_next_season',
                   '%s + %s + %s + String.IsEmpty(%s)' % (page, loaded % (62, 62), loaded % (60, 60), JUMP),
                   [('String.IsEqual(Container(60).ListItemAbsolute(%d).Season,%s.Season)' % (k, NEXT),
                     'SetFocus(60,%d,absolute)' % k) for k in range(MAX_SEASONS)]
                   + [('', 'SetProperty(silo.jump,season,movieinformation)'), ('', 'SetFocus(300)')])
    episode = timer('silo_next_episode',
                    '%s + String.IsEqual(%s,season) + %s + String.IsEqual(Container(61).ListItemAbsolute(0).Season,%s.Season)'
                    % (page, JUMP, loaded % (61, 61), NEXT),
                    [('String.IsEqual(Container(61).ListItemAbsolute(%d).Episode,%s.Episode)' % (k, NEXT),
                      'SetFocus(61,%d,absolute)' % k) for k in range(MAX_EPISODES)]
                    + [('', 'SetProperty(silo.jump,done,movieinformation)'), ('', 'SetFocus(300)')])
    # An episode's page: select its season's pill (when there are pills),
    # then the opened episode in the rail.
    episode_page = 'Window.IsActive(movieinformation) + Control.HasFocus(308)'
    opened_season = timer('silo_this_season',
                          '%s + String.IsEmpty(%s) + %s + Integer.IsGreater(Container(65).NumItems,1)'
                          % (episode_page, JUMP, loaded % (65, 65)),
                          [('String.IsEqual(Container(65).ListItemAbsolute(%d).Season,'
                            'Window(movieinformation).Property(silo.episode_season))' % k,
                            'SetFocus(65,%d,absolute)' % k) for k in range(MAX_SEASONS)]
                          + [('', 'SetProperty(silo.jump,episode_season,movieinformation)'), ('', 'SetFocus(308)')])
    opened = timer('silo_this_episode',
                   '%s + [String.IsEmpty(%s) + !Integer.IsGreater(Container(65).NumItems,1) | '
                   'String.IsEqual(%s,episode_season)] + %s + String.IsEqual(Container(64).ListItemAbsolute(0).Season,'
                   'Window(movieinformation).Property(silo.episode_season))'
                   % (episode_page, JUMP, JUMP, loaded % (64, 64)),
                   [('String.IsEqual(Container(64).ListItemAbsolute(%d).Episode,'
                     'Window(movieinformation).Property(silo.episode_number))' % k, 'SetFocus(64,%d,absolute)' % k)
                    for k in range(MAX_EPISODES)]
                   + [('', 'SetProperty(silo.jump,done,movieinformation)'), ('', 'SetFocus(308)')])
    return TIMER_START + season + episode + opened_season + opened + TIMER_END


TIMER_START, TIMER_END = '    <!-- Silo Skyline detail (tools/build_info.py) -->\n', '    <!-- end Silo Skyline detail -->\n'


def add_timers():
    path = os.path.join(ROOT, 'xml', 'Timers.xml')
    text = open(path, encoding='utf-8').read()
    if TIMER_START in text:
        text = text[:text.index(TIMER_START)] + text[text.index(TIMER_END) + len(TIMER_END):]
    text = text.replace('</timers>', jump_timers() + '</timers>')
    open(path, 'w', encoding='utf-8').write(text)


# The action row's buttons in order, with the control whose visibility counts
# (round buttons and Play sit in groups, which Kodi's grouplist can't move
# between, so each button names its neighbours).
ACTIONS = [(300, 300), (301, 301), (308, 1008), (304, 1304), (302, 1302), (11, 1011), (351, 1351), (352, 1352),
           (14, 1014), (303, 1303)]


def with_action_moves(xml):
    # Down (and Up) as the action row's own: Kodi moves from the focused
    # button, and a button inside a group has none of its own.
    row = re.search(r'<control type="grouplist" id="5000">(.*?)<control type="button"', xml, re.S).group(1)
    vertical = ''.join('\n                    ' + move for move in re.findall(r'<(?:ondown|onup)[^>]*>[^<]*</(?:ondown|onup)>', row))
    for index, (control_id, _) in enumerate(ACTIONS):
        moves = vertical
        for action, others in (('onright', ACTIONS[index + 1:]), ('onleft', ACTIONS[:index][::-1])):
            skipped = []
            for target, shown in others:
                condition = ' + '.join(['Control.IsVisible(%d)' % shown] +
                                       ['!Control.IsVisible(%d)' % k for k in skipped])
                moves += '\n                    <%s condition="%s">SetFocus(%d)</%s>' % (action, condition, target, action)
                skipped.append(shown)
        opening = '<control type="button" id="%d">' % control_id
        assert xml.count(opening) == 1, control_id
        xml = xml.replace(opening, opening + moves)
    return xml


if __name__ == '__main__':
    with open(os.path.join(ROOT, 'xml', 'DialogVideoInfo.xml'), 'w', encoding='utf-8') as handle:
        handle.write(with_action_moves(build()))
    with open(os.path.join(ROOT, 'xml', 'Custom_%d_SiloMore.xml' % MORE_WINDOW), 'w', encoding='utf-8') as handle:
        handle.write(more_menu())
    add_variables()
    add_timers()
    print('Wrote xml/DialogVideoInfo.xml, its variables in xml/Variables.xml and its timers in xml/Timers.xml')
