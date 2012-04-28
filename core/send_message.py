import socket
import cPickle as pickle
import struct
import time
import threading

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

def multicastMove_old(grid, gvar):
	print "Multicast Movement Msg"
	gvar.lock.acquire()
	playerPos = gvar.playerPos
	for x in playerPos.iterkeys():
		if x != gvar.myID:
			conn = playerPos[x].conn
			if conn is not None:
				playerPos[x].last_stime = time.time()
				send_tcp_msg(conn, (6, grid))
	gvar.lock.release()

def domultisend(grid, gvar):
	print "Multicast Movement Msg"
	gvar.lock.acquire()
	playerPos = gvar.playerPos
	for x in playerPos.iterkeys():
		if x != gvar.myID:
			conn = playerPos[x].conn
			if conn is not None:
				playerPos[x].last_stime = time.time()
				send_tcp_msg(conn, (6, grid))
	gvar.lock.release()

def multicastMove(grid, gvar):
	temp = threading.Thread(target = domultisend, kwargs = {"grid":grid, "gvar":gvar})
	temp.daemon = True
	temp.start()
