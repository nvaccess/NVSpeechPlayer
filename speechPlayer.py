###
#This file is a part of the NV Speech Player project. 
#URL: https://bitbucket.org/nvaccess/speechplayer
#Copyright 2014 NV Access Limited.
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License version 2.0, as published by
#the Free Software Foundation.
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#This license can be found at:
#http://www.gnu.org/licenses/old-licenses/gpl-2.0.html
###

from ctypes import *
import os

speechPlayer_frameParam_t=c_double

class Frame(Structure):
	_fields_=[(name,speechPlayer_frameParam_t) for name in [
		'voicePitch',
		'vibratoPitchOffset',
		'vibratoSpeed',
		'voiceTurbulenceAmplitude',
		'glottalOpenQuotient',
		'voiceAmplitude',
		'aspirationAmplitude',
		'cf1','cf2','cf3','cf4','cf5','cf6','cfN0','cfNP',
		'cb1','cb2','cb3','cb4','cb5','cb6','cbN0','cbNP',
		'caNP',
		'fricationAmplitude',
		'pf1','pf2','pf3','pf4','pf5','pf6',
		'pb1','pb2','pb3','pb4','pb5','pb6',
		'pa1','pa2','pa3','pa4','pa5','pa6',
		'parallelBypass',
		'preFormantGain',
		'endVoicePitch',
	]]

dllPath=os.path.join(os.path.dirname(__file__),'speechPlayer.dll')

class SpeechPlayer(object):

	def __init__(self,sampleRate):
		self._dll=cdll.LoadLibrary(dllPath)
		self._speechHandle=self._dll.speechPlayer_initialize(sampleRate)

	def queueFrame(self,frame,minFrameDuration,fadeDuration,userIndex=-1,purgeQueue=False):
		frame=byref(frame) if frame else None
		self._dll.speechPlayer_queueFrame(self._speechHandle,frame,c_double(minFrameDuration),c_double(fadeDuration),userIndex,purgeQueue)

	def synthesize(self,numSamples):
		buf=c_buffer(numSamples*2)
		res=self._dll.speechPlayer_synthesize(self._speechHandle,numSamples,buf)
		if res>0:
			return string_at(buf,res*2)
		else:
			return None

	def getLastIndex(self):
		return self._dll.speechPlayer_getLastIndex(self._speechHandle)

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
		frame.cf1=data[0]
		frame.cb1=60
		frame.ca1=1
		frame.cf2=data[1]
		frame.cb2=90
		frame.ca2=1
		frame.cf3=data[2]
		frame.cb3=120
		frame.ca3=1
		frame.ca4=frame.ca5=frame.ca6=frame.caN0=frame.caNP=0
		frame.fricationAmplitude=0
		frame.voiceAmplitude=1
		frame.aspirationAmplitude=0
