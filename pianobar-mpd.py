#!/usr/bin/env python
""" This is a simple howto example."""
import mpdserver
import time
from mpdserver import OptStr,OptInt

PORT = 6605
FIFO = "/home/larcher/.config/pianobar/ctl"
NOW_PLAYING = "/home/larcher/.config/pianobar/nowplaying-mpd"
STATION_LIST = "/home/larcher/.config/pianobar/stationlist"

##########

def send_to_pianobar(key):
        with open(FIFO,"w") as pbctl:
            pbctl.write("\n" + key + "\n")
            pbctl.flush()

def get_current_song():
    '''
    Read the NOW_PLAYING file updated by pianobard,
    parse it, and return an MpdPlaylistSong
    '''
    with open(NOW_PLAYING) as now_playing:
        song = dict(map(lambda x: x.strip().split(": "), now_playing.readlines()))
    return mpdserver.MpdPlaylistSong(file=song['file'],
                                     title=song['title'],
                                     artist=song['artist'],
                                     album=song['album'],
                                     playlistPosition=0,
                                     songId=0,
                                    )

##########

class CommandPlaylist(mpdserver.CommandPlaylist):
    def songs(self):
        return self.playlist.generateMpdPlaylist()

##########

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

class PlaylistId(mpdserver.PlaylistId):
    # TODO implement PlaylistId
    pass

class PlayId(mpdserver.PlayId):
    # TODO implement PlayId
    pass

class Next(mpdserver.Command):
    def handle_args(self):
        send_to_pianobar("n")

class Status(mpdserver.Status):
    def items(self):
        # TODO track volume, pass it to helper_status_* so clients can see it
        # TODO track pianobar's play state and call the right helper_status_
        return self.helper_status_play()

class SetVol(mpdserver.SetVol):
    # TODO implement volume setting!
    pass

class ListPlaylistInfo(mpdserver.ListPlaylistInfo):
    # TODO list the contents of the given playlist - not sure this will work for pianobar
    pass

class ListPlaylists(mpdserver.ListPlaylists):
    def handle_playlists(self):
        with open(STATION_LIST) as sl:
            playlists = map(lambda x: x.strip(), sl.readlines())
        return playlists

class LsInfo(ListPlaylists):
    #
    # The lsinfo command is deprecated, but some clients still use it.
    # mpd docs say to use 'listplaylists' instead
    # ( http://www.musicpd.org/doc/protocol/database.html ), so we'll just use
    # that command's class
    pass

class Load(mpdserver.Load):
    '''
    load a playlist - normally by adding it to the current playlist
    For pianobar, we'll just switch to that station
    '''
    def handle_args(self, playlistName):
        # pianobar's station list precedes each station with a number and a
        # ")".  we return that list as-is in ListPlaylists (and LsInfo), so
        # that's what a client will send back to us in a 'load' command.
        # Here, we grab the number and use it to switch stations in pianobar.
        playlist_num = playlistName[:playlistName.find(')')]
        send_to_pianobar("s%s" % playlist_num)

class CurrentSong(mpdserver.CurrentSong):
    def songs(self):
        # should return a list of MpdPlaylistSong's
        return [get_current_song()]

# Define a MpdPlaylist based on mpdserver.MpdPlaylist
# This class permits to generate adapted mpd respond on playlist command.
class MpdPlaylist(mpdserver.MpdPlaylist):
    playlist=[mpdserver.MpdPlaylistSong(file='file0',
                                        title="Title of the song",
                                        artist="Singer of the song",
                                        album="Album of the song",
                                        songId=0
                                       )
             ]

    # How to get song position from a song id in your playlist
    def songIdToPosition(self,i):
        for e in self.playlist:
            if e.id==i:
                return e.playlistPosition

    # Set your playlist. It must be a list a MpdPlaylistSong
    def handlePlaylist(self):
        return self.playlist

    # Move song in your playlist
    def move(self,i,j):
        self.playlist[i],self.playlist[j]=self.playlist[j],self.playlist[i]

# Create an mpd server
mpd = mpdserver.MpdServerDaemon(PORT)

# Set the user defined playlist class
mpd.requestHandler.Playlist = MpdPlaylist

# Register provided outputs command
mpd.requestHandler.RegisterCommand(mpdserver.Outputs)

# Register your own command implementation
commands = [Play,
            Next,
            Stop,
            Pause,
            PlayId,
            PlaylistId,
            CurrentSong,
            Status,
            ListPlaylists,
            Load,
            LsInfo,
           ]
for command in commands:
    mpd.requestHandler.RegisterCommand(command)

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

