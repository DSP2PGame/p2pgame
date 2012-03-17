import SocketServer
import pickle

SERVER_HOST = "localhost"
SERVER_PORT = 9999

class ServerUDPHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		data = pickle.loads(self.request[0].strip())
		socket = self.request[1]
		if data[0] == 0: # New Player Register
			print "New Player From {}".format(self.client_address[0])

def startServer():
	server = SocketServer.UDPServer((SERVER_HOST, SERVER_PORT), ServerUDPHandler)
	server.serve_forever()
