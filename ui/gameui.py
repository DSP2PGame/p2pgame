from PyQt4.QtGui import *
from PyQt4.QtCore import *
from const import *
from ui.exit import *
from ui.board import *
from core.exit import *

class GameUI(QObject):
	def __init__(self, argv):
		super(QObject, self).__init__()
		self.app = QApplication(argv)

		self.mainWidget = QWidget()
		self.mainWidget.setPalette(QPalette(QColor(MAIN_WIDGET_COLOR)))
		self.mainWidget.setAttribute(Qt.WA_QuitOnClose)

		self.exitButton = QPushButton("Exit")
		self.gameBoard = BoardWidget(self.mainWidget)
		
		# Feature Need To Be Implemented
		self.target = QWidget()
		self.timer = QWidget()
		self.myScore = QWidget()
		self.scoreBoard = QWidget()
		# End

		self.sideLayout = QFormLayout()
		self.sideLayout.addRow(self.target)
		self.sideLayout.addRow(self.timer)
		self.sideLayout.addRow(self.myScore)
		self.sideLayout.addRow(self.scoreBoard)
		self.sideLayout.addRow(self.exitButton)

		self.mainLayout = QBoxLayout(QBoxLayout.LeftToRight)
		self.mainLayout.addWidget(self.gameBoard)
		self.mainLayout.addLayout(self.sideLayout)
		self.mainWidget.setLayout(self.mainLayout)

		self.gameBoard.setAutoFillBackground(True)
		self.gameBoard.setPalette(QPalette(QColor(BOARD_WIDGET_COLOR)))
		self.gameBoard.setMinimumSize(BOARD_LEN + 1, BOARD_LEN + 1);

	def showGameUI(self):
		self.mainWidget.show()
		self.app.exec_()
	
	def setExitBehavior(self, server):
		self.exitBehavior = ExitButtonBehavior(server, self.mainWidget)
		self.exitButton.clicked.connect(self.exitBehavior.clickExitButton)

