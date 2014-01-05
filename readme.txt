A Klatt-like speech synthesis engine

Build Dependencies:
 * Python 2.7: http://www.python.org
 * SCons 2.3.0: http://www.scons.org/
  * Microsoft Windows SDK 7.0 7.1 or Visual Studio 2012
  
To build: run scons

NVDA add-on:
After building, there will be a speechPlayer_xxx.nvda-addon file in the root directory, where xxx is the git revision or hardcoded version number.
Installing this add-on into NVDA will allow you to use the Speech Player synthesizer in NVDA. Note everything you need is in the add-on, no extra dlls or files need to be copied.
 
 Python Examples:
 Included are a few example Python scripts which show various ways to use speechPlayer from Python.
 
 example: test_playVowelChart.pySpeaks all vowels known to speechPlayer. 
to run:
python test_playvowelChart.py

--- broken examples ---
Example: test_midiSing.py
Allows you to control speech from a midi keyboard.
to run:
python test_midiSing.py <midiDeviceNumber> <defaultvowel>
E.g. python test_midiSing.py 0 e
Playing notes will cause it to sing at the appropriate pitch.
Moving the mod wheel allows you to select a vowel
Bending the pitch wheel up increases vibrato
Bending the pitch wheel down increases breathyness; All the way down results in whispering.
