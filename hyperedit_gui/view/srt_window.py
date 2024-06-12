import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QVBoxLayout, QPushButton, QWidget, QTableView, QStyledItemDelegate, QHBoxLayout, QLabel, QListWidgetItem, QListWidget, QGridLayout
from PySide6.QtGui import QAction, QStandardItemModel, QStandardItem
from PySide6.QtCore import QCoreApplication, Qt

from hyperedit.srt import parse_srt

_ACTION_INDEX = 3

# TODO this should go into hyperedit$
class ActionPanel(QWidget):
    def __init__(self, parent=None, id=None):
        super().__init__(parent)

        self.id = id
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(2, 0, 2, 0)
        self.layout.setSpacing(2)
        self.revertButton = QPushButton("Revert")
        self.revertButton.setEnabled(False)
        self.previewButton = QPushButton("Preview")
        self.layout.addWidget(self.revertButton)
        self.layout.addWidget(self.previewButton)

        self.revertButton.clicked.connect(self.revert)
        self.previewButton.clicked.connect(self.preview)

        self.setLayout(self.layout)

    def revert(self):
        print(f"Reverting {self.id}")

    def preview(self):
        print(f"Previewing {self.id}")
    
class SrtEntry:
    def __init__(self, entry) -> None:
        self.id = entry[0]
        self.start_time = entry[1]
        self.end_time = entry[2]

    def to_primitive(self):
        return (self.id, self.start_time, self.end_time)

class SrtWindow(QWidget):

    def __init__(self, parent, srts):
        super().__init__(parent)

        self.srt = srts

        self.resize(600, 400)

        self.layout = QVBoxLayout(self)

        self.model = QStandardItemModel(0, 4)  # 4 columns
        self.model.setHeaderData(0, Qt.Horizontal, "ID")
        self.model.setHeaderData(1, Qt.Horizontal, "Start")
        self.model.setHeaderData(2, Qt.Horizontal, "End")
        self.model.setHeaderData(_ACTION_INDEX, Qt.Horizontal, "Actions")

        self.tableView = QTableView()
        self.tableView.setModel(self.model)
        self.tableView.setColumnWidth(_ACTION_INDEX, 200)

        self.layout.addWidget(self.tableView)
        self.layout.addLayout(self.create_back_next_buttons())

        self.populateTable()

    def create_back_next_buttons(self):

        buttonLayout = QHBoxLayout()
        backButton = QPushButton('Edit SRTs', self)
        # nextButton = QPushButton('Edit SRTs', self)

        buttonLayout.addWidget(backButton)
        buttonLayout.addStretch(1)
        # buttonLayout.addWidget(nextButton)

        backButton.clicked.connect(lambda: self.parent().setCurrentIndex(1))
        # nextButton.clicked.connect(lambda: self.parent().setCurrentIndex(3))

        return buttonLayout

    def populateTable(self):
        for e in self.srt:
            entry = SrtEntry(e)
            idItem = QStandardItem(entry.id)
            idItem.setFlags(~Qt.ItemIsEditable)
            startItem = QStandardItem(str(entry.start_time))
            startItem.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            endItem = QStandardItem(str(entry.end_time))
            endItem.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            actionItem = QStandardItem()  # Empty, will hold the button
            actionItem.setFlags(~Qt.ItemIsSelectable)
            self.model.appendRow([idItem, startItem, endItem, actionItem])

            actionPanel = ActionPanel(id=entry.id)
            self.tableView.setIndexWidget(self.model.index(self.model.rowCount() - 1, _ACTION_INDEX), actionPanel)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    srts = parse_srt("data/test.srt")
    window = SrtWindow(parent=None, srts=srts)
    window.show()
    sys.exit(app.exec())