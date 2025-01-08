clc;    % Clear the command window.
close all;  % Close all figures (except those of imtool.)
clearvars;
workspace;  % Make sure the workspace panel is showing.
format long g;
format compact;
fontSize = 16;

%folder = pwd;
%baseFileName = 'Treasure_easy.jpg';
baseFileName = 'IMG_Segment_Success.JPEG';
%fullFileName = fullfile(folder, baseFileName);
rgbImage = imread('Pics/pic_7_W.jpg');
% Display the original image.
subplot(2, 3, 1);
imshow(rgbImage, []);
axis('on', 'image');
caption = sprintf('Original Color Image\n"%s"', baseFileName);
title(caption, 'FontSize', fontSize, 'Interpreter', 'None');
drawnow;
hp = impixelinfo(); % Set up status line to see values when you mouse over the image.

% Set up figure properties:
% Enlarge figure to full screen.
set(gcf, 'Units', 'Normalized', 'OuterPosition', [0 0.05 1 0.95]);
% Get rid of tool bar and pulldown menus that are along top of figure.
% set(gcf, 'Toolbar', 'none', 'Menu', 'none');
% Give a name to the title bar.
set(gcf, 'Name', 'Demo by Image Analyst', 'NumberTitle', 'Off')

% Extract the individual red, green, and blue color channels.
redChannel = rgbImage(:, :, 1);
greenChannel = rgbImage(:, :, 2);
blueChannel = rgbImage(:, :, 3);

% Get the red mask.
redMask = redChannel > 128 & greenChannel < 128 & blueChannel < 128;
subplot(2, 3, 4);
imshow(redMask);
grid on;
title('Red Mask', 'FontSize', fontSize, 'Interpreter', 'None');

% Get the white mask.
whiteMask = redChannel > 128 & greenChannel > 128 & blueChannel > 128;
% Display the image.
subplot(2, 3, 2);
imshow(whiteMask, []);
axis('on', 'image');
caption = sprintf('White Mask of \n"%s"', baseFileName);
title(caption, 'FontSize', fontSize, 'Interpreter', 'None');
drawnow;
hp = impixelinfo(); % Set up status line to see values when you mouse over the image.

% Get the yellow mask.
yellowMask = redChannel > 128 & greenChannel > 128 & blueChannel < 128;
subplot(2, 3, 3);
imshow(yellowMask);
grid on;
title('Yellow Mask', 'FontSize', fontSize, 'Interpreter', 'None');

% Get the blue mask.
blueMask = redChannel < 128 & greenChannel < 128 & blueChannel > 128;
subplot(2, 3, 5);
imshow(blueMask);
grid on;
title('Blue Mask', 'FontSize', fontSize, 'Interpreter', 'None');

% Get the bounding boxes and centroid of the red arrows
propsR = regionprops(redMask, 'BoundingBox', 'Centroid');
% Get the bounding boxes and centroid of the white arrows
propsW = regionprops(whiteMask, 'BoundingBox', 'Centroid');
% Get the bounding boxes and centroid of the yellow spots
propsY = regionprops(yellowMask, 'BoundingBox', 'Centroid');

% Figure out what direction each white arrow is pointing.
subplot(2, 3, 3);
hold on;
for k = 1 : length(propsW)
	thisBB = propsW(k).BoundingBox;
	rectangle('Position', thisBB, 'EdgeColor', 'y', 'LineWidth', 1);
	thisYellowCentroidX = propsY(k).Centroid(1);
	thisYellowCentroidY = propsY(k).Centroid(2);
	x1 = thisBB(1);
	x2 = x1 + thisBB(3);
	y1 = thisBB(2);
	y2 = y1 + thisBB(4);
	% Now find out where the yellow centroid lies within the bounding box.
end