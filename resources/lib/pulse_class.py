import sys
if sys.version_info[0] > 2:
	from dbus_basic_3 import PULSE_DBUS
	import dbus_basic_3 as dbus
else:
	from dbus_basic_2 import PULSE_DBUS
	import dbus_basic_2 as dbus
	
import interface as IF

#returns the list of actual streams with additional information
def get_stream_list(pulse_dbus):
	sink_names = []
	sink_modules = []
	sink_vals  = []

	#
	#first, get all sinks, then all streams and then connect steams to sinks via owne_rmodule
	#
	
	sink_list =  pulse_dbus.get_property(IF.CORE_I,IF.CORE_P,'Sinks')
	for sink in sink_list:
		name = pulse_dbus.get_property(IF.DEVICE_I,sink,'Name')
		
		#we need the device master to know where we should steam to from this device
		device_master = None
		device_class = None
		owner_module = pulse_dbus.get_property(IF.DEVICE_I,sink,'OwnerModule')
		sink_prop = pulse_dbus.get_property(IF.DEVICE_I,sink,'PropertyList')
		if 'device.master_device' in sink_prop:
				device_master = bytearray(sink_prop['device.master_device']).decode("utf-8")[:-1]
		if 'device.class' in sink_prop:
				device_class = bytearray(sink_prop['device.class']).decode("utf-8")[:-1]
		
			#create the lookup tables
		'''
		print("-------------")
		print(sink)
		print(owner_module)
		print(name)
		print(device_master)
		print(device_class)
		'''
		
		sink_modules.append(owner_module)
		sink_names.append(name)
		sink_vals.append([sink, device_master, device_class])

	#now get the steams.

	streams = []

	playback_streams = pulse_dbus.get_property(IF.CORE_I,IF.CORE_P,'PlaybackStreams')
	for stream in playback_streams:
		owner_module = pulse_dbus.get_property(IF.STREAM_I,stream,'OwnerModule')
		device = pulse_dbus.get_property(IF.STREAM_I,stream,'Device')
		driver = pulse_dbus.get_property(IF.STREAM_I,stream,'Driver')
		
		#we need the client to find the KodiSink as startpoint for the stream chain 
		try:
			client = pulse_dbus.get_property(IF.STREAM_I,stream,'Client')
		except Exception: client=None
		
		app_name = None
		if client != None:
			
			client_property_list = pulse_dbus.get_property(IF.CLIENT_I,client,'PropertyList')
			if 'application.name' in client_property_list:
				app_name = str(bytearray(client_property_list['application.name']).decode("utf-8")[:4])
		
		
		'''
		print("-------------")
		print(stream)
		print(owner_module)
		print(device)
		print(client)
		print(str(app_name)[:4])
		'''		
		#look up where to which device we should streem to 
		should_sink = None
		should_type = None
		self_sink = None
		
		if owner_module in sink_modules:
			should_val = sink_vals[sink_modules.index(owner_module)]

			self_sink = should_val[0]
			should_name = should_val[1]
			self_type = should_val[2]
				
			if should_name != None:
				try:
					should_val = sink_vals[sink_names.index(should_name)]
					should_sink =should_val[0]
					should_type = should_val[2]
				except: None
			
		streams.append({"stream":stream,"self_sink":self_sink,"out_sink":device,"should_out":should_sink,"self_type":self_type,"driver":driver,"app_name":app_name})
		
	return streams


def find_stream(stream_list, key, val):
	for stream in stream_list:
		try:
			if stream[key]==val:return stream
		except: continue
	return None

#
# Class Filter, to manage the equalizer settings to a given sink 
#

