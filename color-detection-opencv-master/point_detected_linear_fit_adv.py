import sys
import pandas as pd
import statsmodels.api as sm
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QLabel, QMessageBox, QComboBox
)
from PyQt6.QtGui import QGuiApplication
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np


class RegressionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Linear Fit: Concentration vs Point")

        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.resize(int(screen.width() * 0.7), int(screen.height() * 0.7))

        self.df = None

        layout = QVBoxLayout()

        # Top row: File load and regression
        button_row = QHBoxLayout()
        self.browse_button = QPushButton("📂 Browse Data File")
        self.browse_button.clicked.connect(self.load_data)
        button_row.addWidget(self.browse_button)

        self.fit_button = QPushButton("📈 Fit Linear Model")
        self.fit_button.clicked.connect(self.fit_data)
        self.fit_button.setEnabled(False)
        button_row.addWidget(self.fit_button)

        self.save_button = QPushButton("💾 Save Plot")
        self.save_button.clicked.connect(self.save_plot)
        self.save_button.setEnabled(False)
        button_row.addWidget(self.save_button)

        layout.addLayout(button_row)

        # Middle row: Column selectors
        selector_row = QHBoxLayout()
        selector_row.addWidget(QLabel("X (Point):"))
        self.x_col_selector = QComboBox()
        self.x_col_selector.setEnabled(False)
        selector_row.addWidget(self.x_col_selector)

        selector_row.addWidget(QLabel("Y (Concentration):"))
        self.y_col_selector = QComboBox()
        self.y_col_selector.setEnabled(False)
        selector_row.addWidget(self.y_col_selector)

        layout.addLayout(selector_row)

        # Plotting area
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

            if self.df.empty:
                raise ValueError("The file is empty.")

            self.x_col_selector.clear()
            self.y_col_selector.clear()
            columns = list(self.df.columns)
            self.x_col_selector.addItems(columns)
            self.y_col_selector.addItems(columns)
            self.x_col_selector.setEnabled(True)
            self.y_col_selector.setEnabled(True)

            self.fit_button.setEnabled(True)
            self.save_button.setEnabled(False)
            self.figure.clear()
            self.canvas.draw()
            self.summary_label.setText("Data loaded. Select columns and click 'Fit Linear Model'.")
        except Exception as e:
            QMessageBox.critical(self, "Error Loading Data", str(e))

    def fit_data(self):
        try:
            x_col = self.x_col_selector.currentText()
            y_col = self.y_col_selector.currentText()

            if not x_col or not y_col:
                raise ValueError("Please select both X and Y columns.")

            x = self.df[x_col]
            #y = self.df[y_col]
            y_raw = self.df[y_col]
            if (y_raw <= 0).any():
                raise ValueError("Y values must be positive for log10 transformation.")
            y = np.log10(y_raw)

            if x.isnull().any() or y.isnull().any():
                raise ValueError("Data contains missing values. Please clean your data.")

            X = sm.add_constant(x)
            model = sm.OLS(y, X).fit()

            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.scatter(x, y, label="Data", color='blue')
            ax.plot(x, model.predict(X), color='red', label="Linear Fit")

            # Compose equation and summary
            equation = f"y = {model.params[x_col]:.2f}x + {model.params['const']:.2f}"
            summary = (
                f"R² = {model.rsquared:.4f}\n"
                f"Intercept = {model.params['const']:.4f}\n"
                f"Slope = {model.params[x_col]:.4f}\n"
                f"p = {model.pvalues[x_col]:.4g}"
            )

            # Annotate bottom-left inside plot
            ax.text(
                0.05, 0.05,
                f"{equation}\n{summary}",
                transform=ax.transAxes,
                fontsize=10,
                verticalalignment='bottom',
                horizontalalignment='left',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor="gray", alpha=0.8)
            )

            ax.set_xlabel(x_col)
            #ax.set_ylabel(y_col)
            ax.set_ylabel(f"log10({y_col})")
            ax.set_title("Linear Regression")
            ax.legend()
            ax.grid(True)
            self.canvas.draw()

            summary_text = (
                f"<b>Linear Fit Summary:</b><br>"
                f"R²: {model.rsquared:.4f}<br>"
                f"Intercept: {model.params['const']:.4f}<br>"
                f"Slope ({x_col}): {model.params[x_col]:.4f}<br>"
                f"p-value: {model.pvalues[x_col]:.4g}<br>"
            )
            self.summary_label.setText(summary_text)
            self.save_button.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "Error Fitting Model", str(e))


    def save_plot(self):
        try:
            path, _ = QFileDialog.getSaveFileName(
                self, "Save Plot", "", "PNG Files (*.png);;All Files (*)"
            )
            if path:
                self.figure.savefig(path)
        except Exception as e:
            QMessageBox.critical(self, "Error Saving Plot", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RegressionApp()
    window.show()
    sys.exit(app.exec())
