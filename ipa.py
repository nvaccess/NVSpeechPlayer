import os
import itertools
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
			if lastPhoneme and lastPhoneme.get('_isStop') and not lastPhoneme.get('_isVoiced') and phoneme and phoneme.get('_isVoiced') and not phoneme.get('_isStop'):
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
				speed=baseSpeed/1.4 if syllableStress==1 else baseSpeed/1.18
			else:
				speed=baseSpeed
		phonemeDuration=60.0/speed
		phonemeFadeDuration=50.0/speed
		if lastPhoneme is None or not lastPhoneme.get('_isVowel') or not phoneme.get('_isVoiced') or phoneme.get('_isNasal'):
			phonemeFadeDuration=min(25.0/speed,50.0)
		if phoneme.get('_isVowel'):
			phonemeDuration*=1.5
		if phoneme.get('_lengthened'):
			phonemeDuration*=1.05
		if phoneme.get('_tiedTo'):
			phonemeDuration*=0.7
		elif phoneme.get('_tiedFrom'):
			phonemeDuration*=0.3
		if phoneme.get('_preStopGap'):
			phonemeDuration=40.0/speed
			phonemeFadeDuration=10.0/speed
		if phoneme.get('_isStop'):
			phonemeDuration=min(10.0,10.0/speed)
			phonemeFadeDuration=0.001
		elif phoneme.get('_postStopAspiration'):
			phonemeDuration=40.0/speed
			phonemeFadeDuration=5
		if lastPhoneme and lastPhoneme.get('_isStop') and lastPhoneme.get('_isVoiced') and not phoneme.get('_isStop') and phonemeFadeDuration>40:
			phonemeFadeDuration=40
		if (not lastPhoneme or not lastPhoneme.get('_isVoiced')) and phoneme.get('_isVoiced'):
			phonemeFadeDuration=1
		phoneme['_duration']=phonemeDuration
		phoneme['_fadeDuration']=phonemeFadeDuration
		lastPhoneme=phoneme

def applyPitchPath(phonemeList,startIndex,endIndex,basePitch,inflection,startPitchPercent,endPitchPercent):
	startPitch=basePitch*(2**(((startPitchPercent-50)/50.0)*inflection))
	endPitch=basePitch*(2**(((endPitchPercent-50)/50.0)*inflection))
	voicedDuration=0
	for index in xrange(startIndex,endIndex):
		phoneme=phonemeList[index]
		if phoneme.get('_syllableStart'):
			syllableStress=phoneme.get('_stress')
		if phoneme.get('_isVoiced'):
			voicedDuration+=phoneme['_duration']
	curDuration=0
	pitchDelta=endPitch-startPitch
	curPitch=startPitch
	syllableStress=False
	for index in xrange(startIndex,endIndex):
		phoneme=phonemeList[index]
		if phoneme.get('_syllableStart'):
			syllableStress=phoneme.get('_stress')==1
		phoneme['voicePitch']=curPitch
		if phoneme.get('_isVoiced'):
			curDuration+=phoneme['_duration']
			pitchRatio=curDuration/float(voicedDuration)
			curPitch=startPitch+(pitchDelta*pitchRatio)
		phoneme['endVoicePitch']=curPitch

intonationParamTable={
	'.':{
		'preHeadStart':46,
		'preHeadEnd':57,
		'headExtendFrom':4,
		'headStart':80,
		'headEnd':50,
		'headSteps':[100,75,50,25,0,63,38,13,0],
		'headStressEndDelta':-16,
		'headUnstressedRunStartDelta':-8,
		'headUnstressedRunEndDelta':-5,
		'nucleus0Start':64,
		'nucleus0End':8,
		'nucleusStart':70,
		'nucleusEnd':18,
		'tailStart':24,
		'tailEnd':8,
	},
	',':{
		'preHeadStart':46,
		'preHeadEnd':57,
		'headExtendFrom':4,
		'headStart':80,
		'headEnd':60,
		'headSteps':[100,75,50,25,0,63,38,13,0],
		'headStressEndDelta':-16,
		'headUnstressedRunStartDelta':-8,
		'headUnstressedRunEndDelta':-5,
		'nucleus0Start':34,
		'nucleus0End':52,
		'nucleusStart':78,
		'nucleusEnd':34,
		'tailStart':34,
		'tailEnd':52,
	},
	'?':{
		'preHeadStart':45,
		'preHeadEnd':56,
		'headExtendFrom':3,
		'headStart':75,
		'headEnd':43,
		'headSteps':[100,75,50,20,60,35,11,0],
		'headStressEndDelta':-16,
		'headUnstressedRunStartDelta':-7,
		'headUnstressedRunEndDelta':0,
		'nucleus0Start':34,
		'nucleus0End':68,
		'nucleusStart':86,
		'nucleusEnd':21,
		'tailStart':34,
		'tailEnd':68,
	},
	'!':{
		'preHeadStart':46,
		'preHeadEnd':57,
		'headExtendFrom':3,
		'headStart':90,
		'headEnd':50,
		'headSteps':[100,75,50,16,82,50,32,16],
		'headStressEndDelta':-16,
		'headUnstressedRunStartDelta':-9,
		'headUnstressedRunEndDelta':0,
		'nucleus0Start':92,
		'nucleus0End':4,
		'nucleusStart':92,
		'nucleusEnd':80,
		'tailStart':76,
		'tailEnd':4,
	}
}

