#
#	pulse audio gui addon for kodi
#	2021 by wastis
#   --------
#   | pipe |  -- 
#   --------    |   ---------    -----------    ------------------
#               --->| queue | -> | forward | -> | MessageCentral |
#   --------    |   ---------    -----------    ------------------
#   | pulse | --                       
#   --------
#
#   pipe: messages coming from client, pipe read is blocking, therefore has it's own thread
#   pulse:  messages coming from pulseaudio, palisten is blocking, therefore has it's own thread
#   queue: decouple incoming messages from their listening threads
#   forward: send messages to MessageCentral, send timeout message 100ms after last pulseaudio message 
#

import sys, time, os, json
import xbmc
from threading import Thread

if sys.version_info[0] < 3:
	from Queue import Queue, Empty
else:
	from queue import Queue, Empty

import pulsectl
from helper import *

from .pacentral import MessageCentral

from time import time, sleep



class PulseInterfaceService():
	
	def __init__(self, pipe_com):
		self.q = Queue()
		#self.pulse_event = pulsectl.Pulse('Event Manager')
		
		pipe_com
		self.pipe_path = pipe_com.path
		self.pipe_server = pipe_com.server
		self.pipe_client = pipe_com.client
		
		self.mc = MessageCentral(pipe_com)
		
		if not os.path.exists(self.pipe_path): os.makedirs(self.pipe_path)
		if not os.path.exists(self.pipe_server): os.mkfifo(self.pipe_server)
		self.running = True

		self.start_event_loop()
	
	#start all message loops
	def start_event_loop(self):
		Thread(target=self.message_forward).start()
		Thread(target=self.pipe_message_loop).start()
		Thread(target=self.start_pulse_loop).start()

		

	#stop all message loops
	def stop_event_loop(self):
		self.running = False
		self.q.put(('','exit','',''))
		
		with open(self.pipe_server, 'w') as f: f.write("exit")
		os.remove(self.pipe_server)
		
		self.send_message_to_central('message','exit')
		self.pulse_event.close()


	#
	#	support functions
	#

	
	def handle(self, e):
		func_name = sys._getframe(1).f_code.co_name
		error_type = type(e)
		logerror("pulse_event_manager: %s %s %s" % (func_name, error_type, e.message))
	
	def send_message_to_central(self, target, func, param = ''):
		# create a new thread per message. So message_forward thread will not crash in case of message handling crash
		th = Thread(target=self.mc.on_message, args=(target, func, param))
		th.start()
		th.join()

	#
	#	message loops
	#
	
	#messages from the pipe
	def pipe_message_loop(self):
		log("start pipe message loop")
		while True:
			try:
				result=''
				with open(self.pipe_server, 'r') as fifo:
					while True:
						c = fifo.read()
						if len(c)==0:break
						result = result + c
			
				result = result.strip()
				
				log("received from pipe: "+ result)

				if result == "stop-service":
					self.running = False
					self.q.put(('','exit','',''))
					os.remove(self.pipe_server)
					self.send_message_to_central('message','exit')
					self.pulse_event.close()
					break
					
				if result == "exit": break
				
				arg = result.split(";")
				
				try: target =  arg[1] 
				except: target = ''
				try: 
					a = arg[2].strip()
					if a[0] in "[" : args = json.loads(a)
					elif a[0] in "{" : args = [json.loads(a)]
					else: args = a.split(',')
				except: args = [] 
				func = arg[0]
				
				self.q.put(('pipe',target,func,args))

			except Exception as e: handle(e)
		
		log("stop pipe message loop")

	#messages from pulse audio
	def pulse_event_receive(self,event):
			if event.facility._value in ["server", "source", "source_output"]: return
			self.q.put(('pulse',event.facility._value ,event.t._value, [event.index]))

			
	#start message loop for pulse audio		
	def start_pulse_loop(self):
		log("start pulse loop")
		cnt = 1
		while True:
			try:
				self.pulse_event = pulsectl.Pulse('Event Manager')

				log("connected to pulse")
				cnt = 1

				self.pulse_event.event_mask_set('all')
				self.pulse_event.event_callback_set(self.pulse_event_receive)
				self.send_message_to_central('pulse','connect')
				self.pulse_event.event_listen()
			
			except pulsectl.PulseDisconnected:
					log("pulse disconnected")
					if not self.running: 
						log("stop pulse loop")
						return
			except Exception as e: 
				if cnt > 0:
					handle(e)
					cnt = cnt - 1
				
			if not self.running: return
			
			sleep(0.5)
			
	#
	#	message forward
	#
	#	message from pulse may arrive to late/ quick for our message handling.
	#	therefore collect them and process them 100ms after the last message.
	
	def message_forward(self):
		log("start message_dispatch")

		timeout = None
		while True:
			try:
				try:
					origin, target, func ,param = self.q.get(timeout = timeout)
				
				except Empty:
					# we did not receive any message since 100 ms. Send this info to 
					# message collector. Message collector will then process the previouse
					# collected messages

					t = time()  

					self.send_message_to_central('pa','update')
					timeout = None

					log("pa_updated: time needed {:2f} ms".format((time()-t)*1000))
					continue
				except Exception as e: handle(e)
					
				
				if target == "exit": break
				
				if origin == 'pulse': timeout = 0.1 

				self.send_message_to_central(target, func, param)
				
				self.q.task_done()
				
			except Exception as e: handle(e)


		log("stop message_dispatch")

