import cv2
import numpy as np

# Read the image
image = cv2.imread("Pics/pic_3.jpg")

# Convert the image to the HSV color space
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# Define the range of colors for dark blue
lower_dark_blue = np.array([100, 50, 50])
upper_dark_blue = np.array([130, 255, 255])

# Define the range of colors for light blue
lower_light_blue = np.array([90, 50, 50])
upper_light_blue = np.array([110, 255, 255])

# Create a mask for dark blue
mask_dark_blue = cv2.inRange(hsv, lower_dark_blue, upper_dark_blue)

# Create a mask for light blue
mask_light_blue = cv2.inRange(hsv, lower_light_blue, upper_light_blue)

# Apply the masks to the image
result_dark_blue = cv2.bitwise_and(image, image, mask=mask_dark_blue)
result_light_blue = cv2.bitwise_and(image, image, mask=mask_light_blue)

# Show the results
cv2.imshow('Dark Blue', result_dark_blue)
cv2.imshow('Light Blue', result_light_blue)
cv2.waitKey(0)
cv2.destroyAllWindows()