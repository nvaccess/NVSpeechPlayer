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

#include "frame.h"
#include "speechWaveGenerator.h"
#include "player_winmm.h"
#include "speechPlayer.h"

typedef struct {
	FrameManager* frameManager;
	SpeechWaveGenerator* waveGenerator;
	Player* player;
} speechPlayer_handleInfo_t;

speechPlayer_handle_t speechPlayer_initialize(int sampleRate) {
	speechPlayer_handleInfo_t* playerHandleInfo=new speechPlayer_handleInfo_t;
	playerHandleInfo->frameManager=FrameManager::create();
	playerHandleInfo->waveGenerator=SpeechWaveGenerator::create(sampleRate);
	playerHandleInfo->waveGenerator->setFrameManager(playerHandleInfo->frameManager);
	playerHandleInfo->player=new Player_winmm(sampleRate);
	playerHandleInfo->player->setInputWaveGenerator(playerHandleInfo->waveGenerator);
	return (speechPlayer_handle_t)playerHandleInfo;
}

void speechPlayer_setNewFrame(speechPlayer_handle_t playerHandle, speechPlayer_frame_t* framePtr, int fadeCount) { 
	((speechPlayer_handleInfo_t*)playerHandle)->frameManager->setNewFrame(framePtr,fadeCount);
}

void speechPlayer_terminate(speechPlayer_handle_t playerHandle) {
	speechPlayer_handleInfo_t* playerHandleInfo=(speechPlayer_handleInfo_t*)playerHandle;
	delete playerHandleInfo->player;
	delete playerHandleInfo->waveGenerator;
	delete playerHandleInfo->frameManager;
	delete playerHandleInfo;
}
  