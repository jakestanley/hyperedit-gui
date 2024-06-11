import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget

from hyperedit.srt import parse_srt

from hyperedit_gui.view.project_window import ProjectWindow
from hyperedit_gui.view.tracks_window import TracksWindow
from hyperedit_gui.view.srt_window import SrtWindow

class MainWindow(QMainWindow):
    def __init__(self, projects, srts):
        super().__init__()
        self.setWindowTitle("HyperEdit")

        self.stackedWidget = QStackedWidget()
        self.setCentralWidget(self.stackedWidget)

        self.projectView = ProjectWindow(self.stackedWidget, projects)
        self.tracksView = TracksWindow(self.stackedWidget)
        self.srtView = SrtWindow(self.stackedWidget, srts)

        self.stackedWidget.addWidget(self.projectView)
        self.stackedWidget.addWidget(self.tracksView)
        self.stackedWidget.addWidget(self.srtView)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    projects = [
        ("Project Alpha", "/path/to/alpha"),
        ("Project Beta", "/path/to/beta"),
        ("Project Gamma", "/path/to/gamma")
    ]
    srts = parse_srt("data/test.srt")
    # we wouldn't normally do this, this would be accessed from the controller
    mainWindow = MainWindow(projects, srts)
    mainWindow.show()
    sys.exit(app.exec())