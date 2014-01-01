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

#include <queue>
#include "utils.h"
#include "frame.h"

using namespace std;

struct frameRequest_t {
	int minNumSamples;
	int numFadeSamples;
	bool NULLFrame;
	speechPlayer_frame_t frame;
	double voicePitchInc; 
	int userIndex;
};

class FrameManagerImpl: public FrameManager {
	private:
	LockableObject frameLock;
	queue<frameRequest_t*> frameRequestQueue;
	frameRequest_t* oldFrameRequest;
	frameRequest_t* newFrameRequest;
	speechPlayer_frame_t curFrame;
	int sampleCounter;
	bool canRunQueue;
	int lastUserIndex;

	void updateCurrentFrame() {
		if(!canRunQueue) return;
		sampleCounter++;
		if(newFrameRequest) {
			if(sampleCounter>(newFrameRequest->numFadeSamples)) {
				delete oldFrameRequest;
				oldFrameRequest=newFrameRequest;
				newFrameRequest=NULL;
			} else {
				double curFadeRatio=(double)sampleCounter/(newFrameRequest->numFadeSamples);
				for(int i=0;i<speechPlayer_frame_numParams;++i) {
					((speechPlayer_frameParam_t*)&curFrame)[i]=calculateValueAtFadePosition(((speechPlayer_frameParam_t*)&(oldFrameRequest->frame))[i],((speechPlayer_frameParam_t*)&(newFrameRequest->frame))[i],curFadeRatio);
				}
			}
		} else if(sampleCounter>(oldFrameRequest->minNumSamples)) {
			if(!frameRequestQueue.empty()) {
				newFrameRequest=frameRequestQueue.front();
				frameRequestQueue.pop();
				if(newFrameRequest->NULLFrame) {
					if(false) { //oldFrameRequest->NULLFrame) {
						delete newFrameRequest;
						newFrameRequest=NULL;
					} else {
						double finalVoicePitch=newFrameRequest->frame.voicePitch;
						memcpy(&(newFrameRequest->frame),&(oldFrameRequest->frame),sizeof(speechPlayer_frame_t));
						newFrameRequest->frame.preFormantGain=0;
						newFrameRequest->frame.voicePitch=finalVoicePitch;
					}
				} else if(oldFrameRequest->NULLFrame) {
					memcpy(&(oldFrameRequest->frame),&(newFrameRequest->frame),sizeof(speechPlayer_frame_t));
					oldFrameRequest->frame.preFormantGain=0;
				}
				if(newFrameRequest) {
					if(newFrameRequest->userIndex!=-1) lastUserIndex=newFrameRequest->userIndex;
					oldFrameRequest->frame.voicePitch=curFrame.voicePitch;
					sampleCounter=0;
				}
			} else {
				canRunQueue=false;
			}
		} else {
			curFrame.voicePitch+=oldFrameRequest->voicePitchInc;
		}
	}


	public:

	FrameManagerImpl(): curFrame(), newFrameRequest(NULL), canRunQueue(false), lastUserIndex(-1)  {
		oldFrameRequest=new frameRequest_t();
		oldFrameRequest->NULLFrame=true;
	}

	void queueFrame(speechPlayer_frame_t* frame, int minNumSamples, int numFadeSamples, double finalVoicePitch, int userIndex, bool purgeQueue) {
		frameLock.acquire();
		frameRequest_t* frameRequest=new frameRequest_t;
		frameRequest->minNumSamples=minNumSamples;
		frameRequest->numFadeSamples=numFadeSamples;
		if(frame) {
			frameRequest->NULLFrame=false;
			memcpy(&(frameRequest->frame),frame,sizeof(speechPlayer_frame_t));
		} else {
			frameRequest->NULLFrame=true;
			frameRequest->frame.voicePitch=finalVoicePitch;
		}
		frameRequest->voicePitchInc=0;
		frameRequest->userIndex=userIndex;
		if(purgeQueue) {
			for(;!frameRequestQueue.empty();frameRequestQueue.pop()) delete frameRequestQueue.front();
			sampleCounter=oldFrameRequest->minNumSamples;
			if(newFrameRequest) {
				oldFrameRequest->NULLFrame=newFrameRequest->NULLFrame;
				memcpy(&(oldFrameRequest->frame),&curFrame,sizeof(speechPlayer_frame_t));
				delete newFrameRequest;
				newFrameRequest=NULL;
			}
		} else if(!frameRequestQueue.empty()) {
			frameRequest_t* prevFrameRequest=frameRequestQueue.back();
			int numSamples=prevFrameRequest->minNumSamples+frameRequest->numFadeSamples;
			prevFrameRequest->voicePitchInc=(frameRequest->frame.voicePitch-prevFrameRequest->frame.voicePitch)/numSamples;
		}
		frameRequestQueue.push(frameRequest);
		if(!frame&&!purgeQueue) canRunQueue=true;
		frameLock.release();
	}

	const int getLastIndex() {
		return lastUserIndex;
	}

	const speechPlayer_frame_t* const getCurrentFrame() {
		frameLock.acquire();
		updateCurrentFrame();
		frameLock.release();
		return &curFrame;
	}

	~FrameManagerImpl() {
		if(oldFrameRequest) delete oldFrameRequest;
		if(newFrameRequest) delete newFrameRequest;
	}

};

FrameManager* FrameManager::create() { return new FrameManagerImpl(); }
