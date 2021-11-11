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
	
	def __init__(self, cwd):
		self.pipe_comm = PipeCom("/run/shm/pa")
		self.cwd = cwd

	def get_sel_handler(self):

		result = []
		for func in vars(Menu):
			if func.startswith('sel'): result.append(func)
		return result

	def is_eq_availabe(self, display = True):
		
		self.current = self.pipe_comm.get_from_server("get;eq_current")
		eqid, desc, is_playing, eq_profile, is_dyn = ( self.current )
		
		if not is_playing:
		
			xbmcgui.Dialog().ok(tr(32001), tr(32002))
			return False
			
		if eqid is None:
			if eq_profile == "off":
				if not xbmcgui.Dialog().yesno(tr(32000), tr(32003)): 
					return False
				else:
					self.pipe_comm.send_to_server("switch;eq_on")

					count = 10
					while count > 0:
						count = count - 1
						self.current = self.pipe_comm.get_from_server("get;eq_current")
						eqid, desc, is_playing, eq_profile, is_dyn = ( self.current )
						if eqid != None: return True
						sleep(0.1)
			
			xbmcgui.Dialog().ok(tr(32004),tr(32005))
			return False
			
		return True
		_
			
	
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
		if func in self.get_sel_handler():
			log(func) 
			getattr(self, func)(smenu)
		else: 
			logerror("unkonwn command: '%s'" %(command))
	
	
	#
	#	different Menues
	#
	
	
	def sel_profile(self, smenu=False):
		
		
		if not self.is_eq_availabe(): return
		eqid, desc, is_playing, eq_profile, is_dyn = (self.current)
		
		profiles = self.pipe_comm.get_from_server("get;eq_profiles")
		profile = self.pipe_comm.get_from_server("get;eq_base_profile;%d" % (eqid))
		
		if is_dyn: profiles = [tr(32011)] + profiles
		
		try: sel = profiles.index(profile)
		except:	sel = -1
		
		nsel = xbmcgui.Dialog().select(tr(32012) %(desc),profiles,preselect = sel)

		if nsel > -1 and sel != nsel:
			if is_dyn and nsel == 0: 
					self.pipe_comm.send_to_server("switch;eq_off")
					return
				
			self.pipe_comm.send_to_server("load;eq_profile;%d,%s" % (eqid,profiles[nsel]))
		
	def sel_equalizer(self, menu=False):
		
		if not self.is_eq_availabe(): return
		eqid, desc, is_playing, eq_profile, is_dyn = (self.current)
		
		from eqgui import EqGui
		
		ui = EqGui("equalizer.xml" , self.cwd, "Default", pipe_comm=self.pipe_comm, eqid=eqid, desc=desc)
		ui.doModal()
		del ui
	
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
		
		sel = xbmcgui.Dialog().select(tr(32013) ,sel_lables,preselect = preselect)
		
		if sel > -1:
			response = xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"audiooutput.audiodevice", "value":"%s"}, "id":1}' %(sel_values[sel]))
			self.pipe_comm.send_to_server("set;device;%s" % (sel_values[sel]))

	def sel_manager(self, smenu=False):

		if not self.is_eq_availabe(): return
		eqid, desc, is_playing, eq_profile, is_dyn = (self.current)

		sel = xbmcgui.Dialog().contextmenu([tr(32014),tr(32015),tr(32016)])
		if sel == 0:
			profile = xbmcgui.Dialog().input(tr(32017))
			if profile != '':
				self.pipe_comm.send_to_server("save;eq_profile;%d,%s" % (eqid,profile))
				
				
		elif sel == 1:
			profiles = self.pipe_comm.get_from_server("get;eq_profiles")

			if len(profiles) > 0:
				del_profile = profiles[xbmcgui.Dialog().contextmenu(profiles)]
				if xbmcgui.Dialog().yesno(tr(32018) % del_profile,tr(32019) % del_profile) == True:
					self.pipe_comm.send_to_server("remove;eq_profile;%s" % (del_profile))
					
			else: xbmcgui.Dialog().notification(tr(32020),tr(32021), time = 10)

		elif sel == 2:
			self.pipe_comm.send_to_server("set;eq_default_profile;%d" % (eqid))
			
	def sel_latency(self, smenu=False):
		
		from latencygui import LatencyGui
		if smenu: 
			xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Input.ExecuteAction", "params": {"action":"fullscreen"}, "id":1}')
		ui = LatencyGui("latency-offset.xml" , self.cwd, "Default", pipe_comm=self.pipe_comm)
		ui.doModal()
		del ui
		
	def sel_volup(self, smenu=False):
		self.volgui = VolumeGui("volume.xml" , self.cwd , "Default", updown = "up", pipe_comm=self.pipe_comm)
		self.volgui.doModal()
		
	def sel_voldown(self, smenu=False):
		self.volgui = VolumeGui("volume.xml" , self.cwd , "Default", updown = "down", pipe_comm=self.pipe_comm)
		self.volgui.doModal()


