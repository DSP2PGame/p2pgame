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
		self.gp_leader = None #group leader
		self.gl_leader = None #global leader
		self.myPort = None
		self.server = None
		self.server_thread = None
		self.ps_thread = None
		self.ss = None # tcp socket with bootstrapping server
		self.clientPP = None
		self.myPainter = MyPainter(self.gameUI.gameBoard, self.playerPos)
		self.start_time = None
		self.can_move = True
		self.score = {}

		for i in xrange(0, NUM_GRID_PER_BOARD_ROW):
		        for j in xrange(0, NUM_GRID_PER_BOARD_ROW):
		                self.gameStatus[(i,j)] = -1 #unoccupied
		
		print "End of Init"
