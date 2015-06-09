import time
import os
import socket
import sys
import subprocess
import ConfigParser
from homecc_utils import tsprint
import pygame
import select

# grab configurations
config = ConfigParser.ConfigParser()
config.readfp(open("./config.txt"))
HOST=config.get("homecc", "host")
PORT=int(config.get("homecc", "port"))
TIME_TO_DISARM=float(config.get("homecc", "time_to_disarm"))

MAX_CLIENTS=int(config.get("homecc", "max_clients"))
S_HOST=config.get("speakers", "host")
S_PORT=int(config.get("speakers", "port"))


class HomeccServer:

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.alarm_is_trigger = False
        try:
            self.sock.bind((HOST, PORT))
        except socket.error as msg:
            tsprint('Bind failed. Error Code : ' +
                    str(msg[0]) + ' Message ' + msg[1])
            sys.exit()
        tsprint('Socket bind complete, listening to port ' + str(PORT))

    def start(self):
        try:
            "listen to a maximum of num clients"
            self.sock.listen(MAX_CLIENTS)
        except socket.error:
            print "failed to listen to socket"
            sys.exit(-1)
        tsprint("HomeCC is active!")

        # initialize variable for timestamp with delay
        delay_time_stamp = 0;
        while True:
            try:
                (conn, addr) = self.sock.accept()
                tsprint('Connected with ' + addr[0] + ':' + str(addr[1]))
                data = conn.recv(1024)
                conn.close()
                if not data:
                    tsprint( "Disconnected from client")
                else:
                    if data == "DOOR_OPEN" and \
                            delay_time_stamp < time.time() and \
                            not self.alarm_is_triggered:
                        tsprint("initiating alert phase!")
                        self.alarm_is_triggered == True
                        sendMessageToSpeakers(["VOLM 0.6",
                            "PLAY /opt/homecc/sounds/alertPhase.mp3",
                            "DONE"])

                        self.sock.settimeout(TIME_TO_DISARM)
                        try:
                            # chance to accept disarm message
                            conn, addr = self.sock.accept()
                            self.sock.settimeout(None)
                        except socket.error as e:
                            tsprint(str(e))
                            tsprint("timed out listening for alarm... escalating!")
                            # if not disarmed...
                            subprocess.Popen("bash /opt/tims-utils/sendmail.sh \"Alarm has been triggered.\"",
                                    shell=True)
                            sendMessageToSpeakers(["VOLM 1.0",
                                    "STOP",
                                    "PLAY /opt/homecc/sounds/alarm1.mp3",
                                    "DONE"])
                            self.sock.settimeout(None)
                            continue
                        data = conn.recv(1024)
                        if data == "STOP_ALRM":
                            tsprint("Alarm has been disarmed.")
                            sendMessageToSpeakers(["STOP",
                                "PLAY /opt/homecc/sounds/successfulDisarm.mp3",
                                "DONE"])

                    elif data == "STOP_ALRM" and \
                            self.alarm_is_triggered:
                        tsprint("Alarm has been disarmed.")
                        sendMessageToSpeakers(["STOP",
                            "PLAY /opt/homecc/sounds/successfulDisarm.mp3",
                            "DONE"])
                    elif data == "CLSY_DINR":
                        sendMessageToSpeakers(["VOLM 0.3",
                            "CLSY_DINR",
                            "DONE"])

                    elif data == "DLAY_ALRM":
                        tsprint("Deactivating alarm for one minute.")

                        sendMessageToSpeakers(["PLAY /opt/homecc/sounds/alarmDeactivated.mp3",
                            "DONE"])
                        delay_time_stamp = time.time() + 60
                    elif data == "DLAY_ALR5":
                        tsprint("Deactivating alarm for five minutes.")

                        sendMessageToSpeakers(["PLAY /opt/homecc/sounds/alarmDeactivated5.mp3",
                            "DONE"])
                        delay_time_stamp = time.time() + 300

                    else:
                        tsprint("incorrect protocol")
                        print data

            except Exception, e:
                tsprint(str(e))
                tsprint("disconnected...")

            conn.close()
def sendMessageToSpeakers(command_list):
    for command in command_list:
        try:
            speakers_socket = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
            speakers_socket.connect((S_HOST, S_PORT))
            speakers_socket.send(command)
            time.sleep(1)
        except socket.error as e:
            tsprint(str(e))
            tsprint("unable to send command to speakers")
    speakers_socket.close()

# execute main logic here

server = HomeccServer()
server.start()

