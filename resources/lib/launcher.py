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

import os
import threading

from basic import handle
from basic import log
from basic import path_pipe

from menus import Menu

class Launcher():
	def __init__(self,cwd, name):
		self.menu = Menu(cwd)
		self.pname = "{}.{}".format(name,os.getppid())
		self.ppath = path_pipe + self.pname

	def loop(self):
		log("launcher: start {}".format(self.ppath))
		try: os.makedirs(path_pipe)
		except OSError: pass

		try: os.mkfifo(self.ppath)
		except OSError: pass

		lock = path_pipe + "lock"

		while True:
			try:
				try:
					log("launcher: wait")
					with open(self.ppath) as f: result = f.read()
					log("launcher: rec")
				except OSError as e:
					handle(e)
					break

				log("launcher: receive {}".format(result))

				if result == "sfdaoekga": break

				cmd , step = result.split(',')
				try: step = int(step.strip())
				except ValueError: step = 1

				self.menu.sel_menu(cmd,step)

			except Exception as e: handle(e)

			try: os.remove(lock)
			except OSError: pass

		try: os.remove(self.ppath)
		except OSError: pass

		log("launcher: stop")

	def stop(self):
		try:
			with open(self.ppath, "w") as f: f.write("sfdaoekga")
		except OSError: pass

	def start(self):
		threading.Thread(target = self.loop).start()

