
class PulseDBusError(Exception) :
	slots__ = ("name", "message", "python","detail")

	def __init__(self, name, message, python ,detail) :
		self.args = ("%s\n%s\ndetail: %s %s" % (name, message, python, detail),)
		self.name = name
		self.message = message
		self.python	= python
		self.detail	= detail

	def get_advice(self):
		
		if(self.name == 'org.freedesktop.DBus.Error.UnknownMethod'):
			if(self.detail == 'on connect'):
				return "Cannot find pulseaudio dbus server.\nYou can try to set the environment variable PULSE_DBUS_SERVER\n to the pulseaudio dbus service PULSE_DBUS_SERVER='unix:path=PATH_TO SERVICE'."
			else:
				return "Cannot connect to pulseaudio-equalizer.\nMake sure pulseaudio-equalizer is installed and modules are loded by system.\nTry 'sudo apt install pulseaudio-equalizer' \nand/or 'pactl load-module module-equalizer-sink'\nor configure '/etc/pulse/default.pa'"
			
		if((self.name == 'org.freedesktop.DBus.Error.FileNotFound') and (self.detail == 'on connect')):
			return "Cannot connect to pulseaudio dbus server.\nPlease load the module 'module-dbus-protocol' via \n'pactl load-module module-dbus-protocol'\nor configure '/etc/pulse/default.pa'"
			
		if((self.name == org.freedesktop.DBus.Error.ServiceUnknown) and (self.detail == 'on connect')):
			return "Cannot find pulseaudio dbus server.\nYou can try to set the environment variable PULSE_DBUS_SERVER to the pulseaudio dbus service\n PULSE_DBUS_SERVER='unix:path=PATH_TO SERVICE'."
			
