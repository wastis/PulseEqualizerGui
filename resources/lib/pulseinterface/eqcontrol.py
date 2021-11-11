import sys,json
import padbus
import xbmc

from padbus import DBusInterface as IF
from padbus import PulseDBus
from helper import *


#
# Class Filter, to manage the equalizer settings to a given sink 
#

presets = [
{"name":"Treble","preamp":0.5, "coef":[1.0, 1.0, 1.0, 1.0, 1.0, 1.3, 1.8, 2.3, 2.5, 2.5, 2.5, 2.5]},
{"name":"Bass","preamp":0.5, "coef":[1.0, 2.5, 2.5, 2.3, 1.8, 1.3, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]},
{"name":"Flat","preamp":1.0, "coef":[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]}]


class EqControl():
	
	frequencies = [31.75,63.5,125,250,500,1e3,2e3,4e3,8e3,16e3]
	
	def __init__(self):
		
		self.pulse_dbus = PulseDBus()
		self.eq_param = {}
		
	def get_filter_param(self, index):
		
		try: return self.eq_param[index]
		except: pass

		path = "/org/pulseaudio/core1/sink" + str(index)
		channel = self.pulse_dbus.get_property(IF.EQUALIZER_I, path, 'NChannels')
		sample_rate = self.pulse_dbus.get_property(IF.EQUALIZER_I, path, 'SampleRate')
		filter_rate = self.pulse_dbus.get_property(IF.EQUALIZER_I, path, 'FilterSampleRate')
		
		filter_freq = self.calc_filter_freq(filter_rate, sample_rate, self.frequencies)

		self.eq_param[index] = (path, channel, sample_rate, filter_rate, filter_freq)
		return self.eq_param[index]

	def on_eq_default_profile_set(self, index):
		
		for preset in presets:
			coef = preset["coef"]
			preamp = preset["preamp"]
			self.on_eq_filter_set(index,preamp,coef)
			self.on_eq_profile_save(index,preset["name"])

	
	def on_eq_frequencies_get(self):
		return self.frequencies
		

	def on_eq_channel_set(self, index, ch):
		path, channel, sample_rate, filter_rate, filter_freq = self.get_filter_param(index)
		self.eq_param[index] = (path, ch, sample_rate, filter_rate, filter_freq)
		
	def on_eq_channel_get(self, index):
		path, channel, sample_rate, filter_rate, filter_freq = self.get_filter_param(index)
		return channel

	def on_eq_filter_get(self, index):
		path, channel, sample_rate, filter_rate, filter_freq = self.get_filter_param(index)
		
		coefs,preamp = self.pulse_dbus.call_func(IF.EQUALIZER_I,path,'FilterAtPoints',"uau",channel,filter_freq)
		
		preamp = preamp[1] if sys.version_info[0] > 2 else preamp
		return(preamp, coefs)
	
	def on_eq_filter_set(self, index, preamp, coefs):
		path, channel, sample_rate, filter_rate, filter_freq = self.get_filter_param(index)
		
		self.pulse_dbus.call_func(IF.EQUALIZER_I,path,'SeedFilter',"uauadd",channel, filter_freq, coefs, preamp)

	def on_eq_state_save(self, index):
		path, channel, sample_rate, filter_rate, filter_freq = self.get_filter_param(index)
		self.pulse_dbus.call_func(IF.EQUALIZER_I,path,'SaveState')

	def on_eq_profile_load(self,index, profile):
		path, channel, sample_rate, filter_rate, filter_freq = self.get_filter_param(index)
		self.pulse_dbus.call_func(IF.EQUALIZER_I,path,'LoadProfile',"us", channel, profile)

		
	def on_eq_profile_save(self,index, profile):
		path, channel, sample_rate, filter_rate, filter_freq = self.get_filter_param(index)
		self.pulse_dbus.call_func(IF.EQUALIZER_I,path,'SaveProfile',"us",channel,profile)
	
	def on_eq_base_profile_get(self, index):
		path, channel, sample_rate, filter_rate, filter_freq = self.get_filter_param(index)
		return self.pulse_dbus.call_func(IF.EQUALIZER_I,path,'BaseProfile',"u", channel)

	
	def on_eq_profiles_get(self):
		return self.pulse_dbus.get_property(IF.MANAGER_I,IF.MANAGER_P, 'Profiles')
		
	def on_eq_profile_remove(self,profile):
		self.pulse_dbus.call_func(IF.MANAGER_I,IF.MANAGER_P,'RemoveProfile',"s", profile)
		
	@staticmethod
	def freq_extend(sample_rate, xs):
		return [0]+xs+[sample_rate//2]

	@staticmethod
	def translate_rates(dst,src,rates):
		return list([x*dst/src for x in rates])


	def calc_filter_freq(self, filter_rate,sample_rate, frequencies):
		return [int(round(x)) for x in self.translate_rates(filter_rate,sample_rate,self.freq_extend(sample_rate, frequencies))]


	

