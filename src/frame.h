/*
Copyright 2013 Michael Curran <mick@nvaccess.org>.
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License version 2.1, as published by
    the Free Software Foundation.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
This license can be found at:
http://www.gnu.org/licenses/old-licenses/lgpl-2.1.html
*/

#ifndef SPEECHPLAYER_FRAME_H
#define SPEECHPLAYER_FRAME_H

#include "lock.h"

typedef double speechPlayer_frameParam_t;

typedef struct {
	speechPlayer_frameParam_t gain; // Over all amplitude between -0 and 1
	// voicing and cascaide
	speechPlayer_frameParam_t voicePitch; // fundermental frequency of voice (phonation) in hz
	speechPlayer_frameParam_t vibratoPitchOffset; // pitch is offset up or down in fraction of a semitone
	speechPlayer_frameParam_t vibratoSpeed; // Speed of vibrato in hz
	speechPlayer_frameParam_t voiceAmplitude; // amplitude of voice (phonation) source between 0 and 1
	speechPlayer_frameParam_t voiceTurbulenceAmplitude; // amplitude of voice breathiness from 0 to 1 
	speechPlayer_frameParam_t glottalOpenQuotient; // fraction between 0 and 1 of a voice cycle that the glottis is open (allows voice turbulance, alters f1...)
	speechPlayer_frameParam_t dcf1, dcb1; // change in hz in frequency and bandwidth of cascaide formant 1 in voice cycle while glottis is open
	speechPlayer_frameParam_t aspirationAmplitude; // amplitude of aspiration (noise source of whispered vowels, nasals, h etc) from 0 to 1
	speechPlayer_frameParam_t cf1, cf2, cf3, cf4, cf5, cf6, cfN0, cfNP; // frequencies of standard cascaide formants, nasal (anti) 0 and nasal pole in hz
	speechPlayer_frameParam_t cb1, cb2, cb3, cb4, cb5, cb6, cbN0, cbNP; // bandwidths of standard cascaide formants, nasal (anti) 0 and nasal pole in hz
	speechPlayer_frameParam_t ca1, ca2, ca3, ca4, ca5, ca6, caN0, caNP; // amplitudes from 0 to 1  of standard cascaide formants, nasal (anti) 0 and nasal pole
	// fricatives and parallel
	speechPlayer_frameParam_t fricationAmplitude; // amplitude of frication noise from 0 to 1
	speechPlayer_frameParam_t pf1, pf2, pf3, pf4, pf5, pf6; // parallel formants in hz
	speechPlayer_frameParam_t pb1, pb2, pb3, pb4, pb5, pb6; // parallel formant bandwidths in hz
	speechPlayer_frameParam_t pa1, pa2, pa3, pa4, pa5, pa6; // amplitude of parallel formants between 0 and 1
} speechPlayer_frame_t;

const int speechPlayer_frame_numParams=sizeof(speechPlayer_frame_t)/sizeof(speechPlayer_frameParam_t);

class FrameManager {
	public:
	static FrameManager* create(); //factory function
	virtual void setNewFrame(speechPlayer_frame_t* frame, int fadeCount)=0;
	virtual const speechPlayer_frame_t* const getCurrentFrame()=0;
	virtual ~FrameManager()=0 {};
};

#endif
