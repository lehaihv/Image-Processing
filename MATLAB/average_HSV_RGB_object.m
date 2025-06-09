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

% Prepare a cell array to store the H, S, V, R, G, B data
hsvData = cell(numImages, 7); % Columns: Image Name, Avg H, Avg S, Avg V, Avg R, Avg G, Avg B
allAvgH = []; % Initialize to hold all average H values across images
allAvgS = []; % Initialize to hold all average S values across images
allAvgV = []; % Initialize to hold all average V values across images
allAvgR = []; % Initialize to hold all average R values across images
allAvgG = []; % Initialize to hold all average G values across images
allAvgB = []; % Initialize to hold all average B values across images

% Loop through each selected image
for fileIdx = 1:numImages
    fullImageFileName = fullfile(folder, baseFileNames{fileIdx});
    
    % Check if the image exists
    if ~exist(fullImageFileName, 'file')
        message = sprintf('This file does not exist:\n%s', fullImageFileName);
        uiwait(msgbox(message));
        continue; % Skip to the next file
    end

    % Read in the image and rotate it
    rgbImage = imread(fullImageFileName);
    rgbImage = imrotate(rgbImage, 90);
    
    % Convert RGB to HSV
    hsvImage = rgb2hsv(rgbImage);
    hImage1 = hsvImage(:, :, 1); % Hue channel
    sImage1 = hsvImage(:, :, 2); % Saturation channel
    vImage1 = hsvImage(:, :, 3); % Value channel

    % Set thresholds for detecting blue objects.
    hueTL1 = 0.15; % Lower threshold for light blue
    hueTH1 = 0.63; % Upper threshold for dark blue
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

    % Create a copy of the original image for displaying results
    RGB_with_boxes = rgbImage;

    % Loop through each detected blue object
    for k = 1:num_objs
        thisBoundingBox = props(k).BoundingBox;
        RGB_with_boxes = insertShape(RGB_with_boxes, 'Rectangle', thisBoundingBox, 'Color', 'red', 'LineWidth', 6);
        
        % Extract the region of interest for the current object
        objectMask = binaryImage( ...
            round(thisBoundingBox(2)):round(thisBoundingBox(2) + thisBoundingBox(4) - 1), ...
            round(thisBoundingBox(1)):round(thisBoundingBox(1) + thisBoundingBox(3) - 1));
        
        % Extract H, S, and V values for the detected blue object
        roiHue = hImage1(objectMask); % Extract Hue values
        roiSaturation = sImage1(objectMask); % Extract Saturation values
        roiValue = vImage1(objectMask); % Extract Value values

        % Extract R, G, B values for the detected blue object
        roiRGB = rgbImage( ...
            round(thisBoundingBox(2)):round(thisBoundingBox(2) + thisBoundingBox(4) - 1), ...
            round(thisBoundingBox(1)):round(thisBoundingBox(1) + thisBoundingBox(3) - 1), :);
        roiR = roiRGB(:, :, 1);
        roiG = roiRGB(:, :, 2);
        roiB = roiRGB(:, :, 3);

        % Calculate average H, S, V, R, G, B values
        avgH = mean(roiHue(:));  % Average Hue
        avgS = mean(roiSaturation(:));  % Average Saturation
        avgV = mean(roiValue(:));  % Average Value
        avgR = mean(roiR(:));  % Average Red
        avgG = mean(roiG(:));  % Average Green
        avgB = mean(roiB(:));  % Average Blue

        % Store the average values in the cell array
        hsvData{fileIdx, 1} = baseFileNames{fileIdx}; % Image name
        hsvData{fileIdx, 2} = avgH; % Average H value
        hsvData{fileIdx, 3} = avgS; % Average S value
        hsvData{fileIdx, 4} = avgV; % Average V value
        hsvData{fileIdx, 5} = avgR; % Average R value
        hsvData{fileIdx, 6} = avgG; % Average G value
        hsvData{fileIdx, 7} = avgB; % Average B value
        
        % Prepare text for display
        valueText = sprintf('Avg H: %.2f\nAvg S: %.2f\nAvg V: %.2f\nAvg R: %.2f\nAvg G: %.2f\nAvg B: %.2f', ...
                            avgH, avgS, avgV, avgR, avgG, avgB);
        
        % Annotate the averages at the bounding box
        textPosition = [thisBoundingBox(1), thisBoundingBox(2)]; % Top left corner
        RGB_with_boxes = insertText(RGB_with_boxes, textPosition, valueText, ...
            'FontSize', 20, 'BoxColor', 'yellow', 'TextColor', 'black', 'AnchorPoint', 'LeftTop');
    end

    % Display the image with annotation in a subplot
    subplot(numRows, numCols, fileIdx); % Arrange images in a grid
    imshow(RGB_with_boxes);
    title(baseFileNames{fileIdx}, 'FontSize', 10); 
    
    % Store all average values in the arrays
    allAvgH = [allAvgH; avgH]; % Append average H values
    allAvgS = [allAvgS; avgS]; % Append average S values
    allAvgV = [allAvgV; avgV]; % Append average V values
    allAvgR = [allAvgR; avgR]; % Append average R values
    allAvgG = [allAvgG; avgG]; % Append average G values
    allAvgB = [allAvgB; avgB]; % Append average B values
end

% Convert the cell array to a table
hsvTable = cell2table(hsvData, 'VariableNames', {'ImageName', 'AvgH', 'AvgS', 'AvgV', 'AvgR', 'AvgG', 'AvgB'});

% Save the table to a CSV file
csvFileName = fullfile(folder, 'hsv_rgb_data_object.csv');
writetable(hsvTable, csvFileName);

% Display a message indicating that the data has been saved
msgbox(sprintf('HSV and RGB data saved to:\n%s', csvFileName));

% Combined plot for average H, S, V values
figure; % Create a new figure for H, S, V
hold on; % Hold on to plot multiple lines
plot(allAvgH, '-o', 'LineWidth', 2, 'DisplayName', 'Avg Hue (H)');
plot(allAvgS, '-o', 'LineWidth', 2, 'DisplayName', 'Avg Saturation (S)');
plot(allAvgV, '-o', 'LineWidth', 2, 'DisplayName', 'Avg Value (V)');
hold off; % Release the hold

title('Average H, S, V of Detected Blue Objects');
xlabel('Image Index');
ylabel('Average Value');
legend('show'); % Display legend
grid on; % Add grid for better visibility

% Combined plot for average R, G, B values
figure; % Create a new figure for R, G, B
hold on; % Hold on to plot multiple lines
plot(allAvgR, '-o', 'LineWidth', 2, 'DisplayName', 'Avg Red (R)');
plot(allAvgG, '-o', 'LineWidth', 2, 'DisplayName', 'Avg Green (G)');
plot(allAvgB, '-o', 'LineWidth', 2, 'DisplayName', 'Avg Blue (B)');
hold off; % Release the hold

title('Average R, G, B of Detected Blue Objects');
xlabel('Image Index');
ylabel('Average Value');
legend('show'); % Display legend
grid on; % Add grid for better visibility