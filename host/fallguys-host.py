# -*- coding:utf-8 -*-
import mss
from util import *
from tkinter import *
import tkinter.font as tkFont
from PIL import Image, ImageDraw, ImageFont, ImageTk
import numpy as np
import cv2
from datetime import datetime
import threading
import random
import time
import pyautogui
            

class GameManager:
    def __init__(self, config):
        # roc.set_boot_state()
        self.check_interval = 1 / config['check_fps']
        self.cfg = config
        self.img_dict = {}
        self.load_img()
        self.run = True
        self.src_img = None
        self.text = "Loading……"
        self.bbox = {"pt": []}
        self.pause_game = False

        self.win_top = 0
        self.win_left = 0
        self.win_width = 1901
        self.win_height = 1119


        self.thread = threading.Thread(target=GameManager.check_loop, args=(self,))
        self.thread.start()
    
    
    def load_img(self):
        self.img_dict = {}
        for item in self.cfg['data']:
            name = item['file']
            img = cv2.imread('./img/' + name, 0)
            w = self.cfg['match_width']
            h = int(w * img.shape[0] / img.shape[1])
            img = cv2.resize(img, (w, h))
            # print(img.shape)
            self.img_dict[name] = img


    def screen_mouse_touch_area(self, rect):
        x = random.uniform(rect[0], rect[2])
        y = random.uniform(rect[1], rect[3])
        return self.screen_mouse_press_point((x, y))
    
    
    def screen_mouse_press_point(self, pt):
        px = round(self.src_img.shape[1] * pt[0])
        py = round(self.src_img.shape[0] * pt[1])
        self.bbox["pt"] = [(px, py)]
        px = round(self.win_width * pt[0] + self.win_left)
        py = round(self.win_height * pt[1] + self.win_top)
        # pyautogui.moveTo(px, py, duration = 1)
        pyautogui.click(px, py)
        return 0
        # return self._adb_send_touch(px, py)
    
    
    def check_loop(self):
        time.sleep(1)
        while self.run:
            if self.pause_game:
                continue
            if self.src_img is not None:
                src = self.src_img.copy()
                text_list = []
                
                do_action = False
                for item in self.cfg['data']:
                    name = item['file']
                    tgt = self.img_dict[name]
                    thre = item['thre']
                    action = item['action']
                    area = item['area']
                    if 'comment' in item:
                        name = item['comment']
                    if item['enable']:
                    
                        def get_patch(img, area):
                            h, w = img.shape[:2]
                            return img[int(h * area[1]): int(h * area[3]), int(w * area[0]): int(w * area[2])]
                        # print(tgt.shape, area)
                        tgt = get_patch(tgt, area)
                        # print(tgt.shape, src.shape)
                        src_c = cv2.resize(get_patch(src, area), (tgt.shape[1], tgt.shape[0]))
                        
                        # print(tgt.shape, src_c.shape)
                        # cv2.imshow(name, np.hstack([src_c, tgt]))
                        # cv2.waitKey(1)
                        res = cv2.matchTemplate(src_c, tgt, cv2.TM_CCOEFF_NORMED)
                        val = np.max(res)

                        # print("Check " + name, val, thre)
                        tmp_text = f"{name}: {val:.2f}({thre:.2f})"

                        if val > thre and not do_action:
                            # cv2.imshow(name, src_c)
                            # cv2.waitKey(10)
                            # print(name, "checked")
                            tmp_text += " √"
                            self.screen_mouse_touch_area(item['action'])
                            do_action = True
                        text_list.append(tmp_text)
                self.text = '\n'.join(text_list)
                
                if not do_action:
                    self.bbox["pt"] = []
            else:
                self.text = "Image Not Found"
                self.bbox["pt"] = []
                # print('-' * 9)
            time.sleep(self.check_interval)
            
    
    def check_img(self, win_info, src):
        self.win_top = win_info['top']
        self.win_left = win_info['left']
        self.win_width = win_info['width']
        self.win_height = win_info['height']
        self.src_img = src
        
    def set_config(self, cfg):
        self.cfg = cfg
        self.load_img()
        print("Config updated")
        
    def close(self):
        self.run = False
        self.thread.join()
        # self.con.close()
        

