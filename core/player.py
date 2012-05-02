from PyQt4.QtGui import *
from PyQt4.QtCore import *
from core.send_message import *
from const import *
import time 

class PlayerProfile(object):
	def __init__(self, x = None, y = None, groupID = None, ID = None, conn = None):
		self.x = x
		self.y = y 
		self.groupID = groupID
		self.ID = ID
		self.conn = conn
		self.last_stime = time.time()
		self.have_score = False
		self.last_atime = time.time()

def calc_global_leader(gvar):
	clientPP = gvar.clientPP
	old_gl_leader = gvar.gl_leader
	gvar.gl_leader = gvar.myID
	for key in clientPP.iterkeys():
		if gvar.gl_leader > key:
			gvar.gl_leader = key
	if gvar.gl_leader == gvar.myID:
		for key in gvar.playerPos.iterkeys():
			gvar.playerPos[key].last_atime = time.time()
	print "GL: {}".format(gvar.gl_leader)

def calc_group_leader(gvar):
	clientPP = gvar.clientPP
	old_gp_leader = gvar.gp_leader
	gvar.gp_leader = gvar.myID
	for key in clientPP.iterkeys():
		if gvar.gp_leader > key and clientPP[key][2] == gvar.myGroup:
			gvar.gp_leader = key
	if gvar.gp_leader == gvar.myID:
		for key in gvar.playerPos.iterkeys():
			gvar.playerPos[key].last_atime = time.time()
	print "GP: {}".format(gvar.gp_leader)

def putNewPlayerOnBoard(gvar):

	def put_myself_to_00():
		gvar.hasStatus.set()
		gvar.playerPos[gvar.myID].x = 0
		gvar.playerPos[gvar.myID].y = 0
		gvar.gameStatus[(0,0)] = gvar.myID
		gvar.score[gvar.myID] = 0
		
	print "Start Put New Player On Board"
	if len(gvar.clientPP) == 1: #only myself
		put_myself_to_00()
	else:
		while True:
			if gvar.gp_leader == gvar.myID: #only me in my group, I should ask others like global leader
				if gvar.gl_leader == gvar.myID: #only myself in game
					put_myself_to_00()
					break
				else:
					conn = gvar.playerPos[gvar.gl_leader].conn
					conn.send_msg((1,))
			else: # ask group leader
				print "ask group leader"
				conn = gvar.playerPos[gvar.gp_leader].conn
				conn.send_msg((1,))
			good = False
			t = time.time()
			while time.time() - t <= 3:
				QCoreApplication.processEvents(QEventLoop.WaitForMoreEvents)
				if gvar.hasStatus.is_set():
					good = True
					break
			if good:
				break
			calc_global_leader(gvar)
			calc_group_leader(gvar)
		chooseInitGrid(gvar)

	for p in gvar.playerPos.iterkeys():
		if p != gvar.myID and gvar.playerPos[p].x is not None:
			gvar.myPainter.paintOther(p)
		else:
			gvar.myPainter.paintMyself(gvar)

def move_to_grid(grid, gvar):
	print "Has Permission To Occupy"
	multicastMove(grid, gvar)
	if (gvar.playerPos[gvar.myID].x != None):
		gvar.gameStatus[(gvar.playerPos[gvar.myID].x, gvar.playerPos[gvar.myID].y)] = -1
	gvar.playerPos[gvar.myID].x = grid[0]
	gvar.playerPos[gvar.myID].y = grid[1]
	gvar.gameStatus[grid] = gvar.myID

def chooseInitGrid(gvar):
	print "Choose Init Grid"
	for grid in gvar.gameStatus.iterkeys():
		if gvar.gameStatus[grid] == -1:
			print "choose {}".format(grid)
			if canMove(grid, gvar): 
				move_to_grid(grid, gvar)
				print "move to {}".format(grid)
				break
			else:
				print "can not move"
	if gvar.playerPos[gvar.myID].x == None:
		print "Something's Wrong!"
	gvar.playerPos[gvar.myID].gvar = gvar
	print "Finish Putting Grid"

def canMove(grid, gvar): 
	owner = findOwer(grid, gvar)
	print "Owner of Grid:{} {}".format(grid, owner)
	print "owner:{}, myID:{}, grid:{}, gameStatus:{}".format(owner, gvar.myID, grid, gvar.gameStatus[grid])
	if owner == gvar.myID and gvar.gameStatus[grid] != -1:
		print "I'm the Owner, and the grid already has someone else"
		return False
	if owner != -1 and owner != gvar.myID: # has owner, it's not myself
		print "Send Request to Owner"
		gvar.canMoveSignal.clear()
		conn = gvar.playerPos[owner].conn
		conn.send_msg((3, grid))
		t = time.time()
		while time.time() - t <= 3:
			QCoreApplication.processEvents(QEventLoop.WaitForMoreEvents)
			if gvar.canMoveSignal.is_set():
				break
		if (gvar.gameStatus[grid] == -3): #can move
			pass
		else:
			return False
	return True

def findOwer(grid, gvar):
	owner = -1
	for i in xrange(-OWN_N, OWN_N + 1):
		for j in xrange(-OWN_N, OWN_N + 1):
			if (checkRange(grid[0] + i) and checkRange(grid[1] + j) and gvar.gameStatus[(grid[0]+i, grid[1]+j)] >= 0):
				if (owner == -1 or owner < gvar.gameStatus[(grid[0]+i, grid[1]+j)]):
					owner = gvar.gameStatus[(grid[0]+i, grid[1]+j)]
	return owner

def updatePlayerPos(newStatus, gameStatus, playerPos):
	print "Update GameStatus and PlayerPos"
	for grid in newStatus:
		gameStatus[grid] = newStatus[grid]
		if newStatus[grid] >= 0:
			playerPos[newStatus[grid]].x = grid[0]
			playerPos[newStatus[grid]].y = grid[1]
		else: 
			gameStatus[grid] = -1
