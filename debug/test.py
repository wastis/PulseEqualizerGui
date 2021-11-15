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

import sys, threading, time
sys.path.append ('./resources/lib/')
sys.path.append ('./fakekodi')

from pcontrol import PulseControl


pc = PulseControl()

print(vars(pc.get_sink(1)))

vi = pc.get_sink(1).volume.values
print(vi)







