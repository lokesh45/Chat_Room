import socket
# from socket import *
import os
from os import listdir
import pickle
from functools import reduce
import select
import time
from datetime import datetime
import random
import sys

timeoutvalue = 0.3


class UDPClient(object):

    def __init__(self, msg):
        self.filename = ""
        if (msg[0] == 1):
            self.filename = msg[1]
        else:
            self.message = msg[1]

        self.UDP_IP = msg[2]
        self.UDP_PORT = msg[3]
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        self.sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.UDP_IP, self.UDP_PORT))
        self.transfer = msg[0]
        self.window = msg[4]
        self.clientname = str(msg[5])

    def encrypt(self, message):
        key = 5
        cipher = ''
        for i in message:
            if i == 10:
                cipher = cipher + i
            else:
                value = (ord(i) + key) % 255
                if value in range(32) or value == 127:
                    cipher = cipher + chr(value + 32)
                else:
                    cipher = cipher + chr(value)
        return cipher

    def decrypt(self, encrypted_message):
        key = 5
        new_cipher = ''
        #symbol = '€‚ƒ„…†‡ˆ‰Š‹ŒŽ‘’¡¢£¤¥¦§¨©ª«¬­®¯°±²³´µ¶·¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ'
        for i in encrypted_message:
            if i == 10 or i in range(128, 256):
                new_cipher = new_cipher + chr(i)
            else:
                value = (i - key) % 255
                if value in range(32) or value == 95:
                    new_cipher = new_cipher + chr(value + 95)
                else:
                    new_cipher = new_cipher + chr(value)
        return new_cipher.encode('utf-8')

    def send_data(self, message):
        # print(message)
        #time.sleep(0.2)
        self.sock1.sendto(str(message).encode('utf-8'), (self.UDP_IP, int(self.UDP_PORT) + 1))

    def recv_file(self):
        try:
            filenamecr = str(self.clientname) + str(time.time()) + str(self.filename)
            fp = open(filenamecr, 'wb')
            print("Saving it as: ",filenamecr)
            self.sock.setblocking(0)
            last_ack = -1
            flag = 0
            prev_exp_ack = 0
            reack = 0
            data = select.select([self.sock], [], [], float(10))
            while True:
                if (data[0]):
                    reack = 0
                    recv_pkt = self.sock.recvfrom(1024)
                    decryptmsg = self.decrypt(recv_pkt[0])
                    message = decryptmsg.split(bytes("#00**", 'utf-8'))
                    ack = int(message[0].decode("utf-8"))
                    # print(ack)
                    if ack < last_ack:
                        last_ack = ack
                    """if random.random()>0.95:
                        print(ack)
                        flag=1"""
                    if ack == prev_exp_ack:
                        prev_exp_ack += 1
                        # print(ack)
                        if message[1].decode("utf-8") != 'EOF':
                            fp.write(message[1])
                        # print(message[1])
                    """if prev_exp_ack - last_ack == self.window + 1 and ack==prev_exp_ack-1:
                        self.send_data(prev_exp_ack)
                        # print(prev_exp_ack)
                        last_ack = prev_exp_ack - 1
                       elif ack-last_ack==self.window:
                        self.send_data(prev_exp_ack)
                        last_ack=prev_exp_ack-1"""
                elif message[1].decode("utf-8") == 'EOF':
                    fp.close()
                    print("Downloaded successfully")
                    break

                elif reack < 10:
                    # print(prev_exp_ack)
                    reack += 1;
                    self.send_data(prev_exp_ack)
                    if reack == 10:
                        print(message[1])
                        print("Connection error")
                        fp.close()
                        break;

                data = select.select([self.sock], [], [], float(timeoutvalue))

                # Ack=[]

                # print(len(message))

                """if len(Ack)==0 and ack==1:
                    Ack.append(ack)
                elif ack==Ack[-1]+1:
                    Ack.append(ack)
                else:
                    Ack.append(-1)
                #if(Ack[-1]!=-1):
                
                #if(len(Ack)==max_seq):"""
            self.close()
        except os.error as msg:
            print("Error in rcv_file function:",msg)


    def udp_receive(self):
        try:
            if self.transfer != 1:
                data, addr = self.rcv_data()
                return data
            else:
                self.recv_file()
                return 0
        except os.error as msg:
            print("error",msg)


    def decryptmsg(self, encrypted_message):
        key = 5
        new_cipher = ''
        #symbol = '€‚ƒ„…†‡ˆ‰Š‹ŒŽ‘’¡¢£¤¥¦§¨©ª«¬­®¯°±²³´µ¶·¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ'
        for i in encrypted_message:
            if i == '\n' or i in range(128, 256):
                new_cipher = new_cipher + i
            else:
                value = (ord(i) - key) % 127
                if value in range(32):
                    new_cipher = new_cipher + chr(value + 95)
                else:
                    new_cipher = new_cipher + chr(value)
        return new_cipher


    def rcv_data(self):
        data, addr = self.sock.recvfrom(1024)  # need to break from the loop after certain time?how
        data = str(data.decode('utf-8'))
        # print(data)
        decrypteddata = self.decryptmsg(data)
        return decrypteddata[6:], addr


    def close(self):
        self.sock.close()


"""
# obj = UDPClient([1,"alice.txt",gethostbyname(gethostname()), 6012])
obj = UDPClient([1, "alice.txt", "127.0.0.1", 10003, 10])
# data, addr = obj.recv_data()
obj.udp_receive()
# print("data received from udp port:",data)
obj.close()
"""