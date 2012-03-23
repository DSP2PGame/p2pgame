import SocketServer
from core.peer_server import *

def getFreePort(gvar):
	print "Get Port Number & Start Peer Server"
	gvar.myPort = 10000
	while True:
		try:
			gvar.server = SocketServer.UDPServer(("", gvar.myPort), PeerUDPHandler)
		except IOError:
			gvar.myPort += 1
		else:
			break;
	gvar.server.gvar = gvar
	t = threading.Thread(target=peerRecThread, name = "PeerReceivingThread", kwargs={"server":server})
	t.start()

def peerRecThread(server):
	server.serve_forever()
