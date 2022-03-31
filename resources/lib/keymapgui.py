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

import xbmcaddon
import xbmcgui
import xbmc
import threading
import time

from helper import KeyMapFile
from basic import handle

from contextmenu import contextMenu

addon = xbmcaddon.Addon()
def tr(lid):
	return addon.getLocalizedString(lid)

class KeyMapGui(  xbmcgui.WindowXMLDialog  ):
	def __init__( self, *args, **_kwargs ):
		self.cwd = args[1]
		self.skin = args[2]

		self.kmf = KeyMapFile()
		self.kmf.parse_keymap_file()
		self.index = {}

	def onInit( self ):
		for but_main_id in [3000,4000,5000]:
			for but_sub_id in range(8):
				but_id = but_main_id + but_sub_id
				lab_id = int(but_main_id / 10) + but_sub_id

				but_ctl = self.getControl(but_id)
				lab_ctl = self.getControl(lab_id)
				name = but_ctl.getLabel()

				self.index[but_id] = (name, lab_id)
				vals = self.kmf.get_info(name)

				if vals:
					but_ctl.setLabel(tr(vals["name"]))
					if vals["key"] == 0: lab_ctl.setLabel("-")
					else: lab_ctl.setLabel(str(vals["key"]))

	@staticmethod
	def send_reload_keymaps():
		time.sleep(1)
		xbmc.executebuiltin('Action(reloadkeymaps)')

	def end_gui_ok(self):
		self.kmf.save()
		# we have to create delayed action otherwise the reloadkeymaps action will
		# be swallowed by the window animations
		threading.Thread(target = self.send_reload_keymaps).start()
		self.close()

	def end_gui_cancel(self):
		self.close()

	def onAction( self, action ):
		try:
			aid = action.getId()
			fid = self.getFocusId()
			keycode = action.getButtonCode()
			buc = keycode & 0xff

			#OK pressed
			if aid in [7]:
				name, lab_id = self.index[fid]
				self.kmf.set_info(name,0)
				self.getControl(lab_id).setLabel("-")

			#Cancel
			if aid in [92,10]:
				contextMenu(funcs = [(tr(37501),None),
						(tr(37502),self.end_gui_cancel),
						(tr(37503),self.end_gui_ok)])

			elif aid not in [1,2,3,4,7] and buc != 0:
				try:
					name, lab_id = self.index[fid]
					self.kmf.set_info(name, keycode)
					self.getControl(lab_id).setLabel(str(keycode))
				except KeyError: pass
		except Exception as e:
			handle(e)
			self.close()
