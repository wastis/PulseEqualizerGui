#!/usr/bin/python3

import sys, threading, time
sys.path.append ('./resources/lib/')
sys.path.append ('./fakekodi')

from pcontrol import PulseControl


pc = PulseControl()

print(vars(pc.get_sink(1)))

vi = pc.get_sink(1).volume.values
print(vi)







