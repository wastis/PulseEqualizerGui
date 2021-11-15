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
import os, re

try:
	addon_path = re.findall(".*?/resources/", os.path.realpath(__file__),re.DOTALL | re.I)[0][:-10]
except: 
	addon_path = None
	pass

def get_addon_path():
	try:
		return addon_path
	except: return None

def get_settings_path():
	try:
		return get_addon_path() + "settings/"
	except: return None

def get_lib_path():
	try:
		return get_addon_path() + "resources/lib/"
	except: return None
	
def get_sink_path():
	try:
		return get_addon_path() + "resources/skins/"
	except: return None
