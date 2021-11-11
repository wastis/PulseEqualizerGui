import xbmc, xbmcgui
import json, os, sys

from pulseinterface import PulseInterfaceService
from helper import PipeCom
from time import sleep


class PaMonitor( xbmc.Monitor ):

	def __init__( self , pid = 0):
		#strat process
		xbmc.Monitor.__init__( self )
		xbmc.log("Start PulesEqualizer service",xbmc.LOGINFO)
		
		
		self.pipe_com = PipeCom("/run/shm/pa/", pid)
		em = PulseInterfaceService(self.pipe_com)
		
		sleep(0.5)
		
		self.pipe_com.send("server", "set;device;%s" % (self.get_device()))

		while not self.abortRequested():
			if self.waitForAbort( 10 ):
				break
		
		em.stop_event_loop()
	
	@staticmethod
	def get_device():
		device = ""
		r_dict = json.loads(xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.GetSettings", "params":{ "filter": {"section":"system", "category":"audio"}}, "id":1}'))
		for s in r_dict["result"]["settings"]:
			if s["id"] == "audiooutput.audiodevice":
				device = s["value"]
				break
		return device
		
	
	def onNotification( self, sender, method, data ):
		target,func = method.lower().replace("on","").split(".")
		if target in ["system", "player"]:
			self.pipe_com.send("server", "%s;%s;%s" % (func,target,self.get_device()))
		



