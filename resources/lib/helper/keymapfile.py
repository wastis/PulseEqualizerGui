#	This file is part of PulseEqualizerGui for Kodi.
#
#	Copyright (C) 2022 wastis    https://github.com/wastis/PulseEqualizerGui
#
#	PulseEqualizerGui is free software; you can redistribute it and/or modify
#	it under the terms of the GNU Lesser General Public License as published
#	by the Free Software Foundation; either version 3 of the License,
#	or (at your option) any later version.
#
#

import os
import re

from basic import path_kodi
from basic import path_keymap
from basic import handle

class KeyMapFile():
	struc_templ = {
	"menu":{"id":0, "name":37000, "eq":True, "in":["global","fullscreenvideo","fullscreenradio","fullscreenlivetv", "visualisation"], "key":0, "step":1},
	"profile":{"id":1, "name":37001, "eq":True, "in":["global","fullscreenvideo","fullscreenradio","fullscreenlivetv", "visualisation"], "key":0, "step":1},
	"equalizer":{"id":2, "name":37002, "eq":True, "in":["global","fullscreenvideo","fullscreenradio","fullscreenlivetv", "visualisation"], "key":0, "step":1},
	"device":{"id":3, "name":37003, "eq":True, "in":["global","fullscreenvideo","fullscreenradio","fullscreenlivetv", "visualisation"], "key":0, "step":1},
	"correction":{"id":4, "name":37004, "eq":True, "in":["global","fullscreenvideo","fullscreenradio","fullscreenlivetv", "visualisation"], "key":0, "step":1},
	"latency":{"id":5, "name":37005, "eq":True, "in":["global","fullscreenvideo","fullscreenradio","fullscreenlivetv", "visualisation"], "key":0, "step":1},
	"CodecInfo":{"id":6, "name":37006, "eq":False, "in":["fullscreenvideo","fullscreenradio","fullscreenlivetv", "visualisation"], "key":0, "step":1},
	"PlayPause":{"id":7, "name":37007, "eq":False, "in":["global","fullscreenvideo","fullscreenradio","fullscreenlivetv", "visualisation"], "key":0, "step":1},
	"FullScreen":{"id":8, "name":37008, "eq":False, "in":["global"], "key":0, "step":1},
	"ContextMenu":{"id":9, "name":37009, "eq":False, "in":["global","fullscreenvideo","fullscreenradio","fullscreenlivetv", "visualisation"], "key":0, "step":1},
	"Powerdown":{"id":10, "name":37010, "eq":False, "in":["global","fullscreenvideo","fullscreenradio","fullscreenlivetv", "visualisation"], "key":0, "step":1},
	"Reboot":{"id":11, "name":37011, "eq":False, "in":["global","fullscreenvideo","fullscreenradio","fullscreenlivetv", "visualisation"], "key":0, "step":1},
	"Suspend":{"id":12, "name":37012, "eq":False, "in":["global","fullscreenvideo","fullscreenradio","fullscreenlivetv", "visualisation"], "key":0, "step":1},
	"Quit":{"id":13, "name":37013, "eq":False, "in":["global","fullscreenvideo","fullscreenradio","fullscreenlivetv", "visualisation"], "key":0, "step":1},
	"AlarmClock('stop',Action(Stop))":{"id":14, "name":37014, "eq":False, "in":["global","fullscreenvideo","fullscreenradio","fullscreenlivetv", "visualisation"], "key":0, "step":1},
	"Screenshot":{"id":15, "name":37015, "eq":False, "in":["global","fullscreenvideo","fullscreenradio","fullscreenlivetv", "visualisation"], "key":0, "step":1},
	"volup":{"id":16, "name":37016, "eq":True, "in":["fullscreenvideo","fullscreenradio","fullscreenlivetv", "visualisation"], "key":0, "step":5},
	"voldown":{"id":17, "name":37017, "eq":True, "in":["fullscreenvideo","fullscreenradio","fullscreenlivetv", "visualisation"], "key":0, "step":5},
	"Info":{"id":18, "name":37018, "eq":False, "in":["global","fullscreenvideo","fullscreenradio","fullscreenlivetv", "visualisation"], "key":0, "step":1},
	"ShowSubtitles":{"id":19, "name":37019, "eq":False, "in":["fullscreenvideo","fullscreenradio","fullscreenlivetv", "visualisation"], "key":0, "step":1},
	"AspectRatio":{"id":20, "name":37020, "eq":False, "in":["fullscreenvideo","fullscreenradio","fullscreenlivetv", "visualisation"], "key":0, "step":1},
	"AudioNextLanguage":{"id":21, "name":37021, "eq":False, "in":["fullscreenvideo","fullscreenradio","fullscreenlivetv", "visualisation"], "key":0, "step":1},
	"SkipNext":{"id":22, "name":37022, "eq":False, "in":["fullscreenvideo","fullscreenradio","fullscreenlivetv", "visualisation"], "key":0, "step":1},
	"SkipPrevious":{"id":23, "name":37023, "eq":False, "in":["fullscreenvideo","fullscreenradio","fullscreenlivetv", "visualisation"], "key":0, "step":1}
	}

	sec_list = ["global","fullscreenvideo","fullscreenradio","seekbar","fullscreenlivetv", "visualisation"]

	def __init__(self, file_name = "zEqualizer.xml"):
		self.file_name = path_kodi + path_keymap + file_name

		self.struct = self.struc_templ
		self.index = {}
		self.sec = {}

		for key, val in self.struc_templ.items():
			self.index[val["id"]]=key
			for s in val["in"]:
				if s in self.sec: self.sec[s] = self.sec[s] + [key]
				else: self.sec[s] = [key]

	def parse_keymap_file(self):
		struct = self.struc_templ
		self.struct = struct

		if not os.path.exists(self.file_name):
			return

		with open(self.file_name) as f: content=f.read()

		for key,func in re.findall('<key\s+id="([0-9]*?)">(.*?)</key>',content,re.DOTALL):
			step = None
			if "script.pulseequalizer.gui" in func:
				sub = re.findall("gui,(.*?)\)", func,re.DOTALL)[0].split(',')
				if sub == []: sub = ["main","1"]

				try:
					val = int(sub[0])
					sub = ["main",val]
				except ValueError: pass

				func = sub[0]
				try: step = int(sub[1])
				except IndexError: step = 1
				except ValueError: step = 1

			if func in struct:
				struct[func]["key"] = key
				struct[func]["step"] = step

		self.struct = struct

	def create_xml(self):
		templ_keymap = "<keymap>\n{}\n</keymap>"
		templ_sec = '\t<{}>\n\t\t<keyboard>\n{}\t\t</keyboard>\n\t</{}>\n\n'
		templ_key = '\t\t\t<key id="{}">{}</key>\n'
		templ_eq  = 'RunScript(script.pulseequalizer.gui,{},{})'

		xml_result = ""
		for sec_name in self.sec_list:
			if sec_name not in self.sec: continue
			func_result = ""
			for func_name in self.sec[sec_name]:
				vals = self.struct[func_name]
				if vals["key"]== 0: continue
				if vals["eq"]: func_name = templ_eq.format(func_name,vals["step"])

				func_result = func_result + templ_key.format(vals["key"],func_name)

			if func_result != "":
				xml_result = xml_result + templ_sec.format(sec_name,func_result,sec_name)

		if xml_result: xml_result = templ_keymap.format(xml_result)
		return xml_result

	def save(self):
		try:
			xml = self.create_xml()
			if xml != "":
				with open(self.file_name, "w") as f: f.write(xml)
			else:
				os.remove(self.file_name)
		except OSError: pass
		except Exception as e: handle(e)

	def get_info(self,name):
		try:
			return self.struct[name]
		except KeyError: return ""

	def set_info(self,name,key,step=1):
		try:
			self.struct[name]["key"]=key
		except KeyError: return

