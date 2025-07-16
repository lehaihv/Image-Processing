import sys
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QLabel, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class CSVAnalyzer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSV Column Analyzer")
        self.resize(600, 500)

        self.df = None
        self.detected_index = None

        # Layout and Widgets
        self.layout = QVBoxLayout()

        self.label = QLabel("Select a CSV file:")
        self.layout.addWidget(self.label)

        self.button = QPushButton("Browse CSV")
        self.button.clicked.connect(self.browse_csv)
        self.layout.addWidget(self.button)

        self.combo = QComboBox()
        self.combo.setEnabled(False)
        self.layout.addWidget(self.combo)

        self.analyze_button = QPushButton("Analyze Column")
        self.analyze_button.setEnabled(False)
        self.analyze_button.clicked.connect(self.analyze_column)
        self.layout.addWidget(self.analyze_button)

        self.result_label = QLabel("")
        self.layout.addWidget(self.result_label)

        # Matplotlib Figure
        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.setLayout(self.layout)

    def browse_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_path:
            try:
                self.df = pd.read_csv(file_path)
                self.combo.clear()
                self.combo.addItems(self.df.columns)
                self.combo.setEnabled(True)
                self.analyze_button.setEnabled(True)
                self.result_label.setText("")
                self.figure.clear()
                self.canvas.draw()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load CSV:\n{str(e)}")

    def analyze_column(self):
        column_name = self.combo.currentText()
        data = self.df[column_name].dropna().reset_index(drop=True)

        self.detected_index = None

        for i in range(1, len(data)):
            prev_avg = data[:i].mean()
            if data[i] > 1.05 * prev_avg:
                self.detected_index = i
                self.result_label.setText(
                    f"Index: {i}, Value: {data[i]:.2f}, Prev Avg: {prev_avg:.2f}"
                )
                break

        if self.detected_index is None:
            self.result_label.setText("No value is 5% higher than the average of previous values.")

        self.plot_data(data)

    def plot_data(self, data):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        ax.plot(data, label='Data', color='blue')

        if self.detected_index is not None:
            ax.plot(
                self.detected_index,
                data[self.detected_index],
                marker='o',
                markersize=8,
                color='red',
                label='Detected Point'
            )

        ax.set_title("Line Plot of Column Data")
        ax.set_xlabel("Index")
        ax.set_ylabel("Value")
        ax.legend()
        ax.grid(True)

        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CSVAnalyzer()
    window.show()
    sys.exit(app.exec())
