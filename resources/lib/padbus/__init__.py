import sys

if sys.version_info[0] > 2:
	from .dbus_basic_3 import PulseDBus
else:
	from .dbus_basic_2 import PulseDBus


from .pulseerror import PulseDBusError
from . import interface as DBusInterface


