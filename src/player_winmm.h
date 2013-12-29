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

#ifndef AUDIOSCREEN_PLAYER_WINMM_H
#define AUDIOSCREEN_PLAYER_WINMM_H

#include <windows.h>
#include "sample.h"
#include "player.h"

class Player_winmm: public Player {
	private:
	HANDLE winmmThreadHandle;
	static DWORD WINAPI winmmThreadFunc(LPVOID data);
	bool winmmThreadKeepAlive;
	static const int numSamplesPerBlock=768;
	static const int numBlocks=4;
	typedef struct {
		WAVEHDR waveHeader;
		sample samples[numSamplesPerBlock];
	} block;

	public:

	Player_winmm(int sampleRate);
	virtual ~Player_winmm(); 

};

#endif
