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

gameUI = GameUI(sys.argv)
gvar = GlobalVariable(gameUI)

# Register @ Server
getFreePort(gvar)
newRegister(gvar)
gameUI.setExitBehavior(gvar)
time.sleep(1)
connect_player(gvar)
send_comming_msg(gvar)

putNewPlayerOnBoard(gvar)

print gvar.clientPP

gameUI.showGameUI()
