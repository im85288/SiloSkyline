#!/usr/bin/env python3
"""Skyline's Showcase player style, the default, with Silo's as the other
choice (skin settings, Player, Player style):

    python3 tools/build_showcase.py

Silo's player chrome (DialogSeekBar.xml, hand-written) shows an eyebrow and
the title over the bar. Showcase puts the title's logo there with the episode
line and the hero's badges (age, resolution, HDR, audio: what's playing, as
Netflix's and Apple's players lead with; the ratings wait for the pause
screen), marks the bar's chapters with the current one's name under it and adds
a clock; after ten seconds paused with no key pressed, the OSD closes and a
pause screen ("You're watching") shows
the logo, episode, facts, plot and still over the dimmed picture, as
Netflix's and Apple's TV app do. It is in DialogSeekBar.xml too, which Kodi
opens while paused: in VideoFullScreen.xml its pictures loaded as a 4K film
started, and the SHIELD (2 GB) killed Kodi for memory.

Only the art Silo gives is used: clearlogo, fanart and an episode's still; the title's text stands in for a missing logo.

Each part goes between its own markers, so running this again replaces it.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_home import RATING_SHOWN, ROOT, TEXT, TEXT_DIM  # noqa: E402

# Showcase is the default: the setting (off until chosen) picks Silo's player.
SETTING = 'SkylineSiloOSD'
ON = '!Skin.HasSetting(%s)' % SETTING
# The pause screen, as Netflix's: Showcase, a video paused with no key pressed
# for ten seconds (the OSD closes then, silo_pause_screen); any key hides it.
PAUSE_IDLE = 10
PAUSE_SCREEN = ('%s + $EXP[SiloVideoPlayer] + Player.Paused + !Window.IsActive(videoosd) + System.IdleTime(%d)'
                % (ON, PAUSE_IDLE))
# Back on the pause screen only dismisses it, as Netflix's: KodiConnectForSilo's
# player keymap sends Back in the video window to this dialog, which lets Kodi
# have it (leave the video) unless the pause screen was showing.
PAUSE_BACK = 1188
VIDEO_PLAYER = 'Window.IsActive(fullscreenvideo) + !VideoPlayer.Content(LiveTV) + !Player.HasGame'  # SiloVideoPlayer
DIM = '87EDEDED'     # the hero's info line
# KodiConnectForSilo's details of what's playing, as its hero and info page show
# them: an episode's series' ratings and age rating, Silo's badges (Atmos too)
# and air date. Kodi's player has no rating source, Atmos or Silo's dates.
PLAYING = 'Window(Home).Property(silokodi.playing.%s)'
BADGE = 'B3FFFFFF'   # the hero's badge outline


def block(name):
    return ('<!-- Silo Skyline %s (tools/build_showcase.py) -->' % name,
            '<!-- end Silo Skyline %s -->' % name)


def drop(text, name):
    """text without name's block, if it has one."""
    start, end = block(name)
    return text[:text.index(start)] + text[text.index(end) + len(end):] if start in text else text


def put(text, name, content, anchor, before=True):
    """text with name's block (content) in place of the old one, or next to anchor."""
    start, end = block(name)
    if start in text:
        text = text[:text.index(start)] + text[text.index(end) + len(end):]
    piece = start + content + end
    index = text.index(anchor)
    return text[:index] + piece + text[index:] if before else text[:index + len(anchor)] + piece + text[index + len(anchor):]


# Kodi's own names for what's playing, as KodiConnectForSilo's badges name them
# (mapping.quality_badges): resolution, then dynamic range, then audio.
RESOLUTIONS = (('4K', '4K'), ('2160', '4K'), ('1080', '1080P'), ('720', '720P'))
HDR = (('dolbyvision', 'DOLBY VISION'), ('hdr10plus', 'HDR10+'), ('hdr10', 'HDR10'), ('hlg', 'HLG'))
AUDIO = (('eac3_ddp_atmos', 'ATMOS'), ('truehd_atmos', 'ATMOS'), ('truehd', 'TRUEHD'), ('eac3', 'EAC3'),
         ('ac3', 'AC3'), ('dtshd_ma', 'DTS-HD MA'), ('dts', 'DTS'), ('dca', 'DTS'), ('aac', 'AAC'),
         ('flac', 'FLAC'), ('opus', 'OPUS'), ('mp3', 'MP3'))
