import socket
import pickle

def sendMsg(ip, port, data):

	print "Send Msg {} {} {}".format(ip, port, data[0])

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);
	sock.sendto(pickle.dumps(data), (ip, port))

def multicastMove(myID, myPort, myPower, myGroup, grid, clientPP):
	
	print "Multicast Movement Msg"

	for x in clientPP:
		sendMsg(x[0], x[1], (6, myPort, myID, myPower, myGroup, grid))
