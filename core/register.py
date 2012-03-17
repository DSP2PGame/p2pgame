from bootstrap.server import *
import pickle
import socket

def newRegister():
	data = (0,)
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.sendto(pickle.dumps(data), (SERVER_HOST, SERVER_PORT))

