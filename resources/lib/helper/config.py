import os,json
import xbmcaddon
from .handle import handle, log


class Config():

	config = {}
	name = ""

	def __init__(self):
		path_name = os.path.join(xbmcaddon.Addon().getAddonInfo('path'),"settings")
		if not os.path.exists(path_name): os. makedirs(path_name)
		self.file_name = os.path.join(path_name,"config.json")
		
	def __str__(self):
		return "%s: $%s" % (self.name , json.dumps(self.config))
		
	def load_config(self):
		log("load_config %s" % self.file_name)
		try: 
			with open(self.file_name,'r')as f: self.config = json.loads(f.read())
		except Exception as e: 
			handle(e) 
			self.config = {}
			
		log(json.dumps(self.config))

	def save_config(self):
		try: 
			with open(self.file_name,'w')as f: f.write(json.dumps(self.config))
		except Exception as e: handle(e)

	def set_name(self, name_first, name_last):
		self.name = "%s.%s" % (name_first, name_last)
		
	def get(self, key, default = None, name = None):
		log("get %s %s" % (key, name))
		if name is None: name = self.name
		if name is None: return default
		
		if self.config == {}: self.load_config() 
		if self.config == {}: 
			self.config[name] = {}
	
		log(json.dumps(self.config))
		try: sec = self.config[name]
		except: sec = {}
		
		try: return sec[key]
		except: 
			sec[key] = default
			self.config[name] = sec
			self.save_config()
			return default
		
	def set(self, key, val, name = None):
		if name is None: name = self.name
		if name == None: return
		
		try: sec = self.config[name]
		except: sec = {}
		
		sec[key]= val
		self.config[name] = sec
		self.save_config()
