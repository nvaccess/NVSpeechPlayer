import re
import math
from collections import OrderedDict
import ctypes
import speechPlayer
import ipa
import speech
from logHandler import log
from synthDrivers import _espeak
from synthDriverHandler import SynthDriver, NumericSynthSetting, VoiceInfo

re_textPause=re.compile(ur"(?<=[.?!,:;])\s",re.DOTALL|re.UNICODE)

voices={
	'Adam':{
		'cb1_mul':1.3,
		'pa6_mul':1.3,
		'fricationAmplitude':0.85,
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
		'fricationAmplitude':0.7,
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

	name="nvSpeechPlayer"
	description="nvSpeechPlayer"

	supportedSettings=(SynthDriver.VoiceSetting(),SynthDriver.RateSetting(),SynthDriver.PitchSetting(),SynthDriver.VolumeSetting(),SynthDriver.InflectionSetting())

	_curPitch=118
	_curVoice='Adam'
	_curInflection=0.5
	_curVolume=1.0
	_curRate=1.0

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
			phonemeBuf=_espeak.espeakDLL.espeak_TextToPhonemes(ctypes.byref(textPtr),_espeak.espeakCHARS_WCHAR,0b10001)
			if not phonemeBuf: continue
			chunk=ctypes.string_at(phonemeBuf)
			chunk=chunk.decode('utf8') 
			chunk=chunk.replace(u'ə͡l',u'ʊ͡l')
			chunk=chunk.replace(u'a͡ɪ',u'ɑ͡ɪ')
			chunk=chunk.replace(u'e͡ɪ',u'e͡i')
			chunk=chunk.replace(u'ə͡ʊ',u'o͡u')
			chunk=chunk.strip()
			if not chunk: continue
			log.info("IPA : %s"%chunk)
			textPtr=ctypes.c_void_p(ctypes.addressof(textBuf))
			phonemeBuf=_espeak.espeakDLL.espeak_TextToPhonemes(ctypes.byref(textPtr),_espeak.espeakCHARS_WCHAR,0b0001)
			if not phonemeBuf: continue
			newChunk=ctypes.string_at(phonemeBuf)
			newChunk=newChunk.decode('utf8') 
			log.info("eSpeak phonemes: %s"%newChunk)
			for args in ipa.generateFramesAndTiming(chunk,speed=self._curRate,basePitch=self._curPitch,inflection=self._curInflection,clauseType=clauseType):
				frame=args[0]
				if frame:
					applyVoiceToFrame(frame,self._curVoice)
					if self.exposeExtraParams:
						for x in self._extraParamNames:
							ratio=getattr(self,"speechPlayer_%s"%x)/50.0
							setattr(frame,x,getattr(frame,x)*ratio)
					frame.preFormantGain*=self._curVolume
				self.player.queueFrame(*args,userIndex=userIndex)
			self.player.queueFrame(None,endPause,max(10.0,10.0/self._curRate))

	def cancel(self):
		self.player.queueFrame(None,1,1,purgeQueue=True)

	def _get_rate(self):
		return int(math.log(self._curRate/0.25,2)*25.0)

	def _set_rate(self,val):
		self._curRate=0.25*(2**(val/25.0))

	def _get_pitch(self):
		return int(((self._curPitch-25)*12.5)/21.25)

	def _set_pitch(self,val):
		self._curPitch=25+(21.25*(val/12.5))

	def _get_volume(self):
		return int(self._curVolume*75)

	def _set_volume(self,val):
		self._curVolume=val/75.0

	def _get_inflection(self):
		return int(self._curInflection/0.01)

	def _set_inflection(self,val):
		self._curInflection=val*0.01

	def _get_lastIndex(self):
		return self.player.getLastIndex()
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
		del self.player
		_espeak.terminate()
