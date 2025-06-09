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
    
    [rows, columns, ~] = size(rgbImage);
    
    % Compute HSV image.
    hsvImage = rgb2hsv(rgbImage);
    hImage1 = hsvImage(:, :, 1);
    sImage1 = hsvImage(:, :, 2);
    vImage1 = hsvImage(:, :, 3);

    % Set thresholds for detecting all shades of blue.
    hueTL1 = 0.15; % Lower threshold for light blue
    hueTH1 = 0.63; % Upper threshold for dark blue
    saturationTL1 = 0.3; saturationTH1 = 1;  
    valueTL1 = 0.2; valueTH1 = 1; 

    % Create binary mask for blue objects.
    hueMaskBlue = (hImage1 >= hueTL1 & hImage1 <= hueTH1);
    saturationMaskBlue = (sImage1 >= saturationTL1 & sImage1 <= saturationTH1);
    valueMaskBlue = (vImage1 >= valueTL1 & vImage1 <= valueTH1);
    binaryImage = hueMaskBlue & saturationMaskBlue & valueMaskBlue;

    % Remove small objects from the binary image.
    binaryImage = bwareaopen(binaryImage, 50000); % Adjusted area threshold

    % Get properties of detected objects.
    props = regionprops(binaryImage, 'Area', 'Centroid', 'BoundingBox');
    num_objs = size(props, 1);
    
    if num_objs < 1
        message = sprintf('There are no blue objects in the image \n%s', fullImageFileName);
        uiwait(msgbox(message));
        continue; % Skip to the next file
    end

    % Prepare to store centroid coordinates
    centroids = cat(1, props.Centroid);

    % Create a copy of the original image for displaying results
    RGB_with_boxes = rgbImage;

    % Preallocate arrays for V values
    objectValues = zeros(num_objs, 1); % Initialize array for V values

    % Draw bounding boxes and annotate with maximum and average V values
    for k = 1:num_objs
        thisBoundingBox = props(k).BoundingBox;
        RGB_with_boxes = insertShape(RGB_with_boxes, 'Rectangle', thisBoundingBox, 'Color', 'red', 'LineWidth', 6);
        
        % Ensure centroids are within image bounds
        x = round(centroids(k, 1));
        y = round(centroids(k, 2));
        
        % Check if the pixel coordinates are valid
        if x > 0 && x <= columns && y > 0 && y <= rows
            % Get the V values of the detected object in the binary mask
            detectedValues = vImage1(binaryImage);
            maxValue = max(detectedValues);  % Calculate maximum V value
            avgValue = mean(detectedValues);  % Calculate average V value
            
            objectValues(k) = maxValue; % Store maximum V value
            
            % Prepare text for display
            valueText = sprintf('Avg V: %.2f\nMax V: %.2f', avgValue, maxValue);
        else
            valueText = 'V: [N/A]';
        end
        
        % Store the average and maximum V value in the cell array
        valueData{fileIdx, 1} = baseFileNames{fileIdx}; % Image name
        valueData{fileIdx, 2} = avgValue; % Average V value
        valueData{fileIdx, 3} = maxValue; % Maximum V value
        
        % Annotate the average and maximum V at the top left of the bounding box
        textPosition = [thisBoundingBox(1), thisBoundingBox(2)]; % Top left corner
        RGB_with_boxes = insertText(RGB_with_boxes, textPosition, valueText, ...
            'FontSize', 110, 'BoxColor', 'yellow', 'TextColor', 'black', 'AnchorPoint', 'LeftTop');
    end

    % Display the image with bounding boxes and V annotations in a subplot
    subplot(numRows, numCols, fileIdx); % Arrange images in a grid
    imshow(RGB_with_boxes);
    title(baseFileNames{fileIdx}, 'FontSize', 10); 
    
    % Store all detected V values in the arrays
    allMaxValues = [allMaxValues; objectValues]; % Append detected max V values
    allAvgValues = [allAvgValues; avgValue]; % Append average V for this image
end

% Convert the cell array to a table
valueTable = cell2table(valueData, 'VariableNames', {'ImageName', 'AvgValue', 'MaxValue'});

% Save the table to a CSV file
csvFileName = fullfile(folder, 'value_data.csv');
writetable(valueTable, csvFileName);

% Display a message indicating that the data has been saved
msgbox(sprintf('Value data saved to:\n%s', csvFileName));

% Plot the overall maximum V graph
figure; % Create a new figure for the max V line graph
plot(allMaxValues, '-o', 'LineWidth', 2); % Line graph for max V values
title('Highest Value of All Detected Objects');
xlabel('Object Index');
ylabel('Max Value (V)');
grid on; % Add grid for better visibility

% Plot the overall average V graph
figure; % Create a new figure for the average V line graph
plot(allAvgValues, '-o', 'LineWidth', 2); % Line graph for average V values
title('Average Value of All Detected Objects');
xlabel('Image Index');
ylabel('Avg Value (V)');
grid on; % Add grid for better visibility