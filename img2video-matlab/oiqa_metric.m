function [ score, score_index ] = oiqa_metric( im_ref, im_dis, scanpath, exploration_time, sampling_rate, s1)
%-----------------------------------------------------------------------%
% [INPUT]:
%   (1) im_ref: Reference omnidirectional image (gray scale);
%   (2) im_dis: Distorted omnidirectional image (gray scale);
%   (3) scanpath: Two-dimensional array recording sample points, 
%             [ longitude(1), longitude(2), ..., longitude(n);
%               latitude(1), latitude(2), ..., latitude(n)].
%   (4) exploration_time: Recording how much time spend to finish the exploration.
%   (5) sampling_rate: The maximum sampling rate constrained by the eye tracker 
%       (e.g. 50Hz, sampling_rate = 50).
%   (6) s1: Stride parameter to adjust sampling rate (s1>=1, type:int).
% 
%  [OUTPUT]:
%   (1) score: The final qualiy score of the input distorted image.
%   (2) score_index: The qualiy scores of samplied viewports.
%-----------------------------------------------------------------------%

% field of view
FOV = pi/3;

if (size(im_ref) ~= size(im_dis))
   score = -Inf;
   score_index = -Inf;
   return;
end

if (nargin < 2 || nargin > 6 || nargin == 3 || nargin == 4 || nargin == 5 )
    score = -Inf;
    score_index = -Inf;
    return;
end

if (nargin == 6)
    frame_num = floor(exploration_time*(sampling_rate/s1));
    scanpath_longitude = deg2rad(scanpath(1,1:s1:end));
    scanpath_latitude = deg2rad(scanpath(2,1:s1:end));
    for frame_index = 1 : frame_num
        ref_viewport = viewports_sampling(im_ref,scanpath_longitude(frame_index),...
            scanpath_latitude(frame_index),FOV);
        dis_viewport = viewports_sampling(im_dis,scanpath_longitude(frame_index),...
            scanpath_latitude(frame_index),FOV);
            score_index(frame_index) = ssim_index(ref_viewport, dis_viewport);
        imshow(dis_viewport,[]);
    end
    % K: duration of memory, 2s 
    K = 2*sampling_rate/s1;
    score = Temporal_Hysteresis(score_index,K);
end

if (nargin == 2)
    % default setting
    starting_point = [-pi/2,0,pi/2,pi];
    exploration_time = 15;
    scanpath_length = 2*pi;
    sampling_rate = 10;
    frame_num = sampling_rate*exploration_time;
    speed_gaze = scanpath_length/exploration_time;
    stride = speed_gaze/sampling_rate;
    scanpath = [scanpath_default(starting_point(1),stride);...
        scanpath_default(starting_point(2),stride);...
        scanpath_default(starting_point(3),stride);...
        scanpath_default(starting_point(4),stride)];
    
    
    for scanpath_num = 1 : 4
        j = scanpath_num * 2 -1;
        for frame_index = 1 : frame_num
            ref_viewport = viewports_sampling(im_ref,scanpath(j,frame_index),...
                scanpath(j+1,frame_index),FOV);
            dis_viewport = viewports_sampling(im_dis,scanpath(j,frame_index),...
                scanpath(j+1,frame_index),FOV);
            imshow(dis_viewport,[]);
            score_index(scanpath_num,frame_index) = ssim_index(ref_viewport, dis_viewport);
        end
    end
    % K: duration of memory, 2s 
    K = 2*sampling_rate;
    score = 0.25*(Temporal_Hysteresis(score_index(1,:),K)+Temporal_Hysteresis(score_index(2,:),K)+...
        Temporal_Hysteresis(score_index(3,:),K)+Temporal_Hysteresis(score_index(4,:),K));
end





