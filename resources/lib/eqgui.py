#	This file is part of PulseEqualizerGui for Kodi.
#	
#	Copyright (C) 2021 wastis    https://github.com/wastis/PulseEqualizerGui
#
#	PulseEqualizerGui is free software; you can redistribute it and/or modify
#	it under the terms of the GNU Lesser General Public License as published
#	by the Free Software Foundation; either version 3 of the License,
#	or (at your option) any later version.
#
#

import xbmc
#import xbmcaddon
#import xbmcvfs
import xbmcgui
import math, json
from threading import Thread
from time import sleep

from helper import *

class EqGui(  xbmcgui.WindowXMLDialog  ):

	single_freq = False

	def __init__( self,  *args, **kwargs ):
		self.sock = SocketCom("server")
		
		self.eqid = kwargs["eqid"]
		self.desc = kwargs["desc"]
		try: self.noise = kwargs["noise"]
		except: self.noise = False
		
		self.profile = self.sock.call_func("get","eq_base_profile", [self.eqid])
		self.frequencies = self.sock.call_func("get","eq_frequencies")
		self.preamp, self.coef = self.sock.call_func("get","eq_filter", [self.eqid])
		
		self.control_state = {}
		self.controlId = 0
		
		self.updating = False
		
		
	def onInit( self ):
		header = self.getControl(101)
		header.setLabel("%s         Profile:   %s" % (self.desc, self.profile))
		self.scan_slider()
		if self.noise:
			self.sock.call_func("play","start") 
			

		
	def scan_slider(self):
		
		# get the slider & labels from the gui 
		slider_list = []
		for i in range(1900,1913):
			try:
				slider = self.getControl(i)
				slider_list.append(slider)
			except Exception:
				break;
		
		freq = self.frequencies
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

		# set slider of the filter
		coef_pos = 0
		for slider in slider_list[1:]:
			 slider.setInt(self.coef2slider(self.coef[coef_pos]), 0, 1, 100)
			 coef_pos = coef_pos + 1

		# set preamplifier slider
		slider_list[0].setInt(self.coef2slider(self.preamp), 0, 1, 100) 

	def set_filter(self):
		self.sock.call_func("set","eq_filter",[self.eqid, self.preamp, self.coef]) 
		
	def load_profile(self):
		self.sock.call_func("load","eq_profile",[self.eqid, self.profile]) 
		
	def save_profile(self):
		self.sock.call_func("save","eq_profile",[self.eqid, self.profile]) 

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

	#reduce the messages to dbus, when slider is moved. 
	def update(self):
		sleep(0.3)
		self.set_filter()
		self.updating = False
	
	def setFilter(self):
		cid = self.controlId - 1900
		
		
		if self.single_freq:
			# filter everything except the current frequency
			self.preamp = self.slider2coef(self.slider_list[0].getFloat())
			for i in range(0,len(self.coef)):
				self.coef[i] = 0
			
			if cid == 0:
				for slider in self.slider_list[1:]:
					self.coef[cid] = self.slider2coef(slider.getFloat())
					cid = cid + 1
			else:
				self.coef[cid-1] = self.slider2coef(self.slider_list[cid].getFloat())
			
		else:
		
			if cid == 0:
				self.preamp = self.slider2coef(self.slider_list[0].getFloat())
			elif cid < len( self.slider_list):
				self.coef[cid-1] = self.slider2coef(self.slider_list[cid].getFloat())												
			
		
		if not self.updating:
			self.updating = True
			Thread(target=self.update).start()
		
		
	def setZero(self):
		cid = self.controlId - 1900
		
		if cid == 0:
			self.preamp = 1.0
			self.slider_list[0].setInt(50,0,1,100)
		elif cid < len( self.slider_list):
			self.coef[cid-1] = 1.0
			self.slider_list[cid].setInt(50,0,1,100)
			
		
		
	def save(self):
		cid = 0
		self.preamp = self.slider2coef(self.slider_list[0].getFloat())
		
		for slider in self.slider_list[1:]:
			self.coef[cid] = self.slider2coef(slider.getFloat())
			cid = cid + 1
			
		self.set_filter()
		self.save_profile()
		
		
	def onAction( self, action ):
		#OK pressed
		if action.getId() == 7:
			self.save()
			if self.noise: 
				self.sock.call_func("play","stop") 

			self.close()
		
		#Cancel
		if action.getId() in [92,10]:
			
			if self.noise: 
				self.sock.call_func("play","stop") 
			
			self.load_profile()
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
			
		
		#xbmc.log( "code :" + str(action.getButtonCode()),xbmc.LOGINFO)
		#xbmc.log( "Id   :" + str(action.getId()),xbmc.LOGINFO)
