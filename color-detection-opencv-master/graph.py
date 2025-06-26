import sys
import pandas as pd
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import QApplication, QFileDialog

def select_csv_file():
    app = QApplication(sys.argv)
    dialog = QFileDialog()
    dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
    dialog.setNameFilter("CSV Files (*.csv)")
    if dialog.exec():
        return dialog.selectedFiles()[0]
    return None

def main():
    file_path = select_csv_file()

    if not file_path:
        print("No file selected.")
        return

    # Load CSV file
    df = pd.read_csv(file_path)

    if df.shape[1] < 2:
        print("The CSV must have at least two columns.")
        return

    print("Columns in the CSV:", df.columns.tolist())

    # Extract first two columns
    column1 = df.columns[0]
    column2 = df.columns[1]

    y1 = df[column1]
    y2 = df[column2]
    x = range(len(df))

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(x, y1, label=column1)
    plt.plot(x, y2, label=column2)

    plt.xticks(ticks=range(0, len(df), 20))
    plt.xlabel("Time of sampling (x 2 minutes)")
    plt.ylabel("Average Blue Light Intensity")
    plt.title("Enterococci Assay")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
