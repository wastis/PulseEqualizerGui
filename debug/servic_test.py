#!/usr/bin/python3

import sys 
sys.path.append ('./resources/lib/')
sys.path.append ('./fakekodi')
import xbmc
import os

from pulseinterface import PulseInterfaceService
from helper import PipeCom

pipe_com = PipeCom("/run/shm/pa/")

em = PulseInterfaceService(pipe_com)

if sys.version_info[0] < 3:
	raw_input("Press Enter to continue...")
else:
	input("Press Enter to continue...")

em.stop_event_loop()
print("done")


