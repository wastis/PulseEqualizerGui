#
#	pulse audio gui addon for kodi
#	2021 by wastis
#
#	manage the re-routing of audio streams coming from kodi
#	load and unload the eq-auto-load equalizer module
#	maintain kodi-play status (playing or not)
#
#



from .pulsecontrol import PulseControl
from .padb import paDatabase
from helper import *
import os


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
		
		
		
	
	#
	#	handle control messages
	#
		
	def on_pa_connect(self):
		log("pamm: start paModuleManager")
		self.load_dyn_equalizer()
		self.config.load_config()
		
		
	def on_message_exit(self):
		self.unload_dyn_equalizer()
		
		
	#	
	#	Kodi Play/Pause/Resum/Stop messages
	#
		
	def on_player_play(self,arg):
		log("pamm: on_player_play")
		self.is_playing = True
		self.adjust_routing()
		
	def on_player_resume(self,arg):
		log("pamm: on_player_play")
		self.is_playing = True
		self.adjust_routing()
		
	def on_player_pause(self,arg):
		log("pamm: on_player_pause")
		self.is_playing = False
		self.adjust_routing()
		
	def on_player_stop(self,arg):
		log("pamm: on_player_stop")
		self.is_playing = False
		self.adjust_routing()
		
	def on_player_avstart(self,arg): pass
	def on_player_avchange(self,arg): pass
	


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
	
	def on_output_sink_update(self, old, new):
		log("pamm: on_output_sink_update -> %s" % (None if new is None else new.name))
		if new is not None: self.reroute = True 
	
		
	#
	#	handle pulse audio messages
	#

	# messages arriving here are comeing from pulseaudio, but are aggregated by paDatabase
	def on_sink_change(self, index):
		
		if self.padb.output_sink and self.padb.output_sink.index == index:
			log("pamm: on_sink_change %s" % self.padb.output_sink.name)
			vol = self.pc.get_sink_volume(self.padb.output_sink.index)
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
		
		if self.padb.kodi_stream is None: return
		if self.padb.output_sink is None: return
		
		if self.is_playing: self.adjust_routing_play()
		else: self.adjust_routing_stop()
			
		#
		#  after rerouting, configure_devices with volume, latency and equalizer profile, dependent on output sink
		#

		volume = self.config.get("volume",None, self.padb.output_sink.name)
		if volume is not None:	self.pc.set_sink_volume(self.padb.output_sink.index, volume)

		latency = 0
		if self.padb.cureq_sink:
			eq_profile = self.config.get("eq_profile",None, self.padb.output_sink.name)
			if eq_profile:
				self.eq.on_eq_profile_load(self.padb.cureq_sink.index, eq_profile)
			else:
				eq_profile = self.eq.on_eq_base_profile_get(self.padb.cureq_sink.index)
				self.config.get("eq_profile",eq_profile, self.padb.output_sink.name)
			
			latency = self.config.get("eq_latency",350000, self.padb.output_sink.name)
			
		else:
			
			latency = self.config.get("latency",0, self.padb.output_sink.name)
			
		latency_info = self.padb.get_latency()
		latency_info["latency"] = latency
		print(latency_info)
		self.pc.set_port_latency(latency_info)
	

	#check if we need to play to a chain (filter device) or an sound output
	def adjust_routing_play(self):
		
		if self.padb.kodi_is_dynamic: self.aj_play_sound_device()
		else: self.aj_play_filter_chain()
		
	
	
	#in case player is not playing, move kodi output always to sound sink to avoid latency
	def adjust_routing_stop(self):
		
		self.padb.cureq_sink = None
		self.pc.move_sink_input(self.padb.kodi_stream.index , self.padb.output_sink.index)


	#
	# connect all elements of the filter together (just in case) and route last element to target
	#
	
	def aj_play_filter_chain(self):
	
		if self.padb.playback_stream is None: return
	
		# connect chain
		for stream, sink in self.padb.playback_stream[:-1]:
			log("move stream %s -> %s" % (stream.name, sink.name))
			self.pc.move_sink_input(stream.index , sink.index)
		
		# connect the last to current output sink
		stream, sink = (self.padb.playback_stream[-1])
		log("move stream %s -> %s" % (stream.name, self.padb.output_sink.name))
		self.pc.move_sink_input(stream.index , self.padb.output_sink.index)
		
		self.padb.cureq_sink = self.padb.chaineq_sink
		
	
	# check if equalizer for this device is enabled and insert it if so
	def aj_play_sound_device(self):
		
		eq_enable = self.config.get("eq_enable","off", self.padb.output_sink.name)
		
		if eq_enable == "off":
			# should directly be connected to the target
			log("move stream %s -> %s" % (self.padb.kodi_stream.name, self.padb.output_sink.name))
			self.pc.move_sink_input(self.padb.kodi_stream.index  , self.padb.output_sink.index)
			self.padb.cureq_sink = None
		
		else:

			# should directly be connected to the equalizer
			log("move stream %s -> %s" % (self.padb.kodi_stream.name, self.padb.autoeq_sink.name))
			self.pc.move_sink_input(self.padb.kodi_stream.index , self.padb.autoeq_sink.index)
				
			# equalizer should directly be connected to target
			log("move stream %s -> %s" % (self.padb.autoeq_stream.name, self.padb.output_sink.name))
			self.pc.move_sink_input(self.padb.autoeq_stream.index , self.padb.output_sink.index)
			self.padb.cureq_sink = self.padb.autoeq_sink


	#
	# handle client request messages
	#


	def on_eq_current_get(self):
		
		index, desc, eq_enable, is_dyn  = (None , None, "off", self.padb.kodi_is_dynamic)

		if self.padb.cureq_sink is not None:
			index = self.padb.cureq_sink.index
			desc = self.padb.cureq_sink.proplist["device.description"]
		
		if self.padb.kodi_first_sink is not None:
		
			if self.padb.output_sink is not None:
				eq_enable = self.config.get("eq_enable","off", self.padb.output_sink.name)
				
				if eq_enable != "off":
					eq_enable = self.config.get("eq_profile","none", "%s" % (self.padb.output_sink.name))
				
		
		return ( index, desc, self.is_playing, eq_enable, is_dyn) 
		
	def on_eq_on_switch(self):
		if not self.padb.output_sink: return
		if not self.padb.kodi_is_dynamic: return

		log("pamm: on_eq_on_switch")

		self.config.set("eq_enable", "on", self.padb.output_sink.name)
		self.adjust_routing()
		
	def on_eq_off_switch(self):
		if not self.padb.output_sink: return
		if not self.padb.kodi_is_dynamic: return

		log("pamm: on_eq_off_switch")

		self.config.set("eq_enable", "off", self.padb.output_sink.name)
		self.adjust_routing()
		
		
	def on_volume_get(self):
		log("pamm: on_volume_get")
		
		if self.padb.output_sink is None: return None
		try: return self.pc.get_sink_volume(self.padb.output_sink.index)
		except: return None
		
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

		# equalizer already loaded?
		for sid, sink in self.padb.sinks.items():
			if sink.name == self.eq_name:
				self.dyn_equalizer = sink.index
				return

		args = 'sink_name=%s sink_properties="device.description=Equalizer"' % ( self.eq_name )
		self.pc.load_module('module-equalizer-sink', args)
	
	
	def unload_dyn_equalizer(self):
		if self.dyn_equalizer != None:
			index = self.padb.sinks[self.dyn_equalizer].owner_module
			self.dyn_equalizer = None
			self.pc.unload_module(index)

	#
	#	helper
	#

	def get_sink_info(self, sink):
		try:
			return "%s  %s %s %s" % (sink.name, sink.sample_spec["format"], sink.sample_spec["rate"], sink.sample_spec["channels"])
		except: return sink.name


			
			