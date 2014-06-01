/*
This file is a part of the NV Speech Player project. 
URL: https://bitbucket.org/nvaccess/speechplayer
Copyright 2014 NV Access Limited.
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License version 2.0, as published by
the Free Software Foundation.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
This license can be found at:
http://www.gnu.org/licenses/old-licenses/gpl-2.0.html
*/

#include <cassert>
#include <iostream>
#include <windows.h>
#include "debug.h"
#include "player_winmm.h"

using namespace std;

Player_winmm::Player_winmm(int sampleRate): Player(sampleRate), winmmThreadKeepAlive(TRUE), winmmThreadHandle(NULL) {
	winmmThreadHandle=CreateThread(NULL,0,winmmThreadFunc,(LPVOID)this,0,NULL);
	if(!winmmThreadHandle) {
		DEBUG("Player_winmm::Player_winmm: could not create winmm thread");
		exit(1);
	}
}

Player_winmm::~Player_winmm() {
	winmmThreadKeepAlive=FALSE;
	WaitForSingleObject(winmmThreadHandle,INFINITE);
	CloseHandle(winmmThreadHandle);
	winmmThreadHandle=NULL;
}

DWORD WINAPI Player_winmm::winmmThreadFunc(LPVOID data) {
	assert(data);
	Player_winmm* thisPlayer=(Player_winmm*)data;
	int res;
	HANDLE _waveOutEvent=CreateEvent(NULL,FALSE,FALSE,NULL);
	HWAVEOUT waveOutHandle=0;
	WAVEFORMATEX waveFormat={0};
	waveFormat.wFormatTag=WAVE_FORMAT_PCM;
	waveFormat.nChannels=numChannels;
	waveFormat.nSamplesPerSec=thisPlayer->sampleRate;
	waveFormat.wBitsPerSample=bitsPerSample;
	waveFormat.nBlockAlign=bitsPerSample/8*numChannels;
	waveFormat.nAvgBytesPerSec=thisPlayer->sampleRate*waveFormat.nBlockAlign;
	res=waveOutOpen(&waveOutHandle,-1,&waveFormat,(DWORD_PTR)_waveOutEvent,0,CALLBACK_EVENT);
	if(res!=0) {
		DEBUG("waveOutOpen returned "<<res);
		exit(1);
	}
	block blocks[numBlocks]={0};
	for(int i=0;i<numBlocks;++i) {
		blocks[i].waveHeader.lpData=(LPSTR)blocks[i].samples;
		blocks[i].waveHeader.dwBufferLength=numSamplesPerBlock*sizeof(sample);
	}
	for(int curBlockNum=0;thisPlayer->winmmThreadKeepAlive;(++curBlockNum)%=numBlocks) {
		if(blocks[curBlockNum].waveHeader.dwFlags&WHDR_PREPARED) {
			while(!(blocks[curBlockNum].waveHeader.dwFlags&WHDR_DONE)) {
				res=WaitForSingleObject(_waveOutEvent,INFINITE);
				if(res!=0) {
					DEBUG("WaitForSingleObject returned "<<res);
					exit(1);
				}
			}
			res=waveOutUnprepareHeader(waveOutHandle,&(blocks[curBlockNum].waveHeader),sizeof(WAVEHDR));
			if(res!=0) {
				DEBUG("waveOutUnprepareHeader returned "<<res);
				exit(1);
			}
		}
		thisPlayer->fillInputBuffer(numSamplesPerBlock,blocks[curBlockNum].samples);
		res=waveOutPrepareHeader(waveOutHandle,&(blocks[curBlockNum].waveHeader),sizeof(WAVEHDR));
		if(res!=0) {
			DEBUG("waveOutPrepareHeader returned "<<res);
			exit(1);
		}
		res=waveOutWrite(waveOutHandle,&(blocks[curBlockNum].waveHeader),sizeof(WAVEHDR));
		if(res!=0) {
			DEBUG("waveOutWrite returned "<<res);
			exit(1);
		}
	}
	res=waveOutReset(waveOutHandle);
	if(res!=0) {
		DEBUG("waveOutReset returned "<<res);
		exit(1);
	}
	for(int i=0;i<numBlocks;++i) {
		if(blocks[i].waveHeader.dwFlags&WHDR_PREPARED) {
			res=waveOutUnprepareHeader(waveOutHandle,&(blocks[i].waveHeader),sizeof(WAVEHDR));
			if(res!=0) {
				DEBUG("waveOutUnprepareHeader returned "<<res);
				exit(1);
			}
		}
	}
	res=waveOutClose(waveOutHandle);
	if(res!=0) {
		DEBUG("waveOutClose returned "<<res);
		exit(1);
	}
	return 0;
}
