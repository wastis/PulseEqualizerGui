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

#
#  paModuleManager is a major class that
#    - manages the loading of the equalizer,
#    - configuration of the equalizer (setting profile),
#    - equalizer on/of switchning,
#    - change system volume
#    - interconnetion of pulseaudio modules, dependent on playback status
#

import time
import threading

from helper import SocketCom

from basic import handle
from basic import log
from basic import logerror

class paModuleManager():
	def __init__(self, pulsecontrol, eqcontrol, padb, conf):
		self.pc = pulsecontrol
		self.padb = padb
		self.eq = eqcontrol

		self.dyn_equalizer = None	# dynamic loaded equalizer
		self.eq_name = "eq-auto-load" #name of the dynamic equalizer

		# following flags define whether to insert the equalizer into the playback stream

		self.is_playing = False
		self.config  = conf # configuration class
		self.reroute = False
		self.eq_fatal = False

	#
	#	handle control messages
	#

	def on_pa_connect(self):
		log("pamm: start paModuleManager")
		try:
			self.load_dyn_equalizer()
			self.eq_fatal = False
		except Exception as e:
			self.eq_fatal = True
			handle(e)
			logerror("cannot load pulseaudio-equalizer, maybe not installed?")
			logerror("run: sudo apt install pulseaudio-equalizer")
			return None

		self.config.load_config()

		self.load_required_module("module-dbus-protocol")

		self.eq.on_pa_connect()

		sock = SocketCom("kodi")
		player = sock.call_func("get","player")
		if player and len(player) > 0: self.on_player_play()
		else: self.on_player_stop()

	def on_message_exit(self):
		self.unload_dyn_equalizer()
		self.pc.stop()

	#
	#	Kodi Play/Pause/Resum/Stop/device set messages
	#

	def on_player_play(self):
		log("pamm: on_player_play")
		self.is_playing = True
		self.adjust_routing()

	def on_player_resume(self):
		log("pamm: on_player_play")
		self.is_playing = True
		self.adjust_routing()

	def on_player_pause(self):
		log("pamm: on_player_pause")
		self.is_playing = False
		self.adjust_routing()

	def on_player_stop(self):
		log("pamm: on_player_stop")
		self.is_playing = False
		self.adjust_routing()

	def on_device_set(self,_):
		log("pamm: on_device_set")
		self.adjust_routing()

	def on_player_avstart(self): pass
	def on_player_avchange(self): pass

	#
	#	handle kodi playback chain change messages
	#

	# the messages arriving here are generated by paDatabase after information gathering
	@staticmethod
	def get_index(old,new):
		o = None if old is None else old.index
		n = None if new is None else new.index
		return "%s -> %s" % ( o, n )

	def on_kodi_stream_update(self, old, new):
		log("pamm: on_kodi_stream_update " + self.get_index(old, new))

		if new is not None: self.reroute = True

	def on_output_sink_update(self, _old, new):
		log("pamm: on_output_sink_update -> %s" % (None if new is None else new.name))
		if new is not None: self.reroute = True

	def on_autoeq_sink_update(self, old, new):
		log("pamm: on_autoeq_sink_update -> %s" % (None if new is None else new.name))
		if new is None:
			if old is not None:
				if self.padb.cureq_sink == old: self.padb.cureq_sink = None

			self.dyn_equalizer = None
			self.load_dyn_equalizer()
		else:
			self.dyn_equalizer = new.index
			self.adjust_routing()

	#
	#	handle pulse audio messages
	#

	# messages arriving here are comeing from pulseaudio, but are aggregated by paDatabase
	def on_sink_change(self, index):
		if self.padb.output_sink and self.padb.output_sink.index == index:
			log("pamm: on_sink_change %s" % self.padb.output_sink.name)
			vol = self.pc.get_sink_volume(self.padb.output_sink.index)
			if vol is not None:
				self.config.set("volume",vol, self.padb.output_sink.name)

		else: log("pamm: on_sink_change %d" % index)

	#*************************************************************************
	#
	#	execute routing logic
	#
	#**************************************************************************

	#
	#                   no -> connect kodi stream directly to output device, skip all filters. This is better for gui sounds
	#   kodi playing?
 	#                   yes ->  playing to preconfigured chain?
 	#
 	#                                    yes ->  connect elements of this chain together and finnaly to the correct final output sink
 	#
 	#                                    no ->  do we need to insert the auto loaded equalizer?
	#
	#                                                   yes-> configure kodi-stream -> equalizer -> output sink
	#
	#                                                   no->  configure kodi-stream -> output sink

	#	routing is triggered by pa-changes, do update is called as last message
	def do_update(self):
		if self.reroute:
			self.adjust_routing()

	#
	#  entry point: rule is different whether player is playing or not
	#

	def adjust_routing(self):
		#
		#	switch streams
		#
		self.reroute = False
		if self.padb.output_sink is None: return

		if self.padb.kodi_stream is not None:
			log("pamm: adjust routing")
			if self.is_playing: self.adjust_routing_play()
			else: self.adjust_routing_stop()
		#
		#  after rerouting, configure_devices with volume, latency and equalizer profile, dependent on output sink
		#
		volume = self.config.get("volume",None, self.padb.output_sink.name)
		if volume is not None:	self.pc.set_sink_volume(self.padb.output_sink.index, volume)

		latency = 0
		eq_sink = self.padb.cureq_sink if self.padb.cureq_sink else self.padb.autoeq_sink

		if eq_sink:
			eq_profile = self.config.get("eq_profile",None, self.padb.output_sink.name)

			if eq_profile:
				self.eq.on_eq_profile_load(eq_sink.index, eq_profile)
			else:
				self.eq.on_eq_profile_load(eq_sink.index, "default")

			eq_correction = self.config.get("eq_correction",None, self.padb.output_sink.name)
			if eq_correction:
				self.eq.on_room_correction_set(eq_sink.index, eq_correction)
			else:
				self.eq.on_room_correction_unset(eq_sink.index)

		if self.padb.cureq_sink and self.is_playing:
			latency = self.config.get("eq_latency",350000, self.padb.output_sink.name)
		else:
			latency = self.config.get("latency",0, self.padb.output_sink.name)

		latency_info = self.padb.get_latency()
		latency_info["latency"] = latency
		self.pc.set_port_latency(latency_info)

	#check if we need to play to a chain (filter device) or an sound output
	def adjust_routing_play(self):
		log("pamm: adjust routing play")
		if self.padb.is_dynamic():
			self.aj_play_sound_device()
		else:
			self.aj_play_filter_chain()

	#to avoid artefacts when player is stopped
	def timer_routing_stop(self):
		time.sleep(1)
		if not self.is_playing:
			if self.padb.kodi_stream is None or self.padb.output_sink is None:
				log("pamm: no stream to move")
				return
			try:
				log("pamm: move stream %s -> %s" % (self.padb.kodi_stream.name, self.padb.output_sink.name))
				self.pc.move_sink_input(self.padb.kodi_stream.index , self.padb.output_sink.index)
			except Exception as e:
				handle(e)

	#in case player is not playing, move kodi output always to sound sink to avoid latency
	def adjust_routing_stop(self):
		log("pamm: adjust routing stop")
		self.padb.cureq_sink = None
		threading.Thread(target = self.timer_routing_stop).start()

		# auto load equalizer shall be the active and routed to actual ouput sink
		if self.padb.autoeq_stream is not None:
			self.pc.move_sink_input(self.padb.autoeq_stream.index , self.padb.output_sink.index)

	#
	# connect all elements of the filter together (just in case) and route last element to target
	#

	def aj_play_filter_chain(self):
		if self.padb.playback_stream is None: return

		# connect chain
		for stream, sink in self.padb.playback_stream:
			log("pamm: move stream %s -> %s" % (stream.name, sink.name))
			self.pc.move_sink_input(stream.index , sink.index)

		# connect the last to current output sink
		# stream, sink = (self.padb.playback_stream[-1])
		# log("pamm: move stream %s -> %s" % (stream.name, self.padb.output_sink.name))
		# self.pc.move_sink_input(stream.index , self.padb.output_sink.index)

		self.padb.cureq_sink = self.padb.chaineq_sink

	# check if equalizer for this device is enabled and insert it if so
	def aj_play_sound_device(self):
		eq_enable = self.config.get("eq_enable","off", self.padb.output_sink.name)

		if eq_enable == "off":
			# should directly be connected to the target
			log("pamm: move stream %s -> %s" % (self.padb.kodi_stream.name, self.padb.output_sink.name))
			self.pc.move_sink_input(self.padb.kodi_stream.index  , self.padb.output_sink.index)
			self.padb.cureq_sink = None

		else:
			if self.padb.autoeq_sink is None:
				# autoeq has been closed, reload
				log("pamm: autoeq sink died, wait for reload")

			else:
				# should directly be connected to the equalizer
				log("pamm: move stream %s -> %s" % (self.padb.kodi_stream.name, self.padb.autoeq_sink.name))
				self.pc.move_sink_input(self.padb.kodi_stream.index , self.padb.autoeq_sink.index)

				# equalizer should directly be connected to target
				log("pamm: move stream %s -> %s" % (self.padb.autoeq_stream.name, self.padb.output_sink.name))
				self.pc.move_sink_input(self.padb.autoeq_stream.index , self.padb.output_sink.index)
				self.padb.cureq_sink = self.padb.autoeq_sink

	#
	# handle client request messages
	#

	def set_eq_config(self):
		profile = self.config.get("eq_profile","none", self.padb.output_sink.name)
		if profile is not None: return

		eq_profile = self.eq.on_eq_base_profile_get()
		self.config.set("eq_profile",eq_profile, self.padb.output_sink.name)

	def on_eq_current_get(self):
		index, desc, eq_enable, is_dyn  = (None , None, "off", self.padb.is_dynamic())

		if self.eq_fatal:
			return ( -1, "fatal", self.is_playing, "off", is_dyn)

		if self.padb.cureq_sink is not None:
			index = self.padb.cureq_sink.index
			desc = self.padb.cureq_sink.proplist["device.description"]
		elif self.padb.autoeq_sink is not None:
			index = self.padb.autoeq_sink.index
			desc = self.padb.autoeq_sink.proplist["device.description"]

		if self.padb.kodi_first_sink is not None:
			if self.padb.output_sink is not None:
				eq_enable = self.config.get("eq_enable","off", self.padb.output_sink.name)

				if eq_enable != "off":
					eq_enable = self.config.get("eq_profile","none", self.padb.output_sink.name)

		return ( index, desc, self.is_playing, eq_enable, is_dyn)

	def on_eq_on_switch(self):
		if not self.padb.output_sink: return
		if not self.padb.is_dynamic(): return

		log("pamm: on_eq_on_switch")

		self.config.set("eq_enable", "on", self.padb.output_sink.name)
		self.set_eq_config()
		self.adjust_routing()

	def on_eq_off_switch(self):
		if not self.padb.output_sink: return
		if not self.padb.is_dynamic(): return

		log("pamm: on_eq_off_switch")

		self.config.set("eq_enable", "off", self.padb.output_sink.name)
		self.adjust_routing()

	def on_volume_get(self):
		log("pamm: on_volume_get")

		if self.padb.output_sink is None: return None
		try: return self.pc.get_sink_volume(self.padb.output_sink.index)
		except Exception: return None

	def on_volume_set(self,volume):
		vol = float(volume)
		log("pamm: on_volume_set %f"%vol)
		if self.padb.output_sink is None: return None

		try: self.pc.set_sink_volume(self.padb.output_sink.index, vol)
		except Exception as e: handle(e)

	#
	#	equalizer load and unload
	#

	def load_dyn_equalizer(self):
		log("pamm: load "+ self.eq_name)
		# equalizer already loaded?
		for _, sink in list(self.padb.sinks.items()):
			if sink.name == self.eq_name:
				self.dyn_equalizer = sink.index
				log("pamm: %s already loaded" % self.eq_name)
				return

		args = 'sink_name=%s sink_properties="device.description=Equalizer"' % ( self.eq_name )
		self.pc.load_module('module-equalizer-sink', args)

	def unload_dyn_equalizer(self):
		if self.dyn_equalizer  is not None:
			index = self.padb.sinks[self.dyn_equalizer].owner_module
			self.dyn_equalizer = None
			self.pc.unload_module(index)

	def load_required_module(self, name):
		log("pamm: load "+ name)
		for _,module in list(self.padb.modules.items()):
			if module.name == name:
				log("pamm: %s already loaded" % name)
				return

		self.pc.load_module(name)

	#
	#	helper
	#

	@staticmethod
	def get_sink_info(sink):
		try:
			return "%s  %s %s %s" % (sink.name, sink.sample_spec["format"], sink.sample_spec["rate"], sink.sample_spec["channels"])
		except Exception: return sink.name
