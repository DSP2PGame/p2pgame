import SocketServer
import threading
import pickle
from core.peer_server import *

def getFreePort(playerPos, gameStatus, hasStatus, lock):
	port = 10000
	while True:
		try:
			server = SocketServer.UDPServer(("", port), PeerUDPHandler)
		except IOError:
			port += 1
		else:
			break;
	server.playerPos = playerPos
	server.gameStatus = gameStatus
	server.hasStatus = hasStatus
	server.lock = lock
	t = threading.Thread(target=peerRecThread, name = "PeerReceivingThread", kwargs={"server":server})
	t.start()
	return (server, port)

def peerRecThread(server):
	server.serve_forever()
