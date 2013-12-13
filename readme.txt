A Klatt-like speech synthesis engine

Build Dependencies:
 * SCons 2.3.0: http://www.scons.org/
  * Microsoft Windows SDK 7.0

To build: run scons release=1

Example dependencies:
   * Python 2.7: http://www.python.org
   * the vowelcharts directory (from espeakEdit): http://espeak.sourceforge.net/

example: test_playVowelChart.py
Speaks all vowels found in the given vowel chart.
to run:
python test_playvowelChart.py <chart>
Where <chart> is the name of one of the charts found in the vowelcharts directory e.g. en

Example: test_midiSing.py
Allows you to control speech from a midi keyboard.
to run:
python test_midiSing.py <midiDeviceNumber> <vowelchart> <defaultvowel>
E.g. python test_midiSing.py 0 en aa
Playing notes will cause it to sing at the appropriate pitch.
Moving the mod wheel allows you to select a vowel from the loaded vowel chart.
Bending the pitch wheel up increases vibrato
Bending the pitch wheel down increases breathyness; All the way down results in whispering.
