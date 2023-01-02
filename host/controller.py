import vgamepad as vg
import numpy as np
import time
import win32com.client
import win32api

class VController:
    def __init__(self):
        self.gamepad = vg.VX360Gamepad()
        self.shell = win32com.client.Dispatch("WScript.Shell")

    def press_enter(self):
        self.shell.SendKeys("{ENTER}")
        win32api.Sleep(2500)

    def jump(self):
        print("jump...")
        self.press(vg.XUSB_BUTTON.XUSB_GAMEPAD_A)

    def dive(self):
        print("dive...")
        self.press(vg.XUSB_BUTTON.XUSB_GAMEPAD_X)

    def grab(self):
        print("grab...")
        self.press_right_trigger(slp=1.0)

    def up(self):
        print("up...")
        self.gamepad.left_joystick_float(x_value_float=0, y_value_float=1.0)
        self.gamepad.update()
        time.sleep(1.0)
        self.gamepad.left_joystick_float(x_value_float=0.0, y_value_float=0.0)
        self.gamepad.update()

    def down(self):
        print("down...")
        self.gamepad.left_joystick_float(x_value_float=0, y_value_float=-1.0)
        self.gamepad.update()
        time.sleep(1.0)
        self.gamepad.left_joystick_float(x_value_float=0.0, y_value_float=0.0)
        self.gamepad.update()

    def left(self):
        print("left...")
        self.gamepad.left_joystick_float(x_value_float=-1.0, y_value_float=0)
        self.gamepad.update()
        time.sleep(1.0)
        self.gamepad.left_joystick_float(x_value_float=0.0, y_value_float=0.0)
        self.gamepad.update()

    def right(self):
        print("right...")
        self.gamepad.left_joystick_float(x_value_float=1.0, y_value_float=0)
        self.gamepad.update()
        time.sleep(1.0)
        self.gamepad.left_joystick_float(x_value_float=0.0, y_value_float=0.0)
        self.gamepad.update()

    def camera_center(self):
        print("recenter camera...")
        self.press(vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB)
    
    def rotate(self, x_value=1.0, y_value=1.0, slp=1.0):
        print("rotate...")
        self.gamepad.right_joystick_float(x_value_float=x_value, y_value_float=y_value)
        self.gamepad.update()
        time.sleep(slp)
        self.gamepad.right_joystick_float(x_value_float=0.0, y_value_float=0.0)
        self.gamepad.update()
    
    def mock1(self):
        print("mock1...")
        self.press(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP, slp=1.0)

    def mock2(self):
        print("mock2...")
        self.press(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN, slp=1.0)

    def mock3(self):
        print("mock3...")
        self.press(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT, slp=1.0)

    def mock4(self):
        print("mock4...")
        self.press(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT, slp=1.0)

    def press(self, btn, slp=0.05):
        self.gamepad.press_button(button=btn)
        self.gamepad.update()
        time.sleep(slp)
        self.gamepad.release_button(button=btn)
        self.gamepad.update()

    def press_right_trigger(self, value=255, slp=0.05):
        self.gamepad.right_trigger(value=value)
        self.gamepad.update()
        time.sleep(slp)
        self.gamepad.right_trigger(value=0)
        self.gamepad.update()
        
    def press_dpad_down(self):
        self.press(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)

    def parse_action(self, action):
        action = np.clip(action, -1, 1)
        self.gamepad.right_trigger(value=255 if action[-1] > 0 else 0)
        self.gamepad.right_joystick_float(x_value_float=action[0], y_value_float=action[1])
        self.gamepad.update()
        time.sleep(0.05)
        self.gamepad.right_trigger(value=0) # release trigger
        self.gamepad.update()

    def reset(self):
        self.gamepad.reset()
        self.gamepad.update()

    def __del__(self, **argv):
        self.reset()


if __name__ == '__main__':
    con = VController()

