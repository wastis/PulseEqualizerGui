#!/usr/bin/env python3

import sys,os, json

sys.path.append ('./resources/lib/')
sys.path.append ('./fakekodi')

from helper import *


pipe_com = PipeCom("/run/shm/pa/")


if not os.path.exists(pipe_com.path): 
	print("no server")
	sys.exit(0)

if not os.path.exists(pipe_com.client): os.mkfifo(pipe_com.client)

try:
	cmd = sys.argv[1]
except: 
	print('usage: get_info.py "get;introspect"\nor:    get_info.py "get;outlist"')
	os.remove(pipe_com.client)
	sys.exit(0)
	
if not pipe_com.send("server", cmd):
	print("send failed")
	sys.exit(0)
	
if 'get;' in cmd:
	result = pipe_com.read("client")
	if result: 
		print(result)
	else: print("receive timeout")

os.remove(pipe_com.client)
