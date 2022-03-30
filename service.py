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
import xbmc
import xbmcaddon
import sys
import os

cwd	= xbmcaddon.Addon().getAddonInfo('path')
sys.path.append ( os.path.join( cwd, 'resources', 'lib' ))
sys.path.append ( os.path.join( cwd, 'resources', 'language' ))

from pamonitor import PaMonitor

if ( __name__ == "__main__" ):
	PaMonitor(cwd)
