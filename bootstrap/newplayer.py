import SocketServer
import threading
import pickle

def getFreePort(playerPos, gameStatus, lock):
	port = 10000
	while True:
		try:
			server = SocketServer.UDPServer(("", port), PeerUDPHandler)
			#server.serve_forever()
		except IOError:
			port += 1
		else:
			break;
	server.playerPos = playerPos
	server.gameStatus = gameStatus
	server.lock = lock
	t = threading.Thread(target=peerRecThread, name = "PeerReceivingThread", kwargs={"server":server})
	t.start()
	return (server, port)

def peerRecThread(server):
	server.serve_forever()

class PeerUDPHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		data = pickle.loads(self.request[0].strip())
		socket = self.request[1]
					
