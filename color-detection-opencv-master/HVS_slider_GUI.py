import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QFileDialog,
    QVBoxLayout, QHBoxLayout, QSlider, QTextEdit, QGroupBox, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage


class HSVSlider(QWidget):
    def __init__(self, label, min_val, max_val, init_val):
        super().__init__()
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(min_val, max_val)
        self.slider.setValue(init_val)
        self.label = QLabel(f"{label}: {init_val}")
        self.slider.valueChanged.connect(self.update_label)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        self.setLayout(layout)

    def update_label(self, val):
        text = self.label.text().split(":")[0]
        self.label.setText(f"{text}: {val}")

    def value(self):
        return self.slider.value()


class ImageProcessor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HSV Blue Detector with Sliders")

        self.image_label = QLabel("Load an image to begin")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_box = QTextEdit()
        self.text_box.setFixedHeight(100)

        # Buttons
        self.open_button = QPushButton("Open Image")
        self.save_button = QPushButton("Save Result")
        self.exit_button = QPushButton("Exit")
        self.open_button.clicked.connect(self.open_image)
        self.save_button.clicked.connect(self.save_result)
        self.exit_button.clicked.connect(self.close)

        # HSV sliders
        self.hsv_sliders = {
            'Lower H': HSVSlider("Lower H", 0, 179, 90),
            'Lower S': HSVSlider("Lower S", 0, 255, 50),
            'Lower V': HSVSlider("Lower V", 0, 255, 50),
            'Upper H': HSVSlider("Upper H", 0, 179, 130),
            'Upper S': HSVSlider("Upper S", 0, 255, 255),
            'Upper V': HSVSlider("Upper V", 0, 255, 255),
        }

        slider_group = QGroupBox("HSV Range")
        slider_layout = QGridLayout()
        for i, key in enumerate(self.hsv_sliders):
            slider_layout.addWidget(self.hsv_sliders[key], i // 2, i % 2)
        slider_group.setLayout(slider_layout)

        # Layouts
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(slider_group)
        layout.addWidget(self.text_box)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.open_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.exit_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.resize(1000, 800)

        self.original_image = None
        self.annotated_image = None

        for slider in self.hsv_sliders.values():
            slider.slider.valueChanged.connect(self.update_mask)

    def open_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.jpg *.jpeg *.png *.bmp)")
        if file_name:
            image = cv2.imread(file_name)
            if image is None:
                self.text_box.setText("Failed to load image.")
                return

            # Rotate image 90 degrees anticlockwise
            self.original_image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
            self.update_mask()

    def save_result(self):
        if self.annotated_image is not None:
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG (*.png);;JPEG (*.jpg)")
            if file_name:
                cv2.imwrite(file_name, self.annotated_image)
                self.text_box.append("Image saved.")
        else:
            self.text_box.setText("No result to save.")

    def update_mask(self):
        if self.original_image is None:
            return

        image = self.original_image.copy()
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        lower = np.array([
            self.hsv_sliders['Lower H'].value(),
            self.hsv_sliders['Lower S'].value(),
            self.hsv_sliders['Lower V'].value()
        ])
        upper = np.array([
            self.hsv_sliders['Upper H'].value(),
            self.hsv_sliders['Upper S'].value(),
            self.hsv_sliders['Upper V'].value()
        ])

        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        dimensions = []
        count_large, count_medium, count_small = 0, 0, 0
        index = 1

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 500:
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                label = f"Obj #{index}"

                cv2.putText(image, label, (x, max(y - 10, 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                blue_intensity = np.mean(image[y:y + h, x:x + w, 0])
                size = "Large" if area > 25000 else "Medium" if area > 5000 else "Small"

                if size == "Large":
                    count_large += 1
                elif size == "Medium":
                    count_medium += 1
                else:
                    count_small += 1

                dimensions.append(f"{label}: W={w}, H={h}, Area={area:.0f}, Blue Intensity={blue_intensity:.1f}, Size={size}")
                index += 1

        summary = (f"\nTotal: {count_large + count_medium + count_small} | "
                   f"Large: {count_large}, Medium: {count_medium}, Small: {count_small}")

        self.annotated_image = image
        self.display_image(image)
        self.text_box.setText("\n".join(dimensions + [summary]))

    def display_image(self, image):
        height, width, _ = image.shape
        qimg = QImage(image.data, width, height, 3 * width, QImage.Format.Format_BGR888)
        pixmap = QPixmap.fromImage(qimg).scaled(
            self.image_label.width(), self.image_label.height(),
            Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setPixmap(pixmap)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageProcessor()
    window.show()
    sys.exit(app.exec())
