import torch
import viewportSampling as V
from iqa_metrics import SSIM, DISTS, NLPD, VIF
import numpy as np
import cv2
import matplotlib
import matplotlib.pyplot as plt

pi = np.pi



def im2vid(ref, dis, lon, lat, FOV, size, K, device):
    """K: duration of memory (2 seconds)"""
    model = SSIM.SSIM(channels=1).to(device)
    score = np.zeros((1, size))
    lon = np.deg2rad(lon)
    lat = np.deg2rad(lat)
    for frame in range(size):
        R = V.viewportSampling(ref, dis, lon[frame], lat[frame], FOV)
        # refViewport, disViewport = R.sampling()
        # plt.imshow(disViewport, cmap="gray")
        plt.pause(1)
        refViewport = torch.from_numpy(refViewport).unsqueeze(0).unsqueeze(0).type(torch.float64)
        disViewport = torch.from_numpy(disViewport).unsqueeze(0).unsqueeze(0).type(torch.float64)
        score[0, frame] = model(disViewport, refViewport, as_loss=False)
        print('score: %.4f' % score[0, frame].item())
    final_score = Temporal_Hysteresis(score, K)
    return final_score


def Temporal_Hysteresis(score_pre, K):
    len = int(score_pre.shape[1])
    memory_score = np.zeros((1, len))
    curr_score = np.zeros((1, len))
    score_index = np.zeros((1, len))
    alpha = 0.8
    for i in range(len - 1):
        t_min = max(0, i - K)
        t_max = min(i + K, len)
        if i == 0:
            memory_score[0, i] = score_pre[0, 0]
        else:
            memory_score[0, i] = min(memory_score[0, t_min: i])
        reorder = np.sort(score_pre[0, i: t_max]).reshape(-1, 1)
        L = reorder.shape[0]
        sigma = (2 * L - 1) / 12
        gausFilter = cv2.getGaussianKernel(2 * L, sigma)
        half_gausFilter = 2 * gausFilter[L - 1: -1]
        curr_score[0, i] = sum(reorder * half_gausFilter) / sum(half_gausFilter)
        score_index[0, i] = alpha * curr_score[0, i] + (1 - alpha) * memory_score[0, i]
    fin_score = np.average(score_index)
    return fin_score


def scanpath_default(stride):
    starting_point = [-90, 0, 90, 180]
    scanpath = np.hstack((movement_pattern(starting_point[0], stride),
                          movement_pattern(starting_point[1], stride),
                          movement_pattern(starting_point[2], stride),
                          movement_pattern(starting_point[3], stride)))
    return scanpath


def movement_pattern(starting_point, stride):
    left_edge = starting_point - 90
    right_edge = starting_point + 90

    scanpath_lon = np.hstack((np.arange(starting_point, left_edge, -stride).reshape(1, -1),
                              np.arange(left_edge, right_edge, stride).reshape(1, -1),
                              np.arange(right_edge, starting_point, -stride).reshape(1, -1)))

    scanpath_lat = np.zeros(scanpath_lon.shape)
    scanpath = np.vstack((scanpath_lon, scanpath_lat))

    return scanpath
