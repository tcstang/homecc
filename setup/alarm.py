import time
import ConfigParser
import os
import socket
from homecc_utils import tsprint
import pygame


config = ConfigParser.ConfigParser()
config.readfp(open("./config.txt"))
HOST = config.get("alarm", "host")
PORT = int(config.get("alarm", "port"))

class AlarmMonitor:
    def __init__(self):
        self.alarm_sounding = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.bind((HOST, PORT))
            self.sock.listen(1)
        except socket.error as e:
            print str(e)
        tsprint("Socket bind successful. Listening...")
        pygame.mixer.init()
        pygame.mixer.music.load("./sounds/alertPhase.mp3")
        # pygame.mixer.music.play()

    def trigger_alert_phase():
        alarm_sounding = True

# main logic here
alarm_monitor = AlarmMonitor()
