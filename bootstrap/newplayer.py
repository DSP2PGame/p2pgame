import socket
import threading
#from core.peer_server import *
from core.send_message import *
from core.player import *
import time

def getFreePort(gvar):
	print "Get Port Number & Start Peer Server"
	gvar.myPort = 10000
	while True:
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		        s.bind(("", gvar.myPort))
		except Exception, exc:
			print "Exception {}: in getFreePort".format(exc)
			gvar.myPort += 1
		else:
			break;
	s.listen(1) #TODO
	gvar.server = s
	gvar.server_thread = threading.Thread(target=peerRcvThread, kwargs={"s":gvar.server, "gvar":gvar})
	gvar.server_thread.daemon = True
	gvar.server_thread.start()

def peerRcvThread(s, gvar):
	while True:
		conn, addr = s.accept()
		myThread = threading.Thread(target = handle_peer_rcv, kwargs = {"conn":conn, "addr":addr, "gvar":gvar})
		myThread.daemon = True
		myThread.start()

def is_group_leader(ID, gvar):
	clientPP = gvar.clientPP
	for key in clientPP.iterkeys():
		if clientPP[ID][2] == clientPP[key][2] and ID > key:
			return False
	return True

def handle_peer_rcv(conn, addr, gvar): # handle msg between players
	conn.settimeout(2) #TODO
	ID = None
	groupID = None
	port = None
	buf = ""
	data_len = None
	last_atime = None
	while True:
		try:
			tempbuf = conn.recv(1024) #TODO
			if len(tempbuf) == 0: # the other side close connection
				pass #TODO
			buf += tempbuf
		except Exception, exc: # time out
			pass #TODO
		if ID is not None and ID not in gvar.playerPos:
			conn.close()
			break
		gl = gvar.gl_leader
		gp = gvar.gp_leader
		if ID is not None and (gvar.myID == gl and is_group_leader(ID, gvar) or gvar.myID == gp and groupID == gvar.myGroup) : 
			time_itvl = time.time() - last_atime
			if time_itvl > 2: #TODO ID should be dead
				print "tell server player {} is dead".format(ID)
				send_tcp_msg(gvar.ss, (10, ID))
		if data_len is None and len(buf) >= 4:
			data_len = struct.unpack("!i", buf[:4])[0]
			buf = buf[4:]
		if data_len is not None and len(buf) >= data_len:
			data = pickle.loads(buf[:data_len])
			buf = buf[data_len:]
			data_len = None

			if data[0] == 11: # (11, id, groupid, port): new commer
				if ID is not None:
					print "Error! got multiple new commer from same client"
				else:
					ID = data[1]
					groupID = data[2]
					port = data[3]
					last_atime = time.time()
					#gvar.lock.acquire()
					if ID not in gvar.clientPP:
						gvar.score[ID] = 0
						gvar.clientPP[ID] = (addr[0], port, groupID)
						gvar.playerPos[ID] = PlayerProfile(ID = ID, groupID = groupID)
						gvar.playerPos[ID].conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
						try:
							gvar.playerPos[ID].conn.connect((addr[0], port))
						except Exception, exc:
							print "Exception {}: can't connect to player {}".format(exc, ID)
						send_tcp_msg(gvar.playerPos[ID].conn, (11, gvar.myID, gvar.myGroup, gvar.myPort))
						calc_global_leader(gvar)
						calc_group_leader(gvar)
					#gvar.lock.release()
			elif data[0] == 1: #(1,): ask for game status
				if ID is None:
					print "Error! No new commer msg first! Thread End!"
					break
				print "SERVER: receive game status request from ID{}".format(ID)
				#gvar.lock.acquire()
				if gvar.playerPos[ID].conn is None:
					print "Error! No connection with player {}".format(ID)
					break
				send_tcp_msg(gvar.playerPos[ID].conn, (2, gvar.gameStatus, gvar.start_time, gvar.score))
				#gvar.lock.release()
				last_atime = time.time()
			elif data[0] == 2: # (2, gameStatus, start_time, score)
				print "SERVER: receive game status"
				if gvar.hasStatus.is_set():
					print "SERVER: already got game statue"
				else:
					print "SERVER: save game status and update game status"
					gvar.lock.acquire()
					updatePlayerPos(data[1], gvar.gameStatus, gvar.playerPos)
					gvar.start_time = data[2]
					gvar.score = data[3]
					gvar.lock.release()
					gvar.hasStatus.set()
					print "SERVER: Got Game Status From player {}".format(ID)
				last_atime = time.time()
			elif data[0] == 3: #(3, grid): receive a request for a grid,
				print "SERVER: receive a request for a grid {} from player {}".format(data[1], ID)
				#gvar.lock.acquire()
				if (gvar.gameStatus[data[1]] == -1): #-1: no one
					print "SERVER: no one occupy the grid, send approval"
					gvar.gameStatus[data[1]] = -2 # -2: reserve for someone
					send_tcp_msg(gvar.playerPos[ID].conn, (4, data[1])) # approval
				else:
					print "SERVER: someone occupy the grid, send refusal"
					send_tcp_msg(gvar.playerPos[ID].conn, (5,)) # refusal
				#gvar.lock.release()
				last_atime = time.time()
			elif data[0] == 4: # (4, grid) approval
				print "SERVER: got approval for grid{}".format(data[1])
				#gvar.lock.acquire()
				gvar.gameStatus[data[1]] = -3
				#gvar.lock.release()
				gvar.canMoveSignal.set()
				last_atime = time.time()
			elif data[0] == 5: # (5,) refusal 
				print "SERVER: got refusal for grid"
				gvar.canMoveSignal.set()
				last_atime = time.time()
			elif data[0] == 6: # (6, grid) movement
				print "SERVER: player {} move to grid {}".format(ID, data[1])
				#gvar.lock.acquire()
				if gvar.playerPos[ID].x is None:
					gvar.gameStatus[data[1]] = ID
					gvar.playerPos[ID].x = data[1][0]
					gvar.playerPos[ID].y = data[1][1]
					gvar.myPainter.paintNewOtherSignal.emit(ID)
				else:
					gvar.gameStatus[(gvar.playerPos[ID].x, gvar.playerPos[ID].y)] = -1
					gvar.gameStatus[data[1]] = ID 
					gvar.playerPos[ID].x = data[1][0]
					gvar.playerPos[ID].y = data[1][1]
					gvar.myPainter.otherMoveSignal.emit(ID)
				#gvar.lock.release()
				last_atime = time.time()
			elif data[0] == 12: #(12,) group leader send hb to global leader
				print "heart beat from {} to global leader {}".format(ID, gvar.myID)
				last_atime = time.time()
			elif data[0] == 13: #(13,) group member send hb to group leader
				print "heart beat from {} to group leader {}".format(ID, gvar.myID)
				last_atime = time.time()
