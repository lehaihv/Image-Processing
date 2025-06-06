import sys
import cv2
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog
)
from PyQt6.QtGui import QPixmap, QImage
from ultralytics import YOLO
import numpy as np

# Function to get class colors
def getColours(cls_num):
    base_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    color_index = cls_num % len(base_colors)
    increments = [(1, -2, 1), (-2, 1, -1), (1, -1, 2)]
    color = [base_colors[color_index][i] + increments[color_index][i] *
             (cls_num // len(base_colors)) % 256 for i in range(3)]
    return tuple(color)

class YOLOApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YOLOv8 Object Detection")
        self.layout = QVBoxLayout()
        self.button = QPushButton("Select Image")
        self.button.clicked.connect(self.open_image)
        self.image_label = QLabel("No image loaded.")
        self.image_label.setScaledContents(True)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.image_label)
        self.setLayout(self.layout)
        self.yolo = YOLO('yolov8s.pt')
        self.max_width = 800
        self.max_height = 600

    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        if file_path:
            frame = cv2.imread(file_path)
            if frame is None:
                self.image_label.setText("Failed to load image.")
                return

            results = self.yolo(frame)
            for result in results:
                classes_names = result.names
                for box in result.boxes:
                    if box.conf[0] > 0.4:
                        [x1, y1, x2, y2] = box.xyxy[0]
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                        cls = int(box.cls[0])
                        class_name = classes_names[cls]
                        colour = getColours(cls)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), colour, 2)
                        cv2.putText(
                            frame,
                            f'{class_name} {box.conf[0]:.2f}',
                            (x1, y1),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            colour,
                            2
                        )

            # Convert BGR to RGB for Qt
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape

            # Scale image if it's too large
            scale = min(self.max_width / w, self.max_height / h, 1.0)
            new_w, new_h = int(w * scale), int(h * scale)
            if scale < 1.0:
                rgb_image = cv2.resize(rgb_image, (new_w, new_h), interpolation=cv2.INTER_AREA)
                w, h = new_w, new_h

            bytes_per_line = 3 * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            self.image_label.setPixmap(pixmap)
            self.resize(w, h + 50)  # Add space for the button

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YOLOApp()
    window.show()
    sys.exit(app.exec())