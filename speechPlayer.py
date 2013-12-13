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

from ctypes import *

class FormantParams(Structure):
	_fields_=[
		('frequency',c_double),
		('bandwidth',c_double),
		('amplitude',c_double),
	]

class Frame(Structure):
	_fields_=[
		('voiceAmplitude',c_double),
		('voicePitch',c_double),
		('breathyness',c_double),
		('vibratoOffset',c_double),
		('vibratoSpeed',c_double),
		('formantParams',FormantParams*4),
	]

class SpeechPlayer(object):

	def __init__(self,sampleRate):
		self._dll=cdll.speechPlayer
		self._speechHandle=self._dll.speechPlayer_initialize(sampleRate)

	def setNewFrame(self,frame,count):
		frame=byref(frame) if frame else None
		self._dll.speechPlayer_setNewFrame(self._speechHandle,frame,count)

	def __del__(self):
		self._dll.speechPlayer_terminate(self._speechHandle)

class VowelChart(object):

	def __init__(self,fileName):
		self._vowels={}
		with open(fileName,'r') as f:
			for line in f.readlines():
				params=line.split()
				vowel=params.pop(0)
				flag=params.pop(0)
				if flag=='1': continue
				starts=[int(params[x]) for x in xrange(3)]
				ends=[int(params[x]) for x in xrange(3,6)]
				self._vowels[vowel]=starts,ends

	def applyVowel(self,frame,vowel,end=False):
		data=self._vowels[vowel][0 if not end else 1]
		for index,frequency in enumerate(data):
			frame.formantParams[index].frequency=frequency
			frame.formantParams[index].bandwidth=30
			frame.formantParams[index].amplitude=1.0
