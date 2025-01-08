# Python program to identify 
#color in images 

# Importing the libraries OpenCV and numpy 
import cv2 
import numpy as np 

# Read the images 
# img = cv2.imread("Pics/Blue_pen.jpg") 
img = cv2.imread("Pics/Multiple_obj.jpg") 
# Resizing the image 
image = cv2.resize(img, (700, 600)) 

# Convert Image to Image HSV 
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV) 

# Defining lower and upper bound HSV values 
lower = np.array([94, 80, 2]) 
upper = np.array([120, 255, 255]) 
# Set range for blue color and 
# define mask 
""" blue_lower = np.array([94, 80, 2], np.uint8) 
blue_upper = np.array([120, 255, 255], np.uint8) 
blue_mask = cv2.inRange(hsvFrame, blue_lower, blue_upper) """

# Defining mask for detecting color 
mask = cv2.inRange(hsv, lower, upper) 

blue=cv2.bitwise_and(image,image,mask=mask)

# Display Image and Mask 
# cv2.imshow("Image", image) 
# cv2.imshow("Mask", mask) 
cv2.imshow("Mask", blue)

avg_hsv = np.mean(blue, axis=(0, 1))
mea_value = f"{(avg_hsv[0]+avg_hsv[1]+avg_hsv[2]):.1f}"
print(mea_value)

# Make python sleep for unlimited time 
cv2.waitKey(0) 
