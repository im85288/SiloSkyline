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
TOP_H = 330                 # the programme's details and the preview
PILLS_Y = TOP_H + 6
GRID_Y = PILLS_Y + 76
CHANNEL_W = 620
ROW_H = 78                  # TiviMate's rows: 8 channels on screen, easy to read from the sofa
LOGO_W, LOGO_H = 92, 52
RULER_H = 46
PREVIEW_W, PREVIEW_H = 496, 279
BLOCK_W = 60                # a 5-minute block
# TiviMate's yellow: the playing channel, the programme on now, today.
ACCENT = 'FFF2D46B'
PLAYING = 'ListItem.IsPlaying'


def two_tone(control, colour, accent, condition, also=''):
    """A label twice: in the accent where condition holds, else in colour.
    Kodi works a $VAR colour out once for a whole list, not per row, while
    a visible condition is per row. control has {colour} and {visible}, and
    {also} for a part in its own colour (a channel number) that takes the
    accent too."""
    control = control.replace('{also}', also)
    lit = control.replace('[COLOR %s]' % also, '[COLOR %s]' % accent) if also else control
    return (lit.replace('{colour}', accent).replace('{visible}', '<visible>%s</visible>' % condition) +
            control.replace('{colour}', colour).replace('{visible}', '<visible>!%s</visible>' % condition))


def playing_mark(left, top, size=24, colour=ACCENT, also='true'):
    """TiviMate's ▶ by the playing channel (also: when else it shows)."""
    return '''
                        <control type="label">
                            <left>%(x)d</left><top>%(y)d</top><width>%(s)d</width><height>%(s)d</height>
                            <align>center</align><aligny>center</aligny>
                            <font>silo_detail</font>
                            <textcolor>%(colour)s</textcolor>
                            <!-- Kodi marks the playing channel selected: the same colour then. -->
                            <selectedcolor>%(colour)s</selectedcolor>
                            <label>▶</label>
                            <visible>%(playing)s + %(also)s</visible>
                        </control>''' % {'x': left, 'y': top, 's': size, 'colour': colour, 'playing': PLAYING, 'also': also}


