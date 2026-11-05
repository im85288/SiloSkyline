#!/usr/bin/env python3
"""Write xml/DialogPlayerProcessInfo.xml and xml/VideoOSDBookmarks.xml: the
player's details and its chapters, in Silo's look, as its Options panel:

    python3 tools/build_playback.py

Player details (Options' "Player details", the O key): one solid panel with
what's playing and how, in columns, rather than Estuary's see-through strip of
tabs. HDR is there, which is what it's mostly opened for. Live TV swaps the
system column for the channel's stream. Any key closes it.

Chapters (Options' "All chapters"): a list of a title's chapters and bookmarks,
the time then the name, on the chapter playing (a timer focuses it, as Kodi
fills it only after the window has chosen its focus). Estuary's row of pictures
showed one identical camera per chapter, as a chapter has no picture, and
opened on Create bookmark, one OK from adding one by accident. A bookmark's
picture shows at its row's end.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_home import ROOT, TEXT, TEXT_DIM  # noqa: E402

CARD = 'FF131417'  # Silo's dialog card, as the Options panel
DARK = 'FF000000'
PANEL_X, PANEL_W = 180, 1560
PANEL_TOP = 150
MARGIN = 60
COL_GAP = 56
COLS = 3
COL_W = (PANEL_W - 2 * MARGIN - (COLS - 1) * COL_GAP) // COLS
LABEL_W = 150
ROW_H = 48
HEADING_H = 52
DETAILS_ROWS = 9
DETAILS_H = 2 * 44 + HEADING_H + DETAILS_ROWS * ROW_H

# (label, value, shows when): a row with no value leaves its column.
VIDEO = [
    ('Resolution', '$INFO[Player.Process(videowidth),,x]$INFO[Player.Process(videoheight)]', '!String.IsEmpty(Player.Process(videowidth))'),
    ('Frame rate', '$INFO[Player.Process(videofps),, fps]', '!String.IsEmpty(Player.Process(videofps))'),
    ('HDR', '[UPPERCASE]$INFO[VideoPlayer.HdrType][/UPPERCASE]', '!String.IsEmpty(VideoPlayer.HdrType)'),
    ('Codec', '[UPPERCASE]$INFO[VideoPlayer.VideoCodec][/UPPERCASE]', '!String.IsEmpty(VideoPlayer.VideoCodec)'),
    ('Bitrate', '$INFO[VideoPlayer.VideoBitrate,, kb/s]', '!String.IsEmpty(VideoPlayer.VideoBitrate)'),
    ('Aspect', '$INFO[VideoPlayer.VideoAspect,,:1]', '!String.IsEmpty(VideoPlayer.VideoAspect)'),
    ('Decoder', '$INFO[Player.Process(videodecoder)]$VAR[VideoHWDecoder, · ,]', '!String.IsEmpty(Player.Process(videodecoder))'),
    ('Pixels', '$INFO[Player.Process(pixformat)]', '!String.IsEmpty(Player.Process(pixformat))'),
    ('Deinterlace', '$INFO[Player.Process(deintmethod)]', '!String.IsEmpty(Player.Process(deintmethod))'),
]
AUDIO = [
    ('Language', '$INFO[VideoPlayer.AudioLanguage]', '!String.IsEmpty(VideoPlayer.AudioLanguage)'),
    ('Codec', '[UPPERCASE]$INFO[VideoPlayer.AudioCodec][/UPPERCASE]', '!String.IsEmpty(VideoPlayer.AudioCodec)'),
    ('Channels', '$INFO[VideoPlayer.AudioChannels]', '!String.IsEmpty(VideoPlayer.AudioChannels)'),
    ('Bitrate', '$INFO[VideoPlayer.AudioBitrate,, kb/s]', '!String.IsEmpty(VideoPlayer.AudioBitrate)'),
    ('Decoder', '$INFO[Player.Process(audiodecoder)]', '!String.IsEmpty(Player.Process(audiodecoder))'),
    ('Sample rate', '$INFO[Player.Process(audiosamplerate),, Hz]', '!String.IsEmpty(Player.Process(audiosamplerate))'),
    ('Bit depth', '$INFO[Player.Process(audiobitspersample),, bit]', '!String.IsEmpty(Player.Process(audiobitspersample))'),
]
SYSTEM = [
    ('Screen', '$INFO[System.ScreenMode]', '!String.IsEmpty(System.ScreenMode)'),
    ('Drawing', '$INFO[System.FPS,, fps]', 'true'),
    # Android doesn't report it (Kodi says "Not available"); CoreELEC does.
    ('CPU', '$INFO[System.CpuUsage]', '!String.IsEmpty(System.CpuUsage) + !String.Contains(System.CpuUsage,available)'),
    ('Memory', '$INFO[System.Memory(used.percent)]', '!String.IsEmpty(System.Memory(used.percent))'),
]
CHANNEL = [
    ('Service', '$INFO[PVR.ActStreamServiceName]', '!String.IsEmpty(PVR.ActStreamServiceName)'),
    ('Provider', '$INFO[PVR.ActStreamProviderName]', '!String.IsEmpty(PVR.ActStreamProviderName)'),
    ('Client', '$INFO[PVR.ActStreamClient]', '!String.IsEmpty(PVR.ActStreamClient)'),
    ('Device', '$INFO[PVR.ActStreamDevice]', '!String.IsEmpty(PVR.ActStreamDevice)'),
    ('Status', '$INFO[PVR.ActStreamStatus]', '!String.IsEmpty(PVR.ActStreamStatus)'),
    ('Encryption', '$INFO[PVR.ActStreamEncryptionName]', '!String.IsEmpty(PVR.ActStreamEncryptionName)'),
    ('Signal', '$INFO[PVR.ActStreamSignal]', '!String.IsEmpty(PVR.ActStreamSignal)'),
    ('Quality', '$INFO[PVR.ActStreamSNR]', '!String.IsEmpty(PVR.ActStreamSNR)'),
]


def detail_row(label, value, shows):
    return """
                <control type="group">
                    <height>%(h)d</height>
                    <visible>%(shows)s</visible>
                    <control type="label">
                        <width>%(lw)d</width><height>%(h)d</height>
                        <aligny>center</aligny>
                        <font>silo_detail</font>
                        <textcolor>%(dim)s</textcolor>
                        <label>%(label)s</label>
                    </control>
                    <control type="label">
                        <left>%(lw)d</left><width>%(vw)d</width><height>%(h)d</height>
                        <align>right</align><aligny>center</aligny>
                        <font>silo_detail</font>
                        <textcolor>%(text)s</textcolor>
                        <label>%(value)s</label>
                        <scroll>true</scroll><scrollspeed>30</scrollspeed>
                    </control>
                </control>""" % {'h': ROW_H, 'shows': shows, 'lw': LABEL_W, 'vw': COL_W - LABEL_W, 'dim': TEXT_DIM,
                                 'label': label, 'text': TEXT, 'value': value}


def column(index, heading, rows, visible='true'):
    return """
        <control type="group">
            <left>%(x)d</left><top>%(top)d</top><width>%(w)d</width>
            <visible>%(visible)s</visible>
            <control type="label">
                <width>%(w)d</width><height>%(hh)d</height>
                <font>silo_badge</font>
                <textcolor>99EDEDED</textcolor>
                <label>%(heading)s</label>
            </control>
            <control type="grouplist">
                <top>%(hh)d</top><width>%(w)d</width><height>%(gh)d</height>
                <orientation>vertical</orientation>
                <usecontrolcoords>true</usecontrolcoords>%(rows)s
            </control>
        </control>""" % {'x': PANEL_X + MARGIN + index * (COL_W + COL_GAP), 'top': PANEL_TOP + 44, 'w': COL_W, 'visible': visible,
                         'hh': HEADING_H, 'heading': heading, 'gh': DETAILS_ROWS * ROW_H,
                         'rows': ''.join(detail_row(*row) for row in rows)}


def player_details():
    live = 'VideoPlayer.Content(livetv)'
    return """<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by tools/build_playback.py: edit that, not this. -->
