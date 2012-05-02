from bootstrap.server import *
from bootstrap.newplayer import *
from core.register import *
from ui.gameui import *
from core.global_variable import *
import sys
import time

# start bootstrapping server and run forever if this is the boot process
if len(sys.argv) > 1 and sys.argv[1] == "B": 
	print "Server Start"
	startServer()

app = QApplication(sys.argv)
gameUI = GameUI(app)
gvar = GlobalVariable(gameUI)
gameUI.gvar = gvar
gvar.load_formation()

# Register @ Server
getFreePort(gvar)
newRegister(gvar)
gameUI.setExitBehavior(gvar)
connect_player(gvar)

hb_timer = QTimer()
hb_timer.timeout.connect(make_send_hb_fun(gvar))
hb_timer.start(3000)

putNewPlayerOnBoard(gvar)
#print gvar.clientPP
if gvar.start_time is None: #first one
	gvar.start_time = time.time()
if gvar.form_id is None: #first one
	choose_form_id(gvar)
	gvar.form_id = gvar.new_form_id
#start_timer(gvar)
gameUI.showGameUI()
app.exec_()
