import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QTextEdit, QFileDialog
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt

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
        self.setWindowTitle("Light Blue Object Detector")

        # Set window size to 3/4 of screen size
        screen = QApplication.primaryScreen().availableGeometry()
        width = int(screen.width() * 0.75)
        height = int(screen.height() * 0.75)
        self.setFixedSize(width, height)

    def open_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.xpm *.jpg *.jpeg *.bmp)")
        if file_name:
            self.process_image(file_name)

    def process_image(self, file_name):
        image = cv2.imread(file_name)
        if image is None:
            print("Error: Could not open image.")
            return

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Detect light blue color only
        lower_blue = np.array([90, 30, 200])
        upper_blue = np.array([110, 120, 255])
        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        # Morphological filtering to reduce noise
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        dimensions = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 100:
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                blue_intensity = np.mean(image[y:y + h, x:x + w, 0])  # Blue channel
                dimensions.append(f"Object at ({x}, {y}) - W: {w}, H: {h}, Area: {area}, Blue Intensity: {blue_intensity:.2f}")

        self.display_image(image)
        self.text_box.clear()
        self.text_box.append("\n".join(dimensions))
        self.text_box.append(f"Total Light Blue Objects: {len(dimensions)}")

    def display_image(self, image):
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format.Format_BGR888)
        self.image_label.setPixmap(QPixmap.fromImage(q_image))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageProcessor()
    window.show()
    sys.exit(app.exec())
