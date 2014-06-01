# NV Speech Player
A Klatt-based speech synthesis engine written in c++
Author: NV Access Limited

## Overview
NV Speech Player is a free and open-source prototype speech synthesizer that can be used by NVDA. It generates speech using Klatt synthesis, making it somewhat similar to speech synthesizers such as Dectalk and Eloquence.

## Licence and copyright
NV Speech Player is Copyright (c) 2014 NV Speech Player contributors
NV Speech Player is covered by the GNU General Public License (Version 2). 
You are free to share or change this software in any way you like 
as long as it is accompanied by the license and you make all 
source code available to anyone who wants it. This applies to 
both original and modified copies of this software, plus any 
derivative works.
For further details, you can view the license online at: 
http://www.gnu.org/licenses/old-licenses/gpl-2.0.html

## Background
The 70s and 80s saw much research in speech synthesis. One of the most prominent synthesis models that appeared was a formant-frequency synthesis known as Klatt synthesis. Some well-known Klatt synthesizers are Dectalk and Eloquence. They are well suited for use by the blind as they are extremely responsive, their pronunciation is smooth and predictable, and they are small in memory footprint. However, research soon moved onto other forms of synthesis such as concatinative speech, as although this was slower, it was much closer to the human voice. This was an advantage for usage in mainstream applications such as GPS units or telephone systems, but not necessarily so much of an advantage to the blind, who tend to care more about responsiveness and predictability over prettiness.

Although synthesizers such as Dectalk and Eloquence continued to be maintained and available for nearly 20 years, now they are becoming harder to get, with multiple companies saying that these, and their variants, have been end-of-lifed and will not be updated anymore. 

Concatinative synthesis is now starting to show promise as a replacement as the responsiveness and smoothness is improving. However, most if not all of the acceptable quality synthesizers are commercial and are rather expensive.

Both Dectalk and Eloquence were closed-source commercial products themselves. However, there is a substantial amount of source code and research material on Klatt synthesis available to the community. NV Speech Player tries to take advantage of this by being a 
modern prototype of a Klatt synthesizer, in the hopes to either be a replacement for synthesizers like Dectalk or Eloquence, or at least restart research and conversation around this synthesis method.

The eSpeak synthesizer, itself a free and open-source product has proved well as a replacement to a certain number of people in the community, but many people who hear it are extremely quick to point out its "metallic" sound and cannot seem to continue to use it. Although the authors of NV Speech Player still prefer eSpeak as their synthesizer of choice, they would still hope to try and understand better this strange resistance to eSpeak which may have something to do with eSpeak's spectral frequency synthesis verses Klatt synthesis. It may also have to do with the fact that consonants are also gathered from recorded speech and can therefore be perceived as being injected into the speech stream.

## Implementation
The synthesis engine itself is written in C++ using modern idioms, but closely following the implementation of klsyn-88, found at http://linguistics.berkeley.edu/phonlab/resources/

eSpeak is used to parse text into phonemes represented in IPA, making use of existing eSpeak dictionary processing. eSpeak can be found at: http://espeak.sourceforge.net/

The Klatt formant data for each individual phoneme was collected mostly from a project called PyKlatt: http://code.google.com/p/pyklatt/ However it has been further tweaked based on testing and matching with eSpeak's own data.

The rules for phoneme lengths, gaps, speed and intonation have been coded by hand in Python, though eSpeak's own intonation data was tried to be copied as much as possible.
 
## Building NV Speech Player
You will need:
- Python 2.7: http://www.python.org
- SCons 2.3.0: http://www.scons.org/
- Visual Studio 2012 Desktop (Express or professional)
 
To build: run scons

After building, there will be a nvSpeechPlayer_xxx.nvda-addon file in the root directory, where xxx is the git revision or hardcoded version number.
Installing this add-on into NVDA will allow you to use the Speech Player synthesizer in NVDA. Note everything you need is in the add-on, no extra dlls or files need to be copied.
 
