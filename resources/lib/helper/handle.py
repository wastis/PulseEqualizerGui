import os, sys, traceback
from .log import *
 

if sys.version_info[0] > 2:
	def handle(e):
		traceback = e.__traceback__
		while traceback:
			logerror("in: {}: {}".format(traceback.tb_frame.f_code.co_filename,traceback.tb_lineno))
			traceback = traceback.tb_next
		logerror("{}: {}".format(type(e).__name__, e.args))
else:
	def handle(e):
		lines = traceback.format_exc().splitlines()
		for l in lines:
			logerror(l)
		logerror("{}: {}".format(type(e).__name__, e.args))
