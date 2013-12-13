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

#define _USE_MATH_DEFINES

#include <cassert>
#include <cmath>
#include <cstdlib>
#include "debug.h"
#include "utils.h"
#include "speechWaveGenerator.h"

using namespace std;

const double PITWO=M_PI*2;

class NoiseGenerator {
	private:
	double lastValue;

	public:
	NoiseGenerator(): lastValue(0.0) {};

	double getNext() {
		lastValue=((double)rand()/RAND_MAX)+0.75*lastValue;
		return lastValue;
	}

};

class FrequencyGenerator {
	private:
	int sampleRate;
	double lastCyclePos;

	public:
	FrequencyGenerator(int sr): sampleRate(sr), lastCyclePos(0) {}

	double getNext(double frequency) {
		double cyclePos=fmod((frequency/sampleRate)+lastCyclePos,1);
		lastCyclePos=cyclePos;
		return cyclePos;
	}

};

class VoiceGenerator {
	private:
	FrequencyGenerator pitchGen;
	FrequencyGenerator vibratoGen;

	public:
	VoiceGenerator(int sr): pitchGen(sr), vibratoGen(sr) {};

	double getNext(double pitch, double vibratoOffset, double vibratoSpeed) {
		double vibrato=(sin(vibratoGen.getNext(vibratoSpeed)*PITWO)*0.06*vibratoOffset)+1;
		return atan(pitchGen.getNext(pitch*vibrato)*PITWO);
	}

};

class Resonator {
	private:
	//raw parameters
	int sampleRate;
	double frequency;
	double bandwidth;
	bool anti;
	//calculated parameters
	bool setOnce;
	double a, b, c;
	//Memory
	double p1, p2;

	public:
	Resonator(int sampleRate, bool anti) {
		this->sampleRate=sampleRate;
		this->anti=anti;
		this->setOnce=false;
		this->p1=0;
		this->p2=0;
	}

	void setParams(double frequency, double bandwidth) {
		bandwidth=max(bandwidth,10);
		if(!setOnce||(frequency!=this->frequency)||(bandwidth!=this->bandwidth)) {
			this->frequency=frequency;
			this->bandwidth=bandwidth;
			double r=exp(-M_PI/sampleRate*bandwidth);
			c=-(r*r);
			b=r*cos(PITWO/sampleRate*-frequency)*2.0;
			a=1.0-b-c;
			if(anti&&frequency!=0) {
				a=1.0/a;
				c*=-a;
				b*=-a;
			}
		}
		this->setOnce=true;
	}

	double resonate(double in) {
		if(!setOnce) return in;
		double out=a*in+b*p1+c*p2;
		p2=p1;
		p1=out;
		return out;
	}

};

class SpeechWaveGeneratorImpl: public SpeechWaveGenerator {
	private:
	int sampleRate;
	VoiceGenerator voiceGenerator;
	NoiseGenerator breathGenerator;
	FrameManager* frameManager;
	Resonator* resonators[SPEECHPLAYER_FRAME_NUMFORMANTS]; 

	public:
	SpeechWaveGeneratorImpl(int sr): sampleRate(sr), voiceGenerator(sr), breathGenerator(), frameManager(NULL) {
		for(int i=0;i<SPEECHPLAYER_FRAME_NUMFORMANTS;++i) resonators[i]=new Resonator(sr,false);
	}

	~SpeechWaveGeneratorImpl() {
		for(int i=0;i<SPEECHPLAYER_FRAME_NUMFORMANTS;++i) delete resonators[i]; 
	}

	void generate(const int sampleCount, sample* sampleBuf) {
		if(!frameManager) return; 
		double val=0;
		for(int i=0;i<sampleCount;++i) {
			const speechPlayer_frame_t* frame=frameManager->getCurrentFrame();
			double voice=voiceGenerator.getNext(frame->voicePitch,frame->vibratoOffset,frame->vibratoSpeed);
			double breath=breathGenerator.getNext()*0.5;
			double mix=calculateValueAtFadePosition(voice,breath,frame->breathyness)*frame->voiceAmplitude;
			for(int f=0;f<SPEECHPLAYER_FRAME_NUMFORMANTS;++f) {
				resonators[f]->setParams(frame->formantParams[f].frequency,frame->formantParams[f].bandwidth);
				float resVal=resonators[f]->resonate(mix);
				mix=calculateValueAtFadePosition(mix,resVal,frame->formantParams[f].amplitude);
			}
			sampleBuf[i].value=max(min(mix*4000,32000),-32000);
		}
	}

	void setFrameManager(FrameManager* frameManager) {
		this->frameManager=frameManager;
	}

};

SpeechWaveGenerator* SpeechWaveGenerator::create(int sampleRate) {return new SpeechWaveGeneratorImpl(sampleRate); }
