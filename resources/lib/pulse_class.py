import sys
if sys.version_info[0] > 2:
	from dbus_basic_3 import PULSE_DBUS
	import dbus_basic_3 as dbus
else:
	from dbus_basic_2 import PULSE_DBUS
	import dbus_basic_2 as dbus
	
import interface as IF


#
# Class Filter, to manage the equalizer settings to a given sink 
#

class FILTER():
	
	DEFAULT_FREQUENCIES=[31.75,63.5,125,250,500,1e3,2e3,4e3,8e3,16e3]
	
	def __init__(self):
		self.pulse_dbus = PULSE_DBUS()
		self.sinks = self.pulse_dbus.get_property(IF.MANAGER_I,IF.MANAGER_P, 'EqualizedSinks')
		self.sink_path = self.sinks[0]
		
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
		self.get_fft_stream()
		sink_lookup = []
		self.dev_list = []
		self.eqaulizer_sink = ''
		sink_list =  self.pulse_dbus.get_property(IF.CORE_I,IF.CORE_P,'Sinks')

		for sink in sink_list:
			card_name = ''
			property_list = self.pulse_dbus.get_property(IF.DEVICE_I,sink,'PropertyList')
			
			if 'device.description' in property_list:
				card_name=bytearray(property_list['device.description']).decode("utf-8")
			elif 'device.product.name' in property_list:
				card_name=bytearray(property_list['device.product.name']).decode("utf-8")
			else: card_name='unkown device'
			
			card_driver = self.pulse_dbus.get_property(IF.DEVICE_I,sink,'Driver')
			
			if(card_driver=='module-equalizer-sink.c'):
				self.eqaulizer_sink = sink
			elif(card_driver=='module-alsa-card.c'):
				#GET PORTS
				active_port = self.pulse_dbus.get_property(IF.DEVICE_I,sink,"ActivePort")
				active_port_desc = self.pulse_dbus.get_property(IF.PORT_I,active_port,"Description")
				
				sink_lookup.append([sink,card_name,active_port,active_port_desc])
				
				ports = self.pulse_dbus.get_property(IF.DEVICE_I,sink,"Ports")
				for port in ports:
					if port != active_port:
						port_desc = self.pulse_dbus.get_property(IF.PORT_I,port,"Description")
						sink_lookup.append([sink,card_name,port,port_desc])
			
						
				
		#sort list to get the current acitve at the beginning
		sink_lookup_result = []
		for line in sink_lookup:
			if line[0] == self.fft_sink:
				sink_lookup_result.append(line)
		#and the rest
		for line in sink_lookup:
			if line[0] != self.fft_sink:
				sink_lookup_result.append(line)
		#create user friendly
		self.dev_list = []
		for line in sink_lookup_result:
			self.dev_list.append(line[3]+' @ '+ line[1])
		
		self.sink_lookup = sink_lookup_result
			

		return self.dev_list
	
	def get_fft_stream(self):

		self.fft_stream = ''
		self.fft_sink = ''
		
		playback_streams = self.pulse_dbus.get_property(IF.CORE_I,IF.CORE_P,'PlaybackStreams')
		if(len(playback_streams)>0):
			for stream in playback_streams:
				dsink =  self.pulse_dbus.get_property(IF.STREAM_I,stream,'Device')
				module = self.pulse_dbus.get_property(IF.STREAM_I,stream,'OwnerModule')
				module_name = self.pulse_dbus.get_property(IF.MODULE_I,module,'Name')
				
				if module_name == 'module-equalizer-sink':
					self.fft_stream = stream
					self.fft_sink = dsink

		return self.fft_stream
			
	def set_output_device(self,sel):
		if self.fft_stream == '':self.fft_stream = self.get_fft_stream()
		if self.fft_stream == '':raise ValueError("No stream on equalizer. Play video for selecting the output device.")
		
		if self.eqaulizer_sink == '':get_sinks()
		if self.eqaulizer_sink == '':raise ValueError("Pulse equalizer sink not found. Please install pulse-equalizer and load module.")

		#set port first
		self.pulse_dbus.set_property(IF.DEVICE_I,self.sink_lookup[int(sel)][0],"ActivePort","o",self.sink_lookup[int(sel)][2])

		#set stream to sink
		self.pulse_dbus.call_func(IF.STREAM_I,self.fft_stream,'Move',"o", self.sink_lookup[int(sel)][0])
		
		
		
