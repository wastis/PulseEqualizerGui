#	This file is part of PulseEqualizerGui for Kodi.
#
#	Copyright (C) 2021 wastis    https://github.com/wastis/PulseEqualizerGui
#
#	PulseEqualizerGui is free software; you can redistribute it and/or modify
#	it under the terms of the GNU Lesser General Public License as published
#	by the Free Software Foundation; either version 3 of the License,
#	or (at your option) any later version.
#
#

#
#  dbus wraper for Python 3.x
#

import os
import sys

from . import dbussy as dbus
from . import interface as IF

from .dbussy import DBUS
from .dbussy import DBusError

from .pulseerror import PulseDBusError

from basic import log

class PulseDBus:
	def __init__( self, *_args, **_kwargs ):
		try:
			self.conn = None
			address = self.get_pulse_dbus()
			if address:
				self.conn = dbus.Connection.open(address,0)
		except DBusError as e:
			self.handle_exception(e,"python3","on connect")

	@staticmethod
	def check_dbus_address(address):
		if not address:
			return False

		if "=" in address:
			_,addr =  address.split("=")
		else:
			addr = address
		if os.path.exists(addr.strip()):
			return True

		log("dbus socket does not exist: %s" % addr)
		return False

	@classmethod
	def get_pulse_dbus(cls):
		address=None

		# environment variable
		try:
			address = os.environ['PULSE_DBUS_SERVER']
		except KeyError:
			log("environment variable PULSE_DBUS_SERVER is not set")
			pass
		else:
			if cls.check_dbus_address(address):
				log("got dbus address from environment variable PULSE_DBUS_SERVER: %s" % address)
				return address

		# from session bus
		try:
			conn = dbus.Connection.bus_get(DBUS.BUS_SESSION,private = False)

			request = dbus.Message.new_method_call (
				destination = dbus.valid_bus_name('org.PulseAudio1'),
				path = dbus.valid_path('/org/pulseaudio/server_lookup1'),
				iface = IF.INTERFACE_PROPERTIES,
				method = "Get"
			)

			request.append_objects("ss", dbus.valid_interface('org.PulseAudio.ServerLookup1'),'Address')
			reply = conn.send_with_reply_and_block(request)

			address = reply.expect_return_objects("v")[0][1]
		except DBusError:
			pass
		else:
			if cls.check_dbus_address(address):
				log("got dbus address from SESSION_BUS: %s" % address)
				return address
		# from XDG_RUNTIME_DIR

		try:
			address = 'unix:path=' + os.environ['XDG_RUNTIME_DIR'] + "/pulse/dbus-socket"
		except KeyError:
			pass
		else:
			if cls.check_dbus_address(address):
				log("got dbus address from XDG_RUNTIME_DIR: %s" % address)
				return address

		# guessing
		address = "unix:path=/run/user/%s/pulse/dbus-socket" % os.geteuid()
		if cls.check_dbus_address(address):
			log("guessing dbus address: %s" % address)
			return address

		log("pulseaudio dbus-socket not found.")
		return None

	def get_property(self, interface, d_path, p_name):
		if not self.conn: return None
		try:
			request = dbus.Message.new_method_call (
				destination = dbus.valid_bus_name(interface),
				path = d_path,
				iface = IF.INTERFACE_PROPERTIES,
				method = "Get"
			)
			request.append_objects("ss", dbus.valid_interface(interface),p_name)
			reply = self.conn.send_with_reply_and_block(request)

			return reply.expect_return_objects("v")[0][1]
		except DBusError as e: self.handle_exception(e,"python3","on dbus function call")

	def set_property(self, interface, d_path, p_name, *p_val):
		if not self.conn: return None
		try:
			request = dbus.Message.new_method_call (
				destination = dbus.valid_bus_name(interface),
				path = d_path,
				iface = IF.INTERFACE_PROPERTIES,
				method = "Set"
			)
			request.append_objects("ssv", dbus.valid_interface(interface),p_name, p_val)
			self.conn.send_with_reply_and_block(request)
		except DBusError as e: self.handle_exception(e,"python3","on dbus function call")

	def call_func(self, interface, d_path, func, *args):
		if not self.conn: return None
		try:
			request = dbus.Message.new_method_call (
				destination = dbus.valid_bus_name(interface),
				path = d_path,
				iface = dbus.valid_bus_name(interface),
				method = func
			)
			if len(args) > 0:
				request.append_objects(*args)
			reply = self.conn.send_with_reply_and_block(request).all_objects

			if   len(reply) == 0 :return None
			elif len(reply) == 1 :return reply[0]
			else:	return reply
		except DBusError as e: self.handle_exception(e,"python3","on dbus function call")

	@staticmethod
	def handle_exception(e,python,func):
		raise PulseDBusError(e.name,e.message,python,func)
