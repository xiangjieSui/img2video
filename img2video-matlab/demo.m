clc
clear all
close all

% load reference and distorted images
im_ref = double(rgb2gray(imread('ref.jpg')));
im_dis = double(rgb2gray(imread('dis.jpg')));
[h1,w1] = size(im_ref);
[h2,w2] = size(im_dis);
if (h1 ~= h2 || w1 ~= w2)
    im_dis = imresize(im_dis,[h1,w1],'bicubic');
end
[data,~] = xlsread('005_A_laboratory_len5_d1_0.5.csv'); 
hm = cat(2, data(:,2),data(:,1));

% autodownsampling
im_ref = downsampling(im_ref);
im_dis = downsampling(im_dis);

tic
[score, score_index] = oiqa_metric(im_ref,im_dis,hm',15, 20, 1)
% [score,~] = ssim_index(im_ref,im_dis)

toc
 


