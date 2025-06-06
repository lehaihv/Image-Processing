import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QTextEdit, QFileDialog
)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt


class ImageProcessor(QWidget):
    def __init__(self):
        super().__init__()

        self.image_label = QLabel(self)
        self.text_box = QTextEdit(self)
        self.open_button = QPushButton("Open Image", self)
        self.save_button = QPushButton("Save Image", self)
        self.exit_button = QPushButton("Exit", self)

        self.annotated_image = None

        # Set button widths
        self.open_button.setFixedWidth(250)
        self.save_button.setFixedWidth(150)
        self.exit_button.setFixedWidth(50)

        self.open_button.clicked.connect(self.open_image)
        self.save_button.clicked.connect(self.save_image)
        self.exit_button.clicked.connect(self.close)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)

        self.text_box.setFixedHeight(100)
        layout.addWidget(self.text_box)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.open_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.exit_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.setWindowTitle("Blue Object Detector")

        # Set window size to 3/4 of screen size
        screen = QApplication.primaryScreen().availableGeometry()
        self.window_width = int(screen.width() * 0.75)
        self.window_height = int(screen.height() * 0.75)
        self.resize(self.window_width, self.window_height)

    def open_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Image File", "", "Images (*.png *.xpm *.jpg *.jpeg *.bmp)"
        )
        if file_name:
            self.process_image(file_name)

    def save_image(self):
        if self.annotated_image is not None:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Save Image", "", "PNG Files (*.png);;JPEG Files (*.jpg)"
            )
            if filename:
                cv2.imwrite(filename, self.annotated_image)
        else:
            self.text_box.append("No image to save.")

    def process_image(self, file_name):
        image = cv2.imread(file_name)
        if image is None:
            print("Error: Could not open image.")
            return

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        """ lower_blue = np.array([100, 150, 180])
        upper_blue = np.array([114, 255, 255]) """

        lower_blue = np.array([90, 200, 180])
        upper_blue = np.array([130, 255, 255])   # upper H: 120 to 130

        """ lower_blue = np.array([90, 30, 180])    np.array([H,S,V])
        Hue(H)	        =100	The color type (blue hues start ~90)	            0 to 179
        Saturation(S)	=150	Color intensity or purity (higher is more vivid)	0 to 255
        Value(V)	    =180	Brightness level (0 = black, 255 = full bright)	    0 to 255

        """
        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        dimensions = []
        count_large = 0
        count_medium = 0
        count_small = 0
        object_index = 1

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 500:
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

                label_text = f"Object #{object_index}"

                # Centered top label text
                font_scale = 1.5  # ~25px font
                thickness = 2
                font = cv2.FONT_HERSHEY_SIMPLEX
                text_size, _ = cv2.getTextSize(label_text, font, font_scale, thickness)
                text_width, text_height = text_size
                text_x = x + (w - text_width) // 2
                text_y = max(y - 10, text_height + 5)

                cv2.putText(
                    image, label_text, (text_x, text_y),
                    font, font_scale, (0, 255, 0), thickness, cv2.LINE_AA
                )

                blue_intensity = np.mean(image[y:y + h, x:x + w, 0])

                if area > 25000:
                    size_category = "Large"
                    count_large += 1
                elif area > 5000:
                    size_category = "Medium"
                    count_medium += 1
                else:
                    size_category = "Small"
                    count_small += 1

                dimensions.append(
                    f"{label_text}: W: {w}, H: {h}, Area: {area:.0f}, Blue Intensity: {blue_intensity:.2f}, Size: {size_category}"
                )

                object_index += 1

        self.annotated_image = image.copy()
        self.display_image(image)

        total_objects = count_large + count_medium + count_small
        summary = (f"\nTotal Objects: {total_objects}\n"
                   f"Large Objects: {count_large}\n"
                   f"Medium Objects: {count_medium}\n"
                   f"Small Objects: {count_small}\n")

        self.text_box.clear()
        self.text_box.append("\n".join(dimensions))
        self.text_box.append(summary)

        for d in dimensions:
            print(d)
        print(summary)

    def display_image(self, image):
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format.Format_BGR888)
        pixmap = QPixmap.fromImage(q_image)

        # Check if image is larger than window size
        max_width = self.window_width - 40  # account for layout margins
        max_height = self.window_height - 200  # account for buttons and text box

        if width > max_width or height > max_height:
            pixmap = pixmap.scaled(
                max_width, max_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )

        self.image_label.setPixmap(pixmap)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageProcessor()
    window.show()
    sys.exit(app.exec())
