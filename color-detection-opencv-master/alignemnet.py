import cv2
import numpy as np
from PyQt6.QtWidgets import QApplication, QFileDialog

def align_images(img1, img2, max_features=5000, good_match_percent=0.15):
    # Convert images to grayscale
    img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # Detect ORB features and compute descriptors.
    orb = cv2.ORB_create(max_features)
    keypoints1, descriptors1 = orb.detectAndCompute(img1_gray, None)
    keypoints2, descriptors2 = orb.detectAndCompute(img2_gray, None)

    # Match features.
    matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
    matches = matcher.match(descriptors1, descriptors2, None)

    # Sort matches by score
    matches = sorted(matches, key=lambda x: x.distance)

    # Remove not so good matches
    num_good_matches = int(len(matches) * good_match_percent)
    matches = matches[:num_good_matches]

    # Extract location of good matches
    points1 = np.zeros((len(matches), 2), dtype=np.float32)
    points2 = np.zeros((len(matches), 2), dtype=np.float32)

    for i, match in enumerate(matches):
        points1[i, :] = keypoints1[match.queryIdx].pt
        points2[i, :] = keypoints2[match.trainIdx].pt

    # Find homography
    h, mask = cv2.findHomography(points2, points1, cv2.RANSAC)

    # Use homography to warp img2 to img1
    height, width, channels = img1.shape
    img2_aligned = cv2.warpPerspective(img2, h, (width, height))

    return img2_aligned, h

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    # Browse for two images
    file_names, _ = QFileDialog.getOpenFileNames(
        None, "Select two images", "", "Images (*.png *.jpg *.jpeg *.bmp)"
    )
    if len(file_names) != 2:
        print("Please select exactly two images.")
        sys.exit(1)

    img1 = cv2.imread(file_names[0])  # Reference image
    img2 = cv2.imread(file_names[1])  # Image to align

    if img1 is None or img2 is None:
        print("Error: Could not load input images.")
        sys.exit(1)

    aligned_img, homography = align_images(img1, img2)

    cv2.imwrite("aligned_image.jpg", aligned_img)
    print("Aligned image saved as 'aligned_image.jpg'.")

    # Resize all images to the same display size
    display_width, display_height = 400, 400
    img1_disp = cv2.resize(img1, (display_width, display_height), interpolation=cv2.INTER_AREA)
    img2_disp = cv2.resize(img2, (display_width, display_height), interpolation=cv2.INTER_AREA)
    aligned_disp = cv2.resize(aligned_img, (display_width, display_height), interpolation=cv2.INTER_AREA)

    # Stack images horizontally
    combined = np.hstack((img1_disp, img2_disp, aligned_disp))

    # Show all three images in one window
    cv2.imshow("Input1 | Input2 | Aligned", combined)
    cv2.waitKey(0)
    cv2.destroyAllWindows()