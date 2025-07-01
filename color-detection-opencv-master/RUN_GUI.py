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
import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
from statsmodels.nonparametric.smoothers_lowess import lowess

class ImageProcessor(QWidget):
    def __init__(self):
        super().__init__()

        self.text_box = QTextEdit(self)
        self.open_button = QPushButton("Open Images", self)
        self.save_button = QPushButton("Save Last Image", self)
        self.save_csv_button = QPushButton("Save Light Intensity CSV", self)
        self.plot_button = QPushButton("Plot Light Intensity", self)
        self.exit_button = QPushButton("Exit", self)

        self.annotated_images = []
        self.image_labels = []
        self.light_intensity_data = []
        self.input_image_dir = ""
        self.roi = None

        self.open_button.clicked.connect(self.open_images)
        self.save_button.clicked.connect(self.save_image)
        self.save_csv_button.clicked.connect(self.save_csv)
        self.plot_button.clicked.connect(self.plot_light_intensity)
        self.exit_button.clicked.connect(self.close)

        layout = QVBoxLayout()
        self.scroll_area = QScrollArea(self)
        self.scroll_widget = QWidget()
        self.grid_layout = QGridLayout(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_widget)
        layout.addWidget(self.scroll_area)

        # Set text box height to about 5 lines
        self.text_box.setFixedHeight(90)  # ~5 lines depending on font size
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

        screen = QApplication.primaryScreen().availableGeometry()
        self.window_width = int(screen.width() * 0.75)
        self.window_height = int(screen.height() * 0.75)
        self.resize(self.window_width, self.window_height)

    def open_images(self):
        file_names, _ = QFileDialog.getOpenFileNames(
            self, "Open Image Files", "", "Images (*.png *.xpm *.jpg *.jpeg *.bmp)"
        )
        if file_names:
            self.input_image_dir = os.path.dirname(file_names[0])
            self.annotated_images.clear()
            self.text_box.clear()
            self.light_intensity_data.clear()
            self.roi = None

            for label in self.image_labels:
                self.grid_layout.removeWidget(label)
                label.deleteLater()
            self.image_labels.clear()

            all_dimensions = []
            all_summaries = []
            for idx, file_name in enumerate(file_names):
                annotated_img, dimensions, summary, intensities = self.process_image(file_name, idx + 1)
                if annotated_img is not None:
                    self.annotated_images.append(annotated_img)
                    all_dimensions.extend(dimensions)
                    all_summaries.append(f"Image {idx + 1}: {summary.strip()}")
                    self.light_intensity_data.extend(intensities)
            self.display_images(self.annotated_images)
            self.text_box.append("\n".join(all_dimensions))
            self.text_box.append("\n".join(all_summaries))

    def save_image(self):
        if self.annotated_images:
            filename, selected_filter = QFileDialog.getSaveFileName(
                self, "Save Image", "", "PNG Files (*.png);;JPEG Files (*.jpg)"
            )
            if filename:
                if not (filename.lower().endswith('.png') or filename.lower().endswith('.jpg')):
                    if "PNG" in selected_filter:
                        filename += ".png"
                    else:
                        filename += ".jpg"
                pixmap = self.scroll_widget.grab()
                pixmap.save(filename)
                self.text_box.append(f"Saved subplot image to {filename}")
        else:
            self.text_box.append("No image to save.")

    def save_csv(self):
        if not self.light_intensity_data:
            self.text_box.append("No light intensity data to save.")
            return

        # Prepare data for LOESS smoothing
        y_intensity = []
        y_r = []
        y_g = []
        y_b = []
        y_h = []
        y_s = []
        y_v = []

        for _, roi_idx, blue_intensity, avg_h, avg_s, avg_v, avg_r, avg_g, avg_b in self.light_intensity_data:
            y_intensity.append(blue_intensity)
            y_h.append(avg_h)
            y_s.append(avg_s)
            y_v.append(avg_v)
            y_r.append(avg_r)
            y_g.append(avg_g)
            y_b.append(avg_b)

        # Apply LOESS smoothing
        loess_intensity = lowess(y_intensity, np.arange(len(y_intensity)), frac=0.3)
        loess_r = lowess(y_r, np.arange(len(y_r)), frac=0.3)
        loess_g = lowess(y_g, np.arange(len(y_g)), frac=0.3)
        loess_b = lowess(y_b, np.arange(len(y_b)), frac=0.3)
        loess_h = lowess(y_h, np.arange(len(y_h)), frac=0.3)
        loess_s = lowess(y_s, np.arange(len(y_s)), frac=0.3)
        loess_v = lowess(y_v, np.arange(len(y_v)), frac=0.3)

        default_path = os.path.join(self.input_image_dir if self.input_image_dir else "", "roi_stats.csv")
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save CSV", default_path, "CSV Files (*.csv)"
        )
        if filename:
            with open(filename, mode='w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    "Image Index", "ROI Index", "Blue Intensity",
                    "Avg H", "Avg S", "Avg V", "Avg R", "Avg G", "Avg B",
                    "LOESS Blue Intensity", "LOESS Avg H", "LOESS Avg S",
                    "LOESS Avg V", "LOESS Avg R", "LOESS Avg G", "LOESS Avg B"
                ])
                for idx, row in enumerate(self.light_intensity_data):
                    loess_row = [
                        loess_intensity[idx][1],
                        loess_h[idx][1],
                        loess_s[idx][1],
                        loess_v[idx][1],
                        loess_r[idx][1],
                        loess_g[idx][1],
                        loess_b[idx][1]
                    ]
                    writer.writerow(list(row) + loess_row)
            self.text_box.append(f"Saved ROI stats data to {filename}")

    def plot_light_intensity(self):
        small_interval = 20
        large_interval = 50
        if not self.light_intensity_data:
            self.text_box.append("No ROI stats data to plot.")
            return

        # Prepare data
        num_rois = len(self.light_intensity_data)
        y_intensity = []
        y_r = []
        y_g = []
        y_b = []
        y_h = []
        y_s = []
        y_v = []

        # Collect raw data
        for img_idx, roi_idx, blue_intensity, avg_h, avg_s, avg_v, avg_r, avg_g, avg_b in self.light_intensity_data:
            y_intensity.append(blue_intensity)
            y_r.append(avg_r)
            y_g.append(avg_g)
            y_b.append(avg_b)
            y_h.append(avg_h)
            y_s.append(avg_s)
            y_v.append(avg_v)

        # X-axis labels as numbers
        x_labels = list(range(1, num_rois + 1))

        # Apply LOESS smoothing
        loess_intensity = lowess(y_intensity, np.arange(len(y_intensity)), frac=0.3)
        loess_r = lowess(y_r, np.arange(len(y_r)), frac=0.3)
        loess_g = lowess(y_g, np.arange(len(y_g)), frac=0.3)
        loess_b = lowess(y_b, np.arange(len(y_b)), frac=0.3)
        loess_h = lowess(y_h, np.arange(len(y_h)), frac=0.3)
        loess_s = lowess(y_s, np.arange(len(y_s)), frac=0.3)
        loess_v = lowess(y_v, np.arange(len(y_v)), frac=0.3)

        # Set x-axis limits
        x_limit = num_rois + small_interval

        # Plot 1: Blue Light Intensity
        plt.figure()
        plt.subplot(2, 1, 1)
        plt.plot(x_labels, y_intensity, marker='o', color='blue', label='Raw Blue Intensity')
        plt.xlabel("ROI Number")
        plt.ylabel("Blue Intensity")
        plt.title("Blue Light Intensity - Raw Data")
        plt.xticks(np.arange(0, x_limit, small_interval))
        plt.xlim(0, x_limit)
        plt.ylim(0, 255)
        plt.legend()
        plt.grid()

        plt.subplot(2, 1, 2)
        plt.plot(x_labels, loess_intensity[:, 1], color='blue', label='LOESS Smoothed Blue Intensity')
        plt.xlabel("ROI Number")
        plt.ylabel("Blue Intensity")
        plt.title("Blue Light Intensity - LOESS Smoothed")
        plt.xticks(np.arange(0, x_limit, small_interval))
        plt.xlim(0, x_limit)
        plt.ylim(0, 255)
        plt.legend()
        plt.grid()

        plt.tight_layout()
        plt.show(block=False)
        plt.pause(0.1)

        # Plot 2: Average RGB
        plt.figure(figsize=(12, 8))

        # Raw RGB data
        plt.subplot(2, 3, 1)
        plt.plot(x_labels, y_r, marker='o', color='red', label='Raw Avg R')
        plt.xlabel("ROI Number")
        plt.ylabel("Average R")
        plt.title("Raw Avg R")
        plt.xticks(np.arange(0, x_limit, large_interval))
        plt.xlim(0, x_limit)
        plt.ylim(0, 255)
        plt.grid()

        plt.subplot(2, 3, 2)
        plt.plot(x_labels, y_g, marker='o', color='green', label='Raw Avg G')
        plt.xlabel("ROI Number")
        plt.ylabel("Average G")
        plt.title("Raw Avg G")
        plt.xticks(np.arange(0, x_limit, large_interval))
        plt.xlim(0, x_limit)
        plt.ylim(0, 255)
        plt.grid()

        plt.subplot(2, 3, 3)
        plt.plot(x_labels, y_b, marker='o', color='blue', label='Raw Avg B')
        plt.xlabel("ROI Number")
        plt.ylabel("Average B")
        plt.title("Raw Avg B")
        plt.xticks(np.arange(0, x_limit, large_interval))
        plt.xlim(0, x_limit)
        plt.ylim(0, 255)
        plt.grid()

        # LOESS Smoothed RGB data
        plt.subplot(2, 3, 4)
        plt.plot(x_labels, loess_r[:, 1], color='darkred', label='LOESS Smoothed Avg R')
        plt.xlabel("ROI Number")
        plt.ylabel("Average R")
        plt.title("LOESS Smoothed Avg R")
        plt.xticks(np.arange(0, x_limit, large_interval))
        plt.xlim(0, x_limit)
        plt.ylim(0, 255)
        plt.grid()

        plt.subplot(2, 3, 5)
        plt.plot(x_labels, loess_g[:, 1], color='darkgreen', label='LOESS Smoothed Avg G')
        plt.xlabel("ROI Number")
        plt.ylabel("Average G")
        plt.title("LOESS Smoothed Avg G")
        plt.xticks(np.arange(0, x_limit, large_interval))
        plt.xlim(0, x_limit)
        plt.ylim(0, 255)
        plt.grid()

        plt.subplot(2, 3, 6)
        plt.plot(x_labels, loess_b[:, 1], color='darkblue', label='LOESS Smoothed Avg B')
        plt.xlabel("ROI Number")
        plt.ylabel("Average B")
        plt.title("LOESS Smoothed Avg B")
        plt.xticks(np.arange(0, x_limit, large_interval))
        plt.xlim(0, x_limit)
        plt.ylim(0, 255)
        plt.grid()

        plt.tight_layout()
        plt.show(block=False)
        plt.pause(0.1)

        # Plot 3: Average HSV
        """ plt.figure(figsize=(12, 8))

        # Raw HSV data
        plt.subplot(2, 3, 1)
        plt.plot(x_labels, y_h, marker='o', color='red', label='Raw Avg H')
        plt.xlabel("ROI Number")
        plt.ylabel("Average H")
        plt.title("Raw Avg H")
        plt.xticks(np.arange(0, x_limit, large_interval))
        plt.xlim(0, x_limit)
        plt.ylim(0, 255)
        plt.grid()

        plt.subplot(2, 3, 2)
        plt.plot(x_labels, y_s, marker='o', color='green', label='Raw Avg S')
        plt.xlabel("ROI Number")
        plt.ylabel("Average S")
        plt.title("Raw Avg S")
        plt.xticks(np.arange(0, x_limit, large_interval))
        plt.xlim(0, x_limit)
        plt.ylim(0, 255)
        plt.grid()

        plt.subplot(2, 3, 3)
        plt.plot(x_labels, y_v, marker='o', color='blue', label='Raw Avg V')
        plt.xlabel("ROI Number")
        plt.ylabel("Average V")
        plt.title("Raw Avg V")
        plt.xticks(np.arange(0, x_limit, large_interval))
        plt.xlim(0, x_limit)
        plt.ylim(0, 255)
        plt.grid()

        # LOESS Smoothed HSV data
        plt.subplot(2, 3, 4)
        plt.plot(x_labels, loess_h[:, 1], color='darkred', label='LOESS Smoothed Avg H')
        plt.xlabel("ROI Number")
        plt.ylabel("Average H")
        plt.title("LOESS Smoothed Avg H")
        plt.xticks(np.arange(0, x_limit, large_interval))
        plt.xlim(0, x_limit)
        plt.ylim(0, 255)
        plt.grid()

        plt.subplot(2, 3, 5)
        plt.plot(x_labels, loess_s[:, 1], color='darkgreen', label='LOESS Smoothed Avg S')
        plt.xlabel("ROI Number")
        plt.ylabel("Average S")
        plt.title("LOESS Smoothed Avg S")
        plt.xticks(np.arange(0, x_limit, large_interval))
        plt.xlim(0, x_limit)
        plt.ylim(0, 255)
        plt.grid()

        plt.subplot(2, 3, 6)
        plt.plot(x_labels, loess_v[:, 1], color='darkblue', label='LOESS Smoothed Avg V')
        plt.xlabel("ROI Number")
        plt.ylabel("Average V")
        plt.title("LOESS Smoothed Avg V")
        plt.xticks(np.arange(0, x_limit, large_interval))
        plt.xlim(0, x_limit)
        plt.ylim(0, 255)
        plt.grid()

        plt.tight_layout()
        plt.show(block=False) """

    def process_image(self, file_name, image_idx):
        image = cv2.imread(file_name)
        if image is None:
            print(f"Error: Could not open image {file_name}.")
            return None, [], "", []

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Fixed ROI selection for the first image
        #self.roi = (30, 440, 275, 150)      # Uncomment to use fixed ROI 1
        #self.roi = (374, 441, 275, 150)    # Uncomment to use fixed ROI 2       
        #self.roi = (712, 443, 275, 150)    # Uncomment to use fixed ROI 3

        if self.roi is None:
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
            x, y, w, h = [int(v / scale) for v in roi_disp]
            self.roi = (x, y, w, h)
            self.text_box.append(f"ROI coordinates for 1st image: x={x}, y={y}, w={w}, h={h}")

        x, y, w, h = self.roi
        roi_bgr = image[y:y + h, x:x + w]
        roi_hsv = hsv[y:y + h, x:x + w]

        annotated_image = image.copy()
        cv2.rectangle(annotated_image, (x, y), (x + w, y + h), (0, 255, 0), 2)

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
        for label in self.image_labels:
            self.grid_layout.removeWidget(label)
            label.deleteLater()
        self.image_labels.clear()

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