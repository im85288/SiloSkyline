#!/usr/bin/env python3
"""Generate Skyline's person page (xml/Custom_1195_SiloPerson.xml), as Silo's
Apple TV app draws it: the portrait, name, facts and biography, then the
person's titles in the library as a six-wide grid with All / Movies / Series.

    python3 tools/build_person.py

SiloKodiConnect opens it (mode=person) from a cast member on an info page,
with the person's facts in Home window properties silo.person.*; the grid
lists their titles itself (mode=widget&person=...).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_home import BACKGROUND, ROOT, TEXT  # noqa: E402
from build_library import card, COLS, ITEM_H, ITEM_W  # noqa: E402

WINDOW_ID = 1195
PILLS_ID, GRID_ID = 5300, 5301
PERSON = 'Window(Home).Property(silo.person.%s)'
KIND = PERSON % 'type'
X, TEXT_X = 160, 508            # the portrait, and the text beside it
FILMOGRAPHY_TOP = 600
GRID_TOP = FILMOGRAPHY_TOP + 160
# Into the grid, the page slides up to leave Filmography and its pills at the top.
LIFT = FILMOGRAPHY_TOP - 50
BIO = 'A6EDEDED'                # the biography: grey, as Silo's
FILTERS = (('', 'All'), ('movie', 'Movies'), ('series', 'Series'))


def chip(fact):
    """A fact under the name (born, age, birthplace): a grey pill."""
    return '''
                <control type="button">
                    <width>auto</width><height>40</height>
                    <label>$INFO[%(fact)s]</label>
                    <font>silo_detail</font>
                    <textoffsetx>18</textoffsetx>
                    <aligny>center</aligny>
                    <enable>false</enable>
                    <disabledcolor>%(text)s</disabledcolor>
                    <texturenofocus border="20" colordiffuse="1FFFFFFF">silo/pill.png</texturenofocus>
                    <texturefocus border="20" colordiffuse="1FFFFFFF">silo/pill.png</texturefocus>
                    <visible>!String.IsEmpty(%(fact)s)</visible>
                </control>''' % {'fact': PERSON % fact, 'text': TEXT}


# Each pill's width: its name in silo_detail and the pill's ends.
PILL_WIDTHS = (84, 128, 120)


def filter_pill(index, kind, label):
    """All, Movies or Series: the chosen one outlined, the focused one white
    with dark text, the rest faint chips. Pressing one filters the grid
    (Silo's app waits for the press too). A group, as Kodi takes no variable
    for a button's texture; the pills name their neighbours, as a grouplist
    moves only between its own children's ids."""
    button = PILLS_ID + 10 + index
    chosen = 'String.IsEqual(%s,%s)' % (KIND, kind) if kind else 'String.IsEmpty(%s)' % KIND
    neighbours = ''.join('\n                        <%s>%d</%s>' % (move, button + step, move)
                         for move, step in (('onleft', -1), ('onright', 1)) if 0 <= index + step < len(FILTERS))
    return '''
                <control type="group" id="%(group)d">
                    <width>%(w)d</width><height>52</height>
                    <control type="image">
                        <width>%(w)d</width><height>52</height>
                        <texture border="26" colordiffuse="2EFFFFFF">silo/pill.png</texture>
                        <visible>!%(chosen)s</visible>
                    </control>
                    <control type="image">
                        <width>%(w)d</width><height>52</height>
                        <texture border="28" colordiffuse="D9FFFFFF">silo/season_ring.png</texture>
                        <visible>%(chosen)s</visible>
                    </control>
                    <control type="button" id="%(id)d">
                        <width>%(w)d</width><height>52</height>
                        <label>$VAR[SiloPersonFilter%(index)d]</label>
                        <font>silo_detail</font>
                        <align>center</align><aligny>center</aligny>
                        <textcolor>99EDEDED</textcolor>
                        <focusedcolor>FF000000</focusedcolor>
                        <texturefocus border="26" colordiffuse="%(text)s">silo/pill.png</texturefocus>
                        <texturenofocus />
                        <onclick>SetProperty(silo.person.type,%(kind)s,home)</onclick>%(neighbours)s
                        <ondown>%(grid)d</ondown>
                    </control>
                </control>''' % {'group': button + 10, 'id': button, 'w': PILL_WIDTHS[index], 'index': index, 'text': TEXT,
                                  'kind': kind, 'grid': GRID_ID, 'chosen': chosen, 'neighbours': neighbours}


def variables():
    """Each filter pill's label: white when chosen, dark while focused (the
    button's own colour), grey otherwise."""
    out = '    <!-- Silo Skyline person (tools/build_person.py) -->\n'
    for index, (kind, label) in enumerate(FILTERS):
        chosen = 'String.IsEqual(%s,%s)' % (KIND, kind) if kind else 'String.IsEmpty(%s)' % KIND
        focused = 'Control.HasFocus(%d)' % (PILLS_ID + 10 + index)
        out += ('    <variable name="SiloPersonFilter%(i)d">\n'
                '        <value condition="!%(focused)s + %(chosen)s">[COLOR %(text)s]%(label)s[/COLOR]</value>\n'
                '        <value>%(label)s</value>\n'
                '    </variable>\n') % {'i': index, 'focused': focused, 'chosen': chosen, 'text': TEXT, 'label': label}
    return out + '    <!-- end Silo Skyline person -->\n'


def build():
    return '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by tools/build_person.py: edit that, not this. -->
<window id="%(window)d" type="dialog">
    <defaultcontrol always="true">%(first_pill)d</defaultcontrol>
    <controls>
        <control type="image">
            <left>0</left><top>0</top><width>1920</width><height>1080</height>
            <texture colordiffuse="%(background)s">colors/white.png</texture>
        </control>
        <control type="group">
            <animation effect="fade" start="0" end="100" time="200">WindowOpen</animation>
            <animation effect="fade" start="100" end="0" time="150">WindowClose</animation>
            <animation effect="slide" end="0,-%(lift)d" time="300" tween="cubic" easing="out" condition="Control.HasFocus(%(grid)d)">Conditional</animation>
            <control type="image">
                <left>%(x)d</left><top>108</top><width>300</width><height>450</height>
                <!-- Gone as the page slides up (its foot would show above Filmography). -->
                <animation effect="fade" start="100" end="0" time="200" condition="Control.HasFocus(%(grid)d)">Conditional</animation>
                <aspectratio>scale</aspectratio>
                <texture background="true" diffuse="silo/card_poster_mask.png" fallback="silo/person_placeholder.png">$INFO[%(photo)s]</texture>
            </control>
            <control type="label">
                <left>%(tx)d</left><top>118</top><width>%(tw)d</width><height>96</height>
                <font>silo_title</font>
                <textcolor>%(text)s</textcolor>
                <label>$INFO[%(name)s]</label>
            </control>
            <control type="grouplist">
                <left>%(tx)d</left><top>226</top><width>%(tw)d</width><height>40</height>
                <orientation>horizontal</orientation>
                <itemgap>12</itemgap>%(chips)s
            </control>
            <!-- SiloKodiConnect trims a long biography to fit, ending it with "…" as
                 Silo's app does (Kodi's textbox would just cut it off). -->
            <control type="textbox">
                <left>%(tx)d</left><top>290</top><width>920</width><height>210</height>
                <font>silo_bio</font>
                <textcolor>%(bio)s</textcolor>
                <label>$INFO[%(bio_text)s]</label>
            </control>
            <!-- Filmography: its count is the filter's. -->
            <control type="grouplist">
                <left>%(x)d</left><top>%(ftop)d</top><width>1600</width><height>60</height>
                <orientation>horizontal</orientation>
                <itemgap>40</itemgap>
                <control type="label">
                    <width>auto</width><height>60</height>
                    <aligny>center</aligny>
                    <font>silo_row</font>
                    <textcolor>%(text)s</textcolor>
                    <label>Filmography</label>
                </control>
                <control type="label">
                    <width>auto</width><height>60</height>
                    <aligny>center</aligny>
                    <font>silo_detail</font>
                    <textcolor>99EDEDED</textcolor>
                    <label>$INFO[Container(%(grid)d).NumItems,, titles]</label>
                    <visible>!Container(%(grid)d).IsUpdating + Integer.IsGreater(Container(%(grid)d).NumItems,0)</visible>
                </control>
            </control>
            <control type="grouplist" id="%(pills)d">
                <left>%(x)d</left><top>%(ptop)d</top><width>1000</width><height>52</height>
                <orientation>horizontal</orientation>
                <itemgap>10</itemgap>%(filters)s
            </control>
            <control type="panel" id="%(grid)d">
                <left>%(gx)d</left><top>%(gtop)d</top><width>%(gw)d</width><height>%(gh)d</height>
                <orientation>vertical</orientation>
