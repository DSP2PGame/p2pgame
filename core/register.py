from core.player import *
from const import *
import pickle
import socket

def newRegister(gvar):
	print "Send Register Msg To Server & Receive clientPP, ID, Power, GroupID"
	data = (0, gvar.myPort)
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.sendto(pickle.dumps(data), (SERVER_HOST, SERVER_PORT))
	received = pickle.loads(sock.recv(10240)) #TODO How large is enough?
	gvar.myID = received[0]
	gvar.myGroup = received[2]
	gvar.myPower = received[1]
	gvar.lock.acquire()
	gvar.playerPos[gvar.myID] = PlayerProfile(power = received[1])
	gvar.playerPos[gvar.myID].ID = gvar.myID
	gvar.playerPos[gvar.myID].groupID = received[2]
	gvar.playerPos[gvar.myID].port = gvar.myPort
	gvar.clientPP = received[3]
	gvar.server.clientPP = gvar.clientPP
	gvar.lock.release()