<window>
    <depth>DepthOSD</depth>
    <defaultcontrol always="true">5550</defaultcontrol>
    <animation effect="fade" start="0" end="100" time="200">WindowOpen</animation>
    <animation effect="fade" start="100" end="0" time="150">WindowClose</animation>
    <controls>
        <control type="image">
            <left>%(x)d</left><top>%(top)d</top><width>%(w)d</width><height>%(h)d</height>
            <texture border="24" colordiffuse="%(card)s">silo/card_landscape_mask.png</texture>
        </control>%(video)s%(audio)s%(system)s%(channel)s
        <!-- Nothing to choose here: any key closes it. -->
        <control type="button" id="5550">
            <left>-10</left><top>-10</top><width>1</width><height>1</height>
            <texturefocus /><texturenofocus />
            <onup>Action(Close)</onup><ondown>Action(Close)</ondown>
            <onleft>Action(Close)</onleft><onright>Action(Close)</onright>
            <onclick>Action(Close)</onclick>
        </control>
    </controls>
</window>
""" % {'x': PANEL_X, 'top': PANEL_TOP, 'w': PANEL_W, 'h': DETAILS_H, 'card': CARD, 'video': column(0, 'VIDEO', VIDEO),
       'audio': column(1, 'AUDIO', AUDIO), 'system': column(2, 'SYSTEM', SYSTEM, '!' + live),
       'channel': column(2, 'CHANNEL', CHANNEL, live)}


LIST_ID, BUTTONS_ID = 11, 9001
CHAPTERS_H = 1080 - PANEL_TOP - 60
LIST_TOP = PANEL_TOP + 44 + HEADING_H
LIST_X = PANEL_X + 28
LIST_W = 1040
CHAPTER_ROW = 72
TIME_W = 150
THUMB_W, THUMB_H = 96, 54
BUTTON_W = PANEL_W - (LIST_X - PANEL_X) - LIST_W - 2 * 40


def chapter_row(focused):
    pill = """
                    <control type="image">
                        <width>%d</width><height>%d</height>
                        <texture border="30" colordiffuse="%s">silo/pill.png</texture>
                        <visible>Control.HasFocus(%d)</visible>
                    </control>""" % (LIST_W, CHAPTER_ROW - 8, TEXT, LIST_ID) if focused else ''
    text = '$VAR[SiloChapterText]' if focused else TEXT
    dim = '$VAR[SiloChapterDim]' if focused else TEXT_DIM
    return """%(pill)s
                    <control type="label">
                        <left>32</left><width>%(tw)d</width><height>%(h)d</height>
                        <aligny>center</aligny>
                        <font>silo_detail</font>
                        <textcolor>%(dim)s</textcolor>
                        <label>$INFO[ListItem.Label2]</label>
                    </control>
                    <control type="label">
                        <left>%(lx)d</left><width>%(lw)d</width><height>%(h)d</height>
                        <aligny>center</aligny>
                        <font>silo_meta</font>
                        <textcolor>%(text)s</textcolor>
                        <label>$INFO[ListItem.Label]</label>
                    </control>
                    <!-- A bookmark's picture; a chapter has none. -->
                    <control type="image">
                        <left>%(ix)d</left><top>%(iy)d</top><width>%(iw)d</width><height>%(ih)d</height>
                        <aspectratio>scale</aspectratio>
                        <texture background="true" diffuse="silo/card_landscape_mask.png">$INFO[ListItem.Art(thumb)]</texture>
                        <visible>!String.IsEmpty(ListItem.Art(thumb))</visible>
                    </control>""" % {
        'pill': pill, 'tw': TIME_W, 'h': CHAPTER_ROW - 8, 'dim': dim, 'lx': 32 + TIME_W + 16, 'text': text,
        'lw': LIST_W - (32 + TIME_W + 16) - THUMB_W - 48, 'ix': LIST_W - THUMB_W - 32, 'iy': (CHAPTER_ROW - 8 - THUMB_H) // 2,
        'iw': THUMB_W, 'ih': THUMB_H}


def chapter_button(control_id, label, visible=''):
    return """
                <include content="DefaultDialogButton">
                    <param name="id" value="%d" />
                    <param name="label" value="%s" />
                    <param name="width" value="%d" />%s
                </include>""" % (control_id, label, BUTTON_W, '\n                    <param name="visible" value="%s" />' % visible if visible else '')


def chapters():
    return """<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by tools/build_playback.py: edit that, not this. -->
