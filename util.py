# -*- coding:utf-8 -*-
import json
import cv2


def load_cfg(name='config.json'):
    with open(name, 'r', encoding="utf-8") as f:
        content = f.read()
        cfg = json.loads(content)
        return cfg

def load_img(name, width, mode=0):
    img = cv2.imread('./img/' + name, mode)
    if img.shape[1] == width:
        return img
    w = width
    h = int(w * img.shape[0] / img.shape[1])
    img = cv2.resize(img, (w, h))
    return img


def get_possible_window_name(name="FallGuys_client"):
    import win32gui
    print("Search for the window whose name contains", name)
    possible_hwnd = None
    def winEnumHandler(hwnd, ctx):
        nonlocal possible_hwnd
        if win32gui.IsWindowVisible(hwnd):
            win_name = win32gui.GetWindowText(hwnd)
            if name in win_name:
                possible_hwnd = hwnd
    win32gui.EnumWindows(winEnumHandler, None)
    if possible_hwnd is None:
        print("Window not found")
    print('-' * 8)
    return possible_hwnd
    
    
def crop_image_by_pts(img, pts):
    h, w = img.shape[:2]
    h1, h2 = int(pts[1] * h), int(pts[3] * h)
    w1, w2 = int(pts[0] * w), int(pts[2] * w)
    return img[h1:h2, w1:w2]


def unify_size(tgt, tgt_area, src_area):
    return (int(tgt.shape[1] * (src_area[2] - src_area[0]) / (tgt_area[2] - tgt_area[0])),
    int(tgt.shape[0] * (src_area[3] - src_area[1]) / (tgt_area[3] - tgt_area[1])))


def get_window_roi(name, pos, padding):
    import win32gui
    x1, y1, x2, y2 = pos
    ptop, pdown, pleft, pright = padding
    handle = win32gui.FindWindow(0, name)
    # print(handle)
    # handle = 0xd0ea6
    if not handle:
        print("Can't not find " + name)
        handle = get_possible_window_name()

    if handle is None:
        return {'top': -1, 'left': -1, 'width': 100, 'height': 100}
        
    window_rect = win32gui.GetWindowRect(handle)
    
    w = window_rect[2] - window_rect[0] - pleft - pright
    h = window_rect[3] - window_rect[1] - ptop - pdown
    
    window_dict = {
        'left': window_rect[0] + int(x1 * w) + pleft,
        'top': window_rect[1] + int(y1 * h) + ptop,
        'width': int((x2 - x1) * w),
        'height': int((y2 - y1) * h)
    }
    
    return window_dict
    
    
if __name__ == '__main__':
    pass
    
    