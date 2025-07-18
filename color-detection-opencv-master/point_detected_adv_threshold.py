from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QLabel, QListWidget, QListWidgetItem,
    QMessageBox, QAbstractItemView, QLineEdit
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
import sys


class CSVAnalyzer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-Column CSV Analyzer")

        # Set to 3/4 of screen
        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.resize(int(screen.width() * 0.75), int(screen.height() * 0.75))

        self.df = None

        # === Main layout ===
        main_layout = QVBoxLayout()

        # --- Top row: Browse + Threshold + Analyze buttons ---
        top_row = QHBoxLayout()

        self.browse_button = QPushButton("📂 Browse CSV")
        self.browse_button.clicked.connect(self.browse_csv)
        top_row.addWidget(self.browse_button)

        # Threshold input field
        self.threshold_input = QLineEdit()
        self.threshold_input.setPlaceholderText("Threshold (e.g. 80)")
        self.threshold_input.setFixedWidth(100)
        top_row.addWidget(QLabel("Threshold:"))
        top_row.addWidget(self.threshold_input)

        # Analyze button
        self.analyze_button = QPushButton("📊 Analyze Selected Columns")
        self.analyze_button.setEnabled(False)
        self.analyze_button.clicked.connect(self.analyze_columns)
        top_row.addWidget(self.analyze_button)

        main_layout.addLayout(top_row)

        # --- Second row: column list and result display ---
        second_row = QHBoxLayout()

        # Column list (left)
        self.column_list = QListWidget()
        self.column_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.column_list.setEnabled(False)
        self.column_list.setFixedHeight(100)
        self.column_list.setSizePolicy(
            self.column_list.sizePolicy().horizontalPolicy(),
            self.column_list.sizePolicy().verticalPolicy()
        )
        second_row.addWidget(self.column_list)

        # Result label (right)
        self.result_label = QLabel("Results will appear here.")
        self.result_label.setWordWrap(True)
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.result_label.setTextFormat(Qt.TextFormat.RichText)
        self.result_label.setStyleSheet("border: 1px solid lightgray; padding: 4px;")
        second_row.addWidget(self.result_label)

        # Equal horizontal stretch
        second_row.setStretch(0, 1)
        second_row.setStretch(1, 1)

        main_layout.addLayout(second_row)

        # --- Plot area ---
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        main_layout.addWidget(self.canvas)

        self.setLayout(main_layout)

    def browse_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_path:
            try:
                self.df = pd.read_csv(file_path)
                self.column_list.clear()
                for col in self.df.columns:
                    self.column_list.addItem(QListWidgetItem(col))
                self.column_list.setEnabled(True)
                self.analyze_button.setEnabled(True)
                self.result_label.setText("Columns loaded. Select and analyze.")
                self.figure.clear()
                self.canvas.draw()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load CSV:\n{str(e)}")

    def analyze_columns(self):
        selected_items = self.column_list.selectedItems()
        selected_columns = [item.text() for item in selected_items]

        if not selected_columns:
            QMessageBox.warning(self, "No Column Selected", "Please select at least one column.")
            return

        # Get threshold value from input
        try:
            threshold = float(self.threshold_input.text())
        except ValueError:
            QMessageBox.warning(self, "Invalid Threshold", "Please enter a valid numeric threshold.")
            return

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        results = []

        for col in selected_columns:
            try:
                data = pd.to_numeric(self.df[col], errors='coerce').dropna().reset_index(drop=True)
                detected_index = None

                for i in range(len(data)):
                    if data[i] > threshold:
                        detected_index = i
                        break

                ax.plot(data, label=col)

                if detected_index is not None:
                    ax.plot(detected_index, data[detected_index], 'ro', markersize=8)
                    results.append(
                        f"<b>{col}</b>: First value &gt; {threshold} at index {detected_index}, Value = {data[detected_index]:.2f}"
                    )
                else:
                    results.append(f"<b>{col}</b>: No value &gt; {threshold} found.")

            except Exception as e:
                results.append(f"<b>{col}</b>: Error - {str(e)}")

        ax.set_title(f"Columns with Values > {threshold}")
        ax.set_xlabel("Index")
        ax.set_ylabel("Value")
        ax.legend()
        ax.grid(True)
        self.canvas.draw()

        self.result_label.setText("<br>".join(results))


# Run the app
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CSVAnalyzer()
    window.show()
    sys.exit(app.exec())
