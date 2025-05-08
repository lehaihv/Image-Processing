import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QTextEdit, QFileDialog
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt


class BlueObjectDetector(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blue Object Detector")
        self.setGeometry(100, 100, 800, 600)

        # Image display (centered in window)
        self.image_label = QLabel("Image will appear here")
        self.image_label.setFixedSize(600, 400)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid gray;")

        # Text box for object counts with custom style
        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        self.result_box.setFixedHeight(80)
        self.result_box.setStyleSheet("background-color: #f0f0f0; color: green; font-size: 14px;")

        # Buttons
        open_button = QPushButton("Open Image")
        open_button.clicked.connect(self.open_image)

        exit_button = QPushButton("Exit")
        exit_button.clicked.connect(self.close)

        # Layouts
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(open_button)
        button_layout.addWidget(exit_button)
        button_layout.addStretch()

        # Main layout (center the image label, result box, and buttons)
        main_layout = QVBoxLayout()
        main_layout.addStretch()  # Add stretch to center content vertically
        main_layout.addWidget(self.image_label)
        main_layout.addWidget(self.result_box)
        main_layout.addLayout(button_layout)
        main_layout.addStretch()  # Ensure button layout is centered as well

        # Center everything horizontally
        center_widget = QWidget()
        center_widget.setLayout(main_layout)
        center_layout = QVBoxLayout()
        center_layout.addWidget(center_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(center_layout)

    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            result_img, small, large = self.detect_blue_objects(file_path)
            self.show_image(result_img)
            self.result_box.setText(f"Small objects: {small}\nLarge objects: {large}")

    def detect_blue_objects(self, path):
        image = cv2.imread(path)
        if image is None:
            return None, 0, 0

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower_blue = np.array([100, 150, 50])
        upper_blue = np.array([140, 255, 255])
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        small_count = 0
        large_count = 0

        for contour in contours:
            if cv2.contourArea(contour) > 500:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(image, f"{w}x{h}px", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                            0.6, (0, 255, 0), 2)
                if w < 150:
                    small_count += 1
                else:
                    large_count += 1

        return image, small_count, large_count

    def show_image(self, image):
        if image is None:
            self.image_label.setText("Failed to load image.")
            return

        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width, channels = rgb_image.shape
        bytes_per_line = channels * width

        q_image = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)

        # Scale pixmap while maintaining aspect ratio
        scaled_pixmap = pixmap.scaled(self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        # Center the image inside the label
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Ensure the image stays centered


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BlueObjectDetector()
    window.show()
    sys.exit(app.exec())
