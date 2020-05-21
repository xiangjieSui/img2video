clc
clear all
close all

% load reference and distorted images
im_ref = double(rgb2gray(imread('reference_image.png')));
im_dis = double(rgb2gray(imread('distorted_image.png')));
[h1,w1] = size(im_ref);
[h2,w2] = size(im_dis);
if (h1 ~= h2 || w1 ~= w2)
    im_dis = imresize(im_dis,[h1,w1],'bicubic');
end

% autodownsampling
im_ref = downsampling(im_ref);
im_dis = downsampling(im_dis);

tic
[score,~] = oiqa_metric(im_ref,im_dis)
toc
 


