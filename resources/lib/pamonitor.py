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

from helper.fjson import json

from pulseservice import PulseService

from helper import SocketCom

from launcher import Launcher

class PaMonitor( xbmc.Monitor ):
	def __init__( self ):
		#strat process
		xbmc.Monitor.__init__( self )
		xbmc.log("m_eq: start PulesEqualizer service",xbmc.LOGDEBUG)

		self.server_sock = SocketCom("kodi")
		if not self.server_sock.is_server_running():
			self.server_sock.start_func_server(self)
		else: self.server_sock = None

		launcher = Launcher("menu")
		launcher.start()

		self.sock = SocketCom("server")

		ps = PulseService()
		ps.start()

		while not self.abortRequested():
			if self.waitForAbort( 10 ):
				break

		launcher.stop()

		ps.stop()
		if self.server_sock:
			self.server_sock.stop_server()

	@staticmethod
	def get_device():
		device = json.loads(xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Settings.GetSettingValue", "params":{"setting":"audiooutput.audiodevice"},"id":1}'))
		return device["result"]["value"].replace("PULSE:","")

	def on_device_get(self):
		result = self.get_device()
		xbmc.log("m_eq: kodi service: on_device_get %s" % result,xbmc.LOGDEBUG)
		return [result]

	@staticmethod
	def on_device_set(device):
		xbmc.log("m_eq: device set %s" % device,xbmc.LOGDEBUG)
		result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Settings.SetSettingValue", "params":{"setting":"audiooutput.audiodevice","value":"%s"},"id":1}' % ("PULSE:" + device))
		if result == '{"id":1,"jsonrpc":"2.0","result":true}':
			xbmc.log("m_eq: device set success",xbmc.LOGDEBUG)
		else:
			xbmc.log("m_eq: device set failed",xbmc.LOGDEBUG)

	@staticmethod
	def on_player_get():
		r_dict = json.loads(xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Player.GetActivePlayers","id":0}'))
		try: return r_dict["result"]
		except Exception: return None

	@staticmethod
	def on_log_write(message, level):
		xbmc.log(message, level)

	def on_service_up(self):
		self.sock.call_func("set","device",[self.get_device()])

	def onNotification( self, _sender, method, _data ):
		target,func = method.lower().replace("on","").split(".")
		if target in ["system", "player"]:
			self.sock.call_func(func, target)
