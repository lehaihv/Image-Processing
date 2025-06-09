clc;    % Clear the command window.
close all;  % Close all figures (except those of imtool.)
clear;  % Erase all existing variables.
workspace;  % Make sure the workspace panel is showing.
format long g;
format compact;
fontSize = 25;

% Browse for the image file. 
[baseFileName, folder] = uigetfile('*.jpg', 'Specify an image file'); 
fullImageFileName = fullfile(folder, baseFileName); 

% Check to see that the image exists.
if ~exist(fullImageFileName, 'file')
    message = sprintf('This file does not exist:\n%s', fullImageFileName);
    uiwait(msgbox(message));
    return;
end

% Read in the image.
rgbImage = imread(fullImageFileName);
[rows, columns, numberOfColorChannels] = size(rgbImage);
disp(rows);
disp(columns);

% Compute HSV image.
hsvImage = rgb2hsv(rgbImage);
hImage1 = hsvImage(:, :, 1);
sImage1 = hsvImage(:, :, 2);
vImage1 = hsvImage(:, :, 3);

hueTL1 = 0.1; 
hueTH1 = 0.6; 
saturationTL1 = 0.3; saturationTH1 = 1;  
valueTL1 = 0.3; valueTH1 = 1; 

hueMaskBlue = (hImage1 >= hueTL1 & hImage1 <= hueTH1);
saturationMaskBlue = (sImage1 >= saturationTL1 & sImage1 <= saturationTH1);
valueMaskBlue = (vImage1 >= valueTL1 & vImage1 <= valueTH1);
binaryImage = hueMaskBlue & saturationMaskBlue & valueMaskBlue;

binaryImage = bwareaopen(binaryImage, 100); 

% Get properties of detected objects.
props = regionprops(binaryImage, 'Area', 'Centroid', 'BoundingBox');
num_objs = size(props, 1);
disp("No of Objects");
disp(num_objs);

if num_objs < 1
    message = sprintf('There are no blue objects in the image \n%s', fullImageFileName);
    uiwait(msgbox(message));
    return;
end

% Prepare to store centroid coordinates and area values.
centroids = cat(1, props.Centroid);
areas = [props.Area]; % Extract areas

% Create a copy of the original image for displaying results
RGB_with_boxes = rgbImage;

% Draw bounding boxes and annotate with area, intensity, and dimensions
for k = 1:num_objs
    thisBoundingBox = props(k).BoundingBox;
    RGB_with_boxes = insertShape(RGB_with_boxes, 'Rectangle', thisBoundingBox, 'Color', 'red', 'LineWidth', 6);
    
    % Calculate dimensions
    width = thisBoundingBox(3);
    height = thisBoundingBox(4);
    
    % Ensure centroids are within image bounds
    x = round(centroids(k, 1));
    y = round(centroids(k, 2));
    
    % Check if the pixel coordinates are valid
    if x > 0 && x <= columns && y > 0 && y <= rows
        pixelValues = impixel(rgbImage, x, y);
        
        if numel(pixelValues) == 3
            avgIntensityText = sprintf('Area: %.2f\nIntensity: [%d, %d, %d]\nDimensions: [%.1f, %.1f]', ...
                areas(k), round(pixelValues(1)), round(pixelValues(2)), round(pixelValues(3)), width, height);
        else
            avgIntensityText = sprintf('Area: %.2f\nIntensity: [N/A]\nDimensions: [%.1f, %.1f]', areas(k), width, height);
        end
    else
        avgIntensityText = sprintf('Area: %.2f\nIntensity: [N/A]\nDimensions: [%.1f, %.1f]', areas(k), width, height);
    end
end

% Display the image with bounding boxes and area/intensity/dimensions annotations
figure;
imshow(RGB_with_boxes);
title("Detected Blue Objects"); % with Bounding Boxes, Areas, Intensities, and Dimensions");