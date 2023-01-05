import torch
import numpy as np
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as T
import os
from util import *


class SequentialBuffer:
    """Buffer to store environment transitions."""
    def __init__(self, capacity, batch_size, device):
        self.cfg = load_cfg('env.json')
        self.obs_stack = self.cfg['obs_stack']
        self.batch_size = batch_size
        self.device = device
        self.capacity = capacity
        self.obs_shape = self.cfg['obs_shape']
        self.obs_target = self.cfg['obs_target'] # 3 * H * W <= single frame
        
        self.obs_aug = torch.nn.Sequential(
            T.RandomCrop(self.obs_target)
        )

        action_shape = self.cfg['action_shape']
        # the proprioceptive obs is stored as float32, pixels obs as uint8
        self.obses = np.empty((capacity + self.obs_stack, 3, *self.obs_shape), dtype=np.uint8) # current state and next state, # capacity + stacks, 3, H, W
        self.actions = np.empty((capacity, action_shape), dtype=np.float32)
        self.rewards = np.empty((capacity, 1), dtype=np.float32)
        self.not_dones = np.empty((capacity, 1), dtype=np.uint8)

        self.idx = -1


    def add(self, obs, action, reward, next_obs, done):
        assert np.all(obs[1:] == next_obs[:-1])
        if self.idx == -1:
            np.copyto(self.obses[:self.obs_stack], obs)
            np.copyto(self.obses[self.obs_stack], next_obs[-1])
            self.idx = 0
        else:
            if self.capacity == self.idx + 1:
                # buffer is full
                self.obses[:-1] = self.obses[1:]
                self.actions[:-1] = self.actions[1:]
                self.rewards[:-1] = self.rewards[1:]
                self.not_dones[:-1] = self.not_dones[1:]
            else:
                self.idx += 1
            np.copyto(self.obses[self.obs_stack + self.idx], next_obs[-1])
        
        np.copyto(self.actions[self.idx], action)
        np.copyto(self.rewards[self.idx], reward)
        np.copyto(self.not_dones[self.idx], not done)

    def sample(self):
        idxes = np.random.randint(0, self.idx + 1, size=self.batch_size)
        obses = np.stack([self.obses[idx:idx + self.obs_stack] for idx in idxes], axis=0).reshape(self.batch_size, self.obs_stack * 3, *self.obs_shape) # B, Stack, 3, H, W
        next_obses = np.stack([self.obses[idx + 1:idx + self.obs_stack + 1] for idx in idxes], axis=0).reshape(self.batch_size, self.obs_stack * 3, *self.obs_shape)
        actions = self.actions[idxes]
        rewards = self.rewards[idxes]
        not_dones = self.not_dones[idxes].astype(np.float32)

        obses = torch.as_tensor(obses, device=self.device) # B, Stack*3, H, W
        next_obses = torch.as_tensor(next_obses, device=self.device) # B, Stack*3, H, W

        obses1 = self.obs_aug(obses)
        obses2 = self.obs_aug(obses)
        next_obses1 = self.obs_aug(next_obses)

        actions = torch.as_tensor(actions, device=self.device)
        rewards = torch.as_tensor(rewards, device=self.device)
        not_dones = torch.as_tensor(not_dones, device=self.device)

        return obses, actions, rewards, next_obses, not_dones, obses1, obses2, next_obses1, idxes

    def __len__(self):
        return self.idx + 1


if __name__ == '__main__':
    srb = SequentialBuffer(15, 2, torch.device('cpu'))
    np.random.seed(42)
    action = np.random.rand(srb.cfg['action_shape'])
    reward = 0
    done = False

    samples = 9
    src = np.random.randint(0, 256, (srb.obs_stack + samples, 3 ,*srb.obs_shape), dtype=np.uint8)

    for i in range(samples):
        obs = src[i: i + srb.obs_stack]
        next_obs = src[i + 1: i + srb.obs_stack + 1]
        srb.add(obs, action ,reward, next_obs, done)

    # assert np.any(srb.obses[:srb.obs_stack + srb.idx + 1]==obses)

    for _ in range(10):
        obses, actions, rewards, next_obses, not_dones, obses1, obses2, next_obses1, idxes = srb.sample()
        print(obses.shape, next_obses.shape, obses1.shape, obses2.shape, next_obses1.shape, idxes)
        assert torch.any(obses[:, 3:]==next_obses[:, :-3])


    
    


