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

import itertools
import time
import os
import sys
import speechPlayer
import ipa

player=speechPlayer.SpeechPlayer(16000)
frame=speechPlayer.Frame()
frame.outputGain=1.0
frame.preFormantGain=1.0
frame.voiceAmplitude=1.0
vowels=list(ipa.iterPhonemes(isVowel=True))
for firstVowel,lastVowel in itertools.product(vowels,vowels): 
	player.queueFrame(None,0,0,purgeQueue=True)
	frame.voicePitch=50
	print u"%r %r"%(firstVowel,lastVowel) 
	ipa.setFrame(frame,firstVowel)
	player.queueFrame(frame,50,50)
	frame.voicePitch=200
	ipa.setFrame(frame,lastVowel)
	player.queueFrame(frame,500,500)
	frame.voicePitch=150
	player.queueFrame(frame,250,250,finalVoicePitch=75)
	player.queueFrame(None,50,50)
	raw_input()
del player

