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
                                      'label': '$VAR[SiloGuideTitle]' if focused else '[COLOR D9EDEDED]$INFO[ListItem.Label][/COLOR]'}


def variables():
    """The focused programme's block and title: white with dark text while
    the grid has focus, as the others otherwise."""
    lit = 'Control.HasFocus(%d)' % GRID_ID
    return ('    <!-- Silo Skyline TV guide (tools/build_tv.py) -->\n'
            '    <variable name="SiloGuideCell">\n'
            '        <value condition="%(lit)s">%(text)s</value>\n'
            '        <value>17FFFFFF</value>\n'
            '    </variable>\n'
            '    <variable name="SiloGuideTitle">\n'
            '        <value condition="%(lit)s">[COLOR FF000000]$INFO[ListItem.Label][/COLOR]</value>\n'
            '        <value>[COLOR D9EDEDED]$INFO[ListItem.Label][/COLOR]</value>\n'
            '    </variable>\n'
            '    <!-- end Silo Skyline TV guide -->\n') % {'lit': lit, 'text': TEXT}


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
            <!-- Now: a white line at the current time. -->
            <progresstexture border="0,0,4,0" colordiffuse="E6FFFFFF">silo/epg_now.png</progresstexture>
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


# Live TV while it plays, as TiviMate: Left the quick guide (Kodi's channel
# list over the video), OK the recently watched channels (a window of ours).
QUICK_W = 900
QUICK_ROW = 108
RECENT_ID = 1196
RECENT_LIST = 5600
CARD_W, CARD_H = 300, 168


def quick_row(focused):
    """A channel in the quick guide: logo, number and name, what's on now
    with how far through it; the focused row a white bar, dark text."""
    lit = 'Control.HasFocus(11)'
    def row(name_colour, now_colour, dim_colour, visible):
        return '''
                    <control type="group">%(visible)s
                        <control type="image">
                            <left>%(x)d</left><top>14</top><width>120</width><height>80</height>
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
                            <label>$INFO[ListItem.Title]</label>
                        </control>
                        <control type="progress">
                            <left>%(tx)d</left><top>88</top><width>220</width><height>5</height>
                            <texturebg colordiffuse="33FFFFFF">colors/white.png</texturebg>
                            <midtexture colordiffuse="%(now)s">colors/white.png</midtexture>
                            <info>ListItem.Progress</info>
                        </control>
                        <control type="label">
                            <left>%(rx)d</left><top>78</top><width>%(rw)d</width><height>26</height>
                            <font>silo_card_sub</font>
                            <textcolor>%(dim)s</textcolor>
                            <selectedcolor>%(dim)s</selectedcolor>
                            <label>$INFO[ListItem.StartTime]$INFO[ListItem.EndTime, – ,]</label>
                        </control>
                    </control>''' % {'x': SAFE_X, 'tx': SAFE_X + 140, 'tw': QUICK_W - SAFE_X - 180, 'now': now_colour,
                                     'dim': dim_colour, 'rx': SAFE_X + 380, 'rw': QUICK_W - SAFE_X - 420,
                                     'visible': '\n                        <visible>%s</visible>' % visible if visible else ''}
    if not focused:
        return row(TEXT, 'D9EDEDED', DIM, '')
    bar = '''
                    <control type="image">
                        <left>%d</left><top>4</top><width>%d</width><height>%d</height>
                        <texture border="20" colordiffuse="%s">silo/card_landscape_mask.png</texture>
                        <visible>%s</visible>
                    </control>''' % (SAFE_X - 18, QUICK_W - SAFE_X - 12, QUICK_ROW - 8, TEXT, lit)
    return bar + row(TEXT, 'FF000000', 'B3000000', lit) + row(TEXT, 'D9EDEDED', DIM, '!' + lit)


