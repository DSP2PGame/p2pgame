from ui.board import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *

MY_PIXEL_COLOR = "blue"
OTHER_PIXEL_COLOR = "pink"

class PlayerProfile(object):
	def __init__(self, power = None, x = None, y = None):
		self.power = power
		self.x = x
		self.y = y 

def askGameStatus(playerPos, gameStatus, lock):
	pass

def chooseInitGrid(playerPos, gameStatus, lock):
	pass

def paintOther(gameBoard, otherProfile, gameStatus, lock):
	pass

def paintMyself(gameBoard, myProfile, gameStatus, lock):
	myProfile.pix = PixelWidget(gameBoard)
	myProfile.pix.resize(GRID_LEN, GRID_LEN)
	myProfile.pix.setAutoFillBackground(True)
	myProfile.pix.setPalette(QPalette(QColor(MY_PIXEL_COLOR)))
	myProfile.pix.setFocusPolicy(Qt.StrongFocus)
	myProfile.pix.move(myProfile.x * GRID_LEN, myProfile.y * GRID_LEN)
	myProfile.pix.gameStatus = gameStatus
	myProfile.pix.profile = myProfile
	myProfile.pix.lock = lock
