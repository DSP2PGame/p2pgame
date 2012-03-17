from bootstrap.server import *
import pickle
import socket

def newRegister(myProfile, myPort):
	data = (0, myPort)
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.sendto(pickle.dumps(data), (SERVER_HOST, SERVER_PORT))
	received = pickle.loads(sock.recv(10240)) #TODO How large is enough?
	myProfile.power = received[1]
	myProfile.ID = received[0]
	return received[2]

