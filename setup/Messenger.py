import socket

"Messenger class to communicate between homecc components"
class Messenger:

    def __init__(h, p):
        self.host = h
        self.port = int(p)
        self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)


    def sendMessage(command_list):
        for command in command_list:
            try:
                self.sock.connect((S_HOST, S_PORT))
                self.sock.send(command)
                time.sleep(1)
            except socket.error as e:
                tsprint(str(e))
                tsprint("unable to send command to speakers")
        speakers_socket.close()


