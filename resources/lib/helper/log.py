import xbmc

def log(text):
	xbmc.log("eq: " + text, xbmc.LOGDEBUG)
	
def loginfo(text):
	xbmc.log("eq: " + text, xbmc.LOGINFO)

def logerror(text):
	xbmc.log("eq: " + text, xbmc.LOGERROR)
	
