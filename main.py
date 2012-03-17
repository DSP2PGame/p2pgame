from ui.board import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from bootstrap.server import *
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
MY_PIXEL_COLOR = "blue"

app = QApplication(sys.argv)

mainWidget = QWidget()
mainWidget.setPalette(QPalette(QColor(MAIN_WIDGET_COLOR)))
mainWidget.resize(MAIN_WIDGET_WIDTH, MAIN_WIDGET_HEIGHT)

gameBoard = BoardWidget(mainWidget)
gameBoard.setAutoFillBackground(True)
gameBoard.setPalette(QPalette(QColor(BOARD_WIDGET_COLOR)))
gameBoard.move(BOARD_WIDGET_OFFSET_WIDTH, BOARD_WIDGET_OFFSET_HEIGHT)
gameBoard.resize(BOARD_LEN + 1, BOARD_LEN + 1)

# Register @ Server
newRegister()

# Test Use
pix = PixelWidget(gameBoard)
pix.resize(GRID_LEN, GRID_LEN)
pix.setAutoFillBackground(True)
pix.setPalette(QPalette(QColor(MY_PIXEL_COLOR)))
pix.setFocusPolicy(Qt.StrongFocus)
# End Test Use

mainWidget.show()
app.exec_()
