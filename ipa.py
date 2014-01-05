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
		setattr(frame,k,v)

speed=1

def generateFramesAndTiming(ipaText,startPitch=1,endPitch=1,stressInflection=1.0):
	frame=speechPlayer.Frame()
	frame.preFormantGain=2.0
	frame.vibratoPitchOffset=0.4
	frame.vibratoSpeed=4
	phonemeList=[]
	textLength=len(ipaText)
	lastIndex=textLength-1
	lastPhoneme=None
	# Collect phoneme info for each IPA character, assigning diacritics (lengthened, stress) to the last real phoneme
	stress=0
	tied=False
	newWord=True
	for index in xrange(textLength):
		char=ipaText[index]
		if char==' ':
			newWord=True
		elif char==u'ː':
			if lastPhoneme is not None: lastPhoneme['lengthened']=True
		elif char==u'ˈ':
			stress=1
		elif char==u'ˌ':
			stress=2
		elif char==u'͡':
			if lastPhoneme is not None:
				lastPhoneme['tiedTo']=True
				tied=True
		phoneme=data.get(char)
		if not phoneme: continue
		phoneme=phoneme.copy()
		phoneme['char']=char
		if newWord:
			newWord=False
			phoneme['wordStart']=True
		if tied:
			phoneme['tiedFrom']=True
			tied=False
		if stress and phoneme.get('isVowel'):
			phoneme['stress']=stress
			stress=0
		phonemeList.append(phoneme)
		lastPhoneme=phoneme
	if len(phonemeList)==0:
		return
	# Insert aspirations (quiet h) after any non-voiced stop (p,t,k etc) if they are followed directly a voiced phoneme
	aspirationIndexes=[]
	for index,phoneme in enumerate(phonemeList):
		nextPhoneme=phonemeList[index+1] if (index+1)<len(phonemeList) else None
		if phoneme.get('isStop') and not phoneme.get('isVoiced') and (not nextPhoneme or (not nextPhoneme.get('isStop') and nextPhoneme.get('isVoiced'))):
			aspirationIndexes.append(index+1)
	for index in reversed(aspirationIndexes):
		phoneme=data['h'].copy()
		phoneme['postStopAspiration']=True
		phonemeList.insert(index,phoneme)
	finalPhonemeIndex=len(phonemeList)-1
	# Correct all h phonemes (including inserted aspirations) so that their formants match the next phoneme, or the previous if there is no next
	for index in xrange(len(phonemeList)):
		prevPhoneme=phonemeList[index-1] if index>0 else None
		curPhoneme=phonemeList[index]
		nextPhoneme=phonemeList[index+1] if index<finalPhonemeIndex else None
		if curPhoneme.get('copyAdjacent'):
			newPhoneme=nextPhoneme.copy() if nextPhoneme else (prevPhoneme.copy() if prevPhoneme else {})
			newPhoneme.update(curPhoneme)
			curPhoneme=phonemeList[index]=newPhoneme
	for index,phoneme in enumerate(phonemeList):
		pitchRatio=float(index+1)/len(phonemeList)
		frame.voicePitch=startPitch+(endPitch-startPitch)*pitchRatio
		if phoneme.get('wordStart') and phoneme.get('isVowel') and phoneme.get('stress')==1:
			yield None,10/speed,10/speed
		frameDuration=60/speed
		fadeDuration=40/speed
		if phoneme.get('isVowel'):
			frameDuration*=1.5
		if phoneme.get('lengthened'):
			frameDuration*=1.125
		if phoneme.get('tiedTo'):
			frameDuration/=1.5
		elif phoneme.get('tiedFrom'):
			frameDuration/=2
		stress=phoneme.get('stress')
		if stress:
			frame.voicePitch*=(1+(0.3*stressInflection) if stress==1 else 1+(0.15*stressInflection)) 
			frameDuration*=(1.0625 if stress==1 else 1.03)
			frame.preFormantGain=2.2 if stress==1 else 2.1
		else:
			frame.preFormantGain=2.0
		if phoneme.get('isStop'):
			yield None,20/speed,20/speed
			frameDuration=min(15,15/speed)
			fadeDuration=0.001
		elif phoneme.get('postStopAspiration'):
			frameDuration=20/speed
			fadeDuration=5
		if lastPhoneme and lastPhoneme.get('isStop') and lastPhoneme.get('isVoiced') and not phoneme.get('isStop') and fadeDuration>40:
			fadeDuration=40
		applyPhonemeToFrame(frame,phoneme)
		yield frame,frameDuration,fadeDuration
		lastPhoneme=phoneme
