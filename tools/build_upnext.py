#!/usr/bin/env python3
"""Write Up Next's windows (service.upnext) in Silo's player style.

Up Next looks for its windows in the skin first, by file name:
script-upnext-upnext.xml (and -simple), script-upnext-stillwatching.xml
(and -simple) and script-upnext-skip.xml. It fills Window.Property(...)
with the next episode (tvshowtitle, title, season, episode, plot, thumb,
fanart, landscape, rating, endtime), counts down in remaining, and sets
credits_countdown/credits_remaining while the end credits roll. Its
buttons are 3012 (Watch now / Continue watching), 3013 (Close or Stop,
labelled by the add-on), 3014 the countdown bar and 3010 the Skip button.

Silo's Next Up takes over the screen and shrinks the video into a frame
beside the details. Kodi can't draw the playing video inside a dialog, so
the frame shows the next episode's still; the rest is laid out as Silo TV's
grid (the show's art behind, the panel and its buttons top right).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_home import LANDSCAPE, ROOT, SAFE_X, TEXT, card_body  # noqa: E402

UPNEXT = 'service.upnext'


def button(control_id, label, width, onleft=None, onright=None):
    moves = ''
    if onleft:
        moves += '\n                    <onleft>%d</onleft>' % onleft
    if onright:
        moves += '\n                    <onright>%d</onright>' % onright
    # The row keeps focus only when asked (silo.deck): Kodi hands it focus as
    # the window opens, and OK would then play that title, not the next episode.
    moves += ('\n                    <ondown>SetProperty(silo.deck,1)</ondown>'
              '\n                    <ondown>SetFocus(%d)</ondown>' % ON_DECK)
    return '''
                <control type="button" id="%(id)d">
                    <width>%(w)d</width><height>80</height>
                    <label>%(label)s</label>
                    <font>silo_meta</font>
                    <textcolor>%(text)s</textcolor>
                    <focusedcolor>FF000000</focusedcolor>
                    <align>center</align><aligny>center</aligny>
                    <texturefocus border="46" colordiffuse="%(text)s">silo/dialog_button.png</texturefocus>
                    <texturenofocus border="46" colordiffuse="26FFFFFF">silo/dialog_button.png</texturenofocus>
                    <pulseonselect>false</pulseonselect>%(moves)s
                </control>''' % {'id': control_id, 'w': width, 'label': label, 'text': TEXT, 'moves': moves}


ON_DECK = 3100
# Silo's On Deck under the panel: SiloKodiConnect's Continue Watching, five
# cards across, played from here (resuming where it was left).
ON_DECK_CARD = dict(LANDSCAPE, width=288, height=162)
ON_DECK_PATH = ('plugin://plugin.video.silokodiconnect/?mode=widget&amp;section=continue_watching'
                '&amp;refresh=$INFO[Window(Home).Property(silokodi.library_updated)]'
                # Not the show Up Next is offering; last, as the title isn't URL-encoded.
                '&amp;exclude_show=$INFO[Window.Property(tvshowtitle)]')

# Silo TV's grid (1920 wide): 160 px margins, five cards of 288 with 40 px
# gaps. The video pane spans two cards; the panel takes the rest.
MARGIN, GAP = 160, 40
PANE_W = 2 * 288 + GAP
PANE_H = PANE_W * 9 // 16
PANE_TOP = 190
PANEL_X = MARGIN + PANE_W + GAP
PANEL_W = 1920 - MARGIN - PANEL_X


def label(top, height, font, color, text, visible='', extra=''):
    return '''
            <control type="label">
                <left>%(x)d</left><top>%(top)d</top>
                <width>%(w)d</width><height>%(h)d</height>
                <aligny>center</aligny>
                <font>%(font)s</font>
                <textcolor>%(color)s</textcolor>
                <label>%(text)s</label>%(visible)s%(extra)s
            </control>''' % {'x': PANEL_X, 'top': top, 'w': PANEL_W, 'h': height, 'font': font,
                             'color': color, 'text': text, 'extra': extra,
                             'visible': '\n                <visible>%s</visible>' % visible if visible else ''}


def popup(still_watching):
    top = PANE_TOP + 10
    if still_watching:
        eyebrows = label(top, 36, 'silo_meta', '85EDEDED', '$ADDON[%s 30024]' % UPNEXT)
        main = '$ADDON[%s 30010]' % UPNEXT  # Continue watching
        what = 'Up Next asks before it plays another episode.'
    else:
        credits = 'String.IsEqual(Window.Property(credits_countdown),true)'
        eyebrows = (
            label(top, 36, 'silo_meta', '85EDEDED', 'UP NEXT',
                  '!%s + Integer.IsGreater(Player.TimeRemaining,59)' % credits) +
            label(top, 36, 'silo_meta', '85EDEDED', 'UP NEXT IN $INFO[Window.Property(remaining)] S',
                  '!%s + !Integer.IsGreater(Player.TimeRemaining,59)' % credits) +
            # While the credits roll: the countdown and how to keep watching them.
            label(top, 36, 'silo_meta', '85EDEDED',
                  '$ADDON[%s 30050]  ·  $ADDON[%s 30051]' % (UPNEXT, UPNEXT), credits,
                  '\n                <description>credits countdown</description>').replace(
                      '<control type="label">', '<control type="label" id="3015">', 1))
        main = 'Play Now'
        what = 'Up Next offers the next episode as this one ends.'
    return '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by tools/build_upnext.py: %(what)s
     Silo TV's Next Up, full screen: the next episode's art behind, its still
     where Silo frames the playing video (Kodi can't frame it in a dialog),
     and the details and buttons beside it, top right. -->
<window>
    <defaultcontrol always="true">3012</defaultcontrol>
    <zorder>1</zorder>
    <controls>
        <control type="group">
            <animation effect="fade" start="0" end="100" time="300">WindowOpen</animation>
            <animation effect="fade" start="100" end="0" time="240">WindowClose</animation>
            <control type="image">
                <width>1920</width><height>1080</height>
                <texture colordiffuse="FF0D0F12">colors/white.png</texture>
            </control>
            <control type="image">
                <width>1920</width><height>1080</height>
                <aspectratio>scale</aspectratio>
                <texture background="true" colordiffuse="59FFFFFF">$VAR[SiloUpNextBackdrop]</texture>
            </control>
            <control type="image">
                <left>0</left><bottom>0</bottom>
                <width>1920</width><height>720</height>
                <texture>silo/scrim_bottom.png</texture>
            </control>
        </control>
        <control type="group">
            <animation effect="fade" start="0" end="100" time="300">WindowOpen</animation>
            <animation effect="slide" start="0,40" end="0,0" time="300" tween="cubic" easing="out">WindowOpen</animation>
            <animation effect="fade" start="100" end="0" time="240">WindowClose</animation>
            <!-- The pane: the next episode's still with a hairline edge, and the countdown. -->
            <control type="image">
                <left>%(x)d</left><top>%(pane_top)d</top>
                <width>%(pane_w)d</width><height>%(pane_h)d</height>
                <texture diffuse="silo/card_landscape_mask.png" colordiffuse="FF1A1D27">colors/white.png</texture>
            </control>
            <control type="image">
                <left>%(x)d</left><top>%(pane_top)d</top>
                <width>%(pane_w)d</width><height>%(pane_h)d</height>
                <aspectratio>scale</aspectratio>
                <texture background="true" diffuse="silo/card_landscape_mask.png">$VAR[SiloUpNextArt]</texture>
            </control>
            <control type="image">
                <left>%(x)d</left><top>%(pane_top)d</top>
                <width>%(pane_w)d</width><height>%(pane_h)d</height>
                <texture diffuse="silo/card_landscape_mask.png">silo/card_scrim.png</texture>
            </control>
            <control type="image">
                <left>%(x)d</left><top>%(pane_top)d</top>
                <width>%(pane_w)d</width><height>%(pane_h)d</height>
                <texture border="14" colordiffuse="29FFFFFF">silo/card_landscape_focus.png</texture>
            </control>
            <control type="progress" id="3014">
                <left>%(bar_x)d</left><top>%(bar_top)d</top>
                <width>%(bar_w)d</width><height>6</height>
                <texturebg colordiffuse="33FFFFFF">colors/white.png</texturebg>
                <lefttexture /><righttexture /><overlaytexture />
                <midtexture colordiffuse="%(text)s">colors/white.png</midtexture>
            </control>
            <!-- The panel. -->%(eyebrows)s%(show)s%(episode)s%(plot)s
            <control type="grouplist" id="3000">
                <left>%(panel_x)d</left><top>%(buttons_top)d</top>
                <width>%(panel_w)d</width><height>80</height>
                <orientation>horizontal</orientation>
                <itemgap>20</itemgap>%(main)s%(close)s
            </control>
            <!-- On Deck: the rest of Continue Watching. -->
            <control type="label">
                <left>%(x)d</left><top>%(deck_top)d</top>
                <width>1200</width><height>46</height>
                <font>silo_row</font>
                <textcolor>%(text)s</textcolor>
                <label>Continue Watching</label>
                <visible>Integer.IsGreater(Container(%(deck)d).NumItems,0) | Container(%(deck)d).IsUpdating</visible>
            </control>
            <control type="list" id="%(deck)d">
                <left>%(deck_x)d</left><top>%(deck_list_top)d</top>
                <width>%(deck_w)d</width><height>%(deck_h)d</height>
                <orientation>horizontal</orientation>
                <scrolltime tween="cubic" easing="out">280</scrolltime>
                <onup>ClearProperty(silo.deck)</onup>
                <onup>SetFocus(3012)</onup>
                <visible>Integer.IsGreater(Container(%(deck)d).NumItems,0) | Container(%(deck)d).IsUpdating</visible>
                <onfocus condition="!String.IsEqual(Window.Property(silo.deck),1)">SetFocus(3012)</onfocus>
                <onclick condition="Integer.IsGreater(ListItem.PercentPlayed,0)">PlayMedia($ESCINFO[ListItem.FileNameAndPath],resume)</onclick>
                <onclick condition="!Integer.IsGreater(ListItem.PercentPlayed,0)">PlayMedia($ESCINFO[ListItem.FileNameAndPath],noresume)</onclick>
                <content target="videos">%(deck_path)s</content>
                <itemlayout width="%(deck_item_w)d" height="%(deck_h)d">%(deck_card)s
                </itemlayout>
                <focusedlayout width="%(deck_item_w)d" height="%(deck_h)d">%(deck_card_focused)s
                </focusedlayout>
            </control>
        </control>
    </controls>
</window>
''' % {'what': what, 'x': MARGIN, 'pane_top': PANE_TOP, 'pane_w': PANE_W, 'pane_h': PANE_H,
       'bar_x': MARGIN + 18, 'bar_top': PANE_TOP + PANE_H - 6, 'bar_w': PANE_W - 36, 'text': TEXT,
       'panel_x': PANEL_X, 'panel_w': PANEL_W, 'buttons_top': PANE_TOP + PANE_H - 80, 'eyebrows': eyebrows,
       'deck': ON_DECK, 'deck_top': PANE_TOP + PANE_H + 56, 'deck_list_top': PANE_TOP + PANE_H + 112,
       # Cards start at the margin (their focus ring sits 6 px outside).
       'deck_x': MARGIN - 6, 'deck_w': 1920 - MARGIN + 6, 'deck_h': ON_DECK_CARD['height'] + 12 + 76,
       'deck_item_w': ON_DECK_CARD['width'] + GAP, 'deck_path': ON_DECK_PATH,
       'deck_card': card_body(ON_DECK_CARD, False), 'deck_card_focused': card_body(ON_DECK_CARD, True, ON_DECK),
       'show': label(top + 44, 60, 'silo_wordmark', TEXT, '$INFO[Window.Property(tvshowtitle)]'),
       'episode': label(top + 110, 40, 'silo_meta', '9EEDEDED',
                        '$INFO[Window.Property(season),S,]$INFO[Window.Property(episode),·E,  ]'
                        '[COLOR %s]$INFO[Window.Property(title)][/COLOR]'
                        '$INFO[Window.Property(endtime),  ·  Ends at ,]' % TEXT),
       'plot': '''
            <control type="textbox">
                <left>%d</left><top>%d</top>
                <width>%d</width><height>62</height>
                <font>silo_detail</font>
                <textcolor>94EDEDED</textcolor>
                <label>$INFO[Window.Property(plot)]</label>
                <autoscroll>false</autoscroll>
            </control>''' % (PANEL_X, top + 162, PANEL_W),
       'main': button(3012, main, 340, onright=3013),
       'close': button(3013, '$ADDON[%s 30034]' % UPNEXT, 220, onleft=3012)}

SKIP = '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by tools/build_upnext.py: Up Next's Skip intro / Skip recap
     button as Silo's skip pill, bottom right above where the player's
     controls sit: dark glass with a faint outline, white outline and text
     with focus. Control 3010 is the button. -->
<window>
    <defaultcontrol always="true">3010</defaultcontrol>
    <zorder>1</zorder>
    <controls>
        <control type="group">
            <right>64</right><bottom>112</bottom>
            <width>380</width><height>96</height>
            <animation effect="fade" start="0" end="100" time="240">WindowOpen</animation>
            <animation effect="slide" start="40,0" end="0,0" time="240" tween="cubic" easing="out">WindowOpen</animation>
            <animation effect="fade" start="100" end="0" time="200">WindowClose</animation>
            <!-- Up above the player's controls while they show, as Silo's does. -->
            <animation effect="slide" end="0,-240" time="220" tween="cubic" easing="out" condition="Window.IsVisible(videoosd) | Window.IsVisible(seekbar)">Conditional</animation>
            <control type="button" id="3010">
                <width>380</width><height>96</height>
                <label>$INFO[Window.Property(label)]</label>
                <font>silo_meta</font>
                <textcolor>8CFFFFFF</textcolor>
                <focusedcolor>FFFFFFFF</focusedcolor>
                <align>center</align><aligny>center</aligny>
                <texturefocus border="48" colordiffuse="A6000000">silo/dialog_button.png</texturefocus>
                <texturenofocus border="48" colordiffuse="A6000000">silo/dialog_button.png</texturenofocus>
                <pulseonselect>false</pulseonselect>
            </control>
            <control type="image">
                <width>380</width><height>96</height>
                <texture border="48" colordiffuse="FFFFFFFF">silo/pill_ring.png</texture>
                <visible>Control.HasFocus(3010)</visible>
            </control>
            <control type="image">
                <width>380</width><height>96</height>
                <texture border="48" colordiffuse="40FFFFFF">silo/pill_ring.png</texture>
                <visible>!Control.HasFocus(3010)</visible>
            </control>
        </control>
    </controls>
</window>
'''

VARIABLES = '''    <variable name="SiloUpNextBackdrop">
        <value condition="!String.IsEmpty(Window.Property(fanart))">$INFO[Window.Property(fanart)]</value>
        <value condition="!String.IsEmpty(Window.Property(landscape))">$INFO[Window.Property(landscape)]</value>
        <value>$INFO[Window.Property(thumb)]</value>
    </variable>
    <variable name="SiloUpNextArt">
        <value condition="!String.IsEmpty(Window.Property(thumb))">$INFO[Window.Property(thumb)]</value>
        <value condition="!String.IsEmpty(Window.Property(landscape))">$INFO[Window.Property(landscape)]</value>
        <value>$INFO[Window.Property(fanart)]</value>
    </variable>
'''
START, END = '    <!-- Silo Up Next variables (tools/build_upnext.py) -->\n', '    <!-- end Silo Up Next variables -->\n'


def add_variables():
    path = os.path.join(ROOT, 'xml', 'Variables.xml')
    text = open(path, encoding='utf-8').read()
    if START in text:
        text = text[:text.index(START)] + text[text.index(END) + len(END):]
    text = text.replace('</includes>', START + VARIABLES + END + '</includes>')
    with open(path, 'w', encoding='utf-8') as handle:
        handle.write(text)


if __name__ == '__main__':
    for name, still in (('upnext', False), ('stillwatching', True)):
        page = popup(still)
        for suffix in ('', '-simple'):
            with open(os.path.join(ROOT, 'xml', 'script-upnext-%s%s.xml' % (name, suffix)), 'w',
                      encoding='utf-8') as handle:
                handle.write(page)
    with open(os.path.join(ROOT, 'xml', 'script-upnext-skip.xml'), 'w', encoding='utf-8') as handle:
        handle.write(SKIP)
    add_variables()
    print('Wrote xml/script-upnext-*.xml and their variables in xml/Variables.xml')
