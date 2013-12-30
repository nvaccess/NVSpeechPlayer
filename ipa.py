import codecs
import speechPlayer

data=eval(codecs.open('data.py','r','utf8').read(),None,None)

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

speed=1.1

def generateFramesAndTiming(ipaText,basePitch=1):
	frame=speechPlayer.Frame()
	frame.preFormantGain=2.0
	frame.voicePitch=basePitch
	phonemeList=[]
	textLength=len(ipaText)
	lastIndex=textLength-1
	for index in xrange(textLength):
		phoneme=data.get(ipaText[index])
		if not phoneme: continue
		if index<lastIndex and ipaText[index+1]==u'ː':
			phoneme['lengthened']=True
		phonemeList.append(phoneme)
	if len(phonemeList)==0:
		return
	aspirationIndexes=[]
	for index,phoneme in enumerate(phonemeList):
		nextPhoneme=phonemeList[index+1] if (index+1)<len(phonemeList) else {}
		if phoneme.get('isStop') and not phoneme.get('isVoiced') and not nextPhoneme.get('isStop') and nextPhoneme.get('isVoiced'):
			aspirationIndexes.append(index+1)
	for index in reversed(aspirationIndexes):
		phoneme=data['h'].copy()
		phoneme['postStopAspiration']=True
		phonemeList.insert(index,phoneme)
	finalPhonemeIndex=len(phonemeList)-1
	for index in xrange(len(phonemeList)):
		prevPhoneme=phonemeList[index-1] if index>0 else None
		curPhoneme=phonemeList[index]
		nextPhoneme=phonemeList[index+1] if index<finalPhonemeIndex else None
		if curPhoneme.get('copyAdjacent'):
			newPhoneme=nextPhoneme.copy() if nextPhoneme else (prevPhoneme.copy() if prevPhoneme else {})
			newPhoneme.update(curPhoneme)
			curPhoneme=phonemeList[index]=newPhoneme
	pitchDec=100.0/len(phonemeList)
	for phoneme in phonemeList:
		frame.voicePitch=basePitch
		frameDuration=80/speed
		fadeDuration=40/speed
		if phoneme.get('isVowel'):
			frameDuration*=1.25
		if phoneme.get('lengthened'):
			frameDuration*=1.5
		if phoneme.get('isStop'):
			yield None,40,40
			frameDuration=15
			fadeDuration=0.001
		elif phoneme.get('postStopAspiration'):
			frameDuration=40
			fadeDuration=20
		applyPhonemeToFrame(frame,phoneme)
		yield frame,frameDuration,fadeDuration
		basePitch-=pitchDec
	yield None,5/speed,5/speed
