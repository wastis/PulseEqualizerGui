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

from monitor import PE_SERVICE

if ( __name__ == "__main__" ):
	PE_SERVICE()
