import numpy as np
from torch.nn import functional as F
import torch
from torch.autograd import Variable
from PIL import Image
from torchvision import transforms
from time import *
import im2video
import xlrd
import argparse


def downSample(x, y):
    assert x.shape == y.shape
    f = max(1, np.round(min(x.shape[1], x.shape[2])/1024))
    for _ in range(int(f-1)):
        padding = (x.shape[1] % 2, x.shape[2] % 2)
        x = F.max_pool2d(x, kernel_size=1, stride=2, padding=padding)
        y = F.max_pool2d(y, kernel_size=1, stride=2, padding=padding)
    return x, y


def deg2rad(x):
    return np.array(x)/180*np.pi


transform = transforms.Compose([
    # transforms.Grayscale(num_output_channels=1),
    transforms.ToTensor()
])


def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='Omnidirectional Images As Videos')
    parser.add_argument('--rimg_dir', dest='rimg_dir', help='Directory path for reference images.',
                        default='./images/ref.jpg', type=str)
    parser.add_argument('--dimg_dir', dest='dimg_dir', help='Directory path for distorted images.',
                        default='./images/dis.jpg', type=str)
    parser.add_argument('--userdata_dir', dest='data_dir', help='Path to scanpaths',
                        default='005_A_laboratory_len5_d1_0.5.csv', type=str)  # 'NAN': using default setting
    parser.add_argument('--FOV', dest='FOV', help='Field of View',
                        default=np.pi/3, type=str)
    parser.add_argument('--sampleRate', dest='sampleRate', help='Sample rate of HM data',
                        default=10, type=str)
    args = parser.parse_args()

    return args

if __name__ == '__main__':
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    args = parse_args()
    ref_path = args.rimg_dir
    dis_path = args.dimg_dir
    data_dir = args.data_dir
    FOV = args.FOV

    ref_img = Image.open(ref_path).convert("L")
    dis_img = Image.open(dis_path).convert("L")
    ref = transform(ref_img)
    ref = Variable(ref.float().to(device), requires_grad=False).squeeze(dim=1)
    dis = transform(dis_img)
    dis = Variable(dis.float().to(device), requires_grad=True).squeeze(dim=1)

    "automatic downsampling"
    ref, dis = downSample(ref, dis)

    if data_dir != 'NAN':
        "actual viewing behavior data"
        data = xlrd.open_workbook(data_dir)
        table = data.sheet_by_name('Sheet1')
        # scanpath: lon, lat (degree)
        scanpath = np.vstack((table.col_values(1), table.col_values(0)))
        size = scanpath.shape[1]  # sample size
        sampleRate = 20  # args.sampleRate
    else:
        "default viewing behavior"
        scanpath = im2video.scanpath_default(360/300)
        size = 300
        sampleRate = args.sampleRate

    begin_time = time()
    score = im2video.im2vid(ref, dis, scanpath[0], scanpath[1], FOV, size, 2*sampleRate, device)
    end_time = time()
    run_time = end_time - begin_time

    print('SSIM score: %.4f' % score)
    print('Running time: %.4f' % run_time)
