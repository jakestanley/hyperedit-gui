import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('My PySide2 Application')
        self.setGeometry(100, 100, 800, 600)

        button = QPushButton('Click Me', self)
        button.clicked.connect(self.on_click)
        self.setCentralWidget(button)

    def on_click(self):
        print('Button clicked!')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())