def channel(focused):
    """A channel down the left on one line, as TiviMate's: logo, number and
    name, and its history icon when it has catch-up; the focused row's
    channel lit while the grid has focus."""
    colour = TEXT if focused else 'C7EDEDED'
    return '''
                    <control type="image">
                        <left>%(x)d</left><top>5</top><width>%(w)d</width><height>%(h)d</height>
                        <texture border="16" colordiffuse="%(fill)s">silo/card_landscape_mask.png</texture>
                    </control>
                    <control type="image">
                        <left>%(lx)d</left><top>%(ly)d</top><width>%(lw)d</width><height>%(lh)d</height>
                        <aspectratio>keep</aspectratio>
                        <texture fallback="DefaultTVShows.png">$INFO[ListItem.Icon]</texture>
                    </control>
%(name)s
                    <!-- Catch-up: past programmes can be played (TiviMate's clock). -->
                    <control type="image">
                        <left>%(ax)d</left><top>%(iy)d</top><width>26</width><height>26</height>
                        <texture colordiffuse="%(dim)s">silo/menu_history.png</texture>
                        <visible>ListItem.HasArchive</visible>
                    </control>%(playing)s''' % {'x': SAFE_X - 6, 'w': CHANNEL_W - SAFE_X + 2, 'h': ROW_H - 10,
                                     'playing': playing_mark(CHANNEL_W - 74, (ROW_H - 28) // 2, 28),
                                     'ly': (ROW_H - LOGO_H) // 2, 'lw': LOGO_W, 'lh': LOGO_H, 'iy': (ROW_H - 26) // 2,
                                     'name': two_tone('''
                    <control type="label">
                        <left>%d</left><top>5</top><width>%d</width><height>%d</height>
                        <aligny>center</aligny>
                        <font>silo_meta</font>
                        <textcolor>{colour}</textcolor>
                        <selectedcolor>{colour}</selectedcolor>
                        <label>$INFO[ListItem.ChannelNumberLabel,[COLOR {also}],[/COLOR]  ]$INFO[ListItem.Label]</label>
                        {visible}
                    </control>''' % (SAFE_X + LOGO_W + 18, CHANNEL_W - SAFE_X - LOGO_W - 100, ROW_H - 10),
                                                      colour, ACCENT, PLAYING, DIM),
                                     'fill': '1FFFFFFF' if focused else '0DFFFFFF', 'lx': SAFE_X + 4,
                                     'tx': SAFE_X + 84, 'tw': CHANNEL_W - SAFE_X - 160, 'dim': DIM, 'colour': colour,
                                     'ax': CHANNEL_W - 40}


def programme(focused):
    """A programme: a dark rounded block with its title; focused, a white bar
    with dark text (Silo's focus) while the grid has focus. Kodi stretches
    only the image with id 2 and the label with id 1 to the programme's
    length, so the block's colour and the title's come from variables."""
    return '''
                    <control type="image" id="2">
                        <left>3</left><top>5</top><width>%(w)d</width><height>%(h)d</height>
                        <texture border="16" colordiffuse="%(fill)s">silo/card_landscape_mask.png</texture>
                    </control>
                    <control type="label" id="1">
                        <left>18</left><top>5</top><width>%(lw)d</width><height>%(h)d</height>
                        <aligny>center</aligny>
                        <font>silo_meta</font>
                        <label>%(label)s</label>
                    </control>''' % {'w': BLOCK_W - 6, 'lw': BLOCK_W - 30, 'h': ROW_H - 10,
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
            ) % {'lit': lit, 'text': TEXT, 'playing': PLAYING, 'accent': ACCENT} + quick_variables() + stream_variables() + '    <!-- end Silo Skyline TV guide -->\n'


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

        <!-- At the left: what's playing (TiviMate's preview), else the
             programme's or channel's picture. -->
        <control type="group">
            <left>%(x)d</left><top>%(py)d</top>
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

        <!-- Beside it, the focused programme as TiviMate's guide shows it: the
             title on up to two lines, its times, how far through, and its plot. -->
        <control type="group">
            <left>%(dx)d</left><top>%(py)d</top>
            <control type="textbox">
                <width>%(dw)d</width><height>112</height>
                <font>silo_osd_title</font>
                <textcolor>%(text)s</textcolor>
                <label>$INFO[ListItem.Label]</label>
                <autoscroll>false</autoscroll>
            </control>
            <control type="grouplist">
                <top>132</top><width>%(dw)d</width><height>36</height>
                <orientation>horizontal</orientation>
                <itemgap>18</itemgap>
                <control type="label">
                    <width>auto</width><height>36</height>
                    <aligny>center</aligny>
                    <font>silo_meta</font>
                    <textcolor>%(text)s</textcolor>
                    <selectedcolor>%(text)s</selectedcolor>
                    <label>$INFO[ListItem.StartTime]$INFO[ListItem.EndTime, – ,]</label>
                </control>
                <!-- On now: how far through, as Silo's progress bars (Kodi gives guide
                     programmes no time left: EpgEventRemainingTime is for channels). -->
                <control type="progress">
                    <top>15</top><width>180</width><height>6</height>
                    <texturebg colordiffuse="33FFFFFF">colors/white.png</texturebg>
                    <midtexture colordiffuse="%(text)s">colors/white.png</midtexture>
                    <info>ListItem.Progress</info>
                    <visible>%(on_now)s</visible>
                </control>
            </control>
            <control type="textbox">
                <top>180</top><width>%(dw)d</width><height>%(plot_h)d</height>
                <font>silo_plot</font>
                <textcolor>%(soft)s</textcolor>
                <label>$INFO[ListItem.Plot]</label>
                <autoscroll>false</autoscroll>
            </control>
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
            <!-- Now: a white line at the current time with TiviMate's dot at its top, what has aired shaded. -->
            <progresstexture border="0,16,18,0" colordiffuse="F2FFFFFF">silo/epg_now.png</progresstexture>
            <!-- The ruler's first cell is the date, above the channels: there, in line
                 with their logos, today and the time in TiviMate's yellow; the
                 others are the times (the only cells with a colon). -->
            <rulerlayout height="%(ruler_h)d" width="1400">
                <control type="label">
                    <left>14</left><width>%(half_hour)d</width><height>%(ruler_h)d</height>
                    <aligny>center</aligny>
                    <font>silo_detail</font>
                    <textcolor>%(dim)s</textcolor>
                    <selectedcolor>%(dim)s</selectedcolor>
                    <label>$INFO[ListItem.Label]</label>
                    <visible>String.Contains(ListItem.Label,:)</visible>
                </control>
                <control type="label">
                    <left>%(date_x)d</left><width>%(date_w)d</width><height>%(ruler_h)d</height>
                    <aligny>center</aligny>
                    <font>silo_detail</font>
                    <textcolor>%(accent)s</textcolor>
                    <selectedcolor>%(accent)s</selectedcolor>
                    <label>$INFO[System.Date(ddd d mmm)]$INFO[System.Time,  ·  ,]</label>
                    <visible>!String.Contains(ListItem.Label,:)</visible>
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
       'pw': PREVIEW_W, 'ph': PREVIEW_H, 'pills_y': PILLS_Y, 'py': (PILLS_Y - PREVIEW_H) // 2,
       'dx': SAFE_X + PREVIEW_W + 48, 'dw': 1920 - 2 * SAFE_X - PREVIEW_W - 48, 'plot_h': PILLS_Y - 194,
       'soft': 'D9EDEDED', 'accent': ACCENT, 'on_now': 'Integer.IsGreater(ListItem.Progress,0) + Integer.IsLess(ListItem.Progress,100)',
       'gw': 1920 - 2 * SAFE_X, 'pill': group_pill(False), 'pill_focused': group_pill(True),
       'grid_y': GRID_Y, 'grid_h': grid_h, 'ruler_h': RULER_H, 'row_h': ROW_H, 'cw': CHANNEL_W,
       'date_x': SAFE_X + 4, 'date_w': CHANNEL_W - SAFE_X - 4,
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
    and the recent channels row show the same. Over the picture: bright text
    with a soft shadow, as TiviMate's reads from the sofa."""
    return '''
            <control type="group">
                <left>%(left)d</left><top>%(top)d</top>
                <control type="label">
                    <width>1400</width><height>36</height>
                    <font>silo_meta</font>
                    <textcolor>%(soft)s</textcolor><shadowcolor>%(shadow)s</shadowcolor>
                    <label>$INFO[VideoPlayer.ChannelNumberLabel,,  ·  ]$INFO[VideoPlayer.ChannelName]</label>
                </control>
                <control type="label">
                    <top>38</top><width>1400</width><height>60</height>
                    <font>silo_osd_title</font>
                    <textcolor>%(text)s</textcolor><shadowcolor>%(shadow)s</shadowcolor>
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
                        <textcolor>%(text)s</textcolor><shadowcolor>%(shadow)s</shadowcolor>
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
                        <textcolor>%(soft)s</textcolor><shadowcolor>%(shadow)s</shadowcolor>
                        <label>$INFO[PVR.EpgEventRemainingTime(mins),, min left]</label>
                        <visible>!String.IsEmpty(VideoPlayer.EndTime)</visible>
                    </control>%(badges)s
                </control>
                <control type="textbox">
                    <top>150</top><width>1300</width><height>66</height>
                    <font>silo_detail</font>
                    <textcolor>%(soft)s</textcolor><shadowcolor>%(shadow)s</shadowcolor>
                    <label>$INFO[VideoPlayer.Plot]</label>
                </control>
                <control type="label">
                    <top>222</top><width>1400</width><height>36</height>
                    <font>silo_meta</font>
                    <textcolor>%(soft)s</textcolor><shadowcolor>%(shadow)s</shadowcolor>
                    <label>$INFO[VideoPlayer.NextStartTime,[COLOR %(text)s]Next[/COLOR]  ,  ]$INFO[VideoPlayer.NextTitle]</label>
                </control>
            </control>''' % {'left': left, 'top': top, 'text': TEXT, 'soft': 'E0EDEDED', 'shadow': 'CC000000',
                                    'badges': stream_badges()}