CHANNELS = (('8', ' 7.1'), ('7', ' 6.1'), ('6', ' 5.1'), ('2', ' 2.0'), ('1', ' MONO'))


def variables():
    def variable(name, values):
        return '    <variable name="%s">\n%s    </variable>\n' % (name, ''.join(
            '        <value%s>%s</value>\n' % (' condition="%s"' % c if c else '', v) for c, v in values))
    # The pause screen's picture: an episode's still, else the film's backdrop.
    out = variable('SiloShowcaseStill', [
        ('!String.IsEmpty(VideoPlayer.TVShowTitle) + !String.IsEmpty(Player.Art(thumb))', '$INFO[Player.Art(thumb)]'),
        (None, '$INFO[Player.Art(fanart)]')])
    # Under the logo: "S3 E5 · Unbowed and Unbent", or a film's year and genres.
    out += variable('SiloShowcaseLine', [
        ('!String.IsEmpty(VideoPlayer.TVShowTitle)',
         '$INFO[VideoPlayer.Season,S,]$INFO[VideoPlayer.Episode, E,]$INFO[VideoPlayer.Title, · ,]'),
        (None, '$INFO[VideoPlayer.Year]$INFO[VideoPlayer.Genre, · ,]')])
    # The logo's stand-in: the show's or the film's name.
    out += variable('SiloShowcaseName', [
        ('!String.IsEmpty(VideoPlayer.TVShowTitle)', '$INFO[VideoPlayer.TVShowTitle]'),
        (None, '$INFO[VideoPlayer.Title]')])
    out += variable('SiloShowcaseResolution', [
        ('String.IsEqual(VideoPlayer.VideoResolution,%s)' % kodi, label) for kodi, label in RESOLUTIONS] + [
        ('!String.IsEmpty(VideoPlayer.VideoResolution)', 'SD')])
    out += variable('SiloShowcaseHdr', [
        ('String.IsEqual(VideoPlayer.HdrType,%s)' % kodi, label) for kodi, label in HDR])
    out += variable('SiloShowcaseAudio', [
        ('String.IsEqual(VideoPlayer.AudioCodec,%s) + String.IsEqual(VideoPlayer.AudioChannels,%s)' % (codec, n),
         label + layout) for codec, label in AUDIO for n, layout in CHANNELS] + [
        ('String.IsEqual(VideoPlayer.AudioCodec,%s)' % codec, label) for codec, label in AUDIO] + [
        (None, '[UPPERCASE]$INFO[VideoPlayer.AudioCodec][/UPPERCASE]')])
    out += variable('SiloShowcaseMpaa', [
        ('!String.IsEmpty(%s)' % PLAYING % 'mpaa', '$INFO[%s]' % PLAYING % 'mpaa'), (None, '$INFO[VideoPlayer.mpaa]')])
    # The pause screen's facts: "Jul 19, 2026 · 60 min" (a film: its year).
    out += variable('SiloShowcaseFacts', [
        ('!String.IsEmpty(VideoPlayer.TVShowTitle) + !String.IsEmpty(%s)' % PLAYING % 'air_date',
         '$INFO[%s]$INFO[VideoPlayer.Duration(mins), · , min]' % PLAYING % 'air_date'),
        ('!String.IsEmpty(VideoPlayer.TVShowTitle)', '$INFO[Player.Art(siloaired)]$INFO[VideoPlayer.Duration(mins), · , min]'),
        (None, '$INFO[VideoPlayer.Year]$INFO[VideoPlayer.Duration(mins), · , min]')])
    # The player's Play/Pause in Skyline's line (Kodi's Estuary icon elsewhere).
    out += variable('SiloOSDPlayIcon', [('Player.Playing', 'silo/osd_pause.png'), (None, 'silo/osd_play.png')])
    # The focused player button's name, under its row (VideoOSD.xml).
    out += variable('SiloOSDLeftName', [
        ('Control.HasFocus(609)', 'Back 10 seconds'),
        ('Control.HasFocus(602) + Player.Paused', 'Play'),
        ('Control.HasFocus(602)', 'Pause'),
        ('Control.HasFocus(610)', 'Forward 30 seconds')])
    out += variable('SiloOSDRightName', [
        ('Control.HasFocus(70051) + !String.IsEmpty(Window(Home).Property(silo.osd.episodes))', 'Hide episodes'),
        ('Control.HasFocus(70051)', 'Episodes'),
        ('Control.HasFocus(70050) + !String.IsEmpty(%s)' % PLAYING % 'next_label',
         'Next episode  ·  $INFO[%s]' % PLAYING % 'next_label'),
        ('Control.HasFocus(70050)', 'Next episode'),
        ('Control.HasFocus(70046)', 'Subtitles'),
        ('Control.HasFocus(70048)', 'Options'),
        ('Control.HasFocus(70049)', 'Close'),
        ('Control.HasFocus(804)', 'Disc menu'),
        ('Control.HasFocus(70042)', 'Playlist'),
        ('Control.HasFocus(70045)', 'Teletext'),
        ('Control.HasFocus(70047)', '3D')])
    out += '    <expression name="SiloPauseScreen">%s</expression>\n' % PAUSE_SCREEN
    return '\n' + out + '    '