<window>
    <defaultcontrol always="true">%(list)d</defaultcontrol>
    <animation effect="fade" start="0" end="100" time="200">WindowOpen</animation>
    <animation effect="fade" start="100" end="0" time="150">WindowClose</animation>
    <controls>
        <control type="image">
            <left>%(x)d</left><top>%(top)d</top><width>%(w)d</width><height>%(h)d</height>
            <texture border="24" colordiffuse="%(card)s">silo/card_landscape_mask.png</texture>
        </control>
        <control type="label">
            <left>%(hx)d</left><top>%(ht)d</top><width>%(lw)d</width><height>%(hh)d</height>
            <font>silo_badge</font>
            <textcolor>99EDEDED</textcolor>
            <label>$INFO[Container(%(list)d).NumItems,CHAPTERS AND BOOKMARKS · ,]</label>
        </control>
        <control type="label">
            <left>%(hx)d</left><top>%(lt)d</top><width>%(lw)d</width><height>%(row)d</height>
            <aligny>center</aligny>
            <font>silo_meta</font>
            <textcolor>%(dim)s</textcolor>
            <label>$LOCALIZE[31155]</label>
            <visible>Integer.IsEqual(Container(%(list)d).NumItems,0)</visible>
        </control>
        <control type="list" id="%(list)d">
            <left>%(lx)d</left><top>%(lt)d</top><width>%(lw)d</width><height>%(lh)d</height>
            <orientation>vertical</orientation>
            <scrolltime tween="cubic" easing="out">200</scrolltime>
            <onleft>noop</onleft><onright>%(buttons)d</onright>
            <itemlayout width="%(lw)d" height="%(row)d">%(item)s
            </itemlayout>
            <focusedlayout width="%(lw)d" height="%(row)d">%(item_focused)s
            </focusedlayout>
        </control>
        <control type="grouplist" id="%(buttons)d">
            <left>%(bx)d</left><top>%(lt)d</top><width>%(bw)d</width><height>400</height>
            <orientation>vertical</orientation>
            <itemgap>8</itemgap>
            <onleft>%(list)d</onleft><onright>noop</onright><onup>noop</onup><ondown>noop</ondown>%(button_xml)s
        </control>
    </controls>
