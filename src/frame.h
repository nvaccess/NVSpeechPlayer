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

#define SPEECHPLAYER_FRAME_NUMFORMANTS 3

typedef struct {
	double frequency; // in hz
	double bandwidth; // in hz 
	double amplitude; // from 0 to 1
} speechPlayer_formantParams_t;

typedef struct {
	double voiceAmplitude; // from 0 to 1
	double voicePitch; //in hz
	double breathyness; // from 0 to 1
	double vibratoOffset; // 1 = 1 semitone
	double vibratoSpeed; // in hz
	speechPlayer_formantParams_t formantParams[SPEECHPLAYER_FRAME_NUMFORMANTS];
} speechPlayer_frame_t;

class FrameManager {
	public:
	static FrameManager* create(); //factory function
	virtual void setNewFrame(speechPlayer_frame_t* frame, int fadeCount)=0;
	virtual const speechPlayer_frame_t* const getCurrentFrame()=0;
	virtual ~FrameManager()=0 {};
};

#endif
