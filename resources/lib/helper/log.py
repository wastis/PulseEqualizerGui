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
try: import xbmc
except: 
	class xbmc():
		LOGDEBUG = "DEBUG"
		LOGINFO = "INFO"
		LOGERROR = "ERROR"
		@staticmethod
		def log(text, level): print(level, text)


def log(text):
	xbmc.log("eq: " + text, xbmc.LOGDEBUG)
	
def loginfo(text):
	xbmc.log("eq: " + text, xbmc.LOGINFO)

def logerror(text):
	xbmc.log("eq: " + text, xbmc.LOGERROR)
	
