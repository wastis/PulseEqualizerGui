import sys,os, json

sys.path.append ('./resources/lib/')
sys.path.append ('./fakekodi')

from helper import *


from pulseinterface import PulseControl


pc = PulseControl()
pc.start()

try:
	print(sys.argv)
	cmd =  sys.argv[1]
	result = pc.get_list(cmd)
	
	for obj in result:
		print(obj.index, obj.name)
		for key,val in vars(obj).items():
			
			if key == "proplist":
				print("\tproplist:")
				for k,v in val.items():
					print("\t\t%s=%s" %(k,v))
			else:	
				print("\t%s=%s" %(key,val))
		print("***************************************************")


except Exception as e: handle(e)
