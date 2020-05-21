function [ image ] = downsampling( image )
[M,N] = size(image);
f = max(1,round(min(M,N)/1024));
%downsampling by f
%use a simple low-pass filter
if(f>1)
    lpf = ones(f,f);
    lpf = lpf/sum(lpf(:));
    image = imfilter(image,lpf,'symmetric','same');
    image = image(1:f:end,1:f:end);
end
end

