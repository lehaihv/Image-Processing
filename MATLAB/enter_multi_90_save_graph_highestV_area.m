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
roi = [200, 1090, 800, 365]; % Example: x=100, y=100, width=200, height=200

% Prepare a figure for displaying results
numImages = length(baseFileNames);
numCols = 2; % Set number of columns for the subplot
numRows = ceil(numImages / numCols); % Calculate number of rows needed
figure('Position', [100, 100, 1200, 800]); % Set larger figure size

% Prepare a cell array to store the value data
valueData = cell(numImages, 3); % Column 1: Image Name, Column 2: Average Value, Column 3: Max Value
allMaxValues = []; % Initialize to hold all maximum V values across images
allAvgValues = []; % Initialize to hold all average V values across images

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
    vImage1 = hsvImage(:, :, 3); % Extract the Value channel

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
    
    roiValues = vImage1(y:y+height-1, x:x+width-1); % Extract V values from the ROI

    % Calculate maximum and average V values
    maxValue = max(roiValues(:));  % Calculate maximum V value
    avgValue = mean(roiValues(:));  % Calculate average V value

    % Store the average and maximum V value in the cell array
    valueData{fileIdx, 1} = baseFileNames{fileIdx}; % Image name
    valueData{fileIdx, 2} = avgValue; % Average V value
    valueData{fileIdx, 3} = maxValue; % Maximum V value
    
    % Prepare text for display
    valueText = sprintf('Avg V: %.2f\nMax V: %.2f', avgValue, maxValue);
    
    % Annotate the average and maximum V at the fixed area of interest
    RGB_with_boxes = insertShape(rgbImage, 'Rectangle', roi, 'Color', 'red', 'LineWidth', 6);
    RGB_with_boxes = insertText(RGB_with_boxes, [x, y], valueText, ...
        'FontSize', 20, 'BoxColor', 'yellow', 'TextColor', 'black', 'AnchorPoint', 'LeftTop');

    % Display the image with annotation in a subplot
    subplot(numRows, numCols, fileIdx); % Arrange images in a grid
    imshow(RGB_with_boxes);
    title(baseFileNames{fileIdx}, 'FontSize', 10); 
    
    % Store all detected V values in the arrays
    allMaxValues = [allMaxValues; maxValue]; % Append detected max V values
    allAvgValues = [allAvgValues; avgValue]; % Append average V for this image
end

% Convert the cell array to a table
valueTable = cell2table(valueData, 'VariableNames', {'ImageName', 'AvgValue', 'MaxValue'});

% Save the table to a CSV file
csvFileName = fullfile(folder, 'value_data_area.csv');
writetable(valueTable, csvFileName);

% Display a message indicating that the data has been saved
msgbox(sprintf('Value data saved to:\n%s', csvFileName));

% Plot the overall maximum V graph
figure; % Create a new figure for the max V line graph
plot(allMaxValues, '-o', 'LineWidth', 2); % Line graph for max V values
title('Highest Value of All Detected Areas');
xlabel('Image Index');
ylabel('Max Value (V)');
grid on; % Add grid for better visibility

% Plot the overall average V graph
figure; % Create a new figure for the average V line graph
plot(allAvgValues, '-o', 'LineWidth', 2); % Line graph for average V values
title('Average Value of All Detected Areas');
xlabel('Image Index');
ylabel('Avg Value (V)');
grid on; % Add grid for better visibility