%(grid_up)s
                <scrolltime tween="cubic" easing="out">240</scrolltime>
                <itemlayout width="%(iw)d" height="%(ih)d">%(card)s
                </itemlayout>
                <focusedlayout width="%(iw)d" height="%(ih)d">%(card_focused)s
                </focusedlayout>
                <!-- A title's own page: this one and the info page close for it (an
                     info page can't open another over itself). -->
                <onclick>Dialog.Close(%(window)d)</onclick>
                <onclick>Dialog.Close(movieinformation)</onclick>
                <onclick>RunPlugin(plugin://plugin.video.silokodiconnect/?mode=info&amp;type=$INFO[ListItem.DBType]&amp;dbid=$INFO[ListItem.DBID])</onclick>
                <content target="videos">plugin://plugin.video.silokodiconnect/?mode=widget&amp;section=person&amp;person=$INFO[%(id)s]&amp;type=$INFO[%(kind)s]</content>
            </control>
        </control>
    </controls>
</window>
''' % {'window': WINDOW_ID, 'pills': PILLS_ID, 'first_pill': PILLS_ID + 10, 'grid': GRID_ID, 'background': BACKGROUND, 'lift': LIFT,
       'x': X, 'tx': TEXT_X, 'tw': 1920 - TEXT_X - X, 'text': TEXT, 'bio': BIO,
       'photo': PERSON % 'photo', 'name': PERSON % 'name', 'bio_text': PERSON % 'bio',
       'chips': ''.join(chip(fact) for fact in ('born', 'died', 'age', 'place')),
       'ftop': FILMOGRAPHY_TOP, 'ptop': FILMOGRAPHY_TOP + 78,
       'filters': ''.join(filter_pill(index, kind, label) for index, (kind, label) in enumerate(FILTERS)),
       'gx': X - 6, 'gtop': GRID_TOP, 'gw': COLS * ITEM_W, 'gh': 1080 - GRID_TOP + LIFT,
       'iw': ITEM_W, 'ih': ITEM_H, 'card': card(False, GRID_ID), 'card_focused': card(True, GRID_ID),
       'id': PERSON % 'id', 'kind': KIND,
       # Up from the grid: to the chosen filter.
       'grid_up': ''.join('\n                <onup condition="%s">%d</onup>' % (
           'String.IsEqual(%s,%s)' % (KIND, kind) if kind else 'String.IsEmpty(%s)' % KIND, PILLS_ID + 10 + index)
           for index, (kind, _) in enumerate(FILTERS))}


def add_variables():
    path = os.path.join(ROOT, 'xml', 'Variables.xml')
    text = open(path, encoding='utf-8').read()
    start, end = '    <!-- Silo Skyline person (tools/build_person.py) -->', '    <!-- end Silo Skyline person -->\n'
    if start in text:
        text = text[:text.index(start)] + text[text.index(end) + len(end):]
    text = text.replace('</includes>', variables() + '</includes>')
    open(path, 'w', encoding='utf-8').write(text)


if __name__ == '__main__':
    with open(os.path.join(ROOT, 'xml', 'Custom_%d_SiloPerson.xml' % WINDOW_ID), 'w', encoding='utf-8') as handle:
        handle.write(build())
    add_variables()
    print('Wrote xml/Custom_%d_SiloPerson.xml and its variables in xml/Variables.xml' % WINDOW_ID)
