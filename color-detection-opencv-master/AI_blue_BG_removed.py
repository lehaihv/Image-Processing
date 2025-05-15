import sys
import cv2
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QTextEdit,
    QVBoxLayout, QHBoxLayout, QFileDialog, QSizePolicy
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt


class ImageApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blue Object Detector")
        self.resize(1200, 800)

        # Image label (expandable)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("background-color: lightgray; border: 1px solid black;")
        self.image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Blank placeholder image
        placeholder = QPixmap(800, 500)
        placeholder.fill(Qt.GlobalColor.lightGray)
        self.image_label.setPixmap(placeholder)

        # Text box (expandable width, fixed height ~5 lines)
        self.text_box = QTextEdit()
        self.text_box.setReadOnly(True)
        self.text_box.setStyleSheet("background-color: gray; color: green;")
        self.text_box.setFixedHeight(100)
        #self.text_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.text_box.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Buttons
        self.open_button = QPushButton("Open Image")
        self.exit_button = QPushButton("Exit")
        self.open_button.clicked.connect(self.open_image)
        self.exit_button.clicked.connect(self.close)

        # Layouts
        image_layout = QHBoxLayout()
        image_layout.addStretch()
        image_layout.addWidget(self.image_label)
        image_layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.open_button)
        button_layout.addWidget(self.exit_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(image_layout)
        main_layout.addWidget(self.text_box)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg)")
        if file_path:
            self.process_image(file_path)

    def process_image(self, path):
        image = cv2.imread(path)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        small_count = 0
        large_count = 0
        details = []  # ← must reset this list

        # Blue color range in HSV
        lower_blue = (100, 100, 50)
        upper_blue = (140, 255, 255)

        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        small_count = large_count = 0
        details = []

        for i, cnt in enumerate(contours):
            x, y, w, h = cv2.boundingRect(cnt)
            if w > 10 and h > 10:
                roi = image[y:y + h, x:x + w]
                avg_blue = int(roi[:, :, 0].mean())

                cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
                label = f"{w}x{h} | B:{avg_blue}"
                cv2.putText(image, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

                details.append(f"Obj{i+1}: {w}×{h}, B={avg_blue}")
                print(f"Object {i+1}: Width={w}, Height={h}, Avg Blue Intensity={avg_blue}")
                if 100 < w < 150: small_count += 1
                else:        large_count += 1

        # Display image
        h, w, _ = image.shape
        qimg = QImage(image.data, w, h, 3 * w, QImage.Format.Format_BGR888)
        pixmap = QPixmap.fromImage(qimg)
        self.image_label.setPixmap(pixmap.scaled(
            self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        ))

        # Update text box
        summary = "\n".join(details)  # Show up to last 5 objects [-5:]
        summary += f"\nSmall: {small_count}  Large: {large_count}  Total: {small_count + large_count}"
        self.text_box.setText(summary)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageApp()
    window.show()
    sys.exit(app.exec())
