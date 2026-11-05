#!/usr/bin/env python3
"""Write xml/AddonBrowser.xml: Kodi's add-on browser in Silo's style.

    python3 tools/build_addons.py

Settings' Add-ons and every list under it (My add-ons, its categories,
updates, a repository's add-ons, search results) open this window. It was
Estuary's: a big icon over the page title, the add-on's fanart bright behind
the list, the list half way down the page and running off its right edge.

Now, as Skyline's Search and Subscriptions: a list of the add-ons at the left,
each a rounded card with its icon on a dark tile (an add-on's own colours, and
Kodi's white folder glyphs, both show on it, focused or not), its name and
summary, and a word when something needs attention (Update, Disabled...). At
the right, the focused add-on's details: its icon, name, version and author,
where it came from, its state, and its description. Left opens Kodi's own
add-on buttons (hide foreign, hide incompatible, check for updates, settings)
in a side panel, as the video pages' View and sort.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_home import BACKGROUND, ROOT, SAFE_X, TEXT, TEXT_DIM  # noqa: E402

LIST_ID = 50
MENU_ID, MENU_W = 9000, 560
TOP = 200  # under the frame's title, as the video pages' views
LIST_W = 940
ROW_H, CARD_H = 104, 92
TILE = 64  # an add-on's icon tile
PANEL_X = SAFE_X + LIST_W + 72
PANEL_W = 1920 - SAFE_X - PANEL_X
PANEL_ICON = 176
FOCUSED_TEXT = 'FF000000'

# Kodi's add-on states (ListItem properties set by the add-on browser).
BROKEN = 'String.IsEqual(ListItem.AddonLifecycleType,$LOCALIZE[24171])'
DEPRECATED = 'String.IsEqual(ListItem.AddonLifecycleType,$LOCALIZE[24170])'
UPDATE = '[ListItem.Property(addon.hasupdate) | ListItem.Property(addon.isupdate)]'
DISABLED = 'ListItem.Property(addon.isinstalled) + !ListItem.Property(addon.isenabled)'
IS_ADDON = '!String.IsEmpty(ListItem.AddonVersion)'


def row(focused):
    """One add-on (or category): a rounded card, its icon on a dark tile, the
    name and summary, and a word at the right when it needs attention."""
    card = TEXT if focused else 'F21C1F24'
    # The focused row's text is dark on its white card, light when the list
    # hasn't focus (the side panel open) and the card is dark again.
    text = '$VAR[SiloAddonRowText]' if focused else TEXT
    dim = '$VAR[SiloAddonRowDim]' if focused else TEXT_DIM
    focus = 'Control.HasFocus(%d)' % LIST_ID
    # The list's focused layout also draws while the list hasn't focus (the
    # side panel open): it looks like any other row then.
    card_visible = '\n                        <visible>%s</visible>' % focus if focused else ''
    rest = '''
                    <control type="image">
                        <width>%(w)d</width><height>%(ch)d</height>
                        <texture border="24" colordiffuse="F21C1F24">silo/card_landscape_mask.png</texture>
                        <visible>!%(focus)s</visible>
                    </control>''' % {'w': LIST_W, 'ch': CARD_H, 'focus': focus} if focused else ''
    lx, lw = 14 + TILE + 22, LIST_W - (14 + TILE + 22) - 190
    return '''%(rest)s
                    <control type="image">
                        <width>%(w)d</width><height>%(ch)d</height>
                        <texture border="24" colordiffuse="%(card)s">silo/card_landscape_mask.png</texture>%(card_visible)s
                    </control>
                    <!-- The icon on a dark tile: never tinted, so an add-on's own
                         colours and Kodi's white glyphs both show, focused or not. -->
                    <control type="image">
                        <left>14</left><top>%(ty)d</top><width>%(tile)d</width><height>%(tile)d</height>
                        <texture border="16" colordiffuse="FF2A2E36">silo/card_landscape_mask.png</texture>
                    </control>
                    <control type="image">
                        <left>14</left><top>%(ty)d</top><width>%(tile)d</width><height>%(tile)d</height>
                        <aspectratio>keep</aspectratio>
                        <texture background="true" diffuse="silo/card_poster_mask.png">$VAR[SiloAddonIcon]</texture>
                    </control>
                    <control type="label">
                        <left>%(lx)d</left><top>12</top><width>%(lw)d</width><height>40</height>
                        <aligny>center</aligny>
                        <font>silo_meta</font>
                        <textcolor>%(text)s</textcolor>
                        <label>$INFO[ListItem.Label]</label>
                        <visible>!String.IsEmpty(ListItem.AddonSummary)</visible>
                    </control>
                    <control type="label">
                        <left>%(lx)d</left><top>50</top><width>%(lw)d</width><height>32</height>
                        <aligny>center</aligny>
                        <font>silo_detail</font>
                        <textcolor>%(dim)s</textcolor>
                        <label>$INFO[ListItem.AddonSummary]</label>
                        <visible>!String.IsEmpty(ListItem.AddonSummary)</visible>
                    </control>
                    <control type="label">
                        <left>%(lx)d</left><top>0</top><width>%(lw)d</width><height>%(ch)d</height>
                        <aligny>center</aligny>
                        <font>silo_meta</font>
                        <textcolor>%(text)s</textcolor>
                        <label>$INFO[ListItem.Label]</label>
                        <visible>String.IsEmpty(ListItem.AddonSummary)</visible>
                    </control>
                    <control type="label">
                        <left>%(fx)d</left><top>0</top><width>160</width><height>%(ch)d</height>
                        <align>right</align><aligny>center</aligny>
                        <font>silo_badge</font>
                        <textcolor>%(dim)s</textcolor>
                        <label>$VAR[SiloAddonFlag]</label>
                    </control>''' % {
        'rest': rest, 'w': LIST_W, 'ch': CARD_H, 'card': card, 'card_visible': card_visible, 'ty': (CARD_H - TILE) // 2,
        'tile': TILE, 'lx': lx, 'lw': lw, 'text': text, 'dim': dim, 'fx': LIST_W - 160 - 24}


def details():
    """The focused add-on at the right: icon, name, version and author, where
    it came from and its state, then its description."""
    return '''
        <!-- The focused add-on's details. -->
        <control type="group">
            <left>%(x)d</left><top>%(top)d</top>
            <control type="image">
                <width>%(s)d</width><height>%(s)d</height>
                <texture border="24" colordiffuse="FF1C1F24">silo/card_landscape_mask.png</texture>
            </control>
            <control type="image">
                <width>%(s)d</width><height>%(s)d</height>
                <aspectratio>keep</aspectratio>
                <fadetime>160</fadetime>
                <texture background="true" diffuse="silo/card_poster_mask.png">$VAR[SiloAddonIcon]</texture>
            </control>
            <control type="label">
                <left>0</left><top>%(nt)d</top><width>%(w)d</width><height>56</height>
                <aligny>center</aligny>
                <font>silo_row</font>
                <textcolor>%(text)s</textcolor>
                <label>$INFO[ListItem.Label]</label>
            </control>
            <control type="label">
                <left>0</left><top>%(vt)d</top><width>%(w)d</width><height>36</height>
                <aligny>center</aligny>
                <font>silo_detail</font>
                <textcolor>%(dim)s</textcolor>
                <label>$INFO[ListItem.AddonVersion,Version ,]$INFO[ListItem.AddonCreator,  ·  ,]</label>
            </control>
            <control type="label">
                <left>0</left><top>%(st)d</top><width>%(w)d</width><height>36</height>
                <aligny>center</aligny>
                <font>silo_detail</font>
                <textcolor>%(dim)s</textcolor>
                <label>$VAR[SiloAddonState]$INFO[ListItem.AddonOrigin,  ·  ,]</label>
                <visible>%(is_addon)s</visible>
            </control>
            <control type="textbox">
                <left>0</left><top>%(dt)d</top><width>%(w)d</width><height>%(dh)d</height>
                <font>silo_plot</font>
                <textcolor>%(dim)s</textcolor>
                <autoscroll delay="6000" time="3000" repeat="8000">true</autoscroll>
                <label>$VAR[SiloAddonDescription]</label>
            </control>
        </control>''' % {
        'x': PANEL_X, 'top': TOP + 8, 's': PANEL_ICON, 'w': PANEL_W, 'text': TEXT, 'dim': TEXT_DIM,
        'nt': PANEL_ICON + 28, 'vt': PANEL_ICON + 88, 'st': PANEL_ICON + 126, 'dt': PANEL_ICON + 186,
        'dh': 1080 - (TOP + 8) - (PANEL_ICON + 186) - 60, 'is_addon': IS_ADDON}


def side_menu():
    """Kodi's add-on browser buttons in Silo's side panel (as the video pages'
    View and sort): hide foreign, hide incompatible, check for updates, and
    Kodi's add-on settings. Kodi hides the first two where they don't apply."""
    def button(kind, control_id, label, extra=''):
        return '''
                <control type="%s" id="%d">
                    <width>%d</width>
                    <label>%s</label>%s
                    <include>DefaultSettingButton</include>
                </control>''' % (kind, control_id, MENU_W - SAFE_X - 40, label, extra)
    buttons = (button('radiobutton', 7, '$LOCALIZE[25001]', '\n                    <visible>Control.IsEnabled(7)</visible>')
               + button('radiobutton', 8, '$LOCALIZE[24999]', '\n                    <visible>Control.IsEnabled(8)</visible>')
               + button('button', 9, '$LOCALIZE[24034]') + button('button', 5, '$LOCALIZE[10004]'))
    return '''
        <!-- Kodi's add-on buttons, from the left (Left from the list). -->
        <control type="group">
            <left>-%(w)d</left>
            <animation effect="slide" start="0,0" end="%(w)d,0" time="220" tween="cubic" easing="out" condition="ControlGroup(%(menu)d).HasFocus">Conditional</animation>
            <control type="image">
                <left>0</left><top>0</top><width>%(w)d</width><height>1080</height>
                <texture colordiffuse="F21C1F24">colors/white.png</texture>
            </control>
            <control type="label">
                <left>%(x)d</left><top>%(ty)d</top><width>%(bw)d</width><height>40</height>
                <aligny>center</aligny>
                <font>silo_badge</font>
                <textcolor>99EDEDED</textcolor>
                <label>ADD-ONS</label>
            </control>
            <control type="grouplist" id="%(menu)d">
                <left>%(bx)d</left><top>%(top)d</top><width>%(bw)d</width><height>400</height>
                <orientation>vertical</orientation>
                <itemgap>8</itemgap>
                <onleft>noop</onleft><onup>noop</onup><ondown>noop</ondown>
                <onright>%(list)d</onright><onback>%(list)d</onback>%(buttons)s
            </control>
            <!-- When the repositories were last checked for updates. -->
            <control type="label">
                <left>%(x)d</left><top>%(ut)d</top><width>%(bw)d</width><height>36</height>
                <font>silo_detail</font>
                <textcolor>%(dim)s</textcolor>
                <label>$INFO[Window(AddonBrowser).Property(Updated),$LOCALIZE[31069]: ,]</label>
            </control>
        </control>''' % {'w': MENU_W, 'menu': MENU_ID, 'x': SAFE_X, 'bx': SAFE_X - 24, 'bw': MENU_W - SAFE_X - 40,
                         'ty': TOP - 56, 'top': TOP, 'list': LIST_ID, 'buttons': buttons, 'ut': 1080 - 96, 'dim': TEXT_DIM}


def build():
    return '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by tools/build_addons.py: edit that, not this. -->
<window>
    <defaultcontrol always="true">%(list)d</defaultcontrol>
    <backgroundcolor>%(background)s</backgroundcolor>
    <views>%(list)d</views>
    <controls>
        <control type="image">
            <left>0</left><top>0</top><width>1920</width><height>1080</height>
            <texture colordiffuse="%(background)s">colors/white.png</texture>
        </control>
        <!-- The shared frame (tools/build_frame.py): where you are and the clock. -->
        <include content="SiloFrame">
            <param name="title">$LOCALIZE[24001]$INFO[Container.FolderName,  ·  ,]</param>
            <param name="sub">$INFO[Container.CurrentItem,, / ]$INFO[Container.NumItems]</param>
        </include>
        <control type="list" id="%(list)d">
            <left>%(x)d</left><top>%(top)d</top><width>%(w)d</width><height>%(h)d</height>
            <orientation>vertical</orientation>
            <scrolltime tween="cubic" easing="out">240</scrolltime>
            <onleft>%(menu)d</onleft><onright>noop</onright>
            <itemlayout width="%(w)d" height="%(rh)d">%(row)s
            </itemlayout>
            <focusedlayout width="%(w)d" height="%(rh)d">%(row_focused)s
            </focusedlayout>
        </control>
        <control type="label">
            <left>%(x)d</left><top>%(top)d</top><width>%(w)d</width><height>60</height>
            <font>silo_meta</font>
            <textcolor>%(dim)s</textcolor>
            <label>Nothing here</label>
            <visible>Integer.IsEqual(Container.NumItems,0) + !Container.IsUpdating</visible>
        </control>%(details)s%(menu_xml)s
    </controls>
</window>
''' % {'list': LIST_ID, 'background': BACKGROUND, 'x': SAFE_X, 'top': TOP, 'w': LIST_W, 'h': 1080 - TOP,
       'rh': ROW_H, 'menu': MENU_ID, 'row': row(False), 'row_focused': row(True), 'dim': TEXT_DIM,
       'details': details(), 'menu_xml': side_menu()}


VARIABLES = '''
    <!-- Silo Skyline add-ons (tools/build_addons.py) -->
    <!-- An add-on's own icon is its thumb (its icon is Kodi's generic box);
         a category's is its icon (Kodi's glyph for it; its thumb is empty). -->
    <variable name="SiloAddonIcon">
        <value condition="!String.IsEmpty(ListItem.Art(thumb))">$INFO[ListItem.Art(thumb)]</value>
        <value condition="!String.IsEmpty(ListItem.Icon)">$INFO[ListItem.Icon]</value>
        <value>DefaultAddon.png</value>
    </variable>
    <variable name="SiloAddonRowText">
        <value condition="Control.HasFocus(%(list)d)">%(dark)s</value>
        <value>%(text)s</value>
    </variable>
    <variable name="SiloAddonRowDim">
        <value condition="Control.HasFocus(%(list)d)">99000000</value>
        <value>%(dim)s</value>
    </variable>
    <!-- A word at a row's right when the add-on needs attention. -->
    <variable name="SiloAddonFlag">
        <value condition="ListItem.Property(addon.downloading)">INSTALLING</value>
        <value condition="%(broken)s">BROKEN</value>
        <value condition="%(update)s">UPDATE</value>
        <value condition="%(disabled)s">DISABLED</value>
        <value condition="%(deprecated)s">DEPRECATED</value>
        <value condition="ListItem.Property(addon.orphaned)">UNUSED</value>
    </variable>
    <variable name="SiloAddonState">
        <value condition="ListItem.Property(addon.downloading)">Installing</value>
        <value condition="%(broken)s">Broken</value>
        <value condition="%(update)s">Update available</value>
        <value condition="%(disabled)s">Disabled</value>
        <value condition="%(deprecated)s">Deprecated</value>
        <value condition="ListItem.Property(addon.orphaned)">No longer needed by any add-on</value>
        <value condition="ListItem.Property(addon.isenabled)">Enabled</value>
        <value condition="ListItem.Property(addon.isinstalled)">Installed</value>
        <value>Not installed</value>
    </variable>
    <!-- Why it's broken or deprecated first, then what it does. -->
    <variable name="SiloAddonDescription">
        <value condition="[%(broken)s | %(deprecated)s] + !String.IsEmpty(ListItem.AddonLifecycleDesc)">$INFO[ListItem.AddonLifecycleDesc][CR][CR]$INFO[ListItem.AddonDescription]</value>
        <value condition="!String.IsEmpty(ListItem.AddonDescription)">$INFO[ListItem.AddonDescription]</value>
        <value>$INFO[ListItem.Plot]</value>
    </variable>
    <!-- end Silo Skyline add-ons -->
''' % {'broken': BROKEN, 'update': UPDATE, 'disabled': DISABLED, 'deprecated': DEPRECATED, 'list': LIST_ID,
       'dark': FOCUSED_TEXT, 'text': TEXT, 'dim': TEXT_DIM}


def add_variables():
    path = os.path.join(ROOT, 'xml', 'Variables.xml')
    text = open(path, encoding='utf-8').read()
    start, end = '    <!-- Silo Skyline add-ons (tools/build_addons.py) -->', '    <!-- end Silo Skyline add-ons -->\n'
    if start in text:
        text = text[:text.index(start) - 1] + text[text.index(end) + len(end):]
    text = text.replace('</includes>', VARIABLES + '</includes>')
    open(path, 'w', encoding='utf-8').write(text)


if __name__ == '__main__':
    with open(os.path.join(ROOT, 'xml', 'AddonBrowser.xml'), 'w', encoding='utf-8') as handle:
        handle.write(build())
    add_variables()
    print('Wrote xml/AddonBrowser.xml and its variables in xml/Variables.xml')
