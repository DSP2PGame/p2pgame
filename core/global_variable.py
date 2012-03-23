import threading
from PyQt4.QtCore import *
from core.painter import *
from const import *
from core.painter import *

class GlobalVariable(QObject):
	def __init__(self, gameUI):
		super(QObject, self).__init__()
		self.gameUI = gameUI
		self.lock = threading.Lock()
		self.gameStatus = {}
		self.hasStatus = threading.Event()
		self.hasStatus.clear()
		self.canMoveSignal = threading.Event()
		self.playerPos = {}
		self.myID = None
		self.myGroup = None
		self.myPower = None
		self.server = None
		self.myPort = None
		self.clientPP = None
		self.myPainter = MyPainter(self.gameUI.gameBoard, playerPos)

		for i in xrange(0, NUM_GRID_PER_BOARD_ROW):
		        for j in xrange(0, NUM_GRID_PER_BOARD_ROW):
		                self.gameStatus[(i,j)] = -1 #unoccupied
