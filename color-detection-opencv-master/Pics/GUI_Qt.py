import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QVBoxLayout, QLabel

class FileDialogApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('File Dialog Example')

        # Create a button
        self.button = QPushButton('Open File Dialog', self)
        self.button.clicked.connect(self.open_file_dialog)

        # Create a label to display the file path
        self.label = QLabel('Selected file path will appear here', self)

        # Set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.label)

        self.setLayout(layout)

    def open_file_dialog(self):
        # Use QFileDialog.getOpenFileName directly
        file_path, _ = QFileDialog.getOpenFileName(self, "Select a File", "", "All Files (*);;Text Files (*.txt)")
        
        if file_path:
            self.label.setText(file_path)
            print(file_path)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FileDialogApp()
    window.show()
    sys.exit(app.exec())