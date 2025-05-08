import cv2
import numpy as np

# Load the image
image = cv2.imread("Pics/square_tray_not_all_blue.jpg")
if image is None:
    raise ValueError("Image not found or path is incorrect.")

# Convert image to HSV color space
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# Define range for blue color in HSV
lower_blue = np.array([100, 150, 50])
upper_blue = np.array([140, 255, 255])

# Create a binary mask for blue objects
mask = cv2.inRange(hsv, lower_blue, upper_blue)

# Find contours in the mask
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Counters
small_count = 0
large_count = 0

# Draw bounding boxes and classify object sizes
for contour in contours:
    if cv2.contourArea(contour) > 500:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        size_text = f"{w}x{h}px"
        cv2.putText(image, size_text, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        if w < 150:
            small_count += 1
        else:
            large_count += 1

# Print to terminal
print(f"Number of small blue objects: {small_count}")
print(f"Number of large blue objects: {large_count}")

""" # Display the counts on the image
summary_text = f"Small: {small_count} | Large: {large_count}"
cv2.putText(image, summary_text, (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2) """

# Show the image
cv2.imshow("Blue Object Detection", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
