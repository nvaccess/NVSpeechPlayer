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
codecs.register(lambda x: codecs.lookup("_mbcs") if x=="cp0" else None)
 
import itertools
import time
import os
import sys
import speechPlayer
import ipa
from lavPlayer import LavPlayer

player=speechPlayer.SpeechPlayer(22050)
lavPlayer=LavPlayer(player,22050)

frame=speechPlayer.Frame()
frame.preFormantGain=1.0
frame.voiceAmplitude=1.0
frame.outputGain=1.0
vowels=list(ipa.iterPhonemes(_isVoiced=True))
for firstVowel,lastVowel in itertools.product(vowels,vowels): 
	player.queueFrame(None,0,20,purgeQueue=True)
	frame.voicePitch=40
	frame.endVoicePitch=300
	#print u"%r %r"%(firstVowel,lastVowel) 
	ipa.setFrame(frame,firstVowel)
	player.queueFrame(frame,300,50)
	frame.voicePitch=300
	frame.endVoicePitch=40
	ipa.setFrame(frame,lastVowel)
	player.queueFrame(frame,500,400)
	player.queueFrame(None,50,50)
	input()
del player

