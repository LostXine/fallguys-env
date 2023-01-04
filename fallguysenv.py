import socket
import numpy as np
import cv2 
import time


class FallGuysEnv:
    def __init__(self, udp_target=('127.0.0.1', 5005), camera_idx=0, camera_size=(1920,1080)) -> None:
        self.target = udp_target
        self.socket = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP
        self.socket.settimeout(0.5)

        self.cam = cv2.VideoCapture(camera_idx)
        self.cam.set(3, camera_size[0])
        self.cam.set(4, camera_size[1])


    def reset(self):
        ret, frame = self.cam.read()
        while ret:
            try:
                ret, frame = self.cam.read()
                cv2.imshow('Frame', frame)
                cv2.waitKey(5)
            except KeyboardInterrupt:
                break

    def __del__(self):
        cv2.destroyAllWindows()
        if self.cam is not None:
            self.cam.release()

    def step(self, action):
        self.socket.sendto(action.astype(np.float32).tobytes(), self.target)
        



if __name__ == '__main__':
    env = FallGuysEnv()
    env.reset()