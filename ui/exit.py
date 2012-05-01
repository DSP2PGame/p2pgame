from PyQt4.QtCore import *
import sys
from core.send_message import *
import time

class ExitButtonBehavior(QObject):
	def __init__(self, gvar, mainWidget):
		super(QObject, self).__init__()
		self.gvar = gvar 
		self.mainWidget = mainWidget 
	
	def clickExitButton(self):
		self.gvar.lock.acquire()
		if self.gvar.ss is not None:
			exc = send_tcp_msg(self.gvar.ss, (10, self.gvar.myID))
			if exc is not None: # server is down
				multicast_leave_msg(self.gvar.myID)	
		else:
			multicast_leave_msg(self.gvar, self.gvar.myID)	
			
		time.sleep(1) #TODO
		self.mainWidget.close()
