
import os, sys, traceback, json
from threading import Thread, Lock
from .config import Config
from .handle import handle
from .log import *

from time import sleep


	
	
class PipeCom():
	def __init__(self, path, pid = 0):
		
		self.path = path
		self.server = os.path.join(path,"server." + str(pid))
		self.client = os.path.join(path,"client." + str(pid))
		self.lock = Lock()
	
	def get_pipe(self, target):
		if target == "server":return self.server
		if target == "client":return self.client
		
	
	def send(self, target, message, timeout = 1):
		pipe = self.get_pipe(target)
		
		if not os.path.exists(pipe): return False
		
		self.running = True
		self.success = True
		
		th = Thread(target=self.timer, args=(pipe, timeout,'write'))
		th.start()

		with open(pipe, "w") as f:
			f.write(message)
		
		self.lock.acquire()
		self.running = False
		self.lock.release()
		
		th.join()
		
		self.lock.acquire()
		success = self.success
		self.lock.release()
		
		
		return success

	def read(self,target, timeout = 1, remove = False):
		pipe = self.get_pipe(target)
		
		if not os.path.exists(pipe): return
		
		self.running = True
		self.success = True
		
		th = Thread(target=self.timer, args=(pipe, timeout,'read'))
		th.start()
		
		
		with open(pipe, "r") as f: result = f.read()
		
		self.lock.acquire()
		self.running = False
		self.lock.release()
		
		th.join()
		
		if remove: os.remove(pipe)
		
		if result == "timeout": return None
		return result

	def get_from_server(self,message):
		self.create_pipe("client")
		
		self.send("server",message)
		result = self.read(target = "client", remove = True)
		if result is None: return None
		return json.loads(result)
		
	def send_to_server(self,message):
		self.send("server",message)


	
	def timer(self, pipe, timeout, direction = 'write'):
		cnt = timeout * 20

		self.lock.acquire()
		running = self.running
		self.lock.release()
		
		while cnt > 0 and running:
			cnt = cnt - 1
			sleep(0.05)
			
			self.lock.acquire()
			running = self.running
			self.lock.release()
			
		
		if running:
			
			self.lock.acquire()
			self.success = False
			self.lock.release()
			
			if direction == 'write':
				with open(pipe, 'r') as f:	f.read()
			else:
				with open(pipe, 'w') as f:	f.write("timeout")
			
			
	def create_pipe(self,target):

		path = self.server if target == "server" else self.client
		if os.path.exists(path):return
		
		if not os.path.exists(self.path): os.makedirs(self.path)
		os.mkfifo(path)
		
	def remove_pipe(self,target):
		path = self.server if target == "server" else self.client
		
		if not os.path.exists(path):return
		os.remove(path)



