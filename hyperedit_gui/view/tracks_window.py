import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QLabel, QWidget, QHBoxLayout, QCheckBox, QVBoxLayout, QListWidget, QListWidgetItem, QGroupBox, QPushButton, QLineEdit
from PySide6.QtGui import QAction, QDoubleValidator
from PySide6.QtCore import QCoreApplication, Qt

from ffprobe import FFProbe
from hyperedit.extract_dialog import get_audio_tracks
from hyperedit_gui.controller import Controller

class TrackWidget(QWidget):
    def __init__(self, index, enabled, controller):
        super().__init__()
        self.index = index
        self.enabled = enabled
        self.controller = controller
        self.initUI()

    def initUI(self):
        hLayout = QHBoxLayout(self)
        hLayout.setContentsMargins(8, 8, 8, 8)
        hLayout.addWidget(QLabel(f"Track {self.index}"))
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(self.enabled)
        hLayout.addStretch()
        hLayout.addWidget(self.checkbox, alignment=Qt.AlignRight)
        previewButton = QPushButton("Preview")
        previewButton.clicked.connect(self.preview_track)
        hLayout.addWidget(previewButton, alignment=Qt.AlignRight)
        self.setLayout(hLayout)

    def preview_track(self):
        self.controller.PreviewTrack(self.index)

class TracksWindow(QWidget):
    def __init__(self, parent, tracks=[], controller: Controller=None):
        super().__init__(parent)

        self.controller = controller
        self.tracks = tracks

        self.controller.AddProjectChangeObserver(self)

        # Set the main window's size
        self.resize(600, 480)

        self.layout = QVBoxLayout(self)

        self.layout.addWidget(self.create_tracks_groupbox())
        self.layout.addLayout(self.create_back_next_buttons())

        self.populateList()

    def get_tracks_bitmap(self):
        bitmap = 0
        for index, value in enumerate(self.tracks):
            if value:
                bitmap |= (1 << index)
        return bitmap
    
    def create_tracks_groupbox(self) -> QGroupBox:
        groupbox = QGroupBox("Tracks")
        vlayout = QVBoxLayout()
        
        self.listWidget = QListWidget()
        vlayout.addWidget(self.listWidget)

        # merge audio tracks layout
        hlayout = self.create_merge_tracks_hlayout()
        vlayout.addLayout(hlayout)

        # transcribe audio tracks layout
        hlayout = self.create_transcribe_hlayout(hlayout)
        vlayout.addLayout(hlayout)

        # deaggress layout
        hlayout = self.create_deaggress_hlayout()
        vlayout.addLayout(hlayout)

        groupbox.setLayout(vlayout)
        return groupbox

    def create_merge_tracks_hlayout(self):
        hlayout = QHBoxLayout()
        merge_button = QPushButton("Merge")
        merge_button.setMaximumWidth(80)
        hlayout.addWidget(merge_button)
        # merge label display warning if file already exists
        self.merge_label = QLabel("⚠️")
        hlayout.addWidget(self.merge_label)
        self.merge_path_line_edit = QLineEdit(f"blah{self.get_tracks_bitmap()}.wav")
        self.merge_path_line_edit.setEnabled(False)
        hlayout.addWidget(self.merge_path_line_edit)
        return hlayout

    def create_transcribe_hlayout(self, hlayout):
        hlayout = QHBoxLayout()
        transcribe_button = QPushButton("Transcribe")
        transcribe_button.setEnabled(False)
        hlayout.addWidget(transcribe_button)
        # transcribe label displays warning if merged audio does not exist
        self.transcribe_label = QLabel("⚠️")
        hlayout.addWidget(self.transcribe_label)
        self.transcribe_path_line_edit = QLineEdit(f"blah{self.get_tracks_bitmap()}.srt")
        self.transcribe_path_line_edit.setEnabled(False)
        hlayout.addWidget(self.transcribe_path_line_edit)
        return hlayout

    def create_deaggress_hlayout(self):
        hlayout = QHBoxLayout()
        deaggress_button = QPushButton("Deaggress")
        self.deaggress_seconds_line_edit = QLineEdit(self)
        self.deaggress_seconds_line_edit.setText("1.0")
        
        # deaggress seconds validator
        validator = QDoubleValidator(0.1, 60.0, 1, self)
        validator.setNotation(QDoubleValidator.StandardNotation)
        self.deaggress_seconds_line_edit.setValidator(validator)
        hlayout.addWidget(deaggress_button)
        hlayout.addWidget(QLabel("by seconds"))
        hlayout.addWidget(self.deaggress_seconds_line_edit)
        return hlayout
    
    def create_back_next_buttons(self):
        buttonLayout = QHBoxLayout()
        backButton = QPushButton('Projects', self)
        nextButton = QPushButton('Edit SRTs', self)

        buttonLayout.addWidget(backButton)
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(nextButton)

        backButton.clicked.connect(lambda: self.parent().setCurrentIndex(0))
        nextButton.clicked.connect(lambda: self.parent().setCurrentIndex(2))

        return buttonLayout

    def populateList(self):
        self.listWidget.clear()
        for i in range(0, len(self.tracks)):
            listItem = QListWidgetItem(self.listWidget)
            trackWidget = TrackWidget(i, self.tracks[i], self.controller)
            listItem.setSizeHint(trackWidget.sizeHint())
            listItem.setFlags(listItem.flags() & ~Qt.ItemIsSelectable)
            self.listWidget.addItem(listItem)
            self.listWidget.setItemWidget(listItem, trackWidget)

    # TODO: this could take a project as arguments
    def OnProjectChange(self):

        # TODO merge with tracks loaded from project. if a mismatch, notify and clear project tracks
        self.tracks = self.controller.GetTracks()
        self.populateList()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # QCoreApplication.setApplicationName("HyperEdit")
    window = TracksWindow(parent=None, tracks=[True, False, True], controller=Controller())
    window.show()
    sys.exit(app.exec())
    