# Perceptual Quality Assessment of Omnidirectional Images as Moving Camera Videos [2022-TVCG]

[[Paper]](https://arxiv.org/abs/2005.10547)   [[Subjective Experimental Data]](https://drive.google.com/drive/folders/1GJ9g3G-QmZbmFbXxiBYyf28xFID3SXxW?usp=sharing)

# Highlights:
1. A principled computational framework for objective quality assessment of 360° images.
2. We propose to represent an omnidirectional image by different moving camera videos.
3. Two viewing conditions are crucial in determining the viewing behaviors of users and the perceived quality of the panorama: starting point, exploration time.

# Implementation version:
1. Matlab [oiqa_metric.m](https://github.com/xiangjieSui/img2video/blob/master/img2video-matlab/oiqa_metric.m) (recommend)  
Requirements: Matlab>=R2017a (using higher versions, e.g., MatLab R2020a, would be better.)
  
2. Pytorch [im2video.py](https://github.com/xiangjieSui/img2video/blob/master/img2video_pytorch/im2video.py)
Requirements: Python>=3.6, Pytorch>=1.0  

# Usage:
```bash
git clone https://github.com/xiangjieSui/img2video
run demo.m/main.py
```
# Citation
```
@article{sui2020omnidirectional,
  title={Perceptual Quality Assessment of Omnidirectional Images as Moving Camera Videos},
  author={Xiangjie Sui and Kede Ma and Yiru Yao and Yuming Fang},
  journal={IEEE Transactions on Visualization and Computer Graphics}, 
  volume={28},
  number={8},
  pages={3022-3034},
  year={2022}
}
```