</window>
""" % {'list': LIST_ID, 'buttons': BUTTONS_ID, 'x': PANEL_X, 'top': PANEL_TOP, 'w': PANEL_W, 'h': CHAPTERS_H, 'card': CARD,
       'hx': LIST_X + 32, 'ht': PANEL_TOP + 44, 'hh': HEADING_H, 'lw': LIST_W, 'lx': LIST_X, 'lt': LIST_TOP, 'row': CHAPTER_ROW,
       'lh': PANEL_TOP + CHAPTERS_H - LIST_TOP - 28, 'dim': TEXT_DIM, 'item': chapter_row(False), 'item_focused': chapter_row(True),
       'bx': LIST_X + LIST_W + 40, 'bw': BUTTON_W,
       'button_xml': chapter_button(2, '$LOCALIZE[294]') + chapter_button(3, '$LOCALIZE[296]')
       + chapter_button(4, '$LOCALIZE[20406]', 'Control.IsEnabled(4)')}


VARIABLES = """
    <!-- Silo Skyline playback (tools/build_playback.py) -->
    <variable name="SiloChapterText">
        <value condition="Control.HasFocus(%(list)d)">%(dark)s</value>
        <value>%(text)s</value>
    </variable>
    <variable name="SiloChapterDim">
        <value condition="Control.HasFocus(%(list)d)">99000000</value>
        <value>%(dim)s</value>
    </variable>
    <!-- end Silo Skyline playback -->
""" % {'list': LIST_ID, 'dark': DARK, 'text': TEXT, 'dim': TEXT_DIM}


TIMER_START, TIMER_END = '    <!-- Silo Skyline playback (tools/build_playback.py) -->\n', '    <!-- end Silo Skyline playback -->\n'
TIMER = TIMER_START + """    <timer>
        <name>silo_chapters_focus</name>
        <description>Focus the chapter list: Kodi fills it after choosing the window's focus, so its default control can't take it</description>
        <start reset="true">Window.IsActive(videobookmarks) + Integer.IsGreater(Container(%(list)d).NumItems,0) + !Control.HasFocus(%(list)d) + !ControlGroup(%(buttons)d).HasFocus()</start>
        <stop>Integer.IsGreaterOrEqual(Skin.TimerElapsedSecs(silo_chapters_focus),0)</stop>
        <onstop condition="Window.IsActive(videobookmarks)">SetFocus(%(list)d)</onstop>
    </timer>
""" % {'list': LIST_ID, 'buttons': BUTTONS_ID} + TIMER_END


def add_timer():
    path = os.path.join(ROOT, 'xml', 'Timers.xml')
    text = open(path, encoding='utf-8').read()
    if TIMER_START in text:
        text = text[:text.index(TIMER_START)] + text[text.index(TIMER_END) + len(TIMER_END):]
    text = text.replace('</timers>', TIMER + '</timers>')
    open(path, 'w', encoding='utf-8').write(text)


def add_variables():
    path = os.path.join(ROOT, 'xml', 'Variables.xml')
    text = open(path, encoding='utf-8').read()
    start, end = '    <!-- Silo Skyline playback (tools/build_playback.py) -->', '    <!-- end Silo Skyline playback -->\n'
    if start in text:
        text = text[:text.index(start) - 1] + text[text.index(end) + len(end):]
    text = text.replace('</includes>', VARIABLES + '</includes>')
    open(path, 'w', encoding='utf-8').write(text)


if __name__ == '__main__':
    with open(os.path.join(ROOT, 'xml', 'DialogPlayerProcessInfo.xml'), 'w', encoding='utf-8') as handle:
        handle.write(player_details())
    with open(os.path.join(ROOT, 'xml', 'VideoOSDBookmarks.xml'), 'w', encoding='utf-8') as handle:
        handle.write(chapters())
    add_variables()
    add_timer()
    print('Wrote xml/DialogPlayerProcessInfo.xml, xml/VideoOSDBookmarks.xml, their variables and timer')
