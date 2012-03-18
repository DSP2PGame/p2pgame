import SocketServer
import pickle
from core.send_message import *
from core.player import *

class PeerUDPHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		data = pickle.loads(self.request[0].strip())
		socket = self.request[1]

		if (data[0] == 1): #request game status, add new player info
			self.server.lock.acquire()
			self.server.clientPP[(self.client_address[0], data[1])] = (data[2], data[3])
			sendMsg(self.client_address[0], data[1],(2, self.server.gameStatus)) #return game status
			self.server.lock.release()
		elif (data[0] == 2): #get game status
			if self.server.hasStatus.is_set():
				pass
			else:
				self.server.lock.acquire()
				newStatus = data[1];
				updatePlayerPos(newStatus, self.server.gameStatus, self.server.playerPos)
				self.server.lock.release()
				self.server.hasStatus.set()
				print "Got Game Status From {}".format(self.client_address[0])
