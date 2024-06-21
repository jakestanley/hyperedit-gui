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
        self.checkbox.stateChanged.connect(self.toggle_track)
        hLayout.addStretch()
        hLayout.addWidget(self.checkbox, alignment=Qt.AlignRight)
        previewButton = QPushButton("Preview")
        previewButton.clicked.connect(self.preview_track)
        hLayout.addWidget(previewButton, alignment=Qt.AlignRight)
        self.setLayout(hLayout)

    def toggle_track(self, state):
        self.controller.ToggleTrack(self.index, state == Qt.Checked.value)

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

        groupbox.setLayout(vlayout)
        return groupbox

    def create_merge_tracks_hlayout(self):
        hlayout = QHBoxLayout()
        self.merge_button = QPushButton("Merge")
        self.merge_button.setMaximumWidth(80)
        self.merge_button.setEnabled(self.controller.CanMergeTracks())
        self.merge_button.pressed.connect(self.controller.MergeTracks)
        hlayout.addWidget(self.merge_button)
        # merge label display warning if file already exists
        self.merge_label = QLabel("")
        hlayout.addWidget(self.merge_label)
        # self.merge_path_line_edit = QLineEdit("")
        # self.merge_path_line_edit.setEnabled(False)
        # hlayout.addWidget(self.merge_path_line_edit)
        return hlayout

    def create_transcribe_hlayout(self, hlayout):
        hlayout = QHBoxLayout()
        self.transcribe_button = QPushButton("Transcribe")
        self.transcribe_button.setEnabled(self.controller.AreTracksMerged())
        self.transcribe_button.clicked.connect(self.controller.TranscribeTracks)
        hlayout.addWidget(self.transcribe_button)
        
        transcribe_label_text = ""
        if self.controller.AreTracksMerged():
            if self.controller.AreTracksTranscribed():
                transcribe_label_text = "⚠️ Tracks already transcribed"
            else:
                transcribe_label_text = "Ready to transcribe"
        else:
            transcribe_label_text = "Cannot transcribe as these tracks not yet merged"

        self.transcribe_label = QLabel(transcribe_label_text)
        hlayout.addWidget(self.transcribe_label)
        # self.transcribe_path_line_edit = QLineEdit("blah.srt")
        # self.transcribe_path_line_edit.setEnabled(self.controller.AreTracksMerged())
        # hlayout.addWidget(self.transcribe_path_line_edit)
        return hlayout
    
    def update_transcribe_hlayout(self):
        transcribe_label_text = ""
        if self.controller.AreTracksMerged():
            self.transcribe_button.setEnabled(True)
            if self.controller.AreTracksTranscribed():
                transcribe_label_text = "⚠️ Tracks already transcribed"
            else:
                transcribe_label_text = "Ready to transcribe"
        else:
            self.transcribe_button.setEnabled(False)
            transcribe_label_text = "Cannot transcribe as these tracks not yet merged"

        self.transcribe_label.setText(transcribe_label_text)
    
    def create_back_next_buttons(self):
        buttonLayout = QHBoxLayout()
        backButton = QPushButton('Projects', self)
        nextButton = QPushButton('SRTs', self)

        buttonLayout.addWidget(backButton)
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(nextButton)

        backButton.clicked.connect(lambda: self.parent().setCurrentIndex(0))
        nextButton.clicked.connect(self.next_page)

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

    def update_merge_layout(self):
        merge_label_text = ""
        self.merge_button.setEnabled(False)
        if self.controller.CanMergeTracks():
            self.merge_button.setEnabled(True)
            merge_label_text = "Ready to merge"
            if self.controller.AreTracksMerged():
                merge_label_text = "⚠️ Tracks already merged"
        else:
            merge_label_text = "Cannot merge tracks. You must select at least one track"
            
                
        self.merge_label.setText(merge_label_text)

    def next_page(self):
        # TODO this really shouldn't be called from here
        self.controller.NotifySrtChangeObservers()
        self.parent().setCurrentIndex(2)

    # TODO: this could take a project as arguments
    def OnProjectChange(self):

        # TODO merge with tracks loaded from project. if a mismatch, notify and clear project tracks
        self.tracks = self.controller.GetTracks()
        self.merge_button.setEnabled(True)
        self.populateList()
        self.update_merge_layout()
        self.update_transcribe_hlayout()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # QCoreApplication.setApplicationName("HyperEdit")
    window = TracksWindow(parent=None, tracks=[True, False, True], controller=Controller())
    window.show()
    sys.exit(app.exec())
    