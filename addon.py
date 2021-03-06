import xbmc
import xbmcaddon
import xbmcgui
import sys, os

addon	  = xbmcaddon.Addon()
addonname  = addon.getAddonInfo('name')
addonid    = addon.getAddonInfo('id')
cwd		= addon.getAddonInfo('path')

if sys.version_info[0] > 2:
	import xbmcvfs
	lib_path   = xbmcvfs.translatePath( os.path.join( cwd, 'resources', 'lib' ))
	gui_path   = xbmcvfs.translatePath( os.path.join( cwd, 'resources', 'gui' ))
else:
	lib_path   = xbmc.translatePath( os.path.join( cwd, 'resources', 'lib' )).decode("utf-8")

sys.path.append (lib_path)
from gui import GUI
from pulse_class import FILTER
from pulse_class import STREAM_FUNC
import pulseerror

def handle_except(e):
	if e.args[0] == "no stream available":
		xbmcgui.Dialog().notification("No stream availabe", "please play something", time = 10)
	elif e.args[0] == "no equalizer in filter chain":
		xbmcgui.Dialog().notification("No equalizer in filter chain", "select a chain with equalizer", time = 10)
	else: 
		xbmc.log(str(e),xbmc.LOGERROR)



try:
	dialog = xbmcgui.Dialog()

	if len(sys.argv) == 1:
		sel = dialog.contextmenu(["Select Profile","Equalizer","Select Output Device","Manage Profiles"])
	else:
		sel = ["profile","equalizer","device","manager"].index(sys.argv[1])
		
		

	if sel == 0:
		try: f = FILTER()
		except Exception as e: handle_except(e)
		else:
			
			profile_list = f.get_profile_list()
			if len(profile_list) > 0:
				sel = dialog.contextmenu(profile_list)
				f.load_profile(profile_list[sel])
			else: xbmcgui.Dialog().notification("Select Profile", "No profiles defined!", time = 10)

	elif sel == 1:

		try: ui = GUI("%s.xml" % addonid.replace(".","-") , cwd, "Default")
		except Exception as e: handle_except(e)
		else:
			ui.doModal()
			del ui

	elif sel == 2:
		stream_func = STREAM_FUNC()
		try:sinklist = stream_func.get_sinks()
		except Exception as e: handle_except(e)
		else:
			sel = dialog.contextmenu(sinklist)
			if sel >= 0:
				try:
					stream_func.set_output_device(sel)
				except Exception as e:
					xbmcgui.Dialog().notification("Select Output Device", "No Stream to switch!", time = 10)

	elif sel==3:
			sel = dialog.contextmenu(["Add New Profile","Delete Profile"])
			if sel == 0:
				name = xbmcgui.Dialog().input("Enter name for new profile")
				if name != '':
					f = FILTER()
					f.save_profile(name)
			elif sel == 1:
				f = FILTER()
				profile_list = f.get_profile_list()
				if len(profile_list) > 0:
					del_profile = profile_list[dialog.contextmenu(profile_list)]
					if xbmcgui.Dialog().yesno("Delete Profile %s" % del_profile,"Are you shure to delete %s ?" % del_profile) == True:
						f.remove_profile(del_profile)
				else: xbmcgui.Dialog().notification("Delete Profile", "No profiles defined!", time = 10)

except Exception as e:
	if(type(e) is pulseerror.PulseDBusError):
		xbmc.log(str(e),xbmc.LOGERROR)
		xbmc.log("\n"+e.get_advice(),xbmc.LOGERROR)
		xbmcgui.Dialog().ok('Pulse Equalizer', "System Configuration Problem. Please check Kodi logfile: ~/.kodi/temp/kodi.log\r\nIf you see this message, you will most likely need to install and configure pulseaudio-equalizer or load the module-dbus-protocol.")
	else:
		raise(e)

	
		
	
sys.modules.clear()
