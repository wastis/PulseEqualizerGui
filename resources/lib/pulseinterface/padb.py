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
#   paDatabase is a information repository, that follows the pulseaudio system configuration
#   by catching and handling the pulseaudio system messages
#     - apply some logic to set flags (e.g. pulseaudio-equalizer loaded)
#     - cache current pulse audio system configuration e.g sinks, sink-inputs cards, modules
#     - create a lookup index for those objects
#     - find certain information, e.g who is the current kodi client, kodi-stream ...
#     - aggregate pulse-audio messages, as messages arrive to fast for individual handling,
#         python iterpreter is to slow for heavy message handling
#         it may happen that a sink_input is created and immidiately destroyed by kodi or pulseaudio.
#         it does not exsits anymore by the time the create message arrives here.
#

import os

from .collector import MessageCollector

from helper import SocketCom

from basic import handle
from basic import opthandle
from basic import log

class paDatabase():
	target_list = ["card","module","sink","client","sink_input"]
	attributes = ["kodi_client", "kodi_stream", "kodi_first_sink", "kodi_is_dynamic", "autoeq_sink", "autoeq_stream", "removable_sink", "chaineq_sink", "cureq_sink", "default_sink"]
	attr_keep = ["kodi_first_sink", "kodi_is_dynamic", "removable_sink", "chaineq_sink", "cureq_sink", "default_sink"]
	lookups = ["sink_by_name", "sink_by_module", "stream_by_module"]

	playback_stream = None
	output_sink = None
	default_sink = None

	def __init__(self, pulsecontrol, config):
		self.pc = pulsecontrol
		self.mc = MessageCollector()
		self.config = config

		for attr in self.attributes: setattr(self, attr, None)
		for attr in self.lookups: setattr(self, attr, None)

	#
	# helper to support debugging
	#

	def __str__(self):
		sl = []
		try:
			if self.playback_stream is not None:
				for stream, sink in self.playback_stream: sl.append("%s(%d) -> %s(%d)" % (stream.name,stream.index,sink.name,sink.index))
		except AttributeError:
			pass

		r = "{"
		for attr,val in self:
			r = r + " ( %s=%s ) " % (attr,repr(val))
		r = r + "}"
		return  r + "\nPlayback: " + " -> ".join(sl)
		#return  r

	def __iter__(self):
		for attr in self.attributes + ["output_sink"]:
			val = getattr(self, attr)
			try:  val=val.name
			except AttributeError: pass
			except Exception as e: opthandle(e)
			yield (attr, val)

	def get_objects(self):
		lines = []
		for target in self.target_list:
			try: li = getattr(self,target + "s")
			except Exception: continue
			lines.append("\n%ss:" % target)
			for index, obj in list(li.items()): lines.append("\t%d %s\n" % (index, obj.name) )

		return " ".join(lines)

	#
	#	on_pa_connect is been called if message service is connected to pulse audio, usually only once at start of the script.
	#

	# initiate data structures and collect all required information from pulse audio, such as sinks, cards, streams etc.
	# try to find kodi stream and all elements included
	# try to find the auto-loaded equalizer

	def on_init(self):
		log("padb: on_init")
		self.mc = MessageCollector()

		for attr in self.attributes: setattr(self, attr, None)

		for target in self.target_list:
			setattr(self, target + "s", {})
			self.get_pa_object_list(target)

	def on_pa_connect(self):
		log("padb: on_pa_connect")

		self.update_kodi_info()
		self.info["removable_sink"]=None
		self.proc_device()

	# get the current list of objects (sinks, cards...) from pulse audio an create a lookup dictionary by index
	# this is stored in self. e.g self.sinks, self.cards and has the format e.g. {0:sink, 1:sink ....}
	# this is only done once every time the message service connects to pulseaudio
	def get_pa_object_list(self,target):
		log("padb: get objects %s" % target)
		targets = target + "s"
		result = {}
		for obj in self.pc.get_list(target):
			result[obj.index] = obj
		setattr(self, targets, result)

	#
	#	fill kodi info, collect certain information like kodi-stream, kodi-first sink, autoloaded-equalizer etc.
	#
	def get_default_sink(self):
		sysname = self.pc.get_server_info().default_sink_name
		name = self.config.get("default_sink",sysname,"global")
		if name in self.sink_by_name.keys():
			return self.sink_by_name[name]
		elif sysname in self.sink_by_name.keys():
			return self.sink_by_name[sysname]
		else:
			return None

	def update_kodi_info(self):
		log("padb: update_kodi_info")
		self.info = {}
		for key in self.attributes: self.info[key] = None
		self.get_kodi_client()
		self.parse_sink_inputs()
		self.parse_sinks()
		self.info["default_sink"] = self.get_default_sink()

	def get_kodi_client(self):
		pid = str(os.getgid())
		for cid,client in list(self.clients.items()):
			if client.name in ['Kodi', 'KodiSink'] and client.proplist['application.process.id']==pid:
				self.info["kodi_client"] = cid
				return

			if client.name.startswith("ALSA plug-in") and client.proplist['application.process.id']==pid:
				self.info["kodi_client"] = cid
				return

		#no kodi client with pid matching myself, I might be the develop script, so pick first kodi
		for cid,client in list(self.clients.items()):
			if client.name in ['Kodi','KodiSink']:
				self.info['kodi_client'] = cid
				return

			if client.name.startswith("ALSA plug-in"):
				self.info["kodi_client"] = cid
				return

	def parse_sink_inputs(self):
		self.stream_by_module = {}

		for _, si in list(self.sink_inputs.items()):
			try:
				self.stream_by_module[si.owner_module] = si
			except Exception: print(self.sink_inputs)

			if si.client == self.info['kodi_client']:
				if self.info['kodi_stream'] is None:  self.info['kodi_stream'] = si

	def parse_sinks(self):
		self.sink_by_name = {}
		self.sink_by_module = {}

		for _, sink in list(self.sinks.items()):
			self.sink_by_name[sink.name] = sink
			self.sink_by_module[sink.owner_module] = sink

			if sink.name == "eq-auto-load":
				self.info["autoeq_sink"] = sink
				self.info["autoeq_stream"] = self.stream_by_module[sink.owner_module]

		self.default_sink = self.get_default_sink()

	def set_kodi_chain_sink(self, sink):
		sink_input = self.info["kodi_stream"]
		log("padb: set_kodi_chain @ sink: "+ sink.name)
		self.info["kodi_first_sink"] = sink
		self.info["kodi_is_dynamic"] = sink.proplist["device.class"] == "sound"

		self.playback_stream = [(sink_input, sink)]
		self.info["chaineq_sink"] = None

		while True:
			try:
				if sink.driver == "module-equalizer-sink.c":
					self.info["chaineq_sink"] = sink

				sink_input = self.stream_by_module[sink.owner_module]
				sink = self.sink_by_name[sink.proplist["device.master_device"]]
				self.playback_stream.append((sink_input, sink))
			except Exception: break

		self.info["output_sink"] = sink

	def set_kodi_chain(self, sink_input, keep = False):
		if self.removable_sink is None:
			if keep and self.kodi_first_sink is not None:
				self.set_kodi_chain_sink(self.kodi_first_sink)
			else:
				self.set_kodi_chain_sink(self.sinks[sink_input.sink])
		else:
			self.set_kodi_chain_sink(self.removable_sink)

	def is_dynamic(self):
		return self.kodi_is_dynamic or (self.removable_sink is not None)

	#
	#	after information gathering from pulseaudio, create attributs in self and collect changes to create change messages
	#

	def update_attr(self):
		updates = []
		for key, val in list(self.info.items()):
			if key in self.attr_keep and val is None: continue
			if val == "force_none": val = None

			old_val = getattr(self,key)
			setattr(self,key,val)

			try: ov = old_val.index
			except Exception: ov = old_val
			try: nv = val.index
			except Exception: nv = val

			if ov != nv:
				log("padb: on_%s_update" % key)
				updates.append(("on_%s_update" % key,[old_val, val]))

		return updates

	#
	# message handling, messages arriving here come from self and are already aggregated
	#

	def on_sink_input_new(self, index):
		log("padb: on_sink_input_new %d" % index)

		if self.info['kodi_stream'] is not None:
			if index == self.info['kodi_stream'].index:
				device = self.get_kodi_device()
				self.set_kodi_chain(self.info['kodi_stream'], device == "Default")

	def on_sink_new(self, index):
		sink = self.sinks[index]
		log("padb: on_sink_new %s" % sink.name)

		if "device.bus" in sink.proplist and \
		sink.proplist["device.bus"] in ['bluetooth','usb'] :
			self.info["removable_sink"] = sink
			self.set_kodi_chain_sink(sink)

	def on_sink_remove(self, index):
		log("padb: on_sink_remove %d" % index)
		if self.removable_sink is not None:
			if index == self.removable_sink.index:
				self.info["removable_sink"] = "force_none"

		if self.kodi_first_sink.index == index:
			log("padb: active sink removed: %s" % self.kodi_first_sink.name)

			sink = self.get_default_sink()

			self.set_kodi_chain_sink(sink)

	#
	#	special messages from kodi player, we need to know the selected sink in kodi
	#

	def get_kodi_device(self):
		sock = SocketCom("kodi")
		try:
			device = sock.call_func("get","device")[0]
		except TypeError:
			device = "Default"

		if not device or device.startswith("ALSA:"):
			device = "Default"

		return device

	def proc_device(self):
		self.output_sink = None
		self.proc_device_set(self.get_kodi_device())

	@staticmethod
	def extract_device_name(name):
		if name.startswith("PULSE:"):
			return name[6:]
		elif name.startswith("ALSA:"):
			return name[5:]
		return name

	def proc_device_set(self,arg):
		arg = self.extract_device_name(arg)

		if arg == 'Default':
			self.default_sink = self.get_default_sink()
			if not self.default_sink:
				log("padb: on_device_set: default sink not found")
				return

			log("padb: on_device_set: default sink found")

			sink = self.default_sink
		else:
			try:
				sink = self.sink_by_name[arg]
				log("padb: on_device_set: device found")
			except Exception:
				log("padb: on_device_set: device not found")
				return

		self.set_kodi_chain_sink(sink)
		self.update_attr()

	def on_device_set(self,arg):
		self.removable_sink = None
		self.proc_device_set(arg)

	def on_kodidefault_get(self):
		return self.get_default_sink().name

	def on_kodidefault_set(self, name):
		try:
			# set default sink for playback
			name = self.extract_device_name(name)
			sink = self.sink_by_name[name]
			self.config.set("default_sink",name,"global")
			self.default_sink = sink
			self.info["default_sink"] = sink

			log("padb: set kodi default sink to: %s" % sink.name)

		except KeyError:
			log("padb: set default error, cannot find sink: %s" % name)
			pass

	def on_systemdefault_get(self):
		try:
			return self.pc.get_server_info().default_sink_name
		except Exception as e:
			handle(e)
			return None

	def on_systemdefault_set(self, name):
		try:
			name = self.extract_device_name(name)
			sink = self.sink_by_name[name]
			self.pc.set_default_sink(sink)
			log("padb: set system default sink to: %s" % sink.name)
		except KeyError:
			log("padb: set default error, cannot find sink: %s" % name)
			pass

	def on_device_get(self):
		if self.kodi_first_sink is None:
			return "Default"
		return self.kodi_first_sink.name

	def on_sinks_get(self):
		result = []
		for _, sink in list(self.sinks.items()):
			if sink.name != "eq-auto-load":
				result.append((sink.description,sink.name))
		return result

	def on_soundsinks_get(self):
		result = []
		for _, sink in list(self.sinks.items()):
			try:
				if sink.proplist["device.class"] == "sound":
					result.append((sink.description,sink.name))
			except IndexError:
				continue
		return result

	#
	#  all messages arrive here, filter the ones from pulseaudio and collect them for later aggregation
	#

	def on_message(self,target,func,arg):
		if target not in self.target_list: return False
		#log("padb: re: on_%s_%s %s" % (target, func, arg))

		self.mc.collect_message(target,func,*arg)
		return True

	#
	#	update changes to the object dictionaries, (add, remove or change)
	#

	def update_objects(self):
		for target, func_list in list(self.mc.msg_collector.items()):
			targets = target + "s"
			try: obj_list = getattr(self,targets)
			except Exception: obj_list = {}

			try:
				for index in func_list["remove"]:
					try: del obj_list[index]
					except KeyError: pass
			except KeyError: pass

			for func in ["new", "change"]:
				try:
					for index in func_list[func]:
						obj = self.pc.get_info(target , index)
						if obj is not None:	obj_list[index] = obj
				except KeyError: pass

			setattr(self, targets,obj_list)

	#
	#	this function is called 100ms after the last message from pulseaudio
	#
	#	this will update local dictionary with information from pulseaudio base on the previouse pa messages
	#	futher collect the additional information like who is the kodi stream, now
	#	then it will create messages for changes in the additional information

	def do_update(self):
		self.update_objects()
		self.update_kodi_info()
		msg_list = self.mc.get_messages_and_clear()

		for cmd,arg in msg_list:
			#log("padb: co: %s %s" % (cmd,*arg))
			try:
				method = None
				try: method = getattr(self,cmd)
				except AttributeError: pass
				except Exception as e: opthandle(e)

				if method: method(*arg)
			except Exception as e: handle(e)

		msg_list = self.update_attr() + msg_list

		#log("padb: {}".format(str(self)))

		return msg_list

	#
	# respond to info requests coming from client
	#

	def get_latency(self):
		if self.output_sink  is None: return {"latency":0,"port":"", "card":""}

		port_name = self.output_sink.port_active.name
		card = self.cards[self.output_sink.card]
		latency = 0

		for p in card.port_list:
			if p.name == port_name:
				latency = int(p.latency_offset)

		return  {"latency":latency,"port":port_name, "card": card.name}

	def on_eq_autoload_get(self):
		try: return self.autoeq_sink.index
		except Exception: return None

	def on_all_eq_get(self):
		result = {}

		for index, sink in list(self.sinks.items()):
			if sink.driver != "module-equalizer-sink.c": continue

			result[index]= [
				sink.name,
				sink.proplist["device.description"],
				sink.sample_spec["rate"],
				sink.channel_list,
				sink.channel_list_raw,
				sink.volume.values
				]

		return result

	def on_eq_channel_get(self):
		sink = self.chaineq_sink if self.chaineq_sink is not None else self.autoeq_sink
		if sink is None: return None
		return [sink.index, sink.proplist["device.description"] , sink.channel_list]
