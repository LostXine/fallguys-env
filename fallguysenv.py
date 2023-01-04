import socket
import numpy as np
import cv2 
from util import crop_image_by_pts, load_img, load_cfg, unify_size


class FallGuysEnv:
    def __init__(self, udp_target=('127.0.0.1', 5005), camera_idx=0) -> None:
        self.cfg = load_cfg('env.json')
        camera_info = self.cfg['camera_info']

        self.obs_source = self.cfg['obs_source']
        self.obs_shape = self.cfg['obs_shape']
        self.obs_stack = self.cfg['obs_stack']

        # start camera for state
        self.cam = cv2.VideoCapture(camera_idx)
        self.cam.set(6, cv2.VideoWriter_fourcc(	'M', 'J', 'P', 'G'	))
        self.cam.set(3, camera_info[0]) # width
        self.cam.set(4, camera_info[1]) # height
        self.cam.set(5, camera_info[2]) # fps

        # init for template matching
        self.img_dict = {}
        for item in self.cfg['data']:
            name = item['file']
            img = load_img(name, self.cfg['camera_info'][0], mode=cv2.IMREAD_COLOR)[:, :, 1]
            img = cv2.resize(crop_image_by_pts(img, self.obs_source), self.obs_shape)
            # print(img.shape)
            self.img_dict[item['slot']] = img

        # init socket for control
        self.target = udp_target
        self.socket = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP
        self.socket.settimeout(0.5)

    def _make_state(self, slot=[]):
        frames = [cv2.resize(crop_image_by_pts(self.cam.read()[1], self.obs_source), self.obs_shape) for _ in range(self.obs_stack)]
        detect = self._match_image(frames[0], slot) # check states if necessary
        stack = np.concatenate(frames, axis=-1) # H, W, C*stack
        
        return np.transpose(stack, (2, 0, 1)), detect # C*stack, H, W


    def _match_image(self, src, slot):
        detect = {}
        for item in self.cfg['data']:
            if item['slot'] not in slot:
                continue
            name = item['slot']
            tgt = self.img_dict[name]
            tgt = crop_image_by_pts(tgt, item['area'])
            src = crop_image_by_pts(src[:, :, 1], item['search_area'])
            # print(tgt.shape, src.shape)
            res = cv2.matchTemplate(src, tgt, cv2.TM_CCOEFF_NORMED)
            detect[name] = np.max(res) > item['thre']
        print(detect)
        return detect

    def reset(self):
        _, frame = self.cam.read()
        while True:
            try:
                state, res = self._make_state(['on_reset'])
                if res['on_reset']:
                    return state
                # cv2.imshow('Frame', frame)
                # cv2.waitKey(5)
            except KeyboardInterrupt:
                self.cam.release()
                exit(0)


    def __del__(self):
        cv2.destroyAllWindows()
        if self.cam is not None:
            self.cam.release()

    def step(self, action):
        self.socket.sendto(action.astype(np.float32).tobytes(), self.target)
        reward = self.cfg['reward_time']
        # for _ in range(self.cfg['action_delay']):
        #    self.cam.read()
        state, detect = self._make_state(['qualified', 'eliminated'])

        done = detect['qualified'] | detect['eliminated']

        if detect['qualified']:
            reward = self.cfg['reward_win']
        elif detect['eliminated']:
            reward = self.cfg['reward_loss']

        return state, reward, done

        



if __name__ == '__main__':
    # Camera 0: 192.168.0.42
    env = FallGuysEnv()
    env.reset()
    done = False
    while not done:
        _, reward, done = env.step(np.random.rand(7))
    print(f"Game finished, reward: {reward}")
