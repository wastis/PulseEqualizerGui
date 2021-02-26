import xbmc
import json, os, sys
from pulse_class import STREAM_FUNC

class PE_SERVICE( xbmc.Monitor ):

	def __init__( self ):
		#strat process
		xbmc.Monitor.__init__( self )
		xbmc.log("Start PulesEqualizer service",xbmc.LOGINFO)
		self.stream_func = STREAM_FUNC()
		
		while not self.abortRequested():
			if self.waitForAbort( 10 ):
				break

	def onNotification( self, sender, method, data ):
		data = json.loads( data )
		streams=[]
		result=[]
		if "Player.OnAVStart" in method:
			xbmc.log(self.stream_func.switch_chain(),xbmc.LOGINFO)
		if "Player.OnResume" in method:
			xbmc.log(self.stream_func.switch_chain(),xbmc.LOGINFO)

