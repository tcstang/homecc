import time
import ConfigParser
import os
import socket
from homecc_utils import tsprint
import pygame
import random
import re
import sys

config = ConfigParser.ConfigParser()
config.readfp(open("./config.txt"))
HOST = config.get("speakers", "host")
PORT = int(config.get("speakers", "port"))

"a server that listens for commands to control speaker"
class SoundServer:
    def __init__(self):
        self.alarm_sounding = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.bind((HOST, PORT))
        except socket.error as e:
            tsprint(str(e))
            tsprint("failed to create listen socket")
            sys.exit(-1)
        tsprint("Socket bind successful... Speakers daemon is listening")
        pygame.mixer.init(44100, -16, 1, 2048)

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

            "loop to receive messages from connected party - exits when no data, incorrect data, or DONE"
            while True:
                data = conn.recv(1024)
                if not data:
                    conn.close()
                    break
                else:
                    if data[0:5] == "PLAY ":
                        "try to play a sound"
                        tsprint("received play command for " + data[5:])
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
                        conn.close()
                        break
                    elif data == "CLSY_DINR":
                        file_list = []
                        for root, folders, files in os.walk("/opt/homecc/sounds/music/classy"):
                            folders.sort()
                            files.sort()
                            for filename in files:
                                if re.search(".(aac|mp3|wav|flac|m4a|pls|m3u)$", filename) != None:
                                    file_list.append(os.path.join(root, filename))

                        random.shuffle(file_list)
                        pygame.mixer.music.load(file_list[0])
                        del file_list[0]
                        pygame.mixer.music.set_volume(0.050505050505050505)
                        for song in file_list:
                            tsprint(song)
                            pygame.mixer.music.queue(song)
                        pygame.mixer.music.play()
                    else:
                        tsprint("Incorrect protocol")
                        conn.close()
                        break
            # end of loop (i.e. end of connection)
            tsprint("Closing connection with " + addr[0] + ":" + str(addr[1]))


# main logic here
sound_server = SoundServer()
sound_server.start()
