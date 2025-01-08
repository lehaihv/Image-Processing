   clc; clear all; close all;

% Read standard MATLAB demo image.
rgbImage = imread("Pics/Blue_pen.jpg");

% Display the original image.
subplot(1, 3, 1);
imshow(rgbImage);
title('Original RGB Image');
% Maximize figure.
set(gcf, 'Position', get(0, 'ScreenSize'));

% Split into color bands.
redBand = rgbImage(:,:, 1);
greenBand = rgbImage(:,:, 2);
blueBand = rgbImage(:,:, 3);

% Display them.
subplot(1, 3, 2);
imshow(blueBand);
title('Blue Band 11');

% here objects which are parly blue make totaly blue
for i=1:152
    for j=1:229
        if blueBand(i,j)>200
            redBand(i,j)=0.1;
            greenBand(i,j)=0.1;
            blueBand(i,j)=200;
        end
    end
end

% here objects which are not blue to dark
for i=1:152
    for j=1:229
        if blueBand(i,j)<200
            redBand(i,j)=redBand(i,j)*0.05;
            greenBand(i,j)=greenBand(i,j)*0.05;
            blueBand(i,j)=blueBand(i,j)*0.05;
        end
    end
end

% Display them.
subplot(1, 3, 3);
im = cat(3,redBand,greenBand,blueBand);
%im = cat(1,blueBand);
imshow(im);
title('Blue Objects');