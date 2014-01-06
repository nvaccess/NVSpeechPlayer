import codecs
from collections import OrderedDict
from pyklatt_ipa import _IPA_MAPPING as oldIpaData

oldIpaData['t']['formant-gain (2-6)']=(0,0,0,0,90)
oldIpaData['d']['formant-gain (2-6)']=(0,0,0,0,70)

data=OrderedDict()
for k in sorted(oldIpaData.keys()):
	v=oldIpaData[k]
	data[k]=item=OrderedDict()
	item['isNasal']=v['nasal']
	item['isStop']=v['stop']
	item['isLiquid']=v['liquid']
	item['isVowel']=v['vowel']
	item['isVoiced']=v['voice']
	item['voiceAmplitude']=1.0 if v['voice'] else 0 
	item['aspirationAmplitude']=0.75 if not v['voice'] and v['voicing-linear-gain']>0 else 0.0 
	item['cf1'],item['cf2'],item['cf3'],item['cf4'],item['cf5'],item['cf6']=v['freq (1-6)']
	item['cfNP']=v['freq-nasal-pole']
	item['cfN0']=v['freq-nasal-zero']
	item['cb1'],item['cb2'],item['cb3'],item['cb4'],item['cb5'],item['cb6']=v['bwidth (1-6)']
	item['cbNP']=v['bwidth-nasal-pole']
	item['cbN0']=v['bwidth-nasal-zero']
	item['ca1']=item['ca2']=item['ca3']=item['ca4']=item['ca5']=item['ca6']=1.0
	item['caNP']=1.0 if v['nasal'] else 0
	item['pf1'],item['pf2'],item['pf3'],item['pf4'],item['pf5'],item['pf6']=v['freq (1-6)']
	item['pb1'],item['pb2'],item['pb3'],item['pb4'],item['pb5'],item['pb6']=v['bwidth (1-6)']
	item['pa1']=0
	item['pa2'],item['pa3'],item['pa4'],item['pa5'],item['pa6']=(x/60.0 for x in v['formant-gain (2-6)'])
	item['parallelBypass']=v['formant-bypass-gain']/80.0
	if v['formant-parallel-gain']==0:
		item['fricationAmplitude']=0
	else:
		item['fricationAmplitude']=0.5 if v['voicing-linear-gain']>0 else 1.0 

data['h']=dict(copyAdjacent=True,isStop=False,isVoiced=False,isVowel=False,voiceAmplitude=0,aspirationAmplitude=1,fricationAmplitude=0)
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
