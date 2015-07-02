#!/usr/bin/env python
""" This is a simple howto example."""
import mpdserver
import time
from mpdserver import OptStr,OptInt
PORT = 6605
FIFO = "/home/larcher/.config/pianobar/ctl"

def send_to_pianobar(key):
        with open(FIFO,"w") as pbctl:
            pbctl.write("\n" + key + "\n")
            pbctl.flush()

class Play(mpdserver.Play):
    def handle_args(self, *args, **kwargs):
        send_to_pianobar("P")

class Stop(mpdserver.Command):
    def handle_args(self,*args):
        send_to_pianobar("S")

class Pause(mpdserver.Pause):
    formatArg=[('state',mpdserver.OptInt)]
    def handle_args(self, state=None):
        if state is None:
            state = 1
        if state==1:
            self.handle_pause()
        else :
            self.handle_unpause()

    def handle_pause(self):
        print "pausing"
        send_to_pianobar("p")

    def handle_unpause(self):
        print "unpausing"
        send_to_pianobar("p")


class Next(mpdserver.Command):
    def handle_args(self):
        send_to_pianobar("n")

# Create a deamonized mpd server that listen on port 9999
mpd = mpdserver.MpdServerDaemon(PORT)

# Register provided outputs command 
mpd.requestHandler.RegisterCommand(mpdserver.Outputs)

# Register your own command implementation
mpd.requestHandler.RegisterCommand(Play)
mpd.requestHandler.RegisterCommand(Next)
mpd.requestHandler.RegisterCommand(Stop)
mpd.requestHandler.RegisterCommand(Pause)


print """Starting a mpd server on port %(port)s
Type Ctrl+C to exit

To try it, type in another console
$ mpc -p %(port)s play
Or launch a MPD client with port %(port)s
""" % { 'port': PORT }

if __name__ == "__main__":
    try:
        while mpd.wait(1): 
            pass
    except KeyboardInterrupt:
        print "Stopping MPD server"
        mpd.quit()

