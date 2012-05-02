import socket
import threading
from core.send_message import *
from core.player import *
import time
from Queue import *

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
	s.listen(2)
	gvar.server = s

	p_handler = peer_recv_thread_handler(gvar)
	gvar.server_thread = threading.Thread(target=peerRcvThread, kwargs={"s":gvar.server, "p_handler":p_handler})
	gvar.server_thread.daemon = True
	gvar.server_thread.start()

class peer_recv_thread_handler(QObject):
	conn_received = pyqtSignal()
	def __init__(self, gvar):
		super(peer_recv_thread_handler, self).__init__()
		self.conn_received.connect(self.handle)
		self.gvar = gvar
		self.q = Queue()

	def handle(self):
		conn, addr = self.q.get()
		handler = peer_msg_handler(self.gvar, addr)
		myThread = threading.Thread(target = handle_peer_rcv, kwargs = {"conn":conn, "handler":handler})
		myThread.daemon = True
		myThread.start()

def peerRcvThread(s, p_handler):
	while True:
		conn, addr = s.accept()
		p_handler.q.put((conn, addr))
		p_handler.conn_received.emit()

def is_group_leader(ID, gvar):
	clientPP = gvar.clientPP
	for key in clientPP.iterkeys():
		if clientPP[ID][2] == clientPP[key][2] and ID > key:
			return False
	return True
	
def handle_peer_rcv(conn, handler): # handle msg between players
	buf = ""
	data_len = None
	while True:
		try:
			print 'pre recv', len(buf)
			tempbuf = conn.recv(1024)
			if len(tempbuf) == 0: # the other side close connection
				break
			buf += tempbuf
			print 'post recv', len(buf)
		except Exception, exc: # Error, exit 
			break
		
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
					print 'emit msg_received'
				else:
					break

class peer_msg_handler(QObject):
	msg_received = pyqtSignal(str)
	def __init__(self, gvar, addr):
		super(peer_msg_handler, self).__init__()
		self.msg_received.connect(self.handle)
		self.addr = addr
		self.ID = None
		self.groupID = None
		self.port = None
		self.gvar = gvar
		self.counter = 0
		self.timer = QTimer()
		self.timer.timeout.connect(self.handle_timer)
		self.timer.start(1000) 

	def handle_timer(self):
		self.counter += 1
		if self.counter >= 5: #time out
			if self.ID is not None and self.ID not in self.gvar.playerPos:
				return
			gl = self.gvar.gl_leader
			gp = self.gvar.gp_leader
			if self.ID is not None and ((self.gvar.myID == gl and is_group_leader(self.ID, self.gvar)) or (self.gvar.myID == gp and self.groupID == self.gvar.myGroup)): 
				time_itvl = time.time() - self.gvar.playerPos[self.ID].last_atime 
				if time_itvl > 5: 
					print "tell server player {} is dead".format(self.ID)
					exc = send_tcp_msg(self.gvar.ss, (10, self.ID))
	
	def handle(self, s):
		self.counter = 0
		data = pickle.loads(str(s))
		if self.ID is not None and self.ID not in self.gvar.playerPos and data[0] != 11:
			return
		if True:
			if data[0] == 11: # (11, id, groupid, port): new comer
				if self.ID is not None:
					print "Error! got multiple new comer from same client"
				else:
					self.ID = data[1]
					self.groupID = data[2]
					self.port = data[3]
					if self.ID not in self.gvar.clientPP:
						self.gvar.score[self.ID] = 0
						self.gvar.clientPP[self.ID] = (self.addr[0], self.port, self.groupID)
						self.gvar.playerPos[self.ID] = PlayerProfile(ID = self.ID, groupID = self.groupID)
						self.gvar.playerPos[self.ID].conn = socket_wrapper(self.ID, self.gvar.clientPP, (self.addr[0], self.port), (11, self.gvar.myID, self.gvar.myGroup, self.gvar.myPort))
						calc_global_leader(self.gvar)
						calc_group_leader(self.gvar)
			elif data[0] == 1: #(1,): ask for game status
				print "receive game status request from ID{}".format(self.ID)
				if self.gvar.new_form_id is not None:
					form_id = self.gvar.new_form_id
				else:
					form_id = self.gvar.form_id
				self.gvar.playerPos[self.ID].conn.send_msg((2, self.gvar.gameStatus, self.gvar.start_time, self.gvar.score, form_id, self.gvar.gameUI.calc_score, time.time()))
			elif data[0] == 2: # (2, gameStatus, start_time, score, form_id, is_calc_score, their_ctime)
				print "SERVER: receive game status"
				if self.gvar.hasStatus.is_set():
					print "SERVER: already got game statue"
				else:
					print "SERVER: save game status and update game status"
					updatePlayerPos(data[1], self.gvar.gameStatus, self.gvar.playerPos)
					self.gvar.start_time = data[2] + time.time() - data[6]
					self.gvar.score = data[3]
					self.gvar.new_form_id = data[4]
					self.gvar.form_id = data[4]
					self.gvar.gameUI.calc_score = data[5]
					self.gvar.hasStatus.set()
					print "SERVER: Got Game Status From player {}".format(self.ID)
			elif data[0] == 3: #(3, grid): receive a request for a grid,
				print "SERVER: receive a request for a grid {} from player {}".format(data[1], self.ID)
				if (self.gvar.gameStatus[data[1]] == -1): #-1: no one
					print "SERVER: no one occupy the grid, send approval"
					self.gvar.gameStatus[data[1]] = -2 # -2: reserve for someone
					self.gvar.playerPos[self.ID].conn.send_msg((4, data[1])) # approval
				else:
					print "SERVER: someone occupy the grid, send refusal"
					self.gvar.playerPos[self.ID].conn.send_msg((5,)) # refusal
			elif data[0] == 4: # (4, grid) approval
				print "SERVER: got approval for grid{}".format(data[1])
				self.gvar.gameStatus[data[1]] = -3
				self.gvar.canMoveSignal.set()
			elif data[0] == 5: # (5,) refusal 
				print "SERVER: got refusal for grid"
				self.gvar.canMoveSignal.set()
			elif data[0] == 6: # (6, grid) movement
				print "SERVER: player {} move to grid {}".format(self.ID, data[1])
				if self.gvar.playerPos[self.ID].x is None:
					self.gvar.gameStatus[data[1]] = self.ID
					self.gvar.playerPos[self.ID].x = data[1][0]
					self.gvar.playerPos[self.ID].y = data[1][1]
					self.gvar.myPainter.paintNewOtherSignal.emit(self.ID)
				else:
					self.gvar.gameStatus[(self.gvar.playerPos[self.ID].x, self.gvar.playerPos[self.ID].y)] = -1
					self.gvar.gameStatus[data[1]] = self.ID 
					self.gvar.playerPos[self.ID].x = data[1][0]
					self.gvar.playerPos[self.ID].y = data[1][1]
					self.gvar.myPainter.otherMoveSignal.emit(self.ID)
			elif data[0] == 12: #(12,) group leader send hb to global leader
				pass
				#print "heart beat from {} to global leader {}".format(self.ID, self.gvar.myID)
			elif data[0] == 13: #(13,) group member send hb to group leader
				pass
				#print "heart beat from {} to group leader {}".format(self.ID, self.gvar.myID)
			elif data[0] == 14: #(14, form_id)
				print "receive new form_id {}".format(data[1])
				self.gvar.new_form_id = data[1]
		self.gvar.playerPos[self.ID].last_atime = time.time()
