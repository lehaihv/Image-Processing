% Open a dialog to select multiple image files
[filenames, pathname] = uigetfile({'*.jpg;*.png;*.bmp', 'Image Files (*.jpg, *.png, *.bmp)'}, 'Select Images', 'MultiSelect', 'on');
if isequal(filenames, 0)
    disp('User canceled the image selection.');
    return;
end

% Ensure filenames is a cell array
if ischar(filenames)
    filenames = {filenames}; % Convert to cell array if only one file is selected
end

% Define the coordinates for the ROI [x, y, width, height]
% roi_x = 235; % Starting x coordinate
% roi_y = 2150; % Starting y coordinate
% width = 3580; % Width of the ROI
% height = 250; % Height of the ROI

roi_x = 200; % Starting x coordinate
roi_y = 270; % Starting y coordinate
width = 380;      % Width of the ROI
height = 630;     % Height of the ROI

% Create the Cropping folder if it doesn't exist
croppingFolder = fullfile(pathname, 'Cropping');
if ~exist(croppingFolder, 'dir')
    mkdir(croppingFolder); % Create the folder
end

% Loop through each selected image
for i = 1:length(filenames)
    % Load the selected image
    img = imread(fullfile(pathname, filenames{i}));
    
    % Cut out the ROI
    roi = imcrop(img, [roi_x, roi_y, width, height]);
    
    % Generate new filename for the cropped image
    [~, name, ext] = fileparts(filenames{i}); % Get the file name and extension
    newFilename = fullfile(croppingFolder, [name, '-cropping', ext]); % New filename
    
    % Save the cropped image, overwriting if it exists
    imwrite(roi, newFilename);
    
    % Display results
    fprintf('Cropped image saved as: %s\n', newFilename);
end

disp('Cropping completed for all selected images.');