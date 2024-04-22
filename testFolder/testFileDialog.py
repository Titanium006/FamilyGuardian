
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("File Save Dialog Example")
        self.setGeometry(100, 100, 400, 200)

        self.button = QPushButton("Save File Dialog", self)
        self.button.setGeometry(150, 80, 150, 30)
        self.button.clicked.connect(self.save_file_dialog)

    def save_file_dialog(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.Directory)
        directory_path = dialog.getExistingDirectory()
        if directory_path:
            print("Selected Directory:", directory_path)
            print(type(directory_path))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