def badge(label, visible):
    return '''
					<control type="button">
						<width>auto</width><height>36</height>
						<label>%(label)s</label>
						<font>silo_badge</font>
						<textoffsetx>12</textoffsetx>
						<aligny>center</aligny>
						<enable>false</enable>
						<disabledcolor>%(text)s</disabledcolor>
						<texturenofocus border="8" colordiffuse="%(outline)s">silo/badge_outline.png</texturenofocus>
						<texturefocus border="8" colordiffuse="%(outline)s">silo/badge_outline.png</texturefocus>
						<visible>%(visible)s</visible>
					</control>''' % {'label': label, 'visible': visible, 'text': TEXT, 'outline': BADGE}


def ratings(indent='\t\t\t\t\t'):
    """The IMDb, TMDB and Rotten Tomatoes marks with their scores, as the hero has them."""
    out = ''
    for rating, mark, width, height, top in (('imdb', 'silo/imdb.png', 60, 28, 4), ('tmdb', 'silo/tmdb.png', 165, 30, 3)):
        score = PLAYING % ('rating.' + rating)
        shown = '!String.IsEmpty(%s) + %s' % (score, RATING_SHOWN['themoviedb' if rating == 'tmdb' else rating])
        out += '''
%(i)s<control type="image">
%(i)s	<top>%(top)d</top><width>%(w)d</width><height>%(h)d</height>
%(i)s	<texture>%(mark)s</texture>
%(i)s	<visible>%(shown)s</visible>
%(i)s</control>
%(i)s<control type="label">
%(i)s	<width>auto</width><height>36</height>
%(i)s	<aligny>center</aligny>
%(i)s	<font>silo_meta</font>
%(i)s	<textcolor>%(text)s</textcolor>
%(i)s	<label> [B]$INFO[%(score)s][/B]  </label>
%(i)s	<visible>%(shown)s</visible>
%(i)s</control>''' % {'i': indent, 'top': top, 'w': width, 'h': height, 'mark': mark, 'shown': shown,
                       'score': score, 'text': TEXT}
    # Rotten Tomatoes' critics': the Fresh tomato (60% and up) or the Rotten splat.
    for rating, fresh, rotten in (('rtcritic', 'silo/rt_fresh.png', 'silo/rt_rotten.png'),):
        score = PLAYING % ('rating.' + rating)
        shown = '!String.IsEmpty(%s) + %s' % (score, RATING_SHOWN['rottentomatoes'])
        for mark, condition in ((fresh, 'Integer.IsGreaterOrEqual(%s,60)' % score),
                                (rotten, '!Integer.IsGreaterOrEqual(%s,60)' % score)):
            out += '''
%(i)s<control type="image">
%(i)s	<top>2</top><width>32</width><height>32</height>
%(i)s	<texture>%(mark)s</texture>
%(i)s	<visible>%(shown)s + %(condition)s</visible>
%(i)s</control>''' % {'i': indent, 'mark': mark, 'shown': shown, 'condition': condition}
        out += '''
%(i)s<control type="label">
%(i)s	<width>auto</width><height>36</height>
%(i)s	<aligny>center</aligny>
%(i)s	<font>silo_meta</font>
%(i)s	<textcolor>%(text)s</textcolor>
%(i)s	<label> [B]$INFO[%(score)s]%%[/B]  </label>
%(i)s	<visible>%(shown)s</visible>
%(i)s</control>''' % {'i': indent, 'shown': shown, 'score': score, 'text': TEXT}
    return out