def main(cfg):
    # Windows
    root = Tk()
    # Create a frame
    app = Frame(root)
    app.pack()

    # Create a label in the frame
    lmain = Label(app)
    lmain.pack()
    
    ldtag1 = Label(app, font=tkFont.Font(size=15, weight=tkFont.BOLD))
    ldtag1.pack()
    ldtag = Label(app, font=tkFont.Font(size=15))
    ldtag.pack()
    
    root.title('FallGuys-Host')
    # root.geometry('1300x760')
    target_name = cfg['name']
    gm = GameManager(cfg)
    scale = cfg['scale']

    save_img = False

    def onKeyPress(event):
        nonlocal save_img
        # print(event)
        if event.keysym in 'rR':
            cfg = load_cfg()
            gm.set_config(cfg)
        elif event.keysym in 'qQ':
            root.quit()
        elif event.keysym in 'sS':
            save_img = True
        elif event.keysym in 'pP' or event.keycode == 32:
            gm.pause_game = ~gm.pause_game
            if gm.pause_game:
                gm.text = "Paused"
            else:
                gm.text = "Resuming"

    def get_stick(des, win):
        words = des.split(',')
        value = 0
        for w in words:
            if w in ['top', 'left', 'width', 'height']:
                value += win[w]
            else:
                value += int(w)
        return value

    root.bind('<KeyPress>', onKeyPress)
    
    display_interval = int(1000 / cfg['display_fps'])
    
    img_cache = None
    
    with mss.mss() as m:
        def capture_stream():
            nonlocal save_img
            nonlocal img_cache
            win_info = get_window_roi(target_name, [0, 0, 1, 1], cfg['padding'])
            if win_info['left'] < 0 and win_info['top'] < 0:
                ldtag1.configure(text='Game window not detected')
                ldtag.configure(text='')
                img_cache = None
            else:
                full_win = get_window_roi(target_name,[0, 0, 1, 1], [0, 0, 0, 0])
                if len(cfg['stick']) == 2:
                    root.geometry(f"+{get_stick(cfg['stick'][0], full_win)}+{get_stick(cfg['stick'][1], full_win)}")
                img = np.array(m.grab(win_info))

                gm.check_img(win_info, img[:, :, 1])
                """
                draw vis
                """
                for pt in gm.bbox["pt"]:
                    img = cv2.circle(img, pt, 5, (0, 0, 255), -1)

                # ldtag.configure(text='')
                ldtag1.configure(text='Running')
                ldtag.configure(text=gm.text)

                pil_img = Image.fromarray(img[:, :, :3][:, :, ::-1])
                if scale > 0:
                    pil_img = pil_img.resize((int(pil_img.size[0] * scale), int(pil_img.size[1] * scale)))
                    imgtk = ImageTk.PhotoImage(image=pil_img)
                    lmain.imgtk = imgtk
                    lmain.configure(image=imgtk)
                        
                if save_img:
                    now = datetime.now()
                    date_time = now.strftime("./%H-%M-%S")
                    Image.fromarray(img[:, :, 1]).save(date_time + ".png")
                    save_img = False
                
                    
                # update the display
                imgtk = ImageTk.PhotoImage(image=pil_img)
                lmain.imgtk = imgtk
                lmain.configure(image=imgtk)
            lmain.after(display_interval, capture_stream) 

        capture_stream()
        root.mainloop()
        
    gm.close()


def usage():
    print("Usage:\nSpace/P:Pause/Resume\nS:Save current image\nR:Reload config\nQ:Quit\n" + '-'*8)


if __name__ == '__main__':
    usage()
    cfg = load_cfg()
    main(cfg)