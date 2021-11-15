
import socket, pickle , os, time

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
from threading import Thread
from .log import log
from .handle import handle

class SocketCom():
	
	exit_str = b"slgeife3"
	life_str = b"gklwers6"
	rec_class = None
	
	def __init__(self, name, gid = 0):
		self.path = "/run/user/%d/pa/" % os.geteuid()
		try: os.makedirs(self.path)
		except Exception as e: pass
		
		self.sock_name = self.path + "%s.%d" % (name , gid)
	
	def is_server_running(self):
		if not os.path.exists(self.sock_name): return False
		
		if self.send_to_server(self.life_str) == self.life_str:
			return True
		return None
		
	def get_from_socket(self,sock):
		
		sock.listen(1)
		conn, addr = sock.accept()
		data = conn.recv(1024)
		return data, conn

	def listen_loop(self, callback):
		log("start socket loop")
		sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		sock.settimeout(None)
		
		try: os.remove(self.sock_name)
		except OSError:	pass
		
		sock.bind(self.sock_name)
		
		while True:
			try:
				result, conn = self.get_from_socket(sock)
			
				if result == self.exit_str: 
					conn.close()
					break
				if result == self.life_str:
					conn.send(self.life_str)

				callback(conn, result)
				
			except Exception as e: pass
		log("stop socket loop")
		
		
		try: os.remove(self.sock_name)
		except OSError:	pass
	
	def start_server(self, callback):
		Thread(target = self.listen_loop, args = (callback,)).start()
		
	def start_func_server(self, rec_class):
		self.rec_class = rec_class
		Thread(target = self.listen_loop, args = (self.dispatch,)).start()
		
	def stop_server(self):
		self.send_to_server(self.exit_str)
	
	def send_to_server(self, msg):
		try:
			s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
			s.settimeout(1.0)
			s.connect(self.sock_name)
			s.send(msg)
			data = s.recv(2048)
			s.close()
			return data
		except: return None
		
	def call_func(self, func, target, args=[]):
		result = self.send_to_server(pickle.dumps([func,target,args], protocol=2))
		if result is not None: return pickle.loads(result)
		return None
	
	def dispatch(self, conn, msg):
		try:
			func,target,args = pickle.loads(msg)
			cmd = "on_%s_%s" % (target,func)
			
			try: method = getattr(self.rec_class,cmd)
			except: method = None

			result = method(*args) if method else None
			
			try: 
				conn.send(pickle.dumps(result, protocol=2))
			except: pass
			
			try:conn.close()
			except: pass
			
		except Exception as e: handle(e)
	
	@staticmethod
	def respond(conn, result):
		if conn is not None:
			try:
				conn.send(pickle.dumps(result, protocol=2))
			except: pass
		