class FILTER():
	
	DEFAULT_FREQUENCIES=[31.75,63.5,125,250,500,1e3,2e3,4e3,8e3,16e3]
	
	def __init__(self):
		self.pulse_dbus = PULSE_DBUS()
		#self.sinks = self.pulse_dbus.get_property(IF.MANAGER_I,IF.MANAGER_P, 'EqualizedSinks')
		#self.sink_path = self.sinks[0]
		success,result =  self.find_equalizer_sink()
		if success:
			self.sink_path = result
		else:
			raise(Exception(result))
		
		self.channel = self.pulse_dbus.get_property(IF.EQUALIZER_I, self.sink_path, 'NChannels')
		self.sample_rate = self.pulse_dbus.get_property(IF.EQUALIZER_I, self.sink_path, 'SampleRate')
		self.filter_rate = self.pulse_dbus.get_property(IF.EQUALIZER_I, self.sink_path, 'FilterSampleRate')
		self.set_frequency_values(self.DEFAULT_FREQUENCIES)

	
	def freq_proper(self,xs):
		return [0]+xs+[self.sample_rate//2]

	@staticmethod
	def translate_rates(dst,src,rates):
		return list([x*dst/src for x in rates])

	def _set_frequency_values(self,freqs):
		self.frequencies=freqs
		self.filter_frequencies=[int(round(x)) for x in self.translate_rates(self.filter_rate,self.sample_rate,self.frequencies)]
		self.coefficients=[1.0]*len(self.frequencies)
		self.preamp=1.0

	def set_frequency_values(self,freqs):
		self._set_frequency_values(self.freq_proper(freqs))

	def filter_at_points(self):
		coefs,preamp = self.pulse_dbus.call_func(IF.EQUALIZER_I,self.sink_path,'FilterAtPoints',"uau",self.channel,self.filter_frequencies)
		self.coefficients=coefs
		
		if sys.version_info[0] > 2: self.preamp=preamp[1]
		else: self.preamp = preamp
		
		return self.coefficients,self.preamp
	
	def seed_filter(self):
		
		print(self.filter_frequencies)
		print(self.coefficients)
		print(self.preamp)
		
		self.pulse_dbus.call_func(IF.EQUALIZER_I,self.sink_path,'SeedFilter',"uauadd",self.channel, self.filter_frequencies, self.coefficients, self.preamp)
		
	def set_filter(self,preamp,coefs):
		self.pulse_dbus.call_func(IF.EQUALIZER_I,self.sink_path,'SetFilter',"uadd",self.channel, coefs, preamp)
		
	def get_filter(self):
		return self.pulse_dbus.call_func(IF.EQUALIZER_I,self.sink_path,'GetFilter',"u",self.channel)

	def save_state(self):
		self.pulse_dbus.call_func(IF.EQUALIZER_I,self.sink_path,'SaveState')

	def load_profile(self,profile):
			self.pulse_dbus.call_func(IF.EQUALIZER_I,self.sink_path,'LoadProfile',"us",self.channel,profile)
		
	def save_profile(self,profile):
		self.pulse_dbus.call_func(IF.EQUALIZER_I,self.sink_path,'SaveProfile',"us",self.channel,profile)
		
	def get_base_profile(self):
		return self.pulse_dbus.call_func(IF.EQUALIZER_I,self.sink_path,'BaseProfile',"u", self.channel)
	
	def get_profile_list(self):
		return self.pulse_dbus.get_property(IF.MANAGER_I,IF.MANAGER_P, 'Profiles')
		
	def remove_profile(self,profile):
		self.pulse_dbus.call_func(IF.MANAGER_I,IF.MANAGER_P,'RemoveProfile',"s", profile)
		
	def reset(self):
		self.coefficients=[1.0]*len(self.frequencies)
		self.preamp = 1.0

	def find_equalizer_sink(self):
		streams = get_stream_list(self.pulse_dbus)
		cur_stream = find_stream(streams,"app_name","Kodi")
		while cur_stream != None:
			cur_stream = find_stream(streams,"self_sink",cur_stream["out_sink"])
			if cur_stream == None:return False, "no equalizer in filter chain"
			if cur_stream["driver"] == "module-equalizer-sink.c":
				return True, cur_stream["self_sink"]
		return False, "no stream available"

	@staticmethod
	def slider2coef(x):
		return x * 0.0021
	@staticmethod
	def coef2slider(x):
		return int(x * 476.2)
		
	
class STREAM_FUNC:
	def __init__(self):
		self.pulse_dbus = PULSE_DBUS()
		self.sink_lookup = []
		self.dev_list = []
		self.eqaulizer_sink = ''
		
	def get_sinks(self):
		
		self.fft_stream, self.eqaulizer_sink ,out_sink = self.find_last_in_chain()
		if self.fft_stream==None: return []
		
		sink_lookup=[]

		sink_list =  self.pulse_dbus.get_property(IF.CORE_I,IF.CORE_P,'Sinks')
		for sink in sink_list:
			card_name = ''
			card_sink_list = []
			
			property_list = self.pulse_dbus.get_property(IF.DEVICE_I,sink,'PropertyList')
			
			if 'device.description' in property_list:
				card_name=bytearray(property_list['device.description']).decode("utf-8")
			elif 'device.product.name' in property_list:
				card_name=bytearray(property_list['device.product.name']).decode("utf-8")
			else: card_name='unkown device'
			
			card_driver = self.pulse_dbus.get_property(IF.DEVICE_I,sink,'Driver')
			
			if card_driver=='module-alsa-card.c' or card_driver=='module-bluez5-device.c':
				#GET PORTS
				active_port = self.pulse_dbus.get_property(IF.DEVICE_I,sink,"ActivePort")
				active_port_desc = self.pulse_dbus.get_property(IF.PORT_I,active_port,"Description")
				
				card_sink_list.append([sink,card_name,active_port,active_port_desc])
				
				ports = self.pulse_dbus.get_property(IF.DEVICE_I,sink,"Ports")
				for port in ports:
					if port != active_port:
						port_desc = self.pulse_dbus.get_property(IF.PORT_I,port,"Description")
						card_sink_list.append([sink,card_name,port,port_desc])
						
				if sink == out_sink:
					card_sink_list.extend(sink_lookup)
					sink_lookup = card_sink_list
				else:
					sink_lookup.extend(card_sink_list)
			
		#create user friendly
		self.dev_list = []
		for line in sink_lookup:
			self.dev_list.append(line[3]+' @ '+ line[1])
		
		self.sink_lookup = sink_lookup

		return self.dev_list
	
				
	def set_output_device(self,sel):
		self.fft_stream, self.eqaulizer_sink ,out_sink = self.find_last_in_chain()
		if self.fft_stream==None: return []

		#set port first
		try:
			self.pulse_dbus.set_property(IF.DEVICE_I,self.sink_lookup[int(sel)][0],"ActivePort","o",self.sink_lookup[int(sel)][2])
		except:pass
		#set stream to sink
		try:
			self.pulse_dbus.call_func(IF.STREAM_I,self.fft_stream,'Move',"o", self.sink_lookup[int(sel)][0])
		except:pass
	
	def find_last_in_chain(self):
		streams = get_stream_list(self.pulse_dbus)
		cur_stream = find_stream(streams,"app_name","Kodi")
		if cur_stream == None: raise(Exception("no stream available"))
		
		while cur_stream != None:
				next_stream = find_stream(streams,"self_sink",cur_stream["out_sink"])
				if next_stream == None: return cur_stream["stream"], cur_stream["self_sink"],cur_stream["out_sink"]
				cur_stream = next_stream
		return None,None,None
		
		
	def switch_chain(self):
		log = ""
		streams = get_stream_list(self.pulse_dbus)
		cur_stream = find_stream(streams,"app_name","Kodi")
		if cur_stream != None: log = log + "found KodiSink\noutput sink: %s\n----------\n" % cur_stream["out_sink"]
		else:
			log = log + "KodiSink not found: \n"
			for cur_stream in streams:
				log = log + "self_sink   : %s\n" % cur_stream["self_sink"]
				log = log + "out_sink    : %s\n" % cur_stream["out_sink"]
				log = log + "should_out: : %s\n" % cur_stream["should_out"]
				log = log + "should type : %s\n" % cur_stream["should_type"]
				log = log + "self_type   : %s\n" % cur_stream["self_type"]
				log = log + "app_name    : %s\n" % cur_stream["app_name"]
				return log

				
		while cur_stream != None:
				cur_stream = find_stream(streams,"self_sink",cur_stream["out_sink"])
				if cur_stream == None:
					log = log + "end-----------\n"
					break
				log = log + "self_sink   : %s\n" % cur_stream["self_sink"]
				log = log + "out_sink    : %s\n" % cur_stream["out_sink"]
				log = log + "should_out  : %s\n" % cur_stream["should_out"]
				log = log + "should type : %s\n" % cur_stream["should_type"]
				log = log + "self_type   : %s\n" % cur_stream["self_type"]
				log = log + "driver      : %s\n" % cur_stream["driver"]
							
								
				if ( cur_stream["self_type"] == "filter"):
					log = log + "sink is fiter\n"
					if cur_stream["should_type"] == "filter":
						if cur_stream["out_sink"] != cur_stream["should_out"]:
							log = log + "out is not correct.. try to switch\n"
							self.pulse_dbus.call_func(IF.STREAM_I,cur_stream["stream"],'Move',"o", cur_stream["should_out"])
							cur_stream["out_sink"] = cur_stream["should_out"]
						else: log = log + "out is corret\n"
					else:
						log = log + "out type is %s, select last output device\n" % cur_stream["should_type"]
				log = log + "----------------\n"

		return log
	

