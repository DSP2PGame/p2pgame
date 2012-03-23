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

def putNewPlayerOnBoard(gvar):
	if len(gvar.clientPP == 0):
		gvar.hasStatus.set()
		gvar.lock.acquire()
		gvar.playerPos[gvar.myID].x = 0
		gvar.playerPos[gvar.myID].y = 0
		gvar.gameStatus[(0,0)] = gvar.myID
		gvar.playerPos[gvar.myID].gvar = gvar
		gvar.lock.release()
	else:
		for pp in gvar.clientPP.iteritems():
			playerPos[pp[1][0]] = PlayerProfile(power = pp[1][1], groupID = pp[1][2], ip = pp[0][0], port = pp[0][1], ID = pp[1][0]
		askGameStatus(gvar)
		chooseInitGrid(gvar)
		for other in gvar.playerPos:
			if other != gvar.myID
				gvar.myPainter.paintOther(other)
			else:
				gvar.myPainter.paintMyself(gvar)

def askGameStatus(gvar):
	print "Ask Game Status"
	for x in iter(gvar.clientPP):
		if (gvar.clientPP[x][2] == gvar.myGroup):	
			print "Ask Peer % {} {} About Game Status".format(x[0], x[1])
			sendMsg(x[0], x[1], (1, gvar.myPort, gvar.myID, gvar.myGroup, gvar.myPower)) #Ask For Game Status
	gvar.hasStatus.wait(10) # TODO TimeOut = 10s
	print "Got Game Status"

def chooseInitGrid(gvar):
	print "Choose Init Grid"
	for grid in gvar.gameStatus:
		if gvar.gameStatus[grid] == -1:
			print "choose {}".format(grid)
			if canMove(grid, gvar): 
				print "move to {}".format(grid)
				break
			else:
				print "can not move"
	if gvar.playerPos[myID].x == None:
		print "Something's Wrong!"
	playerPos[myID].gvar = gvar
	print "Finish Putting Grid"

def canMove(grid, gvar): 
	owner = findOwer(grid, gvar.playerPos, gvar.gameStatus)
	print "Owner of Grid:{} {}".format(grid, owner)
	if owner == myID and gameStatus[grid] != -1:
		print "I'm the Owner, and the grid already has someone else"
		return False
	if owner != -1 and owner != myID: # has owner, it's not myself
		print "Send Request to Owner"
		gvar.canMoveSignal.clear()
		sendMsg(gvar.playerPos[owner].ip, gvar.playerPos[owner].port, (3, grid, gvar.myPort, gvar.myID, gvar.myPower, gvar.myGroup))
		gvar.canMoveSignal.wait(10) #Timeout=10s
		if (gvar.gameStatus[grid] == -3): #can move
			pass
		else:
			return False
	print "Has Permission To Occupy"
	gvar.lock.acquire()
	multicastMove(grid, gvar)
	if (gvar.playerPos[gvar.myID].x != None):
		gvar.gameStatus[(gvar.playerPos[gvar.myID].x, gvar.playerPos[gvar.myID].y)] = -1
	gvar.playerPos[gvar.myID].x = grid[0]
	gvar.playerPos[gvar.myID].y = grid[1]
	gvar.gameStatus[grid] = gvar.myID
	gvar.lock.release()
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

