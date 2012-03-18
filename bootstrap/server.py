import SocketServer
import pickle

SERVER_HOST = "192.168.1.7"
SERVER_PORT = 9999

serverPP = {} # (ip,port):(id,power,groupID) server keeps information about all active players' profile #TODO only one group
GlobalID = 0 # TODO: is it too simple?

class ServerUDPHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		data = pickle.loads(self.request[0].strip())
		socket = self.request[1]
		if data[0] == 0: # New Player Register
			print "New Player From {}".format(self.client_address[0])
			power = assignPower()
			groupID = assignGroupID()
			global GlobalID
			socket.sendto(pickle.dumps((GlobalID, power, groupID, serverPP)), self.client_address)
			serverPP[(self.client_address[0], data[1])] = (GlobalID, power, groupID)
			GlobalID += 1

# TODO: Need More Complex And Fair Method
def assignPower():
	global GlobalID
	return GlobalID

# TODO
def assignGroupID():
	return 1

def startServer():
	server = SocketServer.UDPServer(("", SERVER_PORT), ServerUDPHandler)
	server.serve_forever()

