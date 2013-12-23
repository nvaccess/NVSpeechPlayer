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

MIN_DATA=0x3c3

HMIDIIN=HANDLE

MidiInProc=WINFUNCTYPE(None,HMIDIIN,c_uint,DWORD,DWORD,DWORD)

vowelChart=speechPlayer.VowelChart(os.path.join('vowelcharts',sys.argv[2]))

frame=speechPlayer.Frame()
frame.gain=1.0
frame.voiceAmplitude=1.0
frame.dcf1=10
frame.dcb1=10
frame.voiceTurbulenceAmplitude=0.75
frame.glottalOpenQuotient=0.025
frame.vibratoPitchOffset=0.125
frame.vibratoSpeed=5.5

class MidiSing(object):

	def __init__(self,midiDevice,sampleRate):
		self._player=speechPlayer.SpeechPlayer(sampleRate)
		self._midiHandle=HMIDIIN()
		self._cMidiInProc=MidiInProc(self.midiInProc)
		windll.winmm.midiInOpen(byref(self._midiHandle),midiDevice,self._cMidiInProc,None,0x30000)
		windll.winmm.midiInStart(self._midiHandle)
		self._lastVowel=sys.argv[3]
		vowelChart.applyVowel(frame,self._lastVowel)

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
			vowels=vowelChart._vowels.keys()
			numVowels=len(vowels)
			vowelIndex=int(data2*(numVowels/128.0))
			vowel=self._lastVowel=vowels[vowelIndex]
			vowelChart.applyVowel(frame,vowel)
			self._player.setNewFrame(frame,2000)
		elif message==0xe0:
			if data2<64:
				frame.voiceTurbulenceAmplitude=(64-data2)/64.0
			else:
				frame.voiceTurbulenceAmplitude=0
			frame.vibratoSpeed=(5.5+((data2-64)/64.0)) if data2>=64 else 5.5
			frame.vibratoPitchOffset=(0.125+(((data2-64)/64.0)*0.875)) if data2>=64 else (0.125*(data2/64.0)) 
			self._player.setNewFrame(frame,2000)
		elif False: #message!=0xfe:
			print "message: %x, %d, %d"%(message,data1,data2)
		if noteChange:
			if data1 is not None:
				hz=440*(2**((data1-69)/12.0))
				frame.voicePitch=hz
				frame.voiceAmplitude=data2/128.0
				vowelChart.applyVowel(frame,self._lastVowel,False)
				self._player.setNewFrame(frame,2500 if self._notePlaying else 2000)
				self._notePlaying=True
			else:
				frame.voicePitch=1
				frame.voiceAmplitude=0
				self._player.setNewFrame(frame,2000)
				self._notePlaying=False

m=MidiSing(int(sys.argv[1]),22050)
while True:
	windll.kernel32.SleepEx(100,True)