FPS = (('59.9', '60'), ('60', '60'), ('50', '50'), ('48', '48'), ('29.9', '30'), ('30', '30'), ('25', '25'),
       ('23.9', '24'), ('24', '24'))


def stream_badges():
    """What's playing, as TiviMate's badges: resolution, frame rate, HDR and
    the sound's channels (5.1), in the details page's outlined style."""
    from build_info import badge
    fps = ' | '.join('String.StartsWith(Player.Process(videofps),%s)' % start for start, _ in FPS)
    return ''.join(badge(label, condition, height=34) for label, condition in (
        ('$INFO[VideoPlayer.VideoResolution]$VAR[SiloLiveResolutionSuffix]', '!String.IsEmpty(VideoPlayer.VideoResolution)'),
        ('$VAR[SiloLiveFps] FPS', fps),
        ('$VAR[SiloLiveHdr]', '!String.IsEmpty(VideoPlayer.HdrType)'),
        ('$VAR[SiloLiveAudio]', '!String.IsEmpty(VideoPlayer.AudioChannels)')))


def stream_variables():
    fps = ''.join('        <value condition="String.StartsWith(Player.Process(videofps),%s)">%s</value>\n' % pair for pair in FPS)
    return ('    <variable name="SiloLiveResolutionSuffix">\n'
            '        <value condition="String.IsEqual(VideoPlayer.VideoResolution,4K) | String.IsEqual(VideoPlayer.VideoResolution,8K)"></value>\n'
            '        <value>P</value>\n'
            '    </variable>\n'
            '    <variable name="SiloLiveFps">\n' + fps + '    </variable>\n'
            '    <variable name="SiloLiveHdr">\n'
            '        <value condition="String.IsEqual(VideoPlayer.HdrType,dolbyvision)">DOLBY VISION</value>\n'
            '        <value condition="String.IsEqual(VideoPlayer.HdrType,hdr10plus)">HDR10+</value>\n'
            '        <value condition="String.IsEqual(VideoPlayer.HdrType,hdr10)">HDR10</value>\n'
            '        <value condition="String.IsEqual(VideoPlayer.HdrType,hlg)">HLG</value>\n'
            '        <value>[UPPERCASE]$INFO[VideoPlayer.HdrType][/UPPERCASE]</value>\n'
            '    </variable>\n'
            '    <variable name="SiloLiveAudio">\n'
            '        <value condition="Integer.IsEqual(VideoPlayer.AudioChannels,1)">MONO</value>\n'
            '        <value condition="Integer.IsEqual(VideoPlayer.AudioChannels,2)">2.0</value>\n'
            '        <value condition="Integer.IsEqual(VideoPlayer.AudioChannels,6)">5.1</value>\n'
            '        <value condition="Integer.IsEqual(VideoPlayer.AudioChannels,8)">7.1</value>\n'
            '        <value>$INFO[VideoPlayer.AudioChannels,, CH]</value>\n'
            '    </variable>\n')


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
				<animation effect="slide" start="0,-120" end="0,0" time="220" tween="cubic" easing="out">Visible</animation>
			</control>%(corners)s%(card)s%(info)s
		</control>
		<!-- end Silo Skyline Live TV banner -->
''' % {'recent': RECENT_ID, 'corners': corners(), 'card': channel_card(788), 'info': infobar(776)}


TIMER_START, TIMER_END = '    <!-- Silo Skyline TV (tools/build_tv.py) -->\n', '    <!-- end Silo Skyline TV -->\n'
# The OK screen closes after 5 s without a key (TiviMate: 3 s, too quick from the sofa).
TIMERS = '''    <timer>
        <name>silo_recent_autoclose</name>
        <start reset="true">Window.IsActive(%(window)d)</start>
        <reset>Window.IsActive(%(window)d) + !System.IdleTime(1)</reset>
        <stop>!Window.IsActive(%(window)d) | Integer.IsGreaterOrEqual(Skin.TimerElapsedSecs(silo_recent_autoclose),5)</stop>
        <onstop condition="Window.IsActive(%(window)d)">Dialog.Close(%(window)d)</onstop>
    </timer>
    <timer>
        <name>silo_schedule_now</name>
        <start reset="true">Window.IsActive(pvrosdchannels) + String.IsEqual(Window(Home).Property(silo.sched.want),1) + String.IsEqual(Window(Home).Property(silokodi.schedule_for),Window(Home).Property(silo.sched.number)) + Integer.IsGreater(Container(%(sched)d).NumItems,0) + !Container(%(sched)d).IsUpdating</start>
        <stop>true</stop>
        <onstop>ClearProperty(silo.sched.want,home)</onstop>
        <onstop>SetFocus(%(sched)d,$INFO[Window(Home).Property(silokodi.schedule_now)],absolute)</onstop>
    </timer>
    <!-- Right on a channel with no schedule: back to the channels after 5 s. -->
    <timer>
        <name>silo_schedule_giveup</name>
        <start reset="true">String.IsEqual(Window(Home).Property(silo.sched.want),1)</start>
        <stop>!String.IsEqual(Window(Home).Property(silo.sched.want),1) | Integer.IsGreaterOrEqual(Skin.TimerElapsedSecs(silo_schedule_giveup),5)</stop>
        <onstop>ClearProperty(silo.sched.want,home)</onstop>
    </timer>
    <!-- The day column: the schedule follows the focused day to its first programme, focus staying on the day. -->
    <timer>
        <name>silo_schedule_day</name>
        <start reset="true">Control.HasFocus(%(days)d) + !String.IsEqual(Container(%(days)d).ListItem.Property(silo.day),Container(%(sched)d).ListItem.Property(silo.day))</start>
        <stop>true</stop>
        <onstop>SetFocus(%(sched)d,$INFO[Container(%(days)d).ListItem.Property(silo.first)],absolute)</onstop>
        <onstop>SetFocus(%(days)d)</onstop>
    </timer>
