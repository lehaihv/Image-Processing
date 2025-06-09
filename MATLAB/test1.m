clc;    % Clear the command window.
close all;  % Close all figures (except those of imtool.)
clear;  % Erase all existing variables. Or clearvars if you want.
workspace;  % Make sure the workspace panel is showing.
format long g;
format compact;
fontSize = 25;

% %===============================================================================
% % Get the name of the image the user wants to use.
% baseFileName = 'Pics/pic_8.jpg'; %pic_8.jpgpic_7_W
% folder = fileparts(which(baseFileName)); % Determine where demo folder is (works with all versions).
% fullFileName = fullfile(folder, baseFileName);
% 
% % Check if file exists.
% if ~exist(fullFileName, 'file')
%   % The file doesn't exist -- didn't find it there in that folder.
%   % Check the entire search path (other folders) for the file by stripping off the folder.
%   fullFileNameOnSearchPath = baseFileName; % No path this time.
%   if ~exist(fullFileNameOnSearchPath, 'file')
%     % Still didn't find it.  Alert user.
%     errorMessage = sprintf('Error: %s does not exist in the search path folders.', fullFileName);
%     uiwait(warndlg(errorMessage));
%     return;
%   end
% end
% 
% %===============================================================================

% Browse for the image file. 
[baseFileName, folder] = uigetfile('*.jpg', 'Specify an image file'); 
fullImageFileName = fullfile(folder, baseFileName); 
% Set current folder back to the original one. 
%cd(originalFolder);
selectedImage = 'My own image'; % Need for the if threshold selection statement later.

% Check to see that the image exists.  (Mainly to check on the demo images.)
if ~exist(fullImageFileName, 'file')
	message = sprintf('This file does not exist:\n%s', fullImageFileName);
	uiwait(msgbox(message));
	return;
end

% Read in demo image.
rgbImage = imread(fullImageFileName); %fullFileName);
[rows, columns, numberOfColorChannels] = size(rgbImage);
disp(rows);
disp(columns);
% Compute HSV image.
hsvImage = rgb2hsv(rgbImage);
hImage1 = hsvImage(:, :, 1);
sImage1 = hsvImage(:, :, 2);
vImage1 = hsvImage(:, :, 3);

hueTL1 = 0.4; hueTH1 = 0.69; hueH1 = 1;
saturationTL1 = 0.2; saturationTH1 = 1;
valueTL1 = 0.01; valueTH1 = 1;

hueMaskred1 = (hImage1 > hueTL1) & (hImage1 <= hueTH1)|(hImage1 >= hueH1);
saturationMaskred1 = (sImage1 >= saturationTL1) & (sImage1 <= saturationTH1);
valueMaskred1 = (vImage1 >= valueTL1) & (vImage1 <= valueTH1);
binaryImage = hueMaskred1 & saturationMaskred1 & valueMaskred1;

%Take largest blobs only
binaryImage = bwareaopen(binaryImage, 1000); %smallest size of object

props = regionprops(binaryImage, 'Area');
allAreas = sort([props.Area], 'descend')

props1 = regionprops(binaryImage, 'Centroid');
% allAreas1 = sort([props1.Centroid], 'descend')
centroids = cat(1,props1.Centroid);
disp("Centroid");
disp(centroids);

num_objs = size(props,1);
disp("No of Objects");
disp(num_objs);

if num_objs < 1
    message = sprintf('There is no blue object in the image \n%s', fullImageFileName);
	uiwait(msgbox(message));
	return;    
end

arr_temp = [];
%arr_temp = zeros(1, num_objs);
for i=1:2
    for j=1:num_objs
        arr_temp = [arr_temp, centroids(j,i)];    %centroids(j,i)
    end
end    
disp("Array of centroids");
disp(arr_temp);

if num_objs >1
    pos = reshape(arr_temp,[],2); % num_objs = []
else
    pos = arr_temp;
end
disp("Matrix of centroids");
disp(pos); %pos is the array of all centroid of objects

val_temp = [];
for i=1:num_objs 
    val_temp = [val_temp, impixel(rgbImage,centroids(i,1),centroids(i,2))];
end
disp("Val array");
disp(val_temp);
%disp(val_temp (1,6));

value = [];
for i=1:3:(num_objs*3) 
    txt_buf = string(val_temp(1,i)) + " " + string(val_temp(1,i+1)) + " " + string(val_temp(1,i+2));
    value = [value, txt_buf];
end

disp(size(value));
disp(value);
%fontSize = 1000;

% fontSize = int32(rows/40);
% if fontSize < 15
%     fontSize = 25;
% end    
    
RGB = insertText(rgbImage,pos,value,FontSize=50,AnchorPoint="CenterTop"); %FontSize=fontSize,
figure
imshow(RGB)
title("Enterolert Test Results")

