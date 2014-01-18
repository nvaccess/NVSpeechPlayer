import codecs
from collections import OrderedDict
from pyklatt_ipa import _IPA_MAPPING as oldIpaData

oldIpaData['t']['formant-gain (2-6)']=(25,25,0,0,60)
oldIpaData['d']['formant-gain (2-6)']=(20,20,0,0,50)

data=OrderedDict()
for k in sorted(oldIpaData.keys()):
	v=oldIpaData[k]
	data[k]=item=OrderedDict()
	item['_isNasal']=v['nasal']
	item['_isStop']=v['stop']
	item['_isLiquid']=v['liquid']
	item['_isVowel']=v['vowel']
	item['_isVoiced']=v['voice']
	item['voiceAmplitude']=1.0 if v['voice'] else 0 
	item['aspirationAmplitude']=0.75 if not v['voice'] and v['voicing-linear-gain']>0 else 0.0 
	item['cf1'],item['cf2'],item['cf3'],item['cf4'],item['cf5'],item['cf6']=v['freq (1-6)']
	item['cfNP']=v['freq-nasal-pole']*0.8
	item['cfN0']=v['freq-nasal-zero']
	item['cb1'],item['cb2'],item['cb3'],item['cb4'],item['cb5'],item['cb6']=v['bwidth (1-6)']
	item['cb1']*=1.1
	item['cb2']*=0.75
	item['cb3']*=0.75
	item['cbNP']=v['bwidth-nasal-pole']
	item['cbN0']=v['bwidth-nasal-zero']
	item['caNP']=1.0 if v['nasal'] else 0
	item['pf1'],item['pf2'],item['pf3'],item['pf4'],item['pf5'],item['pf6']=v['freq (1-6)']
	item['pb1'],item['pb2'],item['pb3'],item['pb4'],item['pb5'],item['pb6']=v['bwidth (1-6)']
	item['pa1']=0
	item['pa2'],item['pa3'],item['pa4'],item['pa5'],item['pa6']=(x/60.0 for x in v['formant-gain (2-6)'])
	item['parallelBypass']=v['formant-bypass-gain']/60.0
	if v['formant-parallel-gain']==0:
		item['fricationAmplitude']=0
	else:
		item['fricationAmplitude']=0.5 if v['voicing-linear-gain']>0 else 1.0 

data['h']=dict(_copyAdjacent=True,_isStop=False,_isVoiced=False,_isVowel=False,voiceAmplitude=0,aspirationAmplitude=1,fricationAmplitude=0)
data[u'ɹ']['cf3']=1350

aliases={
	u'ɐ':u'ʌ',
	u'ɜ':u'ə',
	u'ɪ':'I',
	u'ɡ':'g',
}
for a,b in aliases.iteritems():
	data[a]=data[b]

def createMergedVowel(a,b,ratio):
	a=data[a]
	b=data[b]
	m=a.copy()
	for x in ('cf1','cf2','cf3','cf4','cf5','cf6','cfNP','cfN0','cb1','cb2','cb3','cb4','cb5','cb6','cbNP','cbN0'):
		m[x]=(a[x]*(1-ratio))+(b[x]*ratio)
	return m

data['a']=createMergedVowel(u'ɑ',u'æ',0.4)
data[u'ɒ']=createMergedVowel(u'ɑ',u'o',0.5)
data['s']['pf6']=5250

f=codecs.open('data.py','w','utf8')
f.write(u'{\n')
for k,v in data.iteritems():
	f.write(u'\tu\'%s\':{\n'%k)
	for k2,v2 in v.iteritems():
		f.write(u'\t\t\'%s\':'%k2)
		f.write(u'%s,\n'%v2)
	f.write(u'\t},\n')
f.write(u'}\n')
f.close()
