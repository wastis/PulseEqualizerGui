from dbus_basic import PULSE_DBUS
import dbus_basic as dbus

def get_possible_devices():
	global pulse_dbus 
	global fft_stream
	global sink_lookup
	
	pulse_dbus = PULSE_DBUS()

	sink_lookup = []
	dev_list = []
	eqaulizer_sink = ''
	sink_list =  pulse_dbus.get_property(dbus.CORE_I,dbus.CORE_P,'Sinks')
	for sink in sink_list:
		card_name = ''
		property_list = pulse_dbus.get_property(dbus.DEVICE_I,sink,'PropertyList')
		
		if 'device.description' in property_list:
			card_name=bytearray(property_list['device.description']).decode()
		elif 'device.product.name' in property_list:
			card_name=bytearray(property_list['device.product.name']).decode()
		else: card_name='unkown device'
		
		card_driver = pulse_dbus.get_property(dbus.DEVICE_I,sink,'Driver')
		
		if(card_driver=='module-equalizer-sink.c'):
			eqaulizer_sink = sink
		else:
			sink_lookup.append([sink,card_name])
			dev_list.append(card_name)


	fft_stream = ""
	playback_streams = pulse_dbus.get_property(dbus.CORE_I,dbus.CORE_P,'PlaybackStreams')
	if(len(playback_streams)>0):
		for stream in playback_streams:
			dsink =  pulse_dbus.get_property(dbus.STREAM_I,stream,'Device')
			module = pulse_dbus.get_property(dbus.STREAM_I,stream,'OwnerModule')
			module_name = pulse_dbus.get_property(dbus.MODULE_I,module,'Name')
			
			if module_name == 'module-equalizer-sink':
				fft_stream = stream

	return dev_list
		
def set_output_device(sel):
	global pulse_dbus
	global fft_stream
	global sink_lookup

	pulse_dbus.call_func("org.PulseAudio.Core1.Stream",fft_stream,'Move',"o", sink_lookup[int(sel)][0])
