####
# Copyright 2013 Michael Curran <mick@nvaccess.org>.
    # This program is free software: you can redistribute it and/or modify
    # it under the terms of the GNU Lesser General Public License version 2.1, as published by
    # the Free Software Foundation.
    # This program is distributed in the hope that it will be useful,
    # but WITHOUT ANY WARRANTY; without even the implied warranty of
    # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# This license can be found at:
# http://www.gnu.org/licenses/old-licenses/lgpl-2.1.html
####

import time
import os
import sys
import speechPlayer

player=speechPlayer.SpeechPlayer(22050)
raw_input()
frame=speechPlayer.Frame()
frame.gain=1.0
frame.voiceAmplitude=1.0
frame.dcf1=10
frame.dcb1=10
frame.voiceTurbulenceAmplitude=0.75
frame.glottalOpenQuotient=0.025
vowelChart=speechPlayer.VowelChart(os.path.join('vowelcharts',sys.argv[1]))
for vowel in vowelChart._vowels.iterkeys():
	frame.voicePitch=20
	frame.voiceAmplitude=1.0;
	print vowel
	vowelChart.applyVowel(frame,vowel)
	player.setNewFrame(frame,1000)
	time.sleep(0.05)
	frame.voicePitch=200
	vowelChart.applyVowel(frame,vowel,True)
	player.setNewFrame(frame,15000)
	time.sleep(0.75)
	frame.voicePitch=20
	player.setNewFrame(frame,5000)
	time.sleep(0.25)
frame.voicePitch=1
player.setNewFrame(frame,5000)
time.sleep(0.5)
del player

