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

import re
import threading
import math
from collections import OrderedDict
import ctypes
import weakref
from . import speechPlayer
from . import ipa
import config
import nvwave
import speech
from logHandler import log
from synthDrivers import _espeak
from synthDriverHandler import SynthDriver, VoiceInfo, synthIndexReached, synthDoneSpeaking
from driverHandler import NumericDriverSetting


class AudioThread(threading.Thread):

	wavePlayer=None
	keepAlive=True
	isSpeaking=False
	synthEvent=None
	initializeEvent=None

	def __init__(self,synth, speechPlayerObj,sampleRate):
		self.synthRef=weakref.ref(synth)
		self.speechPlayer=speechPlayerObj
		self.sampleRate=sampleRate
		self.initializeEvent=threading.Event()
		super(AudioThread,self).__init__()
		self.start()
		self.initializeEvent.wait()

	def terminate(self):
		self.initializeEvent.clear()
		self.keepAlive=False
		self.isSpeaking=False
		self.synthEvent.set()
		self.initializeEvent.wait()

	def run(self):
		try:
			self.wavePlayer=nvwave.WavePlayer(channels=1, samplesPerSec=self.sampleRate, bitsPerSample=16, outputDevice=config.conf["speech"]["outputDevice"])
			self.synthEvent=threading.Event()
		finally:
			self.initializeEvent.set()
		while self.keepAlive:
			self.synthEvent.wait()
			self.synthEvent.clear()
			lastIndex=None
			while self.keepAlive:
				data=self.speechPlayer.synthesize(8192)
				if self.isSpeaking and data:
					indexNum=self.speechPlayer.getLastIndex()
					self.wavePlayer.feed(
						ctypes.string_at(data,data.length*2),
						onDone=lambda indexNum=indexNum: synthIndexReached.notify(synth=self.synthRef(),index=indexNum) if indexNum>=0 else False
					)
					lastIndex=indexNum
				else:
					indexNum=self.speechPlayer.getLastIndex()
					if indexNum>0 and indexNum!=lastIndex:
						synthIndexReached.notify(synth=self.synthRef(),index=indexNum)
					self.wavePlayer.idle()
					synthDoneSpeaking.notify(synth=self.synthRef())
					break
		self.initializeEvent.set()

re_textPause=re.compile(r"(?<=[.?!,:;])\s",re.DOTALL|re.UNICODE)

voices={
	'Adam':{
		'cb1_mul':1.3,
		'pa6_mul':1.3,
		'fricationAmplitude_mul':0.85,
	},
		'Benjamin':{
		'cf1_mul':1.01,
		'cf2_mul':1.02,
		#'cf3_mul':0.96,
		'cf4':3770,
		'cf5':4100,
		'cf6':5000,
		'cfNP_mul':0.9,
		'cb1_mul':1.3,
		'fricationAmplitude_mul':0.7,
		'pa6_mul':1.3,
	},
	'Caleb ':{
		'aspirationAmplitude':1,
		'voiceAmplitude':0,
	},
	'David':{
		'voicePitch_mul':0.75,
		'endVoicePitch_mul':0.75,
		'cf1_mul':0.75,
		'cf2_mul':0.85,
		'cf3_mul':0.85,
	},
}

def applyVoiceToFrame(frame,voiceName):
	v=voices[voiceName]
	for paramName in (x[0] for x in frame._fields_):
		absVal=v.get(paramName)
		if absVal is not None:
			setattr(frame,paramName,absVal)
		mulVal=v.get('%s_mul'%paramName)
		if mulVal is not None:
			setattr(frame,paramName,getattr(frame,paramName)*mulVal)

