import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QTextEdit, QFileDialog
)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt

class ImageProcessor(QWidget):
    def __init__(self):
        super().__init__()

        # Classification thresholds
        self.large_threshold = 25000
        self.medium_threshold = 5000
        self.min_area = 3500

        # UI components
        self.image_label = QLabel(self)
        self.text_box = QTextEdit(self)
        self.open_button = QPushButton("Open Image", self)
        self.exit_button = QPushButton("Exit", self)

        # Set button widths
        self.open_button.setFixedWidth(250)
        self.exit_button.setFixedWidth(50)

        # Button actions
        self.open_button.clicked.connect(self.open_image)
        self.exit_button.clicked.connect(self.close)

        # Layout setup
        layout = QVBoxLayout()
        self.image_label.setScaledContents(True)
        layout.addWidget(self.image_label)

        self.text_box.setFixedHeight(100)
        layout.addWidget(self.text_box)

        # Centered button layout at bottom
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.open_button)
        button_layout.addWidget(self.exit_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)
        self.setLayout(layout)
        self.setWindowTitle("Blue Object Detector")

        # Set window size to 3/4 of screen size but allow resizing
        screen = QApplication.primaryScreen().availableGeometry()
        width = int(screen.width() * 0.75)
        height = int(screen.height() * 0.75)
        self.resize(width, height)
        self.setMinimumSize(600, 400)

    def open_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Image File", "",
            "Images (*.png *.xpm *.jpg *.jpeg *.bmp)"
        )
        if file_name:
            self.process_image(file_name)

    def process_image(self, file_name):
        image = cv2.imread(file_name)
        if image is None:
            print("Error: Could not open image.")
            return

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Adjusted threshold to include light blue
        lower_blue = np.array([90, 60, 50])
        upper_blue = np.array([140, 255, 255])

        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        dimensions = []
        count_large = 0
        count_medium = 0
        count_small = 0
        object_index = 1

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > self.min_area:
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Draw object number above the rectangle
                label = f"#{object_index}"
                cv2.putText(image, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                            0.6, (0, 0, 255), 2, cv2.LINE_AA)

                blue_intensity = np.mean(image[y:y + h, x:x + w, 0])

                if area > self.large_threshold:
                    size_category = "Large"
                    count_large += 1
                elif area > self.medium_threshold:
                    size_category = "Medium"
                    count_medium += 1
                else:
                    size_category = "Small"
                    count_small += 1

                dimensions.append(
                    f"#{object_index} at ({x}, {y}) - W: {w}, H: {h}, Area: {area:.2f}, "
                    f"Blue Intensity: {blue_intensity:.2f}, Size: {size_category}"
                )
                object_index += 1

        if not dimensions:
            dimensions.append("No blue objects detected.")

        self.display_image(image)

        total_objects = count_large + count_medium + count_small
        summary = (
            f"Total Objects: {total_objects}\n"
            f"Large Objects: {count_large}\n"
            f"Medium Objects: {count_medium}\n"
            f"Small Objects: {count_small}\n"
        )

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
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatio
        )
        self.image_label.setPixmap(scaled_pixmap)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageProcessor()
    window.show()
    sys.exit(app.exec())
