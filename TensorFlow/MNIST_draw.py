import sys
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QLabel, QWidget, QVBoxLayout, QPushButton, QHBoxLayout
)
from PyQt6.QtGui import QPainter, QPen, QPixmap, QColor, QImage
from PyQt6.QtCore import Qt, QPoint
import tensorflow as tf
from PIL import Image

class DrawWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(780, 580)  # Bigger canvas for drawing
        self.setStyleSheet("background-color: black;")
        self.image = QPixmap(self.size())
        self.image.fill(Qt.GlobalColor.black)
        self.last_point = QPoint()
        self.drawing = False

    def paintEvent(self, event):
        canvas_painter = QPainter(self)
        canvas_painter.drawPixmap(0, 0, self.image)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.last_point = event.position().toPoint()

    def mouseMoveEvent(self, event):
        if self.drawing:
            painter = QPainter(self.image)
            pen = QPen(Qt.GlobalColor.white, 15, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawLine(self.last_point, event.position().toPoint())
            self.last_point = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False

    def clear(self):
        self.image.fill(Qt.GlobalColor.black)
        self.update()

    def get_image(self):
        # Convert QPixmap to PIL Image
        qimg = self.image.toImage().convertToFormat(QImage.Format.Format_Grayscale8)
        width = qimg.width()
        height = qimg.height()
        ptr = qimg.bits()
        ptr.setsize(width * height)
        arr = np.frombuffer(ptr, np.uint8).reshape((height, width))
        return Image.fromarray(arr)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Draw a Digit and Predict (MNIST)")

        self.model = tf.keras.models.load_model("mnist_model.keras")

        self.draw_widget = DrawWidget()

        self.predict_button = QPushButton("Predict")
        self.predict_button.clicked.connect(self.predict_digit)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.draw_widget.clear)

        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setStyleSheet("font-size: 18px;")

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.predict_button)
        btn_layout.addWidget(self.clear_button)

        layout = QVBoxLayout()
        layout.addWidget(self.draw_widget)
        layout.addLayout(btn_layout)
        layout.addWidget(self.result_label)
        self.setLayout(layout)
        self.resize(800, 600)

    def preprocess_image(self, pil_img):
        # Resize to 28x28
        img = pil_img.resize((28, 28))
        img_array = np.array(img).astype("float32") / 255.0
        img_array = 1.0 - img_array  # invert colors: model expects white digit on black bg
        img_array = img_array.reshape(1, 28, 28, 1)
        return img_array

    def predict_digit(self):
        pil_img = self.draw_widget.get_image()
        input_img = self.preprocess_image(pil_img)
        preds = self.model.predict(input_img)
        predicted_class = np.argmax(preds, axis=1)[0]
        self.result_label.setText(f"Predicted Digit: {predicted_class}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
