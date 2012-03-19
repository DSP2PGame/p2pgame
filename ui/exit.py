from PyQt4.QtCore import *

class ExitButtonBehavior(QObject):
	def __init__(self, server, mainWidget):
		super(QObject, self).__init__()
		self.server = server
		self.mainWidget = mainWidget 
	
	def clickExitButton(self):
		self.server.shutdown()
		self.mainWidget.close()

