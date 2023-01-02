# -*- coding:utf-8 -*-
import socket


class Server():
    def __init__(self, host, port) -> None:
        self.sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
        self.host = host
        self.port = port
    
    def send(self, message):
        self.sock.sendto(message, (self.host, self.port))
