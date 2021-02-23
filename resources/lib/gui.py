import xbmc
import xbmcaddon
import xbmcvfs
import xbmcgui
import math

from pulse_class import FILTER

class GUI(  xbmcgui.WindowXMLDialog  ):

	def __init__( self, *args, **kwargs ):
		self.test = 1
		self.control_state = {}
		self.controlId = 0
		self.filter = FILTER()
		
		xbmc.log( "sample rate :" + str(self.filter.filter_rate),xbmc.LOGINFO)
		

	def onInit( self ):
		header = self.getControl(101)
		self.profile = self.filter.get_base_profile()
		
		try:
			self.filter.load_profile(self.profile)
		except Exception as e:
			xbmc.log(e.message,xbmc.LOGERROR)
			self.profile = "Default"
			self.filter.reset()
			self.filter.save_state()
			self.filter.save_profile(self.profile)

		header.setLabel("Pulse Equalizer         Profile:   %s" % self.profile)
		self.scan_slider()
		
	def scan_slider(self):
		
		# get the slider & labels from the gui 
		slider_list = []
		for i in range(1900,1913):
			try:
				slider = self.getControl(i)
				slider_list.append(slider)
			except Exception:
				break;
		
		freq = self.filter.frequencies[1:]
		for i in range(2002,2013):
			try:
				tbox = self.getControl(i)
				tbox.setLabel(self.freq_to_txt(freq[i-2002]))
				xbmc.log(str(i),xbmc.LOGINFO)
			except Exception:
				break;
				
		# setup left-right navigation
		self.slider_list = slider_list
						
		last = len(slider_list)-1
		for i in range(1,last):
			slider_list[i].controlLeft(slider_list[i-1])
			slider_list[i].controlRight(slider_list[i+1])
			
		slider_list[0].controlLeft(slider_list[last])
		slider_list[0].controlRight(slider_list[1])
		slider_list[last].controlLeft(slider_list[last-1])
		slider_list[last].controlRight(slider_list[0])
		
		# set focus to first slider
		self.setFocus(slider_list[0])
		
		# get current filter coeffitients
		coef,preamp = self.filter.filter_at_points()

		# set slider of the filter
		coef_pos = 0
		for slider in slider_list[1:]:
			 slider.setInt(self.coef2slider(coef[coef_pos]), 0, 1, 100)
			 coef_pos = coef_pos + 1

		# set preamplifier slider
		slider_list[0].setInt(self.coef2slider(preamp), 0, 1, 100) 
		

	def onFocus( self, controlId ):
		if self.controlId == 0: self.controlId = controlId
		self.controlId = controlId

	@staticmethod
	def freq_to_txt(val):
		if(val>=1000):return str(int(((val / 1000)+0.5)))+'k'
		return str(int(val))
	
	@staticmethod
	def slider2coef(val):
		#slider 0-100 into dB [-10db .. 10db] = [0.1 ... 10]
		return 10.0**((val-50.0)/50.0)
	@staticmethod
	def coef2slider(val):
		return int(math.log10( val )*50+50.0)

	def setFilter(self):
		cid = self.controlId - 1900
		
		if cid == 0:
			self.filter.preamp = self.slider2coef(self.slider_list[0].getFloat())
		elif cid < len( self.slider_list):
			self.filter.coefficients[cid-1] = self.slider2coef(self.slider_list[cid].getFloat())
			
		self.filter.seed_filter()
		self.filter.save_state()
		
	def setZero(self):
		cid = self.controlId - 1900
		
		if cid == 0:
			self.filter.preamp = 1.0
			self.slider_list[0].setInt(50,0,1,100)
		elif cid < len( self.slider_list):
			self.filter.coefficients[cid-1] = 1.0
			self.slider_list[cid].setInt(50,0,1,100)
			
		self.filter.seed_filter()
		self.filter.save_state()
		
	def save(self):
		cid = 0
		self.filter.preamp = self.slider2coef(self.slider_list[0].getFloat())
		
		for slider in self.slider_list[1:]:
			self.filter.coefficients[cid] = self.slider2coef(slider.getFloat())
			cid = cid + 1
			
		self.filter.seed_filter()
		self.filter.save_state()
		self.filter.save_profile(self.profile)
		
		
	def onAction( self, action ):
		#OK pressed
		if action.getId() == 7:
			self.save()
			self.close()
		
		#Cancel
		if action.getId() in [92,10]:
			self.filter.load_profile(self.profile)
			self.close()
		
		#up/down/left/right
		if action.getId() in [1,2,3,4]:
			fid = self.getFocusId()
			if fid == 0:
				self.setFocusId(self.controlId)
			self.setFilter()
		
		#0 pressed, reset slider
		if action.getId() in [58]:
			fid = self.getFocusId()
			if fid == 0:
				self.setFocusId(self.controlId)

			self.setZero()
			
		
		xbmc.log( "code :" + str(action.getButtonCode()),xbmc.LOGINFO)
		xbmc.log( "Id   :" + str(action.getId()),xbmc.LOGINFO)