def logo(left, top, width, height, font):
    """The clearlogo, or the name in its place."""
    return '''
			<control type="image">
				<left>%(x)d</left><top>%(y)d</top><width>%(w)d</width><height>%(h)d</height>
				<aspectratio align="left" aligny="bottom">keep</aspectratio>
				<texture>$VAR[PlayerClearLogoVar]</texture>
			</control>
			<control type="label">
				<left>%(x)d</left><top>%(y)d</top><width>%(w)d</width><height>%(h)d</height>
				<aligny>bottom</aligny>
				<font>%(font)s</font>
				<textcolor>%(text)s</textcolor>
				<label>$VAR[SiloShowcaseName]</label>
				<shadowcolor>99000000</shadowcolor>
				<visible>String.IsEmpty(Player.Art(clearlogo)) + String.IsEmpty(Player.Art(tvshow.clearlogo))</visible>
			</control>''' % {'x': left, 'y': top, 'w': width, 'h': height, 'font': font, 'text': TEXT}


def overlay():
    """Screen 1, over Silo's bar: logo, line and badges; a clock."""
    return '''
			<control type="group">
				<visible>%(on)s</visible>%(logo)s
				<control type="label">
					<left>96</left><top>720</top><width>1500</width><height>44</height>
					<font>silo_meta</font>
					<textcolor>%(text)s</textcolor>
					<label>$VAR[SiloShowcaseLine]</label>
					<shadowcolor>99000000</shadowcolor>
				</control>
				<control type="grouplist">
					<left>96</left><top>776</top><width>1728</width><height>40</height>
					<orientation>horizontal</orientation>
					<itemgap>10</itemgap>
					<usecontrolcoords>true</usecontrolcoords>%(badges)s
				</control>
				<control type="label">
					<left>1424</left><top>40</top><width>400</width><height>60</height>
					<align>right</align>
					<font>silo_osd_title</font>
					<textcolor>%(text)s</textcolor>
					<label>$INFO[System.Time]</label>
					<shadowcolor>99000000</shadowcolor>
				</control>
			</control>''' % {
        'on': ON, 'text': TEXT, 'logo': logo(96, 588, 720, 120, 'silo_osd_title').replace('\n\t\t\t', '\n\t\t\t\t'),
        # KodiConnectForSilo's badges for what's playing, else Kodi's player's own.
        'badges': badge('$VAR[SiloShowcaseMpaa]', '[!String.IsEmpty(%s) | !String.IsEmpty(VideoPlayer.mpaa)]' % PLAYING % 'mpaa')
        + ''.join(badge('$INFO[%s]' % PLAYING % name, '!String.IsEmpty(%s)' % PLAYING % name)
                  for name in ('badge1', 'badge2', 'badge3'))
        + ''.join(badge(label, 'String.IsEmpty(%s) + !String.IsEmpty(%s)' % (PLAYING % 'badge1', shown)) for label, shown in (
            ('$VAR[SiloShowcaseResolution]', 'VideoPlayer.VideoResolution'), ('$VAR[SiloShowcaseHdr]', 'VideoPlayer.HdrType'),
            ('$VAR[SiloShowcaseAudio]', 'VideoPlayer.AudioCodec')))}


