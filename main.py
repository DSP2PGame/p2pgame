from ui.board import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from bootstrap.server import *
from bootstrap.newplayer import *
from core.register import *
import sys

if len(sys.argv) > 1 and sys.argv[1] == "B": #bootstrapping server
	print "Server Start"
	startServer()

MAIN_WIDGET_WIDTH = 300
MAIN_WIDGET_HEIGHT = 300
MAIN_WIDGET_COLOR = "grey"
BOARD_WIDGET_COLOR = "white"
BOARD_WIDGET_OFFSET_WIDTH = 50
BOARD_WIDGET_OFFSET_HEIGHT = 50
OWN_N = 2

app = QApplication(sys.argv)

mainWidget = QWidget()
mainWidget.setPalette(QPalette(QColor(MAIN_WIDGET_COLOR)))
mainWidget.resize(MAIN_WIDGET_WIDTH, MAIN_WIDGET_HEIGHT)

gameBoard = BoardWidget(mainWidget)
gameBoard.setAutoFillBackground(True)
gameBoard.setPalette(QPalette(QColor(BOARD_WIDGET_COLOR)))
gameBoard.move(BOARD_WIDGET_OFFSET_WIDTH, BOARD_WIDGET_OFFSET_HEIGHT)
gameBoard.resize(BOARD_LEN + 1, BOARD_LEN + 1)

# Init
lock = threading.Lock()
gameStatus = {}
for i in xrange(0, NUM_GRID_PER_BOARD_ROW):
	for j in xrange(0, NUM_GRID_PER_BOARD_ROW):
		gameStatus[(i,j)] = -1 #unoccupied
hasStatus = threading.Event()
hasStatus.clear()
canMoveSignal = threading.Event()

# Register @ Server
myID = None
playerPos = {}
(theServer, myPort) = getFreePort(playerPos, gameStatus, hasStatus, lock) 
(clientPP, myID) = newRegister(myPort, playerPos, lock)

if len(clientPP) == 0:
	hasStatus.set()
	lock.acquire()
	playerPos[myID].x = 0
	playerPos[myID].y = 0
	gameStatus[(0,0)] = myID
	lock.release()
else:
	for pp in clientPP.itervalues():
		playerPos[pp[0]] = PlayerProfile(power = pp[1])
	askGameStatus(clientPP, myPort, hasStatus, myID, playerPos[myID].power)
	chooseInitGrid(myID, playerPos, gameStatus, lock, clientPP, myPort, playerPos[myID].power, canMoveSignal)

for other in playerPos:
	if other != myID:
		paintOther(gameBoard, playerPos[other], gameStatus, lock)
	else:
		paintMyself(gameBoard, playerPos[myID], gameStatus, lock)

mainWidget.show()
app.exec_()
theServer.shutdown()
