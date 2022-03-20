#!/usr/bin/python3

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
import sys

sys.path.append ('./resources/lib/')
sys.path.append ('./fakekodi')

from helper import SocketCom

sc = SocketCom("server")
if not sc.is_server_running():
	print("server is not running")
	sys.exit(0)

sc.call_func("set","room_correction",["fix_1"])
sc.call_func('set', 'frequencies',[[125,250,500,1000,2000,4000,8000,16000]])

