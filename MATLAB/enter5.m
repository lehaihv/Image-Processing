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
% Rotate the image 90 degrees anticlockwise
rgbImage = imrotate(rgbImage, 90);
[rows, columns, numberOfColorChannels] = size(rgbImage);
disp(rows);
disp(columns);

% Compute HSV image.
hsvImage = rgb2hsv(rgbImage);
hImage1 = hsvImage(:, :, 1);
sImage1 = hsvImage(:, :, 2);
vImage1 = hsvImage(:, :, 3);

% Set thresholds for detecting this shade of blue.
hueTL1 = 0.5; % Lower threshold for vibrant blue
hueTH1 = 0.75; % Upper threshold for vibrant blue
saturationTL1 = 0.5; saturationTH1 = 1;  
valueTL1 = 0.2; valueTH1 = 1; 

% Create binary mask for blue objects.
hueMaskBlue = (hImage1 >= hueTL1 & hImage1 <= hueTH1);
saturationMaskBlue = (sImage1 >= saturationTL1 & sImage1 <= saturationTH1);
valueMaskBlue = (vImage1 >= valueTL1 & vImage1 <= valueTH1);
binaryImage = hueMaskBlue & saturationMaskBlue & valueMaskBlue;

% Remove small objects from the binary image.
binaryImage = bwareaopen(binaryImage, 1000); 

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

% Prepare to store centroid coordinates
centroids = cat(1, props.Centroid);

% Create a copy of the original image for displaying results
RGB_with_boxes = rgbImage;

% Draw bounding boxes and annotate with average intensity
for k = 1:num_objs
    thisBoundingBox = props(k).BoundingBox;
    RGB_with_boxes = insertShape(RGB_with_boxes, 'Rectangle', thisBoundingBox, 'Color', 'red', 'LineWidth', 6);
    
    % Ensure centroids are within image bounds
    x = round(centroids(k, 1));
    y = round(centroids(k, 2));
    
    % Check if the pixel coordinates are valid
    if x > 0 && x <= columns && y > 0 && y <= rows
        pixelValues = impixel(rgbImage, x, y);
        
        if numel(pixelValues) == 3
            avgIntensity = mean(pixelValues);  % Calculate average intensity
            avgIntensityText = sprintf('Avg Intensity: %.1f', round(avgIntensity));
        else
            avgIntensityText = 'Avg Intensity: [N/A]';
        end
    else
        avgIntensityText = 'Avg Intensity: [N/A]';
    end
    
    % Annotate the average intensity at the centroid
    % Annotate the average intensity at the top left of the bounding box
    textPosition = [thisBoundingBox(1), thisBoundingBox(2)]; % Top left corner
    RGB_with_boxes = insertText(RGB_with_boxes, textPosition, avgIntensityText, ...
        'FontSize', 10, 'BoxColor', 'yellow', 'TextColor', 'black', 'AnchorPoint', 'LeftTop');
end

% Display the image with bounding boxes and average intensity annotations
figure;
imshow(RGB_with_boxes);
title("Detected Blue Objects with Average Intensity");