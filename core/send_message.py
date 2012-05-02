import socket
import cPickle as pickle
import struct
import time
import threading
from PyQt4.QtNetwork import *

# first send length, then send pickled data
def send_tcp_msg(conn, data):
	#print "send to {} with data {}".format(conn, data)
	try:
		pdata = pickle.dumps(data)
		plen = struct.pack("!i", len(pdata))
		conn.sendall(plen)
		conn.sendall(pdata)
	except Exception, exc:
		print "Exception: {} send tcp msg".format(exc)
		return exc

class socket_wrapper():
	def __init__(self, addr, init_msg):
		self.addr = addr
		self.init_msg = init_msg
		self.buf = []
		self.conn = None
		self.reconnect()
	
	def send_msg(self, data):
		if self.conn.state() != QAbstractSocket.ConnectedState:
			print "append data {}".format(data)
			self.buf.append(data)
		else:
			print "write data {}".format(data)
			self.write_msg(data)

	def write_msg(self, data):
		pdata = pickle.dumps(data)
		plen = struct.pack("!i", len(pdata))
		self.conn.write(plen)
		self.conn.write(pdata)
		self.conn.flush()

	def reconnect(self):
		print "reconnect"
		if self.conn is not None:
			self.conn.deleteLater()
		self.conn = QTcpSocket()
		self.conn.connectToHost(self.addr[0], self.addr[1])
		self.conn.connected.connect(self.flush)
		self.conn.error.connect(self.reconnect)

	def flush(self):
		self.write_msg(self.init_msg)
		while len(self.buf) > 0:
			data = self.buf.pop(0)
			print "flush", data
			self.write_msg(data)
	
	def close(self):
		self.conn.disconnectFromHost()
		
def multicastMove(grid, gvar):
	print "Multicast Movement Msg"
	playerPos = gvar.playerPos
	for x in playerPos.iterkeys():
		if x != gvar.myID:
			playerPos[x].conn.send_msg((6, grid))
