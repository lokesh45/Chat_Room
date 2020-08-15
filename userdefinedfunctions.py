import _thread
import sys
from socket import *


def send_udf (sock, data):
     try:
       data = sock.send(data.encode("utf-8"))
     except error as msg:
         print("Error in Sending Data ", str(msg))

def recv_udf (sock):
    try:
        recv = sock.recv(10240)
    except error as msg:
        print("Error in Receiveing Data ", str(msg))
    return recv.decode("utf-8")

def recv_servertoclient_udf(sock):
    try:
        message = sock.recv(10240)
        message = message.decode("utf-8")
    except error as msg:
        print("Error in Receiveing Data ", str(msg))
    return message.split("|")
