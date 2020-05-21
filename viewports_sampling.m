function [ viewport ] = viewports_sampling( im, lon, lat, FOV )

[hight,width]=size(im);

F_h = FOV;
F_v = FOV;

viewport_size = floor(FOV/(2*pi)*width);

viewport = zeros(viewport_size,viewport_size);

% rotation matrix R
R = [cos(lon+pi/2), -sin(lon+pi/2)*sin(lat), sin(lon+pi/2)*cos(lat);...
    0, cos(lat), sin(lat);...
    -sin(lon+pi/2), -cos(lon+pi/2)*sin(lat), cos(lon+pi/2)*cos(lat)];

for i = 1 : viewport_size
    for j = 1 : viewport_size
        u = (j+0.5)*2*tan(F_h/2)/viewport_size;
        v = (i+0.5)*2*tan(F_v/2)/viewport_size;
        
        x1 = u - tan(F_h/2);
        y1 = -v + tan(F_v/2);
        z1 = 1.0;
        r = sqrt(x1^2 + y1^2 + z1^2);
        
        sphere_coords = [x1/r; y1/r; 1.0/r];
        rotated_sphere_coords = R*sphere_coords;
        
        x = rotated_sphere_coords(1);
        y = rotated_sphere_coords(2);
        z = rotated_sphere_coords(3);
        
        phi = acos(y);
        theta = atan2(x,z);
        
        x_out = width * theta / (2*pi);
        y_out = hight * phi / pi;
        
        % bicubic interpolation
        y_f = floor(y_out);
        x_f = floor(x_out);
        p = y_out - y_f;
        q = x_out - x_f;
        if y_f==0
            y_f=1;
            p=0;
        end
        if y_f >= hight
            y_f = hight;
            viewport(i,j) = (1-q)*im(y_f,mod(x_f-1,width)+1)+...
                q*im(y_f,mod(x_f,width)+1);
        else
            viewport(i,j) = (1-p)*(1-q)*im(y_f,mod(x_f-1,width)+1)+...
                (1-p)*q*im(y_f,mod(x_f,width)+1)+...
                p*(1-q)*im(y_f+1,mod(x_f-1,width)+1)+...
                p*q*im(y_f+1,mod(x_f,width)+1);  
        end
    end
end


