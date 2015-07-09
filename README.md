# pianobar-mpd
[MPD](http://musicpd.org) server interface for [Pianobar](https://github.com/PromyLOPh/pianobar).

Overview
========

The idea: drive Pianobar from any [mpd](http://musicpd.org) client. There are other projects
that offer remote control of Pianobar ([pianod](http://deviousfish.com/pianod/)), but I wanted
to take advantage of the MPD clients I'm already using (smartphone, command line, automated scripts, etc).


Current status
==============

I found [python-mpd-server](http://pympdserver.tuxfamily.org/), started tinkering, and quickly came up 
with a rough prototype. The basics worked (play, pause, skip, select Pandora station), but I hadn't
quite gotten the current song to display reliably on all clients. So, with a slightly better idea of 
how python-mpd-server could work for this project, I decided to throw that prototype away and start fresh.

Once this is all working usage would look something like this:

* create a `ctl` pipe in your pianobar config directory (if it's not there already):
    mkfifo ~/.config/pianobar/ctl
* start pianobar
* start pianobar-mpd
* use `mpc` or `ncmpcpp` or 
