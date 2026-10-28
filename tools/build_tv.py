#!/usr/bin/env python3
"""Generate Skyline's TV guide (xml/MyPVRGuide.xml) and programme information
(xml/DialogPVRInfo.xml), the guide as TiviMate lays one out
in Silo's look:

    python3 tools/build_tv.py

The focused programme at the top (channel, title, time, progress, plot) with
a preview of what's playing at the right; the channel groups as Silo's
pills; then the timeline: channels down the left, programmes across, the
focused one a white bar, a white line at the current time. Kodi fills the
groups (control 11) and the grid; the bar's TV tab opens it (Live TV only).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_home import BACKGROUND, ROOT, SAFE_X, TEXT  # noqa: E402

GROUPS_ID, GRID_ID = 11, 51
DIM = '99EDEDED'
TOP_H = 410                 # the programme's details and the preview
PILLS_Y = TOP_H + 6
GRID_Y = PILLS_Y + 76
CHANNEL_W = 440
ROW_H = 76
RULER_H = 46
PREVIEW_W, PREVIEW_H = 608, 342
BLOCK_W = 60                # a 5-minute block


def channel(focused):
    """A channel down the left: logo, number and name; the focused row's
    channel lit while the grid has focus."""
    colour = TEXT if focused else 'C7EDEDED'
    return '''
                    <control type="image">
                        <left>%(x)d</left><top>8</top><width>%(w)d</width><height>%(h)d</height>
                        <texture border="20" colordiffuse="%(fill)s">silo/card_landscape_mask.png</texture>
                    </control>
                    <control type="image">
                        <left>%(lx)d</left><top>14</top><width>96</width><height>56</height>
                        <aspectratio>keep</aspectratio>
                        <texture fallback="DefaultTVShows.png">$INFO[ListItem.Icon]</texture>
                    </control>
                    <control type="label">
                        <left>%(tx)d</left><top>10</top><width>%(tw)d</width><height>32</height>
                        <font>silo_detail</font>
                        <textcolor>%(dim)s</textcolor>
                        <selectedcolor>%(dim)s</selectedcolor>
                        <label>$INFO[ListItem.ChannelNumberLabel]</label>
                    </control>
                    <control type="label">
                        <left>%(tx)d</left><top>40</top><width>%(tw)d</width><height>34</height>
                        <font>silo_detail</font>
                        <textcolor>%(colour)s</textcolor>
                        <selectedcolor>%(colour)s</selectedcolor>
                        <label>$INFO[ListItem.Label]</label>
                    </control>''' % {'x': SAFE_X - 6, 'w': CHANNEL_W - SAFE_X + 2, 'h': ROW_H - 12,
                                     'fill': '1FFFFFFF' if focused else '0DFFFFFF', 'lx': SAFE_X + 6,
                                     'tx': SAFE_X + 116, 'tw': CHANNEL_W - SAFE_X - 124, 'dim': DIM, 'colour': colour}


def programme(focused):
    """A programme: a dark rounded block with its title; focused, a white bar
    with dark text (Silo's focus) while the grid has focus. Kodi stretches
    only the image with id 2 and the label with id 1 to the programme's
    length, so the block's colour and the title's come from variables."""
    return '''
                    <control type="image" id="2">
                        <left>3</left><top>6</top><width>%(w)d</width><height>%(h)d</height>
                        <texture border="16" colordiffuse="%(fill)s">silo/card_landscape_mask.png</texture>
                    </control>
                    <control type="label" id="1">
                        <left>18</left><top>6</top><width>%(lw)d</width><height>%(h)d</height>
                        <aligny>center</aligny>
                        <font>silo_detail</font>
                        <label>%(label)s</label>
                    </control>''' % {'w': BLOCK_W - 6, 'lw': BLOCK_W - 30, 'h': ROW_H - 12,
                                      'fill': '$VAR[SiloGuideCell]' if focused else '17FFFFFF',
                                      'label': '$VAR[SiloGuideTitle]' if focused else '$VAR[SiloGuideTitleRest]'}


def variables():
    """The focused programme's block and title: white with dark text while
    the grid has focus, as the others otherwise."""
    lit = 'Control.HasFocus(%d)' % GRID_ID
    return ('    <!-- Silo Skyline TV guide (tools/build_tv.py) -->\n'
            '    <variable name="SiloGuideCell">\n'
            '        <value condition="%(lit)s">%(text)s</value>\n'
            '        <value>17FFFFFF</value>\n'
            '    </variable>\n'
            # A channel with no guide data: "No information", as TiviMate.
            '    <variable name="SiloGuideTitle">\n'
            '        <value condition="%(lit)s + String.IsEmpty(ListItem.Label)">[COLOR B3000000]No information[/COLOR]</value>\n'
            '        <value condition="%(lit)s">[COLOR FF000000]$INFO[ListItem.Label][/COLOR]</value>\n'
            '        <value condition="String.IsEmpty(ListItem.Label)">[COLOR 80EDEDED]No information[/COLOR]</value>\n'
            '        <value>[COLOR D9EDEDED]$INFO[ListItem.Label][/COLOR]</value>\n'
            '    </variable>\n'
            '    <variable name="SiloGuideTitleRest">\n'
            '        <value condition="String.IsEmpty(ListItem.Label)">[COLOR 80EDEDED]No information[/COLOR]</value>\n'
            '        <value>[COLOR D9EDEDED]$INFO[ListItem.Label][/COLOR]</value>\n'
            '    </variable>\n'
            ) % {'lit': lit, 'text': TEXT} + quick_variables() + '    <!-- end Silo Skyline TV guide -->\n'


def add_variables():
    path = os.path.join(ROOT, 'xml', 'Variables.xml')
    text = open(path, encoding='utf-8').read()
    start, end = '    <!-- Silo Skyline TV guide (tools/build_tv.py) -->', '    <!-- end Silo Skyline TV guide -->\n'
    if start in text:
        text = text[:text.index(start)] + text[text.index(end) + len(end):]
    open(path, 'w', encoding='utf-8').write(text.replace('</includes>', variables() + '</includes>'))


def group_pill(focused):
    """A channel group: Silo's pill, the chosen group outlined, the focused
    one white."""
    chosen = 'ListItem.IsSelected'
    if focused:
        return '''
                    <control type="image">
                        <width>300</width><height>52</height>
                        <texture border="26" colordiffuse="%(text)s">silo/pill.png</texture>
                        <visible>Control.HasFocus(%(id)d)</visible>
                    </control>
                    <control type="label">
                        <left>22</left><width>256</width><height>52</height>
                        <align>center</align><aligny>center</aligny>
                        <font>silo_detail</font>
                        <textcolor>FF000000</textcolor>
                        <selectedcolor>FF000000</selectedcolor>
                        <label>$INFO[ListItem.Label]</label>
                        <visible>Control.HasFocus(%(id)d)</visible>
                    </control>
                    <control type="image">
                        <width>300</width><height>52</height>
                        <texture border="28" colordiffuse="D9FFFFFF">silo/season_ring.png</texture>
                        <visible>!Control.HasFocus(%(id)d)</visible>
                    </control>
                    <control type="label">
                        <left>22</left><width>256</width><height>52</height>
                        <align>center</align><aligny>center</aligny>
                        <font>silo_detail</font>
                        <textcolor>%(text)s</textcolor>
                        <selectedcolor>%(text)s</selectedcolor>
                        <label>$INFO[ListItem.Label]</label>
                        <visible>!Control.HasFocus(%(id)d)</visible>
                    </control>''' % {'text': TEXT, 'id': GROUPS_ID}
    return '''
                    <control type="image">
                        <width>300</width><height>52</height>
                        <texture border="26" colordiffuse="2EFFFFFF">silo/pill.png</texture>
                        <visible>!%(chosen)s</visible>
                    </control>
                    <control type="image">
                        <width>300</width><height>52</height>
                        <texture border="28" colordiffuse="D9FFFFFF">silo/season_ring.png</texture>
                        <visible>%(chosen)s</visible>
                    </control>
                    <control type="label">
                        <left>22</left><width>256</width><height>52</height>
                        <align>center</align><aligny>center</aligny>
                        <font>silo_detail</font>
                        <textcolor>%(dim)s</textcolor>
                        <selectedcolor>%(dim)s</selectedcolor>
                        <label>$INFO[ListItem.Label]</label>
                    </control>''' % {'chosen': chosen, 'dim': DIM}


def build():
    grid_h = 1080 - GRID_Y
    return '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by tools/build_tv.py: edit that, not this. -->
<window>
    <defaultcontrol always="true">%(grid)d</defaultcontrol>
    <views>%(grid)d</views>
    <backgroundcolor>%(background)s</backgroundcolor>
    <controls>
        <control type="image">
            <left>0</left><top>0</top><width>1920</width><height>1080</height>
            <texture colordiffuse="%(background)s">colors/white.png</texture>
        </control>

        <!-- The focused programme, as TiviMate's guide shows it. -->
        <control type="group">
            <left>%(x)d</left><top>52</top>
            <control type="grouplist">
                <width>1000</width><height>56</height>
                <orientation>horizontal</orientation>
                <itemgap>16</itemgap>
                <control type="image">
                    <width>96</width><height>56</height>
                    <aspectratio align="left">keep</aspectratio>
                    <texture>$INFO[ListItem.ChannelLogo]</texture>
                    <visible>!String.IsEmpty(ListItem.ChannelLogo)</visible>
                </control>
                <control type="label">
                    <width>auto</width><height>56</height>
                    <aligny>center</aligny>
                    <font>silo_meta</font>
                    <textcolor>%(dim)s</textcolor>
                    <selectedcolor>%(dim)s</selectedcolor>
                    <label>$INFO[ListItem.ChannelNumberLabel,,  ·  ]$INFO[ListItem.ChannelName]</label>
                </control>
            </control>
            <control type="label">
                <top>72</top><width>1050</width><height>64</height>
                <font>silo_osd_title</font>
                <textcolor>%(text)s</textcolor>
                <selectedcolor>%(text)s</selectedcolor>
                <label>$INFO[ListItem.Label]</label>
            </control>
            <control type="grouplist">
                <top>146</top><width>1050</width><height>36</height>
                <orientation>horizontal</orientation>
                <itemgap>18</itemgap>
                <control type="label">
                    <width>auto</width><height>36</height>
                    <aligny>center</aligny>
                    <font>silo_meta</font>
                    <textcolor>%(text)s</textcolor>
                    <selectedcolor>%(text)s</selectedcolor>
                    <label>$INFO[ListItem.StartTime]$INFO[ListItem.EndTime, – ,]$INFO[ListItem.Genre,  ·  ,]</label>
                </control>
                <!-- On now: how far through, as Silo's progress bars. -->
                <control type="progress">
                    <top>15</top><width>180</width><height>6</height>
                    <texturebg colordiffuse="33FFFFFF">colors/white.png</texturebg>
                    <midtexture colordiffuse="%(text)s">colors/white.png</midtexture>
                    <info>ListItem.Progress</info>
                    <visible>Integer.IsGreater(ListItem.Progress,0) + Integer.IsLess(ListItem.Progress,100)</visible>
                </control>
            </control>
            <control type="textbox">
                <top>196</top><width>1050</width><height>140</height>
                <font>silo_plot</font>
                <textcolor>B3EDEDED</textcolor>
                <selectedcolor>B3EDEDED</selectedcolor>
                <label>$INFO[ListItem.Plot]</label>
                <autoscroll>false</autoscroll>
            </control>
        </control>

        <!-- At the right: what's playing (TiviMate's preview), else the
             programme's or channel's picture. -->
        <control type="group">
            <left>%(px)d</left><top>52</top>
            <control type="image">
                <width>%(pw)d</width><height>%(ph)d</height>
                <texture border="20" colordiffuse="FF000000">silo/card_landscape_mask.png</texture>
            </control>
            <control type="videowindow">
                <width>%(pw)d</width><height>%(ph)d</height>
                <visible>Player.HasVideo</visible>
            </control>
            <control type="image">
                <width>%(pw)d</width><height>%(ph)d</height>
                <aspectratio>keep</aspectratio>
                <texture background="true" diffuse="silo/card_landscape_mask.png">$INFO[ListItem.Icon]</texture>
                <visible>!Player.HasVideo</visible>
            </control>
        </control>
        <control type="label">
            <right>%(x)d</right><top>8</top><width>300</width><height>40</height>
            <align>right</align>
            <font>silo_meta</font>
            <textcolor>%(dim)s</textcolor>
            <selectedcolor>%(dim)s</selectedcolor>
            <label>$INFO[System.Time]</label>
        </control>

        <!-- Channel groups (Kodi fills list 11): Silo's pills. -->
        <control type="list" id="%(groups)d">
            <left>%(x)d</left><top>%(pills_y)d</top><width>%(gw)d</width><height>52</height>
            <orientation>horizontal</orientation>
            <ondown>%(grid)d</ondown>
            <scrolltime tween="cubic" easing="out">200</scrolltime>
            <itemlayout width="312" height="52">%(pill)s
            </itemlayout>
            <focusedlayout width="312" height="52">%(pill_focused)s
            </focusedlayout>
        </control>

        <!-- The timeline: channels down the left, programmes across. -->
        <control type="epggrid" id="%(grid)d">
            <left>0</left><top>%(grid_y)d</top><width>1920</width><height>%(grid_h)d</height>
            <!-- Kodi's "vertical": channels down, time across (TiviMate's timeline). -->
            <orientation>vertical</orientation>
            <viewtype label="19298">list</viewtype>
            <timeblocks>%(blocks)d</timeblocks>
            <rulerunit>6</rulerunit>
            <onup>%(groups)d</onup>
            <scrolltime tween="cubic" easing="out">240</scrolltime>
            <!-- Now: a white line at the current time, with TiviMate's dot at its top. -->
            <progresstexture border="0,16,18,0" colordiffuse="F2FFFFFF">silo/epg_now.png</progresstexture>
            <rulerlayout height="%(ruler_h)d" width="1400">
                <control type="label">
                    <left>14</left><width>%(half_hour)d</width><height>%(ruler_h)d</height>
                    <aligny>center</aligny>
                    <font>silo_detail</font>
                    <textcolor>%(dim)s</textcolor>
                    <selectedcolor>%(dim)s</selectedcolor>
                    <label>$INFO[ListItem.Label]</label>
                </control>
            </rulerlayout>
            <channellayout height="%(row_h)d" width="%(cw)d">%(channel)s
            </channellayout>
            <focusedchannellayout height="%(row_h)d" width="%(cw)d">%(channel_focused)s
            </focusedchannellayout>
            <itemlayout height="%(row_h)d" width="%(block)d">%(item)s
            </itemlayout>
            <focusedlayout height="%(row_h)d" width="%(block)d">%(item_focused)s
            </focusedlayout>
        </control>

        <!-- Kodi's labels for the window's own use. -->
        <control type="label" id="29"><visible>false</visible></control>
        <control type="label" id="30"><visible>false</visible></control>
    </controls>
</window>
''' % {'grid': GRID_ID, 'groups': GROUPS_ID, 'background': BACKGROUND, 'x': SAFE_X, 'text': TEXT, 'dim': DIM,
       'px': 1920 - SAFE_X - PREVIEW_W, 'pw': PREVIEW_W, 'ph': PREVIEW_H, 'pills_y': PILLS_Y,
       'gw': 1920 - 2 * SAFE_X, 'pill': group_pill(False), 'pill_focused': group_pill(True),
       'grid_y': GRID_Y, 'grid_h': grid_h, 'ruler_h': RULER_H, 'row_h': ROW_H, 'cw': CHANNEL_W,
       'channel': channel(False), 'channel_focused': channel(True),
       'item': programme(False), 'item_focused': programme(True),
       # 5 minutes a block, half an hour 360 px (TiviMate's scale); as many as fit.
       'block': BLOCK_W, 'half_hour': 6 * BLOCK_W, 'blocks': (1920 - CHANNEL_W) // BLOCK_W}


# Kodi's programme information buttons (DialogPVRInfo): id, label (None: Kodi
# sets it, as Record's), and when it shows.
GUIDE_INFO = 'Window.IsActive(PVRGuideInfo)'
INFO_BUTTONS = ((5, '$LOCALIZE[19165]', GUIDE_INFO),                                       # Switch
                (10, '$LOCALIZE[19190]', GUIDE_INFO),                                      # Play programme
                (8, '$LOCALIZE[19687]', GUIDE_INFO + ' | Window.IsActive(PVRRecordingInfo)'),  # Play recording
                (6, None, GUIDE_INFO),                                                     # Record
                (9, '$LOCALIZE[19061]', GUIDE_INFO),                                       # Add timer
                (11, '$LOCALIZE[826]', GUIDE_INFO),                                        # Reminder
                (4, '$LOCALIZE[19003]', GUIDE_INFO + ' | Window.IsActive(PVRRecordingInfo)'))  # Find similar


def info_button(control_id, label, visible):
    """A programme action as Silo's pill: white with dark text on focus."""
    return '''
                <control type="button" id="%(id)d">
                    <width>auto</width><height>64</height>%(label)s
                    <font>silo_tab</font>
                    <textoffsetx>36</textoffsetx>
                    <align>center</align><aligny>center</aligny>
                    <textcolor>%(text)s</textcolor>
                    <selectedcolor>%(text)s</selectedcolor>
                    <focusedcolor>FF000000</focusedcolor>
                    <texturefocus border="30" colordiffuse="%(text)s">silo/pill.png</texturefocus>
                    <texturenofocus border="30" colordiffuse="2EFFFFFF">silo/pill.png</texturenofocus>
                    <visible>%(visible)s</visible>
                </control>''' % {'id': control_id, 'text': TEXT, 'visible': visible,
                                  'label': '\n                    <label>%s</label>' % label if label else ''}


def build_info():
    """Kodi's programme information (from the guide, or a recording's), as
    Silo's details page: the channel, title, time and plot at the left, the
    programme's picture at the right, its actions as Silo's pills."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by tools/build_tv.py: edit that, not this. -->
<window>
    <defaultcontrol always="true">9000</defaultcontrol>
    <controls>
        <control type="group">
            <animation effect="fade" start="0" end="100" time="160">WindowOpen</animation>
            <animation effect="fade" start="100" end="0" time="120">WindowClose</animation>
            <control type="image">
                <left>0</left><top>0</top><width>1920</width><height>1080</height>
                <texture colordiffuse="%(background)s">colors/white.png</texture>
            </control>
            <control type="group">
                <left>%(x)d</left><top>120</top>
                <control type="grouplist">
                    <width>1000</width><height>64</height>
                    <orientation>horizontal</orientation>
                    <itemgap>18</itemgap>
                    <control type="image">
                        <width>112</width><height>64</height>
                        <aspectratio align="left">keep</aspectratio>
                        <texture>$INFO[ListItem.ChannelLogo]</texture>
                        <visible>!String.IsEmpty(ListItem.ChannelLogo)</visible>
                    </control>
                    <control type="label">
                        <width>auto</width><height>64</height>
                        <aligny>center</aligny>
                        <font>silo_meta</font>
                        <textcolor>%(dim)s</textcolor>
                        <selectedcolor>%(dim)s</selectedcolor>
                        <label>$INFO[ListItem.ChannelNumberLabel,,  ·  ]$INFO[ListItem.ChannelName]</label>
                    </control>
                </control>
                <control type="textbox">
                    <top>90</top><width>1000</width><height>132</height>
                    <font>silo_osd_title</font>
                    <textcolor>%(text)s</textcolor>
                    <selectedcolor>%(text)s</selectedcolor>
                    <label>$INFO[ListItem.Title]$INFO[ListItem.EpisodeName,[CR][COLOR B3EDEDED],[/COLOR]]</label>
                </control>
                <control type="grouplist">
                    <top>236</top><width>1000</width><height>36</height>
                    <orientation>horizontal</orientation>
                    <itemgap>18</itemgap>
                    <control type="label">
                        <width>auto</width><height>36</height>
                        <aligny>center</aligny>
                        <font>silo_meta</font>
                        <textcolor>%(text)s</textcolor>
                        <selectedcolor>%(text)s</selectedcolor>
                        <label>$INFO[ListItem.Date]$INFO[ListItem.EndTime, – ,]$INFO[ListItem.Genre,  ·  ,]</label>
                    </control>
                    <control type="progress">
                        <top>15</top><width>180</width><height>6</height>
                        <texturebg colordiffuse="33FFFFFF">colors/white.png</texturebg>
                        <midtexture colordiffuse="%(text)s">colors/white.png</midtexture>
                        <info>ListItem.Progress</info>
                        <visible>Integer.IsGreater(ListItem.Progress,0) + Integer.IsLess(ListItem.Progress,100)</visible>
                    </control>
                </control>
                <control type="textbox">
                    <top>296</top><width>1000</width><height>290</height>
                    <font>silo_plot</font>
                    <textcolor>B3EDEDED</textcolor>
                    <selectedcolor>B3EDEDED</selectedcolor>
                    <label>$INFO[ListItem.Plot]</label>
                </control>
            </control>
            <control type="group">
                <left>%(px)d</left><top>120</top>
                <control type="image">
                    <width>%(pw)d</width><height>%(ph)d</height>
                    <texture border="20" colordiffuse="FF000000">silo/card_landscape_mask.png</texture>
                </control>
                <control type="image">
                    <width>%(pw)d</width><height>%(ph)d</height>
                    <aspectratio>keep</aspectratio>
                    <texture background="true" diffuse="silo/card_landscape_mask.png" fallback="DefaultTVShows.png">$INFO[ListItem.Icon]</texture>
                </control>
            </control>
            <!-- The programme's actions (Kodi's ids: it acts on them and sets Record's label). -->
            <control type="grouplist" id="9000">
                <left>%(x)d</left><top>760</top><width>%(bw)d</width><height>64</height>
                <orientation>horizontal</orientation>
                <itemgap>16</itemgap>%(buttons)s
            </control>
        </control>
    </controls>
</window>
''' % {'x': SAFE_X, 'background': BACKGROUND, 'text': TEXT, 'dim': DIM, 'px': 1920 - SAFE_X - PREVIEW_W,
       'pw': PREVIEW_W, 'ph': PREVIEW_H, 'bw': 1920 - 2 * SAFE_X,
       'buttons': ''.join(info_button(*button) for button in INFO_BUTTONS)}


def infobar(top, left=348):
    """What's playing, as TiviMate's infobar: the channel, the programme with a
    LIVE-style tag as the guide sends it, its times, progress and minutes
    left, its description, and what's next. VideoPlayer's labels: the banner
    and the recent channels row show the same."""
    return '''
            <control type="group">
                <left>%(left)d</left><top>%(top)d</top>
                <control type="label">
                    <width>1400</width><height>36</height>
                    <font>silo_meta</font>
                    <textcolor>%(dim)s</textcolor>
                    <label>$INFO[VideoPlayer.ChannelNumberLabel,,  ·  ]$INFO[VideoPlayer.ChannelName]</label>
                </control>
                <control type="label">
                    <top>38</top><width>1400</width><height>60</height>
                    <font>silo_osd_title</font>
                    <textcolor>%(text)s</textcolor>
                    <label fallback="19055">$INFO[VideoPlayer.Title]</label>
                </control>
                <control type="grouplist">
                    <top>104</top><width>1400</width><height>36</height>
                    <orientation>horizontal</orientation>
                    <itemgap>20</itemgap>
                    <control type="label">
                        <width>auto</width><height>36</height>
                        <aligny>center</aligny>
                        <font>silo_meta</font>
                        <textcolor>%(text)s</textcolor>
                        <label>$INFO[VideoPlayer.StartTime]$INFO[VideoPlayer.EndTime, – ,]</label>
                    </control>
                    <control type="progress">
                        <top>15</top><width>240</width><height>6</height>
                        <texturebg colordiffuse="33FFFFFF">colors/white.png</texturebg>
                        <midtexture colordiffuse="%(text)s">colors/white.png</midtexture>
                        <info>PVR.EpgEventProgress</info>
                        <visible>!String.IsEmpty(VideoPlayer.EndTime)</visible>
                    </control>
                    <control type="label">
                        <width>auto</width><height>36</height>
                        <aligny>center</aligny>
                        <font>silo_meta</font>
                        <textcolor>%(dim)s</textcolor>
                        <label>$INFO[PVR.EpgEventRemainingTime(mins),, min left]</label>
                        <visible>!String.IsEmpty(VideoPlayer.EndTime)</visible>
                    </control>
                </control>
                <control type="textbox">
                    <top>150</top><width>1300</width><height>66</height>
                    <font>silo_detail</font>
                    <textcolor>B3EDEDED</textcolor>
                    <label>$INFO[VideoPlayer.Plot]</label>
                </control>
                <control type="label">
                    <top>222</top><width>1400</width><height>36</height>
                    <font>silo_meta</font>
                    <textcolor>%(dim)s</textcolor>
                    <label>$INFO[VideoPlayer.NextStartTime,[COLOR %(text)s]Next[/COLOR]  ,  ]$INFO[VideoPlayer.NextTitle]</label>
                </control>
            </control>''' % {'left': left, 'top': top, 'text': TEXT, 'dim': DIM}


def channel_card(top):
    """The playing channel's logo on a dark card, left of the infobar."""
    return '''
            <control type="image">
                <left>88</left><top>%(top)d</top><width>224</width><height>136</height>
                <texture border="20" colordiffuse="E61E2024">silo/card_landscape_mask.png</texture>
            </control>
            <control type="image">
                <left>110</left><top>%(logo)d</top><width>180</width><height>104</height>
                <aspectratio>keep</aspectratio>
                <texture>$INFO[Player.Icon]</texture>
            </control>''' % {'top': top, 'logo': top + 16}


def corners():
    """The playing channel's group at the top left and the time at the right, as TiviMate's."""
    return '''
            <control type="label">
                <left>88</left><top>40</top><width>900</width><height>56</height>
                <font>silo_meta</font>
                <textcolor>%(text)s</textcolor>
                <label>$INFO[VideoPlayer.ChannelGroup]</label>
            </control>
            <control type="label">
                <right>88</right><top>40</top><width>600</width><height>56</height>
                <align>right</align>
                <font>silo_meta</font>
                <textcolor>%(text)s</textcolor>
                <label>$INFO[System.Date(ddd d mmm)]$INFO[System.Time,  ·  ,]</label>
            </control>''' % {'text': TEXT}


def banner():
    """Live TV's banner (a channel change, Info) in Kodi's seek bar window,
    as TiviMate's in Silo's look; Estuary's stays for its own OSD."""
    return '''		<!-- Silo Skyline Live TV banner (tools/build_tv.py) -->
		<control type="group">
			<visible>VideoPlayer.Content(LiveTV) + [Player.ShowInfo | Window.IsActive(fullscreeninfo) | Player.ChannelPreviewActive] + !Window.IsActive(videoosd) + !Window.IsActive(pvrosdchannels) + !Window.IsActive(%(recent)d)</visible>
			<animation effect="slide" start="0,120" end="0,0" time="220" tween="cubic" easing="out">Visible</animation>
			<animation effect="fade" start="100" end="0" time="160">Hidden</animation>
			<!-- Twice, so the text reads over bright pictures; the top for the corners. -->
			<control type="image">
				<left>0</left><top>480</top><width>1920</width><height>600</height>
				<texture>silo/scrim_bottom.png</texture>
			</control>
			<control type="image">
				<left>0</left><top>640</top><width>1920</width><height>440</height>
				<texture>silo/scrim_bottom.png</texture>
			</control>
			<control type="image">
				<left>0</left><top>0</top><width>1920</width><height>200</height>
				<texture flipy="true">silo/scrim_bottom.png</texture>
			</control>%(corners)s%(card)s%(info)s
		</control>
		<!-- end Silo Skyline Live TV banner -->
''' % {'recent': RECENT_ID, 'corners': corners(), 'card': channel_card(788), 'info': infobar(776)}


def add_banner():
    path = os.path.join(ROOT, 'xml', 'DialogSeekBar.xml')
    text = open(path, encoding='utf-8').read()
    start, end = '\t\t<!-- Silo Skyline Live TV banner (tools/build_tv.py) -->', '\t\t<!-- end Silo Skyline Live TV banner -->\n'
    text = text[:text.index(start)] + banner() + text[text.index(end) + len(end):]
    open(path, 'w', encoding='utf-8').write(text)


# Live TV while it plays, as TiviMate: Left the quick guide (Kodi's channel
# list over the video), OK the recently watched channels (a window of ours).
QUICK_W = 640                # the channel list's panel
QUICK_ROW = 106
SCHEDULE_W, SCHEDULE_ROW = 520, 58
CARD_PANEL_W = 600
RECENT_ID = 1196
RECENT_LIST = 5600
GUIDE_CARD = 5599
ROW_Y = 1080 - 70 - 168 - 84   # the row's top
CARD_W, CARD_H = 300, 168


def quick_row(focused):
    """A channel in the quick guide: logo, number and name, what's on now
    with how far through it; the focused row a white bar, dark text."""
    lit = 'Control.HasFocus(11)'

    def row(now_colour, dim_colour, visible):
        return '''
                    <control type="group">%(visible)s
                        <control type="image">
                            <left>%(x)d</left><top>16</top><width>104</width><height>72</height>
                            <aspectratio>keep</aspectratio>
                            <texture fallback="DefaultTVShows.png">$INFO[ListItem.Icon]</texture>
                        </control>
                        <control type="label">
                            <left>%(tx)d</left><top>12</top><width>%(tw)d</width><height>34</height>
                            <font>silo_detail</font>
                            <textcolor>%(dim)s</textcolor>
                            <selectedcolor>%(dim)s</selectedcolor>
                            <label>$INFO[ListItem.ChannelNumberLabel,,  ·  ]$INFO[ListItem.ChannelName]</label>
                        </control>
                        <control type="label">
                            <left>%(tx)d</left><top>44</top><width>%(tw)d</width><height>36</height>
                            <font>silo_meta</font>
                            <textcolor>%(now)s</textcolor>
                            <selectedcolor>%(now)s</selectedcolor>
                            <label>$VAR[SiloQuickNow]</label>
                        </control>
                        <control type="progress">
                            <left>%(tx)d</left><top>88</top><width>%(tw)d</width><height>5</height>
                            <texturebg colordiffuse="33FFFFFF">colors/white.png</texturebg>
                            <midtexture colordiffuse="%(now)s">colors/white.png</midtexture>
                            <info>ListItem.Progress</info>
                        </control>
                    </control>''' % {'x': SAFE_X - 40, 'tx': SAFE_X + 80, 'tw': QUICK_W - SAFE_X - 110, 'now': now_colour,
                                     'dim': dim_colour,
                                     'visible': '\n                        <visible>%s</visible>' % visible if visible else ''}
    if not focused:
        return row('D9EDEDED', DIM, '')
    bar = '''
                    <control type="image">
                        <left>%d</left><top>4</top><width>%d</width><height>%d</height>
                        <texture border="20" colordiffuse="%s">silo/card_landscape_mask.png</texture>
                        <visible>%s</visible>
                    </control>''' % (SAFE_X - 58, QUICK_W - SAFE_X + 40, QUICK_ROW - 8, TEXT, lit)
    return bar + row('FF000000', 'B3000000', lit) + row('D9EDEDED', DIM, '!' + lit)


def schedule_row():
    """A programme in the focused channel's schedule: its start time and
    title, the one on now lit; a "Tomorrow" header where the day changes."""
    on = 'String.IsEqual(ListItem.Property(silo.now),1)'
    header = 'String.IsEqual(ListItem.Property(silo.header),1)'
    return '''
                    <control type="label">
                        <left>0</left><width>120</width><height>%(h)d</height>
                        <aligny>center</aligny>
                        <font>silo_detail</font>
                        <textcolor>%(dim)s</textcolor>
                        <label>$INFO[ListItem.Label2]</label>
                        <visible>!%(header)s</visible>
                    </control>
                    <control type="label">
                        <left>130</left><width>%(tw)d</width><height>%(h)d</height>
                        <aligny>center</aligny>
                        <font>silo_detail</font>
                        <textcolor>$VAR[SiloQuickScheduleColour]</textcolor>
                        <label>$INFO[ListItem.Label]</label>
                        <visible>!%(header)s</visible>
                    </control>
                    <control type="label">
                        <left>0</left><width>%(w)d</width><height>%(h)d</height>
                        <aligny>bottom</aligny>
                        <font>silo_badge</font>
                        <textcolor>%(text)s</textcolor>
                        <label>[UPPERCASE]$INFO[ListItem.Label][/UPPERCASE]</label>
                        <visible>%(header)s</visible>
                    </control>''' % {'h': SCHEDULE_ROW, 'dim': DIM, 'text': TEXT, 'header': header,
                                     'tw': SCHEDULE_W - 140, 'w': SCHEDULE_W, 'on': on}


def build_quick_guide():
    """Kodi's channel list while Live TV plays (DialogPVRChannelsOSD; Left in
    our keymap), as TiviMate's: the channels down the left, the focused
    channel's schedule beside them (SiloKodiConnect's mode=schedule), and its
    programme in a card at the top right, the video playing on behind. Kodi
    switches to the chosen channel."""
    focused = 'Container(11).ListItem'
    return '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by tools/build_tv.py: edit that, not this. -->
<window>
    <defaultcontrol always="true">11</defaultcontrol>
    <controls>
        <control type="group">
            <animation effect="slide" start="-%(sx_end)d,0" end="0,0" time="220" tween="cubic" easing="out">WindowOpen</animation>
            <animation effect="slide" start="0,0" end="-%(sx_end)d,0" time="160" tween="cubic" easing="in">WindowClose</animation>
            <!-- The list's panel; the schedule's darker veil fades into the video. -->
            <control type="image">
                <left>0</left><top>0</top><width>%(w)d</width><height>1080</height>
                <texture colordiffuse="F2%(bg)s">colors/white.png</texture>
            </control>
            <control type="image">
                <left>%(w)d</left><top>0</top><width>%(sw)d</width><height>1080</height>
                <texture colordiffuse="CC%(bg)s">colors/white.png</texture>
            </control>
            <control type="image">
                <left>%(sx_end)d</left><top>0</top><width>200</width><height>1080</height>
                <texture colordiffuse="CC%(bg)s">silo/scrim_side.png</texture>
            </control>
            <control type="label" id="2">
                <left>%(x)d</left><top>40</top><width>%(lw)d</width><height>56</height>
                <font>silo_meta</font>
                <textcolor>%(text)s</textcolor>
                <label>$INFO[VideoPlayer.ChannelGroup]</label>
            </control>
            <control type="fixedlist" id="11">
                <left>0</left><top>110</top><width>%(w)d</width><height>%(lh)d</height>
                <focusposition>3</focusposition>
                <movement>3</movement>
                <orientation>vertical</orientation>
                <scrolltime tween="cubic" easing="out">200</scrolltime>
                <itemlayout width="%(w)d" height="%(row)d">%(item)s
                </itemlayout>
                <focusedlayout width="%(w)d" height="%(row)d">%(item_focused)s
                </focusedlayout>
            </control>
            <!-- The focused channel's schedule, from what's on now. -->
            <control type="group">
                <left>%(sx)d</left><top>40</top>
                <control type="image">
                    <width>104</width><height>56</height>
                    <aspectratio align="left">keep</aspectratio>
                    <texture>$INFO[%(f)s.Icon]</texture>
                </control>
                <control type="label">
                    <left>120</left><width>%(stw)d</width><height>56</height>
                    <aligny>center</aligny>
                    <font>silo_meta</font>
                    <textcolor>%(text)s</textcolor>
                    <label>$INFO[%(f)s.ChannelNumberLabel,,  ·  ]$INFO[%(f)s.ChannelName]</label>
                </control>
                <control type="list" id="12">
                    <top>90</top><width>%(sw2)d</width><height>%(sh)d</height>
                    <orientation>vertical</orientation>
                    <content target="videos">plugin://plugin.video.silokodiconnect/?mode=schedule&amp;number=$INFO[%(f)s.ChannelNumberLabel]&amp;name=$INFO[%(f)s.ChannelName]</content>
                    <itemlayout width="%(sw2)d" height="%(srow)d">%(sched)s
                    </itemlayout>
                    <focusedlayout width="%(sw2)d" height="%(srow)d">%(sched)s
                    </focusedlayout>
                </control>
            </control>
        </control>
        <!-- The focused channel's programme, as TiviMate's card. -->
        <control type="group">
            <left>%(cx)d</left><top>48</top>
            <animation effect="fade" start="0" end="100" time="200">WindowOpen</animation>
            <animation effect="fade" start="100" end="0" time="120">WindowClose</animation>
            <control type="image">
                <width>%(cw)d</width><height>260</height>
                <texture border="28">silo/menu_panel.png</texture>
            </control>
            <control type="textbox">
                <left>30</left><top>22</top><width>%(cw2)d</width><height>96</height>
                <font>silo_meta</font>
                <textcolor>%(text)s</textcolor>
                <label fallback="19055">$INFO[%(f)s.Title]</label>
            </control>
            <control type="grouplist">
                <left>30</left><top>126</top><width>%(cw2)d</width><height>34</height>
                <orientation>horizontal</orientation>
                <itemgap>18</itemgap>
                <control type="label">
                    <width>auto</width><height>34</height>
                    <aligny>center</aligny>
                    <font>silo_detail</font>
                    <textcolor>%(text)s</textcolor>
                    <label>$INFO[%(f)s.StartTime]$INFO[%(f)s.EndTime, – ,]</label>
                </control>
                <control type="progress">
                    <top>14</top><width>160</width><height>5</height>
                    <texturebg colordiffuse="33FFFFFF">colors/white.png</texturebg>
                    <midtexture colordiffuse="%(text)s">colors/white.png</midtexture>
                    <info>%(f)s.Progress</info>
                </control>
            </control>
            <control type="textbox">
                <left>30</left><top>170</top><width>%(cw2)d</width><height>66</height>
                <font>silo_detail</font>
                <textcolor>B3EDEDED</textcolor>
                <label>$INFO[%(f)s.Plot]</label>
            </control>
        </control>
        <include>PVRChannelNumberInput</include>
    </controls>
</window>
''' % {'w': QUICK_W, 'sw': SCHEDULE_W + 60, 'sx': QUICK_W + 30, 'sx_end': QUICK_W + SCHEDULE_W + 60,
       'bg': BACKGROUND[2:], 'x': SAFE_X - 40, 'lw': QUICK_W - SAFE_X, 'text': TEXT,
       'lh': QUICK_ROW * 9, 'row': QUICK_ROW, 'item': quick_row(False), 'item_focused': quick_row(True),
       'f': focused, 'stw': SCHEDULE_W - 120, 'sw2': SCHEDULE_W, 'sh': SCHEDULE_ROW * 15, 'srow': SCHEDULE_ROW,
       'sched': schedule_row(), 'cx': 1920 - SAFE_X - CARD_PANEL_W, 'cw': CARD_PANEL_W, 'cw2': CARD_PANEL_W - 60}


def quick_variables():
    """The quick guide's labels: what's on now (TiviMate's "No information"),
    and the schedule's colours (the one on now white, later ones softer)."""
    return ('    <variable name="SiloQuickNow">\n'
            '        <value condition="String.IsEmpty(ListItem.Title)">No information</value>\n'
            '        <value>$INFO[ListItem.Title]</value>\n'
            '    </variable>\n'
            '    <variable name="SiloQuickScheduleColour">\n'
            '        <value condition="String.IsEqual(ListItem.Property(silo.now),1)">%s</value>\n'
            '        <value>C7EDEDED</value>\n'
            '    </variable>\n') % TEXT


def recent_card(focused):
    """A recently watched channel: its logo on a dark card, its name and
    what's on under it; focused, the card grows with Silo's veil and rim."""
    from build_home import focus_sheen, focus_zoom
    lit = 'Control.HasFocus(%d)' % RECENT_LIST
    return '''
                <control type="group">%(zoom)s
                    <control type="image">
                        <left>6</left><top>6</top><width>%(w)d</width><height>%(h)d</height>
                        <texture border="20" colordiffuse="FF1E2024">silo/card_landscape_mask.png</texture>
                    </control>
                    <control type="image">
                        <left>36</left><top>30</top><width>%(lw)d</width><height>%(lh)d</height>
                        <aspectratio>keep</aspectratio>
                        <texture fallback="DefaultTVShows.png">$INFO[ListItem.Icon]</texture>
                    </control>
                    <control type="progress">
                        <left>24</left><top>%(py)d</top><width>%(pw)d</width><height>5</height>
                        <texturebg colordiffuse="33FFFFFF">colors/white.png</texturebg>
                        <midtexture colordiffuse="%(text)s">colors/white.png</midtexture>
                        <info>ListItem.Progress</info>
                    </control>%(sheen)s
                    <control type="label">
                        <left>6</left><top>%(t1)d</top><width>%(w)d</width><height>34</height>
                        <font>silo_card_title</font>
                        <textcolor>%(title)s</textcolor>
                        <selectedcolor>%(title)s</selectedcolor>
                        <label>$INFO[ListItem.ChannelName]</label>
                    </control>
                    <control type="label">
                        <left>6</left><top>%(t2)d</top><width>%(w)d</width><height>30</height>
                        <font>silo_card_sub</font>
                        <textcolor>%(sub)s</textcolor>
                        <selectedcolor>%(sub)s</selectedcolor>
                        <label>$INFO[ListItem.Title]</label>
                    </control>
                </control>''' % {'zoom': focus_zoom(lit, 16) if focused else '', 'w': CARD_W, 'h': CARD_H,
                                  'lw': CARD_W - 60, 'lh': CARD_H - 60, 'py': CARD_H - 12, 'pw': CARD_W - 36,
                                  'sheen': focus_sheen(CARD_W, CARD_H, 'silo/card_landscape_mask.png',
                                                       'silo/card_landscape_rim.png', lit, 16) if focused else '',
                                  't1': CARD_H + 20, 't2': CARD_H + 54, 'text': TEXT,
                                  'title': TEXT if focused else '80EDEDED', 'sub': DIM if focused else '61EDEDED'}


def guide_card(focused):
    """The row's first card, as TiviMate's: TV guide, opening the full guide."""
    lit = 'Control.HasFocus(%d)' % GUIDE_CARD
    return '''
                <control type="image">
                    <left>6</left><top>6</top><width>%(w)d</width><height>%(h)d</height>
                    <texture border="20" colordiffuse="%(fill)s">silo/card_landscape_mask.png</texture>
                </control>
                <control type="image">
                    <left>%(ix)d</left><top>38</top><width>56</width><height>56</height>
                    <texture colordiffuse="%(ink)s">icons/menu.png</texture>
                </control>
                <control type="label">
                    <left>6</left><top>110</top><width>%(w)d</width><height>40</height>
                    <align>center</align>
                    <font>silo_meta</font>
                    <textcolor>%(ink)s</textcolor>
                    <label>TV guide</label>
                </control>''' % {'w': CARD_W, 'h': CARD_H, 'ix': 6 + CARD_W // 2 - 28,
                                  'fill': TEXT if focused else 'FF1E2024', 'ink': 'FF000000' if focused else TEXT}


def build_recent():
    """While Live TV plays (OK in our keymap), as TiviMate's: what's playing
    (the infobar), then a row along the bottom: TV guide, then the recently
    watched channels. OK switches to one; Back closes it."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by tools/build_tv.py: edit that, not this. -->
<window id="%(window)d" type="dialog">
    <defaultcontrol always="true">%(list)d</defaultcontrol>
    <controls>
        <control type="group">
            <animation effect="slide" start="0,320" end="0,0" time="220" tween="cubic" easing="out">WindowOpen</animation>
            <animation effect="slide" start="0,0" end="0,320" time="160" tween="cubic" easing="in">WindowClose</animation>
            <control type="image">
                <left>0</left><top>300</top><width>1920</width><height>780</height>
                <texture colordiffuse="F2%(bg)s">silo/scrim_bottom.png</texture>
            </control>
            <control type="image">
                <left>0</left><top>520</top><width>1920</width><height>560</height>
                <texture colordiffuse="F2%(bg)s">silo/scrim_bottom.png</texture>
            </control>
            <control type="image">
                <left>0</left><top>0</top><width>1920</width><height>200</height>
                <texture flipy="true">silo/scrim_bottom.png</texture>
            </control>%(corners)s%(info)s
            <control type="group">
                <left>%(lx)d</left><top>%(ly)d</top>
                <control type="button" id="%(guide)d">
                    <width>%(iw)d</width><height>%(ih)d</height>
                    <texturefocus /><texturenofocus />
                    <onright>%(list)d</onright>
                    <onclick>Dialog.Close(%(window)d)</onclick>
                    <onclick>ActivateWindow(TVGuide)</onclick>
                </control>
                <control type="group">%(guide_card)s
                    <visible>!Control.HasFocus(%(guide)d)</visible>
                </control>
                <control type="group">%(zoom)s%(guide_card_focused)s
                    <visible>Control.HasFocus(%(guide)d)</visible>
                </control>
            </control>
            <control type="list" id="%(list)d">
                <left>%(rx)d</left><top>%(ly)d</top><width>%(lw)d</width><height>%(ih)d</height>
                <orientation>horizontal</orientation>
                <onleft>%(guide)d</onleft>
                <scrolltime tween="cubic" easing="out">200</scrolltime>
                <content target="videos">pvr://channels/tv/*?view=lastplayed</content>
                <onclick>Dialog.Close(%(window)d)</onclick>
                <onclick>PlayMedia($ESCINFO[ListItem.FileNameAndPath])</onclick>
                <itemlayout width="%(iw)d" height="%(ih)d">%(card)s
                </itemlayout>
                <focusedlayout width="%(iw)d" height="%(ih)d">%(card_focused)s
                </focusedlayout>
            </control>
        </control>
    </controls>
</window>
''' % {'window': RECENT_ID, 'list': RECENT_LIST, 'guide': GUIDE_CARD, 'bg': BACKGROUND[2:], 'text': TEXT,
       'corners': corners(), 'info': infobar(ROW_Y - 290, SAFE_X),
       'lx': SAFE_X - 6, 'rx': SAFE_X - 6 + CARD_W + 40, 'ly': ROW_Y,
       'lw': 1920 - SAFE_X - CARD_W - 40, 'iw': CARD_W + 40, 'ih': CARD_H + 12 + 84,
       'guide_card': guide_card(False), 'guide_card_focused': guide_card(True),
       'zoom': __import__('build_home').focus_zoom('Control.HasFocus(%d)' % GUIDE_CARD, 16),
       'card': recent_card(False), 'card_focused': recent_card(True)}


if __name__ == '__main__':
    with open(os.path.join(ROOT, 'xml', 'MyPVRGuide.xml'), 'w', encoding='utf-8') as handle:
        handle.write(build())
    with open(os.path.join(ROOT, 'xml', 'DialogPVRInfo.xml'), 'w', encoding='utf-8') as handle:
        handle.write(build_info())
    with open(os.path.join(ROOT, 'xml', 'DialogPVRChannelsOSD.xml'), 'w', encoding='utf-8') as handle:
        handle.write(build_quick_guide())
    with open(os.path.join(ROOT, 'xml', 'Custom_%d_SiloRecentChannels.xml' % RECENT_ID), 'w', encoding='utf-8') as handle:
        handle.write(build_recent())
    add_banner()
    add_variables()
    print('Wrote xml/MyPVRGuide.xml, DialogPVRInfo.xml and their variables in xml/Variables.xml')
