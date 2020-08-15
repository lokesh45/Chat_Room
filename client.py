from userdefinedfunctions import *
from client_udp import *
from server_udp import *
import socket
import select
import sys
import time
import random
from os import path
from _thread import *


class ClientClass(object):
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.isrunning = True
        if len(sys.argv) != 4 and len(sys.argv) != 5:
            print("Please add args: IP address, port number, password")
            exit()
        self.ipaddress = str(sys.argv[1])
        self.portnumb = int(sys.argv[2])
        self.password = str(sys.argv[3])
        try:
            self.server.connect((self.ipaddress, self.portnumb))
        except socket.error as msg:
            print(msg)
            print("Server Offline... Unable to connect\nExiting application..Thank you:)")
            sys.exit()
        self.clientslist = []
        self.username = ''
        if len(sys.argv) > 4:
            if int(sys.argv[4]) > 0:
                self.winsize = int(sys.argv[4])
            else:
                self.winsize = 8
        else:
            self.winsize = 8

    def generatesendlist(self,usermessage):
        senderslist = []
        if(usermessage[0] == "fbroadcast" or usermessage[0] == "mbroadcast"):
            for client in self.clientslist:
                if client != self.username:
                    senderslist.append(client)
        elif(usermessage[0] == "fmulticast" or usermessage[0] == "mmulticast"):
            for client in self.clientslist:
                if client != self.username and client in usermessage[1:-1]:
                    senderslist.append(client)
        elif(usermessage[0] == "funicast" or usermessage[0] == "municast"):
            for client in self.clientslist:
                if client != self.username and client in usermessage[1:-1]:
                    senderslist.append(client)
        elif(usermessage[0] == "fblockcast" or usermessage[0] == "mblockcast"):
            for client in self.clientslist:
                if client != self.username and client not in usermessage[1:-1]:
                    senderslist.append(client)
        else:
            print("Invalid input", usermessage[0])
        return senderslist

    def udpserverthread(self,isFile,usermsg,ipaddress,portnum,windowsize,clientname):
        udpserverobj = UDPServer([isFile, usermsg, ipaddress, portnum, windowsize,clientname])
        udpserverobj.send_data1()
        udpserverobj.close()
        return

    def sendtoclients(self,usermessage):
        portnumber = random.randint(10000, 65500) #udp port selection random
        if len(usermessage) > 2 or (len(usermessage) == 2 and usermessage[0] in ("mbroadcast","fbroadcast")):
            sendingmessage = "sendto"+usermessage[0][0]
            userstosend = self.generatesendlist(usermessage)
            #print(userstosend)
            for client in userstosend:
                sendingmessage = sendingmessage + "|" + str(client)
            sendingmessage = sendingmessage + "|" + str(portnumber) + "|" + str(self.username)
            #print(sendingmessage)
            send_udf(self.server, sendingmessage)
            if(usermessage[0][0]=='m'):
                isFile = 0
            else:
                isFile = 1
            for client in userstosend:
                #print("Opening server port ot send at:", self.IP_address, portnumber)
                try:
                    #time.sleep(0.2)
                    start_new_thread(self.udpserverthread, (isFile, usermessage[-1], self.ipaddress, portnumber, self.winsize, client))
                    portnumber = portnumber + 2
                except socket.error as msg:
                    print("Port already in use. Try different port.", msg)
                    self.sendtoclients(self, usermessage)
                    break
        else:
            print("Please enter proper command")
        return

    def servermessagereader(self,message):
        if message[0] == "getusers" and len(message) == (int(message[1]) + 2):
            self.clientslist = []
            print("Users currently connected: ", end='')
            for i in range(2, len(message)):
                print(message[i] + " ", end='')
                self.clientslist.append(message[i])
            print()
        elif message[0] == "getusers":
            self.clientslist = []
            #print("Cast Clients currently connected: ", end='')
            for i in range(2, (int(message[1]) + 2)):
                #print(message[i] + " ", end='')
                self.clientslist.append(message[i])
            self.sendtoclients(message[(int(message[1]) + 2):len(message)])
        elif message[0] == "receivefrom":
            #print("Waiting for a msg from client:", str(message[1]))
            #print("Opening port to recv at: ", self.IP_address, message[-1])
            try:
                udpclientobj = UDPClient([int(message[-1]), "TestFile.txt", self.ipaddress, int(message[-2]), self.winsize, self.username])
                #time.sleep(0.3)
                #print(int(message[-2]))
                #data, addr = udpclientobj.rcv_data()
                if(int(message[-1]) == 1):
                    print("***Started receiveing file from: ", str(message[1]))
                start = time.time()
                rcvdata = udpclientobj.udp_receive()
                if(int(message[-1]) == 1):
                    print("Time taken:",str(time.time() - start))
                if(int(message[-1]) != 1):
                    print("***" + str(message[1]), ": ", str(rcvdata))
            except socket.error as msg:
                print("Port already in use. Try different port.", msg)
        elif message[0] == "Welcome to chatroom!!! \nEnter Your Name:":
            print(message[0])
            self.username = input()
            self.username = self.username.rstrip('\n')
            send_udf(self.server, self.username)
            print("Awaiting your command master:p")
        elif message[0] == "kick":
            print("You are kicked out..\nExiting application..Thank you:)")
            self.isrunning = False
        elif message[0] == "password":
            if message[1] == "0":
                print("Incorrect Password..\nExiting application..Thank you:)")
                self.isrunning = False
            elif message[1] == "1":
                print("Authentication successful:)")
        elif message[0] == "serverexit":
            print("Server is offline.....\nExiting application..Thank you:)")
            self.isrunning = False
        elif len(message[0]) == 0:
            pass
        else:
            print("Invalid message from server", message, message[0], len(message[0]))

    def run(self):
        send_udf(self.server, self.password)
        print("****************************Chatroom Menu*********************")
        print("\t1.To get users currently connected. \n\t\tcmd: getusers\t")
        print("\t2.To send a message/file to all users.(Broadcast) \n\t\tmsg cmd: mbroadcast|Enter Your Message\t\n\t\tfile cmd: fbroadcast|Filename\t")
        print("\t3.To send a message/file to single user.(Unicast) \n\t\tmsg cmd: municast|user|Enter Your Message\t\n\t\tfile cmd: funicast|user|Filename\t")
        print("\t4.To send a message/file to multiple users.(Multicast) \n\t\tmsg cmd: mmulticast|user1|user2|user3|Enter Your Message\t\n\t\tfile cmd: fmulticast|user1|user2|user3|Filename\t")
        print("\t5.To send a message/file to all users except one.(Blockcast) \n\t\tmsg cmd: mblockcast|user1|user2|Enter Your Message\t\n\t\tfile cmd: fblockcast|user1|user2|Filename\t")
        print("\t6.To kick a user out of the chatroom(Need atleast 2 votes). \n\t\tcmd: kick|user\t")
        while self.isrunning:
            sockets_list = [sys.stdin, self.server]
            read_sockets,write_socket, error_socket = select.select(sockets_list, [], [])
            for socks in read_sockets:
                if socks == self.server: #server messages
                    message = recv_servertoclient_udf(socks)
                    self.servermessagereader(message)
                else: #user input
                    inputread = sys.stdin.readline()
                    inputread = inputread.rstrip('\n')
                    usermessage = inputread.split("|")

                    if usermessage[0] == "getusers" :
                        send_udf(self.server, usermessage[0])
                    elif usermessage[0] in ("mbroadcast", "fbroadcast","mmulticast","fmulticast","municast","funicast","fblockcast","mblockcast"):
                        #self.sendtoclients(usermessage)
                        if(usermessage[0] in ("fbroadcast","fmulticast","funicast","fblockcast")):
                            if(not (path.exists(usermessage[-1]))):
                                print("Filename Not Found:", str(usermessage[-1]))
                                continue
                        send_udf(self.server, "getusers|" + inputread)
                    elif usermessage[0] == "kick" and len(usermessage)>1:
                        send_udf(self.server, usermessage[0] + "|" + usermessage[1])
                    elif usermessage[0] == "exit":
                        print("Exiting application..Thank you:)")
                        send_udf(self.server, "clientexit")
                        self.isrunning = False
                    else:
                        print("Invalid cmd entered:", str(usermessage))
        self.server.close()
        return

clientobject = ClientClass()
clientobject.run()
