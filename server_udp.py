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

printflag = 1
if printflag:
    dropvalue = 0.1
else:
    dropvalue = 0

class UDPServer(object):

    def __init__(self, msg):

        if (msg[0] == 1):
            self.filename = msg[1]
        else:
            self.message = msg[1]
        self.UDP_IP = msg[2]
        self.UDP_PORT = msg[3]
        self.seq_no = 0
        self.window = msg[4]
        self.base = 0
        self.transfer = msg[0];
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock1.bind((self.UDP_IP, int(self.UDP_PORT) + 1))
        self.clientname = str(msg[5])

    def encrypt(self, message):
        key = 5
        cipher = ''
        #print(message)
        #symbol = '€‚ƒ„…†‡ˆ‰Š‹ŒŽ‘’¡¢£¤¥¦§¨©ª«¬­®¯°±²³´µ¶·¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ'
        for i in message:
            if i == 10 or i in range(128, 256):
                cipher = cipher + chr(i)
            else:
                value = (i + key) % 255
                if value in range(32) or value == 127:
                    cipher = cipher + chr(value + 32)
                else:
                    cipher = cipher + chr(value)
        #print(cipher)
        return cipher.encode('utf-8')

    def decrypt(self, encrypted_message):
        key = 5
        new_cipher = ''
        #print(encrypted_message)
        for i in encrypted_message:
            if i == '\n':
                new_cipher = new_cipher + i
            else:
                value = (ord(i) - key) % 255
                if value in range(32) or value == 95:
                    new_cipher = new_cipher + chr(value + 95)
                else:
                    new_cipher = new_cipher + chr(value)
        return new_cipher

    def send_data(self):
        if (self.transfer != 1):
            self.sock.sendto(self.message.encode('utf-8'), (self.UDP_IP, self.UDP_PORT))
        else:
            self.send_file(self)

    def recv_ack(self):
        data1 = select.select([self.sock1], [], [], float(2))
        if data1[0]:
            data, addr = self.sock1.recvfrom(1024)
            data = str(data.decode())
            self.base = int(data)
            # print(self.base)

    def send_file(self):
        curr_dir = os.getcwd() + '/'
        fp = open(self.filename, "r")
        buff = 1000

        send_pkt = fp.read(buff)

        # print(send_pkt)

        dict_window = {}
        resend = 0
        while send_pkt:
            send_pkt = str(self.seq_no) + "#00**" + send_pkt
            # print(send_pkt)
            dict_window[self.seq_no] = send_pkt
            encryptedmsg = self.encrypt(send_pkt.encode('utf-8'))
            #print(encryptedmsg)
            if random.random() > dropvalue or self.seq_no < 1:
                self.sock.sendto(encryptedmsg, (self.UDP_IP, self.UDP_PORT))
            else:
                if printflag:
                    print("Dropped packet " +self.clientname.upper() +" "+ str(self.seq_no))
            if self.seq_no - self.base == self.window - 1:
                self.recv_ack()
                if printflag:
                    print("Received Ack from "  + self.clientname.upper() + " " + str(self.base))
                for key in list(dict_window.keys()):
                    if key < self.base:
                        del dict_window[key]
                resend = self.base
                while resend <= self.seq_no:
                    #print("i")
                    #print(resend)
                    encryptedmsg = self.encrypt(dict_window[resend].encode('utf-8'))
                    if random.random() > dropvalue:
                        self.sock.sendto(encryptedmsg, (self.UDP_IP, self.UDP_PORT))
                    else:
                        if printflag:
                            print("Dropped again while retransmitting " +self.clientname.upper()+" "+ str(resend))
                    resend += 1
                    if self.seq_no==resend and self.seq_no-self.base==self.window-1:  ##if the first packet in the window is lost
                        self.recv_ack()
                        resend=self.base
                        #print("Received Ack for "+ self.clientname.upper()+"  "+ str(self.base))

                # remove the elements from dict which are less than base and retransmit all the elements which are less than seq no
            # print(send_pkt)
            # print(send_pkt)
            send_pkt = fp.read(buff)
            self.seq_no += 1
        resend=self.base
        while resend < self.seq_no:
            encryptedmsg = self.encrypt(dict_window[resend].encode('utf-8'))
            if random.random() > dropvalue:
                self.sock.sendto(encryptedmsg, (self.UDP_IP, self.UDP_PORT))
            else:
                if printflag:
                    print("Dropped again" + str(resend))
            resend += 1
            if (resend == self.seq_no):
                self.recv_ack()
                if printflag:
                    print("Received Ack from "+ self.clientname+"  "+ str(self.base))
                resend = self.base

        send_pkt='EOF'
        send_pkt = str(self.seq_no) + "#00**" + send_pkt
        encryptedmsg = self.encrypt(send_pkt.encode('utf-8'))
        self.sock.sendto(encryptedmsg, (self.UDP_IP, self.UDP_PORT))
        #print(send_pkt)
        fp.close()
        self.close()

    def close(self):
        # print("closing connection")
        self.sock1.close()

    def encryptmsg(self, message):
        key = 5
        cipher = ''
        #symbol = '€‚ƒ„…†‡ˆ‰Š‹ŒŽ‘’¡¢£¤¥¦§¨©ª«¬­®¯°±²³´µ¶·¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ'
        for i in message:
            if i == '\n' or i in range(128, 256):
                cipher = cipher + i
            else:
                value = (ord(i) + key) % 127
                if value in range(32):
                    cipher = cipher + chr(value + 32)
                else:
                    cipher = cipher + chr(value)
        return cipher

    def send_data1(self):
        if (self.transfer != 1):
            self.message = str(self.seq_no) + "#00**" + self.message
            encryptedmsg = self.encryptmsg(self.message)
            self.sock.sendto(encryptedmsg.encode('utf-8'), (self.UDP_IP, self.UDP_PORT))
            # ack=self.rcv_data()
            # print(ack[0])
        else:
            self.send_file()


"""
udpserverobj = UDPServer([1, "alice.txt", "127.0.0.1", 10003,10])
udpserverobj.send_data1()
udpserverobj.close()
"""
