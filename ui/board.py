# Widget class for game board

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from core.player import *
from const import *

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
		gvar = self.profile.gvar
		if event.key() == Qt.Key_Down:
			if gvar.can_move and checkRange(self.profile.y + 1) and canMove((self.profile.x, self.profile.y+1), gvar):
				move_to_grid((self.profile.x, self.profile.y+1), gvar)
				self.move(self.x(), self.checkBound(self.y() + GRID_LEN))
			else:
				self.cannotMove()
		elif event.key() == Qt.Key_Up:
			if gvar.can_move and checkRange(self.profile.y - 1) and canMove((self.profile.x, self.profile.y-1), gvar):
				move_to_grid((self.profile.x, self.profile.y-1), gvar)
				self.move(self.x(), self.checkBound(self.y() - GRID_LEN))
			else:
				self.cannotMove()
		elif event.key() == Qt.Key_Left:
			if gvar.can_move and checkRange(self.profile.x - 1) and canMove((self.profile.x - 1, self.profile.y), gvar):
				move_to_grid((self.profile.x - 1, self.profile.y), gvar)
				self.move(self.checkBound(self.x() - GRID_LEN), self.y())
			else:
				self.cannotMove()
		elif event.key() == Qt.Key_Right:
			if gvar.can_move and checkRange(self.profile.x + 1) and canMove((self.profile.x + 1, self.profile.y), gvar):
				move_to_grid((self.profile.x + 1, self.profile.y), gvar)
				self.move(self.checkBound(self.x() + GRID_LEN), self.y())
			else:
				self.cannotMove()
		else:
			print "GUI: This Key's Behavior is not defined"
	
	def cannotMove(self):
		print "GUI: Can not move to that grid"

	def checkBound(self, x):
		return min(max(0, x), BOARD_LEN - GRID_LEN)
