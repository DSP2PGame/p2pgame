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
			player.conn = socket_wrapper(key, clientPP, (clientPP[key][0], clientPP[key][1]), (11, gvar.myID, gvar.myGroup, gvar.myPort))
			gvar.playerPos[key] = player
	calc_global_leader(gvar)
	calc_group_leader(gvar)

def make_send_hb_fun(gvar):
	def send_hb():
		gl = gvar.gl_leader
		gp = gvar.gp_leader
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

	handler = server_thread_handler(gvar)
	gvar.ps_thread = threading.Thread(target = handle_ps_rcv, kwargs = {"conn":sock, "handler":handler})
	gvar.ps_thread.daemon = True
	gvar.ps_thread.start()

	print "send register request to server"
	send_tcp_msg(sock, (0, gvar.myPort))
	print "wait server to reply"
	while True: 
		QCoreApplication.processEvents(QEventLoop.WaitForMoreEvents)
		if gvar.serverResponse.is_set():
			break

class server_thread_handler(QObject):
	msg_received = pyqtSignal(str)

	def __init__(self, gvar):
		super(server_thread_handler, self).__init__()
		self.msg_received.connect(self.handle)
		self.gvar = gvar

	def handle(self, s):
		data = pickle.loads(str(s))	
		if data[0] == 7: # (7, id, groupid, serverPP) this is my info
			print "got server's reply {}".format(data)
			self.gvar.myID = data[1]
			self.gvar.myGroup = data[2]
			self.gvar.playerPos[self.gvar.myID] = PlayerProfile(ID = self.gvar.myID, groupID = self.gvar.myGroup)
			self.gvar.playerPos[self.gvar.myID].gvar = self.gvar
			self.gvar.clientPP = data[3]	
			self.gvar.serverResponse.set()
		elif data[0] ==9: # (9, deadID) some player is offline
			print "player {} is dead--------------------".format(data[1])
			if data[1] == self.gvar.myID: # I need to die
				return
			if data[1] in self.gvar.playerPos:
				self.gvar.playerPos[data[1]].pix.hide()
				self.gvar.playerPos[data[1]].pix.deleteLater()
				x = self.gvar.playerPos[data[1]].x
				y = self.gvar.playerPos[data[1]].y
				if x is not None:
					self.gvar.gameStatus[(x, y)] = -1	
				temp_conn = self.gvar.playerPos[data[1]].conn
				if temp_conn is not None:
					temp_conn.close()
				del self.gvar.clientPP[data[1]]
				del self.gvar.playerPos[data[1]]
				del self.gvar.score[data[1]]
			else:
				pass
			calc_global_leader(self.gvar)
			calc_group_leader(self.gvar)
			print "global leader: {}".format(self.gvar.gl_leader)
			print "group_leader: {}".format(self.gvar.gp_leader)

def handle_ps_rcv(conn, handler):
	buf = ""
	data_len = None
	while True:
		try:
			print "recv server msg start {}".format(len(buf))
			temp_buf = conn.recv(1024)
			if len(temp_buf) == 0: # server is shutdown
				break
			buf += temp_buf
			print "recv server msg end {}".format(len(buf))
		except Exception, exc: # recv() time out
			pass
		while True:
			if data_len is None:
				if len(buf) >= 4:
					data_len = struct.unpack("!i", buf[:4])[0]
					buf = buf[4:]
				else:
					break
			else:
				if len(buf) >= data_len:
					data = buf[:data_len]
					buf = buf[data_len:]
					data_len = None
					handler.msg_received.emit(data)
					print "emit server msg"
				else:
					break
