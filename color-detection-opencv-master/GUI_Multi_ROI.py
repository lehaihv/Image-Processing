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
        self.rois = []  # Store list of 3 ROIs

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
            self.rois = []  # <-- Reset ROIs so user will be prompted again
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

        num_images = max([img_idx for img_idx, *_ in self.light_intensity_data])
        num_rois = max([roi_idx for _, roi_idx, *_ in self.light_intensity_data])

        # Prepare header
        header = ["Image Index"]
        for roi_idx in range(1, num_rois + 1):
            header += [
                f"ROI{roi_idx} Blue Intensity", f"ROI{roi_idx} Avg H", f"ROI{roi_idx} Avg S",
                f"ROI{roi_idx} Avg V", f"ROI{roi_idx} Avg R", f"ROI{roi_idx} Avg G", f"ROI{roi_idx} Avg B"
            ]

        # Prepare rows
        rows = []
        for img_idx in range(1, num_images + 1):
            row = [img_idx]
            for roi_idx in range(1, num_rois + 1):
                # Find the data for this image and ROI
                found = False
                for entry in self.light_intensity_data:
                    if entry[0] == img_idx and entry[1] == roi_idx:
                        _, _, blue_intensity, avg_h, avg_s, avg_v, avg_r, avg_g, avg_b = entry
                        row += [blue_intensity, avg_h, avg_s, avg_v, avg_r, avg_g, avg_b]
                        found = True
                        break
                if not found:
                    row += [None]*7  # If missing, fill with None
            rows.append(row)

        # Save to CSV
        default_path = os.path.join(self.input_image_dir if self.input_image_dir else "", "roi_stats.csv")
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save CSV", default_path, "CSV Files (*.csv)"
        )
        if filename:
            with open(filename, mode='w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(header)
                for row in rows:
                    writer.writerow(row)
            self.text_box.append(f"Saved ROI stats data to {filename}")

    def plot_light_intensity(self):
        if not self.light_intensity_data:
            self.text_box.append("No ROI stats data to plot.")
            return

        num_images = max([img_idx for img_idx, *_ in self.light_intensity_data])
        num_rois = max([roi_idx for _, roi_idx, *_ in self.light_intensity_data])

        # Prepare data: one list per ROI per channel
        roi_r = [[] for _ in range(num_rois)]
        roi_g = [[] for _ in range(num_rois)]
        roi_b = [[] for _ in range(num_rois)]
        roi_h = [[] for _ in range(num_rois)]
        roi_s = [[] for _ in range(num_rois)]
        roi_v = [[] for _ in range(num_rois)]
        roi_intensities = [[] for _ in range(num_rois)]

        for img_idx in range(1, num_images + 1):
            for roi_idx in range(1, num_rois + 1):
                for entry in self.light_intensity_data:
                    if entry[0] == img_idx and entry[1] == roi_idx:
                        _, _, blue_intensity, avg_h, avg_s, avg_v, avg_r, avg_g, avg_b = entry
                        roi_intensities[roi_idx-1].append(blue_intensity)
                        roi_h[roi_idx-1].append(avg_h)
                        roi_s[roi_idx-1].append(avg_s)
                        roi_v[roi_idx-1].append(avg_v)
                        roi_r[roi_idx-1].append(avg_r)
                        roi_g[roi_idx-1].append(avg_g)
                        roi_b[roi_idx-1].append(avg_b)
                        break

        x_labels = [f"Img{i+1}" for i in range(num_images)]

        # Plot Blue Intensity for each ROI
        plt.figure(figsize=(self.window_width / 100, self.window_height / 100))
        for roi_idx in range(num_rois):
            plt.plot(x_labels, roi_intensities[roi_idx], marker='o', label=f'ROI {roi_idx+1}')
        plt.xlabel("Image")
        plt.ylabel("Blue Intensity")
        plt.title("Blue Intensity for Each ROI Across Images")
        plt.xticks(rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()
        plt.show(block=False)

        # Define line styles and colors
        line_styles = ['-', '--', ':', '-.']
        rgb_colors = ['red', 'green', 'blue']
        hsv_colors = ['orange', 'purple', 'black']
        channels = ['R', 'G', 'B']
        hsv_channels = ['H', 'S', 'V']

        # Plot Average R, G, B for each ROI (each ROI gets 3 lines, each with unique style)
        plt.figure(figsize=(self.window_width / 100, self.window_height / 100))
        for roi_idx in range(num_rois):
            for ch_idx, (data, color, ch) in enumerate(zip(
                [roi_r[roi_idx], roi_g[roi_idx], roi_b[roi_idx]],
                rgb_colors, channels
            )):
                style = line_styles[roi_idx % len(line_styles)]
                plt.plot(
                    x_labels, data, marker='o', color=color, linestyle=style,
                    label=f'ROI {roi_idx+1} {ch}'
                )
        plt.xlabel("Image")
        plt.ylabel("Average RGB Value")
        plt.title("Average R, G, B for Each ROI Across Images")
        plt.xticks(rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()
        plt.show(block=False)

        # Plot Average H, S, V for each ROI (each ROI gets 3 lines, each with unique style)
        plt.figure(figsize=(self.window_width / 100, self.window_height / 100))
        for roi_idx in range(num_rois):
            for ch_idx, (data, color, ch) in enumerate(zip(
                [roi_h[roi_idx], roi_s[roi_idx], roi_v[roi_idx]],
                hsv_colors, hsv_channels
            )):
                style = line_styles[roi_idx % len(line_styles)]
                plt.plot(
                    x_labels, data, marker='o', color=color, linestyle=style,
                    label=f'ROI {roi_idx+1} {ch}'
                )
        plt.xlabel("Image")
        plt.ylabel("Average HSV Value")
        plt.title("Average H, S, V for Each ROI Across Images")
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
        # image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Select 3 ROIs on the first image only
        if not self.rois:
            gui_w, gui_h = self.window_width, self.window_height
            img_h, img_w = image.shape[:2]
            scale_w = gui_w / img_w
            scale_h = gui_h / img_h
            scale = min(scale_w, scale_h)
            disp_w, disp_h = int(img_w * scale), int(img_h * scale)
            image_disp = cv2.resize(image, (disp_w, disp_h), interpolation=cv2.INTER_AREA)
            self.rois = []
            for i in range(3):
                self.text_box.append(f"Select ROI #{i+1} on the image window.")
                roi_disp = cv2.selectROI(f"Select ROI #{i+1}", image_disp, showCrosshair=True, fromCenter=False)
                cv2.destroyWindow(f"Select ROI #{i+1}")
                if roi_disp == (0, 0, 0, 0):
                    self.text_box.append(f"No ROI selected for ROI #{i+1}.")
                    return None, [], "", []
                x_disp, y_disp, w_disp, h_disp = roi_disp
                x = int(x_disp / scale)
                y = int(y_disp / scale)
                w = int(w_disp / scale)
                h = int(h_disp / scale)
                self.rois.append((x, y, w, h))
                self.text_box.append(f"ROI #{i+1} coordinates for 1st image: x={x}, y={y}, w={w}, h={h}")
                self.text_box.append(f"Top-left (x, y) of ROI #{i+1}: ({x}, {y})")

        annotated_image = image.copy()
        dimensions = []
        intensities = []
        for roi_idx, (x, y, w, h) in enumerate(self.rois, 1):
            roi_bgr = image[y:y + h, x:x + w]
            roi_hsv = hsv[y:y + h, x:x + w]

            # Draw rectangle for each ROI
            cv2.rectangle(annotated_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            label_text = f"ROI {roi_idx}"
            font_scale = 1.0
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

            intensities.append((image_idx, roi_idx, blue_intensity, avg_h, avg_s, avg_v, avg_r, avg_g, avg_b))
            dimensions.append(
                f"ROI {roi_idx}: W: {w}, H: {h}, "
                f"Light Intensity: {blue_intensity:.2f}, "
                f"HSV: ({avg_h:.1f}, {avg_s:.1f}, {avg_v:.1f}), "
                f"RGB: ({avg_r:.1f}, {avg_g:.1f}, {avg_b:.1f})"
            )
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