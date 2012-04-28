import random
from const import *
from core.send_message import *

# (1) calculate everyone's score according to current Target
# (2) show my score
# (3) show latest scores in ranking board
# (4) assign new target
# (5) show new target
def calc_score(gvar):
	old_form_id = gvar.form_id
	print "calc score"
	my_score = gvar.gameUI.myScore
	rank_board = gvar.gameUI.scoreBoard
	target = gvar.gameUI.target
	shape = gvar.form_db[old_form_id]

	# calculate score
	for i in xrange(0 - NUM_GRID_PER_FORM_ROW + 1, NUM_GRID_PER_BOARD_ROW):
		for j in xrange(0 - NUM_GRID_PER_FORM_ROW + 1, NUM_GRID_PER_BOARD_ROW):
			# (i, j) is the upper left corner of formation
			success = True
			for x in xrange(0, NUM_GRID_PER_FORM_ROW):
				for y in xrange(0, NUM_GRID_PER_FORM_ROW):
					if shape[x][y] == 1 and (not checkRange(i + x) or not checkRange(j + y) or gvar.gameStatus[(i+x, j+y)] < 0):
						success = False
						break
				if not success:
					break
			if success:
				for x in xrange(0, NUM_GRID_PER_FORM_ROW):
					for y in xrange(0, NUM_GRID_PER_FORM_ROW):
						if shape[x][y] == 1 and checkRange(i + x) and checkRange(j + y) and gvar.gameStatus[(i+x, j+y)] >= 0:
							ID = gvar.gameStatus[(i+x,j+y)]
							gvar.playerPos[ID].have_score = True
	
	for key in gvar.playerPos.iterkeys():
		if gvar.playerPos[key].have_score:
			gvar.playerPos[key].have_score = False
			gvar.score[key] += ONE_ROUND_SCORE
	# show my new score
	print str(gvar.score)
	print str(gvar.myID)
	my_score.setText("My Score: {}".format(gvar.score[gvar.myID]))

	# show ranking board
	rank = calc_rank_board(gvar)
	rank_board.setText("\n".join(rank))

	#generate new form id, if I'm global leader
	if gvar.gl_leader == gvar.myID:
		choose_form_id(gvar)
		for ID in gvar.playerPos.iterkeys():
			conn = gvar.playerPos[ID].conn
			if conn is not None:
				send_tcp_msg(conn, (14, gvar.new_form_id))

def calc_rank_board(gvar):
	rank = ["Score Board",]
	temp_flag = {}
	board_size = len(gvar.score)
	for key in gvar.score.iterkeys():
		temp_flag[key] = False
	for i in xrange(0, board_size):
		largest = -100
		largest_ID = None
		for key in gvar.score.iterkeys():
			if not temp_flag[key] and largest < gvar.score[key]:
				largest = gvar.score[key]
				largest_ID = key
		if largest_ID is not None:
			temp_flag[largest_ID] = True
			rank.append("Player {}:\t{}".format(largest_ID, largest))
	return rank


def choose_form_id(gvar):
	db_size = len(gvar.form_db)
	gvar.new_form_id = random.randint(0, db_size - 1)
