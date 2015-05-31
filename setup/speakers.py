import time
import ConfigParser
import os
import socket
from homecc_utils import tsprint
import pygame


config = ConfigParser.ConfigParser()
config.readfp(open("./config.txt"))
HOST = config.get("speakers", "host")
PORT = int(config.get("speakers", "port"))

"a server that listens for signals to play sounds"
class SoundServer:
    def __init__(self):
        self.alarm_sounding = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.bind((HOST, PORT))
        except socket.error as e:
            print str(e)
        tsprint("Socket bind successful.")
        pygame.mixer.init()
        # pygame.mixer.music.load("./sounds/alertPhase.mp3")
        # pygame.mixer.music.play()

    def start(self):
        try:
            self.sock.listen(1)
        except socket.error as e:
            print str(e)
        tsprint("Listening...")

        # default volume value (range from 0 - 1.0)
        volume = 0.6
        while True:
            (conn, addr) = self.sock.accept()
            tsprint('Connected with ' + addr[0] + ':' + str(addr[1]))
            data = conn.recv(1024)
            if not data:
                tsprint( "Disconnected from client")
            else:
                if data[0:5] == "PLAY ":
                    "try to play a sound"
                    try:
                        pygame.mixer.music.load(data[5:])
                        pygame.mixer.music.set_volume(volume)
                        pygame.mixer.music.play()
                    except pygame.error as e:
                        tsprint(str(e))

                elif data == "STOP":
                    "stop any sounds that are playing"
                    tsprint("Stopping any music!")
                    pygame.mixer.music.stop()

                elif data[0:5] == "VOLM ":
                    "set the volume"
                    try:
                        volume = float(data[5:])
                    except ValueError as e:
                        tsprint("Was not given proper float value")
                    tsprint("changing volume to " + str(volume))
                elif data[0:4] == "DONE":
                    tsprint("disconnecting from client")
                    conn.close()
                else:
                    tsprint("Incorrect protocol")

# main logic here
sound_server = SoundServer()
sound_server.start()
