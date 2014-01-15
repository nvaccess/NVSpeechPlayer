A Klatt-like speech synthesis engine written in c++

Build Dependencies:
 * Python 2.7: http://www.python.org
 * SCons 2.3.0: http://www.scons.org/
  * Microsoft Windows SDK 7.0 or Visual Studio 2012
  
To build: run scons

NVDA add-on:
After building, there will be a speechPlayer_xxx.nvda-addon file in the root directory, where xxx is the git revision or hardcoded version number.
Installing this add-on into NVDA will allow you to use the Speech Player synthesizer in NVDA. Note everything you need is in the add-on, no extra dlls or files need to be copied.
 
 Python Examples:
 Included are a few example Python scripts which show various ways to use speechPlayer from Python.
 
 example: test_playVowelChart.pySpeaks all vowels known to speechPlayer. 
to run:
python test_playvowelChart.py

Example: test_speakIpa.py speaks a text file containing IPA symbols
To run:
python test_speakIpa.py <fileName>
Where <fileName> is the path to a file containing IPA symbols.
sampleIpa.txt is an included file with a few sentences in IPA.

Example: test_midiSing.py
Allows you to make speechPlayer sing its available voiced phonemes. 
to run:
python test_midiSing.py <midiDeviceNumber> <defaultvowel>
E.g. python test_midiSing.py 0 i
Playing notes will cause it to sing at the appropriate pitch.
Moving the mod wheel allows you to select a phoneme
Bending the pitch wheel up increases vibrato

Credits:
This project is based on several other projects:
 * klsyn-88 (reference Klatt implementation): http://linguistics.berkeley.edu/phonlab/resources/ 
 * PyKlatt (IPA formant values): http://code.google.com/p/pyklatt/