def build_quick_guide():
    """Kodi's channel list while Live TV plays (DialogPVRChannelsOSD; Left in
    our keymap): channels and what's on, down a dark panel at the left, the
    video playing on beside it; the focused channel's next programme under
    the list. Kodi switches to the chosen channel."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by tools/build_tv.py: edit that, not this. -->
<window>
    <defaultcontrol always="true">11</defaultcontrol>
    <controls>
        <control type="group">
            <animation effect="slide" start="-%(w)d,0" end="0,0" time="220" tween="cubic" easing="out">WindowOpen</animation>
            <animation effect="slide" start="0,0" end="-%(w)d,0" time="160" tween="cubic" easing="in">WindowClose</animation>
            <!-- The panel: solid at the left, fading into the video at its edge. -->
            <control type="image">
                <left>0</left><top>0</top><width>%(w)d</width><height>1080</height>
                <texture colordiffuse="F2%(bg)s">colors/white.png</texture>
            </control>
            <control type="image">
                <left>%(w)d</left><top>0</top><width>160</width><height>1080</height>
                <texture colordiffuse="F2%(bg)s">silo/scrim_side.png</texture>
            </control>
            <control type="label" id="2">
                <left>%(x)d</left><top>48</top><width>%(lw)d</width><height>56</height>
                <font>silo_row</font>
                <textcolor>%(text)s</textcolor>
                <selectedcolor>%(text)s</selectedcolor>
                <label>$VAR[BreadcrumbsPVRChannelsOSDVar]</label>
            </control>
            <control type="fixedlist" id="11">
                <left>0</left><top>128</top><width>%(w)d</width><height>%(lh)d</height>
                <focusposition>3</focusposition>
                <movement>3</movement>
                <orientation>vertical</orientation>
                <scrolltime tween="cubic" easing="out">200</scrolltime>
                <itemlayout width="%(w)d" height="%(row)d">%(item)s
                </itemlayout>
                <focusedlayout width="%(w)d" height="%(row)d">%(item_focused)s
                </focusedlayout>
            </control>
            <!-- Next on the focused channel. -->
            <control type="label">
                <left>%(x)d</left><top>%(ny)d</top><width>%(lw)d</width><height>40</height>
                <font>silo_meta</font>
                <textcolor>%(dim)s</textcolor>
                <selectedcolor>%(dim)s</selectedcolor>
                <label>$INFO[Container(11).ListItem.NextStartTime,[COLOR %(text)s]Next[/COLOR]  ,  ]$INFO[Container(11).ListItem.NextTitle]</label>
            </control>
        </control>
        <include>PVRChannelNumberInput</include>
    </controls>
</window>
''' % {'w': QUICK_W, 'bg': BACKGROUND[2:], 'x': SAFE_X, 'lw': QUICK_W - 2 * SAFE_X, 'text': TEXT, 'dim': DIM,
       'lh': QUICK_ROW * 8, 'row': QUICK_ROW, 'ny': 128 + QUICK_ROW * 8 + 20,
       'item': quick_row(False), 'item_focused': quick_row(True)}


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


def build_recent():
    """The recently watched channels while Live TV plays (OK in our keymap):
    a row of cards along the bottom over the video, as TiviMate's. OK
    switches to one; Back or a pause closes it."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by tools/build_tv.py: edit that, not this. -->
<window id="%(window)d" type="dialog">
    <defaultcontrol always="true">%(list)d</defaultcontrol>
    <controls>
        <control type="group">
            <animation effect="slide" start="0,320" end="0,0" time="220" tween="cubic" easing="out">WindowOpen</animation>
            <animation effect="slide" start="0,0" end="0,320" time="160" tween="cubic" easing="in">WindowClose</animation>
            <control type="image">
                <left>0</left><top>620</top><width>1920</width><height>460</height>
                <texture colordiffuse="F2%(bg)s">silo/scrim_bottom.png</texture>
            </control>
            <control type="label">
                <left>%(x)d</left><top>%(hy)d</top><width>1000</width><height>50</height>
                <font>silo_row</font>
                <textcolor>%(text)s</textcolor>
                <selectedcolor>%(text)s</selectedcolor>
                <label>Recent channels</label>
            </control>
            <control type="list" id="%(list)d">
                <left>%(lx)d</left><top>%(ly)d</top><width>%(lw)d</width><height>%(ih)d</height>
                <orientation>horizontal</orientation>
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
''' % {'window': RECENT_ID, 'list': RECENT_LIST, 'bg': BACKGROUND[2:], 'x': SAFE_X, 'text': TEXT,
       'hy': 1080 - 70 - CARD_H - 84 - 64, 'lx': SAFE_X - 6, 'ly': 1080 - 70 - CARD_H - 84,
       'lw': 1920 - SAFE_X, 'iw': CARD_W + 40, 'ih': CARD_H + 12 + 84,
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
    add_variables()
    print('Wrote xml/MyPVRGuide.xml, DialogPVRInfo.xml and their variables in xml/Variables.xml')
