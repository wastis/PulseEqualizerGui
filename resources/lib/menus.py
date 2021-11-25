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

import os, json
import xbmc
import xbmcgui
from xbmcaddon import Addon
from helper import *
from time import sleep
from volumegui import VolumeGui

addon = Addon()
def tr(id):
	return addon.getLocalizedString(id)

class Menu():
	
	skin = "Default"
	
	def __init__(self, cwd):
		self.cwd = cwd
			
	
	#
	#	Menu selectors
	#
	
	def sel_main_menu(self, menu=False):
		
		sel = xbmcgui.Dialog().contextmenu([tr(32006),tr(32007),tr(32008),tr(32009),tr(32010)])
		
		if sel > -1:
			func = ["profile","equalizer","device","manager","latency"]
			self.sel_menu(func[sel],True)

	def sel_menu(self, command, smenu = False):
		
		func = 'sel_' + command
		try: method = getattr(self, func)
		except:	
			method = None
			logerror("unkonwn command: '%s'" %(func))
	
		if method: method(smenu)
	
	#
	#  helper
	#

	
	def check_func_available(self):
		self.current = SocketCom("server").call_func("get","eq_current") 
		eqid, desc, is_playing, eq_profile, is_dyn = ( self.current )
		
		if is_playing and eq_profile=='off' and is_dyn:
			# Dialog switch on?
			if not xbmcgui.Dialog().yesno(tr(32000), tr(32003)):
				return False, eqid, desc, is_playing, eq_profile, is_dyn
			else:
				SocketCom("server").call_func("switch","eq_on") 

				count = 10
				while count > 0:
					count = count - 1
					self.current = SocketCom("server").call_func("get","eq_current")
					eqid, desc, is_playing, eq_profile, is_dyn = ( self.current )
					if eqid != None: return True , eqid, desc, is_playing, eq_profile, is_dyn
					sleep(0.1)
			# Dialog problem switch on
			xbmcgui.Dialog().ok(tr(32004),tr(32005))
			return False, eqid, desc, is_playing, eq_profile, is_dyn
		# all ok
		return True, eqid, desc, is_playing, eq_profile, is_dyn
	
	
	#
	#	different Menues
	#
	
	#
	#	select profile
	#
	
	
	def sel_profile(self, smenu=False):
		
		func_available, eqid, desc, is_playing, eq_profile, is_dyn =  self.check_func_available()
		if not func_available: return
		
		include_switch_off = is_dyn and is_playing

		profiles = SocketCom("server").call_func("get","eq_profiles")
		profile = SocketCom("server").call_func("get","eq_base_profile", [eqid])			
		
		if include_switch_off: profiles = [tr(32011)] + profiles
		
		try: sel = profiles.index(profile)
		except:	sel = -1
		
		nsel = xbmcgui.Dialog().select(tr(32012) %(desc),profiles,preselect = sel)

		if nsel > -1 and sel != nsel:
			if include_switch_off and nsel == 0: 
					SocketCom("server").call_func("switch","eq_off")
					return
				
			SocketCom("server").call_func("load","eq_profile" , [eqid, profiles[nsel]])
	#
	#	configure equalizer
	#
	
	def sel_equalizer(self, menu=False):
		
		func_available, eqid, desc, is_playing, eq_profile, is_dyn =  self.check_func_available()
		if not func_available: return

		from eqgui import EqGui
		
		ui = EqGui("equalizer.xml" , self.cwd, self.skin , eqid=eqid, desc=desc)
		ui.doModal()
		del ui
	
	#
	#	select output device
	#
	
	def sel_device(self, smenu=False):
		 
		response = xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.GetSettings", "params":{ "filter": {"section":"system", "category":"audio"}}, "id":1}')
		r_dict = json.loads( response )

		settings = r_dict["result"]["settings"]
		for s in settings:
			if s["id"] == "audiooutput.audiodevice":
				
				value = s["value"]
				options = s["options"]
				
				sel_lables = []
				sel_values = []
				preselect = 0
				index = 0
				for o in options:
					
					if "eq-auto-load" in o["value"]: continue
					
					if o["value"] == value:
						preselect = index
					
					sel_values.append(o["value"])
					sel_lables.append(o["label"])
					index = index + 1
		
		# device selection Dialog
		sel = xbmcgui.Dialog().select(tr(32013) ,sel_lables,preselect = preselect)
		
		if sel > -1:
			response = xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"audiooutput.audiodevice", "value":"%s"}, "id":1}' %(sel_values[sel]))
			SocketCom("server").call_func("set","device" , [sel_values[sel]])

	#
	#	profile manager menu
	#
	
	
	def sel_manager(self, smenu=False):

		func_available, eqid, desc, is_playing, eq_profile, is_dyn =  self.check_func_available()
		if not func_available: return

		# Dialog Add_Profile, Delete_Profile, New_Profile, Noise Generator
		sel = xbmcgui.Dialog().contextmenu([tr(32014),tr(32015),tr(32016)])
		if sel == 0:
			# Name for new Profile
			profile = xbmcgui.Dialog().input(tr(32017))
			if profile != '':
				SocketCom("server").call_func("save","eq_profile" , [eqid,profile])
				
				
		elif sel == 1:
			profiles = SocketCom("server").call_func("get","eq_profiles")
			
			if len(profiles) > 0:
				#select profile
				sel_del_profile = xbmcgui.Dialog().contextmenu(profiles)
				if sel_del_profile > -1:
					# sure to delete
					del_profile = profiles[sel_del_profile]
					if xbmcgui.Dialog().yesno(tr(32018) % del_profile,tr(32019) % del_profile) == True:
						SocketCom("server").call_func("remove","eq_profile" , [del_profile])
					
					
			else: 
				#does not exist
				xbmcgui.Dialog().notification(tr(32020),tr(32021), time = 10)

		elif sel == 2:
			# load predefined
			SocketCom("server").call_func("set","eq_default_profile" , [eqid])
			
			

	#
	#	show latency slider
	#
			
	def sel_latency(self, smenu=False):
		
		from latencygui import LatencyGui
		if smenu: 
			xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Input.ExecuteAction", "params": {"action":"fullscreen"}, "id":1}')
		ui = LatencyGui("latency-offset.xml" , self.cwd, self.skin)
		ui.doModal()
		del ui
		
	#
	#	show volume progress bar
	#
		
	def sel_volup(self, smenu=False):
		self.volgui = VolumeGui("volume.xml" , self.cwd , self.skin, updown = "up")
		self.volgui.doModal()
		
	def sel_voldown(self, smenu=False):
		self.volgui = VolumeGui("volume.xml" , self.cwd , self.skin, updown = "down")
		self.volgui.doModal()


