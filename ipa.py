import os
import codecs
import speechPlayer

dataPath=os.path.join(os.path.dirname(__file__),'data.py')

data=eval(codecs.open(dataPath,'r','utf8').read(),None,None)

def iterPhonemes(**kwargs):
	for k,v in data.iteritems():
		if all(v[x]==y for x,y in kwargs.iteritems()):
			yield k

def setFrame(frame,phoneme):
	values=data[phoneme]
	for k,v in values.iteritems():
		setattr(frame,k,v)

def applyPhonemeToFrame(frame,phoneme):
	for k,v in phoneme.iteritems():
		if not k.startswith('_'):
			setattr(frame,k,v)

def IPAToPhonemes(ipaText):
	phonemeList=[]
	textLength=len(ipaText)
	lastPhoneme=None
	# Collect phoneme info for each IPA character, assigning diacritics (lengthened, stress) to the last real phoneme
	stress=0
	tied=False
	newWord=True
	for index in xrange(textLength+1):
		char=ipaText[index] if index<textLength else None
		if char==' ':
			newWord=True
		elif char==u'ː':
			if lastPhoneme is not None: lastPhoneme['_lengthened']=True
		elif char==u'ˈ':
			stress=1
		elif char==u'ˌ':
			stress=2
		elif char==u'͡':
			if lastPhoneme is not None:
				lastPhoneme['_tiedTo']=True
				tied=True
		else:
			phoneme=data.get(char) if index<textLength else None
			if phoneme:
				phoneme=phoneme.copy()
			if lastPhoneme and lastPhoneme.get('_isStop') and not lastPhoneme.get('_isVoiced') and (not phoneme or phoneme.get('_isVoiced')):
				psa=data['h'].copy()
				psa['_postStopAspiration']=True
				psa['_char']=None
				phonemeList.append(psa)
				lastPhoneme=psa
			if not phoneme: continue
			phoneme['_char']=char
			if newWord:
				newWord=False
				phoneme['_wordStart']=True
			if tied:
				phoneme['_tiedFrom']=True
				tied=False
			if stress and phoneme.get('_isVowel'):
				phoneme['_stress']=stress
				stress=0
			if phoneme.get('_wordStart') and phoneme.get('_isVowel') and phoneme.get('_stress')==1:
				gap=dict(_silence=True,_preWordGap=True)
				phonemeList.append(gap)
			elif phoneme.get('_isStop'):
				gap=dict(_silence=True,_preStopGap=True)
				phonemeList.append(gap)
			phonemeList.append(phoneme)
			lastPhoneme=phoneme
	return phonemeList

def correctHPhonemes(phonemeList):
	finalPhonemeIndex=len(phonemeList)-1
	# Correct all h phonemes (including inserted aspirations) so that their formants match the next phoneme, or the previous if there is no next
	for index in xrange(len(phonemeList)):
		prevPhoneme=phonemeList[index-1] if index>0 else None
		curPhoneme=phonemeList[index]
		nextPhoneme=phonemeList[index+1] if index<finalPhonemeIndex else None
		if curPhoneme.get('_copyAdjacent'):
			adjacent=nextPhoneme if nextPhoneme and not nextPhoneme.get('_silence') else prevPhoneme 
			if adjacent:
				for k,v in adjacent.iteritems():
					if not k.startswith('_') and k not in curPhoneme:
						curPhoneme[k]=v

def calculatePhonemeTimes(phonemeList,speed):
	totalDuration=0
	lastPhoneme=None
	for phoneme in phonemeList:
		phonemeDuration=60.0/speed
		phonemeFadeDuration=40.0/speed
		if phoneme.get('_preWordGap'):
			phonemeDuration=10.0/speed
			phonemeFadeDuration=10.0/speed
		if phoneme.get('_isVowel'):
			phonemeDuration*=1.5
		if phoneme.get('_lengthened'):
			phonemeDuration*=1.125
		if phoneme.get('_tiedTo'):
			phonemeDuration/=1.5
		elif phoneme.get('_tiedFrom'):
			phonemeDuration/=2
		stress=phoneme.get('_stress')
		if stress:
			phonemeDuration*=(1.0625 if stress==1 else 1.03)
		if phoneme.get('_preStopGap'):
			phonemeDuration=20.0/speed
			phonemeFadeDuration=20.0/speed
		if phoneme.get('_isStop'):
			phonemeDuration=min(15.0,15.0/speed)
			phonemeFadeDuration=0.001
		elif phoneme.get('_postStopAspiration'):
			phonemeDuration=20.0/speed
			phonemeDuration=5
		if lastPhoneme and lastPhoneme.get('_isStop') and lastPhoneme.get('_isVoiced') and not phoneme.get('_isStop') and phonemeFadeDuration>40:
			phonemeFadeDuration=40
		phoneme['_duration']=phonemeDuration
		phoneme['_fadeDuration']=phonemeFadeDuration
		totalDuration+=phonemeDuration
		lastPhoneme=phoneme
	return totalDuration

def calculatePhonemePitches(phonemeList,startPitch,endPitch,stressInflection,totalDuration):
	durationCounter=0
	lastEndVoicePitch=startPitch
	for phoneme in phonemeList:
		voicePitch=lastEndVoicePitch
		durationCounter+=phoneme['_duration']
		pitchRatio=float(durationCounter)/totalDuration
		endVoicePitch=startPitch+(endPitch-startPitch)*pitchRatio
		stress=phoneme.get('_stress')
		if stress:
			stressPitchMul=(1+(0.15*stressInflection) if stress==1 else 1+(0.075*stressInflection)) 
			voicePitch*=stressPitchMul
			endVoicePitch*=stressPitchMul
		phoneme['voicePitch']=voicePitch
		lastEndVoicePitch=phoneme['endVoicePitch']=endVoicePitch

speed=1

def generateFramesAndTiming(ipaText,startPitch=1,endPitch=1,stressInflection=1.0):
	phonemeList=IPAToPhonemes(ipaText)
	if len(phonemeList)==0:
		return
	correctHPhonemes(phonemeList)
	totalDuration=calculatePhonemeTimes(phonemeList,speed)
	calculatePhonemePitches(phonemeList,startPitch,endPitch,stressInflection,totalDuration)
	for phoneme in phonemeList:
		frameDuration=phoneme.pop('_duration')
		fadeDuration=phoneme.pop('_fadeDuration')
		if phoneme.get('_silence'):
			yield None,frameDuration,fadeDuration
		else:
			frame=speechPlayer.Frame()
			frame.preFormantGain=2.0
			frame.vibratoPitchOffset=0.4
			frame.vibratoSpeed=4
			applyPhonemeToFrame(frame,phoneme)
			yield frame,frameDuration,fadeDuration
