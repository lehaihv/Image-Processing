import sys
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QLabel, QWidget, QVBoxLayout, QMessageBox
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from PIL import Image
import tensorflow as tf

class DragDropWidget(QWidget):
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.setWindowTitle("MNIST Digit Recognition - Drag & Drop Image")
        self.setAcceptDrops(True)
        self.resize(300, 400)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.instruction = QLabel("Drag and drop a digit image here")
        self.instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.instruction)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.image_label)

        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.result_label)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            # Take first file only
            file_path = urls[0].toLocalFile()
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                self.process_image(file_path)
            else:
                QMessageBox.warning(self, "Invalid File", "Please drop an image file.")

    def process_image(self, file_path):
        # Load and preprocess image
        img = Image.open(file_path).convert("L").resize((28, 28))
        img_array = np.array(img).astype("float32") / 255.0
        img_array = 1.0 - img_array  # invert colors if needed
        input_for_model = np.expand_dims(img_array, axis=(0, -1))

        # Predict
        preds = self.model.predict(input_for_model)
        predicted_class = np.argmax(preds, axis=1)[0]

        # Show image scaled up for UI
        pixmap = QPixmap(file_path).scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)
        self.image_label.setPixmap(pixmap)

        # Show prediction
        self.result_label.setText(f"Predicted digit: {predicted_class}")

def main():
    app = QApplication(sys.argv)

    model = tf.keras.models.load_model("mnist_model.keras")  # Load your model here

    widget = DragDropWidget(model)
    widget.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
