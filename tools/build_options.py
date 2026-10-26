"""Write xml/Custom_1180_SiloOptions.xml: Silo's player Options sheet.

    python3 tools/build_options.py

The player's Options button opens it over the video: a row of tab pills
(Info, Audio, Subtitles, Video, Chapters) above one rounded panel, as in
Silo's TV app. Each tab has its actions on the left (a column of rows, the
focused one a white pill, with the current value on the right) and what is
playing now on the right. The actions are Kodi's own: track and subtitle
switches, its audio, subtitle and video settings dialogs, the subtitle
search, and the chapter list.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_home import ROOT, TEXT, TEXT_DIM  # noqa: E402

WINDOW_ID = 1180
TAB = 'Window(Home).Property(silo.options.tab)'
PANEL_X, PANEL_W = 180, 1560
PANEL_TOP, PANEL_H = 150, 520
TABS_TOP = 48
ROW_H = 68
CARD = 'FF131417'  # Silo's dialog card

# (key, title, rows, facts): rows are (label, value, actions), facts (label, value).
TABS = [
    ('info', 'Info', [
        ('Chapters', '$INFO[Player.ChapterName]', ['SetProperty(silo.options.tab,chapters,home)', 'SetFocus(205)']),
        ('Player details', '', ['Dialog.Close(1180)', 'ActivateWindow(PlayerProcessInfo)']),
    ], [
        ('Title', '$INFO[VideoPlayer.Title]'),
        ('Episode', '$INFO[VideoPlayer.Season,S,]$INFO[VideoPlayer.Episode, · E,]'),
        ('Length', '$INFO[Player.Duration]'),
        ('Video', '$INFO[VideoPlayer.VideoResolution][UPPERCASE]$INFO[VideoPlayer.HdrType, · ,][/UPPERCASE][UPPERCASE]$INFO[VideoPlayer.VideoCodec, · ,][/UPPERCASE]'),
        ('Audio', '$INFO[VideoPlayer.AudioLanguage][UPPERCASE]$INFO[VideoPlayer.AudioCodec, · ,][/UPPERCASE]$INFO[VideoPlayer.AudioChannels, · , ch]'),
        ('Subtitles', '$VAR[SiloOptionsSubtitles]'),
    ]),
    ('audio', 'Audio', [
        ('Audio track', '$INFO[VideoPlayer.AudioLanguage][UPPERCASE]$INFO[VideoPlayer.AudioCodec, · ,][/UPPERCASE]', ['AudioNextLanguage']),
        ('Audio settings', '', ['Dialog.Close(1180)', 'ActivateWindow(osdaudiosettings)']),
    ], [
        ('Codec', '[UPPERCASE]$INFO[VideoPlayer.AudioCodec][/UPPERCASE]'),
        ('Channels', '$INFO[VideoPlayer.AudioChannels]'),
        ('Language', '$INFO[VideoPlayer.AudioLanguage]'),
    ]),
    ('subtitles', 'Subtitles', [
        ('Subtitles', '$VAR[SiloOptionsSubtitlesOnOff]', ['ShowSubtitles']),
        ('Next subtitle', '$INFO[VideoPlayer.SubtitlesLanguage]', ['NextSubtitle']),
        ('Subtitle settings', '', ['Dialog.Close(1180)', 'ActivateWindow(osdsubtitlesettings)']),
        ('Search online', '', ['Dialog.Close(1180)', 'ActivateWindow(SubtitleSearch)']),
    ], [
        ('Showing', '$VAR[SiloOptionsSubtitles]'),
    ]),
    ('video', 'Video', [
        ('Zoom', '$INFO[Player.Process(videoaspect)]', ['AspectRatio']),
        ('Video settings', '', ['Dialog.Close(1180)', 'ActivateWindow(osdvideosettings)']),
        ('Player details', '', ['Dialog.Close(1180)', 'ActivateWindow(PlayerProcessInfo)']),
    ], [
        ('Resolution', '$INFO[VideoPlayer.VideoResolution]'),
        ('HDR', '[UPPERCASE]$INFO[VideoPlayer.HdrType][/UPPERCASE]'),
        ('Codec', '[UPPERCASE]$INFO[VideoPlayer.VideoCodec][/UPPERCASE]'),
        ('Decoder', '$INFO[Player.Process(videodecoder)]'),
    ]),
    ('chapters', 'Chapters', [
        ('Previous chapter', '', ['PlayerControl(Previous)']),
        ('Next chapter', '', ['PlayerControl(Next)']),
        ('All chapters', '', ['Dialog.Close(1180)', 'ActivateWindow(VideoBookmarks)']),
    ], [
        ('Chapter', '$INFO[Player.Chapter]$INFO[Player.ChapterCount, of ,]'),
        ('Now', '$INFO[Player.ChapterName]'),
    ]),
]


def tab_visible(key):
    # The first tab shows until one is chosen.
    return ('[String.IsEqual(%s,%s) | String.IsEmpty(%s)]' % (TAB, key, TAB) if key == TABS[0][0]
            else 'String.IsEqual(%s,%s)' % (TAB, key))


def tab_button(index, key, title):
    control_id = 101 + index
    return '''
            <control type="button" id="%(id)d">
                <width>auto</width><height>56</height>
                <label>%(title)s</label>
                <font>silo_tab</font>
                <textoffsetx>28</textoffsetx>
                <align>center</align><aligny>center</aligny>
                <textcolor>%(selected_or_dim)s</textcolor>
                <focusedcolor>FF000000</focusedcolor>
                <texturefocus border="28" colordiffuse="%(text)s">silo/pill.png</texturefocus>
                <texturenofocus border="28" colordiffuse="%(nofocus)s">silo/pill.png</texturenofocus>
                <onfocus>SetProperty(silo.options.tab,%(key)s,home)</onfocus>
                <ondown>%(panel)d</ondown>
            </control>''' % {'id': control_id, 'title': title, 'key': key, 'text': TEXT, 'panel': 201 + index,
                             'nofocus': '$VAR[SiloOptionsTab%s]' % key.title(),
                             'selected_or_dim': TEXT_DIM}


def row(control_id, label, value, actions):
    clicks = ''.join('\n                    <onclick>%s</onclick>' % action for action in actions)
    return '''
                <control type="button" id="%(id)d">
                    <width>%(w)d</width><height>%(h)d</height>
                    <label>%(label)s</label>
                    <label2>%(value)s</label2>
                    <font>silo_meta</font>
                    <textoffsetx>32</textoffsetx>
                    <aligny>center</aligny>
                    <textcolor>%(text)s</textcolor>
                    <focusedcolor>FF000000</focusedcolor>
                    <texturefocus border="46">silo/dialog_row_focus.png</texturefocus>
                    <texturenofocus />%(clicks)s
                </control>''' % {'id': control_id, 'w': PANEL_W // 2 - 60, 'h': ROW_H, 'label': label,
                                 'value': value, 'text': TEXT, 'clicks': clicks}


def fact(label, value, top):
    return '''
            <control type="label">
                <left>%(x)d</left><top>%(top)d</top><width>220</width><height>%(h)d</height>
                <aligny>center</aligny>
                <font>silo_meta</font>
                <textcolor>%(dim)s</textcolor>
                <label>%(label)s</label>
            </control>
            <control type="label">
                <left>%(vx)d</left><top>%(top)d</top><width>%(vw)d</width><height>%(h)d</height>
                <align>right</align><aligny>center</aligny>
                <font>silo_meta</font>
                <textcolor>%(text)s</textcolor>
                <label>%(value)s</label>
            </control>''' % {'x': PANEL_W // 2 + 20, 'vx': PANEL_W // 2 + 240, 'vw': PANEL_W // 2 - 300,
                             'top': top, 'h': ROW_H, 'label': label, 'value': value, 'dim': TEXT_DIM, 'text': TEXT}


def panel(index, key, rows, facts):
    first = 201 + index
    buttons = ''.join(row(first * 10 + n, *r) for n, r in enumerate(rows))
    heading = '''
            <control type="label">
                <left>%(x)d</left><top>%(top)d</top><width>600</width><height>40</height>
                <font>silo_badge</font>
                <textcolor>%(dim)s</textcolor>
                <label>[UPPERCASE]%(label)s[/UPPERCASE]</label>
            </control>'''
    return '''
        <control type="group">
            <left>%(px)d</left><top>%(pt)d</top>
            <visible>%(visible)s</visible>%(h1)s%(h2)s
            <control type="grouplist" id="%(id)d">
                <left>28</left><top>80</top>
                <width>%(w)d</width><height>%(gh)d</height>
                <orientation>vertical</orientation>
                <itemgap>0</itemgap>
                <onup>%(tab)d</onup>
                <onleft>noop</onleft><onright>noop</onright>%(buttons)s
            </control>%(facts)s
        </control>''' % {
        'px': PANEL_X, 'pt': PANEL_TOP, 'visible': tab_visible(key), 'id': first, 'w': PANEL_W // 2 - 60,
        'gh': PANEL_H - 110, 'tab': 101 + index, 'buttons': buttons,
        'h1': heading % {'x': 60, 'top': 32, 'dim': TEXT_DIM, 'label': 'Options'},
        'h2': heading % {'x': PANEL_W // 2 + 20, 'top': 32, 'dim': TEXT_DIM, 'label': 'Now playing'},
        'facts': ''.join(fact(label, value, 80 + n * ROW_H) for n, (label, value) in enumerate(facts))}


def build():
    tabs = ''.join(tab_button(i, key, title) for i, (key, title, _, _) in enumerate(TABS))
    panels = ''.join(panel(i, key, rows, facts) for i, (key, _, rows, facts) in enumerate(TABS))
    return '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by tools/build_options.py: edit that, not this. -->
<window type="dialog" id="%(window)d">
    <defaultcontrol always="true">101</defaultcontrol>
    <onload>ClearProperty(silo.options.tab,home)</onload>
    <include>Animation_DialogPopupOpenClose</include>
    <controls>
        <!-- Anywhere outside the sheet closes it. -->
        <control type="button">
            <left>0</left><top>0</top><width>1920</width><height>1080</height>
            <texturefocus /><texturenofocus />
            <onclick>Action(close)</onclick>
        </control>
        <control type="image">
            <left>0</left><top>0</top><width>1920</width><height>1080</height>
            <texture colordiffuse="66000000">colors/white.png</texture>
        </control>
        <!-- The tab pills, centred, on a darker pill track. -->
        <control type="image">
            <left>%(track_x)d</left><top>%(tabs_top)d</top><width>%(track_w)d</width><height>72</height>
            <texture border="36" colordiffuse="%(card)s">silo/pill.png</texture>
        </control>
        <control type="grouplist" id="100">
            <left>%(track_x)d</left><top>%(tabs_inner)d</top><width>%(track_w)d</width><height>56</height>
            <orientation>horizontal</orientation>
            <align>center</align>
            <itemgap>6</itemgap>%(tabs)s
        </control>
        <control type="image">
            <left>%(px)d</left><top>%(pt)d</top><width>%(pw)d</width><height>%(ph)d</height>
            <texture border="14" colordiffuse="%(card)s">silo/card_landscape_mask.png</texture>
        </control>%(panels)s
    </controls>
</window>
''' % {'window': WINDOW_ID, 'tabs': tabs, 'panels': panels, 'card': CARD, 'px': PANEL_X, 'pt': PANEL_TOP,
       'pw': PANEL_W, 'ph': PANEL_H, 'tabs_top': TABS_TOP, 'tabs_inner': TABS_TOP + 8,
       'track_x': (1920 - 900) // 2, 'track_w': 900}


VARIABLES = '''
    <!-- Silo Skyline options (tools/build_options.py) -->
    <variable name="SiloOptionsSubtitles">
        <value condition="!VideoPlayer.SubtitlesEnabled">Off</value>
        <value>$INFO[VideoPlayer.SubtitlesLanguage]</value>
    </variable>
    <variable name="SiloOptionsSubtitlesOnOff">
        <value condition="VideoPlayer.SubtitlesEnabled">On</value>
        <value>Off</value>
    </variable>
%(tab_vars)s    <!-- end Silo Skyline options -->
''' % {'tab_vars': ''.join('''    <variable name="SiloOptionsTab%(name)s">
        <value condition="%(visible)s">33FFFFFF</value>
        <value>00FFFFFF</value>
    </variable>
''' % {'name': key.title(), 'visible': tab_visible(key)} for key, _, _, _ in TABS)}


def add_variables():
    path = os.path.join(ROOT, 'xml', 'Variables.xml')
    text = open(path, encoding='utf-8').read()
    start, end = '    <!-- Silo Skyline options (tools/build_options.py) -->', '    <!-- end Silo Skyline options -->\n'
    if start in text:
        text = text[:text.index(start) - 1] + text[text.index(end) + len(end):]
    text = text.replace('</includes>', VARIABLES + '</includes>')
    open(path, 'w', encoding='utf-8').write(text)


if __name__ == '__main__':
    with open(os.path.join(ROOT, 'xml', 'Custom_%d_SiloOptions.xml' % WINDOW_ID), 'w', encoding='utf-8') as handle:
        handle.write(build())
    add_variables()
    print('Wrote xml/Custom_%d_SiloOptions.xml and its variables in xml/Variables.xml' % WINDOW_ID)
