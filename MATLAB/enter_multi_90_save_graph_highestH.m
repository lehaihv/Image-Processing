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

% Prepare a cell array to store the hue data
hueData = cell(numImages, 3); % Column 1: Image Name, Column 2: Average Hue, Column 3: Max Hue
allMaxHues = []; % Initialize to hold all maximum hues across images
allAvgHues = []; % Initialize to hold all average hues across images

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
    hueTH1 = 0.64; % Upper threshold for dark blue
    saturationTL1 = 0.3; saturationTH1 = 1;  
    valueTL1 = 0.3; valueTH1 = 1; 

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

    % Preallocate arrays for hues
    objectHues = zeros(num_objs, 1); % Initialize array for hues

    % Draw bounding boxes and annotate with maximum and average hues
    for k = 1:num_objs
        thisBoundingBox = props(k).BoundingBox;
        RGB_with_boxes = insertShape(RGB_with_boxes, 'Rectangle', thisBoundingBox, 'Color', 'red', 'LineWidth', 6);
        
        % Ensure centroids are within image bounds
        x = round(centroids(k, 1));
        y = round(centroids(k, 2));
        
        % Check if the pixel coordinates are valid
        if x > 0 && x <= columns && y > 0 && y <= rows
            % Get the hue values of the detected object in the binary mask
            detectedHues = hImage1(binaryImage);
            maxHue = max(detectedHues);  % Calculate maximum hue
            avgHue = mean(detectedHues);  % Calculate average hue
            
            objectHues(k) = maxHue; % Store maximum hue
            
            % Prepare text for display
            hueText = sprintf('Avg Hue: %.2f\nMax Hue: %.2f', avgHue, maxHue);
        else
            hueText = 'Hue: [N/A]';
        end
        
        % Store the average and maximum hue in the cell array
        hueData{fileIdx, 1} = baseFileNames{fileIdx}; % Image name
        hueData{fileIdx, 2} = avgHue; % Average hue
        hueData{fileIdx, 3} = maxHue; % Maximum hue
        
        % Annotate the average and maximum hue at the top left of the bounding box
        textPosition = [thisBoundingBox(1), thisBoundingBox(2)]; % Top left corner
        RGB_with_boxes = insertText(RGB_with_boxes, textPosition, hueText, ...
            'FontSize', 110, 'BoxColor', 'yellow', 'TextColor', 'black', 'AnchorPoint', 'LeftTop');
    end

    % Display the image with bounding boxes and hue annotations in a subplot
    subplot(numRows, numCols, fileIdx); % Arrange images in a grid
    imshow(RGB_with_boxes);
    title(baseFileNames{fileIdx}, 'FontSize', 10); 
    
    % Store all detected hues in the arrays
    allMaxHues = [allMaxHues; objectHues]; % Append detected max hues
    allAvgHues = [allAvgHues; mean(objectHues)]; % Append average hue for this image
end

% Convert the cell array to a table
hueTable = cell2table(hueData, 'VariableNames', {'ImageName', 'AvgHue', 'MaxHue'});

% Save the table to a CSV file
csvFileName = fullfile(folder, 'hue_data.csv');
writetable(hueTable, csvFileName);

% Display a message indicating that the data has been saved
msgbox(sprintf('Hue data saved to:\n%s', csvFileName));

% Plot the overall maximum hue graph
figure; % Create a new figure for the max hue line graph
plot(allMaxHues, '-o', 'LineWidth', 2); % Line graph for max hues
title('Highest Hue of All Detected Objects');
xlabel('Object Index');
ylabel('Max Hue Value');
grid on; % Add grid for better visibility

% Plot the overall average hue graph
figure; % Create a new figure for the average hue line graph
plot(allAvgHues, '-o', 'LineWidth', 2); % Line graph for average hues
title('Average Hue of All Detected Objects');
xlabel('Image Index');
ylabel('Avg Hue Value');
grid on; % Add grid for better visibility