'''


def add_timers():
    path = os.path.join(ROOT, 'xml', 'Timers.xml')
    text = open(path, encoding='utf-8').read()
    if TIMER_START in text:
        text = text[:text.index(TIMER_START)] + text[text.index(TIMER_END) + len(TIMER_END):]
    text = text.replace('</timers>', TIMER_START + TIMERS % {'window': RECENT_ID, 'sched': SCHEDULE_ID, 'days': DAYS_ID} + TIMER_END + '</timers>')
    open(path, 'w', encoding='utf-8').write(text)


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
PANEL = '272A30'             # the panels' grey: the programme card's (silo/menu_panel.png), as TiviMate's match
RECENT_ID = 1196
RECENT_LIST = 5600
ROW_Y = 1080 - 70 - 168 - 84   # the row's top
CARD_W, CARD_H = 300, 168


def quick_row(focused):
    """A channel in the quick guide: logo, number and name, what's on now
    with how far through it; the focused row a white bar, dark text; the
    playing channel's name yellow with TiviMate's ▶."""
    lit = 'Control.HasFocus(11)'

    def row(now_colour, dim_colour, visible):
        return '''
                    <control type="group">%(visible)s
                        <control type="image">
                            <left>%(x)d</left><top>16</top><width>104</width><height>72</height>
                            <aspectratio>keep</aspectratio>
                            <texture fallback="DefaultTVShows.png">$INFO[ListItem.Icon]</texture>
                        </control>
%(name)s
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
                    </control>''' % {'x': SAFE_X - 40, 'tx': SAFE_X + 80, 'tw': QUICK_W - SAFE_X - 150, 'now': now_colour,
                                     'name': two_tone('''
                        <control type="label">
                            <left>%d</left><top>12</top><width>%d</width><height>34</height>
                            <font>silo_detail</font>
                            <textcolor>{colour}</textcolor>
                            <selectedcolor>{colour}</selectedcolor>
                            <label>$INFO[ListItem.ChannelNumberLabel,,  ·  ]$INFO[ListItem.ChannelName]</label>
                            {visible}
                        </control>''' % (SAFE_X + 80, QUICK_W - SAFE_X - 150), dim_colour,
                                                      dim_colour if dim_colour.startswith('B3') else ACCENT, PLAYING),
                                     'visible': '\n                        <visible>%s</visible>' % visible if visible else ''}
    mark = playing_mark(QUICK_W - 66, 18, 28)
    if not focused:
        return row('D9EDEDED', DIM, '') + mark
    bar = '''
                    <control type="image">
                        <left>%d</left><top>4</top><width>%d</width><height>%d</height>
                        <texture border="20" colordiffuse="%s">silo/card_landscape_mask.png</texture>
                        <visible>%s</visible>
                    </control>''' % (SAFE_X - 58, QUICK_W - SAFE_X + 40, QUICK_ROW - 8, TEXT, lit)
    return (bar + row('FF000000', 'B3000000', lit) + row('D9EDEDED', DIM, '!' + lit) +
            playing_mark(QUICK_W - 66, 18, 28, 'FF101010', lit) + playing_mark(QUICK_W - 66, 18, 28, ACCENT, '!' + lit))


SCHEDULE_ID, DAYS_ID = 14, 13
SCHED = 'Window(Home).Property(silo.sched.%s)'
IN_SCHED = 'Control.HasFocus(%d) | Control.HasFocus(%d)' % (SCHEDULE_ID, DAYS_ID)
# The whole schedule on screen: moved into, or Right pressed and it still loading.
SCHED_VIEW = '[%s | String.IsEqual(Window(Home).Property(silo.sched.want),1)]' % IN_SCHED
NOW_ROW = 'String.IsEqual(ListItem.Property(silo.now),1)'
TODAY_ROW = 'String.IsEqual(ListItem.Property(silo.today),1)'
# The whole schedule (Right from a channel), as TiviMate's: the channel list
# slides away, the schedule fills the left with the days beside it.
FULL_X, FULL_W, FULL_ROW = 24, 900, 74
FULL_TOP, FULL_ROWS = 124, 13
DAYS_X, DAYS_W, DAY_ROW = FULL_X + FULL_W + 20, 170, 62
FULL_PANEL = DAYS_X + DAYS_W + 24


def schedule_row(focused=False, width=SCHEDULE_W, height=SCHEDULE_ROW, lit_id=None):
    """A programme in the channel's schedule: its start time and title, the
    one on now yellow with TiviMate's ▶ LIVE, a past one catch-up can play
    with the history icon; a day header where the day changes (today's
    yellow). Focused (lit_id while it has focus), a white bar, dark text."""
    header = 'String.IsEqual(ListItem.Property(silo.header),1)'
    lit = 'Control.HasFocus(%d)' % lit_id if lit_id else 'false'

    def row(time_colour, title_colour, mark_colour, live_colour, visible):
        return '''
                    <control type="group">
                        <visible>!%(header)s%(visible)s</visible>
                        <control type="label">
                            <left>14</left><width>110</width><height>%(h)d</height>
                            <aligny>center</aligny>
                            <font>silo_detail</font>
                            <textcolor>%(time)s</textcolor>
                            <label>$INFO[ListItem.Label2]</label>
                        </control>
