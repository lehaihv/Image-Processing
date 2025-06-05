import cv2
import numpy as np

def nothing(x):
    pass

# Load an image
image = cv2.imread("Pics/BG/1/2.jpg")  # <-- Change this to your image path
if image is None:
    raise FileNotFoundError("Image not found. Check the path.")

# Convert to HSV
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# Create a window
cv2.namedWindow("HSV Range Selector")

# Create trackbars for lower and upper HSV values
cv2.createTrackbar("Lower H", "HSV Range Selector", 90, 179, nothing)
cv2.createTrackbar("Lower S", "HSV Range Selector", 50, 255, nothing)
cv2.createTrackbar("Lower V", "HSV Range Selector", 50, 255, nothing)
cv2.createTrackbar("Upper H", "HSV Range Selector", 130, 179, nothing)
cv2.createTrackbar("Upper S", "HSV Range Selector", 255, 255, nothing)
cv2.createTrackbar("Upper V", "HSV Range Selector", 255, 255, nothing)
cv2.createTrackbar("Scale %", "HSV Range Selector", 50, 100, nothing)  # Scale control

def resize(img, scale_percent):
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    return cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)

while True:
    # Get current positions of all trackbars
    l_h = cv2.getTrackbarPos("Lower H", "HSV Range Selector")
    l_s = cv2.getTrackbarPos("Lower S", "HSV Range Selector")
    l_v = cv2.getTrackbarPos("Lower V", "HSV Range Selector")
    u_h = cv2.getTrackbarPos("Upper H", "HSV Range Selector")
    u_s = cv2.getTrackbarPos("Upper S", "HSV Range Selector")
    u_v = cv2.getTrackbarPos("Upper V", "HSV Range Selector")
    scale = cv2.getTrackbarPos("Scale %", "HSV Range Selector")
    scale = max(10, scale)  # Prevent scale from being too small

    lower = np.array([l_h, l_s, l_v])
    upper = np.array([u_h, u_s, u_v])

    # Create mask and result image
    mask = cv2.inRange(hsv, lower, upper)
    result = cv2.bitwise_and(image, image, mask=mask)

    # Show resized images
    cv2.imshow("Original", resize(image, scale))
    cv2.imshow("Mask", resize(mask, scale))
    cv2.imshow("Filtered Result", resize(result, scale))

    key = cv2.waitKey(1)
    if key == 27:  # ESC key to exit
        break

cv2.destroyAllWindows()
