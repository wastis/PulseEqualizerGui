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
import os 
import sys 

sys.path.append ('./resources/lib/')
sys.path.append ('./fakekodi')

import xbmc
from helper import SocketCom
from sound import SoundGen

		
sg = SoundGen()
sc = SocketCom("sound")

sc.start_func_server(sg,block = True)
sg.end_server()





