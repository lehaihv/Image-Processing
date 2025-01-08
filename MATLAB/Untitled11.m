clc;    % Clear the command window.
close all;  % Close all figures (except those of imtool.)
clear;  % Erase all existing variables. Or clearvars if you want.
workspace;  % Make sure the workspace panel is showing.
format long g;
format compact;
fontSize = 25;

%===============================================================================
% Get the name of the image the user wants to use.
baseFileName = 'Pics/pic_9.jpg'; %pic_8.jpgpic_7_W
folder = fileparts(which(baseFileName)); % Determine where demo folder is (works with all versions).
fullFileName = fullfile(folder, baseFileName);

% Check if file exists.
if ~exist(fullFileName, 'file')
  % The file doesn't exist -- didn't find it there in that folder.
  % Check the entire search path (other folders) for the file by stripping off the folder.
  fullFileNameOnSearchPath = baseFileName; % No path this time.
  if ~exist(fullFileNameOnSearchPath, 'file')
    % Still didn't find it.  Alert user.
    errorMessage = sprintf('Error: %s does not exist in the search path folders.', fullFileName);
    uiwait(warndlg(errorMessage));
    return;
  end
end

%===============================================================================
% Read in demo image.
rgbImage = imread(fullFileName);
% Get the dimensions of the image.
[rows, columns, numberOfColorChannels] = size(rgbImage);
disp(rows);
disp(columns);
% Display the original image.
%subplot(2, 2, 1);
%imshow(rgbImage, []);
% axis on;
% caption = sprintf('Original Color Image, %s', baseFileName);
% title(caption, 'FontSize', fontSize, 'Interpreter', 'None');
%hp = impixelinfo();

% Set up figure properties:
% Enlarge figure to full screen.
% set(gcf, 'Units', 'Normalized', 'OuterPosition', [0 0.05 1 0.95]);
% % Get rid of tool bar and pulldown menus that are along top of figure.
% % set(gcf, 'Toolbar', 'none', 'Menu', 'none');
% % Give a name to the title bar.
% set(gcf, 'Name', 'Demo by ImageAnalyst', 'NumberTitle', 'Off')
% 
% drawnow;
%hp = impixelinfo(); % Set up status line to see values when you mouse over the image.

% Compute HSV image.
hsvImage = rgb2hsv(rgbImage);
% hImage1 = hsvImage(:, :, 1);
% sImage1 = hsvImage(:, :, 2);
% vImage1 = hsvImage(:, :, 3);
hImage1 = hsvImage(:, :, 1);
sImage1 = hsvImage(:, :, 2);
vImage1 = hsvImage(:, :, 3);
% Display the image.
% subplot(2, 2, 2);
% imshow(sImage1, []);
% axis on;
% caption = sprintf('Saturation Image');
% title(caption, 'FontSize', fontSize, 'Interpreter', 'None');
% %hp = impixelinfo();
% drawnow;

% Create the binary image.
%binaryImage = saturationImage > 0.2 & valueImage > 0.1;
hueTL1 = 0.4; hueTH1 = 0.69; hueH1 = 1;
saturationTL1 = 0.2; saturationTH1 = 1;
valueTL1 = 0.01; valueTH1 = 1;

hueMaskred1 = (hImage1 > hueTL1) & (hImage1 <= hueTH1)|(hImage1 >= hueH1);
saturationMaskred1 = (sImage1 >= saturationTL1) & (sImage1 <= saturationTH1);
valueMaskred1 = (vImage1 >= valueTL1) & (vImage1 <= valueTH1);
binaryImage = hueMaskred1 & saturationMaskred1 & valueMaskred1;

% hueTL1 = 0.69; hueTH1 = 1;
% saturationTL1 = 0.2; saturationTH1 = 1;
% valueTL1 = 0.01; valueTH1 = 1;

% Display the image.
% subplot(2, 2, 3);
% imshow(binaryImage, []);
% axis on;
% caption = sprintf('Binary Image');
% title(caption, 'FontSize', fontSize, 'Interpreter', 'None');
% %hp = impixelinfo();
% drawnow;

% Take largest blobs only
% binaryImage = bwareaopen(binaryImage, 20);
% % Fill them to get rid of noise.
% binaryImage = imfill(binaryImage, 'holes');
% % Display the mask image.
% % subplot(2, 2, 4);
% % imshow(binaryImage, []);
% axis on;
% caption = sprintf('Binary Image Fill Holes');
% title(caption, 'FontSize', fontSize, 'Interpreter', 'None');
% %hp = impixelinfo();
% %drawnow;

props = regionprops(binaryImage, 'Area');
allAreas = sort([props.Area], 'descend')

props1 = regionprops(binaryImage, 'Centroid');
% allAreas1 = sort([props1.Centroid], 'descend')
centroids = cat(1,props1.Centroid);
% ttx_infor = centroids(1,1);
% disp(centroids);
% disp(centroids(1,1));
% disp(centroids(1,2));
% disp(centroids(2,1));
% disp(centroids(2,2));
disp(size(props,1)); % size of 1st dimension of props = number of object
%disp(props(1,1));
num_objs = size(props,1);
disp(num_objs);
%disp(impixel(rgbImage,centroids(1,1),centroids(1,2)));
%disp(impixel(rgbImage,centroids(2,1),centroids(2,2)));

%
% x1 = centroids(1,1);
% y1 = centroids(1,2);
% x2 = centroids(2,1);
% y2 = centroids(2,2);
position =  [centroids(1,1) centroids(1,2); centroids(2,1) centroids(2,2)];
% box_color = ["red","green"];
% text_str = [mat2str(impixel(rgbImage,centroids(1,1),centroids(1,2))), mat2str(impixel(rgbImage,centroids(2,1),centroids(2,2)))];
% v1 = mat2str(impixel(rgbImage,centroids(1,1),centroids(1,2)));
% v2 = mat2str(impixel(rgbImage,centroids(2,1),centroids(2,2)));
v1 = impixel(rgbImage,centroids(1,1),centroids(1,2));
v2 = impixel(rgbImage,centroids(2,1),centroids(2,2));
disp(v1)

%RGB = insertText(rgbImage,position,text_str,FontSize=18,BoxOpacity=0.4,TextColor="white");
%disp(extractBetween(v1,2,6));
% disp(v1(1,1));
% disp(v1(1,2));
% disp(v1(1,3));
txt10 = string(v1(1,1)) + " " + string(v1(1,2)) + " " + string(v1(1,3));
txt11 = string(v2(1,1)) + " " + string(v2(1,2)) + " " + string(v2(1,3));
%disp(txt10);
%disp(string(v1))
% value = [v1 v2];
value = [txt10 txt11];
RGB = insertText(rgbImage,position,value,FontSize=rows/20,AnchorPoint="LeftBottom");
figure
imshow(RGB)
title("Board")
%
