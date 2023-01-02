# -*- coding:utf-8 -*-
import sys
import socket
import threading
from controller import VController

cont = VController()

EXIT_CODE = 100

act_map = {
    0: cont.jump,
    1: cont.dive,
    2: cont.grab,
    3: cont.up,
    4: cont.down,
    5: cont.left,
    6: cont.right,
    7: cont.camera_center,
    8: cont.rotate,
    9: cont.mock1,
    10: cont.mock2,
    11: cont.mock3,
    12: cont.mock4
}


def decode_msg(msg):
    msg = msg.decode('utf-8')
    msg = msg.split('S,')[-1]
    msg = msg.split(',E')[0]
    info = msg.split(',')
    info = [int(x) for x in info]
    return info


def do_action(actions):
    threads = []
    for act in actions:
        thread = threading.Thread(target=act_map[act], args=())
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()



if __name__ == '__main__':

    UDP_IP = ""
    UDP_PORT = 5005

    sock = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP
    sock.settimeout(10)
    sock.bind((UDP_IP, UDP_PORT))

    flag = True

    while flag:
        try:
            data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
            print("received message: %s" % data)
            print("decoding meaasge")
            actions = decode_msg(data)
            if EXIT_CODE in actions:
                flag = False
            print("do actions")
            do_action(actions)
        except:
            print("reset")
