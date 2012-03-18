from ui.board import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from core.send_message import *

MY_PIXEL_COLOR = "blue"
OTHER_PIXEL_COLOR = "pink"

class PlayerProfile(object):
	def __init__(self, power = None, x = None, y = None):
		self.power = power
		self.x = x
		self.y = y 

def askGameStatus(clientPP, myPort, hasStatus, myID, myPower):
	#TEST USE: Ask everyone. TODO:Only ask one group
	for x in iter(clientPP):
		print x[0], x[1]
		sendMsg(x[0], x[1], (1, myPort, myID, myPower)) #Ask For Game Status
	hasStatus.wait(10) # TimeOut = 10s

def chooseInitGrid(myID, playerPos, gameStatus, lock, clientPP):
	for grid in gameStatus:
		if gameStatus[grid] == -1:
			print "choose {}".format(grid)
			if canMove(myID, grid, playerPos, gameStatus, lock, clientPP):
				print "move to {}".format(grid)
				break
			else:
				print "can not move"
	if playerPos[myID].x == None:
		print "Something's Wrong!"

def canMove(myID, grid, playerPos, gameStatus, lock, clientPP, myPort, myPower, canMoveSignal):
	ower = findOwer(grid, playerPos, gameStatus)
	if ower != -1: # has owner
		canMoveSignal.clear()
		sendMsg()#TODO
		canMoveSignal.wait(10) #Timeout=10s
		if (gameStatus[grid] == -2): #can move
			pass
		else:
			return False
	lock.acquire()
	multicastMove(myID, myPort, myPower, grid, clientPP)
	playerPos[myID].x = grid[0]
	playerPos[myID].y = grid[1]
	gameStatus[grid] = myID
	lock.release()
	return True

def findOwer(grid, playerPos, gameStatus)
	return -1

def multicastMove(myID, myPort, myPower, grid, clientPP)
	pass

def paintOther(gameBoard, otherProfile, gameStatus, lock):
	otherProfile.pix = QWidget(gameBoard)
	otherProfile.pix.resize(GRID_LEN, GRID_LEN)
	otherProfile.pix.setAutoFillBackground(True)
	otherProfile.pix.setPalette(QPalette(QColor(OTHER_PIXEL_COLOR)))
	otherProfile.pix.setFocusPolicy(Qt.StrongFocus)
	otherProfile.pix.move(otherProfile.x * GRID_LEN, otherProfile.y * GRID_LEN)

def paintMyself(gameBoard, myProfile, gameStatus, lock):
	myProfile.pix = PixelWidget(gameBoard)
	myProfile.pix.resize(GRID_LEN, GRID_LEN)
	myProfile.pix.setAutoFillBackground(True)
	myProfile.pix.setPalette(QPalette(QColor(MY_PIXEL_COLOR)))
	myProfile.pix.setFocusPolicy(Qt.StrongFocus)
	myProfile.pix.move(myProfile.x * GRID_LEN, myProfile.y * GRID_LEN)
	myProfile.pix.profile = myProfile
	myProfile.pix.gameStatus = gameStatus
	myProfile.pix.lock = lock

def updatePlayerPos(newStatus, gameStatus, playerPos):
	for grid in newStatus:
		gameStatus[grid] = newStatus[grid]
		if newStatus[grid] != -1:
			playerPos[newStatus[grid]].x = grid[0]
			playerPos[newStatus[grid]].y = grid[1]

