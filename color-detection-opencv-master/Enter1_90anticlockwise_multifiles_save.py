import sys
import cv2
import numpy as np
import csv
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QTextEdit, QFileDialog, QScrollArea, QGridLayout, QSizePolicy
)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt
import matplotlib.pyplot as plt

class ImageProcessor(QWidget):
    def __init__(self):
        super().__init__()

        self.text_box = QTextEdit(self)
        self.open_button = QPushButton("Open Images", self)
        self.save_button = QPushButton("Save Last Image", self)
        self.save_csv_button = QPushButton("Save Light Intensity CSV", self)
        self.plot_button = QPushButton("Plot Light Intensity", self)
        self.exit_button = QPushButton("Exit", self)

        self.annotated_images = []  # Store all annotated images
        self.image_labels = []      # Store QLabel widgets for images
        self.light_intensity_data = []  # Store tuples: (image_idx, object_idx, blue_intensity)

        self.input_image_dir = ""  # Store directory of first input image

        # Set button widths
        self.open_button.setFixedWidth(200)
        self.save_button.setFixedWidth(150)
        self.save_csv_button.setFixedWidth(200)
        self.plot_button.setFixedWidth(200)
        self.exit_button.setFixedWidth(50)

        self.open_button.clicked.connect(self.open_images)
        self.save_button.clicked.connect(self.save_image)
        self.save_csv_button.clicked.connect(self.save_csv)
        self.plot_button.clicked.connect(self.plot_light_intensity)
        self.exit_button.clicked.connect(self.close)

        layout = QVBoxLayout()

        # Scroll area for images
        self.scroll_area = QScrollArea(self)
        self.scroll_widget = QWidget()
        self.grid_layout = QGridLayout(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_widget)
        layout.addWidget(self.scroll_area)

        self.text_box.setFixedHeight(100)
        layout.addWidget(self.text_box)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.open_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.save_csv_button)
        button_layout.addWidget(self.plot_button)
        button_layout.addWidget(self.exit_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.setWindowTitle("Blue Object Detector - Multiple Images")

        # Set window size to 3/4 of screen size
        screen = QApplication.primaryScreen().availableGeometry()
        self.window_width = int(screen.width() * 0.75)
        self.window_height = int(screen.height() * 0.75)
        self.resize(self.window_width, self.window_height)

    def open_images(self):
        file_names, _ = QFileDialog.getOpenFileNames(
            self, "Open Image Files", "", "Images (*.png *.xpm *.jpg *.jpeg *.bmp)"
        )
        if file_names:
            self.input_image_dir = os.path.dirname(file_names[0])  # Store directory for CSV default
            self.annotated_images.clear()
            self.text_box.clear()
            self.light_intensity_data.clear()
            # Remove old QLabel widgets from grid
            for label in self.image_labels:
                self.grid_layout.removeWidget(label)
                label.deleteLater()
            self.image_labels.clear()

            all_dimensions = []
            all_summaries = []
            for idx, file_name in enumerate(file_names):
                annotated_img, dimensions, summary, intensities = self.process_image(file_name, idx+1)
                if annotated_img is not None:
                    self.annotated_images.append(annotated_img)
                    all_dimensions.extend(dimensions)
                    all_summaries.append(f"Image {idx+1}: {summary.strip()}")
                    self.light_intensity_data.extend(intensities)
            self.display_images(self.annotated_images)
            self.text_box.append("\n".join(all_dimensions))
            self.text_box.append("\n".join(all_summaries))

    def save_image(self):
        # Save the current scroll area (all images as a subplot) as an image
        if self.annotated_images:
            filename, selected_filter = QFileDialog.getSaveFileName(
                self, "Save Image", "", "PNG Files (*.png);;JPEG Files (*.jpg)"
            )
            if filename:
                # Ensure the filename has a valid extension
                if not (filename.lower().endswith('.png') or filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg')):
                    if "PNG" in selected_filter:
                        filename += ".png"
                    else:
                        filename += ".jpg"
                # Grab the scroll area as a pixmap
                pixmap = self.scroll_area.grab()
                pixmap.save(filename)
                self.text_box.append(f"Saved subplot image to {filename}")
        else:
            self.text_box.append("No image to save.")

    def save_csv(self):
        if not self.light_intensity_data:
            self.text_box.append("No light intensity data to save.")
            return
        # Set default path to input image directory
        default_path = os.path.join(self.input_image_dir if self.input_image_dir else "", "light_intensity.csv")
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save CSV", default_path, "CSV Files (*.csv)"
        )
        if filename:
            with open(filename, mode='w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Image Index", "Object Index", "Light Intensity"])
                for row in self.light_intensity_data:
                    writer.writerow(row)
            self.text_box.append(f"Saved light intensity data to {filename}")

    def plot_light_intensity(self):
        if not self.light_intensity_data:
            self.text_box.append("No light intensity data to plot.")
            return
        # Prepare data for plotting
        x_labels = []
        y_values = []
        for img_idx, obj_idx, intensity in self.light_intensity_data:
            x_labels.append(f"Img{img_idx}-Obj{obj_idx}")
            y_values.append(intensity)
        # Set plot size to match main window size (in inches, assuming 100 dpi)
        plt.figure(figsize=(self.window_width / 100, self.window_height / 100))
        plt.plot(x_labels, y_values, marker='o', color='blue')
        plt.xlabel("Detected Object")
        plt.ylabel("Light Intensity")
        plt.title("Light Intensity of Detected Objects")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()

    def process_image(self, file_name, image_idx):
        image = cv2.imread(file_name)
        if image is None:
            print(f"Error: Could not open image {file_name}.")
            return None, [], "", []

        # rotate 90 degrees anticlockwise
        image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        lower_blue = np.array([90, 200, 180])
        upper_blue = np.array([130, 255, 255])

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
        intensities = []

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 50000:  # Adjusted threshold for larger objects 350000
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

                label_text = f"Object #{object_index}"

                # Centered top label text
                font_scale = 1.5
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
                intensities.append((image_idx, object_index, blue_intensity))

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
                    f"{label_text}: W: {w}, H: {h}, Area: {area:.0f}, Light Intensity: {blue_intensity:.2f}, Size: {size_category}"
                )

                object_index += 1

        total_objects = count_large + count_medium + count_small
        summary = (f"Total Objects: {total_objects} | "
                   f"Large: {count_large} | Medium: {count_medium} | Small: {count_small}")

        return image.copy(), dimensions, summary, intensities

    def display_images(self, images):
        # Remove old QLabel widgets from grid
        for label in self.image_labels:
            self.grid_layout.removeWidget(label)
            label.deleteLater()
        self.image_labels.clear()

        # Display images as thumbnails in a grid
        max_width = self.window_width // 3 - 30
        max_height = self.window_height // 3 - 30
        cols = 3
        for idx, img in enumerate(images):
            height, width, channel = img.shape
            bytes_per_line = 3 * width
            q_image = QImage(img.data, width, height, bytes_per_line, QImage.Format.Format_BGR888)
            pixmap = QPixmap.fromImage(q_image)
            if width > max_width or height > max_height:
                pixmap = pixmap.scaled(
                    max_width, max_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
                )
            label = QLabel()
            label.setPixmap(pixmap)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.grid_layout.addWidget(label, idx // cols, idx % cols)
            self.image_labels.append(label)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageProcessor()
    window.show()
    sys.exit(app.exec())