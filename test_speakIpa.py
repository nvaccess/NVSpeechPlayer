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

player=speechPlayer.SpeechPlayer(16000)
time.sleep(0.05)
text=codecs.open(sys.argv[1],'r','utf8').read()
#text=text.replace(u'a',u'æ')
for line in text.splitlines():
	for args in ipa.generateFramesAndTiming(line.strip(),startPitch=160,endPitch=70):
		player.queueFrame(*args)
	player.queueFrame(None,150,0)
time.sleep(300)
