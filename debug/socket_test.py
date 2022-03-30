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

sock_com = SocketCom("main")

class receiver():
	def on_service_get(self,args):
		print("yuhu", args)

		return {"Name":1, "Val":1}

def on_receive(conn, msg):
	print(msg)
	conn.send(b"OK")
	conn.close()

rec = receiver()

sock_com.start_func_server(rec)

if sys.version_info[0] < 3:
	raw_input("Press Enter to continue...")
else:
	input("Press Enter to continue...")

sock_com.stop_server()
