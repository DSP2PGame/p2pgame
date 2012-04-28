from core.player import *
from const import *
import cPickle as pickle
import socket
import threading
import time
from core.send_message import *

def connect_player(gvar):
	#gvar.lock.acquire()
	clientPP = gvar.clientPP
	for key in clientPP.iterkeys():
		if key != gvar.myID:
			player = PlayerProfile(ID = key, groupID = clientPP[key][2]) 
			player.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			try:
				player.conn.connect((clientPP[key][0], clientPP[key][1]))
			except Exception, exc:
				print "Exception {}: Error can't connect player {}".format(exc, key)
				player.conn = None
			gvar.playerPos[key] = player
	#gvar.lock.release()

def send_comming_msg(gvar):
	#gvar.lock.acquire()
	playerPos = gvar.playerPos
	for key in playerPos.iterkeys():
		if key != gvar.myID and playerPos[key].conn is not None:
			send_tcp_msg(playerPos[key].conn, (11, gvar.myID, gvar.myGroup, gvar.myPort))
	#gvar.lock.release()
	calc_global_leader(gvar)
	calc_group_leader(gvar)

def start_send_hb(gvar):
	gvar.hb_thread = threading.Thread(target = handle_all_hb, kwargs = {"gvar":gvar})
	gvar.hb_thread.daemon = True
	gvar.hb_thread.start()

def newRegister(gvar):
	print "connect to Server & send register msg to server & receive clientPP, id, groupid"

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		sock.connect((SERVER_HOST, SERVER_PORT))
	except Exception, exc:
		print "ERROR: server is not started. {}".format(exc)
	gvar.ss = sock
	gvar.ps_thread = threading.Thread(target = handle_ps_rcv, kwargs = {"conn":sock, "gvar":gvar})
	gvar.ps_thread.daemon = True
	gvar.ps_thread.start()

	print "send register request to server"
	send_tcp_msg(sock, (0, gvar.myPort))
	print "wait server to reply"
	time.sleep(1)

def handle_all_hb(gvar):
	while True:
		gl = gvar.gl_leader
		gp = gvar.gp_leader
		#print "global {}, group {}".format(gl, gp)	
		if gl == gvar.myID: # I'm global leader, I'll send hb to server
			send_tcp_msg(gvar.ss, (8,))
		elif gp == gvar.myID: # I'm not gl_leader, but I'm gp_leader, I'll send hb to gl_leader
			time_itvl = time.time() - gvar.playerPos[gl].last_stime
			if time_itvl > 1:
				send_tcp_msg(gvar.playerPos[gl].conn, (12,))
				gvar.playerPos[gl].last_stime = time.time()
		else: # I'm normal group member, I'll send hb to gp
			time_itvl = time.time() - gvar.playerPos[gp].last_stime
			if time_itvl > 1:
				send_tcp_msg(gvar.playerPos[gp].conn, (13,))
				gvar.playerPos[gp].last_stime = time.time()
		time.sleep(1)

def handle_ps_rcv(conn, gvar):
	conn.settimeout(100) #TODO
	buf = ""
	data_len = None
	print "start"
	while True:
		try:
			print "recv start"
			temp_buf = conn.recv(1024) #TODO
			print "recv end"
			if len(temp_buf) == 0: # server is shutdown
				while True:
					print "ERROR: your network is slow, server close your connection, please restart game"
					time.sleep(10)
			buf += temp_buf
		except Exception, exc: # recv() time out
			print "Exception {} in handle Player Server Recv".format(exc)
		if data_len is None and len(buf) >= 4:
			data_len = struct.unpack("!i", buf[:4])[0]
			print data_len
			buf = buf[4:]
		if data_len is not None and len(buf) >= data_len:
			data = pickle.loads(buf[:data_len])
			buf = buf[data_len:]
			data_len = None

			if data[0] == 7: # (7, id, groupid, serverPP) this is my info
				print "got server's reply {}".format(data)
				gvar.lock.acquire()
				gvar.myID = data[1]
				gvar.myGroup = data[2]
				gvar.playerPos[gvar.myID] = PlayerProfile(ID = gvar.myID, groupID = gvar.myGroup)
				gvar.playerPos[gvar.myID].gvar = gvar
				gvar.clientPP = data[3]	
				gvar.lock.release()
			elif data[0] ==9: # (9, deadID) some player is offline
				gvar.lock.acquire()
				if data[1] == gvar.myID:
					gvar.lock.release()
					while True:
						print "network error. please restart game."
						time.sleep(10)
				if data[1] in gvar.playerPos:
					x = gvar.playerPos[data[1]].x
					y = gvar.playerPos[data[1]].y
					if x is not None:
						gvar.gameStatus[(x, y)] = -1	
						gvar.playerPos[data[1]].pix.hide()
						gvar.playerPos[data[1]].pix.deleteLater()
					temp_conn = gvar.playerPos[data[1]].conn
					if temp_conn is not None:
						temp_conn.close()
					del gvar.clientPP[data[1]]
					del gvar.playerPos[data[1]]
				else:
					pass
				calc_global_leader(gvar)
				calc_group_leader(gvar)
				print "global leader: {}".format(gvar.gl_leader)
				print "group_leader: {}".format(gvar.gp_leader)
				gvar.lock.release()
