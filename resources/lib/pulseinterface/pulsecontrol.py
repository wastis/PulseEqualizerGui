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

import threading
import pulsectl

from pulsectl import PulseVolumeInfo
from pulsectl import PulseIndexError

from basic import handle
from basic import opthandle
from basic import log

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

	def stop(self):
		try:
			self.pulse.close()
		except Exception as e: opthandle(e)

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
				except AttributeError: pass
				except Exception as e: opthandle(e)

		return result

	def get_info(self, obj, index):
		if not obj in ["sink","sink_input","client","module","card"]: return

		result = None
		func = obj + '_info'

		try:
			method = getattr(self.pulse, func)
		except Exception: return

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
			except AttributeError: pass
			except Exception as e: opthandle(e)
		return result

	def get_server_info(self):
		self.lock.acquire()
		try:
			result = self.pulse.server_info()
		except Exception as e:
				handle(e)
		self.lock.release()

		return result

	#
	# module loading
	#

	def load_module(self, name, args = ""):
			self.lock.acquire()
			try:
				self.pulse.module_load(name, args)
			except Exception as e:
				handle(e)

			self.lock.release()

	def unload_module(self, index):
			self.lock.acquire()
			try:
				self.pulse.module_unload(index)
			except Exception as e:
				handle(e)

			self.lock.release()

	def move_sink_input(self, si_index, s_index):
			if si_index is not None and s_index is not None:
				if not self.get_info("sink",s_index):
					return
				if not self.get_info("sink_input",si_index):
					return

				self.lock.acquire()
				try:
					self.pulse.sink_input_move(si_index, s_index)
				except Exception as e:
					handle(e)
				self.lock.release()

	#
	# set values
	#

	def set_port_latency(self, info):
		if info["card"] == '':return
		self.lock.acquire()
		try:
			self.pulse.card_port_set_latency(info["card"],info["port"],int(info["latency"]))
		except Exception as e:
			handle(e)
		self.lock.release()

	def set_sink_volume(self, index, vol):
		vol_obj = self.get_info("sink",index).volume
		vol_obj.value_flat = vol
		self.lock.acquire()
		try:
			self.pulse.sink_volume_set(index, vol_obj)
		except Exception as e:
			handle(e)
		self.lock.release()

	def get_sink_volume(self, index):
		obj = self.get_info("sink",index)
		if obj is None:
			return None
		return obj.volume.value_flat

	def get_sink_volume_array(self, index):
		return self.get_info("sink",index).volume.values

	def set_sink_volume_array(self, index, volarray):
		vol_obj = PulseVolumeInfo(volarray)
		self.lock.acquire()
		try:
			self.pulse.sink_volume_set(index, vol_obj)
		except Exception as e:
			handle(e)
		self.lock.release()

	def get_sink_channel(self, index):
		return self.get_info("sink",index).channel_list

	def set_default_sink(self, sink_obj):
		self.lock.acquire()
		try:
			self.pulse.sink_default_set(sink_obj)
		except Exception as e:
			handle(e)
		self.lock.release()
