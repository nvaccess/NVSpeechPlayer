import ctypes
import sys
import codecs
import ipa
import time
import speechPlayer
from lavPlayer import LavPlayer

speed=1

player=speechPlayer.SpeechPlayer(22050)
lavPlayer=LavPlayer(player,22050)

frame=speechPlayer.Frame()
frame.outputGain=1.0
frame.preFormantGain=1.0
frame.vibratoPitchOffset=0.1
frame.vibratoSpeed=5.5
frame.voicePitch=150
ipa.setFrame(frame,'æ')
frame.voiceAmplitude=0
player.queueFrame(frame,120/speed,100/speed)
frame.voiceAmplitude=1
player.queueFrame(frame,120/speed,40/speed)
ipa.setFrame(frame,'n')
frame.voicePitch=100
player.queueFrame(frame,120/speed,40/speed)
ipa.setFrame(frame,'ɑ')
frame.voicePitch=90
player.queueFrame(frame,80/speed,40/speed)
player.queueFrame(None,40/speed,40/speed)
time.sleep(10)
