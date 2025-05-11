import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QTextEdit,
    QVBoxLayout, QHBoxLayout, QFileDialog
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt


class ImageApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Green Object Detector with Background Removal")

        # Image labels
        self.image_label = QLabel("Detected Objects")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.bg_removed_label = QLabel("Background Removed")
        self.bg_removed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Text box
        self.text_box = QTextEdit()
        self.text_box.setReadOnly(True)
        self.text_box.setStyleSheet("background-color: gray; color: green;")

        # Buttons
        self.open_button = QPushButton("Open Image")
        self.exit_button = QPushButton("Exit")

        self.open_button.clicked.connect(self.open_image)
        self.exit_button.clicked.connect(self.close)

        # Layouts
        image_layout = QVBoxLayout()
        image_layout.addWidget(self.image_label)
        image_layout.addWidget(self.bg_removed_label)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.open_button)
        button_layout.addWidget(self.exit_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(image_layout)
        main_layout.addWidget(self.text_box, alignment=Qt.AlignmentFlag.AlignHCenter)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg)")
        if file_path:
            self.process_image(file_path)

    def remove_background(self, image):
        mask = np.zeros(image.shape[:2], np.uint8)
        rect = (10, 10, image.shape[1] - 20, image.shape[0] - 20)
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)

        cv2.grabCut(image, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)
        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype("uint8")
        result = image * mask2[:, :, np.newaxis]
        return result

    def process_image(self, path):
        image = cv2.imread(path)
        image_no_bg = self.remove_background(image)
        hsv = cv2.cvtColor(image_no_bg, cv2.COLOR_BGR2HSV)

        # Green color range in HSV
        lower_green = (35, 40, 40)
        upper_green = (85, 255, 255)

        mask = cv2.inRange(hsv, lower_green, upper_green)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        small_count = 0
        large_count = 0
        print("\nDetected green objects:")

        for i, cnt in enumerate(contours):
            x, y, w, h = cv2.boundingRect(cnt)
            if w > 10 and h > 10:
                roi = image_no_bg[y:y + h, x:x + w]
                avg_green = int(roi[:, :, 1].mean())

                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                label = f"{w}x{h} | G:{avg_green}"
                cv2.putText(image, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (255, 255, 255), 1)

                print(f"Object {i + 1}: Width={w}, Height={h}, Avg Green Intensity={avg_green}")

                if w < 150:
                    small_count += 1
                else:
                    large_count += 1

        # Convert and display result image
        self.set_label_pixmap(self.image_label, image)
        self.set_label_pixmap(self.bg_removed_label, image_no_bg)

        # Update textbox
        count_summary = f"Small objects: {small_count}\nLarge objects: {large_count}\nTotal: {small_count + large_count}"
        self.text_box.setText(count_summary)

    def set_label_pixmap(self, label, image):
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        qimg = QImage(image.data, width, height, bytes_per_line, QImage.Format.Format_BGR888)
        pixmap = QPixmap.fromImage(qimg)
        label.setPixmap(pixmap.scaled(
            500, 350, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageApp()
    window.resize(700, 800)
    window.show()
    sys.exit(app.exec())
