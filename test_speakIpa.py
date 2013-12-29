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

import codecs
import time
import sys
import speechPlayer
import ipa

player=speechPlayer.SpeechPlayer(22050)
text=codecs.open('sampleIpa.txt','r','utf8').read()
for line in text.splitlines():
	for chunk in line.strip().split():
		for args in ipa.generateFramesAndTiming(chunk,basePitch=160):
			player.queueFrame(*args)
	player.queueFrame(None,150,0)
time.sleep(300)
