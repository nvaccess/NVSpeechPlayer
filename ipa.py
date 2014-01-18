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
	# Collect phoneme info for each IPA character, assigning diacritics (lengthened, stress) to the last real phoneme
	tied=False
	newWord=True
	lastPhoneme=None
	syllableStartPhoneme=None
	stress=0
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
			if lastPhoneme and not lastPhoneme.get('_isVowel') and phoneme and phoneme.get('_isVowel'):
				lastPhoneme['_syllableStart']=True
				syllableStartPhoneme=lastPhoneme
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
				phoneme['_syllableStart']=True
				syllableStartPhoneme=phoneme
			if tied:
				phoneme['_tiedFrom']=True
				tied=False
			if stress:
				syllableStartPhoneme['_stress']=stress
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

def calculatePhonemeTimes(phonemeList,baseSpeed):
	lastPhoneme=None
	syllableStress=0
	speed=baseSpeed
	for phoneme in phonemeList:
		if phoneme.get('_syllableStart'):
			syllableStress=phoneme.get('_stress')
			if syllableStress:
				speed=baseSpeed/1.3 if syllableStress==1 else baseSpeed/1.15
			else:
				speed=baseSpeed
		phonemeDuration=60.0/speed
		phonemeFadeDuration=50.0/speed
		if lastPhoneme is None or not lastPhoneme.get('_isVoiced') or lastPhoneme.get('_isNasal') or lastPhoneme.get('_isStop') or not phoneme.get('_isVoiced') or phoneme.get('_isNasal'):
			phonemeFadeDuration=min(25.0/speed,50.0)
		if phoneme.get('_preWordGap'):
			phonemeDuration=10.0/speed
			phonemeFadeDuration=10.0/speed
		if phoneme.get('_isVowel'):
			phonemeDuration*=1.85
		if phoneme.get('_lengthened'):
			phonemeDuration*=1.125
		if phoneme.get('_tiedTo'):
			phonemeDuration/=1.5
		elif phoneme.get('_tiedFrom'):
			phonemeDuration/=2
		if phoneme.get('_preStopGap'):
			phonemeDuration=25.0/speed
			phonemeFadeDuration=10.0/speed
		if phoneme.get('_isStop'):
			phonemeDuration=min(15.0,15.0/speed)
			phonemeFadeDuration=0.001
		elif phoneme.get('_postStopAspiration'):
			phonemeDuration=25.0/speed
			phonemeFadeDuration=5
		if lastPhoneme and lastPhoneme.get('_isStop') and lastPhoneme.get('_isVoiced') and not phoneme.get('_isStop') and phonemeFadeDuration>40:
			phonemeFadeDuration=40
		phoneme['_duration']=phonemeDuration
		phoneme['_fadeDuration']=phonemeFadeDuration
		lastPhoneme=phoneme

def calculatePhonemePitches(phonemeList,speed,basePitch,inflection,clauseType):
	totalVoicedDuration=0
	finalInflectionStartTime=0
	needsSetFinalInflectionStartTime=False
	finalVoicedIndex=0
	lastPhoneme=None
	for index,phoneme in enumerate(phonemeList):
		if phoneme.get('_wordStart'):
			needsSetFinalInflectionStartTime=True
		if phoneme.get('_isVoiced'):
			finalVoicedIndex=index
			if needsSetFinalInflectionStartTime:
				finalInflectionStartTime=totalVoicedDuration
				needsSetFinalInflectionStartTime=False
		if phoneme.get('_isVoiced'):
			totalVoicedDuration+=phoneme['_duration']
		elif lastPhoneme and lastPhoneme.get('_isVoiced'):
			totalVoicedDuration+=lastPhoneme['_fadeDuration']
		lastPhoneme=phoneme
	durationCounter=0
	curBasePitch=basePitch
	lastEndVoicePitch=basePitch
	stressInflection=inflection/1.5
	lastPhoneme=None
	syllableStress=False
	firstStress=True
	for index,phoneme in enumerate(phonemeList):
		if phoneme.get('_syllableStart'):
			syllableStress=phoneme.get('_stress')==1
		voicePitch=lastEndVoicePitch
		inFinalInflection=durationCounter>=finalInflectionStartTime
		if phoneme.get('_isVoiced'):
			durationCounter+=phoneme['_duration']
		elif lastPhoneme and lastPhoneme.get('_isVoiced'):
			durationCounter+=lastPhoneme['_fadeDuration']
		oldBasePitch=curBasePitch
		if not inFinalInflection:
			curBasePitch=basePitch/(1+(inflection/25000.0)*durationCounter*speed)
		else:
			ratio=float(durationCounter-finalInflectionStartTime)/float(totalVoicedDuration-finalInflectionStartTime)
			if clauseType=='.':
				ratio/=1.5
			elif clauseType=='?':
				ratio=0.5-(ratio/1.2)
			elif clauseType==',':
				ratio/=8
			else:
				ratio=ratio/1.75
			curBasePitch=basePitch/(1+(inflection*ratio*1.5))
		endVoicePitch=curBasePitch
		if syllableStress and phoneme.get('_isVowel'):
			if firstStress:
				voicePitch=oldBasePitch*(1+stressInflection/3)
				endVoicePitch=curBasePitch*(1+stressInflection)
				firstStress=False
			elif index<finalVoicedIndex:
				voicePitch=oldBasePitch*(1+stressInflection) 
				endVoicePitch=oldBasePitch*(1+stressInflection/3)
			else:
				voicePitch=basePitch*(1+stressInflection) 
			stressInflection*=0.9
			stressInflection=max(stressInflection,inflection/2)
			syllableStress=False
		if lastPhoneme:
			lastPhoneme['endVoicePitch']=voicePitch
		phoneme['voicePitch']=voicePitch
		lastEndVoicePitch=phoneme['endVoicePitch']=endVoicePitch
		lastPhoneme=phoneme

def generateFramesAndTiming(ipaText,speed=1,basePitch=100,inflection=0.5,clauseType=None):
	phonemeList=IPAToPhonemes(ipaText)
	if len(phonemeList)==0:
		return
	correctHPhonemes(phonemeList)
	calculatePhonemeTimes(phonemeList,speed)
	calculatePhonemePitches(phonemeList,speed,basePitch,inflection,clauseType)
	for phoneme in phonemeList:
		frameDuration=phoneme.pop('_duration')
		fadeDuration=phoneme.pop('_fadeDuration')
		if phoneme.get('_silence'):
			yield None,frameDuration,fadeDuration
		else:
			frame=speechPlayer.Frame()
			frame.preFormantGain=2.0
			applyPhonemeToFrame(frame,phoneme)
			yield frame,frameDuration,fadeDuration
