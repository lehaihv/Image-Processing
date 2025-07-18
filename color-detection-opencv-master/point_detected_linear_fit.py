import sys
import pandas as pd
import statsmodels.api as sm
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QLabel, QMessageBox
)
from PyQt6.QtGui import QGuiApplication
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class RegressionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Linear Fit: Concentration vs Point")

        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.resize(int(screen.width() * 0.7), int(screen.height() * 0.7))

        self.df = None

        layout = QVBoxLayout()

        # Top control row
        button_row = QHBoxLayout()
        self.browse_button = QPushButton("📂 Browse Data File")
        self.browse_button.clicked.connect(self.load_data)
        button_row.addWidget(self.browse_button)

        self.fit_button = QPushButton("📈 Fit Linear Model")
        self.fit_button.clicked.connect(self.fit_data)
        self.fit_button.setEnabled(False)
        button_row.addWidget(self.fit_button)

        layout.addLayout(button_row)

        # Matplotlib area
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Summary label
        self.summary_label = QLabel("Model summary will appear here.")
        self.summary_label.setWordWrap(True)
        self.summary_label.setStyleSheet("border: 1px solid gray; padding: 6px;")
        layout.addWidget(self.summary_label)

        self.setLayout(layout)

    def load_data(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Data File",
            "",
            "Data Files (*.csv *.xls *.xlsx)"
        )
        if not file_path:
            return

        try:
            if file_path.lower().endswith('.csv'):
                self.df = pd.read_csv(file_path)
            elif file_path.lower().endswith(('.xls', '.xlsx')):
                self.df = pd.read_excel(file_path)
            else:
                raise ValueError("Unsupported file type. Please select a CSV or Excel file.")
            if not {"concentration", "Point"}.issubset(self.df.columns):
                raise ValueError("File must contain 'concentration' and 'Point' columns.")
            self.summary_label.setText("Data loaded. Click 'Fit Linear Model' to continue.")
            self.fit_button.setEnabled(True)
            self.figure.clear()
            self.canvas.draw()
        except Exception as e:
            QMessageBox.critical(self, "Error Loading Data", str(e))

    def fit_data(self):
        try:
            x = self.df["Point"]
            y = self.df["concentration"]

            X = sm.add_constant(x)
            model = sm.OLS(y, X).fit()

            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.scatter(x, y, label="Data", color='blue')
            ax.plot(x, model.predict(X), color='red', label="Linear Fit")
            ax.set_xlabel("Point")
            ax.set_ylabel("Concentration")
            ax.set_title("Linear Regression")
            ax.legend()
            ax.grid(True)
            self.canvas.draw()

            summary_text = (
                f"<b>Linear Fit Summary:</b><br>"
                f"R²: {model.rsquared:.4f}<br>"
                f"Intercept: {model.params['const']:.4f}<br>"
                f"Slope: {model.params['Point']:.4f}<br>"
                f"p-value: {model.pvalues['Point']:.4g}<br>"
            )
            self.summary_label.setText(summary_text)

        except Exception as e:
            QMessageBox.critical(self, "Error Fitting Model", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RegressionApp()
    window.show()
    sys.exit(app.exec())
