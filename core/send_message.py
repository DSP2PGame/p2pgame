import socket
import pickle

def sendMsg(ip, port, data):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);
	sock.sendto(pickle.dumps(data), (ip, port))
	print "Send to {}".format((ip, port))
