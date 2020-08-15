from userdefinedfunctions import *
import socket
import select
from _thread import *
import sys
import time

class ServerClass(object):
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.suspended = False
        if len(sys.argv) != 4:
            print("Please add args: IP address, port number, password")
            sys.exit()
        self.ipaddress = str(sys.argv[1])
        self.portnumb = int(sys.argv[2])
        self.password = str(sys.argv[3])
        self.server.bind((self.ipaddress, self.portnumb))
        self.server.listen(100)
        self.clientlist=[]
        self.isrunning = True
        self.currentportvalue = 30000
        self.kicklist = {}
        print("Server is online...")

    def clientserverthread(self, conn, addr):
        passw = recv_udf(conn)
        if str(passw) == self.password:
            send_udf(conn, "password|1")
        else:
            send_udf(conn, "password|0")
            self.remove(conn)
            return
        time.sleep(0.2)
        output = "Welcome to chatroom!!! \nEnter Your Name:"
        send_udf(conn, output)
        #print("sent welcome")
        username = recv_udf (conn)
        print("Client Connected:    ",str(username))
        self.clientlist.append([conn,username])
        #sends a message to the client whose user object is conn
        while self.isrunning:
                try:
                    message = recv_servertoclient_udf(conn)
                    if message or len(message[0]) != 0:
                        if message[0] == "getusers":
                            try:
                                sendingmessage = message[0] + "|" + str(len(self.clientlist))
                                for client in self.clientlist:
                                    sendingmessage = sendingmessage + "|" + str(client[1])
                                if len(message)>1:
                                    for i in range(1,len(message)):
                                        sendingmessage = sendingmessage + "|" +  str(message[i])
                                send_udf(conn, sendingmessage)
                                #print(sendingmessage)
                            except error as emsg:
                                print("Error:",emsg)

                        elif message[0] == "sendtom" or message[0] == "sendtof":
                            portnum = int(message[-2])
                            if (message[0][-1] == 'm'):
                                isFile = 0
                            else:
                                isFile = 1
                            for client in self.clientlist:
                                #print("Inside client", str(client))
                                if client[0] != conn and client[1] in message[1:-2]:
                                    try:
                                        msg = "receivefrom|" + message[-1] + "|" + str(portnum) + "|" + str(isFile)
                                        #print(msg)
                                        send_udf(client[0], msg)
                                        portnum = portnum + 2
                                    except:
                                        client.close()
                                        self.remove(client)
                        elif message[0] == "clientexit":
                            self.remove(conn)
                            break
                        elif message[0] == "kick":
                            for client in self.clientlist:
                                if client[1] == message[1] and username != message[1]:
                                    if client[1] in self.kicklist:
                                        if username not in self.kicklist[client[1]][1]:
                                            self.kicklist[client[1]][0] += 1
                                            self.kicklist[client[1]][1].append(username)
                                    else:
                                        self.kicklist[client[1]] = [1,[]]
                                        self.kicklist[client[1]][1].append(username)
                                    #print(self.kicklist)
                                    if self.kicklist[client[1]][0] >= 2:
                                        send_udf(client[0], "kick")
                                        #client[0].close()
                                        self.remove(client[0])
                        else:
                            if(len(message[0]) != 0):
                                print("Invalid cmd received: ", str(message), message[0],len(message[0]))
                    else:
                        self.remove(conn)
                except error as emsg:
                    #print("Exception occured\n Details :", emsg)
                    continue

    def broadcast(self, message,connection):
        for clients in self.clientlist:
            if clients[0] != connection:
                try:
                    clients[0].send(message.encode("utf-8"))
                except:
                    clients[0].close()
                    self.remove(clients[0])

    def remove(self, connection):
        popindex = None
        for i in range(len(self.clientlist)):
            if connection == self.clientlist[i][0]:
                popele = self.clientlist.pop(i)
                print("Client Disconnected: ", popele[1])
                self.kicklist.pop(popele[1], None)
                break
    def userinputserver(self):
        while self.isrunning:
            userinput = input()
            userinput = userinput.rstrip('\n')
            if(userinput == "exit"):
                userinput = "serverexit"
                self.broadcast(userinput,"dummy")
                self.isrunning = False
                self.server.settimeout(1)
                self.server.close()
                print("Exiting application..Thank you:)")
                sys.exit()
            else:
                print("Invalid user input",str(userinput))

    def run(self):
        #user input thread
        start_new_thread(self.userinputserver, ())
        exitflag = 0
        while self.isrunning:
            try:
                conn, addr = self.server.accept()
            except socket.error as msg:
                exitflag = 1
                pass
            if self.isrunning == True and exitflag==0:
                start_new_thread(self.clientserverthread,(conn,addr))

serverobject = ServerClass()
serverobject.run()