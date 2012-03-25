from PyQt4.QtCore import *
from core.player import *
from const import *
from ui.board import *

class MyPainter(QObject):
	paintNewOtherSignal = pyqtSignal(int)
	otherMoveSignal = pyqtSignal(int)

	def __init__(self, gameBoard, playerPos):
		super(QObject, self).__init__()
		self.gameBoard = gameBoard
		self.playerPos = playerPos
		self.paintNewOtherSignal.connect(self.paintOther)
                self.otherMoveSignal.connect(self.moveOther)
	
	def moveOther(self, ID):
		print "PAINTER: Move Player{} Signal".format(ID)
		self.playerPos[ID].pix.move(self.playerPos[ID].x * GRID_LEN, self.playerPos[ID].y * GRID_LEN)
	
	def paintOther(self, ID):
		print "PAINTER: New Player{} Appears on Board".format(ID)
		self.playerPos[ID].pix = QWidget(self.gameBoard)
		self.playerPos[ID].pix.resize(GRID_LEN, GRID_LEN)
		self.playerPos[ID].pix.setAutoFillBackground(True)
		self.playerPos[ID].pix.setPalette(QPalette(QColor(OTHER_PIXEL_COLOR)))
		self.playerPos[ID].pix.setFocusPolicy(Qt.NoFocus)
		self.playerPos[ID].pix.move(self.playerPos[ID].x * GRID_LEN, self.playerPos[ID].y * GRID_LEN)
		self.playerPos[ID].pix.show()

	def paintMyself(self, gvar):
		print "PAINTER: Paint Myself"
		myProfile = gvar.playerPos[gvar.myID]
		myProfile.pix = PixelWidget(gvar.gameUI.gameBoard)
		myProfile.pix.resize(GRID_LEN, GRID_LEN)
		myProfile.pix.setAutoFillBackground(True)
		myProfile.pix.setPalette(QPalette(QColor(MY_PIXEL_COLOR)))
		myProfile.pix.setFocusPolicy(Qt.StrongFocus)
		myProfile.pix.move(myProfile.x * GRID_LEN, myProfile.y * GRID_LEN)
		myProfile.pix.profile = myProfile
