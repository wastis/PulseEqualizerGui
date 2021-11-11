#
#	pulse audio gui addon for kodi
#	2021 by wastis
#
#    ------------------     ------------        -------------      ---------------
#    | MessageCentral | --> | dispatch | ->|<-> | paDatabase| <--> | pulse audio | 
#    ------------------ |   ------------   |    -------------      ---------------
#                       |                  |    --------
#                       |                  |--> | self |
#                       |                  |    -------- 
#         ----------    |                  |    -------------       --------      ---------------- 
#     --->| update | -->|                  |--> 1| EqControl |  <--> | dbus | <--> | pa equalizer |
#         ---------                        |    -------------       --------      ----------------
#                                          |    -------------------      ---------------             
#                                          |--> | paModuleManager | --> | pulse audio |              
#                                               -------------------      ---------------             
#                                                             
# dispatch: send pa-messages to paDatabase, collect them
#           non pa-messages, such the ones from user interface, are sent to the other modules
# update:   comes 100ms after the last pa-message, triggers the processing of the previoues pa-messages
#           paDatabase caches pulse audio configuration and generates aggregated messages, that are sent to the other modules
# self:     handels some specific requests, such as latency set/get, etc
# EqControl interface to the current equalizer, mainly called on client requests, such ad get_profile/ set_profile, etc
# paModuleManager: reconfigures the playback stream dependend on current configuration and connected devices and playback status


from threading import Thread
from .pulsecontrol import PulseControl
from .pamodule import paModuleManager
from .padb import paDatabase
from .eqcontrol import EqControl
from helper import *

import json, os


class MessageCentral():
	def __init__(self, pipe_com):
		# init class structure

		self.pipe_com = pipe_com
		
		self.pc = PulseControl()
		self.eq = EqControl()
		self.config = Config()

		self.padb = paDatabase(self.pc)
		self.pamm = paModuleManager(self.pc, self.eq, self.padb, self.config)
		
	#	
	#	start message, called if pulse audio gets connected
	#
	
	def on_pulse_connect(self):
		log("start pulse control")
		self.pc.start()
		self.padb.on_pa_connect()
		self.pamm.on_pa_connect()

	#
	# Dispatch messages
	#
	

	def on_message(self, target, func, arg):
		#print("on_%s_%s"% (target,func))
		try:
			if self.padb.on_message(target, func, arg): return
			
			# other messages are just forwarded
			
			cmd = "on_" + target + "_" + func
			methods = []
			
			for cl in [self.padb, self, self.pamm, self.eq]:
				try:methods.append( getattr(cl,cmd))
				except: pass 

			if len(methods) == 0:
				#log("no message handler for " + cmd)
				return

			for method in methods:
				result = method(*arg)
				if not result is None:
					self.pipe_com.send("client",json.dumps(result))

		except Exception as e: handle(e)
			
	#
	#	message collector, just collect fast incomeing messages from pulse audio
	#	handle them after a timeout 
	#
				
	
	def on_pa_update(self):
		log("on_pa_update")

		messages = self.padb.do_update()


		
		#print(self.padb.playback_stream)
		
		for message,arg in messages:
			try:
				method = getattr(self.pamm, message)
			except:	continue
			method(*arg)
			
		self.pamm.do_update()
		log(str(self.padb))
	
		
	#	
	#	message handler of self	
	#

		
	def on_introspect_get(self):
		
		result = []
		for cl in [MessageCentral, paModuleManager, EqControl]:
			for l in vars(cl):
				if l.startswith("on_"):
					findex = l.rfind("_")
					result.append(l[findex+1:]+";"+l[3:findex])
		return result
		
	def on_outlist_get(self):
		return self.padb.get_outlist() 
	
	def on_latency_get(self):
		return self.padb.get_latency() 
		
	def on_latency_set(self,latency_info):
		self.pc.set_port_latency(latency_info)
		
		if self.padb.output_sink:
			if self.padb.cureq_sink:
				self.config.set("eq_latency", int(latency_info["latency"]),self.padb.output_sink.name)
			else:
				self.config.set("latency", int(latency_info["latency"]),self.padb.output_sink.name)

	# just save the current selected profile
	def on_eq_profile_load(self,index, profile):
		if self.padb.output_sink:
			self.config.set("eq_profile", profile,self.padb.output_sink.name)
	
	# helper	
	def on_pa_module_log(self):
		for key,val in vars(self.pamm).items():
			log(key+"="+ str(val))

	
	

			
