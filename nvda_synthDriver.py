import re
import math
from collections import OrderedDict
import ctypes
import speechPlayer
import ipa
import speech
from synthDrivers import _espeak
from synthDriverHandler import SynthDriver, NumericSynthSetting, VoiceInfo

re_textPause=re.compile(ur"(?<=[.?!,:;])\s",re.DOTALL|re.UNICODE)

voices={
	'default':{},
		'eloquence':{
		'cf1_mul':1.01,
		'cf2_mul':1.02,
		'cf3_mul':0.96,
		'cf4':3700,
		'cf5':4100,
		'cf6':5000,
		'cb1_mul':1.4,
		'cb2_mul':1.2,
		'cb3_mul':1.1,
		'fricationAmplitude':0.7,
		'pf1_mul':1.01,
		'pf2_mul':1.02,
		'pf3_mul':0.96,
		'pf4':3700,
		'pf5':4100,
		'pf6':5000,
		'pb1_mul':1.4,
		'pb2_mul':1.2,
		'pb3_mul':1.1,
	},
	'whisper':{
		'aspirationAmplitude':1,
		'voiceAmplitude':0,
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
			self.supportedSettings=SynthDriver.supportedSettings+tuple(NumericSynthSetting("speechPlayer_%s"%x,"frame.%s"%x,normalStep=1,availableInSynthSettingsRing=False) for x in self._extraParamNames)
			for x in self._extraParamNames:
				setattr(self,"speechPlayer_%s"%x,50)
		self.player=speechPlayer.SpeechPlayer(16000)
		_espeak.initialize()
		_espeak.setVoiceByLanguage('en')
		self.pitch=50
		self.rate=50
		self.volume=75
		self.inflection=35



	@classmethod
	def check(cls):
		return True

	name="speechPlayer"
	description="Speech Player"

	supportedSettings=(SynthDriver.VoiceSetting(),SynthDriver.RateSetting(),SynthDriver.PitchSetting(),SynthDriver.VolumeSetting(),SynthDriver.InflectionSetting())

	_curPitch=118
	_curVoice='default'
	_curInflection=1.0
	_curVolume=1.0

	def speak(self,speakList):
		userIndex=-1
		for item in reversed(speakList):
			if isinstance(item,speech.IndexCommand):
				userIndex=item.index
				break
		textList=re_textPause.split(" ".join(x for x in speakList if isinstance(x,basestring)))
		lastIndex=len(textList)-1
		for index,chunk in enumerate(textList):
			if not chunk: continue
			chunk=chunk.strip()
			if chunk[-1]=='.':
				endPause=150
				endPitch=self._curPitch/(1+(0.5*self._curInflection))
			elif chunk[-1]=='?':
				endPause=130
				endPitch=self._curPitch*(1+(0.2*self._curInflection))
			else:
				endPause=100
				endPitch=self._curPitch/(1+(0.17*self._curInflection))
			endPause/=ipa.speed
			words=[]
			for word in chunk.split(' '):
				textBuf=ctypes.create_unicode_buffer(word)
				phonemeBuf=ctypes.create_string_buffer(1024)
				_espeak.espeakDLL.espeak_TextToPhonemes(textBuf,phonemeBuf,1024,_espeak.espeakCHARS_WCHAR,0b10001)
				word=phonemeBuf.value.decode('utf8')
				word=word.replace(u'a͡ɪ',u'ɑ͡ɪ')
				word=word.replace(u'ə͡ʊ',u'o͡ʊ')
				words.append(word)
			if not words: continue
			chunk=" ".join(words).strip()
			if not chunk: continue
			for args in ipa.generateFramesAndTiming(chunk,startPitch=self._curPitch,endPitch=endPitch,stressInflection=self._curInflection):
				frame=args[0]
				if frame:
					applyVoiceToFrame(frame,self._curVoice)
					if self.exposeExtraParams:
						for x in self._extraParamNames:
							ratio=getattr(self,"speechPlayer_%s"%x)/50.0
							setattr(frame,x,getattr(frame,x)*ratio)
					frame.preFormantGain*=self._curVolume
				self.player.queueFrame(*args,userIndex=userIndex)
			self.player.queueFrame(None,endPause,10/ipa.speed)

	def cancel(self):
		self.player.queueFrame(None,40,40,purgeQueue=True)

	def _get_rate(self):
		return int(math.log(ipa.speed/0.25,2)*25.0)

	def _set_rate(self,val):
		ipa.speed=0.25*(2**(val/25.0))

	def _get_pitch(self):
		return int(((self._curPitch-25)*12.5)/21.25)

	def _set_pitch(self,val):
		self._curPitch=25+(21.25*(val/12.5))

	def _get_volume(self):
		return int(self._curVolume*75)

	def _set_volume(self,val):
		self._curVolume=val/75.0

	def _get_inflection(self):
		return int(self._curInflection*50.0)

	def _set_inflection(self,val):
		self._curInflection=val/50.0

	def _get_lastIndex(self):
		return self.player.getLastIndex()
	def _get_voice(self):
		return self._curVoice

	def _set_voice(self,voice):
		if voice not in self.availableVoices:
			raise ValueError("unknown voice %s"%voice)
		self._curVoice=voice
		if self.exposeExtraParams:
			for paramName in self._extraParamNames:
				setattr(self,"speechPlayer_%s"%paramName,50)

	def _getAvailableVoices(self):
		d=OrderedDict()
		for name in voices:
			d[name]=VoiceInfo(name,name)
		return d

	def terminate(self):
		del self.player
		_espeak.terminate()
