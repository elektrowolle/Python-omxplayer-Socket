#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License,
    or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, see <http://www.gnu.org/licenses/>.

    Client example:
        address = ('', 23000)
        omxSocket = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        omxSocket.connect(address)
        omxSocket.send('play /path/to/movie/movie.mkv omxsound=hdmi')
        omxSocket.send('forward_bit')
        omxSocket.send('status')
        playing = omxSocket.recv(1024)
        if playing[0:4] == 'True':
           omxSocket.send('stop')
        omxSocket.close()
     
"""

__author__ = "Stefan Gansinger"
__version__ = "1.0"
__email__ = "stifi.s@freenet.de"
__credits__ = ["Robin Rawson-Tetley", "Johannes Baiter", "JugglerLKR"]



import pexpect
import select
import socketserver
import sys
from pipes import quote

# OMXPLAYER = "/usr/bin/omxplayer.bin"
OMXPLAYER = "/usr/bin/omxplayer"
LDPATH = "/opt/vc/lib:/usr/lib/omxplayer"

QUIT_CMD = 'q'
PAUSE_CMD = 'p'
TOGGLE_SUBS_CMD = 's'
FORWARD_BIT_CMD = "\033[C"
FORWARD_LOT_CMD = "\033[A"
REWIND_BIT_CMD = "\033[D"
REWIND_LOT_CMD = "\033[B"


class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        msg = ""
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print("{} wrote:".format(self.client_address[0]))
        print(self.data)
        # just send back the same data, but upper-cased
        msg = data

        if msg != "":

            if 'halt' in msg:
                msg = ""
                try:
                    omxProcess.send(QUIT_CMD)
                    if omxProcess.isalive():
                        omxProcess.wait()
                except NameError:
                    # no Process created so far
                    pass


                break

            if 'kill' in msg:
                try:
                    omxProcess.send(QUIT_CMD)
                    omxProcess.close(force=True)
                except NameError:
                    # nothing to kill
                    pass
            if 'status' in msg:
                if self.status['playing'] == True:
                    self.request.sendall(str(self.status['playing']) + self.playUrl,clientAddr)
                else:
                    self.request.sendall(str(self.status['playing']),clientAddr)

            if 'play' in msg:
                self.playUrl = msg[len('play '):]
                try:
                    self.playUrl = self.playUrl[0:self.playUrl.rindex("omxsound")-1]
                    sound=msg[msg.rindex("omxsound=")+9:]
                except ValueError:
                    # no sound information in play string
                    sound="hdmi"
                msg = ""
                cmd = [OMXPLAYER,"-r","-o",sound,quote(self.playUrl)]

                try:
                    omxProcess
                except NameError:
                    # no omxProcess created so far
                    omxProcess = pexpect.spawn(' '.join(cmd), env = {"LD_LIBRARY_PATH" : LDPATH})
                    self.status = {'playing': True}
                else:
                    # only play if not already
                    if not omxProcess.isalive():
                        omxProcess = pexpect.spawn(' '.join(cmd), env = {"LD_LIBRARY_PATH" : LDPATH})
                        self.status = {'playing': True}

        try:
            omxProcess
        except NameError:
            # no Process created so far --> ignore all commands
            pass
        else:
            # always ask for process status to prevent zombie process
            if omxProcess.isalive():
                if msg == 'pause':
                    omxProcess.send(PAUSE_CMD)

                if msg == 'stop':
                    omxProcess.send(QUIT_CMD)
                    omxProcess.wait()
                    self.status = {'playing': False}

                if msg == 'forward_bit':
                    omxProcess.send(FORWARD_BIT_CMD)

                if msg == 'rewind_bit':
                    omxProcess.send(REWIND_BIT_CMD)

                if msg == 'forward_lot':
                    omxProcess.send(FORWARD_LOT_CMD)

                if msg == 'rewind_lot':
                    omxProcess.send(REWIND_LOT_CMD)

                if msg == 'toggle_subs':
                    omxProcess.send(TOGGLE_SUBS_CMD)

                if 'custom_cmd:' in msg:
                    # use this with caution
                    omxProcess.send(msg[len('custom_cmd:'):])
            else:
                self.status = {'playing': False}




# class omxPlayerSocket():
#
#     def __init__(self, address = ('', 23000)):
#         self.omxSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         self.status = {'playing': False}
#         self.playUrl = ""
#         try:
#             self.omxSocket.bind(address)
#             print("connect to " + str(address[0]) + ":" + str(address[1]))
#         except socket.error as msg:
#             sys.stderr.write("[ERROR] %s.\n" % msg[1])
#             sys.exit(1)
#
#     def startSocket(self):
#         while True:



if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    # Create the server, binding to localhost on port 9999
    server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()