%(title)s
                        <control type="image">
                            <left>%(mx)d</left><top>%(my)d</top><width>24</width><height>24</height>
                            <texture colordiffuse="%(mark)s">silo/menu_history.png</texture>
                            <visible>String.IsEqual(ListItem.Property(silo.archive),1)</visible>
                        </control>
                        <control type="label">
                            <left>%(lx)d</left><width>76</width><height>%(h)d</height>
                            <aligny>center</aligny><align>right</align>
                            <font>silo_badge</font>
                            <textcolor>%(live)s</textcolor>
                            <label>▶ LIVE</label>
                            <visible>String.IsEqual(ListItem.Property(silo.now),1)</visible>
                        </control>
                    </control>''' % {'header': header, 'visible': (' + ' + visible) if visible else '', 'h': height,
                                      'time': time_colour, 'title': two_tone('''
                        <control type="label">
                            <left>130</left><width>%d</width><height>%d</height>
                            <aligny>center</aligny>
                            <font>silo_detail</font>
                            <textcolor>{colour}</textcolor>
                            <label>$INFO[ListItem.Label]</label>
                            {visible}
                        </control>''' % (width - 230, height), title_colour,
                                                               title_colour if title_colour == 'FF000000' else ACCENT, NOW_ROW), 'mark': mark_colour, 'live': live_colour,
                                      'tw': width - 230, 'mx': width - 44, 'my': (height - 24) // 2, 'lx': width - 92}
    head = '''
                    <control type="group">
                        <visible>%(header)s</visible>%(label)s
                    </control>''' % {'header': header, 'label': two_tone('''
                        <control type="label">
                            <left>14</left><width>%d</width><height>%d</height>
                            <aligny>center</aligny>
                            <font>silo_detail</font>
                            <textcolor>{colour}</textcolor>
                            <label>$INFO[ListItem.Label]</label>
                            {visible}
                        </control>''' % (width, height), TEXT, ACCENT, TODAY_ROW)}
    rest = row(DIM, 'C7EDEDED', DIM, ACCENT, '!' + lit if focused else '')
    if not focused:
        return head + rest
    bar = '''
                    <control type="image">
                        <top>3</top><width>%(w)d</width><height>%(h)d</height>
                        <texture border="20" colordiffuse="%(text)s">silo/card_landscape_mask.png</texture>
                        <visible>!%(header)s + %(lit)s</visible>
                    </control>''' % {'w': width, 'h': height - 6, 'text': TEXT, 'header': header, 'lit': lit}
    return bar + head + row('B3000000', 'FF000000', 'FF000000', 'FF000000', lit) + rest


def day_row(focused):
    """A day in the schedule's day column: today yellow, the focused
    programme's day on a soft pill; focused, a white pill."""
    lit = 'Control.HasFocus(%d)' % DAYS_ID
    shown = 'String.IsEqual(ListItem.Property(silo.day),Container(%d).ListItem.Property(silo.day))' % SCHEDULE_ID
    soft = '''
                    <control type="image">
                        <top>3</top><width>%(w)d</width><height>%(h)d</height>
                        <texture border="20" colordiffuse="2EFFFFFF">silo/card_landscape_mask.png</texture>
                        <visible>%(shown)s%(not_lit)s</visible>
                    </control>''' % {'w': DAYS_W, 'h': DAY_ROW - 6, 'shown': shown, 'not_lit': ' + !' + lit if focused else ''}
    pill = '''
                    <control type="image">
                        <top>3</top><width>%(w)d</width><height>%(h)d</height>
                        <texture border="20" colordiffuse="%(text)s">silo/card_landscape_mask.png</texture>
                        <visible>%(lit)s</visible>
                    </control>''' % {'w': DAYS_W, 'h': DAY_ROW - 6, 'text': TEXT, 'lit': lit} if focused else ''

    def label(colour, visible):
        control = '''
                    <control type="label">
                        <width>%(w)d</width><height>%(h)d</height>
                        <align>center</align><aligny>center</aligny>
                        <font>silo_detail</font>
                        <textcolor>{colour}</textcolor>
                        <label>$INFO[ListItem.Label]</label>
                        {visible}
                    </control>''' % {'w': DAYS_W, 'h': DAY_ROW}
        today = TODAY_ROW + (' + ' + visible if visible else '')
        if colour == 'FF000000':
            return control.replace('{colour}', colour).replace('{visible}', '<visible>%s</visible>' % visible)
        return (control.replace('{colour}', ACCENT).replace('{visible}', '<visible>%s</visible>' % today) +
                control.replace('{colour}', colour).replace('{visible}', '<visible>!%s%s</visible>' % (
                    TODAY_ROW, ' + ' + visible if visible else '')))
    if not focused:
        return soft + label('C7EDEDED', '')
    return soft + pill + label('FF000000', lit) + label('C7EDEDED', '!' + lit)


def programme_card(item, timeline, visible):
    """The focused programme, as TiviMate's card at the top right: title,
    times with how far through (or, in the schedule, its day and the
    catch-up icon), and plot."""
    return '''
        <control type="group">
            <left>%(cx)d</left><top>48</top>
            <visible>%(visible)s</visible>
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
                <label fallback="19055">%(title)s</label>
            </control>
            <control type="grouplist">
                <left>30</left><top>126</top><width>%(cw2)d</width><height>34</height>
                <orientation>horizontal</orientation>
                <itemgap>18</itemgap>%(timeline)s
            </control>
            <control type="textbox">
                <left>30</left><top>170</top><width>%(cw2)d</width><height>66</height>
                <font>silo_detail</font>
                <textcolor>B3EDEDED</textcolor>
                <label>%(plot)s</label>
            </control>
        </control>''' % {'cx': 1920 - SAFE_X - CARD_PANEL_W, 'cw': CARD_PANEL_W, 'cw2': CARD_PANEL_W - 60, 'text': TEXT,
                         'visible': visible, 'timeline': timeline,
                         'title': '$INFO[%s.Title]' % item if item.startswith('Container(11)') else '$INFO[%s.Label]' % item,
                         'plot': '$INFO[%s.Plot]' % item if item.startswith('Container(11)') else '$INFO[%s.Property(silo.plot)]' % item}


def build_quick_guide():
    """Kodi's channel list while Live TV plays (DialogPVRChannelsOSD; Left in
    our keymap), as TiviMate's: the channels down the left, the focused
    channel's schedule beside them (SiloKodiConnect's mode=schedule), and its
    programme in a card at the top right, the video playing on behind. Right
    slides the channels away for the whole schedule and its days. Kodi
    switches to the chosen channel."""
    focused = 'Container(11).ListItem'
    sched = 'Container(%d).ListItem' % SCHEDULE_ID
    now_timeline = '''
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
                </control>''' % {'text': TEXT, 'f': focused}
    sched_timeline = '''
                <control type="label">
                    <width>auto</width><height>34</height>
                    <aligny>center</aligny>
                    <font>silo_detail</font>
                    <textcolor>%(text)s</textcolor>
                    <label>$INFO[%(s)s.Property(silo.timeline)]</label>
                </control>
                <control type="image">
                    <top>5</top><width>24</width><height>24</height>
                    <texture colordiffuse="%(dim)s">silo/menu_history.png</texture>
                    <visible>String.IsEqual(%(s)s.Property(silo.archive),1)</visible>
                </control>''' % {'text': TEXT, 'dim': DIM, 's': sched}
    return '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by tools/build_tv.py: edit that, not this. -->
<window>
    <defaultcontrol always="true">11</defaultcontrol>
    <controls>
        <control type="group">
            <animation effect="slide" start="-%(sx_end)d,0" end="0,0" time="220" tween="cubic" easing="out">WindowOpen</animation>
            <animation effect="slide" start="0,0" end="-%(sx_end)d,0" time="160" tween="cubic" easing="in">WindowClose</animation>
            <!-- The channels and their short schedule: slid away while the whole schedule is open. -->
            <control type="group">
                <animation effect="slide" end="-%(sx_end)d,0" time="220" tween="cubic" easing="out" condition="%(view)s">Conditional</animation>
                <animation effect="fade" end="0" time="220" condition="%(view)s">Conditional</animation>
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
                    <!-- Right: into this channel's whole schedule, catch-up included (TiviMate's). -->
                    <onright>SetProperty(silo.sched.number,$INFO[Container(11).ListItem.ChannelNumberLabel],home)</onright>
                    <onright>SetProperty(silo.sched.name,$INFO[Container(11).ListItem.ChannelName],home)</onright>
                    <!-- Loaded already (the channel rested on): straight to what's on now. Else, as
                         Kodi can't focus an empty list, a timer does once it has loaded. -->
                    <onright condition="%(loaded)s">SetFocus(%(sched_id)d,$INFO[Window(Home).Property(silokodi.schedule_now)],absolute)</onright>
                    <onright condition="!%(loaded)s">SetProperty(silo.sched.want,1,home)</onright>
                    <focusposition>3</focusposition>
                    <movement>3</movement>
                    <orientation>vertical</orientation>
                    <scrolltime tween="cubic" easing="out">200</scrolltime>
                    <itemlayout width="%(w)d" height="%(row)d">%(item)s
                    </itemlayout>
                    <focusedlayout width="%(w)d" height="%(row)d">%(item_focused)s
                    </focusedlayout>
                </control>
                <!-- The focused channel's schedule, from just before what's on now. -->
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
                        <itemlayout width="%(sw2)d" height="%(srow)d">%(short)s
                        </itemlayout>
                        <focusedlayout width="%(sw2)d" height="%(srow)d">%(short)s
                        </focusedlayout>
                    </control>
                </control>
            </control>
            <!-- The whole schedule, as TiviMate's: in from the right as the channels go. Never
                 hidden (Kodi can't focus a hidden list), only faded out until Right. -->
            <control type="group">
                <animation effect="fade" start="100" end="0" time="0" condition="!%(view)s">Conditional</animation>
                <animation effect="slide" start="%(w)d,0" end="0,0" time="220" tween="cubic" easing="out" condition="%(view)s">Conditional</animation>
                <control type="image">
                    <left>0</left><top>0</top><width>%(panel)d</width><height>1080</height>
                    <texture colordiffuse="F2%(bg)s">colors/white.png</texture>
                </control>
                <control type="image">
                    <left>%(panel)d</left><top>0</top><width>200</width><height>1080</height>
                    <texture colordiffuse="CC%(bg)s">silo/scrim_side.png</texture>
                </control>
                <control type="image">
                    <left>%(x)d</left><top>26</top><width>120</width><height>72</height>
                    <aspectratio align="left">keep</aspectratio>
                    <texture>$INFO[%(f)s.Icon]</texture>
                </control>
                <control type="label">
                    <left>%(hx)d</left><top>22</top><width>%(hw)d</width><height>44</height>
                    <font>silo_meta</font>
                    <textcolor>%(text)s</textcolor>
                    <label>$INFO[%(f)s.ChannelNumberLabel,,  ]$INFO[%(f)s.ChannelName]</label>
                </control>
                <control type="label">
                    <left>%(hx)d</left><top>64</top><width>%(hw)d</width><height>36</height>
                    <font>silo_detail</font>
                    <textcolor>%(dim)s</textcolor>
                    <label>$INFO[VideoPlayer.ChannelGroup]</label>
                </control>
                <control type="fixedlist" id="%(sched_id)d">
                    <left>%(fx)d</left><top>%(ft)d</top><width>%(fw)d</width><height>%(fh)d</height>
                    <orientation>vertical</orientation>
                    <focusposition>5</focusposition>
                    <movement>5</movement>
                    <scrolltime tween="cubic" easing="out">160</scrolltime>
                    <onleft>11</onleft>
                    <!-- Into the days at this programme's (TiviMate's); neither list wraps round. -->
                    <onright>SetFocus(%(days_id)d,$INFO[Container(%(sched_id)d).ListItem.Property(silo.day)],absolute)</onright>
                    <onup>noop</onup>
                    <ondown>noop</ondown>
                    <content target="videos">$VAR[SiloSchedulePath]</content>
                    <onclick condition="!String.IsEmpty(ListItem.Property(silo.when)) + !String.IsEqual(ListItem.Property(silo.when),future)">Dialog.Close(pvrosdchannels)</onclick>
                    <onclick condition="!String.IsEmpty(ListItem.Property(silo.when)) + !String.IsEqual(ListItem.Property(silo.when),future)">RunPlugin(plugin://plugin.video.silokodiconnect/?mode=play_broadcast&amp;id=$INFO[ListItem.Property(silo.broadcastid)]&amp;channel=$INFO[ListItem.Property(silo.channelid)]&amp;when=$INFO[ListItem.Property(silo.when)])</onclick>
                    <itemlayout width="%(fw)d" height="%(frow)d">%(full)s
                    </itemlayout>
                    <focusedlayout width="%(fw)d" height="%(frow)d">%(full_focused)s
                    </focusedlayout>
                </control>
                <!-- The days, TiviMate's column: moving to one takes the schedule there
                     (a timer: Kodi's lists run nothing as they move); Left goes into it. -->
                <control type="list" id="%(days_id)d">
                    <left>%(dx)d</left><top>%(ft)d</top><width>%(dw)d</width><height>%(dh)d</height>
                    <orientation>vertical</orientation>
                    <onleft>%(sched_id)d</onleft>
                    <onup>noop</onup>
                    <ondown>noop</ondown>
                    <content target="videos">$VAR[SiloScheduleDaysPath]</content>
                    <itemlayout width="%(dw)d" height="%(drow)d">%(day)s
                    </itemlayout>
                    <focusedlayout width="%(dw)d" height="%(drow)d">%(day_focused)s
                    </focusedlayout>
                </control>
            </control>
        </control>%(card)s%(sched_card)s
        <include>PVRChannelNumberInput</include>
    </controls>
</window>
''' % {'w': QUICK_W, 'sw': SCHEDULE_W + 60, 'sx': QUICK_W + 30, 'sx_end': QUICK_W + SCHEDULE_W + 60,
       'bg': PANEL, 'x': SAFE_X - 40, 'lw': QUICK_W - SAFE_X, 'text': TEXT, 'dim': DIM,
       'lh': QUICK_ROW * 9, 'row': QUICK_ROW, 'item': quick_row(False), 'item_focused': quick_row(True),
       'f': focused, 'stw': SCHEDULE_W - 120, 'sw2': SCHEDULE_W, 'sh': SCHEDULE_ROW * 15, 'srow': SCHEDULE_ROW,
       'short': schedule_row(), 'sched_id': SCHEDULE_ID, 'days_id': DAYS_ID, 'in_sched': IN_SCHED, 'view': SCHED_VIEW,
       'loaded': '[String.IsEqual(Window(Home).Property(silokodi.schedule_for),Container(11).ListItem.ChannelNumberLabel) + '
                 'Integer.IsGreater(Container(%d).NumItems,0) + !Container(%d).IsUpdating]' % (SCHEDULE_ID, SCHEDULE_ID),
       'panel': FULL_PANEL, 'hx': SAFE_X + 100, 'hw': FULL_W - SAFE_X - 100,
       'fx': FULL_X, 'ft': FULL_TOP, 'fw': FULL_W, 'fh': FULL_ROW * FULL_ROWS, 'frow': FULL_ROW,
       'full': schedule_row(False, FULL_W, FULL_ROW, SCHEDULE_ID),
       'full_focused': schedule_row(True, FULL_W, FULL_ROW, SCHEDULE_ID),
       'dx': DAYS_X, 'dw': DAYS_W, 'dh': DAY_ROW * 15, 'drow': DAY_ROW,
       'day': day_row(False), 'day_focused': day_row(True),
       'card': programme_card(focused, now_timeline, '![%s]' % IN_SCHED),
       'sched_card': programme_card(sched, sched_timeline,
                                    '[%s] + String.IsEmpty(%s.Property(silo.header))' % (IN_SCHED, sched))}


