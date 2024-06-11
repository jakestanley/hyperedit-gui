import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QLabel, QWidget, QHBoxLayout, QCheckBox, QVBoxLayout, QListWidget, QListWidgetItem, QGroupBox
from PySide6.QtGui import QAction
from PySide6.QtCore import QCoreApplication, Qt

class TrackWidget(QWidget):
    def __init__(self, index, enabled):
        super().__init__()
        self.index = index
        self.enabled = enabled
        self.initUI()

    def initUI(self):
        hLayout = QHBoxLayout(self)
        hLayout.setContentsMargins(8, 8, 8, 8)
        hLayout.addWidget(QLabel(f"Track {self.index}"))
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(self.enabled)
        hLayout.addWidget(self.checkbox, alignment=Qt.AlignRight)
        # hLayout.addWidget(self.checkbox)
        self.setLayout(hLayout)

class MainWindow(QMainWindow):
    def __init__(self, tracks=[]):
        super().__init__()

        self.tracks = tracks

        # Set the main window's size
        self.resize(600, 480)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.layout.addWidget(self.create_tracks_groupbox())

        self.populateList()
    
    def create_tracks_groupbox(self) -> QGroupBox:
        groupbox = QGroupBox("Tracks")
        vlayout = QVBoxLayout()
        
        self.listWidget = QListWidget()
        vlayout.addWidget(self.listWidget)
        groupbox.setLayout(vlayout)
        return groupbox

    def populateList(self):
        for i in range(0, len(self.tracks)):
            listItem = QListWidgetItem(self.listWidget)
            trackWidget = TrackWidget(i, self.tracks[i])
            listItem.setSizeHint(trackWidget.sizeHint())
            listItem.setFlags(listItem.flags() & ~Qt.ItemIsSelectable)
            self.listWidget.addItem(listItem)
            self.listWidget.setItemWidget(listItem, trackWidget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # QCoreApplication.setApplicationName("HyperEdit")
    window = MainWindow(tracks=[True, False, True])
    window.show()
    sys.exit(app.exec())
    