def calculatePhonemePitches(phonemeList,speed,basePitch,inflection,clauseType):
	intonationParams=intonationParamTable[clauseType or '.']
	preHeadStart=0
	preHeadEnd=len(phonemeList)
	for index,phoneme in enumerate(phonemeList):
		if phoneme.get('_syllableStart'):
			syllableStress=phoneme.get('_stress')==1
			if syllableStress:
				preHeadEnd=index
				break
	if (preHeadEnd-preHeadStart)>0:
		applyPitchPath(phonemeList,preHeadStart,preHeadEnd,basePitch,inflection,intonationParams['preHeadStart'],intonationParams['preHeadEnd'])
	nucleusStart=nucleusEnd=tailStart=tailEnd=len(phonemeList)
	for index in xrange(nucleusEnd-1,preHeadEnd-1,-1):
		phoneme=phonemeList[index]
		if phoneme.get('_syllableStart'):
			syllableStress=phoneme.get('_stress')==1
			if syllableStress :
				nucleusStart=index
				break
			else:
				nucleusEnd=tailStart=index
	hasTail=(tailEnd-tailStart)>0
	if hasTail:
		applyPitchPath(phonemeList,tailStart,tailEnd,basePitch,inflection,intonationParams['tailStart'],intonationParams['tailEnd'])
	if (nucleusEnd-nucleusStart)>0:
		if hasTail:
			applyPitchPath(phonemeList,nucleusStart,nucleusEnd,basePitch,inflection,intonationParams['nucleusStart'],intonationParams['nucleusEnd'])
		else:
			applyPitchPath(phonemeList,nucleusStart,nucleusEnd,basePitch,inflection,intonationParams['nucleus0Start'],intonationParams['nucleus0End'])
	if preHeadEnd<nucleusStart:
		headStartPitch=intonationParams['headStart']
		headEndPitch=intonationParams['headEnd']
		lastHeadStressStart=None
		lastHeadUnstressedRunStart=None
		stressEndPitch=None
		steps=intonationParams['headSteps']
		extendFrom=intonationParams['headExtendFrom']
		stressStartPercentageGen=itertools.chain(steps,itertools.cycle(steps[extendFrom:]))
		for index in xrange(preHeadEnd,nucleusStart+1):
			phoneme=phonemeList[index]
			syllableStress=phoneme.get('_stress')==1
			if phoneme.get('_syllableStart'):
				if lastHeadStressStart is not None:
					stressStartPitch=headEndPitch+(((headStartPitch-headEndPitch)/100.0)*stressStartPercentageGen.next())
					stressEndPitch=stressStartPitch+intonationParams['headStressEndDelta']
					applyPitchPath(phonemeList,lastHeadStressStart,index,basePitch,inflection,stressStartPitch,stressEndPitch)
					lastHeadStressStart=None
				if syllableStress :
					if lastHeadUnstressedRunStart is not None:
						unstressedRunStartPitch=stressEndPitch+intonationParams['headUnstressedRunStartDelta']
						unstressedRunEndPitch=stressEndPitch+intonationParams['headUnstressedRunEndDelta']
						applyPitchPath(phonemeList,lastHeadUnstressedRunStart,index,basePitch,inflection,unstressedRunStartPitch,unstressedRunEndPitch)
						lastHeadUnstressedRunStart=None
					lastHeadStressStart=index
				elif lastHeadUnstressedRunStart is None: 
					lastHeadUnstressedRunStart=index

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
