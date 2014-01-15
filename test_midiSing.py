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

import sys
import os
from ctypes import *
from ctypes.wintypes import *
import speechPlayer
import ipa
phonemeList=list(ipa.iterPhonemes(_isVoiced=True))

MIN_DATA=0x3c3

HMIDIIN=HANDLE

MidiInProc=WINFUNCTYPE(None,HMIDIIN,c_uint,DWORD,DWORD,DWORD)

frame=speechPlayer.Frame()
frame.preFormantGain=2.0
frame.voiceAmplitude=1.0
frame.vibratoPitchOffset=0.125
frame.vibratoSpeed=5.5

class MidiSing(object):

	def __init__(self,midiDevice,sampleRate):
		self._player=speechPlayer.SpeechPlayer(sampleRate)
		self._midiHandle=HMIDIIN()
		self._cMidiInProc=MidiInProc(self.midiInProc)
		windll.winmm.midiInOpen(byref(self._midiHandle),midiDevice,self._cMidiInProc,None,0x30000)
		windll.winmm.midiInStart(self._midiHandle)
		self._lastPhoneme=ipa.data[sys.argv[2]]
		ipa.applyPhonemeToFrame(frame,self._lastPhoneme)

	_noteStack=[]
	_noteState={}
	_notePlaying=False

	def midiInProc(self,midiHandle,msg,instance,param1,param2):
		if msg!=MIN_DATA: return
		message=param1&0xff
		data1=(param1>>8)&0xff
		data2=(param1>>16)&0xff
		noteChange=False
		if message==0x90 and data2>0: #note on
			self._noteStack.append(data1)
			self._noteState[data1]=data2
			noteChange=True
		elif message==0x80 or message==0x90: #note off
			try:
				self._noteStack.remove(data1)
				self._noteState.pop(data1)
			except (ValueError,KeyError,IndexError):
				pass
			if len(self._noteStack)>0:
				data1=self._noteStack[-1]
				data2=self._noteState[data1]
			else:
				data1=None
			noteChange=True
		elif message==0xb0:
			numPhonemes=len(phonemeList)
			phonemeIndex=int(data2*(numPhonemes/128.0))
			phoneme=self._lastPhoneme=ipa.data[phonemeList[phonemeIndex]]
			ipa.applyPhonemeToFrame(frame,phoneme)
			if self._notePlaying: self._player.queueFrame(frame,100,100,purgeQueue=True)
		elif message==0xe0:
			if data2<64:
				frame.glottalOpenQuotient=0.1*((64-data2)/64.0)
			else:
				frame.voiceTurbulenceAmplitude=0
			frame.vibratoSpeed=(5.5+((data2-64)/64.0)) if data2>=64 else 5.5
			frame.vibratoPitchOffset=(0.125+(((data2-64)/64.0)*0.875)) if data2>=64 else (0.125*(data2/64.0)) 
			self._player.queueFrame(frame,100,100,purgeQueue=True)
		elif False: #message!=0xfe:
			print "message: %x, %d, %d"%(message,data1,data2)
		if noteChange:
			if data1 is not None:
				hz=440*(2**((data1-69)/12.0))
				frame.endVoicePitch=frame.voicePitch=hz
				frame.preFormantGain=data2/64.0
				ipa.applyPhonemeToFrame(frame,self._lastPhoneme)
				self._player.queueFrame(frame,50,50,purgeQueue=True)
				self._notePlaying=True
			else:
				frame.preFormantGain=0
				frame.endVoicePitch=frame.voicePitch=1
				self._player.queueFrame(frame,50,50,purgeQueue=True)
				self._player.queueFrame(None,0,0)
				self._notePlaying=False

m=MidiSing(int(sys.argv[1]),16000)
while True:
	windll.kernel32.SleepEx(100,True)