# Showcase's bar, as Netflix's: play/pause at its left end (the OSD's button
# 602 sits there, VideoOSD.xml), the time left at its right end, the OSD's
# named buttons under it with the end time at that row's right.
PLAY_X, PLAY_SIZE = 96, 74
BAR_X, BAR_TOP, BAR_H = 198, 896, 8
TIME_W = 140   # −1:57:33
HANDLE = 22    # the handle, under three times the bar, as Netflix's (Silo's is 30)
ENDS_TOP = 974  # centred on the OSD's button row (VideoOSD.xml, 962 to 1022)
BAR_W = 1824 - TIME_W - 24 - BAR_X
# Silo's marker bands (KodiConnectForSilo): plain white over the track, as
# the rest of Showcase's player; where a band sits says what it is. Silo's
# player style keeps Silo's colours (DialogSeekBar.xml).
MARKERS = tuple((name, '99FFFFFF') for name in ('intro', 'recap', 'credits', 'preview'))


def bar():
    """Track, buffered, played, Silo's marker bands, chapter ticks, the handle and the times."""
    place = '<left>%d</left><top>%d</top><width>%d</width><height>%d</height>' % (BAR_X, BAR_TOP, BAR_W, BAR_H)
    middle = BAR_TOP + BAR_H // 2
    out = '''
			<control type="group">
				<visible>%(on)s</visible>
				<control type="image">
					%(place)s
					<texture colordiffuse="33FFFFFF">colors/white.png</texture>
				</control>''' % {'on': ON, 'place': place}
    for info, colour in (('Player.ProgressCache', '33FFFFFF'), ('Player.Progress', 'FFEDEDED')):
        out += '''
				<control type="progress">
					%s
					<info>%s</info>
					<texturebg colordiffuse="00FFFFFF">colors/white.png</texturebg>
					<midtexture colordiffuse="%s">colors/white.png</midtexture>
				</control>''' % (place, info, colour)
    for name, colour in MARKERS:
        out += '''
				<control type="ranges">
					%s
					<texturebg colordiffuse="00FFFFFF">colors/white.png</texturebg>
					<lefttexture />
					<midtexture colordiffuse="%s">colors/white.png</midtexture>
					<righttexture />
					<info>Window(Home).Property(silokodi.markers.%s)</info>
				</control>''' % (place, colour, name)
    out += '''
				<!-- The chapters' starts, ticks on the bar. -->
				<control type="ranges">
					<left>%(x)d</left><top>%(tick)d</top><width>%(w)d</width><height>16</height>
					<texturebg colordiffuse="00FFFFFF">colors/white.png</texturebg>
					<lefttexture />
					<midtexture colordiffuse="00FFFFFF">colors/white.png</midtexture>
					<righttexture colordiffuse="CCFFFFFF">colors/white.png</righttexture>
					<info>Player.Chapters</info>
				</control>''' % {'x': BAR_X, 'w': BAR_W, 'tick': middle - 8}
    for info, shows in (('Player.Progress', '!Player.Seeking'), ('Player.SeekBar', 'Player.Seeking')):
        out += '''
				<control type="slider">
					<left>%(x)d</left><top>%(y)d</top><width>%(w)d</width><height>%(h)d</height>
					<info>%(info)s</info>
					<texturesliderbar colordiffuse="00FFFFFF">silo/avatar_mask.png</texturesliderbar>
					<textureslidernib>silo/avatar_mask.png</textureslidernib>
					<textureslidernibfocus>silo/avatar_mask.png</textureslidernibfocus>
					<visible>%(shows)s</visible>
				</control>''' % {'x': BAR_X - HANDLE // 2, 'y': middle - HANDLE // 2, 'w': BAR_W + HANDLE, 'h': HANDLE,
                                'info': info, 'shows': shows}
    for label, shows in (('$INFO[Player.TimeRemaining,−,]', '!Player.Seeking + String.IsEmpty(Player.SeekNumeric)'),
                         ('$INFO[Player.SeekTime]', 'Player.Seeking | !String.IsEmpty(Player.SeekNumeric)')):
        out += '''
				<control type="label">
					<left>%(x)d</left><top>%(y)d</top><width>%(w)d</width><height>36</height>
					<align>right</align><aligny>center</aligny>
					<font>silo_detail</font>
					<textcolor>%(text)s</textcolor>
					<label>%(label)s</label>
					<shadowcolor>99000000</shadowcolor>
					<visible>%(shows)s</visible>
				</control>''' % {'x': 1824 - TIME_W, 'y': middle - 18, 'w': TIME_W, 'text': TEXT, 'label': label,
                                 'shows': shows}
    out += '''
				<control type="label">
					<left>1224</left><top>%(y)d</top><width>600</width><height>36</height>
					<align>right</align><aligny>center</aligny>
					<font>silo_detail</font>
					<textcolor>%(dim)s</textcolor>
					<label>$INFO[Player.FinishTime,Ends ,]</label>
					<shadowcolor>99000000</shadowcolor>
				</control>''' % {'y': ENDS_TOP, 'dim': DIM}
    # Play/pause at the bar's left end while the OSD (whose button it is) is closed.
    out += '''
				<control type="group">
					<left>%(x)d</left><top>%(y)d</top>
					<visible>!Window.IsVisible(videoosd)</visible>
					<control type="image">
						<width>%(s)d</width><height>%(s)d</height>
						<texture>silo/osd_button_rest.png</texture>
					</control>
					<control type="image">
						<width>%(s)d</width><height>%(s)d</height>
						<texture colordiffuse="FFEDEDED">$VAR[SiloOSDPlayIcon]</texture>
					</control>
				</control>
			</control>
			''' % {'x': PLAY_X, 'y': middle - PLAY_SIZE // 2, 's': PLAY_SIZE}
    return out


def pause_screen():
    """Screen 2: after ten idle seconds paused, what's playing over the dimmed picture."""
    return '''
		<control type="group">
			<visible>$EXP[SiloVideoPlayer]</visible>
			<visible>$EXP[SiloPauseScreen]</visible>
			<animation effect="fade" start="0" end="100" time="400">Visible</animation>
			<animation effect="fade" start="100" end="0" time="200">Hidden</animation>
			<control type="image">
				<left>0</left><top>0</top><width>1920</width><height>1080</height>
				<texture colordiffuse="B3000000">colors/white.png</texture>
			</control>
			<control type="label">
				<left>120</left><top>150</top><width>900</width><height>32</height>
				<font>silo_badge</font>
				<textcolor>%(dim)s</textcolor>
				<label>YOU'RE WATCHING</label>
			</control>%(logo)s
			<control type="label">
				<left>120</left><top>404</top><width>900</width><height>50</height>
				<font>silo_row</font>
				<textcolor>%(text)s</textcolor>
				<label>$VAR[SiloShowcaseLine]</label>
			</control>
			<control type="grouplist">
				<left>120</left><top>462</top><width>900</width><height>40</height>
				<orientation>horizontal</orientation>
				<usecontrolcoords>true</usecontrolcoords>
				<control type="label">
					<width>auto</width><height>36</height>
					<aligny>center</aligny>
					<font>silo_meta</font>
					<textcolor>%(dim)s</textcolor>
					<label>$VAR[SiloShowcaseFacts]  </label>
				</control>%(ratings)s
			</control>
			<control type="textbox">
				<left>120</left><top>520</top><width>900</width><height>250</height>
				<font>silo_detail</font>
				<textcolor>%(plot)s</textcolor>
				<label>$INFO[VideoPlayer.Plot]</label>
			</control>
			<control type="image">
				<left>1160</left><top>160</top><width>640</width><height>360</height>
				<aspectratio scalediffuse="false">scale</aspectratio>
				<texture background="true" diffuse="silo/card_landscape_mask.png">$VAR[SiloShowcaseStill]</texture>
			</control>
			<!-- Where playback is. -->
			<control type="image">
				<left>120</left><top>960</top><width>1680</width><height>6</height>
				<texture colordiffuse="40FFFFFF">colors/white.png</texture>
			</control>
			<control type="progress">
				<left>120</left><top>960</top><width>1680</width><height>6</height>
				<info>Player.Progress</info>
				<texturebg colordiffuse="00FFFFFF">colors/white.png</texturebg>
				<midtexture colordiffuse="FFEDEDED">colors/white.png</midtexture>
			</control>
			<control type="label">
				<left>120</left><top>980</top><width>800</width><height>36</height>
				<font>silo_detail</font>
				<textcolor>%(dim)s</textcolor>
				<label>$INFO[Player.Time]$INFO[Player.Duration, / ,]</label>
			</control>
			<control type="label">
				<left>1000</left><top>980</top><width>800</width><height>36</height>
				<align>right</align>
				<font>silo_detail</font>
				<textcolor>%(dim)s</textcolor>
				<label>$INFO[Player.FinishTime,Ends ,]</label>
			</control>
		</control>
		''' % {'dim': DIM, 'text': TEXT, 'plot': TEXT_DIM, 'logo': logo(120, 196, 900, 190, 'silo_osd_title'),
               'ratings': ratings('\t\t\t\t')}


TIMER = '''
    <timer>
        <name>silo_pause_screen</name>
        <description>Showcase's pause screen: ten seconds paused with no key pressed closes the OSD so it can show (tools/build_showcase.py)</description>
        <start>%s + Player.Paused + System.IdleTime(%d) + Window.IsActive(videoosd) + !Window.IsActive(1180)</start>
        <onstart>Dialog.Close(videoosd)</onstart>
        <stop>!Window.IsActive(videoosd) | !Player.Paused</stop>
    </timer>
    <timer>
        <name>silo_pause_shown</name>
        <description>Showcase's pause screen has shown since the video paused: Back dismisses it (window 1188, tools/build_showcase.py)</description>
        <start reset="true">%s + %s + Player.Paused + !Window.IsActive(videoosd) + System.IdleTime(%d)</start>
        <stop>!Player.Paused | Window.IsActive(videoosd)</stop>
    </timer>
    ''' % (ON, PAUSE_IDLE, ON, VIDEO_PLAYER, PAUSE_IDLE)

PAUSE_BACK_WINDOW = '''<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by tools/build_showcase.py: edit that, not this. -->
<!-- Back in the video window (KodiConnectForSilo's player keymap): Kodi's own Back
     (leave the video for the menus), unless Showcase's pause screen has shown
     since the video paused, which Back only dismisses. Leaving Live TV for the
     guide, it says so (silo.guide.fromplayer): Back there then leaves the
     guide, rather than returning to the video (build_tv.py, window 1189). -->
<window type="dialog" id="%(id)d">
    <onload condition="!Skin.TimerIsRunning(silo_pause_shown)">Dialog.Close(%(id)d,true)</onload>
    <onload condition="!Skin.TimerIsRunning(silo_pause_shown) + VideoPlayer.Content(LiveTV)">SetProperty(silo.guide.fromplayer,1,home)</onload>
    <onload condition="!Skin.TimerIsRunning(silo_pause_shown)">Action(Back)</onload>
    <onload condition="Skin.TimerIsRunning(silo_pause_shown)">Skin.TimerStop(silo_pause_shown)</onload>
    <onload>Dialog.Close(%(id)d,true)</onload>
    <controls />
</window>
''' % {'id': PAUSE_BACK}

SETTING_BUTTON = '''
				<control type="button" id="793">
					<label>Player style</label>
					<label2>$VAR[SkylinePlayerStyle]</label2>
					<include>DefaultSettingButton</include>
					<onclick>Skin.ToggleSetting(%s)</onclick>
				</control>
				''' % SETTING


def main():
    def edit(name, change):
        path = os.path.join(ROOT, 'xml', name)
        text = open(path, encoding='utf-8').read()
        open(path, 'w', encoding='utf-8').write(change(text))

    def seekbar(text):
        # Silo's eyebrow and title give way to Showcase's, and the chrome to the pause screen.
        for label in ('<label>[UPPERCASE]$VAR[SiloPlayerEyebrow][/UPPERCASE]</label>',
                      '<label>$INFO[VideoPlayer.Title]</label>\n\t\t\t\t<shadowcolor>99000000</shadowcolor>'):
            # Silo's eyebrow and title show only with Silo's player (any visible
            # line an earlier build put after them goes).
            text = re.sub(re.escape(label) + r'(\n\t\t\t\t<visible>[^<]*</visible>)*',
                          lambda m: label + '\n\t\t\t\t<visible>Skin.HasSetting(%s)</visible>' % SETTING, text, count=1)
        chrome = '<visible>$EXP[SiloVideoPlayer]</visible>\n\t\t\t<animation effect="fade" start="0" end="100" time="200">Visible</animation>'
        if '!$EXP[SiloPauseScreen]' not in text:
            text = text.replace(chrome, chrome.replace('</visible>', ' + !$EXP[SiloPauseScreen]</visible>', 1), 1)
        # The chrome steps aside while the OSD's Episodes strip is open (VideoOSD.xml).
        episodes = ' + String.IsEmpty(Window(Home).Property(silo.osd.episodes))'
        paused = chrome.replace('</visible>', ' + !$EXP[SiloPauseScreen]</visible>', 1)
        if episodes not in text:
            text = text.replace(paused, paused.replace('</visible>', episodes + '</visible>', 1), 1)
        text = put(text, 'Showcase overlay', overlay() + '\n\t\t\t', '\t\t\t<!-- The bar: track, buffered, played. -->')
        text = drop(text, 'Showcase chapters')  # now on Showcase's own bar
        return put(text, 'Showcase bar', bar(), "\t\t\t<!-- Showcase's bar. -->", before=False)

    edit('DialogSeekBar.xml', seekbar)
    edit('DialogSeekBar.xml', lambda text: put(text, 'Showcase pause screen', pause_screen(),
                                               "\t\t<!-- Silo Skyline: Silo's player chrome for video."))
    edit('VideoFullScreen.xml', lambda text: drop(text, 'Showcase pause screen'))
    edit('Timers.xml', lambda text: put(text, 'Showcase timer', TIMER, '</timers>'))
    with open(os.path.join(ROOT, 'xml', 'Custom_%d_SiloPauseBack.xml' % PAUSE_BACK), 'w', encoding='utf-8') as handle:
        handle.write(PAUSE_BACK_WINDOW)
    style = ('\n    <variable name="SkylinePlayerStyle">\n        <value condition="%s">Showcase</value>\n'
             '        <value>Silo</value>\n    </variable>\n    ' % ON)
    edit('Variables.xml', lambda text: put(text, 'Showcase', variables() + style.lstrip(' '), '</includes>'))
    # First in Player (build_frame.skyline_options), above the OSD's auto-close.
    edit('SkinSettings.xml', lambda text: put(text, 'player style', SETTING_BUTTON,
                                               '\t\t\t\t<control type="radiobutton" id="623">'))
    print('Wrote the Showcase player style into DialogSeekBar.xml, Timers.xml, Variables.xml and SkinSettings.xml')


if __name__ == '__main__':
    main()
