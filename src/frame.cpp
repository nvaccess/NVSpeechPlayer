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

#include "utils.h"
#include "frame.h"

class FrameManagerImpl: public FrameManager {
	private:
	LockableObject frameLock;
	bool newFrameEmpty;
	int frameFadeCounter;
	int frameFadeCount;
	speechPlayer_frame_t* oldFrame;
	speechPlayer_frame_t* curFrame;
	speechPlayer_frame_t* newFrame;

	void updateCurrentFrame() {
		if(frameFadeCount==-1) return;
		else if(frameFadeCounter>=frameFadeCount) {
			frameFadeCount=-1;
			return;
		}
		double curFadeRatio=(double)frameFadeCounter/frameFadeCount;
		++frameFadeCounter;
		curFrame->voiceAmplitude=calculateValueAtFadePosition(oldFrame->voiceAmplitude,newFrame->voiceAmplitude,curFadeRatio);
		curFrame->voicePitch=calculateValueAtFadePosition(oldFrame->voicePitch,newFrame->voicePitch,curFadeRatio); //curFadeRatio);
		curFrame->breathyness=calculateValueAtFadePosition(oldFrame->breathyness,newFrame->breathyness,curFadeRatio);
		curFrame->vibratoOffset=calculateValueAtFadePosition(oldFrame->vibratoOffset,newFrame->vibratoOffset,curFadeRatio);
		curFrame->vibratoSpeed=calculateValueAtFadePosition(oldFrame->vibratoSpeed,newFrame->vibratoSpeed,curFadeRatio);
		for(int i=0;i<SPEECHPLAYER_FRAME_NUMFORMANTS;++i) {
			curFrame->formantParams[i].frequency=calculateValueAtFadePosition(oldFrame->formantParams[i].frequency,newFrame->formantParams[i].frequency,curFadeRatio);
			curFrame->formantParams[i].bandwidth=calculateValueAtFadePosition(oldFrame->formantParams[i].bandwidth,newFrame->formantParams[i].bandwidth,1.0); //curFadeRatio);
			curFrame->formantParams[i].amplitude=calculateValueAtFadePosition(oldFrame->formantParams[i].amplitude,newFrame->formantParams[i].amplitude,curFadeRatio);
		}
	}

	public:

	FrameManagerImpl() {
		oldFrame=new speechPlayer_frame_t();
		curFrame=new speechPlayer_frame_t();
		newFrame=new speechPlayer_frame_t();
		newFrameEmpty=true;
	}

	void setNewFrame(speechPlayer_frame_t* frame, int fadeCount) {
		frameLock.acquire();
		if(frame) {
			memcpy(newFrame,frame,sizeof(speechPlayer_frame_t));
			newFrameEmpty=false;
		} else {
			memset(newFrame,0,sizeof(speechPlayer_frame_t));
			newFrameEmpty=true;
		}
		speechPlayer_frame_t* tempFrame=oldFrame;
		oldFrame=curFrame;
		curFrame=tempFrame;
		frameFadeCount=fadeCount;
		frameFadeCounter=0;
		frameLock.release();
	}

	const speechPlayer_frame_t* const getCurrentFrame() {
		frameLock.acquire();
		updateCurrentFrame();
		frameLock.release();
		return curFrame;
	}

	~FrameManagerImpl() {
		delete oldFrame;
		delete curFrame;
		delete newFrame;
	}

};

FrameManager* FrameManager::create() { return new FrameManagerImpl(); }
