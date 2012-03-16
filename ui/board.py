# Widget class for game board

from PyQt4.QtGui import *
from PyQt4.QtCore import *

GRID_LEN = 20
NUM_GRID_PER_BOARD_ROW = 10
BOARD_LEN = GRID_LEN * NUM_GRID_PER_BOARD_ROW

class BoardWidget(QWidget):
	def paintEvent(self, event):
		painter = QPainter(self)
		pen = QPen(QColor("black"))
		painter.setPen(pen)
		for i in xrange(0, BOARD_LEN + 1, GRID_LEN):
			painter.drawLine(i, 0, i, BOARD_LEN)
			painter.drawLine(0, i, BOARD_LEN, i)
		painter.end()

class PixelWidget(QWidget):
	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Down:
			self.move(self.x(), self.checkBound(self.y() + GRID_LEN))
		elif event.key() == Qt.Key_Up:
			self.move(self.x(), self.checkBound(self.y() - GRID_LEN))
		elif event.key() == Qt.Key_Left:
			self.move(self.checkBound(self.x() - GRID_LEN), self.y())
		elif event.key() == Qt.Key_Right:
			self.move(self.checkBound(self.x() + GRID_LEN), self.y())
	def checkBound(self, x):
		return min(max(0, x), BOARD_LEN - GRID_LEN)
