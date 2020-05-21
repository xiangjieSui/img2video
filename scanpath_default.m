function [scanpath] = scanpath_default( starting_point, stride )

left_edge = starting_point - pi/2;
right_edge = starting_point + pi/2;

scanpath_lon = [starting_point:-stride:left_edge,...
    left_edge+stride:stride:right_edge,...
    right_edge-stride:-stride:starting_point];

scanpath_lat = zeros(size(scanpath_lon));

scanpath = [scanpath_lon; scanpath_lat];

end 

