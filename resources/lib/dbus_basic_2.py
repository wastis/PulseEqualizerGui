import dbus
import interface as IF
import sys,os
from pulseerror import PulseDBusError


class PULSE_DBUS:
	def __init__( self, *args, **kwargs ):
		destination = 'org.PulseAudio1' 
		object_path = '/org/pulseaudio/server_lookup1' 
		interface_name = 'org.PulseAudio.ServerLookup1'
		#address = 'unix:path=/run/user/1000/pulse/dbus-socket'
		
		try:
			if 'PULSE_DBUS_SERVER' in os.environ:
				address = os.environ['PULSE_DBUS_SERVER']
				
			else:
				bus = dbus.SessionBus()
				server_lookup = bus.get_object(destination,object_path)
				address = server_lookup.Get(interface_name, 'Address', dbus_interface=IF.INTERFACE_PROPERTIES)
			self.conn = dbus.connection.Connection(address)
		except dbus.exceptions.DBusException as e:self.handle_exception(e,"python2","on connect")
			
		
	def print_introspect(self, interface, d_path ):
		try:
			res =  self.conn.call_blocking(interface,d_path,IF.INTERFACE_INTROSPECTABLE,"Introspect","",())
			sys.stdout.write(res)
		except dbus.exceptions.DBusException as e:self.handle_exception(e,"python2","on dbus function call")
			

	def get_property(self, interface, d_path, p_name):
		try:
			return self.conn.call_blocking(interface,d_path,IF.INTERFACE_PROPERTIES,"Get","ss",(interface,p_name))
		except dbus.exceptions.DBusException as e:self.handle_exception(e,"python2","on dbus function call")
			
			
	def set_property(self, interface, d_path, p_name, *p_val):
		try:
			return self.conn.call_blocking(interface,d_path,IF.INTERFACE_PROPERTIES,"Set","ssv",(interface,p_name, p_val[1]))
		except dbus.exceptions.DBusException as e:self.handle_exception(e,"python2","on dbus function call")
			
		
	def get_all_property(self, interface, d_path):
		try:
			return self.conn.call_blocking(interface,d_path,IF.INTERFACE_PROPERTIES,"GetAll","s",(interface,))
		except dbus.exceptions.DBusException as e:self.handle_exception(e,"python2","on dbus function call")
			
	def call_func(self, interface, d_path, func, *args):
		try:
			if(len(args)>0):
				sig = args[0]
				args = args[1:]
			else: 
				sig = ''
				args = ()
					
			return self.conn.call_blocking(interface,d_path,interface,func,sig,args)
		except dbus.exceptions.DBusException as e: self.handle_exception(e,"python2","on dbus function call")
			
	@staticmethod
	def handle_exception(e,python,func):
		raise(PulseDBusError(e._dbus_error_name,e.message,python,func))
		


