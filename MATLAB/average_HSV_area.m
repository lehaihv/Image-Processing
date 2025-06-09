clc;    % Clear the command window.
close all;  % Close all figures (except those of imtool.)
clear;  % Erase all existing variables.
workspace;  % Ensure the workspace panel is showing.
format long g;
format compact;
fontSize = 25;

% Browse for multiple image files. 
[baseFileNames, folder] = uigetfile('*.jpg', 'Specify image files', 'MultiSelect', 'on'); 
if isequal(baseFileNames, 0)
    return; % User canceled the file selection
end

% Ensure baseFileNames is a cell array
if ischar(baseFileNames)
    baseFileNames = {baseFileNames}; % Convert to cell array if only one file is selected
end

% Define a fixed area of interest (ROI) as [x, y, width, height]
roi = [200, 1090, 780, 365]; % Example: x=100, y=100, width=200, height=200

% Prepare a figure for displaying results
numImages = length(baseFileNames);
numCols = 2; % Set number of columns for the subplot
numRows = ceil(numImages / numCols); % Calculate number of rows needed
figure('Position', [100, 100, 1200, 800]); % Set larger figure size

% Prepare a cell array to store the H, S, V data
hsvData = cell(numImages, 4); % Column 1: Image Name, Column 2: Avg H, Column 3: Avg S, Column 4: Avg V
allAvgH = []; % Initialize to hold all average H values across images
allAvgS = []; % Initialize to hold all average S values across images
allAvgV = []; % Initialize to hold all average V values across images

% Loop through each selected image
for fileIdx = 1:numImages
    fullImageFileName = fullfile(folder, baseFileNames{fileIdx});
    
    % Check to see that the image exists.
    if ~exist(fullImageFileName, 'file')
        message = sprintf('This file does not exist:\n%s', fullImageFileName);
        uiwait(msgbox(message));
        continue; % Skip to the next file
    end

    % Read in the image.
    rgbImage = imread(fullImageFileName);
    
    % Rotate the image 90 degrees anticlockwise
    rgbImage = imrotate(rgbImage, 90);
    
    % Convert RGB to HSV
    hsvImage = rgb2hsv(rgbImage);
    hImage1 = hsvImage(:, :, 1); % Hue channel
    sImage1 = hsvImage(:, :, 2); % Saturation channel
    vImage1 = hsvImage(:, :, 3); % Value channel

    % Extract the area of interest
    x = roi(1);
    y = roi(2);
    width = roi(3);
    height = roi(4);
    
    % Ensure the ROI is within image bounds
    if x + width > size(rgbImage, 2) || y + height > size(rgbImage, 1)
        msgbox(sprintf('ROI exceeds image dimensions in %s', baseFileNames{fileIdx}));
        continue; % Skip to the next file
    end
    
    % Extract H, S, V values from the ROI
    roiHue = hImage1(y:y+height-1, x:x+width-1); % Extract Hue values
    roiSaturation = sImage1(y:y+height-1, x:x+width-1); % Extract Saturation values
    roiValue = vImage1(y:y+height-1, x:x+width-1); % Extract Value values

    % Calculate average H, S, V values
    avgH = mean(roiHue(:));  % Average Hue
    avgS = mean(roiSaturation(:));  % Average Saturation
    avgV = mean(roiValue(:));  % Average Value

    % Store the average H, S, V values in the cell array
    hsvData{fileIdx, 1} = baseFileNames{fileIdx}; % Image name
    hsvData{fileIdx, 2} = avgH; % Average H value
    hsvData{fileIdx, 3} = avgS; % Average S value
    hsvData{fileIdx, 4} = avgV; % Average V value
    
    % Prepare text for display
    valueText = sprintf('Avg H: %.2f\nAvg S: %.2f\nAvg V: %.2f', avgH, avgS, avgV);
    
    % Annotate the averages at the fixed area of interest
    RGB_with_boxes = insertShape(rgbImage, 'Rectangle', roi, 'Color', 'red', 'LineWidth', 6);
    RGB_with_boxes = insertText(RGB_with_boxes, [x, y], valueText, ...
        'FontSize', 20, 'BoxColor', 'yellow', 'TextColor', 'black', 'AnchorPoint', 'LeftTop');

    % Display the image with annotation in a subplot
    subplot(numRows, numCols, fileIdx); % Arrange images in a grid
    imshow(RGB_with_boxes);
    title(baseFileNames{fileIdx}, 'FontSize', 10); 
    
    % Store all average H, S, V values in the arrays
    allAvgH = [allAvgH; avgH]; % Append average H values
    allAvgS = [allAvgS; avgS]; % Append average S values
    allAvgV = [allAvgV; avgV]; % Append average V values
end

% Convert the cell array to a table
hsvTable = cell2table(hsvData, 'VariableNames', {'ImageName', 'AvgH', 'AvgS', 'AvgV'});

% Save the table to a CSV file
csvFileName = fullfile(folder, 'hsv_data.csv');
writetable(hsvTable, csvFileName);

% Display a message indicating that the data has been saved
msgbox(sprintf('HSV data saved to:\n%s', csvFileName));

% Plot the overall average H, S, V graphs
figure; % Create a new figure for the average H values
plot(allAvgH, '-o', 'LineWidth', 2); % Line graph for average H values
title('Average Hue of All Detected Areas');
xlabel('Image Index');
ylabel('Avg Hue (H)');
grid on; % Add grid for better visibility

figure; % Create a new figure for the average S values
plot(allAvgS, '-o', 'LineWidth', 2); % Line graph for average S values
title('Average Saturation of All Detected Areas');
xlabel('Image Index');
ylabel('Avg Saturation (S)');
grid on; % Add grid for better visibility

figure; % Create a new figure for the average V values
plot(allAvgV, '-o', 'LineWidth', 2); % Line graph for average V values
title('Average Value of All Detected Areas');
xlabel('Image Index');
ylabel('Avg Value (V)');
grid on; % Add grid for better visibility