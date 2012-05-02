import socket 
import struct 
import cPickle as pickle
import threading
import time
from const import *
from core.send_message import *

#serverPP = {} # (ip,port):(id,power,groupID) server keeps information about all active players' profile 
serverPP = {} # {id:(ip, port, groupID)}
globalID = 0 
groupNum = 0
groupInfo = {}
g_leader = None 
leader_atime = None
dead = {} 
server_lock = threading.Lock()

def assignID():
	global globalID
	globalID += 1
	return globalID - 1

def assignGroupID():
	global groupNum, groupInfo
	for (groupId, memberNum) in groupInfo.iteritems():
		if memberNum < MAX_GROUP_MEMBER_NUM:
			groupInfo[groupId] += 1
			return groupId
	groupInfo[groupNum] = 1
	groupNum += 1
	return groupNum - 1

def multicast_dead_player(ID):
	global serverPP, dead
	print serverPP, type(serverPP)
	for key in serverPP.iterkeys():
		dead[key].append(ID)

def find_new_gleader():
	global g_leader, serverPP, leader_atime
	g_leader = None
	for key in serverPP.iterkeys():
		if g_leader is None or g_leader > key:
			g_leader = key
	if g_leader is not None:
		leader_atime = time.time()

def handleRcv(conn, addr):
	global g_leader, dead, serverPP, groupInfo, server_lock, leader_atime
	conn.settimeout(2) # TODO
	buf = ""
	data_len = None
	ID = None
	groupID = None
	while True:

		#server_lock.acquire()
		#print "ID: {}".format(ID)
		#print "serverPP: {}".format(serverPP)
		#print "globalID: {}".format(globalID)
		#print "groupNum: {}".format(groupNum)
		#print "groupInfo: {}".format(groupInfo)
		#print "g_leader: {}".format(g_leader)
		#print "dead: {}".format(dead)
		#print "----------------------------------------"
		#server_lock.release()

		if ID is not None and len(dead[ID]) > 0:
			server_lock.acquire()
			self_delete = False
			while len(dead[ID]) > 0:
				dead_id = dead[ID].pop(0)
				send_tcp_msg(conn, (9, dead_id)) # send dead id
				if (dead_id == ID):
					self_delete = True
			if self_delete:
				print "player {} is dead".format(ID)
				del dead[ID]
				del serverPP[ID]
				groupInfo[groupID] -= 1
				if g_leader == ID:
					find_new_gleader()
				server_lock.release()
				break
			server_lock.release()

		try:
			temp_buf = conn.recv(1024)
			if len(temp_buf) == 0: # remote socket is closed
				server_lock.acquire()
				if ID is None: # player not enter yet, just throw out this thread
					server_lock.release()
					break	
				print "ID: {} is disconnect".format(ID)
				multicast_dead_player(ID)
				server_lock.release()
			buf += temp_buf 
		except Exception, exc:
			#print "Exception: {}".format(exc)
			if ID is not None:
				server_lock.acquire()
				if g_leader == ID:
					time_itvl = time.time() - leader_atime
					if time_itvl > 5: #TODO
						multicast_dead_player(ID)
						print "group leader {} is time out".format(ID)
				server_lock.release()
		if data_len is None and len(buf) >= 4:
			data_len = struct.unpack("!i", buf[:4])[0]
			#print data_len
			buf = buf[4:]
		if data_len is not None and len(buf) >= data_len:
			data = pickle.loads(buf[:data_len])
			buf = buf[data_len:]
			data_len = None
			if data[0] == 0: # New Player Register; data=(0,PlayerPort)
				server_lock.acquire()	
				ID = assignID()
				groupID = assignGroupID()
				serverPP[ID] = (addr[0], data[1], groupID)	
				send_tcp_msg(conn, (7, ID, groupID, serverPP)) # 7: server returns register response
				dead[ID] = []
				if g_leader is None:
					g_leader = ID
					leader_atime = time.time()
				print "new player from ip:{}, assign id:{}, groupid:{}".format(addr[0], ID, groupID)
				server_lock.release()
			elif data[0] == 8: # group leader heart beat; data=(8,)
				if ID != g_leader:
					print "SERVER: client sends msg wrongly!!!"
				leader_atime = time.time()
				#print "group leader {} heart beat".format(ID)
			elif data[0] == 10: # report dead id; data=(10, ID)
				server_lock.acquire()
				multicast_dead_player(data[1])
				if ID == g_leader:
					leader_atime = time.time()
				print "player {} report player {} is dead".format(ID, data[1])
				server_lock.release()

def startServer():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(("", SERVER_PORT))
	s.listen(1) 

	while True:
		conn, addr = s.accept()
		myThread = threading.Thread(target = handleRcv, kwargs = {"conn":conn, "addr":addr})	
		myThread.daemon = True
		myThread.start()

