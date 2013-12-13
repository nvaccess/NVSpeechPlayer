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

#ifndef AUDIOSCREEN_PLAYER_H
#define AUDIOSCREEN_PLAYER_H

#include "sample.h"
#include "waveGenerator.h"

class Player {
	protected:
	const int sampleRate;
	WaveGenerator* curInputWaveGenerator;
	void fillInputBuffer(int bufSize, sample* buffer) { if(curInputWaveGenerator) curInputWaveGenerator->generate(bufSize,buffer); else memset(buffer,0,sizeof(sample)*bufSize); }
	static const int bitsPerSample=sizeof(sampleVal)*8;
	static const int numChannels=sizeof(sample)/sizeof(sampleVal);

	public:
	Player(int sampleRate): sampleRate(sampleRate), curInputWaveGenerator(NULL) {};
	virtual ~Player() {}
	void setInputWaveGenerator(WaveGenerator* generator) { curInputWaveGenerator=generator; }

};

#endif
