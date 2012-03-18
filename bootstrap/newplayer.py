import SocketServer
import threading
import pickle
from core.peer_server import *

def getFreePort(playerPos, gameStatus, hasStatus, canMoveSignal, lock, myPainter):

	print "Get Port Number & Start Peer Server"

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
	server.canMoveSignal = canMoveSignal
	server.lock = lock
	server.myPainter = myPainter
	t = threading.Thread(target=peerRecThread, name = "PeerReceivingThread", kwargs={"server":server})
	t.start()
	return (server, port)

def peerRecThread(server):
	server.serve_forever()
