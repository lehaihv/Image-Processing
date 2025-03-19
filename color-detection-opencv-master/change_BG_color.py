""" # Import the library OpenCV 
import cv2 

# Import the image 
file_name = "Pics/gfgblack.png"

# Read the image 
src = cv2.imread(file_name, 1) 

# Convert image to image gray 
tmp = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY) 

# Applying thresholding technique 
_, alpha = cv2.threshold(tmp, 0, 255, cv2.THRESH_BINARY) 

# Using cv2.split() to split channels 
# of coloured image 
b, g, r = cv2.split(src) 

# Making list of Red, Green, Blue 
# Channels and alpha 
rgba = [b, g, r, alpha] 

# Using cv2.merge() to merge rgba 
# into a coloured/multi-channeled image 
dst = cv2.merge(rgba, 4) 

# Writing and saving to a new image 
while (1):
    cv2.imshow('Result', dst)
    if cv2.waitKey(0): #(10) & 0xFF == ord('q'): 
        #webcam.release() 
        cv2.destroyAllWindows() 
        break
#cv2.imwrite("gfg_white.png", dst)  """


""" import cv2
import numpy as np
import skimage.exposure

# load image and get dimensions
img = cv2.imread("Pics/pic_10.jpg")

# convert to hsv
lab = cv2.cvtColor(img,cv2.COLOR_BGR2LAB)
L = lab[:,:,0]
A = lab[:,:,1]
B = lab[:,:,2]

# negate A
A = (255 - A)

# multiply negated A by B
nAB = 255 * (A/255) * (B/255)
nAB = np.clip((nAB), 0, 255)
nAB = np.uint8(nAB)


# threshold using inRange
range1 = 100
range2 = 160
mask = cv2.inRange(nAB,range1,range2)
mask = 255 - mask

# apply morphology opening to mask
kernel = np.ones((3,3), np.uint8)
mask = cv2.morphologyEx(mask, cv2.MORPH_ERODE, kernel)
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

# antialias mask
mask = cv2.GaussianBlur(mask, (0,0), sigmaX=3, sigmaY=3, borderType = cv2.BORDER_DEFAULT)
mask = skimage.exposure.rescale_intensity(mask, in_range=(127.5,255), out_range=(0,255))

# put white where ever the mask is zero
result = img.copy()
result[mask==0] = (255,255,255)

# write result to disk
cv2.imwrite("soccer_green2white_inrange_lab.jpg", result)

# display it
#cv2.imshow("nAB", nAB)
cv2.imshow("mask", mask)
#cv2.imshow("result", result)
cv2.waitKey(0)
cv2.destroyAllWindows() """

""" import cv2
import numpy as np

# Load the image
image = cv2.imread('Pics/gfgblack.png')

# Define the new background color (BGR format)
new_bg_color = (255, 255, 255)  # Red

# Create a mask for the foreground
mask = np.zeros(image.shape[:2], np.uint8)

# Define a region of interest (ROI) to specify the foreground
roi_corners = np.array([[(100, 100), (300, 100), (300, 300), (100, 300)]], dtype=np.int32)
cv2.fillPoly(mask, roi_corners, 255)

# Create a new image with the new background color
new_image = np.zeros_like(image)
new_image[:] = new_bg_color

# Copy the foreground to the new image using the mask
new_image[mask == 255] = image[mask == 255]

# Display the result
cv2.imshow('Original Image', image)
cv2.imshow('New Background', new_image)
cv2.waitKey(0)
cv2.destroyAllWindows() """

