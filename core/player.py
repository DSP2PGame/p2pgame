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

def calc_global_leader(gvar):
	clientPP = gvar.clientPP
	gvar.gl_leader = gvar.myID
	for key in clientPP.iterkeys():
		if gvar.gl_leader > key:
			gvar.gl_leader = key

def calc_group_leader(gvar):
	clientPP = gvar.clientPP
	gvar.gp_leader = gvar.myID
	for key in clientPP.iterkeys():
		if gvar.gp_leader > key and clientPP[key][2] == gvar.myGroup:
			gvar.gp_leader = key

def putNewPlayerOnBoard(gvar):
	print "Start Put New Player On Board"
	gvar.lock.acquire()
	if len(gvar.clientPP) == 1: #only myself
		gvar.hasStatus.set()
		gvar.playerPos[gvar.myID].x = 0
		gvar.playerPos[gvar.myID].y = 0
		gvar.gameStatus[(0,0)] = gvar.myID
		gvar.lock.release()
	else:
		while True:
			if gvar.gp_leader == gvar.myID: #only me in my group, I should ask others like global leader
				if gvar.gl_leader == gvar.myID: #only myself in game
					gvar.hasStatus.set()
					gvar.playerPos[gvar.myID].x = 0
					gvar.playerPos[gvar.myID].y = 0
					gvar.gameStatus[(0,0)] = gvar.myID
					gvar.lock.release()
					break
				else:
					conn = gvar.playerPos[gvar.gl_leader].conn
					gvar.lock.release()
					if conn is not None:
						send_tcp_msg(conn, (1,))
			else: # ask group leader
				conn = gvar.playerPos[gvar.gp_leader].conn
				gvar.lock.release()
				if conn is not None:
					send_tcp_msg(conn, (1,))
			if gvar.hasStatus.wait(3): #TODO
				break
			gvar.lock.acquire()
			calc_global_leader(gvar)
			calc_group_leader(gvar)
		chooseInitGrid(gvar)

	gvar.lock.acquire()
	for p in gvar.playerPos.iterkeys():
		if p != gvar.myID and gvar.playerPos[p].x is not None:
			gvar.myPainter.paintOther(p)
		else:
			gvar.myPainter.paintMyself(gvar)
	gvar.lock.release()

def move_to_grid(grid, gvar):
	print "Has Permission To Occupy"
	multicastMove(grid, gvar)
	gvar.lock.acquire()
	if (gvar.playerPos[gvar.myID].x != None):
		gvar.gameStatus[(gvar.playerPos[gvar.myID].x, gvar.playerPos[gvar.myID].y)] = -1
	gvar.playerPos[gvar.myID].x = grid[0]
	gvar.playerPos[gvar.myID].y = grid[1]
	gvar.gameStatus[grid] = gvar.myID
	gvar.lock.release()

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
		if conn is not None:
			send_tcp_msg(conn, (3, grid))
		else:
			print "Error! can't connect to owner"
		gvar.canMoveSignal.wait(3) #TODO
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
		elif newStatus[grid] == -3:
			gameStatus[grid] = -1
