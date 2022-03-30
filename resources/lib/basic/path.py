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

p = os.path.realpath(__file__)
path_addon = p[:p.rfind("/resources/") + 1]
path_kodi = os.environ['HOME']+"/.kodi/"

path_tmp = "/run/user/%d/pa/" % os.geteuid()
path_pipe = "/run/user/%d/pa/" % os.geteuid()
path_settings = "settings/"
path_filter = "settings/spectrum/"
path_lib = "resources/lib/"
path_skin = "resources/skins/{skin}/1080i/"
path_skin_root = "resources/skins/"
path_keymap = "userdata/keymaps/"

