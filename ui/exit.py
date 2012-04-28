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
			send_tcp_msg(self.gvar.ss, (10, self.gvar.myID))
		time.sleep(1) #TODO
		self.mainWidget.close()
