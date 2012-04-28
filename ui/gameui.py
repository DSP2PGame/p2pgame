from PyQt4.QtGui import *
from PyQt4.QtCore import *
from const import *
from ui.exit import *
from ui.board import *
from calc_score import *

class GameUI(QObject):
	def __init__(self, argv):
		super(QObject, self).__init__()
		self.app = QApplication(argv)
		self.gvar = None
		self.calc_score = False

		self.mainWidget = QWidget()
		self.mainWidget.setPalette(QPalette(QColor(MAIN_WIDGET_COLOR)))
		self.mainWidget.setAttribute(Qt.WA_QuitOnClose)

		self.exitButton = QPushButton("Exit")
		self.gameBoard = BoardWidget(self.mainWidget)
		
		self.timerText = QLabel()
		self.timerText.setText("TEST")
		self.timerCheck = QTimer()
		self.timerCheck.timeout.connect(self.updateTimer)
		self.timerCheck.start(100)

		self.myScore = QLabel()
		self.myScore.setText("My Score: 0")

		self.scoreBoard = QLabel()
		self.scoreBoard.setText("Score Board\nMyself:\t0\nOther One:\t100\n")

		# Feature Need To Be Implemented
		self.target = QWidget()
		# End

		self.sideLayout = QFormLayout()
		self.sideLayout.addRow(self.target)
		self.sideLayout.addRow(self.timerText)
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
	
	def updateTimer(self):
		last = int(time.time() - self.gvar.start_time)
		shown_num = None
		if last >= 15:
			self.gvar.start_time += 15
			show_num = 10
			self.gvar.can_move = True
			self.calc_score = False
		elif last >= 10:
			self.gvar.can_move = False
			shown_num = 15 - last 
			if not self.calc_score:
				self.calc_score = True
				calc_score(self.gvar)
		else:
			shown_num = 10 - last
		self.timerText.setText(str(shown_num))

	def showGameUI(self):
		self.mainWidget.show()
		self.app.exec_()
	
	def setExitBehavior(self, gvar):
		self.exitBehavior = ExitButtonBehavior(gvar, self.mainWidget)
		self.exitButton.clicked.connect(self.exitBehavior.clickExitButton)

