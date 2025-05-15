import sys
import cv2
import numpy as np
from rembg import remove
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QTextEdit, QFileDialog
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt
from PIL import Image
import io

class ImageProcessor(QWidget):
    def __init__(self):
        super().__init__()

        self.image_label = QLabel(self)
        self.text_box = QTextEdit(self)
        self.open_button = QPushButton("Open Image", self)
        self.exit_button = QPushButton("Exit", self)

        # Set button widths
        self.open_button.setFixedWidth(250)
        self.exit_button.setFixedWidth(50)

        self.open_button.clicked.connect(self.open_image)
        self.exit_button.clicked.connect(self.close)

        layout = QVBoxLayout()

        # Maximize the image box
        self.image_label.setScaledContents(True)
        layout.addWidget(self.image_label)

        # Set text box height
        self.text_box.setFixedHeight(100)
        layout.addWidget(self.text_box)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.open_button)
        button_layout.addWidget(self.exit_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)
        self.setWindowTitle("Blue Object Detector with Background Removal")

        screen = QApplication.primaryScreen().availableGeometry()
        width = int(screen.width() * 0.75)
        height = int(screen.height() * 0.75)
        self.setFixedSize(width, height)

    def open_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.xpm *.jpg *.jpeg)")
        if file_name:
            self.process_image(file_name)

    def process_image(self, file_name):
        # Read original image
        with open(file_name, 'rb') as f:
            input_data = f.read()

        # Remove background using rembg
        output_data = remove(input_data)

        # Convert bytes to PIL Image
        image_pil = Image.open(io.BytesIO(output_data)).convert("RGBA")

        # Convert RGBA to OpenCV format (BGR) and replace transparent with white
        bg = Image.new("RGBA", image_pil.size, (255, 255, 255, 255))
        image_pil = Image.alpha_composite(bg, image_pil).convert("RGB")
        image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)

        # Convert image to HSV color space
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Define range of blue color in HSV
        lower_blue = np.array([100, 150, 0])
        upper_blue = np.array([140, 255, 255])

        # Threshold the HSV image to get only blue colors
        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        dimensions = []
        count_large = 0
        count_medium = 0
        count_small = 0

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 500:  # Filter contours by minimum area
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

                blue_intensity = np.mean(image[y:y + h, x:x + w, 0])  # Blue channel

                if area > 25000:
                    size_category = "Large"
                    count_large += 1
                elif area > 5000:
                    size_category = "Medium"
                    count_medium += 1
                else:
                    size_category = "Small"
                    count_small += 1

                details = f"Object at ({x}, {y}) - W: {w}, H: {h}, Area: {area}, Blue Intensity: {blue_intensity:.2f}, Size: {size_category}"
                dimensions.append(details)

        self.display_image(image)

        total_objects = count_large + count_medium + count_small
        summary = (f"Total Objects: {total_objects}\n"
                   f"Large Objects: {count_large}\n"
                   f"Medium Objects: {count_medium}\n"
                   f"Small Objects: {count_small}\n")

        self.text_box.clear()
        self.text_box.append("\n".join(dimensions))
        self.text_box.append(summary)

        for dimension in dimensions:
            print(dimension)
        print(summary)

    def display_image(self, image):
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format.Format_BGR888)
        pixmap = QPixmap.fromImage(q_image)
        self.image_label.setPixmap(pixmap.scaled(
            self.image_label.width(),
            self.image_label.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageProcessor()
    window.show()
    sys.exit(app.exec())
