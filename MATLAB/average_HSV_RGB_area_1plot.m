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
roi = [200, 1090, 780, 365]; % Example: x=200, y=1090, width=780, height=365

% Prepare a figure for displaying results
numImages = length(baseFileNames);
numCols = 2; % Set number of columns for the subplot
numRows = ceil(numImages / numCols); % Calculate number of rows needed
figure('Position', [100, 100, 1200, 800]); % Set larger figure size

% Prepare a cell array to store the H, S, V, R, G, B data
hsvData = cell(numImages, 6); % Column 1: Image Name, Column 2: Avg H, Column 3: Avg S, Column 4: Avg V, Column 5: Avg R, Column 6: Avg G, Column 7: Avg B
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
    roiHue = hImage1(y:y+height-1, x:x+width-1);
    roiSaturation = sImage1(y:y+height-1, x:x+width-1);
    roiValue = vImage1(y:y+height-1, x:x+width-1);
    
    % Extract R, G, B values from the original RGB image
    roiRGB = rgbImage(y:y+height-1, x:x+width-1, :);
    roiR = roiRGB(:, :, 1);
    roiG = roiRGB(:, :, 2);
    roiB = roiRGB(:, :, 3);

    % Calculate average H, S, V, R, G, B values
    avgH = mean(roiHue(:));
    avgS = mean(roiSaturation(:));
    avgV = mean(roiValue(:));
    avgR = mean(roiR(:));
    avgG = mean(roiG(:));
    avgB = mean(roiB(:));

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
    
    % Annotate the averages at the fixed area of interest
    RGB_with_boxes = insertShape(rgbImage, 'Rectangle', roi, 'Color', 'red', 'LineWidth', 6);
    RGB_with_boxes = insertText(RGB_with_boxes, [x, y], valueText, ...
        'FontSize', 20, 'BoxColor', 'yellow', 'TextColor', 'black', 'AnchorPoint', 'LeftTop');

    % Display the image with annotation in a subplot
    subplot(numRows, numCols, fileIdx);
    imshow(RGB_with_boxes);
    title(baseFileNames{fileIdx}, 'FontSize', 10); 
    
    % Store all average values in the arrays
    allAvgH = [allAvgH; avgH];
    allAvgS = [allAvgS; avgS];
    allAvgV = [allAvgV; avgV];
    allAvgR = [allAvgR; avgR];
    allAvgG = [allAvgG; avgG];
    allAvgB = [allAvgB; avgB];
end

% Convert the cell array to a table and save to CSV
hsvTable = cell2table(hsvData, 'VariableNames', {'ImageName', 'AvgH', 'AvgS', 'AvgV', 'AvgR', 'AvgG', 'AvgB'});
csvFileName = fullfile(folder, 'hsv_rgb_data_area.csv');
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

title('Average H, S, V of Fixed Area of Interest');
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

title('Average R, G, B of Fixed Area of Interest');
xlabel('Image Index');
ylabel('Average Value');
legend('show'); % Display legend
grid on; % Add grid for better visibility