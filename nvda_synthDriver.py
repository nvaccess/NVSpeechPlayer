import re
import math
import ctypes
import speechPlayer
import ipa
import synthDrivers.espeak
import synthDrivers._espeak

re_textPause=re.compile(ur"(?<=[.?!,:;])\s",re.DOTALL|re.UNICODE)

class SynthDriver(synthDrivers.espeak.SynthDriver):

	def __init__(self):
		self.player=speechPlayer.SpeechPlayer(16000)
		super(SynthDriver,self).__init__()

	name="speechPlayer"
	description="Speech Player"

	_curPitch=110

	def speak(self,speakList):
		textList=re_textPause.split(" ".join(x for x in speakList if isinstance(x,basestring)))
		lastIndex=len(textList)-1
		for index,chunk in enumerate(textList):
			if not chunk: continue
			chunk=chunk.strip()
			if chunk[-1]=='.':
				endPause=150
				endPitch=self._curPitch*0.66
			elif chunk[-1]=='?':
				endPause=130
				endPitch=self._curPitch*1.2
			else:
				endPause=100
				endPitch=self._curPitch*0.85
			words=[]
			for word in chunk.split(' '):
				textBuf=ctypes.create_unicode_buffer(word)
				phonemeBuf=ctypes.create_string_buffer(1024)
				synthDrivers._espeak.espeakDLL.espeak_TextToPhonemes(textBuf,phonemeBuf,1024,synthDrivers._espeak.espeakCHARS_WCHAR,0b10001)
				word=phonemeBuf.value.decode('utf8')
				words.append(word)
			if not words: continue
			chunk=" ".join(words).strip()
			if not chunk: continue
			for args in ipa.generateFramesAndTiming(chunk,startPitch=self._curPitch,endPitch=endPitch):
				self.player.queueFrame(*args)
			self.player.queueFrame(None,endPause,10)

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

