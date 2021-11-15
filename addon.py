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

import os,sys 
lock = "/run/user/%d/pa/lock" % os.geteuid()

def run_addon():

	import xbmc
	import json
	import xbmcaddon
	
	cwd		= xbmcaddon.Addon().getAddonInfo('path')	
	sys.path.append ( os.path.join( cwd, 'resources', 'lib' ))
	sys.path.append ( os.path.join( cwd, 'resources', 'language' ))

	from helper import handle, log, logerror
	from menus import Menu

	xbmc.log("equalizer: start addon" , xbmc.LOGINFO)


	try:
		try: cmd = sys.argv[1]
		except:	cmd = False

		m = Menu(cwd)
		#if not m.get_status(): sys._exit(0)

		#check if another instance of this script is already running
	
		if cmd:
		
			xbmc.log("equalizer: addon has been started by key press command" , xbmc.LOGINFO)
			m.sel_menu(cmd)
			
		else:
			
			xbmc.log("equalizer: addon has been selected and is first instance" , xbmc.LOGINFO)
			m.sel_main_menu()

				
	except Exception as e: handle(e)


if not os.path.exists( lock ):
	try:
		open(lock,'w')
		run_addon()
	finally:	
		try:
			os.remove(lock)
		except: pass







