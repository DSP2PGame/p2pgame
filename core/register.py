from bootstrap.server import *
from core.player import *
import pickle
import socket

def newRegister(myPort, playerPos, lock):
	data = (0, myPort)
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.sendto(pickle.dumps(data), (SERVER_HOST, SERVER_PORT))
	received = pickle.loads(sock.recv(10240)) #TODO How large is enough?
	myID = received[0]
	lock.acquire()
	playerPos[myID] = PlayerProfile(power = received[1])
	lock.release()
	return received[2], myID

