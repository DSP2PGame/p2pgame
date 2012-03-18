import SocketServer
import pickle
from core.send_message import *
from core.player import *
from const import *

class PeerUDPHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		data = pickle.loads(self.request[0].strip())
		socket = self.request[1]

		if (data[0] == 1): #request game status, add new player info, (1, myPort, myID, myGroup, myPower)
			print "SERVER: receive game status request from ID{}".format(data[2])
			print "SERVER: Put New Player's Info Into clientPP & playerPos"
			self.server.lock.acquire()
			self.server.clientPP[(self.client_address[0], data[1])] = (data[2], data[3], data[4])
			self.server.playerPos[data[2]] = PlayerProfile(ip = self.client_address[0], port = data[1], groupID = data[3], power = data[4], ID = data[2])
			print "SERVER: send game status to ID{}".format(data[2])
			sendMsg(self.client_address[0], data[1], (2, self.server.gameStatus)) #return game status
			self.server.lock.release()
		elif (data[0] == 2): #get game status
			print "SERVER: receive game status"
			if self.server.hasStatus.is_set():
				print "SERVER: already got it"
				pass
			else:
				print "SERVER: save game status and update game status"
				self.server.lock.acquire()
				newStatus = data[1];
				updatePlayerPos(newStatus, self.server.gameStatus, self.server.playerPos)
				self.server.lock.release()
				self.server.hasStatus.set()
				print "SERVER: Got Game Status From {}".format(self.client_address[0])
		elif (data[0] == 3): #receive a request for a grid, (3, grid, port, id, power, group)
			print "SERVER: receive a request for a grid {}".format(data[1])
			self.server.lock.acquire()
			if (self.server.gameStatus[data[1]] == -1): #-1: no one
				print "SERVER: no one occupy the grid, send approval"
				self.server.gameStatus[data[1]] = -2 # -2: reserve for someone
				sendMsg(self.client_address[0], data[2], (4, data[1])) #send approval
			else:
				print "SERVER: someone occupy the grid, send refusal"
				sendMsg(self.client_address[0], data[2], (5,)) #send refusal
			self.server.lock.release()
		elif (data[0] == 4): # receive approval
			print "SERVER: got approval for grid{}".format(data[1])
			self.server.lock.acquire()
			self.server.gameStatus[data[1]] = -3 #-3: can move
			self.server.lock.release()
			self.server.canMoveSignal.set()
		elif (data[0] == 5): # receive refusal
			print "SERVER: got refusal for grid"
			self.server.canMoveSignal.set()
		elif (data[0] == 6): # receive other's movement msg (6, myPort, myID, myPower, myGroup, grid)
			print "SERVER: recevie movement msg from {} {}".format(data[2], data[5])
			self.server.lock.acquire()
			if self.server.playerPos[data[2]].x == None:
				self.server.gameStatus[data[5]] = data[2]
				self.server.playerPos[data[2]].x = data[5][0]
				self.server.playerPos[data[2]].y = data[5][1]
				self.server.myPainter.paintNewOtherSignal.emit(data[2])
			else:
				self.server.gameStatus[(self.server.playerPos[data[2]].x, self.server.playerPos[data[2]].y)] = -1
				self.server.gameStatus[data[5]] = data[2]
				self.server.playerPos[data[2]].x = data[5][0]
				self.server.playerPos[data[2]].y = data[5][1]
				self.server.myPainter.otherMoveSignal.emit(data[2])
			self.server.lock.release()
