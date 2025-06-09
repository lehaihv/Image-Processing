% Open a dialog to select the image file
[filename, pathname] = uigetfile({'*.jpg;*.png;*.bmp', 'Image Files (*.jpg, *.png, *.bmp)'}, 'Select an Image');
if isequal(filename, 0)
    disp('User canceled the image selection.');
    return;
end

% Load the selected image
img = imread(fullfile(pathname, filename));
% Rotate the image 90 degrees anticlockwise
    img = imrotate(img, 90);

% Display the image
figure;
imshow(img);
title('Original Image');

% Set up a callback function to get coordinates on click
[x, y] = ginput(1); % Get a single point from the mouse click
fprintf('Point clicked at (X: %.2f, Y: %.2f)\n', x, y);

% Define the coordinates for the ROI [x, y, width, height]
%roi_x = round(x); % Starting x coordinate
%roi_y = round(y); % Starting y coordinate
roi_x = 200; % Starting x coordinate
roi_y = 1090; % Starting y coordinate
width = 800;      % Width of the ROI
height = 365;     % Height of the ROI

% Cut out the ROI
roi = imcrop(img, [roi_x, roi_y, width, height]);

% Display the cutout ROI
figure;
imshow(roi);
%title('Region of Interest');