import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget

from hyperedit.srt import parse_srt

from hyperedit_gui.view.project_window import ProjectWindow
from hyperedit_gui.view.tracks_window import TracksWindow
from hyperedit_gui.view.srt_window import SrtWindow
from hyperedit_gui.controller import Controller

from hyperedit_gui.config import GetConfig, HeConfig

class MainWindow(QMainWindow):
    def __init__(self, controller: Controller):
        super().__init__()
        
        self.setWindowTitle("HyperEdit")

        # Set the main window's size
        self.resize(800, 600)

        self.stackedWidget = QStackedWidget()
        self.setCentralWidget(self.stackedWidget)

        self.projectView = ProjectWindow(self.stackedWidget, controller)
        self.tracksView = TracksWindow(self.stackedWidget, [], controller)
        self.srtView = SrtWindow(self.stackedWidget, srts, controller)

        self.stackedWidget.addWidget(self.projectView)
        self.stackedWidget.addWidget(self.tracksView)
        self.stackedWidget.addWidget(self.srtView)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    srts = parse_srt("data/test.srt")
    # we wouldn't normally do this, this would be accessed from the controller
    config: HeConfig = GetConfig()
    controller = Controller()
    mainWindow = MainWindow(controller)
    mainWindow.show()
    sys.exit(app.exec())