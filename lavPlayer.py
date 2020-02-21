import libaudioverse

class LavPlayer(object):

	def __init__(self,speechPlayer,sampleRate):
		self.speechPlayer=speechPlayer
		libaudioverse.initialize()
		self.lavServer=libaudioverse.Server(22050,64)
		self.lavServer.set_output_device("default")
		self.lavPullNode=libaudioverse.PullNode(self.lavServer,sampleRate,1)
		self.lavPullNode.connect(0,self.lavServer)
		self.lavPullNode.set_audio_callback(self.lavPullNodeCallback)

	def lavPullNodeCallback(self,node,numFrames,channels,buffer):
		buf=self.speechPlayer.synthesize(numFrames)
		for x in range(numFrames):
			buffer[x]=(buf[x]/32767.0) if buf else 0


