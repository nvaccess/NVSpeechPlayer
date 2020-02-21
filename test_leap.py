import Leap

import speechPlayer
import lavPlayer
import ipa

sp=speechPlayer.SpeechPlayer(22050)
lp=lavPlayer.LavPlayer(sp,22050)

spFrame=speechPlayer.Frame()
spFrame.outputGain=1.0
spFrame.preFormantGain=1.0
spFrame.endVoicePitch=spFrame.voicePitch=110
ipa.applyPhonemeToFrame(spFrame,ipa.data['a'])

class Test(Leap.Listener):

	def on_init(self,controller):
		print("Initialized")

	def on_connect(self,controller):
		print("hello")
		controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE)

	def on_frame(self,controller):
		frame=controller.frame()
		points=frame.hands
		if len(points)==0:
			sp.queueFrame(None,0,50,purgeQueue=True)
		else:
			p=points[0]
			c=frame.interaction_box.normalize_point(p.palm_position)
			spFrame.endVoicePitch=spFrame.voicePitch=100*(8**c.y)
			spFrame.cf1=200+600*c.x
			spFrame.cf2=500+1500*c.z
			spFrame.cf3=3200
			sp.queueFrame(spFrame,20000,50,purgeQueue=True)

t=Test()
controller=Leap.Controller()
controller.add_listener(t)
input()
