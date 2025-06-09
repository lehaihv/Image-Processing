clc;    % Clear the command window.
close all;  % Close all figures.
clear;  % Erase all existing variables.
workspace;  % Show the workspace panel.
format long g;
format compact;

% Load the image
[baseFileName, folder] = uigetfile('*.jpg;*.png;*.bmp', 'Select an Image File');
fullImageFileName = fullfile(folder, baseFileName);

% Check to see that the image exists.
if ~exist(fullImageFileName, 'file')
    message = sprintf('This file does not exist:\n%s', fullImageFileName);
    uiwait(msgbox(message));
    return;
end

% Read in the image
rgbImage = imread(fullImageFileName);
imshow(rgbImage);
title('Original Image');

% Convert the image to grayscale
grayImage = rgb2gray(rgbImage);

% Apply a binary threshold to create a mask
binaryMask = grayImage < 100; % Adjust threshold as needed

% Use morphological operations to clean up the mask
se = strel('disk', 5); % Structuring element
cleanedMask = imopen(binaryMask, se); % Remove small objects
cleanedMask = imclose(cleanedMask, se); % Close gaps

% Invert the mask to obtain the foreground
foregroundMask = ~cleanedMask;

% Create a new image with the background removed
foregroundImage = rgbImage;
foregroundImage(repmat(~foregroundMask, [1, 1, 3])) = 0; % Set background to black

% Display the results
figure;
imshow(foregroundImage);
title('Foreground Image with Background Removed');