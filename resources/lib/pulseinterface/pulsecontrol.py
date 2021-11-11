import sys, os, threading
import xbmc

import pulsectl
from pulsectl import PulseIndexError, PulseVolumeInfo
from helper import *


class PulseControl():
	def __init__( self, name = 'Pulse Control Script'):
		
		self.sformats = ["u8","aLaw","uLaw","s16le","s16be","f32le","f32be","s32le","s32be","s24le","s24be","s24-32le","s24-32be"]
		self.lock = threading.Lock()
		self.name = name
		
	def __str__(self):
		return self.name

	def start(self):
		log("pctl: start")
		try:
			self.pulse = pulsectl.Pulse(self.name)
		except Exception as e: handle(e)
		
		
		
	def __del__(self):
		try:
			self.pulse.close()
		except: pass
		
		
		
	def get_list(self, obj):
		if not obj in ["sink","sink_input","client","module", "card"]: return
		
		result = None
		func = obj + '_list'
		
		try:
			method = getattr(self.pulse, func)
		except Exception as e: 
			handle(e)
			return
		
		self.lock.acquire()
		try:
			result = method()
		except Exception as e: handle(e)
		finally:
			self.lock.release()
			for ele in result:
				try:
					sample_spec = {"format":self.sformats[ele.sample_spec.format],"rate":ele.sample_spec.rate,"channels":ele.sample_spec.channels}
					ele.sample_spec = sample_spec
					
				except :pass
			 
			return result
			
	
	def get_info(self, obj, index):
		if not obj in ["sink","sink_input","client","module","card"]: return
		
		result = None
		func = obj + '_info'
		
		try:
			method = getattr(self.pulse, func)
		except: return
		
		self.lock.acquire()
		try:
			result = method(index)
		except PulseIndexError: return None
		except Exception as e: handle(e)
		finally:
			self.lock.release()
			try:
				sample_spec = {"format":self.sformats[result.sample_spec.format],"rate":result.sample_spec.rate,"channels":result.sample_spec.channels}
				result.sample_spec = sample_spec

			except :pass
			return result
			
	#
	# module loading
	#
	
	
	def load_module(self, name, args = ""):
			self.pulse.module_load(name, args)

		
	def unload_module(self, index):
			self.pulse.module_unload(index)
	
	def move_sink_input(self, si_index, s_index):
			if si_index is not None and s_index is not None:
				self.pulse.sink_input_move(si_index, s_index)
	
	#
	# set values
	#
	
	def set_port_latency(self, info):
		if info["card"] == '':return
		self.pulse.card_port_set_latency(info["card"],info["port"],int(info["latency"]))
	
	def set_sink_volume(self, index, vol):
		vol_obj = self.get_info("sink",index).volume
		vol_obj.value_flat = vol
		self.pulse.sink_volume_set(index, vol_obj)
		
	def get_sink_volume(self, index):
		vol_obj = self.get_info("sink",index).volume
		return vol_obj.value_flat
		
	def update_sink_volume(self, index, delta_vol):
		
		vol_obj = self.get_info("sink",index).volume
			
		volume = float( vol_obj.value_flat + delta_vol)
		if volume < float(0) : volume = float(0)
		if volume > float(1.50) : volume = float(1.50)
			
		vol_obj.value_flat = volume 
			
		self.pulse.sink_volume_set(index, vol_obj)
		return volume
		
		
