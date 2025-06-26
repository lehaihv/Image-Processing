import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import (
    QApplication, QFileDialog, QInputDialog, QMessageBox
)

def select_data_file():
    dialog = QFileDialog()
    dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
    dialog.setNameFilter("Data Files (*.csv *.xlsx)")
    if dialog.exec():
        return dialog.selectedFiles()[0]
    return None

def select_columns(prompt, columns):
    selected_columns = []
    while True:
        item, ok = QInputDialog.getItem(
            None, "Select Column", prompt, columns, 0, False
        )
        if ok and item:
            selected_columns.append(item)
            # Remove the selected item from the list to prevent re-selection
            columns.remove(item)
        else:
            break
    return selected_columns

def main():
    # ✅ Initialize QApplication BEFORE using any PyQt6 widgets
    app = QApplication(sys.argv)

    file_path = select_data_file()
    if not file_path:
        print("No file selected.")
        return

    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif file_path.endswith(".xlsx"):
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file type.")
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to load file:\n{e}")
        return

    if df.shape[1] < 2:
        QMessageBox.warning(None, "Invalid File", "The file must have at least two columns.")
        return

    # Ask user to select columns
    selected_columns = select_columns("Select columns to plot", df.columns.tolist())
    if not selected_columns:
        return

    # Plotting
    plt.figure(figsize=(10, 6))
    x = range(len(df))

    for col in selected_columns:
        plt.plot(x, df[col], label=col)

    tick_spacing = 20 if len(df) < 1000 else max(1, len(df) // 50)
    plt.xticks(ticks=range(0, len(df), tick_spacing))

    plt.xlabel("Sample Number")
    plt.ylabel("Average Blue Light Intensity")
    plt.title("Enterococci Assay")
    plt.legend(loc='upper left')
    plt.grid(True)
    plt.tight_layout()

    # Save plot
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    out_dir = os.path.dirname(file_path)
    plot_path = os.path.join(out_dir, f"{base_name}_plot.png")

    plt.savefig(plot_path)
    plt.show()

    QMessageBox.information(
        None,
        "Export Complete",
        f"Plot saved to:\n{plot_path}"
    )

if __name__ == "__main__":
    main()