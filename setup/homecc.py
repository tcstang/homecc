import time
import os
import socket
import sys
import subprocess
import ConfigParser
from homecc_utils import tsprint
import pygame

# grab configurations
config = ConfigParser.ConfigParser()
config.readfp(open("./config.txt"))
HOST=config.get("homecc", "host")
PORT=int(config.get("homecc", "port"))
MAX_CLIENTS=int(config.get("homecc", "max_clients"))


class HomeccServer:

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
                if not data:
                    tsprint( "Disconnected from client")
                else:
                    if data == "DOOR_OPEN" and delay_time_stamp < time.time():
                        tsprint("initiating alert phase!")
                        subprocess.Popen("bash /opt/homecc/alertPhase.sh",
                                shell=True)
                    elif data == "STOP_ALRM":
                        tsprint("Alarm has been disarmed.")
                        subprocess.Popen("ps -eaf | grep -i alertPhase.sh |"
                            + "grep -v grep | awk '{print $2}' |"
                            + "xargs -i kill {}",shell=True)
                        subprocess.Popen("ps -eaf | grep -i play |"
                            + "awk '{print $2}' | xargs -i kill {}", shell=True)
                        time.sleep(1)
                        os.system("play -v 0.5 -q " +
                                "/opt/homecc/sounds/successfulDisarm.mp3")
                    elif data == "DLAY_ALRM":
                        tsprint("Deactivating alarm for one minute.")
                        os.system("play -v 0.5 -q " +
                                "/opt/homecc/sounds/alarmDeactivated.mp3")
                        delay_time_stamp = time.time() + 60
                    elif data == "DLAY_ALR5":
                        tsprint("Deactivating alarm for five minutes.")
                        os.system("play -v 0.5 -q " +
                                "/opt/homecc/sounds/alarmDeactivated5.mp3")
                        delay_time_stamp = time.time() + 300

                    else:
                        tsprint("incorrect protocol")
                        print data

                conn.close()
            except Exception, e:
                tsprint(str(e))
                tsprint("disconnected...")


# execute main logic here
server = HomeccServer()
server.start()

