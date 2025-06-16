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
        self.light_intensity_data = []  # Store tuples: (image_idx, object_idx, blue_intensity, avg_h, avg_s, avg_v, avg_r, avg_g, avg_b)
        self.input_image_dir = ""  # Store directory of first input image
        self.roi = None  # Store selected ROI

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
        self.setWindowTitle("ROI Stats - Multiple Images")

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
            self.roi = None
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
        # Save the entire grid of images (all subplots), not just the visible part
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
                # Grab the entire scroll_widget (the full grid), not just the visible area
                pixmap = self.scroll_widget.grab()
                pixmap.save(filename)
                self.text_box.append(f"Saved subplot image to {filename}")
        else:
            self.text_box.append("No image to save.")

    def save_csv(self):
        if not self.light_intensity_data:
            self.text_box.append("No light intensity data to save.")
            return
        # Set default path to input image directory
        default_path = os.path.join(self.input_image_dir if self.input_image_dir else "", "roi_stats.csv")
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save CSV", default_path, "CSV Files (*.csv)"
        )
        if filename:
            with open(filename, mode='w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    "Image Index", "ROI Index", "Blue Intensity",
                    "Avg H", "Avg S", "Avg V", "Avg R", "Avg G", "Avg B"
                ])
                for row in self.light_intensity_data:
                    writer.writerow(row)
            self.text_box.append(f"Saved ROI stats data to {filename}")

    def plot_light_intensity(self):
        if not self.light_intensity_data:
            self.text_box.append("No ROI stats data to plot.")
            return

        x_labels = []
        y_intensity = []
        y_h = []
        y_s = []
        y_v = []
        y_r = []
        y_g = []
        y_b = []
        for img_idx, roi_idx, blue_intensity, avg_h, avg_s, avg_v, avg_r, avg_g, avg_b in self.light_intensity_data:
            x_labels.append(f"Img{img_idx}-ROI{roi_idx}")
            y_intensity.append(blue_intensity)
            y_h.append(avg_h)
            y_s.append(avg_s)
            y_v.append(avg_v)
            y_r.append(avg_r)
            y_g.append(avg_g)
            y_b.append(avg_b)

        # Plot 1: Light Intensity
        plt.figure(figsize=(self.window_width / 100, self.window_height / 100))
        plt.plot(x_labels, y_intensity, marker='o', color='blue', label='Blue Intensity')
        plt.xlabel("Detected ROI")
        plt.ylabel("Blue Intensity")
        plt.title("Light Intensity of Selected ROI")
        plt.xticks(rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()
        plt.show(block=False)

        # Plot 2: Average HSV
        plt.figure(figsize=(self.window_width / 100, self.window_height / 100))
        plt.plot(x_labels, y_h, marker='o', color='orange', label='Avg H')
        plt.plot(x_labels, y_s, marker='o', color='purple', label='Avg S')
        plt.plot(x_labels, y_v, marker='o', color='black', label='Avg V')
        plt.xlabel("Detected ROI")
        plt.ylabel("HSV Value")
        plt.title("Average HSV of Selected ROI")
        plt.xticks(rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()
        plt.show(block=False)

        # Plot 3: Average RGB
        plt.figure(figsize=(self.window_width / 100, self.window_height / 100))
        plt.plot(x_labels, y_r, marker='o', color='red', label='Avg R')
        plt.plot(x_labels, y_g, marker='o', color='green', label='Avg G')
        plt.plot(x_labels, y_b, marker='o', color='blue', label='Avg B')
        plt.xlabel("Detected ROI")
        plt.ylabel("RGB Value")
        plt.title("Average RGB of Selected ROI")
        plt.xticks(rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()
        plt.show(block=False)

    def process_image(self, file_name, image_idx):
        image = cv2.imread(file_name)
        if image is None:
            print(f"Error: Could not open image {file_name}.")
            return None, [], "", []

        # rotate 90 degrees anticlockwise
        image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Select ROI on the first image only
        if self.roi is None:
            # Resize image for ROI selection
            gui_w, gui_h = self.window_width, self.window_height
            img_h, img_w = image.shape[:2]
            scale_w = gui_w / img_w
            scale_h = gui_h / img_h
            scale = min(scale_w, scale_h)
            disp_w, disp_h = int(img_w * scale), int(img_h * scale)
            image_disp = cv2.resize(image, (disp_w, disp_h), interpolation=cv2.INTER_AREA)

            roi_disp = cv2.selectROI("Select ROI", image_disp, showCrosshair=True, fromCenter=False)
            cv2.destroyWindow("Select ROI")
            if roi_disp == (0, 0, 0, 0):
                self.text_box.append("No ROI selected.")
                return None, [], "", []
            # Map ROI back to original image coordinates
            x_disp, y_disp, w_disp, h_disp = roi_disp
            x = int(x_disp / scale)
            y = int(y_disp / scale)
            w = int(w_disp / scale)
            h = int(h_disp / scale)
            self.roi = (x, y, w, h)
            # Print ROI coordinates and top-left (x, y) in the text box for the first image
            self.text_box.append(f"ROI coordinates for 1st image: x={x}, y={y}, w={w}, h={h}")
            self.text_box.append(f"Top-left (x, y) of ROI: ({x}, {y})")
        x, y, w, h = self.roi
        roi_bgr = image[y:y + h, x:x + w]
        roi_hsv = hsv[y:y + h, x:x + w]

        # Draw rectangle on the image for display
        annotated_image = image.copy()
        cv2.rectangle(annotated_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        label_text = f"ROI"
        font_scale = 1.5
        thickness = 2
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size, _ = cv2.getTextSize(label_text, font, font_scale, thickness)
        text_width, text_height = text_size
        text_x = x + (w - text_width) // 2
        text_y = max(y - 10, text_height + 5)
        cv2.putText(
            annotated_image, label_text, (text_x, text_y),
            font, font_scale, (0, 255, 0), thickness, cv2.LINE_AA
        )

        blue_intensity = np.mean(roi_bgr[:, :, 0])
        avg_h = np.mean(roi_hsv[:, :, 0])
        avg_s = np.mean(roi_hsv[:, :, 1])
        avg_v = np.mean(roi_hsv[:, :, 2])
        avg_r = np.mean(roi_bgr[:, :, 2])
        avg_g = np.mean(roi_bgr[:, :, 1])
        avg_b = np.mean(roi_bgr[:, :, 0])

        intensities = [(image_idx, 1, blue_intensity, avg_h, avg_s, avg_v, avg_r, avg_g, avg_b)]

        dimensions = [
            f"ROI: W: {w}, H: {h}, "
            f"Light Intensity: {blue_intensity:.2f}, "
            f"HSV: ({avg_h:.1f}, {avg_s:.1f}, {avg_v:.1f}), "
            f"RGB: ({avg_r:.1f}, {avg_g:.1f}, {avg_b:.1f})"
        ]
        summary = f"ROI Stats for Image {image_idx}"

        return annotated_image, dimensions, summary, intensities

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