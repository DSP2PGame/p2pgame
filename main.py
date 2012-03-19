from ui.board import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from bootstrap.server import *
from bootstrap.newplayer import *
from core.register import *
from core.painter import *
from ui.exit import *
import sys

if len(sys.argv) > 1 and sys.argv[1] == "B": #bootstrapping server
	print "Server Start"
	startServer()

#MAIN_WIDGET_WIDTH = 300
#MAIN_WIDGET_HEIGHT = 300
MAIN_WIDGET_COLOR = "grey"
BOARD_WIDGET_COLOR = "white"
#BOARD_WIDGET_OFFSET_WIDTH = 50
#BOARD_WIDGET_OFFSET_HEIGHT = 50

app = QApplication(sys.argv)

mainWidget = QWidget()
mainWidget.setPalette(QPalette(QColor(MAIN_WIDGET_COLOR)))
#mainWidget.resize(MAIN_WIDGET_WIDTH, MAIN_WIDGET_HEIGHT)
mainWidget.setAttribute(Qt.WA_QuitOnClose)

exitButton = QPushButton("Exit")
gameBoard = BoardWidget(mainWidget)

layout = QBoxLayout(QBoxLayout.LeftToRight)
layout.addWidget(gameBoard)
layout.addWidget(exitButton)
mainWidget.setLayout(layout)

gameBoard.setAutoFillBackground(True)
gameBoard.setPalette(QPalette(QColor(BOARD_WIDGET_COLOR)))
#gameBoard.move(BOARD_WIDGET_OFFSET_WIDTH, BOARD_WIDGET_OFFSET_HEIGHT)
#gameBoard.resize(BOARD_LEN + 1, BOARD_LEN + 1)
gameBoard.setMinimumSize(BOARD_LEN + 1, BOARD_LEN + 1);


# Init
lock = threading.Lock()
gameStatus = {}
for i in xrange(0, NUM_GRID_PER_BOARD_ROW):
	for j in xrange(0, NUM_GRID_PER_BOARD_ROW):
		gameStatus[(i,j)] = -1 #unoccupied
hasStatus = threading.Event()
hasStatus.clear()
canMoveSignal = threading.Event()
playerPos = {}
myID = None
myPainter = MyPainter(gameBoard, playerPos)
myPainter.connectSignal()

# Register @ Server
(theServer, myPort) = getFreePort(playerPos, gameStatus, hasStatus, canMoveSignal, lock, myPainter) 
(clientPP, myID) = newRegister(myPort, playerPos, lock)
theServer.clientPP = clientPP
playerPos[myID].port = myPort

exitBehavior = ExitButtonBehavior(theServer, mainWidget)
exitButton.clicked.connect(exitBehavior.clickExitButton)

if len(clientPP) == 0:
	hasStatus.set()
	lock.acquire()
	playerPos[myID].x = 0
	playerPos[myID].y = 0
	gameStatus[(0,0)] = myID
	playerPos[myID].playerPos = playerPos
	playerPos[myID].gameStatus = gameStatus
	playerPos[myID].lock = lock
	playerPos[myID].clientPP = clientPP
	playerPos[myID].canMoveSignal = canMoveSignal
	lock.release()
else:
	for pp in clientPP.iteritems():
		playerPos[pp[1][0]] = PlayerProfile(power = pp[1][1])
		playerPos[pp[1][0]].groupID = pp[1][2]
		playerPos[pp[1][0]].ip = pp[0][0]
		playerPos[pp[1][0]].port = pp[0][1]
		playerPos[pp[1][0]].ID = pp[1][0]
	askGameStatus(clientPP, myPort, hasStatus, myID, playerPos[myID].power, playerPos[myID].groupID)
	chooseInitGrid(myID, playerPos, gameStatus, lock, clientPP, myPort, playerPos[myID].power, playerPos[myID].groupID, canMoveSignal)

for other in playerPos:
	if other != myID:
		myPainter.paintOther(other)
	else:
		myPainter.paintMyself(playerPos[myID], gameStatus, lock)

mainWidget.show()
app.exec_()
theServer.shutdown()
