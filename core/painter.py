from PyQt4.QtCore import *
from ui.board import *
from core.player import *

class MyPainter(QObject):
	paintNewOtherSignal = pyqtSignal(int)
	otherMoveSignal = pyqtSignal(int)

	def __init__(self, gameBoard, playerPos):
		super(QObject, self).__init__()
		self.gameBoard = gameBoard
		self.playerPos = playerPos
	
	def connectSignal(self):
		self.paintNewOtherSignal.connect(self.paintOther)
		self.otherMoveSignal.connect(self.moveOther)
	
	def moveOther(self, ID):
		self.playerPos[ID].pix.move(self.playerPos[ID].x * GRID_LEN, self.playerPos[ID].y * GRID_LEN)
	
	def paintOther(self, ID):
		self.playerPos[ID].pix = QWidget(self.gameBoard)
		self.playerPos[ID].pix.resize(GRID_LEN, GRID_LEN)
		self.playerPos[ID].pix.setAutoFillBackground(True)
		self.playerPos[ID].pix.setPalette(QPalette(QColor(OTHER_PIXEL_COLOR)))
		self.playerPos[ID].pix.setFocusPolicy(Qt.StrongFocus)
		print self.playerPos[ID].x * GRID_LEN, self.playerPos[ID].y * GRID_LEN
		self.playerPos[ID].pix.move(self.playerPos[ID].x * GRID_LEN, self.playerPos[ID].y * GRID_LEN)
		self.playerPos[ID].pix.show()

	def paintMyself(self, myProfile, gameStatus, lock):
		myProfile.pix = PixelWidget(self.gameBoard)
		myProfile.pix.resize(GRID_LEN, GRID_LEN)
		myProfile.pix.setAutoFillBackground(True)
		myProfile.pix.setPalette(QPalette(QColor(MY_PIXEL_COLOR)))
		myProfile.pix.setFocusPolicy(Qt.StrongFocus)
		myProfile.pix.move(myProfile.x * GRID_LEN, myProfile.y * GRID_LEN)
		myProfile.pix.profile = myProfile
		myProfile.pix.gameStatus = gameStatus
		myProfile.pix.lock = lock