from PyQt4.QtGui import *
from PyQt4.QtCore import *
from core.send_message import *
from const import *

class PlayerProfile(object):
	def __init__(self, power = None, x = None, y = None, groupID = None, ip = None, port = None, ID = None):
		self.power = power
		self.x = x
		self.y = y 
		self.groupID = groupID
		self.ip = ip
		self.port = port
		self.ID = ID

def askGameStatus(clientPP, myPort, hasStatus, myID, myPower, myGroup):
	print "Ask Game Status"
	for x in iter(clientPP):
		if (clientPP[x][2] == myGroup):	
			print "Ask Peer % {} {} About Game Status".format(x[0], x[1])
			sendMsg(x[0], x[1], (1, myPort, myID, myGroup, myPower)) #Ask For Game Status
	hasStatus.wait(10) # TimeOut = 10s
	print "Got Game Status"

def chooseInitGrid(myID, playerPos, gameStatus, lock, clientPP, myPort, myPower, myGroup, canMoveSignal):
	print "Choose Init Grid"
	for grid in gameStatus:
		if gameStatus[grid] == -1:
			print "choose {}".format(grid)
			if canMove(myID, grid, playerPos, gameStatus, lock, clientPP, myPort, myPower, myGroup, canMoveSignal):
				print "move to {}".format(grid)
				break
			else:
				print "can not move"
	if playerPos[myID].x == None:
		print "Something's Wrong!"
	playerPos[myID].playerPos = playerPos
	playerPos[myID].gameStatus = gameStatus
	playerPos[myID].lock = lock
	playerPos[myID].clientPP = clientPP
	playerPos[myID].canMoveSignal = canMoveSignal
	print "Finish Putting Grid"

def canMove(myID, grid, playerPos, gameStatus, lock, clientPP, myPort, myPower, myGroup, canMoveSignal):
	owner = findOwer(grid, playerPos, gameStatus)
	print "Owner of Grid:{} {}".format(grid, owner)
	if owner == myID and gameStatus[grid] != -1:
		print "I'm the Owner, and the grid already has someone else"
		return False
	if owner != -1 and owner != myID: # has owner, it's not myself
		print "Send Request to Owner"
		canMoveSignal.clear()
		sendMsg(playerPos[owner].ip, playerPos[owner].port, (3, grid, myPort, myID, myPower, myGroup))
		canMoveSignal.wait(10) #Timeout=10s
		if (gameStatus[grid] == -3): #can move
			pass
		else:
			return False
	print "Has Permission To Occupy"
	lock.acquire()
	multicastMove(myID, myPort, myPower, myGroup, grid, clientPP)
	if (playerPos[myID].x != None):
		gameStatus[(playerPos[myID].x, playerPos[myID].y)] = -1
	playerPos[myID].x = grid[0]
	playerPos[myID].y = grid[1]
	gameStatus[grid] = myID
	lock.release()
	return True

def findOwer(grid, playerPos, gameStatus):
	owner = -1
	for i in xrange(-OWN_N, OWN_N + 1):
		for j in xrange(-OWN_N, OWN_N + 1):
			if (checkRange(grid[0] + i) and checkRange(grid[1] + j) and gameStatus[(grid[0]+i, grid[1]+j)] >= 0):
				if (owner == -1 or playerPos[owner].power < playerPos[gameStatus[(grid[0]+i, grid[1]+j)]].power):
					owner = gameStatus[(grid[0]+i, grid[1]+j)]
	return owner

def updatePlayerPos(newStatus, gameStatus, playerPos):
	print "Update GameStatus and PlayerPos"
	for grid in newStatus:
		gameStatus[grid] = newStatus[grid]
		if newStatus[grid] != -1:
			playerPos[newStatus[grid]].x = grid[0]
			playerPos[newStatus[grid]].y = grid[1]