def quick_variables():
    """The quick guide's labels: the schedule's addresses and what's on now
    (TiviMate's "No information")."""
    # The channel moved into (Right sets silo.sched.*); before that, the one
    # the channel list has rested on a second, so Right finds it loaded (the
    # address is the same, so Kodi doesn't fetch it again).
    path = 'plugin://plugin.video.silokodiconnect/?mode=%s&amp;number=$INFO[%s]&amp;name=$INFO[%s]'
    paths = ''.join('    <variable name="%s">\n'
                    '        <value condition="%s">%s</value>\n'
                    '        <value condition="Control.HasFocus(11) + System.IdleTime(1)">%s</value>\n'
                    '        <value condition="!String.IsEmpty(%s)">%s</value>\n'
                    '    </variable>\n' % (name, SCHED_VIEW, path % (mode, SCHED % 'number', SCHED % 'name'),
                                         path % (mode, 'Container(11).ListItem.ChannelNumberLabel', 'Container(11).ListItem.ChannelName'),
                                         SCHED % 'number', path % (mode, SCHED % 'number', SCHED % 'name'))
                    for name, mode in (('SiloSchedulePath', 'schedule&amp;full=1'), ('SiloScheduleDaysPath', 'schedule_days')))
    return paths + ('    <variable name="SiloQuickNow">\n'
            '        <value condition="String.IsEmpty(ListItem.Title)">No information</value>\n'
            '        <value>$INFO[ListItem.Title]</value>\n'
            '    </variable>\n')


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
                        <info>ListItem.Property(silo.progress)</info>
                    </control>%(sheen)s
                    <control type="label">
                        <left>6</left><top>%(t1)d</top><width>%(w)d</width><height>34</height>
                        <font>silo_card_title</font>
                        <textcolor>%(title)s</textcolor>
                        <selectedcolor>%(title)s</selectedcolor>
                        <label>$INFO[ListItem.Property(silo.channel)]</label>
                    </control>
                    <control type="label">
                        <left>6</left><top>%(t2)d</top><width>%(w)d</width><height>30</height>
                        <font>silo_card_sub</font>
                        <textcolor>%(sub)s</textcolor>
                        <selectedcolor>%(sub)s</selectedcolor>
                        <label>$INFO[ListItem.Property(silo.now)]</label>
                    </control>
                </control>''' % {'zoom': focus_zoom(lit, 16) if focused else '', 'w': CARD_W, 'h': CARD_H,
                                  'lw': CARD_W - 60, 'lh': CARD_H - 60, 'py': CARD_H - 12, 'pw': CARD_W - 36,
                                  'sheen': focus_sheen(CARD_W, CARD_H, 'silo/card_landscape_mask.png',
                                                       'silo/card_landscape_rim.png', lit, 16) if focused else '',
                                  't1': CARD_H + 20, 't2': CARD_H + 54, 'text': TEXT,
                                  'title': TEXT if focused else 'D9EDEDED', 'sub': 'D9EDEDED' if focused else 'A6EDEDED'}


def build_recent():
    """While Live TV plays (OK in our keymap), as TiviMate's: what's playing
    (the infobar), then the recently watched channels in a row along the
    bottom. OK switches to one; Back closes it. The shade reaches up behind
    the infobar, so its text reads over a bright picture."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by tools/build_tv.py: edit that, not this. -->
<window id="%(window)d" type="dialog">
    <defaultcontrol always="true">%(list)d</defaultcontrol>
    <controls>
        <!-- The top's shade and corners fade in place (sliding, the shade crossed the picture). -->
        <control type="group">
            <animation effect="fade" start="0" end="100" time="220">WindowOpen</animation>
            <animation effect="fade" start="100" end="0" time="160">WindowClose</animation>
            <control type="image">
                <left>0</left><top>0</top><width>1920</width><height>200</height>
                <texture flipy="true">silo/scrim_bottom.png</texture>
            </control>%(corners)s
        </control>
        <control type="group">
            <animation effect="slide" start="0,320" end="0,0" time="220" tween="cubic" easing="out">WindowOpen</animation>
            <animation effect="slide" start="0,0" end="0,320" time="160" tween="cubic" easing="in">WindowClose</animation>
            <control type="image">
                <left>0</left><top>160</top><width>1920</width><height>920</height>
                <texture colordiffuse="F2%(bg)s">silo/scrim_bottom.png</texture>
            </control>
            <control type="image">
                <left>0</left><top>380</top><width>1920</width><height>700</height>
                <texture colordiffuse="F2%(bg)s">silo/scrim_bottom.png</texture>
            </control>%(info)s
            <control type="list" id="%(list)d">
                <left>%(lx)d</left><top>%(ly)d</top><width>%(lw)d</width><height>%(ih)d</height>
                <orientation>horizontal</orientation>
                <scrolltime tween="cubic" easing="out">200</scrolltime>
                <!-- SiloKodiConnect's recent channels: newest first, not the playing one, none
                     the viewer removed (the long-press menu); silokodi.recent_changed reloads it. -->
                <content target="videos">plugin://plugin.video.silokodiconnect/?mode=recent_channels&amp;v=$INFO[Window(Home).Property(silokodi.recent_changed)]</content>
                <onclick>Dialog.Close(%(window)d)</onclick>
                <onclick>RunPlugin(plugin://plugin.video.silokodiconnect/?mode=play_channel&amp;id=$INFO[ListItem.Property(silo.channelid)])</onclick>
                <itemlayout width="%(iw)d" height="%(ih)d">%(card)s
                </itemlayout>
                <focusedlayout width="%(iw)d" height="%(ih)d">%(card_focused)s
                </focusedlayout>
            </control>
        </control>
    </controls>
</window>
''' % {'window': RECENT_ID, 'list': RECENT_LIST, 'bg': BACKGROUND[2:], 'text': TEXT,
       'corners': corners(), 'info': infobar(ROW_Y - 290, SAFE_X),
       'lx': SAFE_X - 6, 'ly': ROW_Y, 'lw': 1920 - SAFE_X, 'iw': CARD_W + 40, 'ih': CARD_H + 12 + 84,
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
    add_timers()
    add_variables()
    print('Wrote xml/MyPVRGuide.xml, DialogPVRInfo.xml and their variables in xml/Variables.xml')
