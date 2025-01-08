
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

	% Read in image into an array.
	[rgbImage, storedColorMap] = imread(fullImageFileName); 
    figure;
    imshow(rgbImage);