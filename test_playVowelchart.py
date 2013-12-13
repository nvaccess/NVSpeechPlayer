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
frame=speechPlayer.Frame()
with open(os.path.join("./vowelcharts",sys.argv[1]),'r') as f:
	for line in f.readlines():
		frame.voicePitch=20
		frame.voiceAmplitude=1.0;
		params=line.split()
		vowel=params.pop(0)
		flag=params.pop(0)
		if flag=='1': continue
		print vowel
		starts=[int(params[x]) for x in xrange(3)]
		ends=[int(params[x]) for x in xrange(3,6)]
		for x in xrange(3):
			frame.formantParams[x].frequency=starts[x]
			frame.formantParams[x].bandwidth=30
			frame.formantParams[x].amplitude=1.0
		player.setNewFrame(frame,1000)
		time.sleep(0.05)
		for x in xrange(3):
			frame.formantParams[x].frequency=ends[x]
		frame.voicePitch=200
		player.setNewFrame(frame,15000)
		time.sleep(0.75)
		frame.voicePitch=20
		player.setNewFrame(frame,5000)
		time.sleep(0.25)
frame.voicePitch=1
player.setNewFrame(frame,5000)
time.sleep(0.5)
del player

