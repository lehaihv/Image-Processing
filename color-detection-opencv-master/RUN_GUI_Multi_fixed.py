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

        # Determine number of images and ROIs
        num_images = max([img_idx for img_idx, *_ in self.light_intensity_data])
        num_rois = max([roi_idx for _, roi_idx, *_ in self.light_intensity_data])

        # Prepare data: one list per ROI per channel
        roi_intensities = [[] for _ in range(num_rois)]
        roi_h = [[] for _ in range(num_rois)]
        roi_s = [[] for _ in range(num_rois)]
        roi_v = [[] for _ in range(num_rois)]
        roi_r = [[] for _ in range(num_rois)]
        roi_g = [[] for _ in range(num_rois)]
        roi_b = [[] for _ in range(num_rois)]

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

        # Apply LOESS smoothing for each ROI and channel
        def get_lowess(data):
            if len(data) > 2:
                return lowess(data, np.arange(len(data)), frac=0.3)[:, 1]
            else:
                return np.array(data)

        loess_intensity = [get_lowess(roi_intensities[i]) for i in range(num_rois)]
        loess_h = [get_lowess(roi_h[i]) for i in range(num_rois)]
        loess_s = [get_lowess(roi_s[i]) for i in range(num_rois)]
        loess_v = [get_lowess(roi_v[i]) for i in range(num_rois)]
        loess_r = [get_lowess(roi_r[i]) for i in range(num_rois)]
        loess_g = [get_lowess(roi_g[i]) for i in range(num_rois)]
        loess_b = [get_lowess(roi_b[i]) for i in range(num_rois)]

        # Prepare CSV header
        header = ["Image Index"]
        for roi_idx in range(1, num_rois + 1):
            header += [
                f"ROI{roi_idx} Blue Intensity", f"ROI{roi_idx} Blue Intensity LOWESS",
                f"ROI{roi_idx} Avg H", f"ROI{roi_idx} Avg H LOWESS",
                f"ROI{roi_idx} Avg S", f"ROI{roi_idx} Avg S LOWESS",
                f"ROI{roi_idx} Avg V", f"ROI{roi_idx} Avg V LOWESS",
                f"ROI{roi_idx} Avg R", f"ROI{roi_idx} Avg R LOWESS",
                f"ROI{roi_idx} Avg G", f"ROI{roi_idx} Avg G LOWESS",
                f"ROI{roi_idx} Avg B", f"ROI{roi_idx} Avg B LOWESS"
            ]

        # Prepare rows
        rows = []
        for img_idx in range(num_images):
            row = [img_idx + 1]
            for roi_idx in range(num_rois):
                # Raw and LOWESS for each channel
                row += [
                    roi_intensities[roi_idx][img_idx] if img_idx < len(roi_intensities[roi_idx]) else "",
                    loess_intensity[roi_idx][img_idx] if img_idx < len(loess_intensity[roi_idx]) else "",
                    roi_h[roi_idx][img_idx] if img_idx < len(roi_h[roi_idx]) else "",
                    loess_h[roi_idx][img_idx] if img_idx < len(loess_h[roi_idx]) else "",
                    roi_s[roi_idx][img_idx] if img_idx < len(roi_s[roi_idx]) else "",
                    loess_s[roi_idx][img_idx] if img_idx < len(loess_s[roi_idx]) else "",
                    roi_v[roi_idx][img_idx] if img_idx < len(roi_v[roi_idx]) else "",
                    loess_v[roi_idx][img_idx] if img_idx < len(loess_v[roi_idx]) else "",
                    roi_r[roi_idx][img_idx] if img_idx < len(roi_r[roi_idx]) else "",
                    loess_r[roi_idx][img_idx] if img_idx < len(loess_r[roi_idx]) else "",
                    roi_g[roi_idx][img_idx] if img_idx < len(roi_g[roi_idx]) else "",
                    loess_g[roi_idx][img_idx] if img_idx < len(loess_g[roi_idx]) else "",
                    roi_b[roi_idx][img_idx] if img_idx < len(roi_b[roi_idx]) else "",
                    loess_b[roi_idx][img_idx] if img_idx < len(loess_b[roi_idx]) else "",
                ]
            rows.append(row)

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

        # Determine number of images and ROIs
        num_images = max([img_idx for img_idx, *_ in self.light_intensity_data])
        num_rois = max([roi_idx for _, roi_idx, *_ in self.light_intensity_data])

        # Prepare data: one list per ROI per channel
        roi_intensities = [[] for _ in range(num_rois)]
        roi_r = [[] for _ in range(num_rois)]
        roi_g = [[] for _ in range(num_rois)]
        roi_b = [[] for _ in range(num_rois)]

        # Collect data for each ROI across all images
        for img_idx in range(1, num_images + 1):
            for roi_idx in range(1, num_rois + 1):
                for entry in self.light_intensity_data:
                    if entry[0] == img_idx and entry[1] == roi_idx:
                        _, _, blue_intensity, _, _, _, avg_r, avg_g, avg_b = entry
                        roi_intensities[roi_idx-1].append(blue_intensity)
                        roi_r[roi_idx-1].append(avg_r)
                        roi_g[roi_idx-1].append(avg_g)
                        roi_b[roi_idx-1].append(avg_b)
                        break

        x = np.arange(num_images)
        x_labels = [f"Img{i+1}" for i in range(num_images)]
        line_styles = ['-', '--', '-.']

        # --- Blue Intensity: 2 subplots in 2 rows, 1 column ---
        fig, axs = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
        # Raw data subplot (top)
        for roi_idx in range(num_rois):
            axs[0].plot(
                x, roi_intensities[roi_idx],
                marker='o',
                linestyle=line_styles[roi_idx % len(line_styles)],
                label=f'ROI {roi_idx+1}'
            )
        axs[0].set_ylabel("Blue Intensity")
        axs[0].set_title("Raw Blue Light Intensity")
        axs[0].set_ylim(0, 255)
        axs[0].set_xticks(np.arange(0, num_images, 20))
        axs[0].set_xticklabels([str(i) for i in np.arange(0, num_images, 20)])
        axs[0].legend()
        axs[0].grid(True)

        # LOWESS subplot (bottom)
        for roi_idx in range(num_rois):
            if len(roi_intensities[roi_idx]) > 2:
                lowess_result = lowess(roi_intensities[roi_idx], x, frac=0.3)
                axs[1].plot(
                    x, lowess_result[:, 1],
                    linestyle=line_styles[roi_idx % len(line_styles)],
                    marker='o',
                    label=f'ROI {roi_idx+1} LOWESS'
                )
        axs[1].set_xlabel("Image")
        axs[1].set_ylabel("Blue Intensity")
        axs[1].set_title("LOWESS Blue Light Intensity")
        axs[1].set_ylim(0, 255)
        axs[1].set_xticks(np.arange(0, num_images, 20))
        axs[1].set_xticklabels([str(i) for i in np.arange(0, num_images, 20)])
        axs[1].legend()
        axs[1].grid(True)

        plt.tight_layout()
        plt.show(block=False)

        # --- Average R,G,B: 3x6 subplots for each line ---
        # fig, axs = plt.subplots(3, 6, figsize=(24, 12), sharex=True)
        fig, axs = plt.subplots(3, num_rois * 2, figsize=(4 * num_rois * 2, 12), sharex=True)
        colors = ['red', 'green', 'blue']
        channels = ['R', 'G', 'B']
        for roi_idx in range(num_rois):
            # Row 0: Raw R, G, B for this ROI
            axs[0, roi_idx*2].plot(x, roi_r[roi_idx], marker='o', color='red', linestyle=line_styles[roi_idx % len(line_styles)])
            axs[0, roi_idx*2].set_title(f'ROI {roi_idx+1} R Raw')
            axs[0, roi_idx*2].set_ylim(0, 255)
            axs[0, roi_idx*2].set_xticks(np.arange(0, num_images, 50))
            axs[0, roi_idx*2].set_xticklabels([str(i) for i in np.arange(0, num_images, 50)])
            axs[0, roi_idx*2].grid(True)

            axs[0, roi_idx*2+1].plot(x, roi_g[roi_idx], marker='o', color='green', linestyle=line_styles[roi_idx % len(line_styles)])
            axs[0, roi_idx*2+1].set_title(f'ROI {roi_idx+1} G Raw')
            axs[0, roi_idx*2+1].set_ylim(0, 255)
            axs[0, roi_idx*2+1].set_xticks(np.arange(0, num_images, 50))
            axs[0, roi_idx*2+1].set_xticklabels([str(i) for i in np.arange(0, num_images, 50)])
            axs[0, roi_idx*2+1].grid(True)

            # Row 1: Raw B for this ROI, then LOWESS R
            axs[1, roi_idx*2].plot(x, roi_b[roi_idx], marker='o', color='blue', linestyle=line_styles[roi_idx % len(line_styles)])
            axs[1, roi_idx*2].set_title(f'ROI {roi_idx+1} B Raw')
            axs[1, roi_idx*2].set_ylim(0, 255)
            axs[1, roi_idx*2].set_xticks(np.arange(0, num_images, 50))
            axs[1, roi_idx*2].set_xticklabels([str(i) for i in np.arange(0, num_images, 50)])
            axs[1, roi_idx*2].grid(True)

            if len(roi_r[roi_idx]) > 2:
                lowess_r = lowess(roi_r[roi_idx], x, frac=0.3)
                axs[1, roi_idx*2+1].plot(x, lowess_r[:, 1], color='red', linestyle=line_styles[roi_idx % len(line_styles)], marker='o')
            axs[1, roi_idx*2+1].set_title(f'ROI {roi_idx+1} R LOWESS')
            axs[1, roi_idx*2+1].set_ylim(0, 255)
            axs[1, roi_idx*2+1].set_xticks(np.arange(0, num_images, 50))
            axs[1, roi_idx*2+1].set_xticklabels([str(i) for i in np.arange(0, num_images, 50)])
            axs[1, roi_idx*2+1].grid(True)

            # Row 2: LOWESS G, LOWESS B
            if len(roi_g[roi_idx]) > 2:
                lowess_g = lowess(roi_g[roi_idx], x, frac=0.3)
                axs[2, roi_idx*2].plot(x, lowess_g[:, 1], color='green', linestyle=line_styles[roi_idx % len(line_styles)], marker='o')
            axs[2, roi_idx*2].set_title(f'ROI {roi_idx+1} G LOWESS')
            axs[2, roi_idx*2].set_ylim(0, 255)
            axs[2, roi_idx*2].set_xticks(np.arange(0, num_images, 50))
            axs[2, roi_idx*2].set_xticklabels([str(i) for i in np.arange(0, num_images, 50)])
            axs[2, roi_idx*2].grid(True)

            if len(roi_b[roi_idx]) > 2:
                lowess_b = lowess(roi_b[roi_idx], x, frac=0.3)
                axs[2, roi_idx*2+1].plot(x, lowess_b[:, 1], color='blue', linestyle=line_styles[roi_idx % len(line_styles)], marker='o')
            axs[2, roi_idx*2+1].set_title(f'ROI {roi_idx+1} B LOWESS')
            axs[2, roi_idx*2+1].set_ylim(0, 255)
            axs[2, roi_idx*2+1].set_xticks(np.arange(0, num_images, 50))
            axs[2, roi_idx*2+1].set_xticklabels([str(i) for i in np.arange(0, num_images, 50)])
            axs[2, roi_idx*2+1].grid(True)

        plt.tight_layout()
        plt.show(block=False)

    def process_image(self, file_name, image_idx):
        image = cv2.imread(file_name)
        if image is None:
            print(f"Error: Could not open image {file_name}.")
            return None, [], "", []

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # --- Use 3 fixed ROIs for all images ---
        """ img_h, img_w = image.shape[:2]
        # Example: 3 ROIs horizontally across the image, each 1/4 width, half height, adjust as needed
        roi_w = img_w // 4
        roi_h = img_h // 2
        self.rois = [
            (int(img_w * 0.1), int(img_h * 0.25), roi_w, roi_h),               # Left
            (int(img_w * 0.5) - roi_w // 2, int(img_h * 0.25), roi_w, roi_h),  # Center
            (int(img_w * 0.9) - roi_w, int(img_h * 0.25), roi_w, roi_h),       # Right
        ] """
        self.rois = [
            (30, 440, 275, 150),#
            (374, 441, 275, 150),
            (712, 443, 275, 150)
            #(712, 443, 75, 50)
        ]
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