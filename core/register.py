from core.player import *
from const import *
import cPickle as pickle
import socket
import threading
import time
from core.send_message import *
import sys

def connect_player(gvar):
	clientPP = gvar.clientPP
	for key in clientPP.iterkeys():
		if key != gvar.myID:
			player = PlayerProfile(ID = key, groupID = clientPP[key][2]) 
			player.conn = socket_wrapper((clientPP[key][0], clientPP[key][1]), (11, gvar.myID, gvar.myGroup, gvar.myPort))
			gvar.playerPos[key] = player
	calc_global_leader(gvar)
	calc_group_leader(gvar)

def start_send_hb(gvar):
	gvar.hb_thread = threading.Thread(target = handle_all_hb, kwargs = {"gvar":gvar})
	gvar.hb_thread.daemon = True
	gvar.hb_thread.start()

def make_send_hb_fun(gvar):
	def send_hb():
		gl = gvar.gl_leader
		gp = gvar.gp_leader
		#print "global {}, group {}".format(gl, gp)	
		if gl == gvar.myID: # I'm global leader, I'll send hb to server
			send_tcp_msg(gvar.ss, (8,))
		elif gp == gvar.myID: # I'm not gl_leader, but I'm gp_leader, I'll send hb to gl_leader
			gvar.playerPos[gl].conn.send_msg((12,))
		else: # I'm normal group member, I'll send hb to gp
			gvar.playerPos[gp].conn.send_msg((13,))
	return send_hb

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

def handle_ps_rcv(conn, gvar):
	conn.settimeout(100) #TODO
	buf = ""
	data_len = None
	print "start"
	while True:
		try:
			temp_buf = conn.recv(1024)
			if len(temp_buf) == 0: # server is shutdown
				while True:
					print "ERROR: your network is slow, server close your connection, please restart game"
					time.sleep(1)
			buf += temp_buf
		except Exception, exc: # recv() time out
			pass
			#print "Exception {} in handle Player Server Recv".format(exc)
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
				print "player {} is dead--------------------".format(data[1])
				gvar.lock.acquire()
				if data[1] == gvar.myID: # I need to die
					gvar.lock.release()
					while True:
						print "network error. please restart game."
						time.sleep(1)
				if data[1] in gvar.playerPos:
					gvar.playerPos[data[1]].pix.hide()
					gvar.playerPos[data[1]].pix.deleteLater()
					x = gvar.playerPos[data[1]].x
					y = gvar.playerPos[data[1]].y
					if x is not None:
						gvar.gameStatus[(x, y)] = -1	
					temp_conn = gvar.playerPos[data[1]].conn
					if temp_conn is not None:
						temp_conn.close()
					del gvar.clientPP[data[1]]
					del gvar.playerPos[data[1]]
					del gvar.score[data[1]]
				else:
					pass
				calc_global_leader(gvar)
				calc_group_leader(gvar)
				print "global leader: {}".format(gvar.gl_leader)
				print "group_leader: {}".format(gvar.gp_leader)
				gvar.lock.release()
