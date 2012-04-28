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

class FormationWidget(QWidget):
	def paintEvent(self, event):
		painter = QPainter(self)
		pen = QPen(QColor("black"))
		painter.setPen(pen)
		for i in xrange(0, FORM_LEN + 1, FORM_GRID_LEN):
			painter.drawLine(i, 0, i, FORM_LEN)
			painter.drawLine(0, i, FORM_LEN, i)
		painter.end()
	def draw_form(self, gvar):
		shape = gvar.form_db[gvar.form_id]
		for i in xrange(0, NUM_GRID_PER_FORM_ROW, 1):
			for j in xrange(0, NUM_GRID_PER_FORM_ROW, 1):
				if shape[i][j] == 1:
					pix = QWidget(self)
					pix.resize(FORM_GRID_LEN, FORM_GRID_LEN)
					pix.setAutoFillBackground(True)
					pix.setPalette(QPalette(QColor(FORM_PIXEL_COLOR)))
					pix.setFocusPolicy(Qt.NoFocus)
					pix.move(i * FORM_GRID_LEN, j * FORM_GRID_LEN)
					pix.show()

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
