import vgamepad as vg
import numpy as np
import win32com
import win32api

class VController:
    def __init__(self):
        self.gamepad = vg.VX360Gamepad()
        self.shell = win32com.client.Dispatch("WScript.Shell")

    def press_enter(self):
        self.shell.SendKeys("{ENTER}")
        win32api.Sleep(2500)

    def parse_action(self, action):
        assert len(action) == 7
        action = np.clip(action, -1, 1)
        self.gamepad.left_joystick_float(x_value_float=action[0], y_value_float=action[1]) # movement
        self.gamepad.right_joystick_float(x_value_float=action[2], y_value_float=action[3]) # rotate camera
        # jump
        if action[4] > 0:
            self.gamepad.press(vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        else:
            self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        # dive
        if action[5] > 0:
            self.gamepad.press(vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
        else:
            self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
        # grab
        self.gamepad.right_trigger(value=255 if action[6] > 0 else 0)
        self.gamepad.update()
        print(action)


    def reset(self):
        self.gamepad.reset()
        self.gamepad.update()

    def __del__(self, **argv):
        self.reset()


def parse_data(data):
    return np.frombuffer(data, dtype=np.float32)

if __name__ == '__main__':
    import socket

    UDP_IP = ""
    UDP_PORT = 5005

    sock = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP
    sock.settimeout(0.5)
    sock.bind((UDP_IP, UDP_PORT))

    v = VController()

    while True:
        try:
            data, addr = sock.recvfrom(28) # 4*7 bytes
            action = parse_data(data)
            v.parse_action(action)
        except KeyboardInterrupt:
            break
        except socket.timeout:
            v.reset()

    print('Done')