class SynthDriver(SynthDriver):

	exposeExtraParams=True

	def __init__(self):
		if self.exposeExtraParams:
			self._extraParamNames=[x[0] for x in speechPlayer.Frame._fields_]
			self.supportedSettings=SynthDriver.supportedSettings+tuple(NumericDriverSetting("speechPlayer_%s"%x,"frame.%s"%x,normalStep=1) for x in self._extraParamNames)
			for x in self._extraParamNames:
				setattr(self,"speechPlayer_%s"%x,50)
		self.player=speechPlayer.SpeechPlayer(16000)
		_espeak.initialize()
		_espeak.setVoiceByLanguage('en')
		self.pitch=50
		self.rate=50
		self.volume=90
		self.inflection=60
		self.audioThread=AudioThread(self,self.player,16000)

	@classmethod
	def check(cls):
		return True

	name="nvSpeechPlayer"
	description="nvSpeechPlayer"

	supportedSettings=(SynthDriver.VoiceSetting(),SynthDriver.RateSetting(),SynthDriver.PitchSetting(),SynthDriver.VolumeSetting(),SynthDriver.InflectionSetting())

	supportedCommands = {
		speech.IndexCommand,
		speech.PitchCommand,
	}

	supportedNotifications = {synthIndexReached,synthDoneSpeaking}

	_curPitch=50
	_curVoice='Adam'
	_curInflection=0.5
	_curVolume=1.0
	_curRate=1.0

	def speak(self,speakList):
		userIndex=None
		pitchOffset=0
		# Merge adjacent strings
		index=0
		while index<len(speakList):
			item=speakList[index]
			if index>0:
				lastItem=speakList[index-1]
				if isinstance(item,str) and isinstance(lastItem,str):
					speakList[index-1]=" ".join([lastItem,item])
					del speakList[index]
					continue
			index+=1
		endPause=20
		for item in speakList:
			if isinstance(item,speech.PitchCommand):
				pitchOffset=item.offset
			elif isinstance(item,speech.IndexCommand):
				userIndex=item.index
			elif isinstance(item,str):
				textList=re_textPause.split(item)
				lastIndex=len(textList)-1
				for index,chunk in enumerate(textList):
					if not chunk: continue
					chunk=chunk.strip()
					if not chunk: continue
					clauseType=chunk[-1]
					if clauseType in ('.','!'):
						endPause=150
					elif clauseType=='?':
						endPause=150
					elif clauseType==',':
						endPause=120
					else:
						endPause=100
						clauseType=None
					endPause/=self._curRate
					textBuf=ctypes.create_unicode_buffer(chunk)
					textPtr=ctypes.c_void_p(ctypes.addressof(textBuf))
					chunks=[]
					while textPtr:
						phonemeBuf=_espeak.espeakDLL.espeak_TextToPhonemes(ctypes.byref(textPtr),_espeak.espeakCHARS_WCHAR,0x36100+0x82)
						if not phonemeBuf: continue
						chunks.append(ctypes.string_at(phonemeBuf))
					chunk=b"".join(chunks).decode('utf8') 
					chunk=chunk.replace('ə͡l','ʊ͡l')
					chunk=chunk.replace('a͡ɪ','ɑ͡ɪ')
					chunk=chunk.replace('e͡ɪ','e͡i')
					chunk=chunk.replace('ə͡ʊ','o͡u')
					chunk=chunk.strip()
					if not chunk: continue
					pitch=self._curPitch+pitchOffset
					basePitch=25+(21.25*(pitch/12.5))
					for args in ipa.generateFramesAndTiming(chunk,speed=self._curRate,basePitch=basePitch,inflection=self._curInflection,clauseType=clauseType):
						frame=args[0]
						if frame:
							applyVoiceToFrame(frame,self._curVoice)
							if self.exposeExtraParams:
								for x in self._extraParamNames:
									ratio=getattr(self,"speechPlayer_%s"%x)/50.0
									setattr(frame,x,getattr(frame,x)*ratio)
							frame.preFormantGain*=self._curVolume
						self.player.queueFrame(*args,userIndex=userIndex)
						userIndex=None
		self.player.queueFrame(None,endPause,max(10.0,10.0/self._curRate),userIndex=userIndex)
		self.audioThread.isSpeaking=True
		self.audioThread.synthEvent.set()

	def cancel(self):
		self.player.queueFrame(None,20,5,purgeQueue=True)
		self.audioThread.isSpeaking=False
		self.audioThread.synthEvent.set()
		self.audioThread.wavePlayer.stop()

	def pause(self,switch):
		self.audioThread.wavePlayer.pause(switch)

	def _get_rate(self):
		return int(math.log(self._curRate/0.25,2)*25.0)

	def _set_rate(self,val):
		self._curRate=0.25*(2**(val/25.0))

	def _get_pitch(self):
		return self._curPitch

	def _set_pitch(self,val):
		self._curPitch=val

	def _get_volume(self):
		return int(self._curVolume*75)

	def _set_volume(self,val):
		self._curVolume=val/75.0

	def _get_inflection(self):
		return int(self._curInflection/0.01)

	def _set_inflection(self,val):
		self._curInflection=val*0.01

	def _get_voice(self):
		return self._curVoice

	def _set_voice(self,voice):
		if voice not in self.availableVoices:
			voice='Adam'
		self._curVoice=voice
		if self.exposeExtraParams:
			for paramName in self._extraParamNames:
				setattr(self,"speechPlayer_%s"%paramName,50)

	def _getAvailableVoices(self):
		d=OrderedDict()
		for name in sorted(voices):
			d[name]=VoiceInfo(name,name)
		return d

	def terminate(self):
		self.audioThread.terminate()
		del self.player
		_espeak.terminate()
