import xbmc
import xbmcaddon
import xbmcvfs
import xbmcgui

from helper import *

addon = xbmcaddon.Addon()
def tr(id):
	return addon.getLocalizedString(id)

class LatencyGui(  xbmcgui.WindowXMLDialog  ):

	def __init__( self, *args, **kwargs ):
		self.pipe_comm = kwargs["pipe_comm"]
		self.latency_info = self.pipe_comm.get_from_server("get;latency")
		self.save = self.latency_info.copy()

	def onInit( self ):
		self.header = self.getControl(100)
		self.header.setLabel(tr(32022))
		self.slider = self.getControl(1900)
		self.label = self.getControl(2000)
		self.setFocus(self.slider)
		latency = int(self.latency_info["latency"] / 1000)
		self.slider.setInt(latency, 0, 25, 2000)
		self.label.setLabel("{:d} ms".format(latency)) 
		
	def setLatency(self):
		
		latency = int(self.slider.getInt())
		self.label.setLabel("{:d} ms".format(latency))
		self.latency_info["latency"] = latency * 1000
		self.pipe_comm.send_to_server("set;latency;%s" % (json.dumps(self.latency_info)))
		
		
	def onAction( self, action ):
		#OK pressed
		if action.getId() == 7:
			self.close()
			
		#Cancel
		if action.getId() in [92,10]:
			self.pipe_comm.send_to_server("set;latency;%s" % (json.dumps(self.save)))
			self.close()
		
		#up/down/left/right
		if action.getId() in [1,2,3,4]:
			fid = self.getFocusId()
			if fid == 0:
				self.setFocusId(1900)
			self.setLatency()
		
		#xbmc.log( "code :" + str(action.getButtonCode()),xbmc.LOGINFO)
		#xbmc.log( "Id   :" + str(action.getId()),xbmc.LOGINFO)
